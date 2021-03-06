#!/usr/bin/python
#######standard impots#######
import sys
import json

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
from transcirrus.common.auth import get_token
import transcirrus.component.nova.error as ec

from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

#get the nova libs
from flavor import flavor_ops
from image import nova_image_ops

#######Special imports#######
#sys.path.append('/home/jonathan/alpo.0/component/neutron')
#from security import net_security_ops

class server_storage_ops:
    #UPDATED/UNITTESTED
    #DESC:
    #INPUT:
    #OUTPUT:
    
    def __init__(self,user_dict):
        reload(config)
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        # user_dict = {"username":self.username,"password":self.user_pass,"project_id":exist[0][7],"status_level":status_level,"user_level":user_level,"is_admin": is_admin,"token":token}
        else:
            self.username = user_dict['username']
            self.password = user_dict['password']
            self.project_id = user_dict['project_id']
            self.token = user_dict['token']
            self.status_level = user_dict['status_level']
            self.user_level = user_dict['user_level']
            self.is_admin = user_dict['is_admin']
            self.adm_token = user_dict['adm_token']
            self.user_id = user_dict['user_id']
            
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

        if(self.is_admin == 1 and self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")
            raise Exception("No admin tokens passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        #attach to the DB
        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        #build flavor object
        self.flav = flavor_ops(user_dict)

        #build the nova image object
        self.image = nova_image_ops(user_dict)

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def destructor(self):
        #close any open db connections
        self.db.pg_close_connection()

    def attach_vol_to_server(self,input_dict):
        #curl -i http://192.168.10.30:8774/v2/7c9b14b98b7944e7a829a2abdab12e02/servers/1d0abaa2-e981-449b-a3b2-7e52f400cb30/os-volume_attachments -X POST -H "X-Auth-Project-Id: demo"
        #-d '{"volumeAttachment": {"device": "/dev/vdc", "volumeId": "a5d6820b-140b-4a35-b5a3-57f05e3b23f6"}}'
        """
        DESC: Attach a volume to a virtual server.
        INPUT: input_dict - project_id
                          - instance_id
                          - volume_id
                          - mount_point - ex. /dev/vdc
        OUTPUT: OK - success
                raise error
        NOTE: All veriables are rquiered. Admins can attach a volume to any instance. Power users can attach volumes to any instance in their project.
              Users can  only attach volumes they own to instances they own.
        """
        for key, val in input_dict.items():
            #skip over these
            if(val == ""):
                logger.sys_error("The value %s was left blank" %(val))
                raise Exception("The value %s was left blank" %(val))
            if(key not in input_dict):
                logger.sys_error("Volume mount info not specified")
                raise Exception ("Volume mount info not specified")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(input_dict['project_id'])}
            proj_name = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        #if(self.is_admin == 0):
        #    if(self.project_id != input_dict['project_id']):
        #        logger.sys_error("Users can only attach volumes to instances in their project.")
        #        raise Exception("Users can only attach volumes to instances in their project.")

        if(self.is_admin == 0):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error("Users can only attach volumes to instances in their project.")
                raise Exception("Users can only attach volumes to instances in their project.")
        #check if the volume/instance given is owned by the user
            try:
                select_vol = {'select':'vol_name','from':'trans_system_vols','where':"keystone_user_uuid='%s'"%(self.user_id),'and':"vol_id='%s'"%(input_dict['volume_id'])}
                vol_name = self.db.pg_select(select_vol)
                if(vol_name == ''):
                    logger.sys_error("The user does not own the volume.")
                    raise Exception("The user does not own the volume.")
            except:
                logger.sys_error("The volume given does not exist. Can not attach.")
                raise Exception("The volume given does not exist. Can not attach")

            try:
                #username needs to be changed to keystone user uuid
                select_instance = {'select':'inst_name','from':'trans_instances','where':"inst_id='%s'"%(input_dict['instance_id']),'and':"inst_user_id='%s'"%(self.user_id)}
                inst_name = self.db.pg_select(select_instance)
                if(inst_name == ''):
                    logger.sys_error("The user does not own the instance.")
                    raise Exception("The user does not own the instance.")
            except:
                logger.sys_error("The instance given does not exist. Can not attach.")
                raise Exception("The instance given does not exist. Can not attach")

        #if(self.user_level <= 2):
        try:
            #build an api connection
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(input_dict['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the api caller.")
            raise Exception("Could not connect to the api caller.")

        try:
            # First we need find the next available mountpoint for this instance.
            # We have to get the mountpoint(s) already in use (if any) by the instance.
            select_dev = {'select':'vol_mount_location','from':'trans_system_vols','where':"vol_attached_to_inst='%s'"%(input_dict['instance_id'])}
            dev_list = self.db.pg_select (select_dev)
            if (len(dev_list) == 0):
                # We didn't get any devices so we need to make sure we have a valid instance.
                select_inst = {'select':'inst_id','from':'trans_instances','where':"inst_id='%s'"%(input_dict['instance_id'])}
                inst_list = self.db.pg_select (select_inst)
                if (len(inst_list) == 0):
                    # We got a bad instance because it wasn't in the db.
                    logger.sys_error("The given instance for the mountpoint does not exist.")
                    raise Exception("The given instance for the mountpoint does not exist.")

            # Go get the next available mountpoint based on what the instance already is using and update the dict for later use.
            mountpoint = self.find_available_mountpoint(dev_list)
            logger.sys_info("Given mountpoint: %s being changed to %s" % (input_dict['mount_point'], mountpoint))
            input_dict['mount_point'] = mountpoint

            body = '{"volumeAttachment": {"device": "%s", "volumeId": "%s"}}'%(input_dict['mount_point'],input_dict['volume_id'])
            token = self.token
            #NOTE: if token is not converted python will pass unicode and not a string
            header = {"Content-Type": "application/json", "X-Auth-Project-Id": proj_name[0][0], "X-Auth-Token": str(token)}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/os-volume_attachments' %(input_dict['project_id'],input_dict['instance_id'])
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8774"}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            self.db.pg_transaction_rollback()
            raise e

        if(rest['response'] == 200):
            #insert the volume info into the DB
            self.db.pg_transaction_begin()
            update_vol = {'table':'trans_system_vols','set':"vol_attached_to_inst='%s',vol_attached=true,vol_mount_location='%s'"%(input_dict['instance_id'],input_dict['mount_point']),'where':"vol_id='%s'"%(input_dict['volume_id'])}
            self.db.pg_update(update_vol)
            self.db.pg_transaction_commit()
            return "OK"
        else:
            #util.http_codes(rest['response'],rest['reason'],rest['data'])
            ec.error_codes(rest)

    def detach_vol_from_server(self,input_dict):
        #curl -i http://192.168.10.30:8774/v2/7c9b14b98b7944e7a829a2abdab12e02/servers/1d0abaa2-e981-449b-a3b2-7e52f400cb30/os-volume_attachments/a5d6820b-140b-4a35-b5a3-57f05e3b23f6 -X DELETE -H "X-Auth-Project-Id: demo"
        """
        DESC: Check if the uplink ip gateway is on the same network as the uplink ip
        INPUT: input_dict - project_id
                          - instance_id
                          - volume_id
        OUTPUT: OK - success
                raise error
        NOTE: All veriables are rquiered. Admins and power users can detach a volume from any instance in their project. Users
              can only remove volumes from instances they own.
        """
        for key, val in input_dict.items():
            #skip over these
            if(val == ""):
                logger.sys_error("The value %s was left blank" %(val))
                raise Exception("The value %s was left blank" %(val))
            if(key not in input_dict):
                logger.sys_error("Volume mount info not specified")
                raise Exception ("Volume mount info not specified")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(input_dict['project_id'])}
            proj_name = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error("Users can only reboot virtual serves in their project.")
                raise Exception("Users can only reboot virtual serves in their project.")

        if(self.is_admin != 1):
        #check if the volume/instance given is owned by the user
            try:
                select_vol = {'select':'vol_name','from':'trans_system_vols','where':"keystone_user_uuid='%s'"%(self.user_id),'and':"vol_id='%s'"%(input_dict['volume_id'])}
                vol_name = self.db.pg_select(select_vol)
                if(vol_name == ''):
                    logger.sys_error("The user does not own the volume.")
                    raise Exception("The user does not own the volume.")
            except:
                logger.sys_error("The volume given does not exist. Can not detach.")
                raise Exception("The volume given does not exist. Can not detach")

            try:
                #username needs to be changed to keystone user uuid
                select_instance = {'select':'inst_name','from':'trans_instances','where':"inst_id='%s'"%(input_dict['instance_id']),'and':"inst_username='%s'"%(self.username)}
                inst_name = self.db.pg_select(select_instance)
                if(inst_name == ''):
                    logger.sys_error("The user does not own the instance.")
                    raise Exception("The user does not own the instance.")
            except:
                logger.sys_error("The instance given does not exist. Can not detach.")
                raise Exception("The instance given does not exist. Can not detach")
        try:
            #build an api connection
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(input_dict['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the api caller.")
            raise Exception("Could not connect to the api caller.")

        try:
            #add the new user to openstack 
            body = ''
            token = self.token
            #NOTE: if token is not converted python will pass unicode and not a string
            header = {"Content-Type": "application/json", "X-Auth-Project-Id": proj_name[0][0], "X-Auth-Token": str(token)}
            function = 'DELETE'
            api_path = '/v2/%s/servers/%s/os-volume_attachments/%s' %(input_dict['project_id'],input_dict['instance_id'],input_dict['volume_id'])
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8774"}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            self.db.pg_transaction_rollback()
            raise e

        if(rest['response'] == 202):
            #insert the volume info into the DB
            self.db.pg_transaction_begin()
            update_vol = {'table':'trans_system_vols','set':"vol_attached_to_inst=NULL,vol_attached=false,vol_mount_location=NULL",'where':"vol_id='%s'"%(input_dict['volume_id'])}
            self.db.pg_update(update_vol)
            self.db.pg_transaction_commit()
        else:
            ec.error_codes(rest)

        return "OK"

    def list_attached_vols(self,input_dict):
        """
        DESC: List the volumes that are attached to the instance
        INPUT: input_dict - instance_id
                          - project_id
        OUTPUT: array of r_dict - vol_id
                                - vol_name
                                - vol_size
                                - vol_mount_location
        ACCESS: Admin - List volumes attached to any instance
                PU - List vols attahed to any instance in their project
                User - List volumes attached to instances they own
        NOTE: All veriables are rquiered. Admins and power users can detach a volume from any instance in their project. Users
              can only remove volumes from instances they own.
        """
        for key, val in input_dict.items():
            #skip over these
            if(val == ""):
                logger.sys_error("The value %s was left blank" %(val))
                raise Exception("The value %s was left blank" %(val))
            if(key not in input_dict):
                logger.sys_error("Volume attached info not specified")
                raise Exception ("Volume attached info not specified")

        if(self.is_admin == 0):
            if(self.user_level == 1):
                self.select_att = {'select':'vol_id,vol_name,vol_size,vol_mount_location','from':'trans_system_vols','where':"vol_attached_to_inst='%s'"%(input_dict['instance_id']),'and':"proj_id='%s'"%(input_dict['project_id'])}
            elif(self.is_admin == 2):
                self.select_att = {'select':'vol_id,vol_name,vol_size,vol_mount_location','from':'trans_system_vols','where':"vol_attached_to_inst='%s'"%(input_dict['instance_id']),'and':"keystone_user_uuid='%s'"%(self.user_id)}
        else:
            self.select_att = {'select':'vol_id,vol_name,vol_size,vol_mount_location','from':'trans_system_vols','where':"vol_attached_to_inst='%s'"%(input_dict['instance_id'])}

        #check if the snapshot exists in the project and that the user can use it
        try:
            get_att = self.db.pg_select(self.select_att)
        except:
            logger.sys_error("The snapshot does not exist in this project, or you may not have permission to use it.")
            raise Exception("The snapshot does not exist in this project, or you may not have permission to use it.")

        r_array = []
        for att in get_att:
            r_dict = {'vol_id':att[0],'vol_name':att[1],'vol_size':att[2],'vol_mount_location':att[3]}
            r_array.append(r_dict)
        return r_array

    def find_available_mountpoint(self,used_list):
        """
        DESC: Find the first available mount point based on the given list of used mountpoints.
        INPUT: used_list - list of lists (or DictRows) to used mount points
        OUTPUT: a mountpoint - success
                None - if no available mount points were found
        NOTE: If the list is empty it should not be an empty list of lists, just an empty list.
              A list of lists or list of DictRows is fine.
        """
        complete_list = ["/dev/vdc", "/dev/vdd", "/dev/vde", "/dev/vdf", "/dev/vdg", "/dev/vdh", "/dev/vdi", "/dev/vdj",
                         "/dev/vdk", "/dev/vdl", "/dev/vdm", "/dev/vdn", "/dev/vdo", "/dev/vdp", "/dev/vdq", "/dev/vdr",
                         "/dev/vds", "/dev/vdt", "/dev/vdu", "/dev/vdv", "/dev/vdw", "/dev/vdx", "/dev/vdy", "/dev/vdz"]

        # Since this is a list of lists, we need to check if there is anything in the list first. If there isn't
        # anything there then just return the first device from this complete list.
        num_items = len(used_list)
        if (num_items < 1):
            return (complete_list[0])

        # Loop through the complete list until we don't find a match which means its available to be used.
        found = None
        for index in range (len(complete_list)):
            if (any(complete_list[index] in x[0] for x in used_list)):
                continue
            else:
                found = complete_list[index]
                break

        return (found)
