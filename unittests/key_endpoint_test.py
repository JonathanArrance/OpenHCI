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
from keystone_endpoints import endpoint_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","builder")
#get the user dict
d = a.get_auth()

print "Instantiating user_ops object."
end = endpoint_ops(d)


print "Create a new service endpoint with a cloud name."
new_endpoint_dict = {"cloud_name":'joncloud',"service_name":"cinder"}
create = end.create_endpoint(new_endpoint_dict)
print create
print "---------------------------------------------"
"""
print "Create a new service endpoint with out a cloud name."
new_endpoint_dict2 = {"service_name":"nova"}
create2 = end.create_endpoint(new_endpoint_dict2)
print create2
print "---------------------------------------------"
time.sleep(2)

print "Create a new service endpoint with a fake service name."
new_endpoint_dict3 = {"service_name":"blah"}
create3 = end.create_endpoint(new_endpoint_dict3)
print create3
print "---------------------------------------------"
time.sleep(2)
"""
time.sleep(5)
print "Delete a service endpoint with out a cloud name."
new_endpoint_dict2 = {"service_name":"cinder"}
create2 = end.delete_endpoint(new_endpoint_dict2)
print create2
print "---------------------------------------------"