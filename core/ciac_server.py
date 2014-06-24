#!/usr/bin/python2.7

import os
import sys
import socket
from thread import *
import pickle
import select
from time import sleep

import transcirrus.common.util as util
import transcirrus.database.node_db as node_db
import transcirrus.common.node_util as node_util
import transcirrus.common.logger as logger
import transcirrus.core.core_util as core_util
from transcirrus.common.gluster import gluster_ops

count=0

def setDbFlag(node_id, flag):
    '''
    @author         : Shashaa
    comment         : set appropriate flag in the DB
                      Input: node_id and flag variable to set
    return value    : 
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    if flag == 'node_ready':
        r_dict = node_util.set_node_ready_flag(node_id)
        if r_dict['ready_flag_set'] == 'SET':
            logger.sys_info("ready flag set success, node_id: %s" %(node_id))
            if __debug__ :
                print "ready flag set success, node_id: %s" % node_id
        else:
            logger.sys_error("ready flag set failure !!! node_id: %s" %(node_id))
            if __debug__ :
                print "ready flag set failure !!! node_id: %s" % node_id
            # TODO
        r_dict = node_util.clear_node_fault_flag(node_id)
        if r_dict['fault_flag_set'] == 'UNSET':
            logger.sys_info("fault flag clear success")
            if __debug__ :
                print "fault flag clear success"
        else:
            logger.sys_error("fault flag clear failure !!!, node_id: %s" %(node_id))
            if __debug__ :
                print "fault flag clear failure !!!, node_id: %s" % node_id
            # TODO

    elif flag == 'node_halt':
        r_dict = node_util.set_node_fault_flag(node_id)
        if r_dict['fault_flag_set'] == 'SET':
            logger.sys_info("fault flag set success, node_id: %s" %(node_id))
            if __debug__ :
                print "fault flag set success, node_id: %s" % node_id
        else:
            logger.sys_error("fault flag set failure!!!, node_id: %s" %(node_id))
            if __debug__ :
                print "fault flag set failure!!!, node_id: %s" % node_id
            # TODO
        r_dict = node_util.set_node_ready_flag(node_id)
        if r_dict['ready_flag_set'] == 'SET':
            logger.sys_info("ready flag set success, node_id: %s" %(node_id))
            if __debug__ :
                print "ready flag set success, node_id: %s" % node_id
        else:
            logger.sys_error("ready flag set failure!!!, node_id: %s" %(node_id))
            if __debug__ :
                print "ready flag set failure!!!, node_id: %s" % node_id
            # TODO
    else:
        logger.sys_error("ERROR:received %s in staus message from node_id: %s" %(data['Value'], node_id))
        if __debug__ :
            print "ERROR:received %s in staus message from node_id: %s" % (data['Value'], node_id)

def check_node_update(data):

    '''
    @author         : Shashaa
    comment         : get the node from TC ciac DB, check for any
                      mismatch in node_info.
                      Input: data dictionary of node_info
    return value    : OK if there is any mismatch, else NA
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    update = 'NA'
    node_id = data['Value']['node_id']

    node = node_db.get_node(node_id)

    if node == 'NA' or node == 'ERROR':
        logger.sys_error("node_id : %s not found in the DB, exiting !!!" %(node_id))
        if __debug__ :
            print "node_id : %s not found in the DB, exiting !!!" % node_id
        sys.exit()
    else:
        if node['status'] == 'OK':

            # check for mismatch records

            if data['Value']['node_data_ip'] != node['node_data_ip']:
                update = 'OK'
            elif data['Value']['node_mgmt_ip'] != node['node_mgmt_ip']:
                update = 'OK'
            elif data['Value']['node_controller'] != node['node_controller']:
                update = 'OK'
            elif data['Value']['node_cloud_name'] != node['node_cloud_name']:
                update = 'OK'
            elif data['Value']['node_nova_zone'] != node['node_nova_zone']:
                if data['Value']['node_nova_zone'] == '':
                    update = 'NA'
                else:
                    update = 'OK'

    return update


def sendStorageConfig(conn, node_id):

    '''
    @author         : Shashaa
    comment         : pulls storage nodes default configurationa and
                      sends it to node via socket
                      Input: socket descriptor fro communication
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''

    # get cinder config
    config = node_db.get_node_cinder_config(node_id)
    node_info = node_db.get_node(node_id)

    if config:
        #add the Gluster storage node before configureing cinder
        SNglusterOperations(conn,node_info['node_data_ip'])

        core_util.send_data(pickle.dumps(config, -1), conn)
        logger.sys_info("node_id: %s, sent storage node config files")
        if __debug__ :
            print "node_id: %s, sent storage node config files"

        # listen for ok ack message
        data = core_util.recv_data(conn)
        if data:
            data = pickle.loads(data)
            if data['Type'] == 'status'  and data['Value'] == 'ok':
                logger.sys_info("node_id: %s, ciac server received %s" %(node_id, data['Value']))
            else:
                logger.sys_error("node_id: %s, ciac server received %s" %(node_id, data['Value']))
                sys.exit()
            if __debug__ :
                print "node_id: %s, ciac server received %s" % (node_id, data)
        else:
            logger.sys_error("node_id: %s, ciac server did not receiv ok ack for config files" %(node_id))
            if __debug__ :
                print "node_id: %s, ciac server did not receiv ok ack for config files" % node_id
            sys.exit()

    else:
        logger.sys_error("node_id: %s, ciac server failure in extracting storage node config files" %(node_id))
        if __debug__ :
            print "node_id: %s, ciac server failure in extracting storage node config files" % node_id

    logger.sys_info("node_id: %s, ciac server done with sending storage config files" %(node_id))
    if __debug__ :
        print "node_id: %s, ciac server done with sending storage config files" % node_id

def sendComputeConfig(conn, node_id):

    '''
    @author         : Shashaa
    comment         : pulls out compute node default configration and
                      sends it to new node via socket
                      Input: socket desriptor
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    # get compute node nova config
    config = node_db.get_node_nova_config(node_id)
    if config:
        logger.sys_info("node_id: %s got nova config from DB" %(node_id))
        #logger.sys_info("node_id: %s nova config %s" %(node_id, config))
        if __debug__ :
            #print "node_id: %s nova config %s" % (node_id, config)
            print "node_id: %s got nova config from DB" %(node_id)

        # send config
        #conn.sendall(pickle.dumps(config, -1))
        core_util.send_data(pickle.dumps(config, -1), conn)
        logger.sys_info("node_id: %s sent cn nova config!!" %(node_id))
        if __debug__ :
            print "node_id: %s sent cn nova config!!" % node_id
            print config #TEST

        # listen for ok message, ack
        data = core_util.recv_data(conn)
        if data:
            data = pickle.loads(data)
            if data['Type'] == 'status'  and data['Value'] == 'ok':
                logger.sys_info("node_id: %s, ciac server received %s" %(node_id, data['Value']))
            else:
                logger.sys_error("node_id: %s, ciac server received %s" %(node_id, data['Value']))
                sys.exit()
            if __debug__ :
                print "node_id: %s ciac server received %s" % (node_id, data)
        else:
            logger.sys_error("node_id: %s ciac server NOT received ok ack for cn nova conf exiting!!!" %(node_id))
            if __debug__ :
                print "node_id: %s ciac server NOT received ok ack for cn nova conf exiting!!!" % (node_id)
            sys.exit()

        # get ovs config for compute node
        config = node_db.get_node_neutron_config(node_id)
        if config:

            '''
            here we are sending the complete neutron config structure,
            the receiving compute node should extract necessary config
            structure
            '''
            #print "sending ovs conf %s" % config
            #conn.sendall(pickle.dumps(config, -1))
            core_util.send_data(pickle.dumps(config, -1), conn)
            logger.sys_info("node_id: %s sent cn ovs conf" %(node_id))
            if __debug__ :
                print "node_id: %s sent cn ovs conf" % (node_id)

            # listen for ok message, ack
            data = core_util.recv_data(conn)
            if data:
                data = pickle.loads(data)
                if data['Type'] == 'status' and data['Value'] == 'ok': 
                    logger.sys_info("node_id: %s, ciac server received %s" %(node_id, data['Value']))
                else:
                    logger.sys_error("node_id: %s, ciac server received %s" %(node_id, data['Value']))
                    sys.exit()
                if __debug__ :
                    print "node_id: %s ciac server received %s" % (node_id, data)
            else:
                logger.sys_error("node_id: %s ciac server NOT received ok ack for cn ovs conf" %(node_id))
                if __debug__ :
                    print "node_id: %s ciac server NOT received ok ack for cn ovs conf" % (node_id)
                sys.exit()
        else:
            logger.sys_error("node_id: %s Error in get neutron config from DB" %(node_id))
            if __debug__:
                print "node_id: %s Error in get neutron config from DB" %(node_id)


    else:
        logger.sys_error("node_id: %s Error in get nova config" %(node_id))
        if __debug__ :
            print "node_id: %s Error in get nova config" % (node_id)
        sys.exit()

    logger.sys_info("node_id:%s ciac server send config completed" %(node_id))
    if __debug__ :
        print "node_id:%s ciac server send config completed" % (node_id)
    
def SNglusterOperations(conn,data_ip):
    '''
    @author:
    comments: Carrying out various operations like adding a brick, listing
    volumes and rebalancing all the current volumes 
    '''
    #HUGE HACK - not going to work.
    input_dict = {'username':'admin','user_level':1,'is_admin':1,'obj':1}
    gluster = gluster_ops(input_dict)

    new = gluster.attach_gluster_peer(data_ip)
    glust_vols = []
    if new == "OK":
        #get the gluster volumes on the core node
        glust_vols = gluster.list_gluster_volumes()
    else:
        SNglusterOperations(conn,data_ip)

    #adding brick to all the listed volumes
    for vol in glust_vols:
        print vol
        logger.sys_info('Adding storage to gluster volume %s'%(vol))
        brick = "%s:/data/gluster/%s"%(data_ip,vol)
        print brick
        expand = {'vol_name':"%s",'brick':"%s"%(vol,brick)}
        add_storage = gluster.add_gluster_brick(expand)
        if add_storage == "OK":
            print "Success: Brick %s added to volume %s"%(brick,vol)
            logger.sys_info("Success: Brick %s added to volume %s"%(brick,vol))
        else:
            print "Error: Brick %s not added to volumes %s"%(brick,vol)
            logger.sys_info("Error: Brick %s not added to volumes %s"%(brick,vol))

        #rebalance the volume over the new brick
        rebalance = gluster.rebalance_gluster_volume(vol)
        if rebalance == 'OK':
            logger.sys_info("Success: volume %s rebalanced."%(vol))
        elif rebalance == 'ERROR':
            logger.sys_info("Error: volumes %s not rebalanced"%(vol))

def handle():

    '''
    @author         : Shashaa
    comment         : handle exception in node_type
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        : TODO
    '''
    print "Unknowm node_type"
    sys.exit()


def sendOk(conn):

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
    #conn.sendall(pickle.dumps(status_ok, -1))
    core_util.send_data(pickle.dumps(status_ok, -1), conn)


def keep_alive_check(node_id, conn):

    '''
    @author         : Shashaa
    comment         : Send keep alive status messages 
    return value    : 
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    terminate=0
    while True:
        status_alive = {
                'Type': 'status',
                'Length': '1',
                'Value': 'alive'
                }
        logger.sys_info("node_id: %s ***keep_alive***" %(node_id))
        if __debug__ :
            print "node_id: %s ***keep_alive***" %(node_id)
        #conn.sendall(pickle.dumps(status_alive, -1))
        core_util.send_data(pickle.dumps(status_alive, -1), conn)
        data = core_util.recv_data_alive(conn)
        if data:
            data = pickle.loads(data)
            if data['Type'] == 'status' and data['Value'] == 'alive':
                logger.sys_info("node_id: %s ***alive***" %(node_id))
                if __debug__ :
                    print "node_id: %s ***alive***" %(node_id)
            else:
                logger.sys_info("node_id: %s keep alive error received %s" %(node_id, data))
        else:
            logger.sys_info("node_id: %s keep alive reply not received" %(node_id))

        # sleep for keep_alive_sec
        sleep(core_util.keep_alive_sec)


def sendBuild(conn):

    '''
    @author         : Shashaa
    comment         : will construct and send build status message to
                      newly connected node to the cluster
    return value    : 
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    status_build = {
            'Type':'status', 
            'Length':'1', 
            'Value':'build'
            }
    try:
        #conn.sendall(pickle.dumps(status_build, -1))
        core_util.send_data(pickle.dumps(status_build, -1), conn)
    except socket.error , msg:
        logger.sys_error('Failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        if __debug__ :
            print 'Failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()


def client_thread(conn, client_addr):
    '''
    @author         : Shashaa
    comment         : contol thread that is called for each client
                      connection from nodes inserted into the cluster.
                      * does connection handshaking
                      * receives node information
                      * processes configuration of storage, compute node
                      Input: connection descriptor, client address
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    #logger.sys_info("Thread created for a connection from host: %s" %(client_addr))
    print "ciac_server: Thread created for a connection from host:", client_addr
    try:
        while True:

            # receive data from client, retry_count
            data = core_util.recv_data(conn)

            # received data from client
            if data:
                data = pickle.loads(data)
                logger.sys_info("ciac_server: received: %s" %(data))
                if __debug__:
                    print "ciac_server: received: %s" % data

                # process packet
                if data['Type'] == 'connect':

                    # send a TLV status ok packet
                    sendOk(conn)
                    logger.sys_info("ciac_server: sent ok ack for connect")
                    if __debug__ :
                        print "ciac_server: sent ok ack for connect"


                    # recv data, retry_count
                    data = core_util.recv_data(conn)

                    # received data from client
                    if data:
                        data = pickle.loads(data)
                        logger.sys_info("ciac_server: received: %s" %(data))
                        if __debug__ :
                            print "ciac_server: received %s" % data

                        # extract node_id from the packet
                        node_id = data['Value']['node_id']

                        # check for the node in DB
                        exists = node_db.check_node_exists(node_id)

                        if exists == 'OK':
                            logger.sys_info("node_id: %s exists in the DB" %(node_id))
                            if __debug__ :
                                print "node_id: %s exists in the DB" % (node_id)

                            # check for updation
                            update = 'NA'
                            update = check_node_update(data)

                            if update == 'OK':
                                logger.sys_info("node_id: %s conflicts with default DB" %(node_id))
                                logger.sys_info("node_id: %s sending build message node_type: %s" %(node_id, data['Value']['node_type']))
                                if __debug__ :
                                    print "node_id: %s conflicts with default DB" % (node_id)
                                    print "node_id: %s sending build message node_type: %s" % (node_id, data['Value']['node_type'])

                                sendBuild(conn)

                                node_id = data['Value']['node_id']
                                # check node type
                                if data['Value']['node_type'] == 'sn':
                                    sendStorageConfig(conn, node_id)
                                elif data['Value']['node_type'] == 'cn':
                                    sendComputeConfig(conn, node_id)

                                while True:
                                    ready = select.select([conn], [], [], core_util.timeout_sec)
                                    if ready[0]:
                                        #data = conn.recv(core_util.recv_buffer)
                                        data = core_util.recv_data(conn)
                                        break
                                    else:
                                        logger.sys_warning("node_id: %s ciac server waiting for status ready/halt from cn" %(node_id))
                                        if __debug__ :
                                            print "node_id: %s ciac server waiting for status ready/halt from cn" %(node_id)
                                if data:
                                    data = pickle.loads(data)
                                    if data['Type'] == 'status':
                                        logger.sys_info("node_id: %s ciac server received %s" %(node_id, data['Value']))
                                        logger.sys_info("node_id: %s ciac server sending ok ack" %(node_id))
                                        if __debug__ :
                                            print "node_id: %s ciac server received %s" %(node_id, data['Value'])
                                            print "node_id: %s ciac server sending ok ack" %(node_id)
                                        sendOk(conn)
                                        setDbFlag(node_id, data['Value'])
                                    else:
                                        logger.sys_error("node_id: %s ciac server received non status message" %(node_id))
                                        if __debug__ :
                                            print "node_id: %s ciac server received non status message" % (node_id)
                                        sys.exit()

                                else:
                                    logger.sys_error("node_id: %s ciac server did not receive any data" %(node_id))
                                    if __debug__ :
                                        print "node_id: %s ciac server did not receive any data" %(node_id)

                                logger.sys_info("node_id: %s ciac server sending keep alive messages" %(node_id))
                                if __debug__ :
                                    print "node_id: %s ciac server sending keep alive messages" % (node_id)
                                keep_alive_check(node_id, conn)

                            # node info has not been changed
                            else:
                                logger.sys_info("node_id:%s,node_type: %s is ready to use" %(node_id, data['Value']['node_type']))
                                if __debug__ :
                                    print "node_id:%s,node_type: %s is ready to use" % (node_id, data['Value']['node_type'])

                                sendOk(conn)
                                # proactively setting Db flag, may be # redundant ? TODO
                                setDbFlag(node_id, 'node_ready')

                                # go for keep_alive check
                                logger.sys_info("node_id: %s ciac server sending keep alive messages" %(node_id))
                                if __debug__ :
                                    print "node_id: %s ciac server sending keep alive messages" % (node_id)
                                keep_alive_check(node_id, conn)
                                

                        # node does not exists in the ciac DB
                        else:
                            logger.sys_info("node_id: %s new node being inserted in DB" %(node_id))
                            if __debug__ :
                                print "node_id: %s new node being inserted in DB" %(node_id)

                            #global input_dict
                            # make a DB compatible dictionary 
                            input_dict = {
                                    'node_id':data['Value']['node_id'],
                                    'node_name':data['Value']['node_name'],
                                    'node_type':data['Value']['node_type'],
                                    'node_data_ip':data['Value']['node_data_ip'],
                                    'node_mgmt_ip':data['Value']['node_mgmt_ip'],
                                    'node_controller':data['Value']['node_controller'],
                                    'node_cloud_name':data['Value']['node_cloud_name'],
                                    'node_nova_zone':data['Value']['node_nova_zone'],
                                    #'node_iscsi_iqn':data['Value']['node_iscsi_iqn'],
                                    #'node_swift_ring':data['Value']['node_swift_ring']
                                    }

                            # insert into ciac DB
                            insert = node_db.insert_node(input_dict)

                            if insert == 'OK':
                                logger.sys_info("node_id %s inserted sucessfully in DB" %(node_id))
                                if __debug__ :
                                    print "node_id %s inserted sucessfully in DB" % (node_id)

                                # check for node_type, then send build message
                                sendBuild(conn)

                                node_id = data['Value']['node_id']

                                if data['Value']['node_type'] == 'sn':
                                    sendStorageConfig(conn, node_id)
                                elif data['Value']['node_type'] == 'cn':
                                    sendComputeConfig(conn, node_id)

                                while True:
                                    ready = select.select([conn], [], [], core_util.timeout_sec)
                                    if ready[0]:
                                        #data = conn.recv(core_util.recv_buffer)
                                        data = core_util.recv_data(conn)
                                        break
                                    else:
                                        logger.sys_warning("node_id: %s ciac server waiting for status ready/halt" %(node_id))
                                        if __debug__ :
                                            print "node_id: %s ciac server waiting for status ready/halt" % (node_id)
                                if data:
                                    print data
                                    data = pickle.loads(data)
                                    if data['Type'] == 'status':
                                        logger.sys_info("node_id: %s ciac server received %s" %(node_id, data['Value']))
                                        logger.sys_info("node_id: %s ciac server sent ok ack" %(node_id))
                                        if __debug__ :
                                            print "node_id: %s ciac server received %s" %(node_id, data['Value'])
                                            print "node_id: %s ciac server sent ok ack" %(node_id)
                                        sendOk(conn)
                                        setDbFlag(node_id, data['Value'])
                                else:
                                    logger.sys_error("node_id: %s ciac server did not receive any data" %(node_id))
                                    if __debug__ :
                                        print "node_id: %s ciac server did not receive any data" % (node_id)

                                # go for keep alive check
                                logger.sys_info("node_id: %s ciac server sending keep alive messages" %(node_id))
                                if __debug__ :
                                    print "node_id: %s ciac server sending keep alive messages" % (node_id)
                                keep_alive_check(node_id, conn)

                            else:
                                logger.sys_error("node_id: %s error in inserting in DB, exiting !!!" %(node_id))
                                if __debug__ :
                                    print "noe_id: %s error in inserting in DB, exiting !!!" % (node_id)
                                sys.exit()

                    
                    # server did not receive node_info
                    else:
                        logger.sys_error("ciac_server: did not receive any data")
                        if __debug__ :
                            print "ciac_server: did not receive any data"
                # handshake process failure
                else:
                    logger.sys_error("ciac_server: did not receive connect, exiting")
                    if __debug__ :
                        print "ciac_server: did not receive connect, exiting"
                    sys.exit(1)


            else:
                logger.sys_error("ciac_server: no data received")
                if __debug__ :
                    print "ciac_server: no data received"
                break
    except socket.error , msg:

        if __debug__ :
            print 'Failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        logger.sys_error('Failed. Error Code : ' + str(msg[0]) + 'Message ' + msg[1])
        sys.exit()
    finally:
        logger.sys_warning("ciac_server: In finally block, node_id: %s" %(node_id))
        if __debug__ :
            print "ciac_server: In finally block, node_id: %s" %(node_id)
       # conn.close()


# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind it to data network interface bind's it to physical interface
sock.setsockopt(socket.SOL_SOCKET, 25, "bond1"+'\0')

# bind the socket on all interfaces
sock.bind(('', core_util._server_port))

sock.listen(5)

try:
    while True:
        logger.sys_info("ciac_server: waiting for connection...on %s of ciac server, port: %s" %("bond1", "6161"))
        if __debug__ :
            print "ciac_server: waiting for connection...on %s of ciac server, port: %s" % ("bond2", "6161")
        conn, client_addr = sock.accept()
        #logger.sys_info("connection from: ", (client_addr))
        print "ciac_server: connection from ", client_addr
        start_new_thread(client_thread, (conn, client_addr))
except socket.error , msg:
    logger.sys_error('ciac_server: Failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    if __debug__ :
        print 'ciac_server: Failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
finally:
    sock.close()
               

