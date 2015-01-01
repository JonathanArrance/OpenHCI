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


project_dict = {'project_name':"jontest2",
             'user_dict': {'username': "jontest2",
                           'password': "jontest2",
                           'user_role': "pu",
                           'email': "jontest2@transcirrus.com",
                           'project_id': None},
             'net_name': "jontest2",
             'subnet_dns': ['8.8.8.8','192.168.168.79'],
             'sec_group_dict': {'group_name': "jontest2",
                                'group_desc': "jontest2",
                                'project_id': None},
             'sec_keys_name': "jontest2",
             'router_name': "jontest2",
             'advanced_ops': {'quota': None
                              }
             }

quota = {
                        'cores':'20',
                        'fixed_ips':'9',
                        'floating_ips':None,
                        'injected_file_content_bytes':None,
                        'injected_file_path_bytes':None,
                        'injected_files':None,
                        'instances':'15',
                        'key_pairs':'10',
                        'metadata_items':'8',
                        'ram':'70000',
                        'security_group_rules':None,
                        'security_groups':None,
                        'storage':'5000',
                        'snapshots':'5',
                        'volumes':'5'
                }

project_dict['advanced_ops']['quota'] = quota
#print "\n\n this is the unit test file %s"%project_dict

print "Building project..."
bcp.build_project(d, project_dict)
