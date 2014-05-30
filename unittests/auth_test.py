#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

#from auth import authorization
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_users import user_ops


"""
print "Instantiateing authorization object"
a = authorization("admin","builder")
#print "Get the authorization dictionary for user."
#get the user dict
d = a.get_auth()
print d

print "---------------------------------------------"
time.sleep(1)
print "changeing test user password."
new = user_ops(d)
change = new.update_user_password('jontest')
print change
"""

print "Instantiating authorization object for an default admin"
c= authorization("dude","password")

print "Get admin authorization dictionary"
b = c.get_auth()
print b

#print "Instantiating authorization object for an admin"
#e = authorization("jonadmin","test")

#print "Get admin authorization dictionary"
#f = e.get_auth()
#print f
