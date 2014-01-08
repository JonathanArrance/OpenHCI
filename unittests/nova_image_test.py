#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization

from transcirrus.component.nova.image import nova_image_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","password")
#get the user dict
d = a.get_auth()

#instantiate a flavor_ops object
img = nova_image_ops(d)

#list the availabe images
listimg = img.nova_list_images("523e5098be6c4438b428d7f3f94b3a2d")
print listimg

#list the availabe images
for image in listimg:
    dic = {'image_id':image['image_id'],'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
    getimg = img.nova_get_image(dic)
    print getimg


#list the availabe images
listimg3 = img.nova_list_images("0ce0b37cb8284291b571949a8f028b14")
print listimg3

#list the availabe images
for image in listimg3:
    dic = {'image_id':image['image_id'],'project_id':"0ce0b37cb8284291b571949a8f028b14"}
    getimg3 = img.nova_get_image(dic)
    print getimg3



print "Loggin in as a power user"
#onlyt an admin can create a new user
e = authorization("bill","test")
#get the user dict
f = e.get_auth()

#instantiate a flavor_ops object
img2 = nova_image_ops(f)

#list the availabe images
listimg2 = img2.nova_list_images("523e5098be6c4438b428d7f3f94b3a2d")
print listimg2

#list the availabe images
for image in listimg2:
    dic = {'image_id':image['image_id'],'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
    getimg2 = img2.nova_get_image(dic)
    print getimg2

#list the availabe images
listimg4 = img2.nova_list_images("0ce0b37cb8284291b571949a8f028b14")
print listimg4

#list the availabe images
for image in listimg4:
    dic = {'image_id':image['image_id'],'project_id':"0ce0b37cb8284291b571949a8f028b14"}
    getimg4 = img2.nova_get_image(dic)
    print getimg4