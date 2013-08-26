#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys

sys.path.append('../common')
import logger
import config

sys.path.append('../database')
from postgres import pgsql

from auth import authorization

print "Instantiateing authorization object"
#a = authorization("jon2","test")

print "Get the authorization dictionary for user."
#get the user dict
#d = a.get_auth()
#print d

print "Instantiating authorization object for an default admin"
c = authorization("admin","builder")

print "Get admin authorization dictionary"
b = c.get_auth()
print b

#print "Instantiating authorization object for an admin"
#e = authorization("jonadmin","test")

#print "Get admin authorization dictionary"
#f = e.get_auth()
#print f
