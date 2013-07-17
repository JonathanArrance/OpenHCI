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

a = authorization("jon5","test")

#get the user dict
d = a.get_auth()

snap = snapshot_ops(d)

#print "creating snapshot"
snapit = {"snap_name":"snaptest3","snap_desc":"this is a test","vol_id":"9754ebe5-f13b-4a09-a57d-20ec3b9e1a41","project_id":"26c877c1d5f7449c93001cc9187754dd"}
yo = snap.create_snapshot(snapit)
#time.sleep(2)

#print "listing snapshot"
#snapstuff = snap.get_snapshot("snaptest3")
#print snapstuff


#time.sleep(2)
#print "deleteing snapshot"
#yo = snap.delete_snapshot("snaptest3")
#print yo
