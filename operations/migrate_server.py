#!/bin/python2.7

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.component.nova.admin_actions import server_admin_actions
from transcirrus.component.nova.server import server_ops

def migrate_instance(auth_dict,input_dict):
    """
    DESC: The operations file allows admins to move vms with in the cloud environment.
    INPUT: auth_dict - authentication dictionary
           input_dict - instance_id - REQ
                      - project_id - REQ
                      - migration_type offline/live - REQ
                      - openstack_host_id
    OUTPUT: OK - success
    ACCESS: Only admins and power users can resize a server.
    NOTE: openstack_host_id is required if the type is set to live
    """

    if(auth_dict['is_admin'] == 1):
        if(('instance_id' not in input_dict) or (input_dict['instance_id'] == '')):
            logger.sys_error('Reguired value instance_id not passed.')
            raise Exception('Reguired value instance_id not passed.')
        if(('project_id' not in input_dict) or (input_dict['project_id'] == '')):
            logger.sys_error('Reguired value project_id not passed.')
            raise Exception('Reguired value project_id not passed.')
        if(('migration_type' not in input_dict) or (input_dict['migration_type'] == '')):
            logger.sys_error('Reguired value migration_type not passed.')
            raise Exception('Reguired value migration_type not passed.')
    
        mtype = input_dict['migration_type']
        if(mtype.lower() == 'offline'):
            logger.sys_info('Offline migration selected for %s.'%(input_dict[instance_id]))
        if(mtype.lower() == 'live'):
            logger.sys_info('Live migration selected for %s.'%(input_dict[instance_id]))
            if(('openstack_host_id' not in input_dict) or (input_dict['openstack_host_id'] == '')):
                logger.sys_error('Reguired value openstack_host_id not passed.')
                raise Exception('Reguired value openstack_host_id not passed.')
        else:
            logger.sys_error('Invalid migration migration type.')
            raise Exception('Invalid migration migration type.')
    
        saa = server_admin_actions(auth_dict)
        sa = server_ops(auth_dict)
    
        migrate = None
        if(mtype.lower() == 'live'):
            migrate = saa.live_migrate_server(input_dict)
        elif(mtype.lower() == 'offline'):
            migrate = saa.migrate_server(input_dict)
    
        status = None
        if(migrate == 'OK'):
            while(True):
                status = sa.get_server(server)
                if(status['server_status'] == 'ACTIVE'):
                    logger.sys_info('Active server with ID %s.'%(input_dict['instance_id']))
                    break
                #elif(status['server_status'] == 'MIGRATEING'):
                #    logger.sys_info('Building server with ID %s.'%(input_dict['server_id']))
                #    time.sleep(10)
                elif(status['server_status'] == 'ERROR'):
                    logger.sys_info('Server with ID %s failed to build.'%(input_dict['instance_id']))
                    raise Exception("Could not create a migrate server due to an unknown error. Please contact your TransCirrus support representitive. ERROR: 555")
                else:
                    logger.sys_info('Building server with ID %s.'%(input_dict['instance_id']))
                    time.sleep(10)

        return status