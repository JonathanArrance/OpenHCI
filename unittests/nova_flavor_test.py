#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

sys.path.append('../common')
import logger
import config
from auth import authorization

sys.path.append('/home/jonathan/alpo.0/component/nova')
from flavor import flavor_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","builder")
#get the user dict
d = a.get_auth()

#instantiate a flavor_ops object
flav = flavor_ops(d)

#add a new flavor
flav_dict = {"name":'test21',"ram":'256',"boot_disk":'10',"cpus":'4',"swap":'2',"public":"true"}
new_flav1 = flav.create_flavor(flav_dict)
print new_flav1
print "-------------------------------------------"
time.sleep(2)

#list all of the flavors in the cloud
flav_list = flav.list_flavors()
print flav_list
print "-------------------------------------------"
time.sleep(2)

flav_get = flav.get_flavor(new_flav1['flav_id'])
print flav_get
print "-------------------------------------------"
time.sleep(2)

flav_del = flav.delete_flavor(new_flav1['flav_id'])
print flav_del
print "-------------------------------------------"
time.sleep(2)