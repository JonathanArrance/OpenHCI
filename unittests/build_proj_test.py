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
from transcirrus.component.neutron.layer_three import layer_three_ops

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
proj = ten.create_tenant("ffvc2")
print proj
time.sleep(1)
print "----------------------------------------"

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

add_user_dict = {"username":"jill","user_role":'pu',"project_name":'ffvc2'}

add = use.add_user_to_project(add_user_dict)
print add
time.sleep(1)

print "Creating security group with default ports - default"
#create a security group with default ports
create_group = {"group_name": 'yosec',"group_desc": 'This is a test','project_id':proj['tenant_id']}
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
add_user_dict2 = {"username":"jill2","user_role":'user',"project_name":'ffvc2'}
add2 = use.add_user_to_project(add_user_dict2)
print add2
time.sleep(1)

print "Create a new standard user with no project."
new_user_dict = {"username":'bill4',"password":"test","userrole":"user","email":"test@domain.com"}
create = use.create_user(new_user_dict)
print create

print "----------------------------------------"
time.sleep(1)
print "Instantiating neutron_net_ops object."

net = neutron_net_ops(d)

print "creating a new network"
create = {'net_name':"ffvcnet2",'admin_state':"true", 'shared':"true",'project_id':proj['tenant_id']}
newnet = net.add_private_network(create)
print newnet


print "----------------------------------------"
time.sleep(1)
print "Setting a subnet on new network"
dns = ["192.168.190.20"]
input_dict = {'net_id':newnet['net_id'],'subnet_dhcp_enable':'true','subnet_dns':dns}
getsubnet = net.add_net_subnet(input_dict)
print getsubnet


print "Adding a new router"
r = {'router_name':'inttestrouter','project_id':"9fad7cee35024b858795097f6e7d62da"}
create = router.add_router(r)
print create
time.sleep(1)
print"-------------------------------------------------"

print "Adding an internal interface."
add_dict = {'router_id':"bb1ee95f-7a33-4a1a-9a5f-e0a48eba106e",'subnet_id':"e007d46e-df30-4686-83f7-4d01ec5daebc",'project_id':"9fad7cee35024b858795097f6e7d62da"}
int_interface = router.add_router_internal_interface(add_dict)
print int_interface
time.sleep(1)
print "-------------------------------------------------"

print "Add a gateway"
add_dict2 = {'router_id':"bb1ee95f-7a33-4a1a-9a5f-e0a48eba106e",'ext_net_id':"1e1af977-d218-4f10-83b3-741a1aa96bd2",'project_id':"9fad7cee35024b858795097f6e7d62da"}
ext_int = router.add_router_gateway_interface(add_dict2)
print ext_int
time.sleep(1)
print "-------------------------------------------------"
'''
router = layer_three_ops(d)
del_dict = {'router_id':"bb1ee95f-7a33-4a1a-9a5f-e0a48eba106e",'subnet_id':"e007d46e-df30-4686-83f7-4d01ec5daebc",'project_id':"9fad7cee35024b858795097f6e7d62da"}
delr = router.delete_router_internal_interface(del_dict)
print delr

