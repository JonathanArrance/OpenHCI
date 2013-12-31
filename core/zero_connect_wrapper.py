#! /usr/sbin/python

import os
import sys
import subprocess
import transcirrus.common.util as util
import transcirrus.database.node_db as node_db
import transcirrus.common.service_control as service_controller
import transcirrus.common.logger as logger
"""
DESC: zero connect wrapper script:
    - get DHCP server IP
    - ping test
    -  invoke zero connect client process
INPUT: 
OUTPUT: 
NOTE: 
"""

# get DHCP server IP
dhcp_server = util.getDhcpServer()

# ping test
status = util.ping_ip(dhcp_server)
if status != 'OK' :
    logger.sys_info("dhcp server ping success")
else :
    logger.sys_error("dhcp server ping failure")
    sys.exit()

# invoke zero client process
out = subprocess.call(" python /usr/local/lib/python2.7/dist-packages/transcirrus/core/cn_sn_client.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#os.system("python /usr/local/lib/python2.7/dist-packages/transcirrus/core/cn_sn_client.py")
console_out = out.stdout.readlines()
console_err = out.stderr.readlines()
print "**********console out************"
print console_out
print "**********console out************"
print console_err
