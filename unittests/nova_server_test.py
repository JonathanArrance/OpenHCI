#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

sys.path.append('../common')
import logger
import config
from auth import authorization

sys.path.append('/home/jonathan/alpo.0/component/nova')
from server import server_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","builder")
#get the user dict
d = a.get_auth()

nova = server_ops(d)

#config_script - op
    #                     security_group - default project group if none specified
    #                     avail_zone - default availability zone - nova
    #                     server - Server
    #                     image - req - image name
    #                     flavor - req - flavor name
    #                     name - req - name of the server
#server = {}
#nova.creater_server()

print "Createing security group with default ports"
#createa security group with default ports
create_group = {"group_name": 'test_group',"group_desc": 'This is a test'}
sec_group = nova.create_sec_group(create_group)
print sec_group
print "------------------------------------------------"

print "Createing security group with custom ports"
#create a security group with the defualt ports
create_group2 = {"group_name": 'test_group2',"group_desc": 'This is a test2',"ports":[139,22,80]}
sec_group2 = nova.create_sec_group(create_group2)
print sec_group2
print "------------------------------------------------"