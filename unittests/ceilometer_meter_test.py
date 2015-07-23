#!/usr/bin/python
from transcirrus.common.auth import authorization
from transcirrus.component.ceilometer.ceilometer_meters import meter_ops

c = authorization("admin", "password")
b = c.get_auth()
mo = meter_ops(b)
# print mo

# print "Post meter memory.usage"
# project_id = "9e8d9999e31c4e41a38867ec0e4ae542"
# counter_type = "gauge"
# counter_name = "memory.usage"
# counter_volume = 200.12345
# counter_unit = "MB"
# resource_id = "ba1f5b04-d222-45d1-a010-583ba9a23d61"
# pm = mo.post_meter(project_id, counter_type, counter_name, counter_volume, counter_unit, resource_id)
# print pm

# print "Listing meters"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# lm = mo.list_meters(project_id)
# print lm

# print "Show CPU percentage statistics"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T20%3A00"
# meter_type = "compute.node.cpu.percent"
# cpu_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, None)
# print cpu_stats
#
# print "Show disk root usage statistics"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T14%3A00"
# meter_type = "disk.root.size"
# disk_root_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, None)
# print disk_root_stats

print "Show memory usage & VCPU stats"
project_id = "e3dd24d867d442c3badf02fc0c475f54"
tenant_identifier = "e3dd24d867d442c3badf02fc0c475f54"
resource_identifier = "3c8b0be9-a646-49aa-885a-6f7687f025fd"
start_time = "2015-07-12T13%3A00"
end_time = "2015-07-16T23%3A00"
meter_list = "memory.usage,vcpus"
meters = meter_list.split(",")
meter_stats = mo.show_stats_for_meter_list(project_id, start_time, end_time, meters, tenant_identifier,
                                           resource_identifier)
print meter_stats

# print "Show memory usage statistics"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T14%3A00"
# meter_type = "memory.usage"
# memory_usage_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, None)
# print memory_usage_stats
#
# print "Show VCPU statistics"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T14%3A00"
# meter_type = "vcpus"
# vcpu_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, None)
# print vcpu_stats

# print "Show VCPU statistics for resource"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T23%3A00"
# meter_type = "vcpus"
# resource_identifier = "9d60427f-2602-4582-9bd6-18b9757f976f"
# resource_vcpu_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, resource_identifier)
# print resource_vcpu_stats
#
# print "Show memory.usage statistics for resource"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T23%3A00"
# meter_type = "memory.usage"
# resource_identifier = "37128ad6-daaa-4d22-9509-b7e1c6b08697"
# resource_memory_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, resource_identifier)
# print resource_memory_stats
#
# print "Show disk.root.size statistics for resource"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T23%3A00"
# meter_type = "disk.root.size"
# resource_identifier = "9d60427f-2602-4582-9bd6-18b9757f976f"
# resource_disk_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, resource_identifier)
# print resource_disk_stats
#
# print "Show VCPU statistics for tenant"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T23%3A00"
# meter_type = "vcpus"
# tenant_identifier = "10796d79f7124e0f8c9505b64bd8819d"
# tenant_vcpu_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, tenant_identifier, None)
# print tenant_vcpu_stats
#
# print "Show memory.usage statistics for tenant"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T23%3A00"
# meter_type = "memory.usage"
# tenant_identifier = "b89f25e0ac2147fba74a3db2acebcaa1"
# tenant_memory_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, tenant_identifier, None)
# print tenant_memory_stats
#
# print "Show disk.root.size statistics for tenant"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T23%3A00"
# meter_type = "disk.root.size"
# tenant_identifier = "10796d79f7124e0f8c9505b64bd8819d"
# tenant_disk_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, tenant_identifier, None)
# print tenant_disk_stats
#
# print "Show VCPU statistics for resource in a tenant"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T23%3A00"
# meter_type = "vcpus"
# tenant_identifier = "10796d79f7124e0f8c9505b64bd8819d"
# resource_identifier = "9d60427f-2602-4582-9bd6-18b9757f976f"
# tenant_vcpu_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, tenant_identifier, resource_identifier)
# print tenant_vcpu_stats
#
# print "Show memory.usage statistics for resource in a tenant"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T23%3A00"
# meter_type = "memory.usage"
# tenant_identifier = "b89f25e0ac2147fba74a3db2acebcaa1"
# resource_identifier = "37128ad6-daaa-4d22-9509-b7e1c6b08697"
# tenant_memory_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, tenant_identifier, resource_identifier)
# print tenant_memory_stats
#
# print "Show disk.root.size statistics for resource in a tenant"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# start_time = "2015-05-05T13%3A00"
# end_time = "2015-05-07T23%3A00"
# meter_type = "disk.root.size"
# tenant_identifier = "10796d79f7124e0f8c9505b64bd8819d"
# resource_identifier = "9d60427f-2602-4582-9bd6-18b9757f976f"
# tenant_disk_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, tenant_identifier, resource_identifier)
# print tenant_disk_stats
