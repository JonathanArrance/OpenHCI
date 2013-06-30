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

a = authorization("testuser2","test")

#get the user dict
d = a.get_auth()
print d