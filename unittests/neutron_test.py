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

print"----------------------------------------"
print "createin a new external network"
create = {'net_name':"pubtest",'admin_state':"true", 'shared':"false"}
newpubnet = net.add_public_network(create)
print newpubnet
time.sleep(1)
'''
print"-----------------------------------------"
print "Setting a subnet on new network"
dns = ["192.168.190.20"]
input_dict = {'net_id':newpubnet['net_id'],'subnet_dhcp_enable':'true','subnet_dns':dns,'subnet_start_range':'192.168.177.10','subnet_end_range':'192.168.177.40','public_ip':'192.168.177.2','public_gateway':'192.168.177.1','public_subnet_mask':'255.255.255.0'}
getsubnet = net.add_public_subnet(input_dict)
print getsubnet


print "----------------------------------------"
print "deleteing subnet"
shit = net.remove_net_pub_subnet(getsubnet['subnet_id'])
print shit

print "creating a new network"
create = {'net_name':"internaltest",'admin_state':"true", 'shared':"false",'project_id':"523e5098be6c4438b428d7f3f94b3a2d"}
newnet = net.add_private_network(create)
print newnet

time.sleep(1)
print "----------------------------------------"
print "listing the networks"
newnet = net.list_internal_networks("9fad7cee35024b858795097f6e7d62da")
print newnet

time.sleep(1)
print "----------------------------------------"
print "listing the networks"
newnet2 = net.list_external_networks()
print newnet2

time.sleep(1)
print "----------------------------------------"
print "getting the new."
getnet = net.get_network("20400a44-7abc-4468-abfb-b2f45e74b6cb")
print getnet

time.sleep(1)
print"-----------------------------------------"
print "Setting a subnet on new network"
dns = ["192.168.190.20"]
input_dict2 = {'net_id':"4ea066c7-f376-484b-ae96-773e35f1b99c",'subnet_dhcp_enable':'true'}
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
listsub = net.list_net_subnet("20400a44-7abc-4468-abfb-b2f45e74b6cb")
print listsub

time.sleep(1)
print "---------------------------------------"
print "get the subnet"
subnet = listsub[0]
getsub3 = net.get_net_subnet('e007d46e-df30-4686-83f7-4d01ec5daebc')
print getsub3

time.sleep(1)
print "---------------------------------------"
print "Deleteing the subnet from the network."
del_dict = {'subnet_name':'int-sub-3','net_id':'4ea066c7-f376-484b-ae96-773e35f1b99c'}
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

input_dict = {'net_id':"52dea20c-c7fc-4db3-92a6-a0fa4a8f742c",
              'subnet_id':"ae1c8992-9d71-4146-a9f5-dcfaf7aebbde",
              'project_id':"de6647df708542ddafc00baf39534f56"}
yo = net.list_net_ports(input_dict)
print yo
'''
