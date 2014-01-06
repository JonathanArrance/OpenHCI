#!/usr/bin/python
import time
# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

#from auth import authorization
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
from transcirrus.component.cinder.cinder_snapshot import snapshot_ops

a = authorization("admin","password")
#get the user dict
d = a.get_auth()
snap = snapshot_ops(d)

"""
print "createing a new volume"
create = {'volume_name':'testvol','volume_size':'1'}
create_vol = vol.create_volume(create)
print create_vol
print "sleeping for 10 seconds while volume created"
time.sleep(10)
print "------------------------------------------"
"""
"""
print "creating snapshot"
snapit = {"snap_name":"snaptest3","snap_desc":"this is a test","vol_id":"8ee75400-1474-408d-be35-eadd54a9f5c5","project_id":"523e5098be6c4438b428d7f3f94b3a2d"}
snaps = snap.create_snapshot(snapit)
print snaps
print "sleeping for 10 seconds while snapshot created"
time.sleep(10)

print "------------------------------------------"

print "geting the snapshot"
snapstuff = snap.get_snapshot("snaptest3")
print snapstuff
time.sleep(2)
print "-----------------------------------------"
"""
lis = snap.list_snapshots()
print lis


c = authorization("bill","test")
#get the user dict
f = c.get_auth()
snap2 = snapshot_ops(f)

"""
print "creating snapshot"
snapit2 = {"snap_name":"snaptest4","snap_desc":"this is a test","vol_id":"970042dd-cfe4-4426-8a6c-c7c694b091d7","project_id":"523e5098be6c4438b428d7f3f94b3a2d"}
snaps2 = snap2.create_snapshot(snapit2)
print snaps2
print "sleeping for 10 seconds while snapshot created"
time.sleep(10)

print "------------------------------------------"

print "geting the snapshot"
snapstuff2 = snap2.get_snapshot("snaptest4")
print snapstuff2
time.sleep(2)
print "-----------------------------------------"
"""

lis2 = snap2.list_snapshots()
print lis2


"""
h = authorization("bill2","test")
#get the user dict
g = h.get_auth()
snap3 = snapshot_ops(g)

lis3 = snap3.list_snapshots()
print lis3
"""

#print "deleteing snapshot"
#delete2 = snap2.delete_snapshot("snaptest4")
#print delete2

#print "deleteing snapshot"
#delete = snap.delete_snapshot("snaptest3")
#print delete
