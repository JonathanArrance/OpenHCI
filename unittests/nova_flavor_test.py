#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time


import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization

from transcirrus.component.nova.flavor import flavor_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","password")
#a = authorization("admin","password")
#get the user dict
d = a.get_auth()


#instantiate a flavor_ops object
flav = flavor_ops(d)

#add a new flavor
"""
input_dict = {'flavor_id':'11739','key':'description','value':'this is a test'}
x = flav.add_flavor_metadata(input_dict)
print x

flav_dict = {"name":'test29',"ram":'256',"boot_disk":'10',"cpus":'4',"swap":'2',"public":"FALSE"}
new_flav1 = flav.create_flavor(flav_dict)
print new_flav1
print "-------------------------------------------"
time.sleep(2)

#list all of the flavors in the cloud
flav_list = flav.list_flavors()
print flav_list
print "-------------------------------------------"
time.sleep(2)

flav_get = flav.get_flavor("11739")
print flav_get
print "-------------------------------------------"
time.sleep(2)

flav_del = flav.delete_flavor(new_flav1['flav_id'])
print flav_del
print "-------------------------------------------"
time.sleep(2)

input_dict = {'flavor_id':'11739','metadata_key':'description'}
x = flav.get_flavor_metadata(input_dict)
print x
"""
input_dict = {'flavor_id':'11739','metadata_key':'description'}
x = flav.delete_flavor_metadata(input_dict)
print x