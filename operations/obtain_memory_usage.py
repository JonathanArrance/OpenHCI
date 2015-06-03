import os
import transcirrus.common.logger as logger
from transcirrus.component.ceilometer.ceilometer_mem_usage_patch import MemoryUtilization

def query_nova_for_all_active_instances(auth_dict):
    """
    DESC:   This operation will enable a service that monitors memory usage across
            all active instance within our cloud environment.
            Once the usage is obtain it is then reported to ceilometer for record keeping.
    INPUT:  auth_dict
    OUTPUT: Array of Dictionaries with active instances
    ACCESS: Admins Only
    NOTES:
    """
    instance_list = None
    return instance_list

def mock_instance_list():
    instance_list = [{'server_name':'test01','instance_id':'serverid01',
                      'project_id':'projectid01', 'status':'ACTIVE','virsh_id':'virshid01'},
                     {'server_name':'test02','instance_id':'serverid02',
                      'project_id':'projectid02', 'status':'ACTIVE','virsh_id':'virshid02'},
                     {'server_name':'test03','instance_id':'serverid03',
                      'project_id':'projectid03', 'status':'ACTIVE','virsh_id':'virshid03'},
                     {'server_name':'test04','instance_id':'serverid04',
                      'project_id':'projectid04', 'status':'PAUSED','virsh_id':'virshid03'}]
    return instance_list

def get_mem_usage_for_instances(instance_list):

    for i, entry in enumerate(instance_list):
        if entry['status'] == 'ACTIVE':
            child_pid = os.fork()
            if child_pid == 0:
                try:
                    print entry['instance_id']
                    MemoryUtilization.manual_inspect_memory_usage(entry['virsh_id'],
                                                                  entry['project_id'],
                                                                  entry['instance_id'])
                finally:
                    os.exit(0)

