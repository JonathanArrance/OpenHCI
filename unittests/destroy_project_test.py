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

proj_dict = {'project_name': "jontest3", 'project_id':'7371f871fe404dd4b17ce42d2746e0c9' , 'keep_users': 0}
#project_id = raw_input('project_id: ')
#proj_dict['project_id'] = project_id

print "Destroying project..."
dst_proj = destroy.destroy_project(d, proj_dict)
print dst_proj
