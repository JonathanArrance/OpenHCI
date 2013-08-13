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

print "Createing security group with default ports - default"
#create a security group with default ports
create_group = {"group_name": 'jon',"group_desc": 'This is a test'}
sec_group = nova.create_sec_group(create_group)
print sec_group
print "------------------------------------------------"
time.sleep(3)

print "Createing security group with custom ports"
#create a security group with the defualt ports
create_group2 = {"group_name": 'test_group2',"group_desc": 'This is a test2',"ports":[139,22,80]}
sec_group2 = nova.create_sec_group(create_group2)
print sec_group2
print "------------------------------------------------"
time.sleep(3)

print "creating a new default security key"
create_def_key = nova.create_sec_keys("default_keys")
print create_def_key
print "------------------------------------------------"
time.sleep(3)

#try code path that does not include default key
print "creating a new security key"
create_def_key2 = nova.create_sec_keys("keys_new")
print create_def_key2
print "------------------------------------------------"
time.sleep(3)

print "listing the security keys"
list_key = nova.list_sec_keys()
print list_key
print "-------------------------------------------------"
time.sleep(3)

print "listing the security groups"
list_group = nova.list_sec_group()
print list_group
print "-------------------------------------------------"
time.sleep(3)

print "Get detailed security group info"
get_group = nova.get_sec_group("jon")
print get_group
print "------------------------------------------------"
time.sleep(3)

#try code path that does not include default key
print "Get the detailed security group info"
get_group2 = nova.get_sec_group("test_group2")
print get_group2
print "------------------------------------------------"
time.sleep(3)

#print "Get detailed security group info"
#get_group3 = nova2.get_sec_group("jontest")
#print get_group3
#print "------------------------------------------------"
#time.sleep(3)

#try code path that does not include default key
#print "Get the detailed security group info"
#get_group4 = nova2.get_sec_group("jontest2")
#print get_group4
#print "------------------------------------------------"
#time.sleep(3)

print "Get detailed security key info"
get_key = nova.get_sec_keys("default_keys")
print get_key
print "------------------------------------------------"
time.sleep(3)

#try code path that does not include default key
print "Get the detailed security key info"
get_key2 = nova.get_sec_keys("keys_new")
print get_key2
print "------------------------------------------------"
time.sleep(3)

print "deleteing the default security group"
del_group2 = nova.delete_sec_group("jon")
print del_group2
print "-------------------------------------------------"
time.sleep(2)

print "deleteing the security group"
del_group = nova.delete_sec_group("test_group2")
print del_group
print "-------------------------------------------------"
time.sleep(2)

print "deleteing the security key"
del_key = nova.delete_sec_group("keys_new")
print del_key
print "-------------------------------------------------"
time.sleep(2)

print "deleteing the default security key"
del_key2 = nova.delete_sec_group("default_keys")
print del_key2
print "-------------------------------------------------"
time.sleep(2)