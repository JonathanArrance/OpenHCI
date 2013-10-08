import time
from transcirrus.common.auth import authorization
from transcirrus.component.neutron.network import neutron_net_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","builder")
#get the user dict
d = a.get_auth()

print "Instantiating user_ops object."
net = neutron_net_ops(d)

create = {'net_name':"thistest6",'admin_state':"true", 'shared':"true"}
newnet = net.add_private_network(create)
print newnet

#newnet = net.list_networks()
#print newnet