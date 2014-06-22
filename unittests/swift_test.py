#!/usr/local/bin/python2.7
import time
from transcirrus.common.auth import authorization
from transcirrus.component.swift.account_services import account_service_ops as accounts
from transcirrus.component.swift.container_services import container_service_ops as container
from transcirrus.component.swift.object_services import object_service_ops as objects
from transcirrus.common.gluster import gluster_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
au = authorization("admin","password")
auth = au.get_auth()

a = accounts(auth)
c = container(auth)
o = objects(auth)
glust = gluster_ops(auth)


#id1 = {'container_name':'container4','project_id':"84d3e074012a42ce919771c503993f4e"}
#container1= c.create_container(id1)
#print container1

#gac1 = a.get_account_info("84d3e074012a42ce919771c503993f4e")
#print gac1

gac = a.get_account_containers("84d3e074012a42ce919771c503993f4e")
print gac

#id1 = {'container_name':'container2','project_id':"634911ba0d794a4dadefdf872e0d8abe"}
#container1= c.create_container(id1)
#print container1

#id2 = {'container_name':'container2','project_id':"634911ba0d794a4dadefdf872e0d8abe"}
#conatiner2 = c.create_container(id2)
#print container2

#gac = a.get_account_containers("634911ba0d794a4dadefdf872e0d8abe")
#print gac


#oc1 = {'container_name':'container2','object_path':'/admin_pass_test.py','project_id':'634911ba0d794a4dadefdf872e0d8abe'}
#object1 = o.create_object(oc1)
#print object1

#lc1 = {'container_name':'container2','project_id':"634911ba0d794a4dadefdf872e0d8abe"}
#list1 = c.list_container_objects(lc1)
#print list1

#god = {'container_name':'container2','project_id':"634911ba0d794a4dadefdf872e0d8abe",'object_name':'auth_test.py'}
#out = o.get_object_details(god)
#print out
"""
do = {'container_name':'container1','project_id':"634911ba0d794a4dadefdf872e0d8abe",'object_name':'home/transuser/alpo_rhel/unittests/auth_test.py'}
delob = o.delete_object(do)
print delob


dc1 = {'container_name':'container1','project_id':"634911ba0d794a4dadefdf872e0d8abe"}
delete1 = c.delete_container(dc1)
print delete1
"""
