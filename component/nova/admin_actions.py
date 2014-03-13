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
from transcirrus.common.auth import get_token

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

    def pause_server(self,input_dict):
        """
        DESC: Pause a running virtual server. Pauseing saves vm state to memory.
        INPUT: input_dict - project_id
                         - instance_id
        OUTPUT: 'OK' - pass
                'ERROR' - fail
                'NA' - unknown
        ACCESS: Admins can pause an instance in the cloud.
        NOTES: This is not the same as suspend.
        """
        logger.sys_info('\n**Server action pause. Component: Nova Def: pause_server**\n')
        for key,value in input_dict.items():
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
            if(self.project_id != input_dict['project_id']):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
        # construct request header and body
            body='{"pause": null}'
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json", "Accept": "application/json", "X-Auth-Project-Id": "newproj"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (input_dict['project_id'],input_dict['instance_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        # check the response code
        except:
            logger.sys_error("Error in server pause request.")
            raise Exception("Error in server pause request")

        if(rest['response'] == 202):
                # this method does not return any response body
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
        else:
            util.http_codes(rest['response'],rest['reason'],rest['data'])

        return 'OK'

    def unpause_server(self,input_dict):
        """
        DESC: Unpause a running virtual server. Resume the virtual server from memory.
        INPUT: input_dict - project_id
                         - instance_id
        OUTPUT: 'OK' - pass
                'ERROR' - fail
                'NA' - unknown
        ACCESS: Admins can unpause an instance in the cloud.
        NOTES: This is not the same as resume.
        """
        logger.sys_info('\n**Server action unpause. Component: Nova Def: unpause_server**\n')
        for key,value in input_dict.items():
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
            if(self.project_id != input_dict['project_id']):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            # construct request header and body
            body='{"unpause": null}'
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (input_dict['project_id'],input_dict['instance_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            # check the response code
        except:
            logger.sys_error("Error in server unpause request.")
            raise Exception("Error in server unpause request")

        if(rest['response'] == 202):
                # this method does not return any response body
                logger.sys_info("Response %s with Reason %s Data: %s" % (rest['response'],rest['reason'],rest['data']))
        else:
            util.http_codes(rest['response'],rest['reason'],rest['data'])

        return 'OK'

    def suspend_server(self,input_dict):
        """
        DESC: Suspend a running virtual server. Suspending saves the vm state to disk.
        INPUT: input_dict - project_id
                         - instance_id
        OUTPUT: 'OK' - pass
                'ERROR' - fail
                'NA' - unknown
        ACCESS: Admins can suspend an instance in the cloud.
        NOTES: This is not the same as pause.
        """
        logger.sys_info('\n**Server action suspend. Component: Nova Def: suspend_server**\n')
        for key,value in input_dict.items():
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
            if(self.project_id != input_dict['project_id']):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            # construct request header and body
            body='{"suspend": null}'
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (input_dict['project_id'],input_dict['instance_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            # check the response code
        except:
            logger.sys_error("Error in server suspend request.")
            raise Exception("Error in server suspend request")

        if(rest['response'] == 202):
                # this method does not return any response body
                logger.sys_info("Response %s with Reason %s" % (rest['response'],rest['reason']))
        else:
            util.http_codes(rest['response'],rest['reason'])

        return 'OK'

    def resume_server(self,input_dict):
        """
        DESC: Resume a suspended server from disc.
        INPUT: input_dict - project_id
                         - instance_id
        OUTPUT: 'OK' - pass
                'ERROR' - fail
                'NA' - unknown
        ACCESS: Admins can resume an instance in the cloud.
        NOTES: This is not the same as unpause.
        """
        logger.sys_info('\n**Server action resume. Component: Nova Def: resume_server**\n')
        for key,value in input_dict.items():
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
            if(self.project_id != input_dict['project_id']):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            # construct request header and body
            body='{"resume": null}'
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (input_dict['project_id'],input_dict['instance_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            # check the response code
        except:
            logger.sys_error("Error in server resume request.")
            raise Exception("Error in server resume request")

        if(rest['response'] == 202):
                # this method does not return any response body
                logger.sys_info("Response %s with Reason %s" % (rest['response'],rest['reason']))
        else:
            util.http_codes(rest['response'],rest['reason'])

        return 'OK'

    def migrate_server(self,input_dict):
        """
        DESC: Migrate a server form one physical node to another. This requires the server
              to be powered down.
        INPUT: input_dict - project_id
                         - instance_id
        OUTPUT: 'OK' - pass
                'ERROR' - fail
                'NA' - unknown
        ACCESS: ONLY the admin can migrate an instance
        NOTES: This is not the same as the live_migration function
        """
        for key,value in input_dict.items():
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
            if(self.project_id != input_dict['project_id']):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
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
        for key,value in input_dict.items():
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
            if(self.project_id != input_dict['project_id']):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
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

    def evacuate_server(self,input_dict):
        """
        DESC: Resume a suspended server from disc.
        INPUT: input_dict - project_id
                          - instance_id
                          - openstack_host_id
        OUTPUT: 'OK' - pass
                'ERROR' - fail
                'NA' - unknown
        ACCESS: Admins can resume an instance in the cloud.
        NOTES: This is not the same as unpause.
        """
        logger.sys_info('\n**Server action evacuate. Component: Nova Def: evacuate_server**\n')
        for key,value in input_dict.items():
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
            if(self.project_id != input_dict['project_id']):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            # construct request header and body
            body='{"evacuate": {"host": "%s","onSharedStorage": "True"}}'%(input_dict['openstack_host_id'])
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (input_dict['project_id'],input_dict['instance_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            # check the response code
        except:
            logger.sys_error("Error in server evacuation request.")
            raise Exception("Error in server evacuation request")

        if(rest['response'] == 202):
                # this method does not return any response body
                logger.sys_info("Response %s with Reason %s" % (rest['response'],rest['reason']))
        else:
            util.http_codes(rest['response'],rest['reason'],rest['data'])

        return 'OK'

    def list_compute_hosts(self,input_dict):
        """
        http://docs.openstack.org/api/openstack-compute/2/content/GET_os-hosts-v2_listHosts_v2__tenant_id__os-hosts_ext-os-hosts.html
        DESC: Get the openstack compute hosts in the cloud.
        INPUT: input_dict - project_id
                          - zone
        OUTPUT: array of r_dict - zone
                                - host_name
                                - service
        ACCESS: ONLY the admin can migrate an instance
        NOTES: This is not the same as the transcirrus node ids. These are uuids assigend
                by Nova, Compute host zone is set to nova by default.
        """
        logger.sys_info('\n**Listing physical compute hosts. Component: Nova Def: list_compute_hosts**\n')
        for key,value in input_dict.items():
            if(key == 'zone'):
                continue
            if(key == ''):
                logger.sys_error('Reguired value not passed.')
                raise Exception('Reguired value not passed.')
            if(value == ''):
                logger.sys_error('Reguired value not passed.')
                raise Exception('Reguired value not passed.')

        if(self.is_admin == 1):
            if('zone' not in input_dict):
                input_dict['zone'] = 'nova'
    
            # Create an API connection with the Admin
            try:
                # build an API connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                if(self.project_id != input_dict['project_id']):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")
    
            try:
            # construct request header and body
                body=''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'GET'
                api_path = '/v2/%s/os-hosts?zone=%s&service=compute' % (input_dict['project_id'],input_dict['zone'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sys_error("Error in sending list compute hosts request.")
                raise Exception("Error in sending list compute request")
    
            if(rest['response'] == 200):
                    # this method does not return any response body
                    logger.sys_info("Response %s with Reason %s Data: %s" % (rest['response'],rest['reason'],rest['data']))
                    load = json.loads(rest['data'])
                    return load['hosts']
            else:
                util.http_codes(rest['response'],rest['reason'],rest['data'])

    def get_os_host(self,input_dict):
        """
        DESC: Get the detailed info on an OpenStack host.
        INPUT: input_dict - project_id
                          - host_name
        OUTPUT: array of dict - project resources
        ACCESS: ONLY the admin can get the the host.
        NOTES:
        """
        logger.sys_info('\n**Getting physical host. Component: Nova Def: get_os_hosts**\n')
        for key,value in input_dict.items():
            if(key == ''):
                logger.sys_error('Reguired value not passed.')
                raise Exception('Reguired value not passed.')
            if(value == ''):
                logger.sys_error('Reguired value not passed.')
                raise Exception('Reguired value not passed.')

        if(self.is_admin == 1):
            if('zone' not in input_dict):
                input_dict['zone'] = 'nova'

            # Create an API connection with the Admin
            try:
                # build an API connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                if(self.project_id != input_dict['project_id']):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")
    
            try:
            # construct request header and body
                body=''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'GET'
                api_path = '/v2/%s/os-hosts/%s' % (input_dict['project_id'],input_dict['host_name'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sys_error("Error getting OpenStack host.")
                raise Exception("Error getting OpenStack host.")
    
            if(rest['response'] == 200):
                    # this method does not return any response body
                    logger.sys_info("Response %s with Reason %s Data: %s" % (rest['response'],rest['reason'],rest['data']))
                    load = json.loads(rest['data'])
                    return load['host']
            else:
                util.http_codes(rest['response'],rest['reason'],rest['data'])