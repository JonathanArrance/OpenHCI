import os
import time
import transcirrus.common.logger as logger
from transcirrus.component.nova.server import server_ops
from transcirrus.component.ceilometer.ceilometer_third_party_meters import ThirdPartyMeters
from transcirrus.common import extras as extras
from transcirrus.common.auth import authorization

def daemonize(daemon_status, query_interval=None):
    if query_interval is None:
        query_interval = 600
    while daemon_status:
        # factory_creds = '/home/transuser/factory_creds'
        # with open(factory_creds) as f:
        #     content = [x.strip('export ').strip('\n') for x in f.readlines()]
        #
        # factory_creds_dict = dict(item.split("=") for item in content)
        # c = authorization(factory_creds_dict['OS_USERNAME'], factory_creds_dict['OS_PASSWORD'])
        # auth_dict = c.get_auth()
        auth_dict = extras.shadow_auth()
        get_mem_usage_for_instances(auth_dict)
        get_disk_info_for_instances(auth_dict)
        get_memory_resident_for_instances(auth_dict)
        time.sleep(query_interval)


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
                    mu = ThirdPartyMeters(auth_dict)
                    mu.manual_inspect_memory_usage(entry['os_ext_inst_name'], entry['project_id'], entry['server_id'])
                    # print entry['os_ext_inst_name'] + " || " + entry['project_id'] + " || " + entry['server_id']
                except Exception as e:
                    print ('Connection to mem patch failed: %s' % e)
                    logger.sys_error('Connection to mem patch failed: %s' % e)
                    raise Exception('Connection to mem patch failed: %s' % e)
                finally:
                    os._exit(0)

def get_disk_info_for_instances(auth_dict):
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
                    mu = ThirdPartyMeters(auth_dict)
                    mu.manual_inspect_disk_info(entry['os_ext_inst_name'], entry['project_id'], entry['server_id'])
                    # print entry['os_ext_inst_name'] + " || " + entry['project_id'] + " || " + entry['server_id']
                except Exception as e:
                    print ('Connection to mem patch failed: %s' % e)
                    logger.sys_error('Connection to mem patch failed: %s' % e)
                    raise Exception('Connection to mem patch failed: %s' % e)
                finally:
                    os._exit(0)

def get_memory_resident_for_instances(auth_dict):
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
                    mu = ThirdPartyMeters(auth_dict)
                    mu.manual_inspect_memory_resident(entry['os_ext_inst_name'], entry['project_id'], entry['server_id'])
                    # print entry['os_ext_inst_name'] + " || " + entry['project_id'] + " || " + entry['server_id']
                except Exception as e:
                    print ('Connection to mem patch failed: %s' % e)
                    logger.sys_error('Connection to mem patch failed: %s' % e)
                    raise Exception('Connection to mem patch failed: %s' % e)
                finally:
                    os._exit(0)