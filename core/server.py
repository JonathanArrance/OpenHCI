#! /usr/sbin/python

import os
import sys
import socket
from thread import *
import pickle
import select
from time import sleep

import transcirrus.common.util as util
import transcirrus.database.node_db as node_db

timeout_sec=1
count=0
retry_count=5
recv_buffer=4096


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
            elif data['Value']['node_iscsi_iqn'] != node['node_iscsi_iqn']:
                if data['Value']['node_iscsi_iqn'] == '':
                    update = 'NA'
                else:
                    update = 'OK'

            elif data['Value']['node_swift_ring'] != node['node_swift_ring']:
                if data['Value']['node_swift_ring'] == '':
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
    print "In sendStorageConfig TODO"
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
        print "nova config %s" % config

        # send config
        conn.sendall(pickle.dumps(config, -1))
        print "sent compute node nova config!!"

        # listen for ok message, ack
        data = recv_data(conn)
        if data:
            data = pickle.loads(data)
            print "server received %s" % data
        else:
            print "server did not receive ack for sent nova config for compute node, exiting!!!"
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
            conn.sendall(pickle.dumps(config, -1))
            print "sent compute node ovs config"

            # listen for ok message, ack
            data = recv_data(conn)
            if data:
                data = pickle.loads(data)
                print "server received %s" % data
            else:
                print "serve did not receive ack for sent ovs config structure for compute node,.\
		 exiting"
                sys.exit()

    else:
        print "server did not extract nova config, exiting"
        sys.exit()

    print "ciac server done with sending config files"
    
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
    conn.sendall(pickle.dumps(status_ok, -1))

def recv_data(conn):

    '''
    @author         : Shashaa
    comment         : receives data from socket connected to conn
                      retries 'retry_count' for 'timeout_sec' then exits
                      out of the current thread control
    return value    :
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''
    count=0
    while True:
        ready = select.select([conn], [], [], timeout_sec)
        if ready[0]:
            data = conn.recv(recv_buffer)
            break
        else:
            count = count + 1
            if count >= retry_count:
                print "retry count expired..exiting!!"
                sys.exit(1)
            print "retrying... ", count

    return data


def keep_alive_check(conn):

    '''
    @author         : Shashaa
    comment         : 
    return value    : 
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        :
    '''

    while True:
        ready = select.select([conn], [], [], timeout_sec)
        if ready[0]:
            data = conn.recv(recv_buffer)

            data = pickle.loads(data)
            if data['Type'] == 'status' and data['Value'] == 'alive':
                print "***%s***" % data['Value']
            elif data['Type'] == 'status' and data['Value'] == 'node_ready':
                print "received %s " % data['Value']
            else:
                print "received %s " % data
        else:
            print "ciac server waiting for keep alive messages"


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
        conn.sendall(pickle.dumps(status_build, -1))
    except socket.error , msg:
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
    try:
        while True:

            # receive data from client, retry_count
            data = recv_data(conn)

            # received data from client
            if data:
                data = pickle.loads(data)
                print "data received: %s" % data

                # process packet
                if data['Type'] == 'connect':

                    # construct a TLV status ok packet
                    sendOk(conn)

                    # recv data, retry_count
                    data = recv_data(conn)

                    # received data from client
                    if data:
                        data = pickle.loads(data)
                        print "server received %s" % data

                        # extract node_id from the packet
                        node_id = data['Value']['node_id']

                        # check for the node in DB
                        exists = node_db.check_node_exists(node_id)

                        if exists == 'OK':
                            print "node exists in the DB"

                            # check for updation
                            update = 'NA'
                            update = check_node_update(data)

                            if update == 'OK':
                                print "sending build mesage to %s,node_type: %s" % (node_id,
                                data['Value']['node_type'])

                                sendBuild(conn)

                                node_id = data['Value']['node_id']
                                # check node type
                                if data['Value']['node_type'] == 'sn':
                                    sendStorageConfig(conn, node_id)
                                elif data['Value']['node_type'] == 'cn':
                                    sendComputeConfig(conn, node_id)

                                while True:
        			    ready = select.select([conn], [], [], timeout_sec)
        			    if ready[0]:
            			        data = conn.recv(recv_buffer)
            			        break
                                    else:
                                        print "ciac server waiting for status ready/halt from compute node"
                                if data:
                                    data = pickle.loads(data)
                                    if data['Type'] == 'status':
                                        print "server received %s" % data['Value']
                                        sendOk(conn)
                                        break
                                else:
                                    print "ciac server did not receive any data"

                                print "ciac server listening for keep alive messages"
                                keep_alive_check(conn)

                            # node info has not been changed
                            else:
                                print "node_id:%s,node_type: %s is ready .\
                                to use" % (node_id, data['Value']['node_type'])

                                sendOk(conn)

                                # go for keep_alive check
                                print "ciac server listening for keep alive messages"
                                keep_alive_check(conn)
                                

                        # node does not exists in the ciac DB
                        else:
                            print "new node being inserted in DB"

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
                                    'node_iscsi_iqn':data['Value']['node_iscsi_iqn'],
                                    'node_swift_ring':data['Value']['node_swift_ring']
                                    }
                            # insert into ciac DB
                            insert = node_db.insert_node(input_dict)

                            if insert == 'OK':
                                print "new node %s inserted sucessfully in DB" % node_id

                                # check for node_type, then send build message
                                sendBuild(conn)

                                node_id = data['Value']['node_id']

                                if data['Value']['node_type'] == 'sn':
                                    sendStorageConfig(conn, node_id)
                                elif data['Value']['node_type'] == 'cn':
                                    sendComputeConfig(conn, node_id)

                                while True:
        			    ready = select.select([conn], [], [], timeout_sec)
        			    if ready[0]:
            			        data = conn.recv(recv_buffer)
            			        break
                                    else:
                                        print "ciac server waiting for status ready/halt from compute node"
                                if data:
                                    data = pickle.loads(data)
                                    if data['Type'] == 'status':
                                        print "server received %s" % data['Value']
                                        sendOk(conn)
                                        break
                                else:
                                    print "ciac server did not receive any data"

                                # go for keep alive check
                                print "ciac server listening for keep alive messages"
                                keep_alive_check(conn)

                            else:
                                print "error in inserting new node in DB, exiting !!!"
                                sys.exit()

                    
                    # server did not receive node_info
                    else:
                        print "server did not receive any data"
                # handshake process failure
                else:
                    print "server did not receive connect, exiting"
                    sys.exit(1)


            else:
                print "no more data"
                break
    except socket.error , msg:
        print 'Failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    finally:
       print "In finally block"
       # conn.close()


# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket
sock.bind(('', 6161))

sock.listen(5)

try:
    while True:
        print "waiting for connection...IP: %s, port: %s" % ("127.0.0.1", "6161")
        conn, client_addr = sock.accept()
        print "connection from ", client_addr
        start_new_thread(client_thread, (conn, client_addr))
except socket.error , msg:
    print 'Failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
finally:
    sock.close()
               

