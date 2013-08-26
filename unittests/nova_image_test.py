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
from image import nova_image_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","builder")
#get the user dict
d = a.get_auth()

#instantiate a flavor_ops object
img = nova_image_ops(d)

#list the availabe images
listimg = img.nova_list_images()
print listimg

#list the availabe images
#for image in listimg:
#    getimg = img.nova_get_image(image['image_id'])
#    print getimg