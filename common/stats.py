#!/usr/bin/python2.7

import os
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.util as util
import transcirrus.common.node_util as node_util
import transcirrus.common.config as config

class stat_ops:

    def __init__(self,user_dict):
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
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
            self.user_id = user_dict['user_id']

            if(self.is_admin == 1):
                self.adm_token = user_dict['adm_token']
            else:
                self.adm_token = 'NULL'

            if 'sec' in user_dict:
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'
                
            #get the database connection
            self.db = util.db_connect()

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

    def get_num_project(self):
        """
        DESC: Get the number of projects that are active in the cloud
        INPUT: None
        OUTPUT: num_of_projects
        ACCESS: Admin only
        NOTES: Only return a number
        """
        #check if admin
        if(self.is_admin == 0):
            logger.sys_error("Stats are admin-only.")
            raise Exception("Stats are admin-only.")
        else:            
            proj_dict = {'table':'trans_user_projects'}
            num_proj = self.db.count_elements(proj_dict)
            return num_proj
    
    def get_total_cloud_memory(self):
        """
        DESC: Get the total amount of memory in the cloud.
        INPUT: None
        OUTPUT: total_memory
        ACCESS: Admin only
        NOTES: Only return a number. Must account for core and all compute.
        """
        pass
    
    def get_total_cloud_storage(self):
        """
        DESC: Get the total cloud storage, broken out by SSD and Spindle
        INPUT: None
        OUTPUT: r_array - ssd_total
                        - spindle_total
        ACCESS: Admin only
        NOTES: Returns an array with total ssd and spindle storage in the cloud
        """
        pass
    
    def get_num_servers(self,project_id = None):
        """
        DESC: Get the total servers by project
        INPUT: None
        OUTPUT: total_num_servers
        ACCESS: Admin can get number of servers in any project
                PU number of servers in the project
                User number of servers they own
        NOTES: Returns a number
        """
        pass
    
    def get_total_cloud_servers(self):
        """
        DESC: Get the total servers in the cloud environment
        INPUT: None
        OUTPUT: total_num_servers
        ACCESS: Admin can get number of servers in the cloud
                PU none
                User none
        NOTES: Returns a number
        """
        pass
    
    def get_num_int_networks(self,project_id = None):
        """
        DESC: Get the total networks by project
        INPUT: None
        OUTPUT: total_num_nets
        ACCESS: Admin can get number of nets in any project
                PU number of nets in the project
                User number of nets they own
        NOTES: Returns a number
        """
        pass
    
    def get_num_ext_networks(self,project_id = None):
        """
        DESC: Get the total ext networks by project
        INPUT: None
        OUTPUT: total_num_servers
        ACCESS: Admin can get number of nets in any project
                PU number of nets in the project
                User none
        NOTES: Returns a number, also counts the default external network. So, in effect all projcts
               have at least 1 external network.
        """
        pass
    
    def get_num_users(self,project_id = None):
        """
        DESC: Get the total users for each project
        INPUT: None
        OUTPUT: total_num_users
        ACCESS: Admin can get number of users in any project
                PU number of users in the project
                User none
        NOTES: Returns a number
        """
        pass
    
    def get_total_cloud_users(self):
        """
        DESC: Get the total users in the cloud environment
        INPUT: None
        OUTPUT: total_num_users
        ACCESS: Admin can get number of users in the cloud
                PU none
                User none
        NOTES: Returns a number
        """
        pass
    
    def get_num_volumes(self,project_id = None):
        """
        DESC: Get the total volumes for each project
        INPUT: None
        OUTPUT: total_num_volumes
        ACCESS: Admin can get number of volumes in any project
                PU number of volumes in the project
                User none
        NOTES: Returns a number
        """
        pass
    
    def get_total_cloud_volumes(self):
        """
        DESC: Get the total volumes in the cloud environment
        INPUT: None
        OUTPUT: total_num_volumes
        ACCESS: Admin can get number of volumes in the cloud
                PU none
                User none
        NOTES: Returns a number
        """
        pass
    
    def get_volumes_attached(self,project_id = None):
        """
        DESC: Get the total volumes attached to servers
        INPUT: None
        OUTPUT: r_array - server_name
                        - num_volumes
        ACCESS: Admin can get volumes attached for any project
                PU none
                User none
        NOTES: Returns an array
        """
        pass
    
    def get_num_containers(self,project_id = None):
        """
        DESC: Get the number of containers in a project
        INPUT: None
        OUTPUT: num_of_containers
        ACCESS: Admin can get containers in project
                PU none
                User none
        NOTES: Returns a number
        """
        pass
    
    def get_volume_stats(self, project_id = None):
        """
        DESC: Get the amount of sapce used in a volume
        INPUT: None
        OUTPUT: r_array - total_size
                        - used
                        - free
        ACCESS: Admin can get vol stats in project or volume
                PU can get vol stats in project
                User can get vol stats for volumes they own
        NOTES: Returns an array
        """
        pass

