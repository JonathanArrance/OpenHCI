#!/usr/local/bin/python2.7
import subprocess
import os
from fnmatch import fnmatch

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.import_util import import_ops
from transcirrus.component.glance.glance_ops_v2 import glance_ops
from transcirrus.component.cinder.cinder_volume import volume_ops

def import_vmware(auth_dict,input_dict):
    """
    DESC: Extract and import ovf virtual disks. Then attempt to rebuild the virtual machine.
    INPUT: input_dict - image_name - REQ
                      - package_name - REQ
                      - path - REQ
                      - os_type - REQ
    OUTPUT: array of r_dict - disk_type
                            - disk
                            - path
                            - order
    ACCESS: Admins - can extract in any project
            PU - can extract only in their project
            User - can extract only in their project
    NOTE: All images are set up as private. They can be made public by the importer. It is expected that the first
          virtual disk is the boot disk and any other disks are for data.
    """

    #make sure req values are in input_dict

    io = import_ops(auth_dict)
    glance = glance_ops(auth_dict)
    vol = volume_ops(auth_dict)

    #extract the ovf/ova package
    extract = io.extract_package({'package_name':input_dict['package_name'],'path':input_dict['path']})
    name = input_dict['package_name'].split('.')
    #set up the fully qualified path
    fqp = input_dict['path']+'/'+name[0]

    out = os.listdir(fqp)
    image_attrib = None
    for o in out:
        if(fnmatch(o,'*.ovf')):
            image_attrib = io.get_import_specs(fqp+'/'+o)

    #convert the disk(s)
    convert = io.convert_vdisk(extract)

    #import each one of the disk images to glance.
    ret_dict = {}
    import_dict = {}
    for x in convert:
        print x
        #Split the package name from the ova/ovf extension
        download_file = x['path']+'/'+ x['convert_disk']
        import_dict = {'image_name': input_dict['image_name'], 'container_format': 'bare', 'disk_format': 'qcow2', 'visibility': 'private', 'image_location': "", 'os_type': input_dict['os_type']}
        import_dict['image_location'] = download_file
        ret_dict = glance.import_image(import_dict)
        if(x['order'] != 'file1'):
            convert_vol = vol.create_volume({'volume_name':input_dict['image_name']+'_'+x['order'],'volume_size':x['disk_size'],'project_id':auth_dict['project_id'],'volume_type':'spindle','image_id':ret_dict['image_id']})
            print convert_vol
            ret_dict['new_vol_name'] = convert_vol['volume_name']
            ret_dict['volume_size'] = convert_vol['volume_size']

    #recreate the data disk(s) images to cinder volumes and keep the order
    #for disk in extract:
    #    if(disk)
    #connect the data(s) to the instance
    return ret_dict

