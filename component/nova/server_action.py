#!/usr/bin/python
# Used manage nova server actions
# Refer to http://docs.openstack.org/api/openstack-compute/2/content/Server_Actions-d1e3229.html
# for all API information.

import sys
import json
import socket

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

class server_actions:
    #DESC:
    #INPUT:
    #OUTPUT:
    def __init__(self,user_dict):
        """
        DESC: Constructor to build out the tokens object
        INPUT: user_dict dictionary containing - built in auth.py
               username
               password
               project_id - could be blank
               token
               status_level
               user_level
               is_admin
               sec - optional - use HTTPS sec = TRUE defaults to FALSE
        """
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        else:
            self.username = user_dict['username']
            self.password = user_dict['password']
            self.project_id = user_dict['project_id']
            if((self.project_id == 'NULL') or (not user_dict['project_id'])):
                logger.sys_error("No project ID was specified in the condtructor")
                raise Exception("No project ID was specified in the condtructor")
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

            #Retrieve all default values from the DB????
            #Screw a config file????
            #get the default cloud controller info
            self.controller = config.CLOUD_CONTROLLER
            self.api_ip = config.API_IP
            #self.db = user_dict['db']

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        #if(self.adm_token == ''):
        #    logger.sys_error("No admin tokens passed.")
        #    raise Exception("No admin tokens passed.")
            #self.adm_token = config.ADMIN_TOKEN

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        #attach to the DB
        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def destructor(self):
        #close any open db connections
        self.db.close_connection()

    def reboot_server(self, server_id, action_type):
        """
        DESC: This operation enables you to complete either a soft or
        hard reboot of a specified server. With a soft reboot (SOFT),
        the operating system is signaled to restart, which allows for a
        graceful shutdown of all processes. A hard reboot (HARD) is the
        equivalent of power cycling the server
        INPUT: server_id, action_type
        OUTPUT: This operation does not return a response body
        ACCESS: Admin and authenticted users can use this operation
        NOTE:none
        """
        if(self.user_level <= 1):
            get_nets = {}
            if(self.is_admin == 1):
                get_nets = {'select':"net_name,net_id,proj_id",'from':"trans_network_settings"}
            else:
                get_nets = {'select':"net_name,net_id,proj_id",'from':"trans_network_settings",'where':"proj_id='%s'"%(self.project_id)}
    
            nets = self.db.pg_select(get_nets)
            r_array = []
            for net in nets:
                r_dict = {}
                r_dict['net_name'] = net[0]
                r_dict['net_id'] = net[1]
                r_dict['project_id'] = net[2]
                r_array.append(r_dict)
            return r_array
        
    def change_server_password(self,input_dict):
        """
        DESC: Change the administrative password on the virtual server.
        INPUT: input_dict - new_pass
                          - server_id
        OUTPUT: OK - success
                ERROR - failure
                NA - unknown
        ACCESS: Admins can chnage the admin password for any virtual server, power users
                can change passwords for virtual servers in their project
        NOTE:
        """
        #Use the thrans_instances table to get the virtual server info.
    
    def rebuild_server(self,input_dict):
        """
        DESC: The rebuild operation removes all data on the server and replaces it
              with the specified image
        INPUT: input_dict - server_name - req
                          - server_image_id - req
                          - server_admin_pass - req
                          - server_ip - op
                          - server_metadata - op
                          - server_personality - not used
        OUTPUT: OK - success
                ERROR - failure
                NA - unknown
        ACCESS: Admins can rebuild any server power users can only rebuild a server
                in their project.
        NOTE: Personalities are pushed to alpo.1
        """
    
    def resize_server(self,input_dict):
        """
        DESC: The resize operation converts an existing server to a different flavor, in essence,
              scaling the server up or down
        INPUT: input_dict - server_id
                          - flavor_id
        OUTPUT: OK - success
                ERROR - failure
                NA - unknow
        ACCESS: Only admins can resize a server.
        NOTE:
        """
        #After the server resize is completed confirm the resize so that the vm stabalizes at that size.
    
    def revert_resized_server(self,server_id):
        """
        DESC: Used to revert a resized server if there is an issue.
        INPUT: server_id
        OUTPUT: OK - success
                ERROR - failure
                NA - unknown
        ACCESS: Only admins can revert the server if there is an issue.
        NOTE: transcirrus db will have to be updated accordingly
        """

    def create_server_image():
        """
        DESC: Creates an image from a server.
        INPUT: create_dict - server_id
                           - image_name
        OUTPUT: OK - success
                ERROR - failure
                NA - unknown
        ACCESS: Admins can create an image of any server, power users can only
                create images of servers in their project.
        NOTE:
        """

#######reserved for alpo.1#######
#not needed for the prototype
#http://docs.openstack.org/api/openstack-network/2.0/content/Ports.html

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def list_net_ports():
        print "not implemented"

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def get_net_port():
        print "not implemented"

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def add_net_port():
        print "not implemented"

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def update_net_port():
        print "not implemented"

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def remove_net_port():
        print "not implemented"
