#!/bin/python2.7

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.component.nova.admin_actions import server_admin_actions
from transcirrus.component.nova.server import server_ops
from transcirrus.component.nova.storage import server_storage_ops

def server_vol_ops(auth_dict,input_dict):
    print input_dict
    """
    DESC: Used to mount and unmount a volume to a server.
    INPUT: auth_dict - authentication dictionary
           input_dict - instance_id - REQ
                      - project_id - REQ
                      - volume_id - REQ
                      - action mount/unmount
                      - mount_point - ex. /dev/vdc
    OUTPUT: OK - success
    ACCESS: Admins - attach/detach vol to any instance
            PU - attach/detach vol to any instnance in their project.
            User - attach/detach vol to any instance they own.
    NOTE:
    """
    action_raw = input_dict['action']
    action = action_raw.lower()
    action_flag = None
    if(action == 'mount'):
        action_flag = 'mount'
    elif(action == 'unmount'):
        action_flag = 'unmount'
    else:
        logger.sys_error('Invalid volume operation specified, must specify mount or unmount.')
        raise Exception('Invalid volume operation specified, must specify mount or unmount.')

    #get the stats of the server.
    so = server_ops(auth_dict)
    sso = server_storage_ops(auth_dict)

    stat_input = {'server_id':input_dict['instance_id'],'project_id':input_dict['project_id']}
    stats = so.get_server(stat_input)

    mount = None
    if(stats['server_status'] == 'ACTIVE'):
        if(action_flag == 'mount'):
            mount = sso.attach_vol_to_server(input_dict)
        elif(action_flag == 'unmount'):
            mount = sso.detach_vol_from_server(input_dict)
    else:
        logger.sys_error('Can not perform the volume %s operation on volume %s'%(action,input_dict['volume_id']))
        raise Exception('Can not perform the volume %s operation on volume %s'%(action,input_dict['volume_id']))

    return mount