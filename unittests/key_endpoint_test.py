#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization

from transcirrus.component.keystone.keystone_endpoints import endpoint_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","builder")
#get the user dict
d = a.get_auth()

print "Instantiating user_ops object."
end = endpoint_ops(d)

print "Create a new service endpoint with a cloud name."
new_endpoint_dict = {"cloud_name":'joncloud',"service_name":"swift"}
create = end.create_endpoint(new_endpoint_dict)
print create
print "---------------------------------------------"

'''
time.sleep(1)
print "Create a new service endpoint with out a cloud name."
new_endpoint_dict2 = {"service_name":"keystone"}
create2 = end.create_endpoint(new_endpoint_dict2)
print create2
print "---------------------------------------------"

time.sleep(1)
print "list the configured services"
listservice = end.list_service_catalog()
print listservice
print "----------------------------------------------"


print "Create a new service endpoint with a fake service name."
new_endpoint_dict3 = {"service_name":"blah"}
create3 = end.create_endpoint(new_endpoint_dict3)
print create3
print "---------------------------------------------"


time.sleep(1)
print "listing the service endpoints"
listend = end.list_endpoints()
print listend
print "----------------------------------------------"

time.sleep(1)
print "getting the service endpoint info"
getend = end.get_endpoint("s3")
print getend
print"-----------------------------------------------"

time.sleep(1)
print "Delete a service endpoint with out a cloud name."
new_endpoint_dict2 = {"service_name":"s3"}
create2 = end.delete_endpoint(new_endpoint_dict2)
print create2
print "---------------------------------------------"
'''