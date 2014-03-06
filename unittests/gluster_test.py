#!/usr/local/bin/python2.7
import time
from transcirrus.common.auth import authorization
from transcirrus.common.gluster import gluster_ops
from transcirrus.component.swift.account_services import account_service_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","password")
#get the user dict
auth = a.get_auth()


glust = gluster_ops(auth)

#input_dict = {'volume_name':'jonarrance','gluster_dir_name':'jonrrance'}
#create = glust.create_gluster_volume(input_dict)
#print create

#yo = glust.create_gluster_swift_ring()
#print yo

yo = glust.list_gluster_volumes()
print yo

yo2 = glust.delete_gluster_volume('myvolume')
print yo2

#yo = account_service_ops(auth)
#blah = yo.get_account_containers('f283a6409db24392b78b22c196813c3a')
#print blah