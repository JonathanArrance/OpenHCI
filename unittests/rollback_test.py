#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

#from auth import authorization
import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.operations.rollback_setup as rollback
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_users import user_ops


print "Instantiating authorization object for an default admin"
c= authorization("admin","password")

print "Get admin authorization dictionary"
b = c.get_auth()
print b
rollback.rollback(b)

#print "Instantiating authorization object for an admin"
#e = authorization("jonadmin","test")

#print "Get admin authorization dictionary"
#f = e.get_auth()
#print f
