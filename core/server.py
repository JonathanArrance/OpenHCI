#! /usr/sbin/python

import os
import sys
import socket
from thread import *
import pickle
import select
from time import sleep

timeout_sec=1
count=0
retry_count=5


def recv_data(conn):

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
    count=0
    while True:
        ready = select.select([conn], [], [], timeout_sec)
        if ready[0]:
            data = conn.recv(1024)
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
        data = conn.recv(1024)

        if data:
            data = pickle.loads(data)
            if data['Type'] == 'status' and data['Value'] == 'alive':
                print "***%s***" % data['Value']



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
    try:
        while True:

            # receive data from client, retry_count
            '''
            while True:
                ready = select.select([conn], [], [], timeout_sec)
                if ready[0]:
                    data = conn.recv(1024)
                    break
                else:
                    count = count + 1
                    if count >= retry_count:
                        print "retry count expired..exiting!!"
                        sys.exit(1)
                    print "retrying... ", count
            '''
            data = recv_data(conn)

            # received data from client
            if data:
                data = pickle.loads(data)
                print "data received: %s" % data

                # process packet
                if data['Type'] == 'connect':

                    # construct a TLV status ok packet
                    status_ok = {
                        'Type': 'status',
                        'Length': '1',
                        'Value': 'ok'
                        }
                    conn.sendall(pickle.dumps(status_ok, -1))

                    # recv data, retry_count
                    '''
                    count=0
                    while True:
                        ready = select.select([conn], [], [], timeout_sec)
                        if ready[0]:
                            data = conn.recv(1024)
                            break
                        else:
                            count = count + 1
                            if count >= retry_count:
                                print "retry count expired..exiting!!"
                                sys.exit(1)
                            print "retrying... ", count
                     '''
                    data = recv_data(conn)

                    # received data from client
                    if data:
                        data = pickle.loads(data)
                        print "server received %s" % data

                        # check for the node in DB
                        #result = check_node(data)

                        ''' check for node existence and write if not
                        available. If exists check for node updation if
                        there is no updation then send status_ok. else check
                        for node_type and send status_build message
                         
                        '''

                        '''
                        if result == '':
                            print ""
                        elif result == '':
                            print ""
                        '''

                        # construct status packet
                        status_ok = {
                            'Type': 'status',
                            'Length': '1',
                            'Value': 'ok'
                            }
                        print "sending status_ok"
                        conn.sendall(pickle.dumps(status_ok, -1))
                        # go for keep_alive check
                        keep_alive_check(conn)

                        is_update = True

                        # check for node_type
                        #print "Node type: %s" % data['Values']['Node_Type']
                        if data['Value']['Node_Type'] == 'storage' and is_update:
                            sendBuild(conn)
                        elif data['Value']['Node_Type'] == 'compute' and is_update:
                            sendBuild(conn)
                        
                    else:
                        print "server did not receive any data"
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
        conn.close()


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
               

