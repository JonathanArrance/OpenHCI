#!/usr/bin/python
import time
# get the user level from the transcirrus system DB
#passes the user level out 
import sys

sys.path.append('../common')
import logger
import config
from auth import authorization

sys.path.append('/home/jonathan/alpo.0/component/cinder')
from cinder_volume import volume_ops

a = authorization("admin","builder")
#get the user dict
d = a.get_auth()

print "instantiating a volume abject."
vol = volume_ops(d)

print "createing a new volume"
create = {'volume_name':'testvol','volume_size':'1'}
create_vol = vol.create_volume(create)
print create_vol
time.sleep(10)
print "------------------------------------------"
print "sleeping for 10 seconds"

print "list current volumes"
listit = vol.list_volumes()
print listit
time.sleep(2)
print "------------------------------------------"

print "deleteing the volume"
delete_vol = {"vol_name":'testvol'}
delete = vol.delete_volume(delete_vol)
print delete