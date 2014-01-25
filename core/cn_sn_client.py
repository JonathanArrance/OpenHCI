#! /usr/sbin/python

import os
import sys
import socket
import pickle
from time import sleep
import select
import subprocess
import transcirrus.common.util as util
import transcirrus.database.node_db as node_db
import transcirrus.common.service_control as service_controller
import transcirrus.common.logger as logger

timeout_sec = 1
retry_count = 5
recv_buffer = 4096
dhcp_retry = 5
services_retry = 5

connect_pkt = {
'Type' : 'connect',
'Length': '1',
'Value': 1
}

status_ready = {
'Type':'status',
'Length':'1',
'Value':'node_ready'
}

status_halt = {
'Type':'status',
'length':'1',
'Value':'node_halt'
}

node_info = {
'Type': 'Node_info', 
'Length': 10, 
'Value': {
    'node_name':'box15',
    'node_type':'cn',
    'node_mgmt_ip':'',
    'node_data_ip':'',
    'node_controller':'',
    'node_cloud_name':'',
    'node_nova_zone':'',
    'node_iscsi_iqn':'',
    'node_swift_ring':'',
    'node_id':'trans01'
    }
}

reply_alive = {
'Type' : 'status',
'Length': '1',
'Value': 'alive'
}

def getNodeInfo():
    '''
    @author         : Shashaa
    comment         : this function will fetch default factory default
                      information from a node and then construts a node info dictionary.
                      changes are made to global dictionary node_info 
    return value    : 
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    global node_info

    node_info['Value']['node_id'] = util.get_node_id()
    node_info['Value']['node_name'] = util.get_node_name()
    node_info['Value']['node_type'] = util.get_node_type()
    node_info['Value']['node_data_ip'] = util.get_node_data_ip()

    # node_mgmt_ip is left as default, NOT set to any predefined ip
    # for reasons of ip clashes in the mgmgt network

    # node_cloud_name, node_controller, node_nova_zone, node_iscsi_iqn,
    # node_swift_ring set to null values; as the node added to the
    # cluster is cloud information agnostic. 


def getDhcpServer():
    '''
    @author         : Shashaa
    comment         : get DHCP server IP address from dhcp.bond1.leases
                      file. bond1 interface of the machine connects to
                      data network of the cloud.
    return value    : dhcp_server ip
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''

    dhcp_file = "/var/lib/dhcp/dhclient.bond1.leases"
    dhcp_server = ""
    global dhcp_retry

    while dhcp_retry:

        out = subprocess.Popen('grep dhcp-server-identifier %s' % (dhcp_file), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        data = out.stdout.readlines()
        if (data):
            #print data[0].split(" ")
            data = data[0].split(" ")
            dhcp_server = data[4].strip()
            dhcp_server = dhcp_server.strip(";")
            logger.sys_info("dhcp_server IP: %s" % dhcp_server)
            dhcp_retry=0
            #sys.exit()
        else:
            # TODO: can initiate a command to acquire dhcp assigned IP
            logger.sys_warning("Trying to get DHCP server IP")
            dhcp_retry = dhcp_retry-1
            time.sleep(1)

    if (dhcp_server == ""):
        logger.sys_error("Error in getting DHCP server IP")
        sys.exit()
    else:
        return dhcp_server


def sendOk(sock):

    '''
    @author         : Shashaa
    comment         : send's ok packet to the socket connected to conn
                      input: conn socket descriptor 
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    status_ok = {
            'Type': 'status',
            'Length': '1',
            'Value': 'ok'
        }
    #sock.sendall(pickle.dumps(status_ok, -1))
    send_data(pickle.dumps(status_ok, -1), sock)

def restartServices(node_id, node_type):

    '''
    @author         : Shashaa
    comment         : restart node services 
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''

    if node_type == "sn":

        # restart cinder services
        ret = service_controller.cinder("restart")

        if ret == "OK":
            logger.sys_info("node_id: %s, services restart success" %(node_id))
            if __debug__ :
                print "node_id: %s, services restart success" % node_id
            return True
        else:
            logger.sys_error("node_id: %s, services restart failure" %(node_id))
            if __debug__ :
                print "node_id: %s, services restart failure" % node_id
            return False
    elif node_type == "cn":

        # restart nova services
        ret = service_controller.nova("restart")
        if ret == "OK":

            # restart openvswitch services
            ret = service_controller.openvswitch("restart")

            if ret == "OK":
                logger.sys_info("node_id: %s, services restart success" %(node_id))
                if __debug__ :
                    print "node_id: %s, services restart success" % node_id
                return True
            else:
                logger.sys_error("node_id: %s, openvswitch services restart failure" %(node_id))
                if __debug__ :
                    print "node_id: %s, openvswitch services restart failure" % node_id
                return False
        else:
            logger.sys_error("node_id: %s, nova services restart failure" %(node_id))
            if __debug__ :
                print "node_id: %s, nova services restart failure" % node_id
            return False
    else:
        logger.sys_error("node_id: %s, unknown node_type" %(node_id))
        if __debug__ :
            print "node_id: %s, unknown node_type" % node_type
        return False


def recv_data(sock):

    '''
    @author         : Shashaa
    comment         : receives data from connected socket to sock
                      then deserializes it
    return value    : received data
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    count=0
    while True:
        ready = select.select([sock], [], [], timeout_sec)
        if ready[0]:
            data = sock.recv(recv_buffer)
            break
        else:
            count = count + 1
            if count >= retry_count:
                logger.sys_error("retry count expired..exiting!!")
                if __debug__ :
                    print "retry count expired..exiting!!"
                sys.exit(1)
            logger.sys_warning("retrying...%s" %(count))
            if __debug__ :
                print "retrying... ", count

    return data

def send_data(msg, sock):


    global retry_count
    global timeout_sec
    count=0
    totalsent = 0
    #msglen = msg.length()
    # TODO send data based on size of the message being sent
    # assume 10 bytes as minimum length of any message exchanged between client
    # and server sockets
    msglen = 10
    while totalsent < msglen:
        sent = sock.send(msg[totalsent:])
        if sent == 0:
            count = count+1
            if count >= retry_count:
                logger.sys_error("send failed !!")
                raise RuntimeError("socket connection broken")
                sys.exit()
            else:
                logger.sys_info("socket send data retrying ...")
                time.sleep(1)
        totalsent = totalsent + sent


def restartNovaServices(node_id):
    '''
    @author         : Shashaa
    description     : restart Nova compute services and check for
                      running status 
    return value    : 
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    # restart nova services
    out = os.popen('service nova-compute restart')
    status = out.read()
    #print "node_id: %s, nova compute restart:: %s" % (node_id, status)

    # check output
    out_array = status.split('\n')

    if out_array[0] == "nova-compute stop/waiting":
        logger.sys_error("nova-compute stopped!! node_id %s" %(node_id))
        if __debug__ :
            print "nova-compute stopped!! node_id %s" % node_id
        if out_array[1].find("nova-compute start/running") != -1:
            logger.sys_info("nova-compute re-started!!! node_id: %s" %(node_id))
            if __debug__ :
                print "nova-compute re-started!!! node_id: %s" % node_id
        else:
            logger.sys_error("failure to re-start nova-compute!!! node_id: %s" %(node_id))
            if __debug__ :
                print "failure to re-start nova-compute!!! node_id: %s" % node_id
    else:
        logger.sys_error("failure to stop nova-compute!!! node_id: %s" %(node_id))
        if __debug__ :
            print "failure to stop nova-compute!!! node_id: %s" % node_id

def restartOvsServices(node_id):    
    '''
    @author         : Shashaa
    description     : restart ovs services and check for
                      running status 
    return value    : 
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    # restart ovs
    out = os.popen("sudo service quantum-server restart")
    status = out.read()

    #print "node_id: %s, nova quantum server restart: %s" % (node_id, status)

    # check output
    out_array = status.split('\n')

    if out_array[1].find("start/running") != -1:
        logger.sys_info("node_id: %s, quantum server re-started!!!" %(node_id))
        if __debug__ :
            print "node_id: %s, quantum server re-started!!!" % node_id
    else:
        logger.sys_error("node_id: %s, failure in starting quantum server!!!" %(node_id))
        if __debug__ :
            print "node_id: %s, failure in starting quantum server!!!" % node_id


    # check openvswitch
    out = os.popen("service openvswitch-switch restart")
    status = out.read()

    #print "node_id: %s, openvswitch retstart status: %s" % (node_id, status)

    # check output
    out_array = status.split('\n')

    for i in range(0, len(out_array)-1):
        if out_array[i].find("Killing ovs-vswitchd") != -1:
            logger.sys_info("node_id: %s, ovs-vswitchd killed" %(node_id))
            if __debug__ :
                print "node_id: %s, ovs-vswitchd killed" % (node_id)
        elif out_array[i].find("Killing ovsdb-server") != -1:
            logger.sys_info("node_id: %s, ovsdb-server killed" %(node_id))
            if __debug__ :
                print "node_id: %s, ovsdb-server killed" % (node_id)
        elif out_array[i].find("Starting ovsdb-server") != -1:
            logger.sys_info("node_id: %s, ovsdb-server re-started !!!" %(node_id))
            if __debug__ :
                print "node_id: %s, ovsdb-server re-started !!!" % node_id
        elif out_array[i].find("Starting ovs-vswitchd") != -1:
            logger.sys_info("node_id: %s, ovs-switchd re-started !!!" %(node_id))
            if _debug__ :
                print "node_id: %s, ovs-switchd re-started !!!" % node_id



def checkNovaCompute(status):
    '''
    @author         : Shashaa
    description     : parse and checks nova compute output 
    return value    : True/False
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''

    if status.find("start/running") != -1:
        return True
    else:
        return False

def checkNovaManage(status):
    '''
    @author         : Shashaa
    description     : parse and check nova manage services 
    return value    : True/False
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    line_array = status.split('\n')
    ret = 0

    for i in range(0, len(line_array)-1):            
        if line_array[i].find('nova-conductor') != -1:
            if line_array[i].find('enabled') != -1 and line_array[i].find(':-)') != -1:
                ret = ret+1
            else:
                logger.sys_error("nova-conductor is not running")
                if __debug__ :
                    print "nova-conductor is not running"
        elif line_array[i].find('nova-scheduler') != -1:
            if line_array[i].find('enabled') != -1 and line_array[i].find(':-)') != -1:
                ret = ret+1
            else:
                logger.sys_error("nova-scheduler is not running")
                if __debug__ :
                    print "nova-scheduler is not running"
        elif line_array[i].find('nova-consoleauth') != -1:
            if line_array[i].find('enabled') != -1 and line_array[i].find(':-)') != -1:
                ret = ret+1
            else:
                logger.sys_error("nova-consoleauth is not running")
                if __debug__ :
                    print "nova-consoleauth is not running"
        elif line_array[i].find('nova-cert') != -1: 
            if line_array[i].find('enabled') != -1 and line_array[i].find(':-)') != -1:
                ret = ret+1
            else:
                logger.sys_error("nova-cert is not running")
                if __debug__ :
                    print "nova-cert is not running"
        elif line_array[i].find('nova-compute') != -1:
            if line_array[i].find('enabled') != -1 and line_array[i].find(':-)') != -1:
                ret = ret+1
            else:
                logger.sys_error("nova-compute is not running")
                if __debug__ :
                    print "nova-compute is not running"


    # make sure all services are listed            
    if ret == 5:
        return True
    else:
        return False

def checkOpenvswitch(status):
    '''
    @author         : Shashaa
    description     : parse and check openv switch process status  
    return value    : True/False
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    if status.find('start/running') != -1:
        return True
    else:
        logger.sys_error("quantum-plugin-openvswitch-agent stopped/halted !!!")
        if __debug__ :
            print "quantum-plugin-openvswitch-agent stopped/halted !!!"
        return False

def checkOvs(node_id, status):
    '''
    @author         : Shashaa
    description     : parse and check openv switch process status  
    return value    : True/False
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    line_array = status.split('\n')
    for i in range(0, len(line_array)-1):
        if line_array[i].find("br-int") != -1:
            logger.sys_info("node_id: %s, bridge exists : %s" %(node_id,line_array[i]))
            if __debug__ :
                print "node_id: %s, bridge exists : %s" % (node_id,line_array[i])
            return True
        else:
            return False

def checkNovaServices(node_id):
    '''
    @author         : Shashaa
    description     : execute and check nova services 
    return value    : False if any of the service fails, else True
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''

    # check nova services
    out = os.popen('service nova-compute status')
    status = out.read()
    #print "nova compute :: %s" % status
    ret = checkNovaCompute(status)
    if ret == False:
        logger.sys_error("node_id: %s, nova-compute status failure !!!" %(node_id))
        if __debug__ :
            print "node_id: %s, nova-compute status failure !!!" % node_id
        return ret

    out = os.popen('nova-manage service list')
    status = out.read()
    ret = checkNovaManage(status)
    if ret == False:
        logger.sys_error("node_id: %s, nova-manage services failure !!!" %(node_id))
        if __debug__ :
            print "node_id: %s, nova-manage services failure !!!" % node_id
        return ret

    out = os.popen('service quantum-plugin-openvswitch-agent status')
    status = out.read()
    #print "quantun-plugin :: %s" % status
    ret = checkOpenvswitch(status)
    if ret == False:
        logger.sys_error("node_id: %s, quantum openvswitch agent failure !!!" %(node_id))
        if __debug__ :
            print "node_id: %s, quantum openvswitch agent failure !!!" % node_id
        return ret

    # export environment variables TODO
    out = os.system("source $PWD/creds")
    #out = os.popen('nova host-list') # TODO

    return True


def checkOvsServices(node_id):

    '''
    @author         : Shashaa
    description     : Fasle if any of the service fails, else True
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    # check ovs services
    out = os.popen('sudo ovs-vsctl list-br')
    status = out.read()
    #print "ovs-vsctl :: %s" % status
    ret = checkOvs(node_id, status)
    if ret == False:
        logger.sys_error("node_id: %s, ovs services failure !!!" %(node_id))
        if __debug__ :
            print "node_id: %s, ovs services failure !!!" % node_id
        return ret
    else:
        #print "node_id: %s, ovs services success !!!" % node_id
        return True

def processComputeConfig(sock, node_id):

    '''
    @author         : Shashaa
    description     : receives compute node default config
                      write config files for compute node
                      checks for compute node services
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''

    # receive compute node nova config file
    cn_config = recv_data(sock)

    # parse config file
    if cn_config:
        cn_config = pickle.loads(cn_config)

        # send ok, ack 
        sendOk(sock)
        for i in range(0,len(cn_config)):
            if cn_config[i]['file_name'] == 'nova.conf':
                nova_conf = cn_config[i]
            elif cn_config[i]['file_name'] == 'nova-compute.conf':
                comp_conf = cn_config[i]
            elif cn_config[i]['file_name'] == 'api-paste.ini' :
                api_conf = cn_config[i]
    else:
        logger.sys_error("compute node did not receive nova config file, exiting!!!")
        if __debug__ :
            print "compute node did not receive nova config file, exiting!!!"
        sys.exit()

    # receive ovs config structures
    cn_config1 = recv_data(sock)

    if cn_config1:
        cn_config1 = pickle.loads(cn_config1)

        # send ok, ack
        sendOk(sock)

        # get ovs config file
        for i in range(0,len(cn_config1)):
            if cn_config1[i]['file_name'] == 'ovs_quantum_plugin.ini':
                ovs_conf = cn_config1[i]
	    elif cn_config1[i]['file_name'] == 'quantum.conf':
                net_conf = cn_config[i]

    else:
        logger.sys_error("compute node did not receive ovs config file, exiting!!!")
        if __debug__ :
            print "compute node did not receive ovs config file, exiting!!!"
        sys.exit()
                

    '''
    there is no need for config file match checking, as build message is
    sent for any update in node info or if the node is inserted into
    cluster for the first time
    '''

    # write compute nodes nova config files

    ret = util.write_new_config_file(nova_conf)
    if ret == "ERROR" or ret == "NA":
        logger.sys_error("eror in writing nova conf, exiting!!!")
        if __debug__ :
            print "eror in writing nova conf, exiting!!!"
        sys.exit()
    else:
        logger.sys_info("write success, nova conf")
        if __debug__ :
            print "write success, nova conf"

    ret = util.write_new_config_file(comp_conf)
    if ret == "ERROR" or ret == "NA":
        logger.sys_error("error in writing comp conf, exiting!!!")
        if __debug__ :
            print "error in writing comp conf, exiting!!!"
        sys.exit()
    else:
        logger.sys_info("write success, comp conf")
        if __debug__ :
            print "write success, comp conf"

    ret = util.write_new_config_file(api_conf)
    if ret == "ERROR" or ret == "NA":
        logger.sys_error("error in writing api conf, exiting!!!")
        if __debug__ :
            print "error in writing api conf, exiting!!!"
        sys.exit()
    else:
        logger.sys_info("write success, api conf")
        if __debug__ :
            print "write success, api conf"

    # write compute nodes ovs config file

    ret = util.write_new_config_file(ovs_conf)
    if ret == "ERROR" or ret == "NA":
        logger.sys_error("error in writing ovs conf, exiting!!!")
        if __debug__ :
            print "error in writing ovs conf, exiting!!!"
        sys.exit()
    else:
        logger.sys_info("write success, ovs conf")
        if __debug__ :
            print "write success, ovs conf"

    ret = util.write_new_config_file(net_conf)
    if ret == "ERROR" or ret == "NA":
        logger.sys_error("error in writing net conf, exiting!!!")
        if __debug__ :
            print "error in writing net conf, exiting!!!"
        sys.exit()
    else:
        logger.sys_info("write success, net_conf")
        if __debug__ :
            print "write success, net_conf"
                                                                                   

    post_install_status = True

    # TEST
   # sys.exit()
    # TEST
    # restart Nova and ovs services
    """
    # old code to restart services
    restartNovaServices(node_id)
    restartOvsServices(node_id)

    nova_services = checkNovaServices(node_id)

    ovs_services = checkOvsServices(node_id)
    """
    nova_services = service_controller.nova("restart")
    ovs_services = service_controller.openvswitch("restart")

    if nova_services=='OK' and ovs_services=='OK':
        logger.sys_info("All services are up and running !!!")
        if __debug__ :
            print "All services are up and running !!!"
        logger.sys_info("All services are up and running")
        post_install_status=True
    else:
        if __debug__ :
            print "nova/ovs services restart failure"
        logger.sys_error("nova/ovs services restart failure")
        post_install_status=False


    if post_install_status == True:

        # send node_ready status message to cc
        #sock.sendall(pickle.dumps(status_ready, -1))
        send_data(pickle.dumps(status_ready, -1), sock)

        # listen for ok message, ack -- loops infinetly
        while True:
            data = recv_data(sock)

            if data:
                data = pickle.loads(data)
                if data['Type'] == 'status' and data['Value'] == 'ok':
                    logger.sys_info("client received %s" %(data['Value']))
                    if __debug__ :
                        print "client received %s" % data
                    break
            else:
                logger.sys_info("listening for status_ready ack")
                if __debug__ :
                    print "listening for status_ready ack"

    else:

        # retry  TODO
        global services_retry

        # loop 
        while(services_retry >= 0):

            # restart services
            """
            # old code to restart services
            restartNovaServices(node_id)
            restartOvsServices(node_id)

            # check services
            nova_services = checkNovaServices(node_id)
            ovs_services = checkOvsServices(node_id)
            """

            nova_services = service_controller.nova("restart")
            ovs_services = service_controller.openvswitch("restart")

            if nova_services == 'OK' and ovs_services == 'OK':
                post_install_status = True 
                break;
            services_retry = services_retry-1
            logger.sys_warning("node_id: %s, ******retrying services******* %s" %(node_id, services_retry))
            if __debug__ :
                print "node_id: %s, ******retrying services******* %s" %(node_id,services_retry)

        if post_install_status != True:

            # send node_halt status message to cc
            #sock.sendall(pickle.dumps(status_halt, -1))
            send_data(pickle.dumps(status_halt, -1), sock)

            # listen for ok message, ack -- loop infinetly
            while True:
                data = recv_data(sock)

                if data:
                    data = pickle.loads(data)
                    if data['Type'] == 'status' and data['Value'] =='ok':
                        logger.sys_info("client received %s" %(data['Value']))
                        if __debug__ :
                            print "client received %s" % data
                        break
                else:
                    logger.sys_info("listening for status_halt ack")
                    if __debug__ :
                        print "listening for status_halt ack"
        else:
             
            # send node_ready status message to cc
            #sock.sendall(pickle.dumps(status_ready, -1))
            send_data(pickle.dumps(status_ready, -1), sock)

            # listen for ok message, ack -- loops infinetly
            while True:
                data = recv_data(sock)

                if data:
                    data = pickle.loads(data)
                    if data['Type'] == 'status' and data['Value'] == 'ok':
                        logger.sys_info("client received %s" %(data))
                        if __debug__ :
                            print "client received %s" % data
                        break
                else:
                    logger.sys_info("listening for status_ready ack")
                    if __debug__ :
                        print "listening for status_ready ack"


    # receive keep alive messages
    keep_alive(sock)

def restartStorageServices(node_id):
    '''
    @author         : Shashaa
    description     : restart storage cinder/swift services
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''

    print "TODO"

def checkStorageServices(node_id):
    '''
    @author         : Shashaa
    description     : check for status of cinder/swift services
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''

    print "TODO"

def processStorageConfig(sock, node_id):

    '''
    @author         : Shashaa
    description     : receives compute node default config
                      checks for existing config matching
                      checks for compute node services
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''

    # receive cinder config files

    sn_config = recv_data(sock)

    if sn_config:
        sn_config = pickle.loads(sn_config)

        # send ok, ack
        sendOk(sock)

        # parse config file packet
        for i in range(0, len(sn_config)-1):
            if sn_config[i]['file_name'] == 'api-paste.ini':
                api_conf = sn_config[i]
            elif sn_config[i]['file_name'] == 'cinder.conf':
                cin_conf = sn_config[i]
    else:
        logger.sys_error("node_id: %s client did not receive cinder config files" %(node_id))
        if __debug__ :
            print "node_id: %s client did not receive cinder config files" % node_id
        sys.exit()


    # write config files
    ret = util.write_new_config_file(api_conf)
    if ret == "ERROR" or ret == "NA":
        logger.sys_error("node_id: %s error in writing api conf, exiting!!!" %(node_id))
        if __debug__ :
            print "node_id: %s error in writing api conf, exiting!!!" %  node_id
        sys.exit()
    else:
        logger.sys_info("node_id: %s write success, api conf" %(node_id))
        if __debug__ :
            print "node_id: %s write success, api conf" % node_id

    ret = util.write_new_config_file(cin_conf)
    if ret == "ERROR" or ret == "NA":
        logger.sys_error("node_id: %s error in writing cinder conf, exiting!!!" %(node_id))
        if __debug__ :
            print "node_id: %s error in writing cinder conf, exiting!!!" % node_id
        sys.exit()
    else:
        logger.sys_info("write success, cinder conf")
        if __debug__ :
            print "write success, cinder conf"


    # create service_controller object: TODO auth_dict      
    #controller = service_controller(auth_dict)
    # check for post install tests
    post_install_status = True

    # restart services
    sn_services = service_controller.cinder("restart")
    if sn_services == "NA" or sn_services == "ERROR":
        logger.sys_error("node_id: %s, error in restarting cinder services")
        if __debug__ :
            print "node_id: %s, error in restarting cinder services" % node_id
    elif sn_services == "OK":
        sn_services = True
    #restartStorageServices(node_id)

    # Here we do not check for services explicitly as restart would
    # also check the services running
    #sn_services = checkStorageServices(node_id)

    if sn_services == True:
        logger.sys_info("node_id: %s All services in storage node are running" %(node_id))
        if __debug__ :
            print "node_id: %s All services in storage node are running" % node_id
        post_install_status = True
    else:
        post_install_status = False

    if post_install_status == True:
        # send node ready status to cc
        #sock.sendall(pickle.loads(status_ready, -1))
        send_data(pickle.dumps(status_ready, -1), sock)

        # listen for ok ack message -- loop infinetly
        while True:
            data = recv_data(sock)

            if data:
                data = pickle.loads(data)
                if data['Type'] == 'status' and data['Value'] == 'ok':
                    logger.sys_info("node_id: %s client received %s" %(node_id, data['Value']))
                    if __debug__ :
                        print "node_id: %s client received %s" %(node_id, data['Value'])
                    break
            else:
                logger.sys_info("listening for ok ack message for status ready message")
                if __debug__ :
                    print "listening for ok ack message for status ready message"
    else:
        # retry
        retry = 5

        while(retry >= 0):

            # restart services
            sn_services = service_controller.cinder("restart")
            if sn_services == "NA" or sn_services == "ERROR":
                logger.sys_error("node_id: %s, error in restarting cinder services" %(node_id))
                if __debug__ :
                    print "node_id: %s, error in restarting cinder services" % node_id
            elif sn_services == "OK":
                sn_services = True
            #restartStorageServices(node_id)

            # check services
            #sn_services = checkStorageServices(node_id)

            if sn_services==True:
                post_install_status=True
                break
            retry = retry-1
            logger.sys_warning("node_id: %s ********* retrying services ********* %s" %(node_id, retry))
            if __debug__ :
                print "node_id: %s ********* retrying services ********* %s" % (node_id, retry)

        # check after stipulated retry's
        if post_install_status != True:
            # send node halt mesage to cc
            #sock.sendall(pickle.loads(status_halt, -1))
            send_data(pickle.dumps(status_halt, -1), sock)

            # listen for ok ack message
            while True:
                data = recv_data(sock)

                if data:
                    data = pickle.loads(data)
                    if data['Type'] == 'status' and data['Value'] == 'ok':
                        logger.sys_info("node_id: %s client received: %s" %(node_id,data['Value']))
                        if __debug__ :
                            print "node_id: %s client received: %s" % (node_id,data)
                        break
                else:
                    logger.sys_info("node_id: %s listening for status_halt ack" %(node_id))
                    if __debug__ :
                        print "node_id: %s listening for status_halt ack" % (node_id)
        else:
            # send node ready status message to cc
            #sock.sendall(pickle.loads(status_ready, -1))
            send_data(pickle.dumps(status_ready, -1), sock)

            # listen for ok ack message
            while True:
                data = recv_data(sock)

                if data:
                    data = pickle.loads(data)
                    if data['Type'] and data['Value'] == 'ok':
                        logger.sys_info("node_id: %s client received: %s" %(node_id, data['Value']))
                        if __debug__ :
                            print "node_id: %s client received: %s" %(node_id,data['Value'])
                    else:
                        logger.sys_error("node_id: %s received: %s" %(node_id, data['Value']))
                else:
                    logger.sys_info("node_id: %s listening for status_ready ack" %(node_id))
                    if __debug__ :
                        print "node_id: %s listening for status_ready ack" % (node_id)

    # keep alive check       
    keep_alive(sock)
            

def keep_alive(sock):

    '''
    @author         : Shashaa
    description     : listen for keep alive status messages and other
                      status messages
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    while True:
        ready = select.select([sock], [], [], timeout_sec)
        if ready[0]:
            data = sock.recv(recv_buffer)

            data = pickle.loads(data)
            if data['Type'] == 'status' and data['Value'] == 'alive':
                logger.sys_info("***%s***" % (data['Value']))
                # send reply as alive
                sock.sendall(pickle.loads(reply_alive, -1))
                if __debug__ :
                    print "***%s***" % data['Value']
            elif data['Type'] == 'command':
                logger.sys_info("received command %s" %(data['Value']))
                # TODO
            else:
                logger.sys_info("received %s" %(data))
                if __debug__ :
                    print "received %s " % data
                #keep_alive(sock)
        else:
            logger.sys_info("client waiting for keep alive messages")
            if __debug__ :
                print "client waiting for keep alive messages"


# start of client process
# create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get ciac ip address
ciac_ip = util.getDhcpServer()

# TEST
#print ciac_ip
#sys.exit()
# TEST

# data network ip
data_ip = "172.38.24.11"

# Bind it to data network interface
sock.setsockopt(socket.SOL_SOCKET, 25, "bond1"+'\0')     # bind's it to physical interface
#sock.bind((data_ip,0))                             # bind's it an IP address 

# Connect to the server socket
server_address = (ciac_ip, 6161)
print "connecting to %s port %s " % server_address
sock.connect(server_address)
sock.setblocking(0)
count=0
timeout_sec=1
retry_count=5
keep_alive_sec=10

try:
    # send connect
    logger.sys_info("sending connect_pkt")
    if __debug__ :
        print "sending connect_pkt"
    #sock.sendall(pickle.dumps(connect_pkt, -1))
    send_data(pickle.dumps(connect_pkt, -1), sock)

    # receive packet using select, retry_count
    while True:
        ready = select.select([sock], [], [], timeout_sec)
        if ready[0]:
            data = sock.recv(recv_buffer)
            break
        else:
            count = count + 1
            if count == retry_count:
                logger.sys_error("retry count expired..exiting!!")
                if __debug__ :
                    print "retry count expired..exiting!!"
                sys.exit(1)
            logger.sys_warning("retrying...%s" %(count))
            if __debug__ :
                print "retrying... ", count

    if data:
        data = pickle.loads(data)
        logger.sys_info("client received %s" %(data))
        if __debug__ :
            print "client received %s" % data

        # check for status ok
        if data['Type'] == 'status' and data['Value'] == 'ok':
            logger.sys_info("client received %s" %(data['Value']))
            if __debug__ :
                print "client received %s" % data['Value']

            # send node data
            getNodeInfo()
            node_type = node_info['Value']['node_type']
            node_id = node_info['Value']['node_id']
            logger.sys_info("sending %s " %(node_info))
            if __debug__ :
                print "sending %s " % node_info
            #print "node_id = %s" % node_id
            #sock.sendall(pickle.dumps(node_info, -1))
            send_data(pickle.dumps(node_info, -1), sock)

            # receive status message, retry_count
            data = recv_data(sock)

            if data:
                data = pickle.loads(data)
                #print "client received %s" % data
                if data['Type'] == 'status' and data['Value'] == 'ok':
                    logger.sys_info("client received %s" %(data['Value']))
                    if __debug__ :
                        print "client received %s" % data['Value']
                    # check for services TODO, based on node_type
                    ret = restartServices(node_id, node_type)
                    if ret == True:
                        logger.sys_info("Node is setup and ready to use!!!")
                        if __debug__ :
                            print "Node is setup and ready to use!!!"
                    else:
                        logger.sys_error("node_id: %s, failure to restart services")
                        if __debug__ :
                            print "node_id: %s, failure to restart services"
                    keep_alive(sock)

                elif data['Type'] == 'status' and data['Value'] == 'build':
                    logger.sys_info("client received %s" %(data['Value']))
                    if __debug__ :
                        print "client received %s" % data['Value']
                    #sys.exit(1) # TEST

                    if node_type == 'cn':
                        processComputeConfig(sock, node_id)
                    elif node_type == 'sn':
                        processStorageConfig(sock, node_id)

                else:
                    logger.sys_error("client received invalid status message")
                    if __debug__ :
                        print "client received invalid status message"
            else:
                logger.sys_error("client did not receive status message, exiting!!!")
                if __debug__ :
                    print "client did not receive status message, exiting!!!"
                sys.exit(1)

        else:
            logger.sys_error("client did not received status ok")
            if __debug__ :
                print "client did not received status ok"
    else:
        logger.sys_error("client received no data for connect packet")
        if __debug__ :
            print "client received no data for connect packet"

finally:
    logger.sys_error("closing client socket")
    if __debug__ :
        print "closing client socket"
    sock.close()

