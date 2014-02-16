#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

import transcirrus.common.logger
import transcirrus.common.config
from transcirrus.common.auth import authorization

from transcirrus.component.keystone.keystone_users import user_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","newpass")
#get the user dict
d = a.get_auth()

print "Instantiating user_ops object."
use = user_ops(d)
"""
print "listing orphaned users"
orph = use.list_orphaned_users()
print orph
"""

print "Create a new standard user with no project."
new_user_dict = {"username":'keven',"password":"test","user_role":"pu","email":"keven@domain.com"}
create = use.create_user(new_user_dict)
print create


time.sleep(2)
#print "Adding user %s to demo project" %(create['username'])
add_user_dict = {"username":"keven","user_role":'pu',"project_id":'0a206d3822c54da2981a6196ea4dec31'}
add = use.add_user_to_project(add_user_dict)
print add

'''
print "Create a new standard user."
new_user_dict = {"username":'ralph',"password":"test","userrole":"user","email":"ralph@domain.com","project_id":"5b5a1f8784a742bc8bae98021d7e884b"}
create = use.create_user(new_user_dict)
print create


print "getting user info"
user_info = {"username":'keven2',"project_name":'testproj'}
get = use.get_user_info(user_info)
print get
time.sleep(2)
print "---------------------------------------------"

print "Create a new power user."
new_pu_dict = {"username":'shitbird6',"password":"test","userrole":"user","email":"testpu@domain.com"}
create_pu = use.create_user(new_pu_dict)
print create_pu

print "Create a new standard user."
new_user_dict = {"username":'POWER4',"password":"test","userrole":"pu","email":"power@domain.com","project_id":"523e5098be6c4438b428d7f3f94b3a2d"}
create = use.create_user(new_user_dict)
print create

print "Create a new standard user."
new_user_dict = {"username":'POWER5',"password":"test","userrole":"user","email":"power2@domain.com","project_id":"523e5098be6c4438b428d7f3f94b3a2d"}
create = use.create_user(new_user_dict)
print create

print "Create a new standard user."
new_user_dict = {"username":'POWER6',"password":"test","userrole":"admin","email":"power3@domain.com","project_id":"523e5098be6c4438b428d7f3f94b3a2d"}
create = use.create_user(new_user_dict)
print create


print "Create a new power user."
new_pu_dict = {"username":'shitbird5',"password":"test","userrole":"pu","email":"testpu@domain.com"}
create_pu = use.create_user(new_pu_dict)
print create_pu


add_user_dict = {"username":"shitbird5","user_role":'pu',"project_name":'ffvc'}
add = use.add_user_to_project(add_user_dict)
print add

print "getting test power user info"
user_info = {"username":'keven4',"project_name":'testproj'}
get_p = use.get_user_info(user_info)
print get_p
time.sleep(2)
print "---------------------------------------------"

print "Create a new admin user."
new_admin_dict = {"username":'testadmin',"password":"test","userrole":"admin","email":"testadmin@domain.com","project_name":"testproj"}
create_admin = use.create_user(new_admin_dict)
print create_admin

print "getting testadmin info"
user_info = {"username":'testadmin',"project_name":'testproj'}
get_a = use.get_user_info(user_info)
print get_a
time.sleep(2)
print "---------------------------------------------"

print "toggle user to disable"
toggle = {"username":'keven4',"toggle":'disable'}
tog = use.toggle_user(toggle)
print tog

print "getting poweruser info"
user_info = {"username":'keven4',"project_name":'testproj'}
get_t = use.get_user_info(user_info)
print get_t

time.sleep(2)
if(get_t['user_enabled'] == 'FALSE'):
    print "toggle user back to enable"
    toggle = {"username":'keven4',"toggle":'enable'}
    tog_e = use.toggle_user(toggle)
    print tog_e
time.sleep(2)
print "---------------------------------------------"

print "Updateing user password"
pas_dict = {'new_password':'testtest','project_id':'da54c5efa79841f0888c0c4ea35d9895','user_id':get_t['user_id']}
pas = use.update_user_password(pas_dict)
time.sleep(2)
print "----------------------------------------------"

print "Removing user from project"

remove_user_dict = {"user_id":"e38e8a6ebf2c4331830892622d36cc91","project_id":'5b5a1f8784a742bc8bae98021d7e884b'}
remove = use.remove_user_from_project(remove_user_dict)
print remove


print "Deleteing a testuser"
delete = {"user_id":"53f9b62ef34c46b3a53e8fa1e5308b2f","project_id":'523e5098be6c4438b428d7f3f94b3a2d'}
blah = use.delete_user(delete)
print blah
time.sleep(2)
print "---------------------------------------------"
'''
