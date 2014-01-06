#!/usr/bin/python
import time
# get the user level from the transcirrus system DB
#passes the user level out 
import sys

#sys.path.append('../common')
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization

#sys.path.append('/home/jonathan/alpo.0/component/cinder')
from transcirrus.component.cinder.cinder_volume import volume_ops
"""
a = authorization("admin","password")
#get the user dict
d = a.get_auth()

print "instantiating a volume abject."
vol = volume_ops(d)

print "createing a new volume"
create = {'volume_name':'ffvcvol','volume_size':'1','project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
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



print "Creaing vol with testuser"
c = authorization("bill","test")
#get the user dict
d = c.get_auth()

print "instantiating a volume abject."
vol2 = volume_ops(d)

print "createing a new volume"
create2 = {'volume_name':'ffvcvol2','volume_size':'1','project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
create_vol2 = vol2.create_volume(create2)
print create_vol2
time.sleep(10)
print "------------------------------------------"
print "sleeping for 10 seconds"

print "list current volumes"
listit2 = vol2.list_volumes()
print listit2
time.sleep(2)
print "------------------------------------------"
"""

print "Creaing vol with testuser"
e = authorization("bill2","test")
#get the user dict
f = e.get_auth()

print "instantiating a volume abject."
vol3 = volume_ops(f)

print "createing a new volume"
create3 = {'volume_name':'ffvcvol3','volume_size':'1','project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
create_vol3 = vol3.create_volume(create3)
print create_vol3
time.sleep(10)
print "------------------------------------------"
print "sleeping for 10 seconds"

listit3 = vol3.list_volumes()
print listit3
