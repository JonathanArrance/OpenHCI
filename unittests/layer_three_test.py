from transcirrus.common.auth import authorization
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.neutron.ports import port_ops
import time

auth = authorization('admin','password')

a = auth.get_auth()
router = layer_three_ops(a)
'''
print "Adding a new router"
r = {'router_name':'inttestrouter','project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
create = router.add_router(r)
print create
time.sleep(1)
print"-------------------------------------------------"
'''
print "Adding an internal interface."
add_dict = {'router_id':"6896172e-7788-4c05-bbec-c3b71a5028c1",'subnet_id':"37ae0641-3dd2-4d4e-a78d-e436e266bf47",'project_id':'975378d013664df394e3284bd7030108'}
int_interface = router.add_router_internal_interface(add_dict)
print int_interface
time.sleep(1)
print "-------------------------------------------------"

'''
print "Add a gateway"
add_dict2 = {'router_id':"6429d4e8-9dae-4595-8d6b-62b807380ac3",'ext_net_id':"a2a21d14-9630-455b-b31a-1d3d1d8c0680"}
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

print "Allocating a new floating ip"
s = {'ext_net_id':"7bb5744c-c34b-48b5-83b5-5325e36f12ef",'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
yo = router.allocate_floating_ip(s)
print yo

print "Listing floating ips"
yo2 = router.list_floating_ips()
print yo2

for y in yo2:
    print "Getting floating ip info"
    yo3 = router.get_floating_ip(y['floating_ip_id'])
    print yo3
    

print "attaching floating ip to instance"
update_dict = {'floating_ip':yo['floating_ip'],'instance_id':"e25caef9-a5af-4496-80e6-58a57faa0856",'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'action':"add"}
yo4 = router.update_floating_ip(update_dict)
print yo4

print "Listing floating ips"
yo5 = router.list_floating_ips()
print yo5

for z in yo5:
    print "Getting floating ip info"
    yo6 = router.get_floating_ip(z['floating_ip_id'])
    print yo6

print "detaching floating ip from instance"
update_dict = {'floating_ip':yo['floating_ip'],'instance_id':"e25caef9-a5af-4496-80e6-58a57faa0856",'project_id':"523e5098be6c4438b428d7f3f94b3a2d",'action':"remove"}
yo12 = router.update_floating_ip(update_dict)
print yo12

print "Listing floating ips"
yo10 = router.list_floating_ips()
print yo10

for z2 in yo10:
    print "Getting floating ip info"
    yo11 = router.get_floating_ip(z2['floating_ip_id'])
    print yo11

print "deallocating a new floating ip"
e = {'floating_ip':yo['floating_ip'],'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
yo7 = router.deallocate_floating_ip(e)
print yo7

print "Listing floating ips"
yo13 = router.list_floating_ips()
print yo13

for z3 in yo13:
    print "Getting floating ip info"
    yo14 = router.get_floating_ip(z3['floating_ip_id'])
    print yo14
'''
