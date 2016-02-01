#!/usr/local/bin/python2.7
import subprocess
import os
from fnmatch import fnmatch

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.import_util import import_ops
from transcirrus.component.glance.glance_ops_v2 import glance_ops
from transcirrus.component.cinder.cinder_volume import volume_ops
from transcirrus.component.nova.flavor import flavor_ops

def import_vmware(auth_dict,input_dict):
    """
    DESC: Extract and import ovf virtual disks. Then attempt to rebuild the virtual machine.
    INPUT: input_dict - image_name - REQ
                      - package_name - REQ
                      - path - REQ
                      - os_type - REQ
                      - project_id - REQ
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
    logger.sys_info('\n**Import Vmware workload operation: def: import_vmware**\n')
    for key,value in input_dict.items():
        if(key == ''):
            logger.sys_error('Required value not passed.')
            raise Exception('Required value not passed.')
        if(value == ''):
            logger.sys_error('Required value not passed.')
            raise Exception('Required value not passed.')

    io = import_ops(auth_dict)
    glance = glance_ops(auth_dict)
    vol = volume_ops(auth_dict)
    flav = flavor_ops(auth_dict)

    try:
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
    except Exception as e:
        logger.sys_error('Could not extract the package %s. Please check the package and retry the import. %s'%(input_dict['package_name'],e))
        raise Exception('Could not extract the package %s. Please check the package and retry the import. %s'%(input_dict['package_name'],e))

    try:
        #convert the disk(s)
        convert = io.convert_vdisk(extract)
    except Exception as e:
        logger.sys_error('Could not convert the package %s. Please check the package and retry the import. %s'%(input_dict['package_name'],e))
        raise Exception('Could not convert the package %s. Please check the package and retry the import. %s'%(input_dict['package_name'],e))

    #import each one of the disk images to glance.
    ret_dict = {}
    import_dict = {}
    r_array = []
    for x in convert:
        #Split the package name from the ova/ovf extension
        download_file = x['path']+'/'+ x['convert_disk']
        import_dict = {'image_name': input_dict['image_name'], 'container_format': 'bare', 'disk_format': 'qcow2', 'visibility': 'private', 'image_location': "", 'os_type': input_dict['os_type']}
        import_dict['image_location'] = download_file
        ret_dict = glance.import_image(import_dict)
        if(x['order'] != 'file1'):
            try:
                convert_vol = vol.create_volume({'volume_name':input_dict['image_name']+'_'+x['order'],'volume_size':x['disk_size'],'project_id':input_dict['project_id'],'volume_type':'spindle','image_id':ret_dict['image_id']})
                ret_dict['new_vol_name'] = convert_vol['volume_name']
                ret_dict['volume_size'] = convert_vol['volume_size']
            except Exception as e:
                #check to make sure cinder imported drives
                logger.sys_info('Could not import data drive into Cinder. %s'%(e))
                raise Exception('Could not import data drive into Cinder. %s'%(e))
            r_array.append(ret_dict)
            #delete the datadisk glance image
            try:
                image_delete = glance.delete_image(ret_dict['image_id'])
            except Exception as e:
                logger.sys_info('Could not delete data drive image for drive %s. %s'%(input_dict['image_name']+'_'+x['order'],e))
                raise Exception('Could not delete data drive image for drive %s. %s'%(input_dict['image_name']+'_'+x['order'],e))
        else:
            #append the boot disk.
            image_attrib['boot_disk'] = x['disk_size']
            r_array.append(ret_dict)

    #build out a custom flavor for the new instance based on the ovf spec
    try:
        build_flav = flav.create_flavor({'name':input_dict['image_name']+'_temp_flav','ram':image_attrib['memory'],'boot_disk':image_attrib['boot_disk'],'cpus':image_attrib['num_cpu']})
    except Exception as e:
        logger.sys_error('Could not build a temp flavor with the information given during import workload. %s'%(e))
        raise Exception('Could not build a temp flavor with the information given during import workload. %s'%(e))

    #boot up the new instance with the attached data disks 
    #nova --debug boot --flavor 1 --image 4bcbe4e0-fef8-46ed-8221-82f92ccf24ee --block-device-mapping vdb=08b1885c-4660-4c59-8fd0-6f27f7532f57:::0 jon
    #curl -i 'http://192.168.2.34:8774/v2/027f32b21dcb4e83bff0b0ebb4bf79a3/os-volumes_boot' -X POST
    #-d '{"server": {"name": "jon", "imageRef": "4bcbe4e0-fef8-46ed-8221-82f92ccf24ee", "block_device_mapping": [{"volume_id": "08b1885c-4660-4c59-8fd0-6f27f7532f57", \
    #"delete_on_termination": "0", "device_name": "vdb"}], "flavorRef": "1", "max_count": 1, "min_count": 1}}'

    #connect the data(s) to the instance

    #remove the custom flavor

    #clean up the mess in /tmp
    clean_up = os.system('sudo rm -rf %s'%(fqp))
    clean_up2 = os.system('sudo rm -rf %s'%(input_dict['path']+'/'+input_dict['package_name']))
    if(clean_up == 0 and clean_up2 == 0):
        logger.sys_info('Cleaned up %s after workload import.'%(fqp))
    else:
        logger.sys_warning('Cleaned up %s after workload import.'%(fqp))
        
    return r_array

