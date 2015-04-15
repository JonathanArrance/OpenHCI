#!/bin/python2.7

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.component.nova.admin_actions import server_admin_actions
from transcirrus.component.nova.server import server_ops

def evacuation(auth_dict,input_dict):
    """
    DESC: The operations file will allow the admin to evacuate a vm from a dead compute node
    INPUT: auth_dict - authentication dictionary
           input_dict - instance_id - REQ
                      - project_id - REQ
                      - openstack_host_id
    OUTPUT: OK - success
    ACCESS: Only admins can evacuate a server from a failed host.
    NOTE: openstack_host_id is required if the type is set to live
    """

    if(('instance_id' not in input_dict) or (input_dict['instance_id'] == '')):
        logger.sys_error('Reguired value instance_id not passed.')
        raise Exception('Reguired value instance_id not passed.')
    if(('project_id' not in input_dict) or (input_dict['project_id'] == '')):
        logger.sys_error('Reguired value project_id not passed.')
        raise Exception('Reguired value project_id not passed.')

    saa = server_admin_actions(auth_dict)
    sa = server_ops(auth_dict)

    evac = saa.evacuate_server(input_dict)

    status = None
    if(evac == 'OK'):
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