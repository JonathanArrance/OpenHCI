import sys
import json
import subprocess

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token
from transcirrus.database.postgres import pgsql

class account_service_ops:
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

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        #attach to the DB
        self.db = util.db_connect()

    def get_account_containers(self,project_id):
        """
        DESC: Get the account information
        INPUT None
        OUTPUT: r_array - list of containers
        ACCESS: Admin - can get the account data from an project
                PU - can get the account data for their project
                User - can not get account data
        NOTE:
        """
        logger.sys_info('\n**Getting Swift account data. Component: Swift Def: get_account_data**\n')
        if(self.user_level == 0):
            logger.sys_info('Admin user logged in.')
        elif(self.user_level == 1):
            if(project_id != self.project_id):
                logger.sys_error('Power user not in the project.')
                raise Exception('Power user not in the project.')
        else:
            logger.sys_error('Only admins and power users can get info from .')
            raise Exception('Power user not in the project.')

        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":project_id}
            if(self.project_id != project_id):
                self.token = get_token(self.username,self.password,project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            #add the new user to openstack
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'GET'
            api_path = '/v1/AUTH_%s' %(project_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8080'}
            rest = api.call_rest(rest_dict)
        except:
            logger.sql_error("Could not get the Swift account info.")
            raise Exception("Could not get the Swift account info.")

        #check the response and make sure it is a 204
        if(rest['response'] == 204 or rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            r_array = rest['data'].split('\n')
            r_array.pop()
            return r_array
        else:
            util.http_codes(rest['response'],rest['reason'])

    def create_account_metadata(self):
        pass

    def update_account_metadata(self):
        pass

    def delete_account_metadata(self):
        pass