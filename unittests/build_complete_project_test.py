import sys
import time
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
import transcirrus.operations.build_complete_project as bcp

print "Authenticating..."
a = authorization("admin","password")

#get the user dict
d = a.get_auth()
print d

project_dict = {'project_name':"9", 
             'user_dict': {'username': "9", 
                           'password': "9", 
                           'user_role': "pu", 
                           'email': "9@transcirrus.com",
                           'project_id': None},
             'net_name': "9",
             'subnet_dns': [],
             'sec_group_dict': {'group_name': "9",
                                'group_desc': "9",
                                'project_id': None},
             'sec_keys_name': "9",
             'router_name': "9"}

print "Building project..."
bcp.build_project(d, project_dict)
