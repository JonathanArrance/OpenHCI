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
auth = authorization("admin","builder")
#get the user dict
perms = auth.get_auth()

nova = server_ops(perms)
print "Createing a new virtual instance"
server = {'sec_group_name':'jontest','avail_zone':'nova','sec_key_name':'keys_new','network_name':'test','image_name':'cirros-0.3.1-x86_64-uec','flavor_name':'m1.tiny','name':'testvm'}
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
