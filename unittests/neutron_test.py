import time
from transcirrus.common.auth import authorization
from transcirrus.component.neutron.network import neutron_net_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","password")
#get the user dict
d = a.get_auth()

print "Instantiating neutron_net_ops object."
net = neutron_net_ops(d)
'''
print"----------------------------------------"
print "createin a new external network"
create = {'net_name':"Jon4",'admin_state':"true", 'shared':"true"}
newpubnet = net.add_public_network(create)
print newpubnet
time.sleep(1)

print"-----------------------------------------"
print "Setting a subnet on new network"
dns = ["192.168.190.20"]
input_dict = {'net_id':newpubnet['net_id'],'subnet_dhcp_enable':'true','subnet_dns':dns,'subnet_start_range':'192.168.167.10','subnet_end_range':'192.168.167.40','public_ip':'192.168.167.2','public_gateway':'192.168.167.1','public_subnet_mask':'255.255.255.0'}
getsubnet = net.add_public_subnet(input_dict)
print getsubnet

print "creating a new network"
create = {'net_name':"internaltest",'admin_state':"true", 'shared':"true",'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
newnet = net.add_private_network(create)
print newnet

time.sleep(1)
print "----------------------------------------"
print "listing the networks"
newnet = net.list_networks()
print newnet
'''
time.sleep(1)
print "----------------------------------------"
print "getting the new."
getnet = net.get_network("03a730bb-72d1-4b32-ae13-15de60fbfef9")
print getnet
'''
time.sleep(1)
print"-----------------------------------------"
print "Setting a subnet on new network"
dns = ["192.168.190.20"]
input_dict2 = {'net_id':"4665a6b5-f5cc-46d0-8fb7-2b1a90a1ffae",'subnet_dhcp_enable':'true','subnet_dns':dns}
getsubnet2 = net.add_net_subnet(input_dict2)
print getsubnet2

time.sleep(1)
print "----------------------------------------"
print "getting the new network8 after subnet added"
getnet2 = net.get_network("4665a6b5-f5cc-46d0-8fb7-2b1a90a1ffae")
print getnet2

time.sleep(1)
print "----------------------------------------"
print "Listing the subnets in use for thistest8"
listsub = net.list_net_subnet("4665a6b5-f5cc-46d0-8fb7-2b1a90a1ffae")
print listsub

time.sleep(1)
print "---------------------------------------"
print "get the subnet"
subnet = listsub[0]
getsub3 = net.get_net_subnet(subnet['subnet_name'])
print getsub3

time.sleep(1)
print "---------------------------------------"
print "Deleteing the subnet from the network."
del_dict = {'subnet_name':'crap','net_id':getnet['net_id']}
delsub = net.remove_net_subnet(del_dict)
print delsub

time.sleep(1)
print "----------------------------------------"
print "Listing the subnets in use for thistest8"
listsub2 = net.list_net_subnet(getnet['net_id'])
print listsub2


t = {'subnet_name':'int-sub-3','net_id':'4665a6b5-f5cc-46d0-8fb7-2b1a90a1ffae'}
tdel = net.remove_net_subnet(t)
print tdel

time.sleep(1)
print"----------------------------------------"
print "attempting to deleteing the new network"
r = {'net_id':"4665a6b5-f5cc-46d0-8fb7-2b1a90a1ffae",'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
delnet = net.remove_network(r)
print delnet

time.sleep(1)
print "----------------------------------------"
print "listing the networks"
newnet = net.list_networks()
print newnet
'''
