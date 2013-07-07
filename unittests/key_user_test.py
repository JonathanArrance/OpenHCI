#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys

sys.path.append('../common')
import logger
import config
from auth import authorization

sys.path.append('/home/jonathan/alpo.0/component/keystone')
from keystone_users import user_ops

a = authorization("admin","builder")

#get the user dict
d = a.get_auth()
print "unittest"
print d

use = user_ops(d)

#new_user_dict = {"username":'jonjon',"password":"test","userrole":"pu","email":"jon@domain.com"}
#create = use.create_user(new_user_dict)

#print create

#new_user_dict2 = {"username":'jonjon2',"password":"test","userrole":"pu","email":"jon@domain.com","project_name":"demo"}
#create2 = use.create_user(new_user_dict2)

#print create2

#add a keystone role to the user
user_role_dict = {"username":"jonjon2","project_id":"7da21eb21e9541e38e0bce8bf9a7dde4","role":"Member"}
yo = use.add_role_to_user(user_role_dict)
print yo