#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

#from auth import authorization
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.import_util import import_ops
from transcirrus.common.auth import authorization

print "Instantiating authorization object for an default admin"
c= authorization("admin","password")


print "Get admin authorization dictionary"
b = c.get_auth()

io = import_ops(b)

disks = io.extract_package({'package_name':'windows.ova','path':'/home/transuser/jon'})
print disks


convert = io.convert_vdisk(disks)

print convert