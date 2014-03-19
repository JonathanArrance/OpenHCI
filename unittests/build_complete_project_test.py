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


project_dict = {'project_name':"keven5", 
             'user_dict': {'username': "keven5", 
                           'password': "keven5", 
                           'user_role': "pu", 
                           'email': "keven5@transcirrus.com",
                           'project_id': None},
             'net_name': "keven5",
             'subnet_dns': [],
             'sec_group_dict': {'group_name': "keven5",
                                'group_desc': "keven5",
                                'project_id': None},
             'sec_keys_name': "keven5",
             'router_name': "keven5"}

print "Building project..."
bcp.build_project(d, project_dict)
