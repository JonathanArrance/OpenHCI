#!/usr/bin/python
#######standard impots#######
import sys
import json

import transcirrus.common.logger as logger
import transcirrus.common.config as config

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
            if 'sec' in user_dict:
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'
                
            #get the default cloud controller info
            self.controller = config.DEFAULT_CLOUD_CONTROLER
            self.api_ip = config.DEFAULT_API_IP

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
        
    def attach_vol_to_server(input_dict):
        curl -i http://192.168.10.30:8774/v2/7c9b14b98b7944e7a829a2abdab12e02/servers/1d0abaa2-e981-449b-a3b2-7e52f400cb30/os-volume_attachments -X POST -H "X-Auth-Project-Id: demo"
        -d '{"volumeAttachment": {"device": "/dev/vdc", "volumeId": "a5d6820b-140b-4a35-b5a3-57f05e3b23f6"}}'
        
    def detach_vol_from_server(input_dict):
        curl -i http://192.168.10.30:8774/v2/7c9b14b98b7944e7a829a2abdab12e02/servers/1d0abaa2-e981-449b-a3b2-7e52f400cb30/os-volume_attachments/a5d6820b-140b-4a35-b5a3-57f05e3b23f6 -X DELETE -H "X-Auth-Project-Id: demo"
        