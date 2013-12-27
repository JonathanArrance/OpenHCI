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
from transcirrus.component.glance.glance_ops import glance_ops

print "Instantiating authorization object for an default admin"
c= authorization("admin","builder")

print "Get admin authorization dictionary..."
b = c.get_auth()

print "Image..."
i= glance_ops(b)
print i
print

print "List Images..."
li = i.list_images()
print li
print

print "Get Image %s..." % (str(li[1]['image_id']))
gi = i.get_image(str(li[1]['image_id']))
print gi
print

name = gi['image_name']

print "Update Image %s..." % (str(li[0]['image_id']))
update = [
            {"x-image-meta-name": "test"}
         ]
update_dict = {"image_id": (str(li[0]['image_id'])), "update": update}
ui = i.update_image(update_dict)
print ui
print

print "Update Image %s..." % (str(li[0]['image_id']))
update = [
            {"x-image-meta-name": "cirros-0.3.1-x86_64-uec-ramdisk"}
         ]
update_dict = {"image_id": (str(li[0]['image_id'])), "update": update}
ui = i.update_image(update_dict)
print ui
print

print "Create Image from CentOS-6.5-x86_64-netinstall.iso..."
create_dict = {"image_name": "TEST1", "disk_format": "vhd", "container_format": "ovf", "is_public": "false", "file_location": "/home/nick/CentOS-6.5-x86_64-netinstall.iso"}
ci = i.create_image(create_dict)
print ci
print

print "List Images..."
li = i.list_images()
print li
print

print "Get Image %s..." % (str(li[0]['image_id']))
gi = i.get_image(str(li[0]['image_id']))
print gi
print

#print "Delete Image %s..." % (str(li[0]['image_id']))
#di = i.delete_image(str(li[0]['image_id']))
#print di
#print

print "List Images..."
li = i.list_images()
print li
print

