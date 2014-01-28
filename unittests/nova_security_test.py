#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization

from transcirrus.component.nova.server import server_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","password")
#get the user dict
d = a.get_auth()
nova = server_ops(d)
'''
print "Loggin in as the power user."
#onlyt an admin can create a new user
c = authorization("admin","password")
#get the user dict
e = c.get_auth()
nova2 = server_ops(e)

print "deleteing the security group"
d = {'sec_group_id':"61789128-04a8-422e-b28f-1a20db1eb479", 'project_id':"975378d013664df394e3284bd7030108"}
del_group = nova.delete_sec_group(d)
print del_group
print "-------------------------------------------------"
time.sleep(2)

print "deleteing the security group"
d2 = {'sec_group_id':"88cf68cc-a47a-489e-aab5-99734bcc0ba4", 'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
del_group2 = nova2.delete_sec_group(d2)
print del_group
print "-------------------------------------------------"
time.sleep(2)

print "deleteing the security group"
d3 = {'sec_group_id':"dfb42f01-f22a-44bc-bf62-130363724dc5", 'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
del_group3 = nova2.delete_sec_group(d3)
print del_group3
print "-------------------------------------------------"
time.sleep(2)

print "deleteing the security key"
yo = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'sec_key_name':'testkey2'}
del_key = nova.delete_sec_keys(yo)
print del_key
print "-------------------------------------------------"
time.sleep(1)

print "deleteing the default security key"
yo2 = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'sec_key_name':'testkey3'}
del_key2 = nova2.delete_sec_keys(yo2)
print del_key2
print "-------------------------------------------------"
time.sleep(1)

print "deleteing the default security key"
yo3 = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'sec_key_name':'testkey4'}
del_key3 = nova2.delete_sec_keys(yo3)
print del_key3
print "-------------------------------------------------"
time.sleep(1)

print "creating a new default security key"
key1 = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'key_name':'testkey'}
create_def_key = nova.create_sec_keys(key1)
print create_def_key
print "------------------------------------------------"
time.sleep(1)

#try code path that does not include default key
print "creating a new security key"
key2 = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'key_name':'ffvckey'}
create_def_key2 = nova.create_sec_keys(key2)
print create_def_key2
print "------------------------------------------------"
time.sleep(1)

print "Createing security group with default ports - default"
#create a security group with default ports

create_group = {"group_name": 'blah',"group_desc": 'This is a test','project_id':"66069dc297a449ca90582187011ac8e9"}
sec_group = nova.create_sec_group(create_group)
print sec_group
print "------------------------------------------------"
time.sleep(1)

print "Createing security group with custom ports"
#create a security group with the defualt ports
create_group2 = {"group_name": 'ffvcsec2','project_id':"523e5098be6c4438b428d7f3f94b3a2d","group_desc": 'This is a test2',"ports":[139,22,80]}
sec_group2 = nova.create_sec_group(create_group2)
print sec_group2
print "------------------------------------------------"
time.sleep(1)

print "listing the security keys"
list_key = nova.list_sec_keys()
for lk in list_key:
    try:
        get_key = nova.get_sec_keys(lk['key_id'])
        print get_key
    except:
        pass
time.sleep(1)

print "listing the security groups"
list_group = nova.list_sec_group()
for lg in list_group:
    print "Get detailed security group info"
    sec = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'sec_group_id':lg['sec_group_id']}
    get_group = None
    try:
        get_group = nova.get_sec_group(sec)
        print get_group
    except:
        pass
    print "------------------------------------------------"
time.sleep(1)

print "-----------------------------------------------------------------"


print "creating a new default security key"
key3 = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'key_name':'ffvcuserkey'}
create_def_key3 = nova2.create_sec_keys(key3)
print create_def_key3
print "------------------------------------------------"
time.sleep(1)
'''
#try code path that does not include default key
print "creating a new security key"
key4 = {'project_id':"de6647df708542ddafc00baf39534f56",'key_name':'jonkeys2'}
create_def_key4 = nova.create_sec_keys(key4)
print create_def_key4
print "------------------------------------------------"
time.sleep(1)
'''
print "Createing security group with default ports - default"
#create a security group with default ports
create_group3 = {"group_name": 'ffvcsec3',"group_desc": 'This is a test3','project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
sec_group3 = nova2.create_sec_group(create_group3)
print sec_group3
print "------------------------------------------------"
time.sleep(1)

print "Createing security group with custom ports"
#create a security group with the defualt ports
create_group4 = {"group_name": 'ffvcsec4','project_id':"523e5098be6c4438b428d7f3f94b3a2d","group_desc": 'This is a test4',"ports":[139,22,80]}
sec_group4 = nova2.create_sec_group(create_group4)
print sec_group4
print "------------------------------------------------"
time.sleep(1)

print "listing the security keys"
list_key2 = nova2.list_sec_keys()
for lk2 in list_key2:
    try:
        get_key2 = nova2.get_sec_keys(lk2['key_id'])
        print get_key2
    except:
        pass
time.sleep(1)
print "-------------------------------------------------"

print "listing the security groups"
list_group2 = nova2.list_sec_group()
for lg2 in list_group2:
    print "Get detailed security group info"
    sec2 = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'sec_group_id':lg2['sec_group_id']}
    get_group2 = None
    try:
        get_group2 = nova2.get_sec_group(sec2)
        print get_group2
    except:
        pass
    print "------------------------------------------------"

print "-----------------------------------------------------------------"
print "Loggin in as the user."
#onlyt an admin can create a new user
h = authorization("bill2","test")
#get the user dict
g = h.get_auth()

nova3 = server_ops(g)
print "listing the security keys"
list_key3 = nova3.list_sec_keys()
for lk3 in list_key3:
    get_key3 = nova3.get_sec_keys(lk3['sec_key_id'])
    print get_key3
time.sleep(1)
print "-------------------------------------------------"

print "listing the security groups"
list_group3 = nova3.list_sec_group()
for lg3 in list_group3:
    print "Get detailed security group info"
    sec3 = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'sec_group_id':lg3['sec_group_id']}
    get_group3 = None
    try:
        get_group3 = nova3.get_sec_group(sec2)
        print get_group3
    except:
        pass
    print "------------------------------------------------"

print "Createing security group with default ports - default"
#create a security group with default ports
create_group3= {"group_name": 'billsecgroup',"group_desc": 'This is a test','project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
sec_group3 = nova3.create_sec_group(create_group3)
print sec_group3
print "------------------------------------------------"
time.sleep(1)

#try code path that does not include default key
print "creating a new security key"
key10 = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'key_name':'usertestkey'}
create_def_key10 = nova3.create_sec_keys(key10)
print create_def_key10
print "------------------------------------------------"
time.sleep(1)

#try code path that does not include default key
print "Get the detailed security key info"
get_key2 = nova.get_sec_keys("keys_new")
print get_key2
print "------------------------------------------------"
time.sleep(3)

print "deleteing the default security group"
del_group2 = nova.delete_sec_group("jon")
print del_group2
print "-------------------------------------------------"
time.sleep(2)

print "deleteing the security group"
del_group = nova.delete_sec_group("test_group2")
print del_group
print "-------------------------------------------------"
time.sleep(2)

print "deleteing the security key"
del_key = nova.delete_sec_group("keys_new")
print del_key
print "-------------------------------------------------"
time.sleep(2)

print "deleteing the default security key"
del_key2 = nova.delete_sec_group("default_keys")
print del_key2
print "-------------------------------------------------"
time.sleep(2)
'''
