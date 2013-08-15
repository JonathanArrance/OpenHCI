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
#body = '{"server": {"name": "%s", "imageRef": "%s", "key_name": "%s", "flavorRef": "%s", "max_count": 1, "min_count": 1,"networks": [{"uuid": "%s"}], "security_groups": [{"name": "%s"}]}}'
#config_script - op
    #                     sec_group_name - default project security group if none specified
    #                     sec_key_name - default project security key if none specified.
    #                     avail_zone - default availability zone - nova
    #                     network_name - default project net used if none specified
    #                     image_name - default system image used if none specified
    #                     flavor_name - default system flavor used if none specifed
    #                     name - req - name of the server
server = {'sec_group_name':'jontest','avail_zone':'nova','sek_key_name':'keys_new','network_name':'test','image_name':'cirros-0.3.1-x86_64-uec','flavor_name':'m1.tiny','name':'testvm'}
nova.create_server(server)