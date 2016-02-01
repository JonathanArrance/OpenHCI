#!/usr/bin/python2.7
import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
from transcirrus.component.nova.server import server_ops
from transcirrus.component.cinder.cinder_volume import volume_ops
from transcirrus.component.glance.glance_ops_v2 import glance_ops


def format_volume(input_dict,auth_dict):
    """
    DESC: Format a volume that is attached to an instance.
    INPUTS: input_dict - instance_id - REQ
                       - project_id - REQ -
                       - volume_id - REQ - 
                       - file_system - OP default - EXT3(Linux) NTFS(Windows)
            auth_dict - authentication
    OUTPUTS: 
    ACCESS: All users can boot and install from an iso.
    NOTE: This will only boot up and allow a user to install from an ISO. It will not build the cloud image.
          The create_cloud_image def will build the cloud image. Also the user will need to install any needed
          software to make their instance work.
    """
    #1. validate the input.
    logger.sys_info('\n**Format attach volume operation: def: format_volume**\n')
    for key,value in input_dict.items():
        if(key == 'file_system'):
            continue
        if(key == ''):
            logger.sys_error('Required value not passed.')
            raise Exception('Required value not passed.')
        if(value == ''):
            logger.sys_error('Required value not passed.')
            raise Exception('Required value not passed.')

    volume = volume_ops(auth_dict)
    server = server_ops(auth_dict)
    image = glance_ops(auth_dict)

    #get the volume info
    get_volume = volume.get_volume({'volume_id':input_dict['volume_id'],'project_id':input_dict['project_id']})
    attach_id = server_id = None
    if(get_volume['volume']):
        #2. check if the volume is attached to an instance
        if(len(get_volume['volume']['attachments']) == 0):
            logger.sys_error('The volume %s is not attached to instance %s.'%(input_dict['volume_id'],input_dict['instance_id']))
            raise Exception('The volume %s is not attached to instance %s.'%(input_dict['volume_id'],input_dict['instance_id']))
        else:
            for vol in get_volume['volume']['attachments']:
                if(input_dict['volume_id'] == vol['volume_id']):
                    attach_id = vol['device']
                    server_id = vol['server_id']
        #3. See if the volume attached is a boot volume
        if(get_volume['volume']['bootable'] == 'true'):
            logger.sys_error('The volume %s is bootable.'%(input_dict['volume_id']))
            raise Exception('The volume %s is bootable.'%(input_dict['volume_id']))
    else:
        logger.sys_error('The volume %s is not attached.'%(input_dict['volume_id']))
        raise Exception('The volume %s is not attached.'%(input_dict['volume_id']))

    #4. check if the volume is attached to the instance
    if(server_id == input_dict['instance_id']):
        logger.sys_error('The volume %s is not attached to instance %s.'%(input_dict['volume_id'],input_dict['instance_id']))
        raise Exception('The volume %s is not attached to instance %s.'%(input_dict['volume_id'],input_dict['instance_id']))

    #5. check the instance os_type
    instance_info = server.get_server({'instance_id':input_dict['instance_id'],'project_id':input_dict['project_id']})
    inst_image_info = image.get_image(instance_info['image_id'])

    #6. get the mount location of the volume
    drive_letter = _fix_drive_letter(attach_id)

    #7. get the ssh key
    ssh_key_name = server.get_sec_keys({instance_info['server_key_name']'project_id':input_dict['project_id']})

    #8. connect to the instance from the backend
    if(inst_image_info['os_type'] == 'linux'):
        _linux()
    elif(inst_image_info['os_type'] == 'windows'):
        _windows()

def _linux():
    #opertion needed to format the volume in linux
    pass

def _windows():
    #operation needed to format a volume in windows
    pass

def _fix_drive_letter(drive):
    #this is a hack since openstack returns the drive letter that is one higher.
    # ex /dev/vdc is /dev/vdb in reality
    letter = chr(ord(drive[-1:]) - 1)
    new_drive = '/dev/vd'+letter
    return new_drive