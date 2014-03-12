from transcirrus.common.auth import authorization
from transcirrus.component.neutron.ports import port_ops

auth = authorization('shithead','password')

a = auth.get_auth()

ports = port_ops(a)


li = {'net_id':'6d599861-19be-4a50-858f-91d0b709ea58','project_id':'30b63ffa0d95440b83d204a2456f16ef','subnet_id':'a993bf3b-782e-4169-b7ad-71085bac507c'}
list = ports.list_net_ports(li)
print list

y = {'port_id':'c59c59d2-9372-4f86-8269-96712cd6ea1e','project_id':'a96120a697754aff80eeb4ab4554f025'}
yo = ports.get_net_port(y)
print yo
