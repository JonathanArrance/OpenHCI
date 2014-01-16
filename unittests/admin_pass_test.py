#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time

#from auth import authorization
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.change_adminuser_password import change_admin_password
#from celery.result import AsyncResult
#from celery import task
#from celery import Celery

print "Instantiating authorization object for an default admin"
c= authorization("admin","test")

print "Get admin authorization dictionary"
b = c.get_auth()

#change_admin_password.delay()

#print "Waiting for the result"
#while password.ready() == False:
#    print "waiting"

result = change_admin_password(b,"password")
print result

#res = AsyncResult(result.task_id)
#print res.status
