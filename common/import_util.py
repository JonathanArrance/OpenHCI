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
                                - disk_size
                                - order
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

        #extract and convert to raw or qcow2
        package_split = input_dict['package_name'].split('.')
        if(package_split[1] == 'ova'):
            os.mkdir(input_dict['path']+'/'+package_split[0])
            out = subprocess.call(["tar", "-xvf", input_dict['path']+'/'+input_dict['package_name'],"-C",input_dict['path']+'/'+package_split[0]])
            if(out == 0):
                self.contents = os.listdir(input_dict['path']+'/'+package_split[0])
        elif(package_split[1] == 'ovf'):
            self.contents = os.listdir(input_dict['path']+'/'+input_dict['package_name'])
        else:
            logger.sys_error("Invalid package type. %s not supported"%(package_split[1]))
            raise Exception("Invalid package type. %s not supported"%(package_split[1]))

        for x in self.contents:
            if(fnmatch(x,'*.ovf')):
                #get the ovf xml
                self.attribs = self.get_import_specs('%s'%(input_dict['path']+'/'+package_split[0]+'/'+x))

        self.r_array = []
        for y in self.attribs['disks']:
            self.r_dict = {'disk_type':'vmdk','disk':str(y['disk']),'path':input_dict['path']+'/'+package_split[0],'disk_size':str(y['size']),'order':str(y['order'])}
            self.r_array.append(self.r_dict)

        return self.r_array

    def convert_vdisk(self,input_array):
        """
        DESC: Pull the vmdks out of the OVA or OVF based package and convert to qcow2 or raw.
        INPUT: input_array of dict - disk_type - REQ
                                   - disk - REQ
                                   - path - REQ
                                   - disk_size - OP
                                   - order - OP
        OUTPUT: r_array of dict - path
                                - convert_disk
                                - order
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

        #if array brough in from extract order will be included with it.
        r_array = []
        if(flag == 1):
            for item in input_array:
                if('order' not in item):
                    item['order'] = 'NULL'
                #if('disk_size' in item):
                    #self.command = 'cd %s; sudo qemu-img convert -f %s -O qcow2 %s %s.qcow2 -o size=%sG'%(item['path'],item['disk_type'],item['disk'],item['disk'].split('.')[0],item['disk_size'])
                #else:
                self.command = 'cd %s; sudo qemu-img convert -f %s -O qcow2 %s %s.qcow2'%(item['path'],item['disk_type'],item['disk'],item['disk'].split('.')[0])
                out = os.popen('%s'%(self.command))
                r_array.append({'path':item['path'],'convert_disk':item['disk'].split('.')[0] +".qcow2",'order':str(item['order']),'disk_size':item['disk_size']})

        return r_array

    def get_import_specs(self,path):
        """
        DESC: Pull the relevent spec info from the .ovf(xml) file.
        INPUT: path - REQ
        OUTPUT: r_dict - inst_name
                       - memory
                       - num_cpu
                       - disks - array or r_dict - disk
                                                 - order
                                                 - size
        ACCESS: Admins - can extract in any project
                PU - can extract only in their project
                User - can extract only in their project
        NOTE: This will be used to build out a new spec if needed.
        """
        #check user levels
        flag = 0
        if(self.user_level == 0):
            flag = 1
        elif(self.user_level >= 1 and self.project_id == input_dict['project_id']):
            flag == 1
        else:
            logger.sys_info('Can not get the extracted package spec. Invalid User.')
            raise Exception('Can not get the extracted package spec. Invalid User.')

        r_dict = {}
        xmldoc = minidom.parse('%s'%(path))
        files = xmldoc.getElementsByTagName('File')
        disks = []
        for f in files:
            disk_dict = {}
            disk_dict['disk'] = f.getAttribute('ovf:href')
            disk_dict['order'] = f.getAttribute('ovf:id')
            storage = xmldoc.getElementsByTagName('Disk')
            for s in storage:
                if(s.getAttribute('ovf:fileRef') == disk_dict['order']):
                    disk_dict['size'] = s.getAttribute('ovf:capacity')
            disks.append(disk_dict)
        r_dict['disks'] = disks

        vs = xmldoc.getElementsByTagName('VirtualSystem')[0]
        r_dict['inst_name'] = vs.getAttribute('ovf:id')

        items = xmldoc.getElementsByTagName('Item')
        for item in items:
            description = item.getElementsByTagName('rasd:Description')
            values = item.getElementsByTagName('rasd:VirtualQuantity')
            for desc in description:
                out = desc.childNodes[0].nodeValue
                if(out == 'Number of Virtual CPUs'):
                    for val in values:
                        out2 = val.childNodes[0].nodeValue
                        r_dict['num_cpu'] = out2
                if(out == 'Memory Size'):
                    for val in values:
                        out2 = val.childNodes[0].nodeValue
                        r_dict['memory'] = out2
        return r_dict

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