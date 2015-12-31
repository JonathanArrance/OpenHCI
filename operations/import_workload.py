#!/usr/local/bin/python2.7
import subprocess
import os

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.import_util import import_ops
from transcirrus.component.glance.glance_ops_v2 import glance_ops

def import_vmware(auth_dict,input_dict):
    """
    DESC: Extract and import ovf virtual disks. Then attempt to rebuild the virtual machine.
    INPUT: input_dict - package_name - REQ
                      - path - REQ
    OUTPUT: array of r_dict - disk_type
                            - disk
                            - path
                            - order
    ACCESS: Admins - can extract in any project
            PU - can extract only in their project
            User - can extract only in their project
    NOTE:
    """
    io = import_ops(auth_dict)
    glance = glance_ops(auth_dict)

    image_name = input_dict['package_name'].split('.')

    #extract the ovf/ova package
    extract = io.extract_package({'package_name':input_dict['package_name'],'path':input_dict['path']})

    #convert the disk(s)
    convert = io.convert_vdisk(extract)

    #import each one of the disk images to glance.
    #for x in convert:
    #    glance_import = {'image_name':image_name[0],'container_format':image_name[1],'disk_format':'qcow2','image_type':'image_file','visibility':'private','image_location':''}
    #    import_image = glance.import_image(glance_import)

    #recreate the data disk(s) images to cinder volumes and keep the order
    #for disk in extract:
    #    if(disk)

    #connect the data(s) to the instance
    

