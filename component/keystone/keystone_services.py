#!/usr/bin/python

#NOT IMPLEMENTED ATTHIS TIME. SERVICES ARE ADDED AND DELETED WITH ENDPOINTS
# IN THE PROTOTYPE

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import json

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

class service_ops:

    #DESC: Constructor to build out the tokens object
    #INPUT: user_dict dictionary containing - built in auth.py
    def __init__(self,user_dict):
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        # user_dict = {"username":self.username,"password":self.user_pass,"project_id":exist[0][7],"status_level":status_level,"user_level":user_level,"is_admin": is_admin,"token":token}
        else:
            self.username = user_dict['username']
            self.password = user_dict['password']
            self.project_id = user_dict['project_id']
            if((self.project_id == 'NULL') or (not user_dict['project_id'])):
                logger.sys_error("In order to perform user operations, Admin user must be assigned to project")
                raise Exception("In order to perform user operations, Admin user must be assigned to project")
            self.token = user_dict['token']
            self.status_level = user_dict['status_level']
            self.user_level = user_dict['user_level']
            self.is_admin = user_dict['is_admin']
            self.is_cloud_admin = user_dict['is_cloud_admin']
            self.adm_token = user_dict['adm_token']
            if 'sec' in user_dict:
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'
                
            #get the default cloud controller info
            self.controller = config.DEFAULT_CLOUD_CONTROLER

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")

        if((self.token == 'error') or (self.token == '')):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        try:
            #use util.close_db when you no longer need o have the connection open.
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
            logger.sql_info("Connected to the Transcirrus DB to do keystone user operations.")
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB, %s" %(e))
            raise

    #DESC: Add a service to the keystone service catalog. Only Cloud admins may do this.
    #INPUT: input_dict - service_name
    #                  - service_type
    #OUTPUT: r_dict - service_name
    #               - service_id
    def add_service(self,input_dict):
        #REQ: curl -i -X POST http://192.168.10.30:35357/v2.0/OS-KSADM/services -H "User-Agent: python-keystoneclient" -H "Content-Type: application/json" -H "X-Auth-Token: cheapass"
        #REQ BODY: {"OS-KSADM:service": {"type": "volume", "name": "cinder2", "description": null}}
        #RESP: [200] {'date': 'Sat, 07 Sep 2013 02:44:09 GMT', 'content-type': 'application/json', 'content-length': '122', 'vary': 'X-Auth-Token'}
        #RESP BODY: {"OS-KSADM:service": {"id": "e22e313a829d47198d61aea7742ff791", "type": "volume", "name": "cinder2", "description": null}}

        #http://docs.openstack.org/api/openstack-identity-service/2.0/content/POST_addService_v2.0_OS-KSADM_services_Service_Operations_OS-KSADM.html
        print "not implemented"

    #DESC: Delete a service from the keystone service catalog. Only Cloud admins may do this.
    #INPUT: service_name
    #OUTPUT: OK if deleted else error
    def delete_service(self,service_name):
        print "not implemented"

    #DESC: List all of the services in the openstack cloud Cloud admin, admins, power_users may do this.
    #INPUT: None
    #OUTPUT: array or r_dict - service_name
    #                        - service_id
    def list_services(self):
        print "not implemented"

    #DESC: List attributes for a given service Cloud admin,admin, and power_users
    #INPUT: service_name
    #OUTPUT: r_dict - service_name
    #               - service_type
    #               - service_id
    #               - service_desc
    def get_service(self,service_name):
        print "not implemented"
        
