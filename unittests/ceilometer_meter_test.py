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
lm = mo.list_meters()
print lm