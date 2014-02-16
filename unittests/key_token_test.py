#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_tokens import token_ops

print "Authenticate as the default admin."
a = authorization("admin","newpass")
#get the user dict
d = a.get_auth()

print "Instantiate a new token_ops object"
tokenops = token_ops(d)

print "checking token for validity"
t = tokenops.check_token()