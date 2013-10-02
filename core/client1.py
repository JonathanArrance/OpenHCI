#! /usr/sbin/python

import os
import socket
import pickle
from time import sleep
import select


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
                'Length': 2, 
                'Value': 
                    {
                    'Node_id':'abcd',
                    'Node_Type':'storage',
                    'Node_IP':'192.168.10.35',
                    'Node_Mgmt_IP':'10.10.10.10'
                    }
                }
    
            print "sending %s " % data
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

                    # accept cinder config info, retry_count
                    count=0
                    while True:
                        ready = select.select([sock], [], [], timeout_sec)
                        if ready[0]:
                            data = sock.recv(1024)
                            break
                        else:
                            count = count + 1
                            if count >= retry_count:
                                print "retry count expired..exiting!!"
                                sys.exit(1)
                                print "retrying... ", count
                    if data:
                        data = pickle.loads(data)
                        print "client received %s" % data
                        if data['Type'] == 'config':
                            print "write config file ... TODO"
                        else:
                            print "client did not receive valid packet"

                    # accept swift config info, retry_count
                    count=0
                    while True:
                        ready = select.select([sock], [], [], timeout_sec)
                        if ready[0]:
                            data = sock.recv(1024)
                            break
                        else:
                            count = count + 1
                            if count >= retry_count:
                                print "retry count expired..exiting!!"
                                sys.exit(1)
                                print "retrying... ", count

                    if data:
                        data = data.pickle.loads(data)
                        print "client received %s" % data
                        if data['Type'] == 'config':
                            print "write config file ... TODO"
                        else:
                            print "client did not receive valid packet"


                else:
                    print "client received invalid status message"
            else:
                print "client did not receive status message"
                sys.exit(1)

        else:
            print "client did not received status ok"
    else:
        print "client received no data for connect packet"

finally:
    print "closing client socket"
    sock.close()


def recv_data(sock):

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
        ready = select.select([sock], [], [], timeout_sec)
        if ready[0]:
            data = sock.recv(1024)
            break
        else:
            count = count + 1
            if count >= retry_count:
                print "retry count expired..exiting!!"
                sys.exit(1)
            print "retrying... ", count
    data = pickle.loads(data)

    return data

