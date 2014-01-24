#!/usr/bin/python
# Used manage nova server actions
# Refer to http://docs.openstack.org/api/openstack-compute/2/content/Server_Actions-d1e3229.html
# for all API information.

#need to implement AMQP queing on this

import sys
import json
import socket

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.component.nova.flavor import flavor_ops
from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

class server_admin_actions:
    #UPDATED and Unit tested
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
            self.user_id = user_dict['user_id']

            if(self.is_admin == 1):
                self.adm_token = user_dict['adm_token']
            else:
                logger.sys_error("User is not an admin.")
                raise Exception("User is not an admin.")

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

        def pause_server(self):
            pass
        #alpo.1
        
        def unpause_server(self):
            pass
        #alpo.1
        
        def suspend_server(self):
            pass
        #alpo.1
        
        def resume_server(self):
            pass
        #alpo.1
        
        def migrate_server(self,input_dict):
            """
            DESC: Migrate a server form one physical node to another. This requires the server
                  to be powered down.
            INPUT: inpu_dict - project_id
                             - instance_id
            OUTPUT: 'OK' - pass
                    'ERROR' - fail
                    'NA' - unknown
            ACCESS: ONLY the admin can migrate an instance
            NOTES: This is not the same as the live_migration function
            """
            for key,value in input_dict:
                if(key == ''):
                    logger.sys_error('Reguired value not passed.')
                    raise Exception('Reguired value not passed.')
                if(value == ''):
                    logger.sys_error('Reguired value not passed.')
                    raise Exception('Reguired value not passed.')

            # Create an API connection with the Admin
            try:
                # build an API connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")
    
            try:
                # construct request header and body
                body='{"migrate": null}'
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2/%s/servers/%s/action' % (input_dict['project_id'],input_dict['instance_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
                # check the response code
            except:
                logger.sys_error("Error in sending migrate request.")
                raise Exception("Error in sending migrate request")
    
            if(rest['response'] == 202):
                    # this method does not return any response body
                    logger.sys_info("Response %s with Reason %s" % (rest['response'],rest['reason']))
            else:
                util.http_codes(rest['response'],rest['reason'])

            return 'OK'
        
        def live_migrate_server(self,input_dict):
            """
            http://docs.openstack.org/api/openstack-compute/2/content/POST_os-admin-actions-v2_os-migrateLive_v2__tenant_id__servers__server_id__action_ext-action.html
            DESC: Migrate a server form one physical node to another. Server does not need to be rebooted.
            INPUT: inpu_dict - project_id
                             - instance_id
                             - openstack_host_id
            OUTPUT: 'OK' - pass
                    'ERROR' - fail
                    'NA' - unknown
            ACCESS: ONLY the admin can migrate an instance
            NOTES: This is not the same as the migration function
            """
            for key,value in input_dict:
                if(key == ''):
                    logger.sys_error('Reguired value not passed.')
                    raise Exception('Reguired value not passed.')
                if(value == ''):
                    logger.sys_error('Reguired value not passed.')
                    raise Exception('Reguired value not passed.')

            # Create an API connection with the Admin
            try:
                # build an API connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")
    
            try:
                # construct request header and body
                body='{"os-migrateLive": {"host": "%s","block_migration": "false", "disk_over_commit": "false"}}'%(openstack_host_id)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2/%s/servers/%s/action' % (input_dict['project_id'],input_dict['instance_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
                # check the response code
            except:
                logger.sys_error("Error in sending live migrate request.")
                raise Exception("Error in sending live migrate request")
    
            if(rest['response'] == 202):
                    # this method does not return any response body
                    logger.sys_info("Response %s with Reason %s" % (rest['response'],rest['reason']))
            else:
                util.http_codes(rest['response'],rest['reason'])

            return 'OK'

        def evacuate_server(self):
            pass
        
        def list_compute_hosts(self,project_id):
            """
            http://docs.openstack.org/api/openstack-compute/2/content/GET_os-hosts-v2_listHosts_v2__tenant_id__os-hosts_ext-os-hosts.html
            DESC: Get the openstack (nova) compute host ids based on the project_id.
            INPUT: project_id
            OUTPUT: array of r_dict - compute_host_name
                                    - os_host_id
            ACCESS: ONLY the admin can migrate an instance
            NOTES: This is not the same as the transcirrus node ids. These are uuids assigend
                    by Nova
            """
            if(project_id == ''):
                logger.sys_error('No project_id spcified, can not get nova compute hosts')
                raise Exception('No project_id spcified, can not get nova compute hosts')
            
            # Create an API connection with the Admin
            try:
                # build an API connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")
    
            try:
                # construct request header and body
                body=''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2/%s/os-hosts?={compute}' % (project_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
                # check the response code
            except:
                logger.sys_error("Error in sending list compute hosts request.")
                raise Exception("Error in sending list compute request")
    
            if(rest['response'] == 202):
                    # this method does not return any response body
                    logger.sys_info("Response %s with Reason %s" % (rest['response'],rest['reason']))
            else:
                util.http_codes(rest['response'],rest['reason'])

            return 'OK'
