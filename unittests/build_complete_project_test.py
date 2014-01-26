import sys
import time
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
from transcirrus.operations.build_complete_project import build_complete_project

print "Authenticating..."
a = authorization("admin","password")

#get the user dict
d = a.get_auth()
print d

proj_dict = {'proj_name':"test_proj", 
             'user_dict': {'username': "powuser", 
                           'password': "powuser", 
                           'userrole': "pu", 
                           'email': "power@transcirrus.com",
                           'project_id': NULL},
             'net_name': "netname",
             'subnet_dns': [],
             'sec_group_dict': {'group_name': "groupname",
                                'group_desc': "groupdesc",
                                'project_id': NULL},
             'sec_keys_name': "seckeys",
             'router_name': "routername"}

print "Building project..."
build_complete_project(a, proj_dict)