#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

#from auth import authorization
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.glance.glance_v2 import glance_ops

print "Instantiating authorization object for an default admin"
c= authorization("admin","builder")

print "Get admin authorization dictionary"
b = c.get_auth()

print "Image"
i= glance_ops(b)
print i

print "List Images"
li = i.list_images()
print li

print "Get Image %s" % (str(li[1]['image_id']))
gi = i.get_image(str(li[1]['image_id']))
print gi


#print "Instantiating authorization object for an admin"
#e = authorization("jonadmin","test")

#print "Get admin authorization dictionary"
#f = e.get_auth()
#print f
