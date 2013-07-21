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
from keystone_tenants import tenant_ops

a = authorization("admin","builder")

#get the user dict
d = a.get_auth()

print "Instantiating a new tenant ops object."
ten = tenant_ops(d)
time.sleep(2)
print "----------------------------------------"

print "creating test project"
proj = ten.create_tenant("testproj")
print proj
time.sleep(2)
print "----------------------------------------"

print "listing projects"
listit = ten.list_all_tenants()
print listit
time.sleep(2)
print "----------------------------------------"

print "deleting testproject"
delproj = ten.remove_tenant("testproj")
print delproj
