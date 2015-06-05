import os
import time
import transcirrus.common.logger as logger
from transcirrus.component.nova.server import server_ops
from transcirrus.component.ceilometer.ceilometer_mem_usage_patch import MemoryUtilization

def daemonize(auth_dict, daemon_status, query_interval=None):
    if query_interval is None:
        query_interval = 10
    while daemon_status:
        time.sleep(query_interval)
        get_mem_usage_for_instances(auth_dict)

def get_mem_usage_for_instances(auth_dict):
    """
    DESC:   This operation will enable a service that monitors memory usage across
            all active instance within our cloud environment.
            Once the usage is obtain it is then reported to ceilometer for record keeping.
    INPUT:  auth_dict
    OUTPUT: NONE
    ACCESS: Admins Only
    NOTES:
    """

    so = server_ops(auth_dict)
    instance_list = so.list_all_servers()

    for i, entry in enumerate(instance_list):
        if entry['status'] == 'ACTIVE':
            child_pid = os.fork()
            if child_pid == 0:
                try:
                    mu = MemoryUtilization(auth_dict)
                    mu.manual_inspect_memory_usage(entry['os_ext_inst_name'], entry['project_id'], entry['server_id'])
                    print entry['os_ext_inst_name'] + " || " + entry['project_id'] + " || " + entry['server_id']
                except Exception as e:
                    print ('Connection to mem patch failed: %s' % e)
                    logger.sys_error('Connection to mem patch failed: %s' % e)
                    raise Exception('Connection to mem patch failed: %s' % e)
                finally:
                    os._exit(0)