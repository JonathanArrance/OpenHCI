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
import transcirrus.common.service_control as service_controller


_server_port=6161
keep_alive_sec=10
timeout_sec = 1
#retry_count = 5
retry_count = 1000
recv_buffer = 8192 #TEST 
#Note: the buffer length must be a minimum of x + 1( 1-> for ':') bytes, whee x is the
#length of the total message passed between the client and server i.e.
#number of bytes occupied in senidng the length of the message at he
#begining of the message
dhcp_retry = 5

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

reply_alive = {
'Type' : 'status',
'Length': '1',
'Value': 'alive'
}

#mgmt ip changed
mgmt_ip_chnaged = {
'Type':'status',
'Length':'1',
'Value':'mgmt_ip_changed'
}

gluster_ready = {
'Type':'status',
'Length':'1',
'Value':'gluster_ready'
}

gluster_set = {
'Type':'status',
'Length':'1',
'Value':'node_ready'
}

def send_data(msg, sock):

    global retry_count
    global timeout_sec
    count=0
    totalsent = 0
    # send pkt length
    msglen = len(msg)
    #send_pkt_len(msglen, sock)

    logger.sys_info("send_data: %s bytes" %(msglen))

    # appending size of the message to msg with colon as delimiter
    msg = `msglen`+':'+msg

    while True:
        #print "sending ... %s" %(msg) #TEST
        try:
            
            sent = sock.sendall(msg)
            if sent == 0:
                '''
                Note: This if clause will have no meaning as this method
                continues to send data from string until either all data has
                been sent or an error occurs. None is returned on success. On
                error, an exception is raised, and there is no way to determine
                how much data, if any, was successfully sent.
                '''
                count = count+1
                if count >= retry_count:
                    logger.sys_error("send failed !!")
                    raise RuntimeError("socket connection broken")
                    sys.exit()
                else:
                    logger.sys_info("socket send data retrying ...")
                    time.sleep(1)
            else:
                # None is returned when the data is sucessfully sent
                logger.sys_info("send_data: sent %s bytes" %(sent))
                # print "sent = %s" %(sent) #TEST
                break

        except socket.error , msg:
            logger.sys_error('send_data: Failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            if __debug__ :
                print 'send_data: Failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]

                # retry code, NOT tested
                count = count+1
                if count >= retry_count:
                    logger.sys_error("send failed !!")
                    raise RuntimeError("socket connection broken")
                    sys.exit()
                else:
                    logger.sys_info("socket send data retrying ...")
                    time.sleep(1)
                    continue




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
    data = ""
    buffer=""
    message=""
    recv_len=None
    msglen=0
    global retry_count
    global timeout_sec

    while True:
        ready = select.select([sock], [], [], timeout_sec)
        if ready[0]:
            data = sock.recv(recv_buffer)
            if not data:
                logger.sys_info("recv_data: no data received")
                #print "no data break outer loop" #TEST
                break

            #print "received data... %s" %(data) #TEST
            buffer += data
            #print "buffer append ...%s" %(buffer)         #TEST
            while True:
                if recv_len is None:
                    if ':' not in buffer:
                        #print ": break"  #TEST
                        break
                    # remove recv_len bytes from front of buffer
                    # leave any remaining bytes in buffer
                    length_str, ignored, buffer = buffer.partition(':')
                    recv_len = int(length_str)
                    #print "recv_len... %s" %(recv_len) #TEST

                if len(buffer) < recv_len:
                    #print "len(buf):%s < recv_len" %(len(buffer))         #TEST
                    #print "break inner loop" #TEST
                    break

                # split off message from remaining bytes
                # leave any remaining bytes in buffer

                message = buffer[:recv_len]
                buffer = buffer[recv_len:]
                recv_len=None

                #print "messsag ...%s" %(message) #TEST
               # print "buffer ...%s" %(buffer)  #TEST
                # process message here
                return message
                break
            if len(buffer) < recv_len:
                #print "continue..."              #TEST
                continue
            else:
                #print "break outer loop"              #TEST
                break
        else:
            count = count + 1
            if count >= retry_count:
                logger.sys_error("recv_data: retry count expired")
                if __debug__ :
                    print "recv_data: retry count expired..exiting!!"
                sys.exit(1)
            logger.sys_warning("recv_data: retrying...%s" %(count))
            if __debug__ :
                print "recv_data: retrying... ", count
    return message



def recv_data_alive(sock):

    '''
    @author         : Shashaa
    comment         : receives data from connected socket to sock
                      then deserializes it. Thi s function is exclusively used by keep alive code.
    return value    : received data
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        : This function doesnot exit if loop count expires
    '''
    count=0
    data = ""
    buffer=""
    message=""
    recv_len=None
    msglen=0
    global retry_count
    global timeout_sec

    while True:
        ready = select.select([sock], [], [], timeout_sec)
        if ready[0]:
            data = sock.recv(recv_buffer)
            if not data:
                logger.sys_info("recv_data: no data received")
                #print "no data break outer loop" #TEST
                break

            #print "received data... %s" %(data) #TEST
            buffer += data
            #print "buffer append ...%s" %(buffer)         #TEST
            while True:
                if recv_len is None:
                    if ':' not in buffer:
                        #print ": break"  #TEST
                        break
                    # remove recv_len bytes from front of buffer
                    # leave any remaining bytes in buffer
                    length_str, ignored, buffer = buffer.partition(':')
                    recv_len = int(length_str)
                    #print "recv_len... %s" %(recv_len) #TEST

                if len(buffer) < recv_len:
                    #print "len(buf):%s < recv_len" %(len(buffer))         #TEST
                    #print "break inner loop" #TEST
                    break

                # split off message from remaining bytes
                # leave any remaining bytes in buffer

                message = buffer[:recv_len]
                buffer = buffer[recv_len:]
                recv_len=None

                #print "messsag ...%s" %(message) #TEST
               # print "buffer ...%s" %(buffer)  #TEST
                # process message here
                return message
                break
            if len(buffer) < recv_len:
                #print "continue..."              #TEST
                continue
            else:
                #print "break outer loop"              #TEST
                break
        else:
            count = count + 1
            if count >= retry_count:
                logger.sys_error("recv_data: retry count expired, looping again")
            logger.sys_warning("recv_data: retrying...%s" %(count))
            if __debug__ :
                print "recv_data: retrying... ", count
    return message


