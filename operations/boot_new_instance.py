#!/usr/bin/python2.7
import sys
import json

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.component.nova.error as ec
from transcirrus.component.nova.server import server_ops
from transcirrus.component.cinder.cinder_volume import volume_ops
from transcirrus.component.glance.glance_ops_v2 import glance_ops
from transcirrus.component.nova.flavor import flavor_ops
from transcirrus.component.nova.quota import quota_ops

def boot_instance(input_dict,auth_dict):
    """
    DESC: Boot an instance directly from a volume.
    INPUTS: input_dict - project_id - REQ
                       - instance_name - REQ
                       - sec_group_name - REQ
                       - sec_key_name - REQ
                       - image_id - REQ
                       - flavor_id - REQ
                       - boot_from_vol - OP(True/False) - default False
                       - volume_size - OP
                       - volume_name - OP
                       - volume_type - OP
                       - avail_zone - default availability zone - nova
                       - network_name - default project net used if none specified
            auth_dict - authentication
    OUTPUTS: r_dict instance - vm_name - vm name
                            - vm_id - vm id
                            - sec_key_name - security key name
                            - sec_group_name - security group name
                            - created_by - name of creater
                            - project_id - id of project
                    volume - volume_name
                           - volume_type
    ACCESS: All users can boot from a volume.
    NOTE: If boot_from_vol is set to True, and the volume type is not specified then the instance
          will boot from TransCirrus spindle disks.
    """
    logger.sys_info('\n**Boot a new instance. Component: Operations: boot_from_vol**\n')
    volume = volume_ops(auth_dict)
    instance = server_ops(auth_dict)
    glance = glance_ops(auth_dict)
    quota = quota_ops(auth_dict)
    flavor = flavor_ops(auth_dict)
    db = util.db_connect()

    if(('flavor_id' not in input_dict) or ('instance_name' not in input_dict) or
        ('image_id' not in input_dict) or ('project_id' not in input_dict) or
        ('sec_group_name' not in input_dict) or ('sec_key_name' not in input_dict)):
            logger.sys_error("Required value not passed to create_server operation")
            raise Exception("Required value not passed to create_server operation")

    #check the quota
    quotas = quota.get_project_quotas(input_dict['project_id'])
    #see how many vms in project
    try:
        instances = {'table':'trans_instances','where':"proj_id='%s'"%(input_dict['project_id'])}
        num_instances = db.count_elements(instances)
    except:
        raise Exception('Could not get instance count for project %s'%(input_dict['project_id']))

    if(int(num_instances) >= int(quotas['instances'])):
        raise Exception('Could not create Instance, quota Exceded.')

    flavor_details = flavor.get_flavor(input_dict['flavor_id'])
    if('flavor_name' not in flavor_details):
        logger.sys_error('The flavor %s could not be found.'%(input_dict['flavor_id']))
        raise Exception('The flavor %s could not be found.'%(input_dict['flavor_id']))

    image_details = glance.get_image(input_dict['image_id'])
    if('image_name' not in image_details):
        logger.sys_error('The flavor %s could not be found.'%(input_dict['image_id']))
        raise Exception('The flavor %s could not be found.'%(input_dict['image_id']))

    if('avail_zone' not in input_dict):
        input_dict['avail_zone'] = 'nova'

    #This is not getting caught for some reason
    if(input_dict['avail_zone'] is None):
        input_dict['avail_zone'] = 'nova'

    if('boot_from_vol' not in input_dict):
        input_dict['boot_from_vol'] == 'False'

    #initialize create_vol
    create_vol = {}

    if(input_dict['boot_from_vol'] == 'True'):
        if('volume_type' in input_dict):
            logger.sys_info('Booting the new instance from an %s volume'%(input_dict['volume_type']))
        else:
            input_dict['volume_type'] = 'spindle'

        if('volume_size' in input_dict):
            logger.sys_info("Setting user select volume size to boot instace from.")
        else:
            input_dict['volume_size'] = flavor_details['disk_space(GB)'] + flavor_details['swap(GB)']
            logger.sys_info("Creating a volume of %s to boot instance from"%(input_dict['volume_size']))

        if('volume_name' not in input_dict):
            input_dict['volume_name'] = "%s_%s"%(input_dict['instance_name'],image_details['image_name'])

        #create a bootable volume
        #cinder --debug create --image-id 32778bb7-e6ab-4568-a110-8e7573df0f3b --volume-type spindle --display-name my-boot-vol 8
        logger.sys_info("Building boot volume for instance %s"%(input_dict['instance_name']))
        create = {'volume_size':input_dict['volume_size'],'project_id':input_dict['project_id'],
                  'volume_type':input_dict['volume_type'],'image_id':input_dict['image_id'],
                  'volume_name':input_dict['volume_name'],'volume_zone':input_dict['avail_zone']}
        create_vol = volume.create_bootable_volume(create)
        logger.sys_info("Building an instance to boot from volume %s"%(create_vol['volume_id']))

    #create the instance
    #nova boot --flavor 2 --image 32778bb7-e6ab-4568-a110-8e7573df0f3b --block_device_mapping vda=7315eb50-da9f-4e21-a308-10b6b921ae91:::0 myInstanceFromVolume
    instance_vars = {'project_id': input_dict['project_id'], 'sec_group_name': input_dict['sec_group_name'],
                'sec_key_name': input_dict['sec_key_name'], 'avail_zone': input_dict['avail_zone'], 
                'network_name':input_dict['network_name'],'image_id':input_dict['image_id'],'image_name':image_details['image_name'],
                'flavor_id':input_dict['flavor_id'],'flavor_name':flavor_details['flavor_name'],'instance_name':input_dict['instance_name'],
                'volume_id':create_vol['volume_id']}
    create_instance = instance.create_server(instance_vars)
    #set volume to attached for boot vol
    if('volume_id' in create_vol):
        up_dict = {'table':"trans_system_vols",'set':"vol_set_bootable=true,vol_attached=true,vol_attached_to_inst='%s',vol_mount_location='/dev/vda',vol_type='%s'"%(create_instance['vm_id'],input_dict['volume_type']),
                   'where':"vol_id='%s'"%(create_vol['volume_id'])}
        db.pg_update(up_dict)

    r_dict = {'instance':create_instance,'volume':create_vol}

    return r_dict

