#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.component.nova.server_action import server_actions

print "Loggin in as the default admin."
#onlyt an admin can create a new user
auth = authorization("admin","password")
#get the user dict
perms = auth.get_auth()

action = server_actions(perms)
#input_dict = {'server_id':'3e8e74fa-cd4d-41d6-9e34-73614418b3db','action_type':'SOFT'}
#reboot = action.reboot_server(input_dict)

input_dict = {'server_id':'3e8e74fa-cd4d-41d6-9e34-73614418b3db','flavor_id':'2'}
resize = action.resize_server(input_dict)
print resize

time.sleep(60)
'''
print 'Confirming server resize'
confirm = action.confirm_resize('3e8e74fa-cd4d-41d6-9e34-73614418b3db')
print confirm
'''

print 'Revert server resize'
revert = action.revert_resize('3e8e74fa-cd4d-41d6-9e34-73614418b3db')
print revert