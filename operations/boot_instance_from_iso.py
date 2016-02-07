#!/usr/bin/python2.7
import sys
import json
# need the following packages
# yum install virt-install
# yum install virtio-win
# yum install virt-viewer

# virtio drivers
# /usr/share/virtio-win/virtio-win-0.1.102.iso

# command
# sudo virt-install --connect qemu:///system --name ws2012 --ram 2048 --vcpus 2 --network user,model=virtio --disk path=/tmp/ws2012.qcow2,format=qcow2,device=disk,bus=virtio
# --cdrom /tmp/windows2012.iso --disk path=/usr/share/virtio-win/virtio-win-0.1.102.iso,device=cdrom --vnc --os-type windows --os-variant win2k8

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.component.nova.error as ec
from transcirrus.component.nova.server import server_ops
from transcirrus.component.cinder.cinder_volume import volume_ops
from transcirrus.component.glance.glance_ops_v2 import glance_ops
from transcirrus.component.nova.flavor import flavor_ops
from transcirrus.component.nova.quota import quota_ops

def boot_instance_from_iso(input_dict,auth_dict):
    """
    DESC: Boot an instance and install it from an iso.
    INPUTS: input_dict - project_id - REQ
                       - instance_name - REQ
                       - flavor_id - REQ - ram/disk
                       - network_name - REQ
                       - os_type - REQ - linux/windows
                       - os_variant - REQ
                       - install_iso - REQ
                       - driver_disk - OP
            auth_dict - authentication
    OUTPUTS: r_dict 
    ACCESS: All users can boot and install from an iso.
    NOTE: This will only boot up and allow a user to install from an ISO. It will not build the cloud image.
          The create_cloud_image def will build the cloud image. Also the user will need to install any needed
          software to make their instance work.
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
    
    
    
def create_cloud_image(input_dict,auth_dict):
    """
    DESC: Boot an instance and install it from an iso.
    INPUTS: input_dict - project_id - REQ
                       - instance_name - REQ
                       - flavor_id - REQ - ram/disk
                       - network_name - REQ
                       - os_type - REQ - linux/windows
                       - os_variant - REQ
                       - install_iso - REQ
                       - driver_disk - OP
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