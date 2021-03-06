from transcirrus.common.auth import authorization
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.neutron.ports import port_ops
import time

auth = authorization('admin','password')

a = auth.get_auth()
router = layer_three_ops(a)


ip_list = router.list_floating_ips("6492cba476994153800c5220a2f51bc2")
print "fip list"
print ip_list
'''
get_ip = router.get_floating_ip("2476890a-ab03-4c16-b99c-b5fddd92d8e4");
print "get ip"
print get_ip
print

update_dict = {'floating_ip':"192.168.10.162",'instance_id':"aa6a498e-dbd7-44fa-8dd5-b56feefcdaf1",'project_id':"d7b57ec600724d429a3c7916d2243474",'action':"add"}
update_ip = router.update_floating_ip(update_dict)
print "update ip"
print update_ip


print "Adding a new router"
r = {'router_name':'inttestrouter10','project_id':"84d3e074012a42ce919771c503993f4e"}
create = router.add_router(r)
print create
time.sleep(1)
print"-------------------------------------------------"

print "Adding an internal interface."
add_dict = {'router_id':create['router_id'],'subnet_id':"3dfe0e67-61ed-43f6-bad7-db6fa146ac24",'project_id':'84d3e074012a42ce919771c503993f4e'}
int_interface = router.add_router_internal_interface(add_dict)
print int_interface
time.sleep(1)
print "-------------------------------------------------"

print "Add a gateway"
add_dict2 = {'router_id':create['router_id'],'ext_net_id':"bf14df23-065b-4aaf-ab2a-8ca77fca2755","project_id":"84d3e074012a42ce919771c503993f4e"}
ext_int = router.add_router_gateway_interface(add_dict2)
print ext_int
time.sleep(1)
print "-------------------------------------------------"


print "listing the routers"
lister = router.list_routers()
print lister
time.sleep(1)

print "updateing a router"
print create['router_id']
update_dict = {'router_id':create['router_id'],'router_name':"jonarranceYO",'router_admin_state_up':"false"}
update = router.update_router(update_dict)
print update

del_dict = {'router_id':'','subnet_id':"7e45e5b6-f95b-415a-893a-c8e092f0150d",'project_id':"a38c70b7a87c404cab33d0a5959ba57a"}
delete = router.delete_router_internal_interface(del_dict)
print delete
time.sleep(1)
print "-------------------------------------------------"

router_stuff = {'router_id':create['router_id'],'project_id':"a38c70b7a87c404cab33d0a5959ba57a"}
del_ext = router.delete_router_gateway_interface(router_stuff)
print del_ext
time.sleep(1)
print "--------------------------------------------------"

print "deleteing router"
router_dict = {'router_id':'411fb076-5f22-474b-8b8b-d05bb646b197','project_id':"84d3e074012a42ce919771c503993f4e"}
yo = router.delete_router(router_dict)
print yo

print "Allocating a new floating ip"
s = {'ext_net_id':"1d8bb1cd-85b6-45fa-8b43-f51eb302aa25",'project_id':"9a2b2eae323f437eb60183d26fa76a50"}
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
update_dict = {'floating_ip':'192.168.10.71','instance_id':"ac65509e-da9d-4d2a-b82f-ad269287367d",'project_id':"1c52c0fdf145438d9a8b3b114cbc608a",'action':"add"}
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
update_dict = {'floating_ip':'192.168.2.202','instance_id':"aac0f01-bdf6-4368-b59d-4c04ae9697ae",'project_id':"a38c70b7a87c404cab33d0a5959ba57a",'action':"remove"}
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
e = {'floating_ip':yo['floating_ip'],'project_id':"a38c70b7a87c404cab33d0a5959ba57a"}
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
