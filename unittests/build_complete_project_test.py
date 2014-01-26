import sys
import time
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
import transcirrus.operations.build_complete_project as bcp

print "Authenticating..."
a = authorization("admin","newpass")

#get the user dict
d = a.get_auth()
print d

proj_dict = {'proj_name':"11", 
             'user_dict': {'username': "11", 
                           'password': "11", 
                           'userrole': "pu", 
                           'email': "power@transcirrus.com",
                           'project_id': None},
             'net_name': "netname",
             'subnet_dns': [],
             'sec_group_dict': {'group_name': "11",
                                'group_desc': "11",
                                'project_id': None},
             'sec_keys_name': "11",
             'router_name': "11"}

print "Building project..."
print bcp
bcp.build_project(d, proj_dict)