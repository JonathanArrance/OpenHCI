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
from transcirrus.component.cinder.cinder_snapshot import snapshot_ops

a = authorization("admin","password")
#get the user dict
d = a.get_auth()

print "instantiating a volume abject."
vol = volume_ops(d)
snap = snapshot_ops(d)

'''
print "createing a new volume"
create = {'volume_name':'transcirrus4','volume_size':'1','project_id':"d4b29af44660474da7d5f884ec107f76",'volume_type':'ssd'}
create_vol = vol.create_volume(create)
print create_vol
time.sleep(5)

print "createing a new volume snap"
create = {'snapshot_name':'trans_snap4','snapshot_desc':'Yo yo','project_id':"d4b29af44660474da7d5f884ec107f76",'volume_id':create_vol['volume_id']}
create_snap = snap.create_snapshot(create)
print create_snap
time.sleep(5)
'''
print "createing a new volume from snap"
create = {'volume_name':'trans_from_snap4','volume_size':'1','project_id':"157a34897e8246b4871676c5feb64ab8",'snapshot_id':'93923748-8f5b-44d7-a55a-0808927f7cc7'}
create_vol_from_snap = vol.create_vol_from_snapshot(create)
print create_vol_from_snap
time.sleep(5)
'''
print "createing a new volume from snap"
create = {'volume_name':'trans_from_snap_delta','volume_size':'1','project_id':"d4b29af44660474da7d5f884ec107f76",'snapshot_id':create_snap['snapshot_id']}
create_vol = vol.create_vol_from_snapshot(create)
print create_vol
time.sleep(5)


print "createing a new volume clone"
create = {'volume_name':'trans_clone','volume_size':'1','project_id':"d4b29af44660474da7d5f884ec107f76",'volume_id':create_vol['volume_id']}
create_vol = vol.create_vol_clone(create)
print create_vol
time.sleep(5)

print "createing a new volume clone2"
create = {'project_id':"d4b29af44660474da7d5f884ec107f76",'volume_id':create_vol['volume_id']}
create_vol = vol.create_vol_clone(create)
print create_vol
time.sleep(5)


print "createing a new volume snap"
create = {'snapshot_name':'the_snapshot','snapshot_desc':'Yo yo','project_id':"d4b29af44660474da7d5f884ec107f76",'volume_id':'23e06c9b-c6fa-4f59-9a0d-9b2bebcfb449'}
create_vol = snap.create_snapshot(create)
print create_vol


print "createing a new volume snap"
create = {'snapshot_name':'the_snapshot','snapshot_desc':'Yo yo','project_id':"bf54175ff7594e23b8f320c74fb05d68",'volume_id':'a853e89c-a959-4e6f-82ad-3aa833fcf9b5','force':'True'}
create_vol = snap.create_snapshot(create)
print create_vol

print "createing a new volume snap"
create = {'snapshot_name':'the_snapshot','snapshot_desc':'Yo yo','project_id':"bf54175ff7594e23b8f320c74fb05d68",'volume_id':'a853e89c-a959-4e6f-82ad-3aa833fcf9b5'}
create_vol = snap.create_snapshot(create)
print create_vol

print "createing a new volume"
create = {'volume_name':'test111','volume_size':'1','project_id':"bf54175ff7594e23b8f320c74fb05d68",'volume_type':'ssd','snapshot_id':'a32d8390-1df0-445a-b560-f38697dd3d8f'}
create_vol = vol.create_vol_from_snapshot(create)
print create_vol


print "createing a new volume"
create = {'volume_name':'test111','volume_size':'1','project_id':"bf54175ff7594e23b8f320c74fb05d68",'volume_type':'ssd','snapshot_id':'a32d8390-1df0-445a-b560-f38697dd3d8f'}
create_vol = vol.create_vol_from_snapshot(create)
print create_vol

voltype = vol.create_volume_type("nimble")
print voltype
voltype2 = vol.create_volume_type("e-series")
print voltype2

get = {'volume_id':'23e06c9b-c6fa-4f59-9a0d-9b2bebcfb449','project_id':'d4b29af44660474da7d5f884ec107f76'}
yo = vol.get_volume_info(get)
print yo


stuff = vol.get_volume(get)
print stuff

print "createing a new volume"
create = {'volume_name':'test11','volume_size':'1','project_id':"bf54175ff7594e23b8f320c74fb05d68",'volume_type':'ssd'}
create_vol = vol.create_volume(create)
print create_vol

print "------------------------------------------"
print "sleeping for 15 seconds"
time.sleep(15)

print "list current volumes"
listit = vol.list_volumes()
print listit
time.sleep(2)
print "------------------------------------------"

print "deleteing volume"
de={'volume_id':'1b95ab3c-7fa5-4be5-955c-e946cdd7361c','project_id':'e20744efbb384c9abbc888b9a0961574'}
y=vol.delete_volume(de)
print y

print "list current volumes"
listit = vol.list_volumes()
print listit
time.sleep(2)
print "------------------------------------------"

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


print "Creaing vol with testuser"
e = authorization("admin","newpass")
#get the user dict
f = e.get_auth()

print "instantiating a volume abject."
vol3 = volume_ops(f)

print "createing a new volume"
create3 = {'volume_name':'ffvcvol3','volume_size':'1','project_id':"bb85322a95db4990802b9c09b6f943fa"}
create_vol3 = vol3.create_volume(create3)
print create_vol3
time.sleep(10)
print "------------------------------------------"
print "sleeping for 10 seconds"

listit3 = vol3.list_volumes()
print listit3
'''
