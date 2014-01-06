#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.component.nova.server import server_ops
from transcirrus.component.nova.storage import server_storage_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
auth = authorization("testuser","test")
#get the user dict
perms = auth.get_auth()
store = server_storage_ops(perms)

nova = server_ops(perms)
print "Createing a new virtual instance"
server = {'sec_group_name':'testproj','avail_zone':'nova','sec_key_name':'test_keys','network_name':'testnet','image_name':'cirros-64','flavor_name':'m1.tiny','name':'testvm'}
nova.create_server(server)

'''
input_dict = {'project_id': '0591dbde27ce4904b50cdd0d598e1d7e' ,'instance_id': '3e8e74fa-cd4d-41d6-9e34-73614418b3db','volume_id': '15ecae50-0975-408c-b69a-b54e6530bf4b','mount_point': '/dev/vdc'}
attach = store.attach_vol_to_server(input_dict)

print attach

time.sleep(10)

input_dict2 = {'project_id': '0591dbde27ce4904b50cdd0d598e1d7e' ,'instance_id': '3e8e74fa-cd4d-41d6-9e34-73614418b3db','volume_id': '15ecae50-0975-408c-b69a-b54e6530bf4b'}
detach = store.detach_vol_from_server(input_dict2)

print detach

nova = server_ops(perms)
print "Createing a new virtual instance"
server = {'sec_group_name':'testgroup','avail_zone':'nova','sec_key_name':'testkey','network_name':'testnet','image_name':'cirros-64','flavor_name':'m1.tiny','name':'testvm'}
nova.create_server(server)

print "---------------------------------------"
time.sleep(2)

print "List the virtual intances in the database"
serv_list = nova.list_servers()
print serv_list
print "---------------------------------------"
time.sleep(2)

print "Get the info for the virtual instances in the database."
for serv in serv_list:
    get_server = nova.get_server(serv['server_name'])
    print get_server
print "---------------------------------------"
time.sleep(2)

print "Update the virtual instance"
up_dict = {'server_name':"testtest",'new_server_name':"testtest20"}
update = nova.update_server(up_dict)
print update
print "---------------------------------------"
time.sleep(2)

print "Deleteing the virtual instance"
delete = nova.delete_server('testtest20')
print delete
'''
