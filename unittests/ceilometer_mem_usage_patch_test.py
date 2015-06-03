from transcirrus.common.auth import authorization
from transcirrus.component.ceilometer.ceilometer_mem_usage_patch import MemoryUtilization

print "Instantiating authorization object for an default admin"
c = authorization("admin", "password")

print "Get admin authorization dictionary"
b = c.get_auth()
print b

print "Instantiating mem patch object"
mo = MemoryUtilization(b)
print mo

print "Get meter memory.usage for instance"
instance_virsh_name = "instance-00000001"
project_id = "c69fb4f6feb2456bbbcb16a8f00d9ef3"
instance_id = "ea3eca10-32d6-4c82-b39e-bdd68a6b09ae"
pm = mo.manual_inspect_memory_usage(instance_virsh_name, project_id, instance_id)
print pm