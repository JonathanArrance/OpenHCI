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
        if (action_type == ''):
            logger.sys_error("No action_type was specified.")
            raise Exception("No action_type was specified.")
        if (server_id == ''):
            logger.sys_error("No server id was specified.")
            raise Exception("No server id was specified.")


        # check if the server_id is in the power user project: TODO

        if(self.user_level <= 1):
            # Create an API connection with the Admin
            try:
                # build an API connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                # construct request header and body
                body='{"reboot":{"type": "%s"}}' % (action_type)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2.0/servers/%s/action' % (server_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'35357'}
                rest = api.call_rest(rest_dict)

                # check the response code
                if(rest['response'] == 202):
                    # this method does not return any response body
                    logger.sys_info("Response %s with Reason %s" % (rest['response'],rest['reason']))
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except:
                logger.sys_logger("Error in sending reboot request.")
                raise Exception("Error in sending reboot request")
        else:
            logger.sys_error("Only an admin or a power user can reboot the server.")
            raise Exception("Only an admin or a power user can reboot the server.")


    def resize_server(self, server_id, server_name, flavor_id):
        """
        DESC:The resize operation converts an existing server to a
        different flavor, in essence, scaling the server up or down. The
        original server is saved for a period of time to allow rollback
        if a problem occurs. You should test and explicitly confirm all
        resizes. When you confirm a resize, the original server is
        removed. All resizes are automatically confirmed after 24 hours
        if you do not explicitly confirm or revert them.
        INPUT: server_id, flavor_id
        OUTPUT: This operation does not return a response body
        ACCESS: Admin and authenticted users can use this operation
        NOTE:none
        """
        if (server_id == ''):
            logger.sys_error("No server_id was provided")
            raise Exception("No server_id was provided")
        if (flavor_id == ''):
            logger.sys_error("No flavor_id was provided")
            raise Exception("No flavor_id was provided")
        if (server_name == ''):
            logger.sys_error("No server name was provided.")
            raise Exception("No server name was provided.")

        if(self.user_level <= 1):
            # Create an API connection with the Admin
            try:
                # build an API connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                # construct request header and body
                body='{"resize": {"name": "%s", "flavorRef": "%s"}}' % (server_name, flavor_id)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2.0/servers/%s/action' % (server_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'35357'}
                rest = api.call_rest(rest_dict)

                # check the response code
                if(rest['response'] == 202):
                    # this method does not return any response body
                    logger.sys_info("Response %s with Reason %s" % (rest['response'],rest['reason']))
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except:
                logger.sys_logger("Error in sending resize request to server.")
                raise Exception("Error in sending resize request to server.")
        else:
            logger.sys_error("Only an admin or a power user can resize the server.")
            raise Exception("Only an admin or a power user can resize the server.")



    def confirm_resize(self, server_id):
        """
        During a resize operation, the original server is saved for a
        period of time to allow roll back if a problem exists. Once the
        newly resized server is tested and has been confirmed to be
        functioning properly, use this operation to confirm the resize.
        After confirmation, the original server is removed and cannot be
        rolled back to. All resizes are automatically confirmed after 24
        hours if they are not explicitly confirmed or reverted
        INPUT: server_id
        OUTPUT: This operation does not return a response body.
        ACCESS: Admin and authenticated users can use this operation
        NOTE: none
        """

        if (server_id == ''):
            logger.sys_error("No server id was provided.")
            raise Exception("No server id was provided.")

        if(self.user_level <= 1):
            # Create an API connection with the Admin
            try:
                # build an API connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")


            try:
                # construct request header and body
                body='{"confirmResize": "null"}'
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2.0/servers/%s/action' % (server_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'35357'}
                rest = api.call_rest(rest_dict)

                # check the response code
                if(rest['response'] == 204):
                    # this method does not return any response body
                    logger.sys_info("Response %s with Reason %s" % (rest['response'],rest['reason']))
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except:
                logger.sys_logger("Error in sending resize confirm request to server.")
                raise Exception("Error in sending resize confirm request to server.")
        else:
            logger.sys_error("Only an admin or a power user can confirm resize the server.")
            raise Exception("Only an admin or a power user can confirm resize the server.")



    def revert_resize(self, server_id):
        """
        During a resize operation, the original server is saved for a
        period of time to allow for roll back if a problem occurs. If
        the resized server has a problem, use the revert resize
        operation to revert the resize and roll back to the original
        server. All resizes are automatically confirmed after 24 hours
        if you do not confirm or revert them.
        INPUT: server_id
        OUTPUT: This operation does not return a response body.
        ACCESS: Admin and authenticated users can use this operation
        NOTE: none
        """

        if (server_id == ''):
            logger.sys_error("No server id was passed.")
            raise Exception("No server id was passed.")


        if(self.user_level <= 1):
            # Create an API connection with the Admin
            try:
                # build an API connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                # construct request header and body
                body='{"revertResize": "null"}'
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2.0/servers/%s/action' % (server_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'35357'}
                rest = api.call_rest(rest_dict)

                # check the response code
                if(rest['response'] == 202):
                    # this method does not return any response body
                    logger.sys_info("Response %s with Reason %s" % (rest['response'],rest['reason']))
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except:
                logger.sys_logger("Error in sending revert resize request to server.")
                raise Exception("Error in sending revert resize request to server.")
        else:
            logger.sys_error("Only an admin or a power user can revert resize request to the server.")
            raise Exception("Only an admin or a power user can revert resize request to the server.")

