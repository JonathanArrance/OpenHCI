#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.component.nova.server import server_ops
from transcirrus.component.nova.storage import server_storage_ops
from transcirrus.component.nova.admin_actions import server_admin_actions
from transcirrus.component.nova.server_action import server_actions

print "Loggin in as the default admin."
#onlyt an admin can create a new user
auth = authorization("admin","password")

#get the user dict
perms = auth.get_auth()
store = server_storage_ops(perms)
nova = server_ops(perms)
#action = server_admin_actions(perms)
#sa = server_actions(perms)

'''
input_dict = {'host_name':'ciac-10176','project_id':'157a34897e8246b4871676c5feb64ab8'}
yo = action.get_os_host(input_dict)

print yo

input_dict = {'zone':'nova','project_id':'157a34897e8246b4871676c5feb64ab8'}
yo = action.list_compute_hosts(input_dict)


input_dict = {'project_id':'157a34897e8246b4871676c5feb64ab8','instance_id':'84180110-b7cf-47ed-b962-8a35b0e172b4','secgroup_id': 'eb66d78f-ec7f-4162-a073-04425cd45d0a','action':'add'}
yo = sa.update_instance_secgroup(input_dict)
print yo


yo = sa.list_instance_snaps('e12a1c25-379b-44db-b0c6-359e7ec62e1b')
print yo

yo = sa.list_instance_snaps('e12a1c25-379b-44db-b0c6-359e7ec62e1b')
print yo

input_dict = {'instance_id':'e2cb3662-c42f-4299-b00e-851e99a67367','project_id':'d4b29af44660474da7d5f884ec107f76'}
yo = store.list_attached_vols(input_dict)

print yo

'''
server_input = {'server_id':'707b8c8d-3c1c-4bfc-9978-45c8e19c6010','project_id':'c417abbb61014f2a8d330a0f7c0210a1'}
inst_info = nova.get_server(server_input)

print inst_info
'''

back_image = {'server_id':'c811007d-b26a-41f2-baf3-0a6a83738c28','project_id':'bf54175ff7594e23b8f320c74fb05d68','rotation':'1','backup_description':'This a test1'}
yo = sa.create_instance_backup(back_image)
print yo


snap_image = {'server_id':'99e85016-4f7d-43cf-b28e-ebca2d0fadda','project_id':'27e633859b2b46db9b0fc0cbece206ea','snapshot_description':'This a test1'}
yo = sa.create_instance_snapshot(snap_image)
print yo

time.sleep(30)

doop = sa.delete_instance_snapshot('a2eb26d0-ac42-4a9d-a131-ad65fc70093f')
print doop

auth2 = authorization("bill","test")
#get the user dict
perms2 = auth2.get_auth()
store2 = server_storage_ops(perms2)
nova2 = server_ops(perms2)

auth3 = authorization("bill2","test")
#get the user dict
perms3 = auth3.get_auth()
store3 = server_storage_ops(perms3)
nova3 = server_ops(perms3)

inp = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",
       'instance_id':"e25caef9-a5af-4496-80e6-58a57faa0856",
       'volume_id':"8ee75400-1474-408d-be35-eadd54a9f5c5"
       }
yo = store2.detach_vol_from_server(inp)

inp = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",
       'instance_id':"8ea76508-29f3-4d7e-957e-b2f9c90f2027",
       'volume_id':"ed16222b-8971-445a-88c6-2aacca0e9c78"
       }
yo = store.detach_vol_from_server(inp)

inp = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",
       'instance_id':"e25caef9-a5af-4496-80e6-58a57faa0856",
       'volume_id':"8ee75400-1474-408d-be35-eadd54a9f5c5",
       'mount_point': '/dev/vdc'
       }
yo = store2.attach_vol_to_server(inp)

inp = {'project_id':"d4b29af44660474da7d5f884ec107f76",
       'instance_id':"e2cb3662-c42f-4299-b00e-851e99a67367",
       'volume_id':"1c01b26b-66d1-4ca2-ac34-ab24d2a9f18d",
       'mount_point': '/dev/vdc'
       }
yo = store.attach_vol_to_server(inp)

input_dict = {'project_id':'a4bff7fc3ff34a5787a711bdfec5fbc1','zone':'nova'}
yo = action.list_compute_hosts(input_dict)
print yo


input_dict = {'server_id':'4866b3c7-201d-4b31-ab33-762b5ae25628','project_id':'13d92fe4b2de4051abc5de0654277af0'}
on = sa.power_cycle_server(input_dict)
print on


input_dict = {'project_id':'13d92fe4b2de4051abc5de0654277af0','instance_id':'4866b3c7-201d-4b31-ab33-762b5ae25628'}
act = action.check_instance_status(input_dict)
print act


print "Createing a new virtual instance"
server = {'sec_group_name':'project1','avail_zone':'nova','amount':'1','sec_key_name':'project1','network_name':'project1','image_name':'Cirros-x86_64-0-3-1','flavor_name':'m1.tiny','name':'blah','project_id':'730b15279af34b959b26db5e38559a81'}
yo = nova.create_server(server)
print yo

'''
print "List the virtual intances in the database"
serv_list = nova.list_servers()
print serv_list
'''
print "---------------------------------------"
time.sleep(2)

#print "Get the info for the virtual instances in the database."
#for serv in serv_list:

get_server = nova.get_server(serv['server_id'])
print get_server
#print "---------------------------------------"
#time.sleep(2)

print "Get the info for the virtual instances 2nd time in the database."
for serv in serv_list:

input_dict = {'server_id':'e2cb3662-c42f-4299-b00e-851e99a67367','project_id':'d4b29af44660474da7d5f884ec107f76'}
get_server = nova.get_server(input_dict)
print get_server

exit

print "---------------------------------------"
time.sleep(2)

print "Update the virtual instance"
up_dict = {'server_id':serv['server_id'],'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'new_server_name':"testtest20"}
update = nova.update_server(up_dict)
print update
print "---------------------------------------"
time.sleep(2)

print "Createing a new user virtual instance"
server = {'sec_group_name':'billsecgroup','avail_zone':'nova','sec_key_name':'usertestkey','network_name':'ffvctest','image_name':'CirrOS','flavor_name':'m1.tiny','name':'user-vm'}
server3 = nova3.create_server(server)
print server3

print "Deleteing the virtual instance (admin)"
delete_dict = {'server_id':"914395e9-5260-48ef-b4b7-b8c68683a000",'project_id':"29dd2759d3a442b595b63cdc2d6ef8c5"}
delete = nova.delete_server(delete_dict)
print delete

print "Deleteing the virtual instance (admin)"
delete_dict2 = {'server_id':"b96162ca-687a-4630-9027-8e00abbf69fd",'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
delete2 = nova.delete_server(delete_dict2)
print delete2

print "Deleteing the virtual instance (user)"
delete_dict3 = {'server_id':"af731c8f-b537-4e74-be25-e106f300e3d3",'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
delete3 = nova2.delete_server(delete_dict3)
print delete3


print "Deleteing the virtual instance (user)"
delete_dict4 = {'server_id':"fd278f99-a6c9-4f22-bec3-842901437f50",'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
delete4 = nova2.delete_server(delete_dict4)
print delete4


print "List the user virtual intances in the database (user)"
serv_list3 = nova3.list_servers()
print serv_list3
print "---------------------------------------"
time.sleep(2)


print "List the user virtual intances in the database (power user)"
serv_list2 = nova2.list_servers()
print serv_list2
print "---------------------------------------"
time.sleep(2)

print "List the virtual intances in the database (admin)"
serv_list = nova.list_all_servers()
print serv_list
print "---------------------------------------"
time.sleep(2)

input_dict = {'project_id': '6492cba476994153800c5220a2f51bc2' ,'instance_id': 'd37d66ab-bdc7-42e4-939a-58a592f70a6e','volume_id': '6a110555-1128-40e6-9cc2-2ff01d927cef','mount_point': '/dev/vdc'}
print input_dict
attach = store.attach_vol_to_server(input_dict)

print attach

time.sleep(10)

input_dict2 = {'project_id': '0591dbde27ce4904b50cdd0d598e1d7e' ,'instance_id': 'ab25fbe7-945c-473e-94a7-3edf30958b1f','volume_id': '2f10ea39-0b36-4155-8424-6795911044ac'}
detach = store.detach_vol_from_server(input_dict2)

print detach

nova = server_ops(perms)
print "Createing a new virtual instance"
server = {'sec_group_name':'testgroup','avail_zone':'nova','sec_key_name':'testkey','network_name':'testnet','image_name':'cirros-64','flavor_name':'m1.tiny','name':'testvm'}
nova.create_server(server)

print "---------------------------------------"
time.sleep(2)

print "List the virtual intances in the database"
serv_list = nova.list_servers()
print serv_list
print "---------------------------------------"
time.sleep(2)

print "Get the info for the virtual instances in the database."
for serv in serv_list:
    get_server = nova.get_server(serv['server_name'])
    print get_server
print "---------------------------------------"
time.sleep(2)

print "Update the virtual instance"
up_dict = {'server_name':"testtest",'new_server_name':"testtest20"}
update = nova.update_server(up_dict)
print update
print "---------------------------------------"
time.sleep(2)

print "Deleteing the virtual instance"
input_dict = {'server_id':'a8fee5e8-049d-41fd-8081-c4c8d38c0fd7','project_id':'634911ba0d794a4dadefdf872e0d8abe'}
delete = nova.delete_server(input_dict)
print delete

input_dict = {'server_id':"39e20ffd-903d-45bd-a631-e4763f1c7377",'project_id':"de6647df708542ddafc00baf39534f56",'net_id':"52dea20c-c7fc-4db3-92a6-a0fa4a8f742c" }
dtp = nova.detach_server_from_network(input_dict)
print dtp

time.sleep(15)

input_dict = {'server_id':"39e20ffd-903d-45bd-a631-e4763f1c7377",'project_id':"de6647df708542ddafc00baf39534f56",'net_id':"52dea20c-c7fc-4db3-92a6-a0fa4a8f742c" }
atp = nova.attach_server_to_network(input_dict)
print atp
'''
