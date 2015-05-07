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

print "Show CPU percentage statistics for a given time frame"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-07T13%3A00%3A00"
end_time = "2015-05-07T14%3A00%3A00"
cpustats = mo.show_cpu_percentage_statistics(project_id, start_time, end_time)
print cpustats

print "Show disk root usage statistics for a given time frame"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-07T13%3A00%3A00"
end_time = "2015-05-07T14%3A00%3A00"
diskrootstats = mo.show_disk_root_usage_statistics(project_id, start_time, end_time)
print diskrootstats

print "Show disk root usage statistics for a given time frame"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-07T13%3A00%3A00"
end_time = "2015-05-07T14%3A00%3A00"
memoryusagestats = mo.show_memory_usage_statistics(project_id, start_time, end_time)
print memoryusagestats

print "Show VCPU statistics for a given time frame"
project_id = "10796d79f7124e0f8c9505b64bd8819d"
start_time = "2015-05-07T13%3A00%3A00"
end_time = "2015-05-07T14%3A00%3A00"
vcpustats = mo.show_vcpu_statistics(project_id, start_time, end_time)
print vcpustats