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
print

print "List Images"
li = i.list_images()
print li
print

print "Get Image %s" % (str(li[1]['image_id']))
gi = i.get_image(str(li[1]['image_id']))
print gi
print

name = gi['image_name']

print "Update Image %s" % (str(li[1]['image_id']))
update = [
            {"x-image-meta-name": "test"}
         ]
update_dict = {"image_id": (str(li[1]['image_id'])), "update": update}
ui = i.update_image(update_dict)
print ui
print

print "Update Image %s" % (str(li[1]['image_id']))
update = [
            {"x-image-meta-name": "cirros-0.3.1-x86_64-uec-ramdisk"}
         ]
update_dict = {"image_id": (str(li[1]['image_id'])), "update": update}
ui = i.update_image(update_dict)
print ui
print

#print "Instantiating authorization object for an admin"
#e = authorization("jonadmin","test")

#print "Get admin authorization dictionary"
#f = e.get_auth()
#print f
