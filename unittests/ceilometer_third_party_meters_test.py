from transcirrus.common.auth import authorization
from transcirrus.component.ceilometer.ceilometer_third_party_meters import ThirdPartyMeters

print "Instantiating authorization object for an default admin"
c = authorization("admin", "password")

print "Get admin authorization dictionary"
b = c.get_auth()

print "Instantiating mem patch object"
mo = ThirdPartyMeters(b)

# print "Get meter memory.usage for instance"
# instance_virsh_name = "instance-00000001"
# project_id = "4633053212a84fe3aac17c1269004ecb"
# instance_id = "25f9162f-a58c-4b65-971d-48c5ba40b6f2"
# usage = mo.manual_inspect_memory_usage(instance_virsh_name, project_id, instance_id)
#
# print "Get meter memory.resident for instance"
# instance_virsh_name = "instance-00000001"
# project_id = "4633053212a84fe3aac17c1269004ecb"
# instance_id = "25f9162f-a58c-4b65-971d-48c5ba40b6f2"
# resident = mo.manual_inspect_memory_resident(instance_virsh_name, project_id, instance_id)


print "Get meter disk.info for instance"
instance_virsh_name = "instance-00000001"
project_id = "4633053212a84fe3aac17c1269004ecb"
instance_id = "25f9162f-a58c-4b65-971d-48c5ba40b6f2"
disk = mo.manual_inspect_disk_info(instance_virsh_name, project_id, instance_id)

