#!/usr/bin/python2.7
import sys
import json
import time
import random

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.component.cinder.error as ec
from transcirrus.component.cinder.cinder_volume import volume_ops
from transcirrus.component.cinder.cinder_snapshot import snapshot_ops
from transcirrus.component.nova.storage import server_storage_ops

def revert_vol_snap(input_dict,auth_dict):
    """
    DESC: Revert to an earlier volume state from a snapshot.
    INPUTS: input_dict - snapshot_id - snapshot to revert from- REQ
                       - volume_id - volume you want to revert - REQ
                       - project_id - the project you are working in - REQ
                       - volume_name - the name of the new volume reverted from snapshot- OP
    OUTPUTS: OK - SUCCESS
             else ERROR
    ACCESS: Admins can create a volume in any project, Users can only create
            volumes in their primary projects
    NOTE: You can not create two volumes with the same name in the same project.
    """
    logger.sys_info('\n**Revet to vol snapshot. Component: Operations: revert_vol_snap**\n')
    vol = volume_ops(auth_dict)
    snap = snapshot_ops(auth_dict)
    sso = server_storage_ops(auth_dict)
    rannum = random.randrange(1000,9000)

    #this not only create a new volume, but it also detaches the original volume and reattaches the snapshot vol at the same mont point
    #get all of the volume info
    get_vol = {'volume_id':input_dict['volume_id'],'project_id':input_dict['project_id']}
    vol_info = vol.get_volume_info(get_vol)

    #get all of the snapshot info
    snap_info = snap.get_snapshot(input_dict['snapshot_id'])

    #make sure the snapshot and the volume are in the same project
    if(snap_info['project_id'] != input_dict['project_id']):
        logger.sys_error('The snapshot and the project are not in the same project.')
        raise Exception('The snapshot and the project are not in the same project.')

    #make sure the snapshot is related to the volume
    if(snap_info['volume_id'] != vol_info['volume_id']):
        logger.sys_error('The snapshot and the original volume are not related.')
        raise Exception('The snapshot and the original volume are not related.')

    #1. create a new volume from snapshot
    if(('volume_name' not in input_dict) or (input_dict['volume_name'] == 'none')):
        input_dict['volume_name'] = 'revert_vol_from_snap_'+input_dict['snapshot_id']+'_%s'%(str(rannum))

    logger.sys_info('Creating a new volume from snapshot %s'%(input_dict['snapshot_id']))
    create_from_snap = {'volume_name':input_dict['volume_name'],'volume_size':vol_info['volume_size'],'project_id':input_dict['project_id'],'snapshot_id':input_dict['snapshot_id']}
    create_vol = vol.create_vol_from_snapshot(create_from_snap)

    #2. Detach the old volume if needed
    attach_dict = {}
    if(vol_info['volume_attached'] == 'true'):
        logger.sys_info('Detaching the volume %s from the instance.'%(vol_info['volume_id']))
        detach_dict = {'project_id':input_dict['project_id'],'volume_id':vol_info['volume_id'],'instance_id':vol_info['volume_instance']}
        detach = sso.detach_vol_from_server(detach_dict)
        time.sleep(5)
        logger.sys_info('Attaching the volume %s to the instance.'%(vol_info['volume_id']))
        attach_dict = {'project_id':input_dict['project_id'],'volume_id':create_vol['volume_id'],'instance_id':vol_info['volume_instance'],'mount_point':vol_info['volume_mount_location']}
        attach = sso.attach_vol_to_server(attach_dict)

    r_dict = {'volume_info':create_vol,'attach_info':attach_dict}
    return r_dict
