from transcirrus.common.auth import authorization
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.neutron.ports import port_ops
import time

auth = authorization('admin','password')

a = auth.get_auth()
router = layer_three_ops(a)
'''
print "Test the ports"
ports = port_ops(a)
yo = ports.get_port("f9547289-182d-4c2a-acf2-5ec3497adec3")
print yo
time.sleep(1)
print "------------------------------------------------"

print "Adding a new router"
r = {'router_name':'ffvcrouter1','project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
create = router.add_router(r)
print create
time.sleep(1)
print"-------------------------------------------------"

print "Adding an internal interface."
add_dict = {'router_id':create['router_id'],'subnet_name':"int-sub-2",'project_id':'523e5098be6c4438b428d7f3f94b3a2d'}
int_interface = router.add_router_internal_interface(add_dict)
print int_interface
time.sleep(1)
print "-------------------------------------------------"


print "Add a gateway"
add_dict2 = {'router_id':create['router_id'],'ext_net_id':"7bb5744c-c34b-48b5-83b5-5325e36f12ef"}
ext_int = router.add_router_gateway_interface(add_dict2)
print ext_int
time.sleep(1)
print "-------------------------------------------------"


print "listing the routers"
lister = router.list_routers()
print lister
time.sleep(1)

print "updateing a router"
print create2['router_id']
update_dict = {'router_id':create2['router_id'],'router_name':"jonarranceYO",'router_admin_state_up':"false"}
update = router.update_router(update_dict)
print update

del_dict = {'router_id':"a195ec8b-5486-4cef-abc1-ecd99518ea03",'subnet_name':"test"}
delete = router.delete_router_internal_interface(del_dict)
print delete
time.sleep(1)
print "-------------------------------------------------"

del_ext = router.delete_router_gateway_interface("a195ec8b-5486-4cef-abc1-ecd99518ea03")
print del_ext
time.sleep(1)
print "--------------------------------------------------"

s = {'ext_net_id':"7bb5744c-c34b-48b5-83b5-5325e36f12ef",'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
yo = router.allocate_floating_ip(s)
print yo
'''
yo2 = router.list_floating_ips()
print yo2

for y in yo2:
    yo3 = router.get_floating_ip(y['floating_ip_id'])
    print yo3