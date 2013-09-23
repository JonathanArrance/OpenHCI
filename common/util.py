#!/usr/bin/python
import sys
import os
import shutil

import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.database.postgres import pgsql
from time import gmtime, strftime
from ifconfig import ifconfig

######Transcirrus utils#######

#DESC: Logs and rasies excpetions from the OpenStack REST API
#INPUT: code - https error code
#       reason - message from REST API
#OUTPUT: void
def http_codes(code,reason):
    if(code):
        logger.sys_error("Response %s with Reason %s" %(code,reason))
        raise Exception("Response %s with Reason %s" %(code,reason))
    else:
        logger.sys_error("Error for unknown reason.")
        raise Exception("Error for unknown reason.")

def db_connect():
    try:
        #use util.close_db when you no longer need o have the connection open.
        #Try to connect to the transcirrus db
        db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        logger.sql_info("Connected to the Transcirrus DB to do keystone user operations.")
    except Exception as e:
        logger.sql_error("Could not connect to the Transcirrus DB, %s" %(e))
        raise

    return db

#DESC: used to clean up after the server class
#INPUT: self object
#OUTPUT: void
def db_close(db_obj):
    #close any open db connections
    db_obj.pg_close_connection()


def write_new_config_file(file_dict):
    """
    DESC: Write out a config file.
    INPUT: file_dict - file_path - req
                     - file_name - req
                     - file_content - array - req
                     - file_owner - req
                     - file_group - req
                     - file_perm - default 644
    OUTPUT: A file written out to the proper location with the proper permissions
            raise exceptions on fail
            OK - file written
            ERROR - file not written
            NA - unknown
    ACCESS: wide open
    NOTES: Note the file permissions come in the bit format, ex. 644
           The defualt file permissions should be sufficient for any config
           file written.
    """
    #make sure none of the values are empty
    for key, val in file_dict.items():
        #skip over these
        if(key == 'file_permissions'):
            continue
        if(val == ""):
            logger.sys_error("The value %s was left blank" %(val))
            raise Exception("The value %s was left blank" %(val))
        if(key not in file_dict):
            logger.sys_error("Required info not specified for file creation.")
            raise Exception ("Required info not specified for file creation.")

    permissions = None
    if(('file_permissions' not in file_dict) or (file_dict['file_permissions'])):
        permissions = '644'
    else:
        permissions = file_dict['file_permissions']

    #check if the config file exists in the file system
    path = []
    path.extend([file_dict['file_path'],file_dict['file_name']])
    fqp = "/".join(path)

    spath = []
    spath.extend(['/tmp',file_dict['file_name']])
    scratch = "/".join(spath)

    check_fqp = os.path.exists(fqp)
    config = None
    if(check_fqp == False):
        logger.sys_warning("The file %s does not exists, Creating..." %(fqp))
        #os.system('touch %s' %(scratch))
        config = open(scratch, 'w')
    else:
        logger.sys_warning("The file %s exists. Creating a backup and building new config." %(fqp))
        date = strftime("%Y-%m-%d", gmtime())
        old = '%s_%s' %(fqp,date)
        os.system('sudo cp -f %s %s' %(fqp,old))
        config = open(scratch, 'w')

    #check that the array of lines is not empty
    if(len(file_dict['file_content']) == 0):
        logger.sys_warning("No file input was given. Can not write out the file.")
        raise Exception("No file input was given. Can not write out the file.")

    try:
        for line in file_dict['file_content']:
            config.write(line)
            config.write('\n')
        os.system('sudo mv %s %s' %(scratch,fqp))
        config.close()
        os.system('rm -f %s' %(scratch))

        #set ownership
        os.system('sudo chown %s:%s %s' %(file_dict['file_owner'],file_dict['file_group'],fqp))

        #set permissions
        os.system('sudo chmod %s %s' %(file_dict['file_perm'],fqp))

    except IOError:
        config.close()
        #move the backup copy back to the original copy
        #shutil.move('%s_%s','%s') %(fqp,date,fqp)
        logger.sys_error("Could not write the config file at path %s" %(fqp))
        raise Exception("Could not write the config file at path %s" %(fqp))

    #confirm the file was written and return OK if it was ERROR if not
    check_new_path = os.path.exists(fqp)
    if(check_new_path == True):
        return 'OK'
    elif(check_new_path == False):
        return 'ERROR'
    else:
        return 'NA'

def delete_config_file(file_dict):
    """
    DESC: Write out a config file.
    INPUT: file_dict - file_path
                     - file_name
                     - file_content
    OUTPUT: OK - file deleted
            ERROR - file could not be deleted
            NA - Unknown
    ACCESS: wide open
    NOTES: This will be used as part fo the cleanup procedure to set the system back to
           the factory state.
    """
#######System level calls used to run linux commands#######

def ping_ip(ip):
    """
    DESC: Ping an ip
    INPUT: ip
    OUTPUT: OK - success
            ERROR - fail
            NA - unknown
    """
    out = os.system('sudo ping %s'  %(ip))
    if(out):
        return 'OK'
    elif(!out):
        return 'ERROR'
    else:
        return 'NA'


def set_adapter_ip():
    """
    DESC: Change the ip address for the given adapter. Only cloud admins can
          perform this operation.
    INPUT: input_dict - user_level
                      - net_adapter
                      - new_ip
                      - new_subnet - op
                      - new_gateway - op
    OUTPUT: r_dict - net_adapter
                   - new_ip
                   - ping SUCCESS/FAIL
    """

    print "not implemented"
    

def set_adapter_dhcp(net_adapter):
    print "not implemented"

def get_adapter_ip(net_adapter):
    """
    DESC: Get the ip info associated with a specific network adapter.
    INPUT: net_adapter
    OUTPUT: r_dict - net_adapter
                   - net_ip
                   - net_mask
                   - net_mac
    """
    out = ifconfig('%s' %(net_adapter))
    r_dict = {'net_adapter':net_adapter,'net_ip':out['addr'],'net_mask':out['netmask'],'net_mac':out['hwaddr']}
    return r_dict

def halt_system():
    """
    DESC: Halt the local system.
    INPUT: none
    OUTPUT: none
    NOTE: VERY DANGEROUS. THIS IS WIDE OPEN AS OF NOW
    """
    os.system('sudo shutdown -H')

def reboot_system():
    """
    DESC: Reboot the local system.
    INPUT: none
    OUTPUT:
    NOTE: VERY DANGEROUS. THIS IS WIDE OPEN AS OF NOW
    """
    os.system('sudo reboot')

def power_off_system():
    """
    DESC: Power off the local system.
    INPUT: none
    OUTPUT: none
    NOTE: VERY DANGEROUS. THIS IS WIDE OPEN AS OF NOW
    """
    os.system('sudo shutdown -P')


