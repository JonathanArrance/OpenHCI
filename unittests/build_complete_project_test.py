import sys
import time
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
import transcirrus.operations.build_complete_project as bcp

print "Authenticating..."
a = authorization("shithead","password")

#get the user dict
d = a.get_auth()
print d

project_dict = {'project_name':"thissucksballs2", 
             'user_dict': {'username': "thissucksballs2", 
                           'password': "thissucksballs2", 
                           'user_role': "pu", 
                           'email': "thissucksballs2@transcirrus.com",
                           'project_id': None},
             'net_name': "thissucksballs2",
             'subnet_dns': [],
             'sec_group_dict': {'group_name': "thissucksballs2",
                                'group_desc': "thissucksballs2",
                                'project_id': None},
             'sec_keys_name': "thissucksballs2",
             'router_name': "thissucksballs2"}

print "Building project..."
bcp.build_project(d, project_dict)
