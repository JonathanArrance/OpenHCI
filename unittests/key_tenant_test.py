#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_tenants import tenant_ops

a = authorization("admin","password")

#get the user dict
d = a.get_auth()

print "Instantiating a new tenant ops object."
ten = tenant_ops(d)
time.sleep(1)
print "----------------------------------------"

print "creating test project"
proj = ten.create_tenant("jon1")
print proj
time.sleep(1)
print "----------------------------------------"
'''
print "listing projects"
listit = ten.list_all_tenants()
print listit
time.sleep(1)
print "----------------------------------------"

print "Get the project"
get = ten.get_tenant("")
print get
print "----------------------------------------"
time.sleep(1)

print "deleting testproject"
delproj = ten.remove_tenant("13bb3911ba3241bd88b0bd7a4783bf71")
print delproj
'''
"""
lis = ten.list_tenant_users("testproj")
print lis
"""
