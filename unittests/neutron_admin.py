#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.common.auth import authorization
from transcirrus.component.neutron.admin_actions import admin_ops


print "Loggin in as the default admin."
#onlyt an admin can create a new user
auth = authorization("admin","test")
#get the user dict
perms = auth.get_auth()
admin = admin_ops(perms)

yo = admin.list_net_quota('30b63ffa0d95440b83d204a2456f16ef')
print yo

show = admin.get_net_quota('30b63ffa0d95440b83d204a2456f16ef')
print show

input_dict = {'project_id':'30b63ffa0d95440b83d204a2456f16ef' ,'subnet_quota': '15','router_quota':'20','network_quota':'17','floatingip_quota':'4','port_quota':'9'}
yo1 = admin.update_net_quota(input_dict)
print yo1
