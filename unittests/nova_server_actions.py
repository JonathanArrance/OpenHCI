#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.component.nova.server_action import server_actions
from transcirrus.component.nova.admin_actions import server_admin_actions

print "Loggin in as the default admin."
#onlyt an admin can create a new user
auth = authorization("admin","password")
#get the user dict
perms = auth.get_auth()
action = server_actions(perms)
action2 = server_admin_actions(perms)

#print "Loggin in as the default admin."
#onlyt an admin can create a new user
#auth2 = authorization("admin","password")
#get the user dict
#perms2 = auth2.get_auth()
#action2 = server_actions(perms2)
'''
input_dict = {'server_id':'8ea76508-29f3-4d7e-957e-b2f9c90f2027','project_id':'523e5098be6c4438b428d7f3f94b3a2d','action_type':'SOFT'}
reboot = action.reboot_server(input_dict)
print reboot

input_dict2 = {'server_id':'e25caef9-a5af-4496-80e6-58a57faa0856','project_id':'523e5098be6c4438b428d7f3f94b3a2d','action_type':'SOFT'}
reboot2 = action.reboot_server(input_dict2)
print reboot2

time.sleep(120)


input_dict3 = {'server_id':'8ea76508-29f3-4d7e-957e-b2f9c90f2027','project_id':'523e5098be6c4438b428d7f3f94b3a2d','action_type':'SOFT'}
reboot3 = action2.reboot_server(input_dict3)
print reboot3


input_dict4 = {'server_id':'e25caef9-a5af-4496-80e6-58a57faa0856','project_id':'523e5098be6c4438b428d7f3f94b3a2d','action_type':'SOFT'}
reboot4 = action2.reboot_server(input_dict4)
print reboot4



input_dict = {'server_id':'8ea76508-29f3-4d7e-957e-b2f9c90f2027','project_id':'523e5098be6c4438b428d7f3f94b3a2d','flavor_id':'2'}
resize = action.resize_server(input_dict)
print resize

time.sleep(120)

print 'Confirming server resize'
input_dict2 = {'server_id':'8ea76508-29f3-4d7e-957e-b2f9c90f2027','project_id':'523e5098be6c4438b428d7f3f94b3a2d'}
confirm = action.confirm_resize(input_dict2)
print confirm

print 'Revert server resize'
input_dict3 = {'server_id':'8ea76508-29f3-4d7e-957e-b2f9c90f2027','project_id':'523e5098be6c4438b428d7f3f94b3a2d'}
revert = action.revert_resize(input_dict3)
print revert


input_dict4 = {'server_id':'e25caef9-a5af-4496-80e6-58a57faa0856','project_id':'523e5098be6c4438b428d7f3f94b3a2d','flavor_id':'2'}
resize2 = action.resize_server(input_dict4)
print resize2

time.sleep(120)

print 'Confirming server resize'
input_dict5 = {'server_id':'e25caef9-a5af-4496-80e6-58a57faa0856','project_id':'523e5098be6c4438b428d7f3f94b3a2d'}
confirm2 = action.confirm_resize(input_dict5)
print confirm2


print 'Revert server resize'
input_dict6 = {'server_id':'e25caef9-a5af-4496-80e6-58a57faa0856','project_id':'523e5098be6c4438b428d7f3f94b3a2d'}
revert2 = action.revert_resize(input_dict6)
print revert2
'''

idi = {'instance_id':'73d51f87-7d19-4088-a66f-d960e64986b2','project_id':'a8c44dec2d6e47ad9f06e7af4a4fbaf8'}
pause = action2.pause_server(idi)
print pause
