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

proj_dict = {'proj_name':"test_proj", 
             'user_dict': {'username': "powuser", 
                           'password': "powuser", 
                           'userrole': "pu", 
                           'email': "power@transcirrus.com",
                           'project_id': None},
             'net_name': "netname",
             'subnet_dns': [],
             'sec_group_dict': {'group_name': "groupname",
                                'group_desc': "groupdesc",
                                'project_id': None},
             'sec_keys_name': "seckeys",
             'router_name': "routername"}

print "Building project..."
print bcp
bcp.build_complete_project(a, proj_dict)