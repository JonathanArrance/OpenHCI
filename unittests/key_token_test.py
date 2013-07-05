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

a = authorization("testuser2","test")

#get the user dict
d = a.get_auth()

#d is the user_dictionary

tokenops = token_ops(d)

t = tokenops.check_token()