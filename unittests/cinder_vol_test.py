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

a = authorization("admin","password")
#get the user dict
d = a.get_auth()

print "instantiating a volume abject."
vol = volume_ops(d)


voltype = vol.create_volume_type("ssd")
print voltype
voltype2 = vol.create_volume_type("spindle")
print voltype2
"""
get = {'volume_id':'8d4204fd-4d9e-4d83-8949-e33c963650a0','project_id':'84d3e074012a42ce919771c503993f4e'}
yo = vol.get_volume_info(get)
print yo


print "createing a new volume"
create = {'volume_name':'ffvcvol20','volume_size':'1','project_id':"84d3e074012a42ce919771c503993f4e",'volume_type':'SSD'}
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
"""
