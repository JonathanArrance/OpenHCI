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
c= authorization("admin","password")

print "Get admin authorization dictionary..."
b = c.get_auth()

print "Image..."
i= glance_ops(b)
print i


d = i.delete_image("a6920f75-d179-4917-86ee-1237a2da0f1a")
print d

'''
print "List Images..."
li = i.list_images()
print li

for x in li:
    print x
    gi = i.get_image(x['image_id'])
    print gi


#get_image = {'img_name':'yoimage','img_disk_format':'qcow2','img_is_public':'True','img_is_protected':'True',
#             'project_id':'66069dc297a449ca90582187011ac8e9','url':'http://download.cirros-cloud.net/0.3.1/cirros-0.3.1-x86_64-disk.img'}
get_image = {'img_name':'yoimage2','img_disk_format':'qcow2','img_is_public':'True','img_is_protected':'False',
             'project_id':'66069dc297a449ca90582187011ac8e9','file_location':'/home/transuser/cirros-0.3.1-x86_64-disk.img'}
yup = i.import_image(get_image)
print yup

for x in li:
    print x
    gi = i.get_image(x['image_id'])
    print gi


print "logging in as bill"
c= authorization("bill","test")

print "Get admin authorization dictionary..."
b = c.get_auth()

print "Image..."
x= glance_ops(b)
print x


print "List Images..."
li = x.list_images()
print li
print



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
'''