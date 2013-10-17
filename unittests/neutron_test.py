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
"""
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
"""

time.sleep(1)
print"-----------------------------------------"
print "Setting a subnet on new network"
dns = ["192.168.190.20"]
input_dict = {'net_name':"thistest8",'subnet_dhcp_enable':'true','subnet_dns':dns}
getsubnet = net.add_net_subnet(input_dict)
print getsubnet

time.sleep(1)
print "----------------------------------------"
print "getting the new network8 afte subnet added"
getnet = net.get_network("thistest8")
print getnet
"""
time.sleep(1)
print"-----------------------------------------"
print "attempting to deleteing the new network"
delnet = net.remove_network("thistest8")
print delnet
"""