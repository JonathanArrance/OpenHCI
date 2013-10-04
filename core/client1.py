#! /usr/sbin/python

import os
import sys
import socket
import pickle
from time import sleep
import select
import transcirrus.common.util as util
import transcirrus.database.node_db as node_db

timeout_sec = 1
retry_count = 5
recv_buffer = 4096


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
    sock.sendall(pickle.dumps(status_ok, -1))

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
                print "retry count expired..exiting!!"
                sys.exit(1)
            print "retrying... ", count

    return data

def processComputeConfig(sock):

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
        for i in range(0,len(cn_config)): # 2 - since three arrays are received
            if cn_config[i]['file_name'] == 'nova.conf':
                nova_conf = cn_config[i]
            elif cn_config[i]['file_name'] == 'nova-compute.conf':
                comp_conf = cn_config[i]
            elif cn_config[i]['file_name'] == 'api-paste.ini' :
                api_conf = cn_config[i]
    else:
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
        print "eror in writing nova conf, exiting!!!"
        sys.exit()
    else:
        print "write success, nova conf"

    ret = util.write_new_config_file(comp_conf)
    if ret == "ERROR" or ret == "NA":
        print "error in writing comp conf, exiting!!!"
        sys.exit()
    else:
        print "write success, comp conf"

    ret = util.write_new_config_file(api_conf)
    if ret == "ERROR" or ret == "NA":
        print "error in writing api conf, exiting!!!"
        sys.exit()
    else:
        print "write success, api conf"

    # write compute nodes ovs config file

    ret = util.write_new_config_file(ovs_conf)
    if ret == "ERROR" or ret == "NA":
        print "error in writing ovs conf, exiting!!!"
        sys.exit()
    else:
        print "write success, ovs conf"

    ret = util.write_new_config_file(net_conf)
    if ret == "ERROR" or ret == "NA":
        print "error in writing net conf, exiting!!!"
        sys.exit()
    else:
        print "write success, net_conf"


    post_install_status = True

    # check nova services
    out = os.popen('service nova-compute status')
    status = out.read()
    # process status TODO
    print "nova compute :: %s" % status

    out = os.popen('nova-manage service list')
    status = out.read()
    # process status TODO
    print "nova manage :: %s" % status

    out = os.popen('service quantum-plugin-openvswitch-agent restart')
    status = out.read()
    # process status TODO
    print "quantun-plugin :: %s" % status


    #out = os.system('nova host-list') # TODO


    # check ovs services
    out = os.popen('ovs-vsctl list-br')
    status = out.read()
    # process status TODO
    print "ovs-vsctl :: %s" % status


    if post_install_status == True:

        # send node_ready status message to cc
        status_ready = {
                'Type':'status',
                'Length':1,
                'Value':'node_ready'
                }

        sock.sendall(pickle.dumps(status_ready, -1))

        # listen for ok message, ack -- loops infinetly
        while True:
            data = recv_data(sock)

            if data:
                data = pickle.loads(data)
                print "client received %s" % data
                break
            else:
                print "listening for status_ready ack"

    else:

        # retry for 2 times TODO

        if post_install_status != True:

            # send node_halt status message to cc
            status_halt = {
                    'Type':'status',
                    'length':1,
                    'Value':'node_halt'
                    }
            sock.sendall(pickle.dumps(status_halt, -1))

            # listen for ok message, ack -- loop infinetly
            while True:
                data = recv_data(sock)

                if data:
                    data = pickle.loads(data)
                    print "client received %s" % data
                    break
                else:
                    print "listening for status_halt ack"
        else:
             
            # send node_ready status message to cc
            status_ready = {
                'Type':'status',
                'Length':1,
                'Value':'node_ready'
                }

            sock.sendall(pickle.dumps(status_ready, -1))

            # listen for ok message, ack -- loops infinetly
            while True:
                data = recv_data(sock)

                if data:
                    data = pickle.loads(data)
                    print "client received %s" % data
                    break
                else:
                    print "listening for status_ready ack"


    # send keep alive messages
    keep_alive(sock)

def processStorageConfig():

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
    print "TODO"

def keep_alive(sock):

    '''
    @author         : Shashaa
    description     : send keep alive messages to CiaC node periodically
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    while True:
        status_alive = {
                'Type': 'status',
                'Length': '1',
                'Value': 'alive'
                }
        sock.sendall(pickle.dumps(status_alive, -1))

        # sleep for keep_alive_sec
        print "***keep_alive***"
        sleep(keep_alive_sec)


# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server socket
server_address = ('127.0.0.1', 6161)
print "connecting to %s port %s " % server_address
sock.connect(server_address)
sock.setblocking(0)
count=0
timeout_sec=1
retry_count=5
keep_alive_sec=10

try:
    # send connect
    connect_pkt = {
            'Type' : 'connect',
            'Length': '1',
            'Value': 1
            }
    print "sending connect_pkt"
    sock.sendall(pickle.dumps(connect_pkt, -1))

    # receive packet using select, retry_count
    while True:
        ready = select.select([sock], [], [], timeout_sec)
        if ready[0]:
            data = sock.recv(1024)
            break
        else:
            count = count + 1
            if count == retry_count:
                print "retry count expired..exiting!!"
                sys.exit(1)
            print "retrying... ", count

    if data:
        data = pickle.loads(data)
        print "client received %s" % data

        # check for status ok
        if data['Type'] == 'status' and data['Value'] == 'ok':
            print "client received %s" % data['Value']

            # send node data
            data = {
                'Type': 'Node_info', 
                'Length': 10, 
                'Value': 
                    {
                    'node_name':'box6',
                    'node_type':'cn',
                    'node_mgmt_ip':'10.10.10.10',
                    'node_data_ip':'172.16.16.16',
                    'node_controller':'ciac6',
                    'node_cloud_name':'cloud6',
                    'node_nova_zone':'',
                    'node_iscsi_iqn':'',
                    'node_swift_ring':'',
                    'node_id':'trans6'
                    }
                }
    

            node_type = 'cn'
            print "sending %s " % data
            print "node_id = %s" % data['Value']['node_id']
            sock.sendall(pickle.dumps(data, -1))

            # receive status message, retry_count
            count=0
            while True:
                ready = select.select([sock], [], [], timeout_sec)
                if ready[0]:
                    data = sock.recv(1024)
                    break
                else:
                    count = count + 1
                    if count == retry_count:
                        print "retry count expired..exiting!!"
                        sys.exit(1)
                    print "retrying... ", count

            if data:
                data = pickle.loads(data)
                print "client received %s" % data
                if data['Type'] == 'status' and data['Value'] == 'ok':
                    print "client received %s" % data['Value']
                    print "Node is setup and ready to use!!!"
                    keep_alive(sock)

                elif data['Type'] == 'status' and data['Value'] == 'build':
                    print "client received %s" % data['Value']

                    if node_type == 'cn':
                        processComputeConfig(sock)
                    elif node_type == 'sn':
                        processStorageConfig(sock)

                else:
                    print "client received invalid status message"
            else:
                print "client did not receive status message, exiting!!!"
                sys.exit(1)

        else:
            print "client did not received status ok"
    else:
        print "client received no data for connect packet"

finally:
    print "closing client socket"
    sock.close()

