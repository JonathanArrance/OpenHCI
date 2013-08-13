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
#INPUT: create_dict - config_script - op
    #   security_group - default project group if none specified
    #   avail_zone - default availability zone - nova
    #   server - Server
    #   image - req - image name
    #   flavor - req - flavor name
    #   name - req - name of the server
server = {'security_group':'default','avail_zone':'nova','server':}
nova.creater_server()