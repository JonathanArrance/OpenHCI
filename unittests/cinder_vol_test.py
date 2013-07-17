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

vol = volume_ops(d)

desc = {'volume_name':'testjon2','volume_size':'1'}
create = vol.create_volume(desc)
print create

#time.sleep(2)

#desc = {'volume_name':'testjon3','volume_size':'1'}
#create = vol.create_volume(desc)
#print create

#time.sleep(2)

#desc = {'volume_name':'testjon4','volume_size':'1'}
#create = vol.create_volume(desc)
#print create

#time.sleep(5)
#listit = vol.list_volumes()
#print listit

#delete_vol = {"vol_name":'testjon2'}
#yo = vol.delete_volume(delete_vol)
#print "unittest"
#print yo