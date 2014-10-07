#!/usr/local/bin/python2.7
#######standard impots#######
import sys
import json
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token

from transcirrus.database.postgres import pgsql

#######Special imports#######

class quota_ops:
    #UPDATED/UNIT TESTED
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
            self.user_id = user_dict['user_id']
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
            
            if('sec' in user_dict):
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
        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))


    def show_project_quotas(self,project_id=None):
        """
        DESC: Get the quotas that are set on a project
        INPUT: project_id - op
        OUTPUT: r_dict - id
                       - cores
                       - fixed_ips
                       - floating_ips
                       - injected_file_content_bytes
                       - injected_file_path_bytes
                       - injected_files
                       - instances
                       - key_pairs
                       - metadata_items
                       - ram(in megabytes)
                       - security_group_rules
                       - storage(in gigabytes)
                       - snapshots
                       - volumes
        ACCESS: Admins can list quotas for any project
                Power users can list the quotas for the project they belong to
                Users can list the quotas for the project they belong to
        NOTE: We are combining the Cinder and Nova quota API calls. If the project id is
              not given then the users project id will be used.
        """
    def show_user_quoatas(self, input_dict):
        """
        DESC: Get the quotas that are set on a specific user in a project
        INPUT: project_id - op
               user_id - op
        OUTPUT: r_dict - id
                       - cores
                       - fixed_ips
                       - floating_ips
                       - injected_file_content_bytes
                       - injected_file_path_bytes
                       - injected_files
                       - instances
                       - key_pairs
                       - metadata_items
                       - ram(in megabytes)
                       - security_group_rules
                       - storage(in gigabytes)
                       - snapshots
                       - volumes
        ACCESS: Admins can list quotas for any project
                Power users can list the quotas for the project they belong to
                Users can list the quotas for the project they belong to
        NOTE: We are combining the Cinder and Nova quota API calls. If the project id or user id is
              not given then the users project id  and user id will be used.
        """
    def update_project_quotas(self,input_dict):
        """
        DESC: Get the quotas that are set on a specific user in a project
        INPUT: project_id - op
               user_id - op
        OUTPUT: r_dict - id
                       - cores
                       - fixed_ips
                       - floating_ips
                       - injected_file_content_bytes
                       - injected_file_path_bytes
                       - injected_files
                       - instances
                       - key_pairs
                       - metadata_items
                       - ram(in megabytes)
                       - security_group_rules
                       - storage(in gigabytes)
                       - snapshots
                       - volumes
        ACCESS: Admins can list quotas for any project
                Power users can list the quotas for the project they belong to
                Users can list the quotas for the project they belong to
        NOTE: We are combining the Cinder and Nova quota API calls. If the project id or user id is
              not given then the users project id  and user id will be used.
        """
    def update_user_quotas(self):
        """
        DESC: Get the quotas that are set on a specific user in a project
        INPUT: project_id - op
               user_id - op
        OUTPUT: r_dict - id
                       - cores
                       - fixed_ips
                       - floating_ips
                       - injected_file_content_bytes
                       - injected_file_path_bytes
                       - injected_files
                       - instances
                       - key_pairs
                       - metadata_items
                       - ram(in megabytes)
                       - security_group_rules
                       - storage(in gigabytes)
                       - snapshots
                       - volumes
        ACCESS: Admins can list quotas for any project
                Power users can list the quotas for the project they belong to
                Users can list the quotas for the project they belong to
        NOTE: We are combining the Cinder and Nova quota API calls. If the project id or user id is
              not given then the users project id  and user id will be used.
        """
    def delete_project_quota(self):
        #admin
        pass
    def delete_user_quota(self):
        #admin
        pass
    def get_default_project_quotas(self):
        #all
        pass
    def get_default_user_quotas(self):
        #all
        pass