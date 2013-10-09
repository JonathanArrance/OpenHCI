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
create = {'net_name':"thistest7",'admin_state':"true", 'shared':"true"}
newnet = net.add_private_network(create)
print newnet

time.sleep(1)
print "----------------------------------------"
print "listing the networks"
newnet = net.list_networks()
print newnet

time.sleep(1)
print "----------------------------------------"
print "getting the new network7"
getnet = net.get_network("thistest7")
print getnet

time.sleep(1)
print"-----------------------------------------"
print "deleteing the new network"
delnet = net.remove_network("thistest7")
print delnet