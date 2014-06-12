#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.component.nova.server import server_ops
from transcirrus.component.nova.storage import server_storage_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
auth = authorization("admin","password")
#get the user dict
perms = auth.get_auth()
store = server_storage_ops(perms)
nova = server_ops(perms)

'''
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

inp = {'project_id':"523e5098be6c4438b428d7f3f94b3a2d",
       'instance_id':"8ea76508-29f3-4d7e-957e-b2f9c90f2027",
       'volume_id':"ed16222b-8971-445a-88c6-2aacca0e9c78",
       'mount_point': '/dev/vdc'
       }
yo = store.attach_vol_to_server(inp)


print "Createing a new virtual instance"
server = {'sec_group_name':'keven5','avail_zone':'nova','sec_key_name':'keven5','network_name':'keven5','image_name':'Cirros-x86_64-0-3-1','flavor_name':'m1.tiny','name':'thevm','project_id':'441e0a31c2ed4168872ef9f53aad4e63'}
yo = nova.create_server(server)
print yo

print "List the virtual intances in the database"
serv_list = nova.list_servers()
print serv_list
print "---------------------------------------"
time.sleep(2)

print "Get the info for the virtual instances in the database."
for serv in serv_list:
    get_server = nova.get_server(serv['server_id'])
    print get_server
print "---------------------------------------"
time.sleep(2)

print "Get the info for the virtual instances 2nd time in the database."
for serv in serv_list:

input_dict = {'server_id':'57f1ebfb-f476-49e6-9083-87ade1dca73b','project_id':'84d3e074012a42ce919771c503993f4e'}
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
delete_dict = {'server_id':"a8fee5e8-049d-41fd-8081-c4c8d38c0fd7",'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
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

input_dict = {'project_id': '0591dbde27ce4904b50cdd0d598e1d7e' ,'instance_id': '3e8e74fa-cd4d-41d6-9e34-73614418b3db','volume_id': '15ecae50-0975-408c-b69a-b54e6530bf4b','mount_point': '/dev/vdc'}
attach = store.attach_vol_to_server(input_dict)

print attach

time.sleep(10)

input_dict2 = {'project_id': '0591dbde27ce4904b50cdd0d598e1d7e' ,'instance_id': '3e8e74fa-cd4d-41d6-9e34-73614418b3db','volume_id': '15ecae50-0975-408c-b69a-b54e6530bf4b'}
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
