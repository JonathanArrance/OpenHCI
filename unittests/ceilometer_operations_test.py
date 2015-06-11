from transcirrus.common.auth import authorization
from transcirrus.common.auth import authorization
import transcirrus.operations.obtain_memory_usage as memory_usage_ops

print "Instantiating authorization object for an default admin"
c = authorization("admin", "password")

print "Get admin authorization dictionary"
b = c.get_auth

print "Check elements of list"
memory_usage_ops.daemonize(True, 600)

