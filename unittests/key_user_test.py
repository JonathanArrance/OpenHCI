#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

sys.path.append('../common')
import logger
import config
from auth import authorization

sys.path.append('/home/jonathan/alpo.0/component/keystone')
from keystone_users import user_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","builder")
#get the user dict
d = a.get_auth()

print "Instantiating user_ops object."
use = user_ops(d)


print "Create a new standard user."
new_user_dict = {"username":'testuser',"password":"test","userrole":"user","email":"test@domain.com","project_name":"demo"}
create = use.create_user(new_user_dict)
print create

print "getting user info"
user_info = {"username":'testuser',"project_name":'demo'}
get = use.get_user_info(user_info)
print get
time.sleep(2)
print "---------------------------------------------"

print "Create a new power user."
new_pu_dict = {"username":'testpuser',"password":"test","userrole":"pu","email":"testpu@domain.com"}
create_pu = use.create_user(new_pu_dict)
print create_pu

print "getting test power user info"
user_info = {"username":'testpuser',"project_name":'demo'}
get_p = use.get_user_info(user_info)
print get_p
time.sleep(2)
print "---------------------------------------------"

print "Create a new admin user."
new_admin_dict = {"username":'testadmin',"password":"test","userrole":"admin","email":"testadmin@domain.com"}
create_admin = use.create_user(new_admin_dict)
print create_admin

print "getting testadmin info"
user_info = {"username":'testadmin',"project_name":'demo'}
get_a = use.get_user_info(user_info)
print get_a
time.sleep(2)
print "---------------------------------------------"

#ROLES NEED TO BE FIXED keep getting 404 error when attempting to add a new role
"""
#add a keystone role to the user
print "Add the Member role to the testuser."
user_role_dict = {"username":"testuser","project_id":"26c877c1d5f7449c93001cc9187754dd","role":"Member"}
role = use.add_role_to_user(user_role_dict)
print role
time.sleep(2)
print "--------------------------------------------"

#remove role from user in a tenant
remove_role = {"username":'testuser',"key_role":'_member_'}
remove = use.remove_role_from_user(remove_role)
print remove
time.sleep(2)
"""
print "---------------------------------------------"

print "toggle user to disable"
toggle = {"username":'testuser',"toggle":'disable'}
tog = use.toggle_user(toggle)
print tog

print "getting testadmin info"
user_info = {"username":'testuser',"project_name":'demo'}
get_t = use.get_user_info(user_info)
print get_t

time.sleep(2)
if(get_t['user_enabled'] == 'FALSE'):
    print "toggle user back to enable"
    toggle = {"username":'testuser',"toggle":'enable'}
    tog_e = use.toggle_user(toggle)
    print tog_e
time.sleep(2)
print "---------------------------------------------"

print "Deleteing a testuser"
delete = {"username":"testuser","userid":get_t['user_id']}
blah = use.remove_user(delete)
print blah

print "---------------------------------------------"