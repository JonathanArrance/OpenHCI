import os
import transcirrus.common.logger as logger
from transcirrus.component.nova.server import server_ops

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
                    print entry['server_id']
                finally:
                    os.exit(0)