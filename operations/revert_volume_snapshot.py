#!/usr/bin/python2.7
import sys
import json
import time

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
    INPUTS: input_dict - snapshot_id - REQ
                       - volume_id - REQ
                       - project_id - REQ
                       - volume_name - OP
    OUTPUTS: OK - SUCCESS
             else ERROR
    ACCESS: Admins can create a volume in any project, Users can only create
            volumes in their primary projects
    NOTE: You can not create two volumes with the same name in the same project.
    """
    vol = volume_ops(auth_dict)
    snap = snapshot_ops(auth_dict)
    sso = server_storage_ops(auth_dict)

    #this not only create a new volume, but it also detaches the origainal volume and reattaches the snapshot vol at the same mont point
    #get all of the volume info
    get_vol = {'volume_id':input_dict['volume_id'],'project_id':input_dict['project_id']}
    vol_info = vol.get_volume(get_vol)

    #get all of the snapshot info
    snap_info = snap.get_snapshot(input_dict['snapshot_id'])

    #make sure the snapshot and the volume are in the same project
    if(snap_info['project_id'] != input_dict['project_id']):
        logger.sys_error('The snapshot and the project are not in the same project.')
        raise Excepton('The snapshot and the project are not in the same project.')

    #make sure the snapshot is related to the volume
    if(snap_info['volume_id'] != vol_info['volume_id']):
        logger.sys_error('The snapshot and the original volume are not related.')
        raise Excepton('The snapshot and the original volume are not related.')

    #1. create a new volume from snapshot
    if(('volume_name' not in input_dict) or (input_dict['volume_name'] == '')):
        input_dict['volume_name'] = input_dict['snapshot_id'] + '_vol_from_snap_%s'%(str(self.rannum))

    create_from_snap = {'volume_name':input_dict['volume_name'],'volume_size':vol_info['volume_size'],'project_id':input_dict['project_id'],'snapshot_id':create_snap['snapshot_id']}
    create_vol = vol.create_vol_from_snapshot(create_from_snap)

    #2. Detach the old volume if needed
    if(vol_info['volume_attached'] == 'true'):
        detach_dict = {'project_id':input_dict['project_id'],'volume_id':vol_info['volume_id'],'instance_id':vol_info['volume_instance']}
        detach = sso.detach_vol_from_server(detach_dict)
        attach_dict = {'project_id':input_dict['project_id'],'volume_id':vol_info['volume_id'],'instance_id':vol_info['volume_instance'],'mount_point':vol_info['volume_mount_location']}
        attach = sso.attach_vol_to_server(attach_dict)

    return 'OK'
