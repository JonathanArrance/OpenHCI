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
import transcirrus.operations.remove_virtual_router as remove_router

print "Instantiating authorization object for an default admin"
c= authorization("admin_keven","password")


print "Get admin authorization dictionary"
b = c.get_auth()
io = import_ops(b)
#disks = io.extract_package({'package_name':'windows-multidisk.ova','path':'/home/transuser/jon'})
#print disks
#convert = io.convert_vdisk(disks)
#print convert
#r = io.get_import_specs('/home/transuser/jon/windows-multidisk.ovf')
#print r


out = remove_router.remove_virt_router(b,{'router_id': '61586d62-c601-40c4-80f8-3924608981f1', 'project_id': '027f32b21dcb4e83bff0b0ebb4bf79a3'})
print out