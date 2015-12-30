#!/usr/local/bin/python2.7
import subprocess
import os

import transcirrus.common.migration as migration
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.component.glance.glance_ops_v2.py import glance_ops

def importvmdk(auth_dict,input_dict):

    status = _set_up_ovf_tool()
    if(status == 'ERROR'):
        logger.sys_error('Could not install the OVFTool please check your settings.')
        raise Exception('Could not install the OVFTool please check your settings.')

    extract = migration.extract_packaged_vm(package_name)

    input_dict = {'format':'qcow2','image_name':input_dict['image_name']}
    convert = migration.convert_vmdk(input_dict)

    glance = glance_ops(auth_dict)

    glance_import = {'image_name':input_dict['image_name'],'container_formet':'bare','disk_format':'qcow2','image_type':'image_file','visibility':'private','image_location':''}
    import_image = glance.import_image(glance_import)


Do you agree? [yes/no]: y

The product is ready to be installed.  Press Enter to begin
installation or Ctrl-C to cancel.

                
                pass
            else:
                continue
            if(len(directory) == (index - 1)):
                logger.sys_error('Could not find the OVFtool, please upload it and retry.')
                raise Exception('Could not find the OVFtool, please upload it and retry.')