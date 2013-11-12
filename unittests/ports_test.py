from transcirrus.common.auth import authorization
from transcirrus.component.neutron.layer_three import routing_ops
from transcirrus.component.neutron.ports import port_ops

auth = authorization('admin','builder')

a = auth.get_auth()

ports = port_ops(a)

yo = ports.get_port("f9547289-182d-4c2a-acf2-5ec3497adec3")

print yo