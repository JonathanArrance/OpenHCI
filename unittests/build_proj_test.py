import sys
import time
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.component.nova.server import server_ops

a = authorization("admin","password")

#get the user dict
d = a.get_auth()
print d
'''
print "Instantiating a new tenant ops object."
ten = tenant_ops(d)
time.sleep(1)
print "----------------------------------------"

print "creating test project"
proj = ten.create_tenant("ffvc")
print proj
time.sleep(1)
print "----------------------------------------"
'''
print "Instantiating user_ops object."
use = user_ops(d)
nova = server_ops(d)

print "Create a new standard user with no project."
new_user_dict = {"username":'jill',"password":"test","userrole":"pu","email":"jill@domain.com"}
create = use.create_user(new_user_dict)
print create
time.sleep(1)
print "----------------------------------------"

print "Adding user %s to test project" %(create['username'])
add_user_dict = {"username":"jill","user_role":'pu',"project_name":'yo'}
add = use.add_user_to_project(add_user_dict)
print add
time.sleep(1)

print "Createing security group with default ports - default"
#create a security group with default ports
create_group = {"group_name": 'yosec',"group_desc": 'This is a test','project_id':"66069dc297a449ca90582187011ac8e9"}
sec_group = nova.create_sec_group(create_group)
print sec_group
print "------------------------------------------------"
time.sleep(1)

print "Create a new standard user with no project."
new_user_dict2 = {"username":'jill2',"password":"test","userrole":"pu","email":"jill2@domain.com"}
create2 = use.create_user(new_user_dict2)
print create2
time.sleep(1)
print "----------------------------------------"

print "Adding user %s to test project" %(create2['username'])
add_user_dict2 = {"username":"jill2","user_role":'user',"project_name":'yo'}
add2 = use.add_user_to_project(add_user_dict2)
print add2
'''
print "Create a new standard user with no project."
new_user_dict = {"username":'bill2',"password":"test","userrole":"user","email":"test@domain.com"}
create = use.create_user(new_user_dict)
print create
time.sleep(1)
print "----------------------------------------"

print "Adding user %s to test project" %(create['username'])
add_user_dict = {"username":"bill2","user_role":'user',"project_name":'ffvc'}
add = use.add_user_to_project(add_user_dict)
print add


print "----------------------------------------"
time.sleep(1)
print "Instantiating neutron_net_ops object."


net = neutron_net_ops(d)


print "creating a new network"
create = {'net_name':"ffvcnet",'admin_state':"true", 'shared':"true",'project_id':"daf2a16e972c4cf4aaa8f722acccdd70"}
newnet = net.add_private_network(create)
print newnet


print "----------------------------------------"
time.sleep(1)
print "Setting a subnet on new network"
dns = ["192.168.190.20"]
input_dict = {'net_id':newnet['net_id'],'subnet_dhcp_enable':'true','subnet_dns':dns}
getsubnet = net.add_net_subnet(input_dict)
print getsubnet
'''