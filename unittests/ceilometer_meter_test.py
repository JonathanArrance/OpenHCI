#!/usr/bin/python

import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
from transcirrus.component.ceilometer.ceilometer_meters import meter_ops

print "Instantiating authorization object for an default admin"
c = authorization("admin","password")

print "Get admin authorization dictionary"
b = c.get_auth()
print b

print "Instantiating meters object"
mo = meter_ops(b)
print mo

print "Listing meters"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
lm = mo.list_meters(project_id)
print lm

print "Show CPU percentage statistics"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T20%3A00"
meter_type = "compute.node.cpu.percent"
cpu_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, None)
print cpu_stats

print "Show disk root usage statistics"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T14%3A00"
meter_type = "disk.root.size"
disk_root_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, None)
print disk_root_stats

print "Show memory usage statistics"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T14%3A00"
meter_type = "memory.usage"
memory_usage_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, None)
print memory_usage_stats

print "Show VCPU statistics"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T14%3A00"
meter_type = "vcpus"
vcpu_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, None)
print vcpu_stats

print "Show VCPU statistics for resource"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T23%3A00"
meter_type = "vcpus"
resource_identifier = "9d60427f-2602-4582-9bd6-18b9757f976f"
resource_vcpu_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, resource_identifier)
print resource_vcpu_stats

print "Show memory.usage statistics for resource"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T23%3A00"
meter_type = "memory.usage"
resource_identifier = "37128ad6-daaa-4d22-9509-b7e1c6b08697"
resource_memory_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, resource_identifier)
print resource_memory_stats

print "Show disk.root.size statistics for resource"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T23%3A00"
meter_type = "disk.root.size"
resource_identifier = "9d60427f-2602-4582-9bd6-18b9757f976f"
resource_disk_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, None, resource_identifier)
print resource_disk_stats

print "Show VCPU statistics for tenant"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T23%3A00"
meter_type = "vcpus"
tenant_identifier = "10796d79f7124e0f8c9505b64bd8819d"
tenant_vcpu_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, tenant_identifier, None)
print tenant_vcpu_stats

print "Show memory.usage statistics for tenant"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T23%3A00"
meter_type = "memory.usage"
tenant_identifier = "b89f25e0ac2147fba74a3db2acebcaa1"
tenant_memory_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, tenant_identifier, None)
print tenant_memory_stats

print "Show disk.root.size statistics for tenant"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T23%3A00"
meter_type = "disk.root.size"
tenant_identifier = "10796d79f7124e0f8c9505b64bd8819d"
tenant_disk_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, tenant_identifier, None)
print tenant_disk_stats

print "Show VCPU statistics for resource in a tenant"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T23%3A00"
meter_type = "vcpus"
tenant_identifier = "10796d79f7124e0f8c9505b64bd8819d"
resource_identifier = "9d60427f-2602-4582-9bd6-18b9757f976f"
tenant_vcpu_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, tenant_identifier, resource_identifier)
print tenant_vcpu_stats

print "Show memory.usage statistics for resource in a tenant"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T23%3A00"
meter_type = "memory.usage"
tenant_identifier = "b89f25e0ac2147fba74a3db2acebcaa1"
resource_identifier = "37128ad6-daaa-4d22-9509-b7e1c6b08697"
tenant_memory_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, tenant_identifier, resource_identifier)
print tenant_memory_stats

print "Show disk.root.size statistics for resource in a tenant"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00"
end_time = "2015-05-07T23%3A00"
meter_type = "disk.root.size"
tenant_identifier = "10796d79f7124e0f8c9505b64bd8819d"
resource_identifier = "9d60427f-2602-4582-9bd6-18b9757f976f"
tenant_disk_stats = mo.show_statistics(project_id, start_time, end_time, meter_type, tenant_identifier, resource_identifier)
print tenant_disk_stats