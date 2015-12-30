#!/usr/local/bin/python2.7
import subprocess
import os
from fnmatch import fnmatch
from xml.dom import minidom

import transcirrus.common.logger as logger
import transcirrus.common.config as config
#from transcirrus.component.glance.glance_ops_v2.py import glance_ops

class import_ops:
    def __init__(self,user_dict):
        reload(config)
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        else:
            self.username = user_dict['username']
            self.password = user_dict['password']
            self.user_id = user_dict['user_id']
            self.project_id = user_dict['project_id']
            self.token = user_dict['token']
            self.status_level = user_dict['status_level']
            self.user_level = user_dict['user_level']
            self.is_admin = user_dict['is_admin']

            if(self.is_admin == 1):
                self.adm_token = user_dict['adm_token']
            else:
                self.adm_token = 'NULL'

            if 'sec' in user_dict:
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'

            #get the default cloud controller info
            self.controller = config.CLOUD_CONTROLLER
            self.api_ip = config.API_IP

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")
            #raise Exception("No admin tokens passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        #attach to the DB
        #try:
            #Try to connect to the transcirrus db
        #    self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        #except Exception as e:
        #    logger.sys_error("Could not connect to db with error: %s" %(e))
        #    raise Exception("Could not connect to db with error: %s" %(e))

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def destructor(self):
        #close any open db connections
        self.db.close_connection()

    def extract_package(self,input_dict):
        """
        DESC: Pull the v-disks out of the OVA or OVF based package and determin what vendor.
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
        #extract and convert to raw or qcow2
        package_split = input_dict['package_name'].split('.')
        contents = None
        if(package_split[1] == 'ova'):
            os.mkdir(input_dict['path']+'/'+package_split[0])
            out = subprocess.call(["tar", "-xvf", input_dict['path']+'/'+input_dict['package_name'],"-C",input_dict['path']+'/'+package_split[0]])
            if(out == 0):
                contents = os.listdir(input_dict['path']+'/'+package_split[0])
        elif(package_split[1] == 'ovf'):
            contents = os.listdir(input_dict['path']+'/'+input_dict['package_name'])
        else:
            logger.sys_error("Invalid package type. %s not supported"%(package_split[1]))
            raise Exception("Invalid package type. %s not supported"%(package_split[1]))

        r_array = []
        r_dict = {}
        itemlist = None
        for x in contents:
            if(fnmatch(x,'*.ovf')):
                #get the ovf xml
                xmldoc = minidom.parse('%s'%(input_dict['path']+'/'+package_split[0]+'/'+x))
                itemlist = xmldoc.getElementsByTagName('File')
            if(fnmatch(x,'*.vmdk')):
                r_dict = {'disk_type':'vmdk','disk':x,'path':input_dict['path']+'/'+package_split[0]}
                if(itemlist[0].attributes['ovf:href'].value == x):
                    r_dict['order'] = itemlist[0].attributes['ovf:id'].value
                r_array.append(r_dict)
            if(fnmatch(x,'*.vhd')):
                r_dict = {'disk_type':'vhd','disk':x,'path':input_dict['path']+'/'+package_split[0]}
                r_array.append(r_dict)

        return r_array

    def convert_vdisk(self,input_array):
        """
        DESC: Pull the vmdks out of the OVA or OVF based package and convert to qcow2 or raw.
        INPUT: input_array of dict - disk_type
                                   - disk
                                   - path
        OUTPUT: r_array of dict - path
                                - convert_disk
        ACCESS: Admins - can extract in any project
                PU - can extract only in their project
                User - can extract only in their project
        NOTE: 
        """
        #check user levels
        flag = 0
        if(self.user_level == 0):
            flag = 1
        elif(self.user_level >= 1 and self.project_id == input_dict['project_id']):
            flag == 1
        else:
            logger.sys_info('Can not extract the VMware OVF/OVA package. Invalid User.')
            raise Exception('Can not extract the VMware OVF/OVA package. Invalid User.')

        r_array = []
        if(flag == 1):
            for item in input_array:
                command = 'cd %s; sudo qemu-img convert -f %s -O qcow2 %s %s.qcow2'%(item['path'],item['disk_type'],item['disk'],item['disk'].split('.')[0])
                out = os.popen('%s'%(command))
                r_array.append({'path':item['path'],'convert_disk':item['disk'].split('.')[0] +".qcow2"})

        print r_array

    def list_imports(self):
        """
        DESC: List the vmware ovf/ova packages that were imported
        INPUT: input_dict - instance_id - REQ
                          - project_id - REQ
                          - package_name - REQ
        OUTPUT: output_dict - out_array - not converted
                            - out_array - converted
        ACCESS: Admins - can extract in any project
                PU - can extract only in their project
                User - can extract only in their project
        NOTE: 
        """
        #get the converted an non-converted packages
        pass
    
    def remove_import(self):
        """
        DESC: Pull the vmdks out of the OVA or OVF based package.
        INPUT: input_dict - instance_id - REQ
                          - project_id - REQ
                          - package_name - REQ
        OUTPUT: OK - success
                ERROR - error
        ACCESS: Admins - can extract in any project
                PU - can extract only in their project
                User - can extract only in their project
        NOTE: 
        """
        #Remove the OVF/OVA/VMDK once it is imported into glance
        pass

    def set_up_ovf_tool():
        pass
        """
        #check if OVF tool is installed and ready
        
        #if not install it
        #https://developercenter.vmware.com/web/dp/tool/ovf/3.5.2
        #try the opensource version as well
            #check if it is uploaded to the /transcirrus directory
        p = pexpect.spawn("sudo ./VMware-ovftool-3.5.0-1274719-lin.x86_64.bundle")
    time.sleep(2)
    p.send("\n")
    while True:
        time.sleep(1)
        print p.readline()
        p.sendline()
        print p.readline()
        p.sendline()
        print p.readline()
        p.send('\n')
        print p.readline()
        break
    while True:
        p.send('\n')
        shit = p.readline()
        print shit.strip()
        if(shit.strip() == "Do you agree? [yes/no]:"):
            p.expect('Do you agree? [yes/no]: ')
            time.sleep(1)
            p.sendline('yes')
            print p.readline()
            time.sleep(5)
            p.sendline()
            break
        """