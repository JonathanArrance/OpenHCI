from transcirrus.common.auth import authorization
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.neutron.ports import port_ops
import time

auth = authorization('admin','builder')

a = auth.get_auth()

'''
print "Test the ports"
ports = port_ops(a)
yo = ports.get_port("f9547289-182d-4c2a-acf2-5ec3497adec3")
print yo
time.sleep(1)
print "------------------------------------------------"
'''
router = layer_three_ops(a)
'''
print "Adding a new router"
create = router.add_router("jonarrance")
print create
time.sleep(1)
print"-------------------------------------------------"

print "Adding another router"
create2 = router.add_router("jonarrance6")
print create2
time.sleep(1)
print "------------------------------------------------"

print "listing the routers"
lister = router.list_routers()
print lister
time.sleep(1)

print "------------------------------------------------"
print "Adding an internal interface."
add_dict = {'router_id':create2['router_id'],'subnet_name':"test"}
int_interface = router.add_router_internal_interface(add_dict)
print int_interface
time.sleep(1)
print "-------------------------------------------------"


print "Add a gateway"
add_dict2 = {'router_id':create2['router_id'],'ext_net_id':"636858c5-7124-471e-b465-bc353c2db12a"}
ext_int = router.add_router_gateway_interface(add_dict2)
print ext_int
time.sleep(1)
print "-------------------------------------------------"

print "updateing a router"
print create2['router_id']
update_dict = {'router_id':create2['router_id'],'router_name':"jonarranceYO",'router_admin_state_up':"false"}
update = router.update_router(update_dict)
print update
'''
'''
del_dict = {'router_id':"a195ec8b-5486-4cef-abc1-ecd99518ea03",'subnet_name':"test"}
delete = router.delete_router_internal_interface(del_dict)
print delete
time.sleep(1)
print "-------------------------------------------------"
'''

del_ext = router.delete_router_gateway_interface("a195ec8b-5486-4cef-abc1-ecd99518ea03")
print del_ext
time.sleep(1)
print "--------------------------------------------------"