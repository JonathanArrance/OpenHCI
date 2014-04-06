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
retry_count = 5
recv_buffer = 4096
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
        sent = sock.sendall(msg)
        if sent == 0:
            count = count+1
            if count >= retry_count:
                logger.sys_error("send failed !!")
                raise RuntimeError("socket connection broken")
                sys.exit()
            else:
                logger.sys_info("socket send data retrying ...")
                time.sleep(1)
        else:
            logger.sys_info("send_data: sent %s bytes" %(sent))
            break



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
            data += sock.recv(recv_buffer)

            if not data:
                logger.sys_info("recv_data: no data received")
                break

            buffer += data
            while True:
                if recv_len is None:
                    if ':' not in buffer:
                        break
                    # remove recv_len bytes from front of buffer
                    # leave any remaining bytes in buffer
                    length_str, ignored, buffer = buffer.partition(':')
                    recv_len = int(length_str)

                if len(buffer) < recv_len:
                    break

                # split off message from remaining bytes
                # leave any remaining bytes in buffer

                message = buffer[:recv_len]
                buffer = buffer[recv_len:]
                recv_len=None

                # process message here
                #return message
                #print message #TEST
                break
            if len(buffer) < recv_len:
                continue
            else:
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
    print "reached end" #TEST
    return message

