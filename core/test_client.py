
import os
import sys
import socket
import pickle
from time import sleep
import select
import transcirrus.core.core_util as core_util


# start of client process
# create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get ciac ip address
ciac_ip = 127.0.0.1

# TEST
#print ciac_ip
#sys.exit()
# TEST
logger.sys_info("ciac_ip: %s" % ciac_ip)

# Connect to the server socket
server_address = (ciac_ip, 6161)
print "connecting to %s port %s " % server_address
sock.connect(server_address)
sock.setblocking(0)
core_util.send_data("1234567890")
