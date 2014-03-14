#!/usr/bin/python
import sys
import time
import urllib2
import re
import urllib

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.glance.glance_ops_v2 import glance_ops

print "**Instantiating Authorization Object for the Default Admin...**"
c = authorization("admin","password")
print

print "**Getting Admin Authorization Dictionary...**"
b = c.get_auth()
print

print "**Instantiating Glance Object...**"
i= glance_ops(b)
print i
print

print "**Listing Images...**"
li = i.list_images()
print li
print

get_name = li[2]['image_name']
get_id = li[2]['image_id']
print "**Getting Image Details for: %s...**" %(get_name)
gi = i.get_image(get_id)
print "ID: %s" %str(gi['image_id'])
print "Name: %s" %str(gi['image_name'])
print "Status: %s" %str(gi['status'])
print "Visibility: %s" %str(gi['visibility'])
print "Tags: %s" %str(gi['tags'])
print "Created: %s" %str(gi['created_at'])
print "Updated: %s" %str(gi['updated_at'])
print "File: %s" %str(gi['image_file'])
print "Schema: %s" %str(gi['schema'])
print

print "**Creating Image: test...**"
input_dict = {'image_name':"test", 'image_file':"cirros-0.3.1-x86_64-disk.img", 'container_format': "bare", 'disk_format': "raw", 'visibility': "public"}
ii = i.import_image(input_dict)
print ii
print

print "**Listing Images...**"
li = i.list_images()
print li
print

for image in li:
    if(image['image_name'] == "test"):
        del_name = image['image_name']
        del_id = image['image_id']

print "**Getting Image Details for: %s...**" %(del_name)
gi = i.get_image(del_id)
print "ID: %s" %str(gi['image_id'])
print "Name: %s" %str(gi['image_name'])
print "Status: %s" %str(gi['status'])
print "Visibility: %s" %str(gi['visibility'])
print "Tags: %s" %str(gi['tags'])
print "Created: %s" %str(gi['created_at'])
print "Updated: %s" %str(gi['updated_at'])
print "File: %s" %str(gi['image_file'])
print "Schema: %s" %str(gi['schema'])
print

print "**Deleting Image: %s...**" %(del_name)
di = i.delete_image(del_id)
print di
print

print "**Listing Images...**"
li = i.list_images()
print li
print

"""
# create a password manager
password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

# Add the username and password.
# If we knew the realm, we could use it instead of None.
top_level_url = "http://192.168.10.10"
password_mgr.add_password(None, top_level_url, "builder", "builder")

handler = urllib2.HTTPBasicAuthHandler(password_mgr)

# create "opener" (OpenerDirector instance)
opener = urllib2.build_opener(handler)
urllib2.install_opener(opener)

remote_open = urllib2.urlopen("http://192.168.10.10/cirros-0.3.1-x86_64-disk.img")
print remote_open
open_file = re.search(r'= (.*)>', str(remote_open))
group = open_file.group(1)
print group
"""

print "**Creating Image: test2...**"
input_dict = {'image_name':"test2", 'image_url':"http://192.168.10.10/cirros-0.3.1-x86_64-disk.img", 'container_format': "bare", 'disk_format': "raw", 'visibility': "public"}
ii = i.import_image(input_dict)
print ii
print

print "**Listing Images...**"
li = i.list_images()
print li
print

for image in li:
    if(image['image_name'] == "test2"):
        del_name = image['image_name']
        del_id = image['image_id']

print "**Getting Image Details for: %s...**" %(del_name)
gi = i.get_image(del_id)
print "ID: %s" %str(gi['image_id'])
print "Name: %s" %str(gi['image_name'])
print "Status: %s" %str(gi['status'])
print "Visibility: %s" %str(gi['visibility'])
print "Tags: %s" %str(gi['tags'])
print "Created: %s" %str(gi['created_at'])
print "Updated: %s" %str(gi['updated_at'])
print "File: %s" %str(gi['image_file'])
print "Schema: %s" %str(gi['schema'])
print

print "**Deleting Image: %s...**" %(del_name)
di = i.delete_image(del_id)
print di
print

print "**Listing Images...**"
li = i.list_images()
print li
print