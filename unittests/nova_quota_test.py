#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import time


import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization

from transcirrus.component.nova.quota import quota_ops

print "Loggin in as the default admin."
#onlyt an admin can create a new user
a = authorization("admin","password")
#a = authorization("admin","password")
#get the user dict
d = a.get_auth()

#print d

#instantiate a flavor_ops object
quota = quota_ops(d)
#x = quota.get_project_quotas()
#print x

#instantiate a flavor_ops object
#print "project and user given"
#input_dicty = {'user_id':'f7c4bfb8220f469d8112bae4ee8136e1', 'project_id':'54209ef0f7ba4935a2a8984cba4f27f2'}
y = quota.get_project_quotas('13d92fe4b2de4051abc5de0654277af0')
print y

#print "user given"
#input_dictz = {'user_id':'f7c4bfb8220f469d8112bae4ee8136e1'}
#z = quota.show_user_quotas(input_dictz)
#print z

#print "project given"
#input_dicta = {'project_id':'54209ef0f7ba4935a2a8984cba4f27f2'}
#a = quota.show_user_quotas(input_dicta)
#print a

#print "neither given"
#b = quota.show_user_quotas()
#print b

#print "neither given"
#b = quota.get_max_limits("13d92fe4b2de4051abc5de0654277af0")
#print b

#input_dict = {'storage':'3000','instances':'20','cores':'25','snapshots':'30','volumes':'19','key_pairs':None,'ram':'90000','injected_file_content_bytes': None,'user_id':'f7c4bfb8220f469d8112bae4ee8136e1', 'project_id':'8979d99d618045308817dcb2b8be068e'}
#f = quota.update_project_quotas(input_dict)
#print f

#input_dicty = {'user_id':'f7c4bfb8220f469d8112bae4ee8136e1', 'project_id':'8979d99d618045308817dcb2b8be068e'}
#y = quota.get_project_quotas('8979d99d618045308817dcb2b8be068e')
#print y
