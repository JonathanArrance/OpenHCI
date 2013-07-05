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

a = authorization("testuser2","test")

#get the user dict
d = a.get_auth()
print "unittest"
print d

ten = tenant_ops(d)

#proj = ten.create_tenant("kevenduerr4")

#print proj

yo = ten.list_all_tenants()
print yo

#delproj = ten.remove_tenant("kevenduerr4")