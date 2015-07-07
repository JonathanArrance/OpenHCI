#!/usr/bin/python
from transcirrus.common.auth import authorization
from transcirrus.component.nova.hypervisor import hypervisor_ops

print "Instantiating authorization object for an default admin"
c = authorization("admin", "password")

print "Get admin authorization dictionary"
b = c.get_auth()

print "Instantiating hypervisor object"
ho = hypervisor_ops(b)

print "Get hypervisor list"
project_id = "8c37340157634b29be59143240f0a5e8"
hl = ho.list_hypervisors(project_id)
print hl

print "Get hypervisor stats"
project_id = "8c37340157634b29be59143240f0a5e8"
hs = ho.get_hypervisor_stats(project_id)
print hs

print "list instances on a given hypervisor"
project_id = "8c37340157634b29be59143240f0a5e8"
hypervisor_id = 1
hls = ho.list_servers_on_hypervisor(project_id, hypervisor_id)
print hls

print "Get details on a hypervisor"
project_id = "8c37340157634b29be59143240f0a5e8"
hypervisor_id = 1
hd = ho.get_hypervisor_details(project_id, hypervisor_id)
print hd

print "Get the uptime for a hypervisor"
project_id = "8c37340157634b29be59143240f0a5e8"
hypervisor_id = 1
hu = ho.get_hypervisor_uptime(project_id, hypervisor_id)
print hu