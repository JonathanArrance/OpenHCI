#!/usr/bin/python
#######standard impots#######
import sys
import json

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

#get the nova libs
from flavor import flavor_ops
from image import nova_image_ops

#######Special imports#######
#sys.path.append('/home/jonathan/alpo.0/component/neutron')
#from security import net_security_ops

class server_storage_ops:
    #DESC:
    #INPUT:
    #OUTPUT:
    def __init__(self,user_dict):
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
                logger.sys_error("The volume given does not exist. Can not attach.")
                raise Exception("The volume given does not exist. Can not attach")

            try:
                #username needs to be changed to keystone user uuid
                select_instance = {'select':'inst_name','from':'trans_instances','where':"inst_id='%s'"%(input_dict['instance_id']),'and':"inst_username='%s'"%(self.username)}
                inst_name = self.db.pg_select(select_instance)
                if(inst_name == ''):
                    logger.sys_error("The user does not own the instance.")
                    raise Exception("The user does not own the instance.")
            except:
                logger.sys_error("The instance given does not exist. Can not attach.")
                raise Exception("The instance given does not exist. Can not attach")

        if(self.user_level <= 1):
            try:
                #build an api connection
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the api caller.")
                raise Exception("Could not connect to the api caller.")
    
            try:
                #add the new user to openstack 
                body = '{"volumeAttachment": {"device": "%s", "volumeId": "%s"}}'%(input_dict['mount_point'],input_dict['volume_id'])
                token = self.token
                #NOTE: if token is not converted python will pass unicode and not a string
                header = {"Content-Type": "application/json", "X-Auth-Project-Id": proj_name[0][0], "X-Auth-Token": str(token)}
                function = 'POST'
                api_path = '/v2/%s/servers/%s/os-volume_attachments' %(input_dict['project_id'],input_dict['instance_id'])
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8774"}
                rest = api.call_rest(rest_dict)
                print rest
                if(rest['response'] == 200):
                    #insert the volume info into the DB
                    self.db.pg_transaction_begin()
                    update_vol = {'table':'trans_system_vols','set':"vol_attached_to_inst='%s',vol_attached=true,vol_mount_location='%s'"%(input_dict['instance_id'],input_dict['mount_point']),'where':"vol_id='%s'"%(input_dict['volume_id'])}
                    self.db.pg_update(update_vol)
                    self.db.pg_transaction_commit()
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except Exception as e:
                self.db.pg_transaction_rollback()
                print "%s" %(e)
                raise e
        return "OK"

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
            if(rest['response'] == 202):
                #insert the volume info into the DB
                self.db.pg_transaction_begin()
                update_vol = {'table':'trans_system_vols','set':"vol_attached_to_inst='NULL',vol_attached=false,vol_mount_location='NULL'",'where':"vol_id='%s'"%(input_dict['volume_id'])}
                self.db.pg_update(update_vol)
                self.db.pg_transaction_commit()
            else:
                util.http_codes(rest['response'],rest['reason'])
        except Exception as e:
            self.db.pg_transaction_rollback()
            raise e
        return "OK"