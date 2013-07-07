#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys

sys.path.append('../common')
import logger
import config
from auth import authorization

sys.path.append('/home/jonathan/alpo.0/component/keystone')
from keystone_tenants import tenant_ops
from keystone_users import user_ops

a = authorization("admin","builder")

#get the user dict
auth = a.get_auth()

proj = tenant_ops(auth)
user = user_ops(auth)

newproj = proj.create_tenant("transcirrus")

print newproj

new_user_dict = {"username":'rob',"password":"test","email":"rob@domain.com","userrole":"user","project_name":newproj['project_name']}

use = user.create_user(new_user_dict)

print use