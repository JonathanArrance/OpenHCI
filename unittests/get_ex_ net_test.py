from transcirrus.common.auth import authorization
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.component.keystone.keystone_tenants import tenant_ops

a = authorization("admin","password")
auth = a.get_auth()
to = tenant_ops(auth)
no = neutron_net_ops(auth)
l3o = layer_three_ops(auth)
project = to.get_tenant("ffvc2")
pid = project["project_id"]
pub_net_list  = no.list_external_networks()
routers       = l3o.list_routers(pid)

public_networks={}
for net in pub_net_list: public_networks[net['net_name']]= no.get_network(net['net_id'])

default_public = public_networks.values()[0]['net_id']
