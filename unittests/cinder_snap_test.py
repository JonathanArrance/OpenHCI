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
from cinder_snapshot import snapshot_ops
from cinder_volume import volume_ops
sys.path.append('/home/jonathan/alpo.0/component/keystone')
from keystone_tenants import tenant_ops

a = authorization("admin","builder")
#get the user dict
d = a.get_auth()

print "instantiating a volume abject."
vol = volume_ops(d)

print "createing a new volume"
create = {'volume_name':'testvol','volume_size':'1'}
create_vol = vol.create_volume(create)
print create_vol
print "sleeping for 10 seconds while volume created"
time.sleep(10)
print "------------------------------------------"

print "instantiateing an tenant_ops object"
ten = tenant_ops(d)

print "getting the project info"
proj = ten.get_tenant("demo")
print proj
print "------------------------------------------"

print "instantiating a snapshot_ops object"
snap = snapshot_ops(d)

print "creating snapshot"
snapit = {"snap_name":"snaptest","snap_desc":"this is a test","vol_id":create_vol['volume_id'],"project_id":proj['project_id']}
snap = snap.create_snapshot(snapit)
print "sleeping for 10 seconds while snapshot created"
time.sleep(10)

print "------------------------------------------"

print "gettin the snapshot"
snapstuff = snap.get_snapshot("snaptest")
print snapstuff
time.sleep(2)
print "-----------------------------------------"

print "deleteing snapshot"
delete = snap.delete_snapshot("snaptest")
print delete
