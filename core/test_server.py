
import os
import sys
import socket
from thread import *
import pickle
import select
from time import sleep
import transcirrus.core.core_util as core_util



def client_thread(conn, client_addr):
    print "ciac_server: Thread created for a connection from host:", client_addr

    data = core_util.recv_data(conn)
    print data
    conn.close()
    exit


# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket on all interfaces
sock.bind(('', core_util._server_port))

sock.listen(5)

try:
    while True:
        conn, client_addr = sock.accept()
        #logger.sys_info("connection from: ", (client_addr))
        print "ciac_server: connection from ", client_addr
        start_new_thread(client_thread, (conn, client_addr))
except socket.error , msg:
    sys.exit()
finally:
    sock.close()
               

