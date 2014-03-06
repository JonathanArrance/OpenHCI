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

project_dict = {'project_name':"7", 
             'user_dict': {'username': "7", 
                           'password': "7", 
                           'user_role': "pu", 
                           'email': "7@transcirrus.com",
                           'project_id': None},
             'net_name': "7",
             'subnet_dns': [],
             'sec_group_dict': {'group_name': "7",
                                'group_desc': "7",
                                'project_id': None},
             'sec_keys_name': "7",
             'router_name': "7"}

print "Building project..."
bcp.build_project(d, project_dict)
