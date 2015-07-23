#!/usr/bin/python
from transcirrus.common.auth import authorization
from transcirrus.component.nova.absolute_limits import absolute_limits_ops

print "Instantiating authorization object for an default admin"
c = authorization("user", "password")

print "Get admin authorization dictionary"
b = c.get_auth()

print "Instantiating absolution_limit object"
ho = absolute_limits_ops(b)

print "Get limits"

project_id = "9e8d9999e31c4e41a38867ec0e4ae542"
hl = ho.get_absolute_limit_for_tenant(project_id)
print hl
