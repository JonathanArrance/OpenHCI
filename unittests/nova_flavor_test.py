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
a = authorization("power","password")
#a = authorization("admin","password")
#get the user dict
d = a.get_auth()

print d

#instantiate a flavor_ops object
flav = flavor_ops(d)
"""
#add a new flavor
flav_dict = {"name":'test21',"ram":'256',"boot_disk":'10',"cpus":'4',"swap":'2',"public":"true"}
new_flav1 = flav.create_flavor(flav_dict)
print new_flav1
print "-------------------------------------------"
time.sleep(2)
"""
#list all of the flavors in the cloud
flav_list = flav.list_flavors()
print flav_list
print "-------------------------------------------"
time.sleep(2)

flav_get = flav.get_flavor("1")
print flav_get
print "-------------------------------------------"
time.sleep(2)
"""
flav_del = flav.delete_flavor(new_flav1['flav_id'])
print flav_del
print "-------------------------------------------"
time.sleep(2)
"""
