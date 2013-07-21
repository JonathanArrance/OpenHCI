#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys

sys.path.append('../common')
import logger
import config
from auth import authorization

sys.path.append('/home/jonathan/alpo.0/component/keystone')
from keystone_tokens import token_ops

print "Authenticate as the default admin."
a = authorization("admin","builder")
#get the user dict
d = a.get_auth()

print "Instantiate a new token_ops object"
tokenops = token_ops(d)

print "checking token for validity"
t = tokenops.check_token()