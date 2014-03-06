import sys
import time
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
import transcirrus.operations.destroy_project as destroy

print "Authenticating..."
a = authorization("admin","password")

#get the user dict
d = a.get_auth()
print d

proj_dict = {'project_name': "7", 'project_id':'b0bd412534df4ca6aeba933188d800ee' , 'keep_users': 0}
#project_id = raw_input('project_id: ')
#proj_dict['project_id'] = project_id

print "Destroying project..."
dst_proj = destroy.destroy_project(d, proj_dict)
print dst_proj
