import sys
import time
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.neutron.network import neutron_net_ops

a = authorization("admin","password")

#get the user dict
d = a.get_auth()
print d

print "Instantiating a new tenant ops object."
ten = tenant_ops(d)
time.sleep(1)
print "----------------------------------------"

print "creating test project"
proj = ten.create_tenant("ffvc2")
print proj
time.sleep(1)
print "----------------------------------------"

print "Instantiating user_ops object."
use = user_ops(d)

print "Create a new standard user with no project."
new_user_dict = {"username":'bill3',"password":"test","userrole":"pu","email":"bill@domain.com"}
create = use.create_user(new_user_dict)
print create
time.sleep(1)
print "----------------------------------------"

print "Adding user %s to test project" %(create['username'])
add_user_dict = {"username":"bill3","user_role":'pu',"project_name":'ffvc2'}
add = use.add_user_to_project(add_user_dict)
print add

print "Create a new standard user with no project."
new_user_dict = {"username":'bill4',"password":"test","userrole":"user","email":"test@domain.com"}
create = use.create_user(new_user_dict)
print create
time.sleep(1)
print "----------------------------------------"

print "Adding user %s to test project" %(create['username'])
add_user_dict = {"username":"bill4","user_role":'user',"project_name":'ffvc2'}
add = use.add_user_to_project(add_user_dict)
print add


print "----------------------------------------"
time.sleep(1)
print "Instantiating neutron_net_ops object."


net = neutron_net_ops(d)


print "creating a new network"
create = {'net_name':"ffvcnet2",'admin_state':"true", 'shared':"true",'project_id':"proj['project_id']"}
newnet = net.add_private_network(create)
print newnet


print "----------------------------------------"
time.sleep(1)
print "Setting a subnet on new network"
dns = ["192.168.190.20"]
input_dict = {'net_id':newnet['net_id'],'subnet_dhcp_enable':'true','subnet_dns':dns}
getsubnet = net.add_net_subnet(input_dict)
print getsubnet
