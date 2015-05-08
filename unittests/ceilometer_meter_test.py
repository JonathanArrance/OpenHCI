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

# print "Listing meters"
# project_id = "10796d79f7124e0f8c9505b64bd8819d"
# lm = mo.list_meters(project_id)
# print lm

print "Show CPU percentage statistics"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00%3A00"
end_time = "2015-05-07T20%3A00%3A00"
meter_type = "compute.node.cpu.percent"
cpustats = mo.show_statistics(project_id, start_time, end_time, meter_type)
print cpustats

print "Show disk root usage statistics"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00%3A00"
end_time = "2015-05-07T14%3A00%3A00"
meter_type = "disk.root.size"
diskrootstats = mo.show_statistics(project_id, start_time, end_time, meter_type)
print diskrootstats

print "Show memory usage statistics"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00%3A00"
end_time = "2015-05-07T14%3A00%3A00"
meter_type = "memory.usage"
memoryusagestats = mo.show_statistics(project_id, start_time, end_time, meter_type)
print memoryusagestats

print "Show VCPU statistics"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00%3A00"
end_time = "2015-05-07T14%3A00%3A00"
meter_type = "vcpus"
vcpustats = mo.show_statistics(project_id, start_time, end_time, meter_type)
print vcpustats

print "Show VCPU statistics for resource"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-05T13%3A00%3A00"
end_time = "2015-05-07T23%3A00"
meter_type = "memory"
resource_identifier = "9d60427f-2602-4582-9bd6-18b9757f976f"
resourcevcpustats = mo.show_statistics_for_meter_and_resource(project_id, start_time, end_time, meter_type, resource_identifier)
print resourcevcpustats