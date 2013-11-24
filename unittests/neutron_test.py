import time
from transcirrus.common.auth import authorization
from transcirrus.component.neutron.network import neutron_net_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","builder")
#get the user dict
d = a.get_auth()

print "Instantiating neutron_net_ops object."
net = neutron_net_ops(d)

print"----------------------------------------"
print "creating a new network"
create = {'net_name':"thistest8",'admin_state':"true", 'shared':"true"}
newnet = net.add_private_network(create)
print newnet

time.sleep(1)
print "----------------------------------------"
print "listing the networks"
newnet = net.list_networks()
print newnet

time.sleep(1)
print "----------------------------------------"
print "getting the new network8"
getnet = net.get_network("thistest8")
print getnet

time.sleep(1)
print"-----------------------------------------"
print "Setting a subnet on new network"
dns = ["192.168.190.20"]
input_dict = {'net_name':"thistest8",'subnet_dhcp_enable':'true','subnet_dns':dns}
getsubnet = net.add_net_subnet(input_dict)
print getsubnet

time.sleep(1)
print "----------------------------------------"
print "getting the new network8 after subnet added"
getnet = net.get_network("thistest8")
print getnet

time.sleep(1)
print "----------------------------------------"
print "Listing the subnets in use for thistest8"
listsub = net.list_net_subnet("thistest8")
print listsub

time.sleep(1)
print "---------------------------------------"
print "get the subnet"
subnet = listsub[0]
getsub = net.get_net_subnet(subnet['subnet_name'])
print getsub

time.sleep(1)
print "---------------------------------------"
print "Deleteing the subnet from the network."
del_dict = {'subnet_name':'crap','net_id':getnet['net_id']}
delsub = net.remove_net_subnet(del_dict)
print delsub

time.sleep(1)
print "----------------------------------------"
print "Listing the subnets in use for thistest8"
listsub2 = net.list_net_subnet("thistest8")
print listsub2


time.sleep(1)
print"----------------------------------------"
print "attempting to deleteing the new network"
delnet = net.remove_network("thistest8")
print delnet

time.sleep(1)
print "----------------------------------------"
print "listing the networks"
newnet = net.list_networks()
print newnet
