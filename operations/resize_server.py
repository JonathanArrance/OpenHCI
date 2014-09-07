#!/usr/bin/python

import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.component.nova.server_action import server_actions
from transcirrus.component.nova.server import server_ops

def resize_and_confirm(auth_dict,server_dict):
    """
    DESC: The operations file definition will allow the resize and confirmation of the
          resize, of the instance in the OpenStack cloud.
    INPUT: auth_dict - authentication dictionary
           server_dict - server_id
                       - project_id
                       - flavor_id
    OUTPUT: OK - success
    ACCESS: Only admins and power users can resize a server.
    NOTE:None
    """
    action = server_actions(auth_dict)
    server = server_ops(auth_dict)

    #resize the server
    resize = action.resize_server(server_dict)
    if(resize == 'ERROR'):
        logger.sys_error('The instance %s was not resized to flavor %s'%(server_dict['server_id'],server_dict[' flavor_id']))
        raise Exception('The instance %s was not resized to flavor %s'%(server_dict['server_id'],server_dict[' flavor_id']))

    #get the server status
    status = server.get_server(server_dict)
    while(status['server_status'] == 'RESIZE'):
        logger.sys_info("Server is resizeing.")
        time.sleep(20)
        status = server.get_server(server_dict)
        logger.sys_info("Server status is %s."%(status['server_status']))

    logger.sys_info('Sleeping for 60 seconds while instance %s stabilizes.'%(server_dict['server_id']))
    time.sleep(60)

    #we need to confirm the resize of the server
    confirm = action.confirm_resize(server_dict)
    if(confirm != 'OK'):
        logger.sys_error('Could not confirm the instance resize.')
        raise Exception('Could not confirm the instance resize.')

    return 'OK'