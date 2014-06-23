#!/usr/local/bin/python2.7
import time
from transcirrus.common.auth import authorization
from transcirrus.common.gluster import gluster_ops
from transcirrus.component.swift.account_services import account_service_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","password")
#get the user dict
#auth = a.get_auth()
#glust = gluster_ops(auth)

input_dict = {'username':'admin','user_level':1,'is_admin':1,'obj':1}
glust = gluster_ops(input_dict)

#brick = ['172.38.24.10:/data/gluster/jonarrance2','172.38.24.12:/data/gluster/jonarrance2']
#input_dict = {'volume_name':'jonarrance2','bricks': brick}
#input_dict = {'volume_name':'testvol7'}
#print input_dict
#create = glust.create_gluster_volume(input_dict)
#print create

#yo = glust.create_gluster_swift_ring()
#print yo

yo = glust.list_gluster_volumes()
print yo

#yo2 = glust.delete_gluster_volume('jonarrance3')
#print yo2

#yo3 = glust.delete_gluster_volume('jonarrance2')
#print yo3

#yo4 = glust.list_gluster_volumes()
#print yo4

#input_dict = {'volume_name':'jonarrance6','brick':'172.38.24.12:/data/gluster/jonarrance6'}
#yo5 = glust.add_gluster_brick(input_dict)
#print yo5

##input_dict = {'volume_name':'jonarrance6','brick':'172.38.24.12:/data/gluster/jonarrance6'}
##yo7 = glust.remove_gluster_brick(input_dict)
##print yo7

#yo8 = glust.stop_gluster_volume('jonarrance6')
#print yo8

#yo9 = glust.rebalance_gluster_volume('jonarrance6')
#print yo9

#yo10 = glust.attach_gluster_peer('172.38.24.12')
#print yo10

#yo12 = glust.list_gluster_nodes()
#print yo12


#yo11 = glust.detach_gluster_peer('172.38.24.12')
#print yo11

#yo6 = glust.list_gluster_volumes()
#print yo6
#yo = account_service_ops(auth)
#blah = yo.get_account_containers('f283a6409db24392b78b22c196813c3a')
#print blah

#brick = glust.get_gluster_brick()
#print brick
