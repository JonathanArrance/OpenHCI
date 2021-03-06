#!/usr/bin/python
# Used manage nova server actions
# Refer to http://docs.openstack.org/api/openstack-compute/2/content/Server_Actions-d1e3229.html
# for all API information.

#need to implement AMQP queing on this

import sys
import json
import socket
import time
import datetime

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.component.nova.flavor import flavor_ops
from transcirrus.component.glance.glance_ops_v2 import glance_ops
from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token
from transcirrus.database.postgres import pgsql
import transcirrus.component.nova.error as nova_ec

class server_actions:
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
        reload(config)
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
                self.adm_token = 'NULL'

            if 'sec' in user_dict:
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'

            self.controller = config.CLOUD_CONTROLLER
            self.api_ip = config.API_IP

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

        self.flavor = flavor_ops(user_dict)
        self.datetime = datetime.date.today()
        self.glance = glance_ops(user_dict)

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def destructor(self):
        #close any open db connections
        self.db.close_connection()

    def pause_server(self,input_dict):
        """
        DESC: Pause a running virtual server. Pauseing saves vm state to memory.
        INPUT: input_dict - project_id
                         - instance_id
        OUTPUT: 'OK' - pass
                'ERROR' - fail
                'NA' - unknown
        ACCESS: Users can pause an instance in the cloud based on user_level.
        NOTES: This is not the same as suspend.
        """
        logger.sys_info('\n**Server action pause. Component: Nova Def: pause_server**\n')
        for key,value in input_dict.items():
            if(key == ''):
                logger.sys_error('Required value not passed.')
                raise Exception('Required value not passed.')
            if(value == ''):
                logger.sys_error('Required value not passed.')
                raise Exception('Required value not passed.')

        if(self.is_admin == 0):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error("Users can only pause virtual servers in their project.")
                raise Exception("Users can only pause virtual servers in their project.")

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
            #util.http_codes(rest['response'],rest['reason'],rest['data'])
            nova_ec.error_codes(rest)

        return 'OK'

    def unpause_server(self,input_dict):
        """
        DESC: Unpause a running virtual server. Resume the virtual server from memory.
        INPUT: input_dict - project_id
                         - instance_id
        OUTPUT: 'OK' - pass
                'ERROR' - fail
                'NA' - unknown
        ACCESS: Users can unpause an instance in the cloud based on user_level.
        NOTES: This is not the same as resume.
        """
        logger.sys_info('\n**Server action unpause. Component: Nova Def: unpause_server**\n')
        for key,value in input_dict.items():
            if(key == ''):
                logger.sys_error('Required value not passed.')
                raise Exception('Required value not passed.')
            if(value == ''):
                logger.sys_error('Required value not passed.')
                raise Exception('Required value not passed.')

        if(self.is_admin == 0):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error("Users can only unpause virtual servers in their project.")
                raise Exception("Users can only unpause virtual servers in their project.")

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
            #util.http_codes(rest['response'],rest['reason'],rest['data'])
            nova_ec.error_codes(rest)

        return 'OK'

    def suspend_server(self,input_dict):
        """
        DESC: Suspend a running virtual server. Suspending saves the vm state to disk.
        INPUT: input_dict - project_id
                         - instance_id
        OUTPUT: 'OK' - pass
                'ERROR' - fail
                'NA' - unknown
        ACCESS: Users can suspend an instance in the cloud based on user_level.
        NOTES: This is not the same as pause.
        """
        logger.sys_info('\n**Server action suspend. Component: Nova Def: suspend_server**\n')
        for key,value in input_dict.items():
            if(key == ''):
                logger.sys_error('Required value not passed.')
                raise Exception('Required value not passed.')
            if(value == ''):
                logger.sys_error('Required value not passed.')
                raise Exception('Required value not passed.')

        if(self.is_admin == 0):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error("Users can only suspend virtual servers in their project.")
                raise Exception("Users can only suspend virtual servers in their project.")

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
            #util.http_codes(rest['response'],rest['reason'])
            nova_ec.error_codes(rest)

        return 'OK'


    def resume_server(self,input_dict):
        """
        DESC: Resume a suspended server from disc.
        INPUT: input_dict - project_id
                         - instance_id
        OUTPUT: 'OK' - pass
                'ERROR' - fail
                'NA' - unknown
        ACCESS: Users can resume an instance in the cloud based on user_level.
        NOTES: This is not the same as unpause.
        """
        logger.sys_info('\n**Server action resume. Component: Nova Def: resume_server**\n')
        for key,value in input_dict.items():
            if(key == ''):
                logger.sys_error('Required value not passed.')
                raise Exception('Required value not passed.')
            if(value == ''):
                logger.sys_error('Required value not passed.')
                raise Exception('Required value not passed.')

        if(self.is_admin == 0):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error("Users can only resume virtual servers in their project.")
                raise Exception("Users can only resume virtual servers in their project.")

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
            #util.http_codes(rest['response'],rest['reason'])
            nova_ec.error_codes(rest)

        return 'OK'


    def server_power_control(self,input_dict):
        """
        DESC: Power on or off an instance
        INPUT: input_dict - server_id - req
                          - project_id - req
                          - power_state on/off - req
        OUTPUT: This operation does not return a response body.
        ACCESS: Admins can do power operations on any instance
                power users can do power operations on instances in their project
                user can do power operations on instances they own.
        NOTE: none
        """

        if ((input_dict['server_id'] == '') or ('server_id' not in input_dict)):
            logger.sys_error("No server id was provided.")
            raise Exception("No server id was provided.")
        if ((input_dict['project_id'] == '') or ('project_id' not in input_dict)):
            logger.sys_error("No project id was provided.")
            raise Exception("No project id was provided.")
        if ((input_dict['power_state'] == '') or ('power_state' not in input_dict)):
            logger.sys_error("No power state was provided.")
            raise Exception("No power state was provided.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(input_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        state = input_dict['power_state'].lower()
        flag = None
        if(state == 'on'):
            flag = 1
        elif(state == 'off'):
            flag = 0
        else:
            logger.sys_error('Invalid power state given.')
            raise Exception('Invalid power state given.')

        if(self.is_admin == 0):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error("Users can only power on/off virtual servers in their project.")
                raise Exception("Users can only power on/off virtual servers in their project.")

        #check to make sure non admins can perofrm the task
        if(self.is_admin == 0):
            self.get_server = None
            if(self.user_level == 1):
                self.get_server = {'select':'inst_name','from':'trans_instances','where':"proj_id='%s'"%(input_dict['project_id'])}
            elif(self.user_level == 2):
                self.get_server = {'select':'inst_name','from':'trans_instances','where':"proj_id='%s'"%(input_dict['project_id']),'and':"inst_user_id='%s'"%(self.user_id)}
            server = self.db.pg_select(self.get_server)
            if(server[0][0] == ''):
                logger.sys_error('The current user can not perform server power control operation.')
                raise Exception('The current user can not perform server power control operation.')

        # Create an API connection with the Admin
        try:
            # build an API connection for the admin user
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(input_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            # construct request header and body
            if(flag == 0):
                self.body='{"os-stop": null}'
                self.state = 'SHUTOFF'
            elif(flag == 1):
                self.body='{"os-start": null}'
                self.state = 'ACTIVE'
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (input_dict['project_id'],input_dict['server_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": self.body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            # check the response code
        except Exception as e:
            self.db.pg_transaction_rollback()
            raise e

        if(rest['response'] == 202):
            while(True):
                status = self._check_status(input_dict['project_id'],input_dict['server_id'])
                if(status['server_status'] == '%s'%(self.state)):
                    logger.sys_info('Active server with ID %s.'%(input_dict['server_id']))
                    break
                elif(status['server_status'] == 'ERROR'):
                    logger.sys_info('Server with ID %s failed to power cycle.'%(input_dict['server_id']))
                    raise Exception("Could not create a new server. ERROR: 555")
                time.sleep(2)
        else:
            nova_ec.error_codes(rest)

        return 'OK'

    def power_on_server(self,input_dict):
        """
        DESC: Power on a virtual server
        INPUT: input_dict - server_id - req
                          - project_id - req
        OUTPUT: OK - success
                error - fail
        ACCESS: Admins can do power operations on any instance
                power users can do power operations on instances in their project
                user can do power operations on instances they own.
        NOTE: none
        """
        input_dict['power_state'] = 'on'
        out = self.server_power_control(input_dict)
        return out

    def power_off_server(self,input_dict):
        """
        DESC: Power off a virtual server
        INPUT: input_dict - server_id - req
                          - project_id - req
        OUTPUT: This operation does not return a response body.
        ACCESS: Admins can do power operations on any instance
                power users can do power operations on instances in their project
                user can do power operations on instances they own.
        NOTE: none
        """
        input_dict['power_state'] = 'off'
        out = self.server_power_control(input_dict)
        return out

    def power_cycle_server(self,input_dict):
        """
        DESC: Power off a virtual server
        INPUT: input_dict - server_id - req
                          - project_id - req
        OUTPUT: This operation does not return a response body.
        ACCESS: Admins can do power operations on any instance
                power users can do power operations on instances in their project
                user can do power operations on instances they own.
        NOTE: none
        """
        status = self._check_status(input_dict['project_id'],input_dict['server_id'])
        if(status['server_status'] == 'ACTIVE'):
            input_dict['power_state'] = 'off'
            self.server_power_control(input_dict)
            input_dict['power_state'] = 'on'
            out = self.server_power_control(input_dict)
            return out
        elif(status['server_status'] == 'SHUTOFF'):
            input_dict['power_state'] = 'on'
            out = self.server_power_control(input_dict)
            return out

    def reboot_server(self, input_dict):
        """
        DESC: This operation enables you to complete either a soft or
              hard reboot of a specified server(vm). With a soft reboot (SOFT),
              the operating system is signaled to restart, which allows for a
              graceful shutdown of all processes. A hard reboot (HARD) is the
              equivalent of power cycling the server
        INPUT: input_dict - server_id
                          - project_id
                          - action_type SOFT/HARD
        OUTPUT: OK - success
                ERROR - fail
        ACCESS: Admin and power users can reboot any instace in the project
                users can only reboot servers in their project they own.
                
        NOTE:Need to implement user estriction - pushed to alpo.1
        """
        logger.sys_info('\n**Server action reboot. Component: Nova Def: reboot_server**\n')
        if ((input_dict['action_type'] == '') or ('action_type' not in input_dict)):
            logger.sys_error("No action_type was specified.")
            raise Exception("No action_type was specified.")
        if ((input_dict['server_id'] == '') or ('server_id' not in input_dict)):
            logger.sys_error("No server id was specified.")
            raise Exception("No server id was specified.")
        if ((input_dict['project_id'] == '') or ('project_id' not in input_dict)):
            logger.sys_error("No project id was specified.")
            raise Exception("No project id was specified.")

        if(input_dict['action_type'].upper() == 'SOFT'):
            logger.sys_info("Soft reboot specified for %s"%(input_dict['server_id']))
        elif(input_dict['action_type'].upper() == 'HARD'):
            logger.sys_info("Hard reboot specified for %s"%(input_dict['server_id']))
        else:
            logger.sys_error("Invalid action_type was specified.")
            raise Exception("Invalid action_type was specified.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(input_dict['project_id'])}
            if(input_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error("Users can only reboot virtual servers in their project.")
                raise Exception("Users can only reboot virtual servers in their project.")

        # check if the server_id is in the power user project: TODO
        if(self.is_admin == 0):
            get_server = {'select':'inst_id','from':'trans_instances','where':"proj_id='%s'"%(input_dict['project_id']),'and':"inst_user_id='%s'"%(self.user_id)}
            server = self.db.pg_select(get_server)
            if(server[0][0] == ''):
                logger.sys_error("The virtual server instance cannot be rebooted.")
                raise Exception("The virtual server instance cannot be rebooted.")

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
            body='{"reboot":{"type": "%s"}}' % (input_dict['action_type'].upper())
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (input_dict['project_id'],input_dict['server_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            # check the response code
        except:
            logger.sys_error("Error in sending reboot request.")
            raise Exception("Error in sending reboot request")

        if(rest['response'] == 202):
                # this method does not return any response body
                logger.sys_info("Response %s with Reason %s" % (rest['response'],rest['reason']))
        else:
            #util.http_codes(rest['response'],rest['reason'])
            nova_ec.error_codes(rest)

        return 'OK'

    def resize_server(self, input_dict):
        """
        DESC:The resize operation converts an existing server to a
             different flavor, in essence, scaling the server up or down. The
             original server is saved for a period of time to allow rollback
             if a problem occurs. You should test and explicitly confirm all
             resizes. When you confirm a resize, the original server is
             removed. All resizes are automatically confirmed after 24 hours
             if you do not explicitly confirm or revert them.
        INPUT: input_dict - server_id
                          - project_id
                          - flavor_id
        OUTPUT: OK - success
                ERROR - failure
        ACCESS: Only Admins and power users can perform this task.
        NOTE:none
        """
        logger.sys_info('\n**Server action resize. Component: Nova Def: resize_server**\n')
        if ((input_dict['server_id'] == '') or ('server_id' not in input_dict)):
            logger.sys_error("No server_id was provided")
            raise Exception("No server_id was provided")
        if ((input_dict['flavor_id'] == '') or ('flavor_id' not in input_dict)):
            logger.sys_error("No flavor_id was provided")
            raise Exception("No flavor_id was provided")
        if ((input_dict['project_id'] == '') or ('project_id' not in input_dict)):
            logger.sys_error("No project_id was provided")
            raise Exception("No project_id was provided")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(input_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error("Users can only reboot virtual servers in their project.")
                raise Exception("Users can only reboot virtual servers in their project.")
        
        #Make it so all users can resize an instance
        #if(self.user_level <= 1):
        #see if the server in the users tenant
        if(self.user_level >= 1):
            try:
                get_server = {'select':'inst_id,inst_flav_name','from':'trans_instances','where':"proj_id='%s'"%(input_dict['project_id']),'and':"inst_user_id='%s'"%(self.user_id)}
                server = self.db.pg_select(get_server)
            except:
                logger.sys_error("The virtual server instance cannot be resized.")
                raise Exception("The virtual server instance cannot be resized.")

        #get the new flavor name
        flavor_info = self.flavor.get_flavor(input_dict['flavor_id'])

        # Create an API connection with the Admin
        try:
            # build an API connection for the admin user
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(input_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")
        try:
            # construct request header and body
            body='{"resize": {"flavorRef": "%s"}}' % (input_dict['flavor_id'])
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (input_dict['project_id'],input_dict['server_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            # check the response code
        except:
            logger.sys_error("Error in sending resize request to server.")
            return 'ERROR'

        if(rest['response'] == 202):
            #update the instance with the new flavor and set confirm flag to 1
            stamp = util.time_stamp()
            try:
                self.db.pg_transaction_begin()
                update_inst = {'table':'trans_instances','set':"inst_flav_name='%s',inst_confirm_resize=1,inst_resize_julian_date='%s',inst_resize_hr_date='%s'"%(flavor_info['flavor_name'],stamp['julian'],stamp['raw']),'where':"inst_id='%s'"%(input_dict['server_id'])}
                self.db.pg_update(update_inst)
            except:
                #print update_inst
                self.db.pg_transaction_rollback()
                logger.sql_error('Could not update the instance %s with resize information.'%(input_dict['server_id']))
                #raise Exception('Could not update the instance %s with resize information.'%(input_dict['server_id']))
                return 'ERROR'
            else:
                self.db.pg_transaction_commit()
                return 'OK'
        else:
            nova_ec.error_codes(rest)
        #else:
        #    logger.sys_error("Only an admin or a power user can resize the server.")
        #    raise Exception("Only an admin or a power user can resize the server.")

    def confirm_resize(self, confirm_dict):
        """
        DESC: During a resize operation, the original server is saved for a
              period of time to allow roll back if a problem exists. Once the
              newly resized server is tested and has been confirmed to be
              functioning properly, use this operation to confirm the resize.
              After confirmation, the original server is removed and cannot be
              rolled back to. All resizes are automatically confirmed after 24
              hours if they are not explicitly confirmed or reverted
        INPUT: confirm_dict - server_id
                            - project_id
        OUTPUT: This operation does not return a response body.
        ACCESS: All users can perofrm this operation
        NOTE: The user will have to confirm the resize is good after the admin
              or the power user resizes the vm. May get a conflict issue if this command
              is issued to soon after resize is issued.
        """

        if ((confirm_dict['server_id'] == '') or ('server_id' not in confirm_dict)):
            logger.sys_error("No server id was provided.")
            raise Exception("No server id was provided.")
        if ((confirm_dict['project_id'] == '') or ('project_id' not in confirm_dict)):
            logger.sys_error("No server id was provided.")
            raise Exception("No server id was provided.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(confirm_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != confirm_dict['project_id']):
                logger.sys_error("Users can only reboot virtual servers in their project.")
                raise Exception("Users can only reboot virtual servers in their project.")

        #check to make sure non admins can perofrm the task
        if(self.is_admin == 0):
            self.get_server = None
            if(self.user_level == 1):
                self.get_server = {'select':'inst_name','from':'trans_instances','where':"proj_id='%s'"%(confirm_dict['project_id'])}
            elif(self.user_level == 2):
                self.get_server = {'select':'inst_name','from':'trans_instances','where':"proj_id='%s'"%(confirm_dict['project_id']),'and':"inst_user_id='%s'"%(self.user_id)}
            server = self.db.pg_select(self.get_server)
            if(server[0][0] == ''):
                logger.sys_error('The current user can not confirm the snapshot resize operation.')
                raise Exception('The current user can not confirm the snapshot resize operation.')

        # Create an API connection with the Admin
        try:
            # build an API connection for the admin user
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(confirm_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,confirm_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            # construct request header and body
            body='{"confirmResize": null}'
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (confirm_dict['project_id'],confirm_dict['server_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Error in sending resize confirm request to server.")
            raise Exception("Error in sending resize confirm request to server.")

        # check the response code
        if(rest['response'] == 204):
            # this method does not return any response body
            self.db.pg_transaction_begin()
            update_inst = {'table':'trans_instances','set':"inst_confirm_resize=0,inst_resize_julian_date='%s',inst_resize_hr_date='%s'"%('NULL','NULL'),'where':"inst_id='%s'"%(confirm_dict['server_id'])}
            self.db.pg_update(update_inst)
            self.db.pg_transaction_commit()
        else:
            #util.http_codes(rest['response'],rest['reason'],rest['data'])
            nova_ec.error_codes(rest)

        return 'OK'

    def revert_resize(self, revert_dict):
        """
        DESC: During a resize operation, the original server is saved for a
              period of time to allow for roll back if a problem occurs. If
              the resized server has a problem, use the revert resize
              operation to revert the resize and roll back to the original
              server. All resizes are automatically confirmed after 24 hours
              if you do not confirm or revert them.
        INPUT: revert_dict - server_id
                           - project_id
        OUTPUT: This operation does not return a response body.
        ACCESS: Admins can revert any vm, power users can on;y revert vms in their
                project, users can nonly revert their own vms.
        NOTE: none
        """

        if ((revert_dict['server_id'] == '') or ('server_id' not in revert_dict)):
            logger.sys_error("No server id was provided.")
            raise Exception("No server id was provided.")
        if ((revert_dict['project_id'] == '') or ('project_id' not in revert_dict)):
            logger.sys_error("No server id was provided.")
            raise Exception("No server id was provided.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(revert_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != revert_dict['project_id']):
                logger.sys_error("Users can only reboot virtual servers in their project.")
                raise Exception("Users can only reboot virtual servers in their project.")

        #check to make sure non admins can perofrm the task
        if(self.is_admin == 0):
            self.get_server = None
            if(self.user_level == 1):
                self.get_server = {'select':'inst_name','from':'trans_instances','where':"proj_id='%s'"%(self.project_id)}
            elif(self.user_level == 2):
                self.get_server = {'select':'inst_name','from':'trans_instances','where':"proj_id='%s'"%(self.project_id),'and':"inst_user_id='%s'"%(self.user_id)}
            server = self.db.pg_select(self.get_server)
            if(server[0][0] == ''):
                logger.sys_error('The current user can not confirm the resize operation.')
                raise Exception('The current user can not confirm the resize operation.')

        # Create an API connection with the Admin
        try:
            # build an API connection for the admin user
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(revert_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,revert_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            # construct request header and body
            body='{"revertResize": null}'
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (revert_dict['project_id'],revert_dict['server_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            # check the response code
        except:
            self.db.pg_transaction_rollback()
            logger.sys_error("Error in sending revert resize request to server.")
            raise Exception("Error in sending revert resize request to server.")

        if(rest['response'] == 202):
            # this method does not return any response body
            self.db.pg_transaction_begin()
            update_inst = {'table':'trans_instances','set':"inst_confirm_resize=0,inst_resize_julian_date='%s',inst_resize_hr_date='%s'"%('NULL','NULL'),'where':"inst_id='%s'"%(revert_dict['server_id'])}
            self.db.pg_update(update_inst)
            self.db.pg_transaction_commit()
        else:
            #util.http_codes(rest['response'],rest['reason'])
            nova_ec.error_codes(rest)

        return 'OK'

    def create_instance_snapshot(self,snap_dict):
        """
        DESC: This will create a new instance snapshot.
        INPUT: snap_dict - server_id - REQ
                         - project_id - REQ
                         - snapshot_name - OP
                         - snapshot_description - OP
                         - visibility - OP - public/private, defaults to private
        OUTPUT: r_dict - snapshot_name
                       - snapshot_id
        ACCESS: Cloud Admin - can snashot any vm
                PU - snapshot only vms in thei project
                User - snapshot only the vms they own
        NOTE: Any volumes that are attached to the instance will not be snapped,
              you will have to snapshot the environment in order to capture it.
        """

        if ((snap_dict['server_id'] == '') or ('server_id' not in snap_dict)):
            logger.sys_error("No server id was provided.")
            raise Exception("No server id was provided.")
        if ((snap_dict['project_id'] == '') or ('project_id' not in snap_dict)):
            logger.sys_error("No server id was provided.")
            raise Exception("No server id was provided.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(snap_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != snap_dict['project_id']):
                logger.sys_error("Users can only snapshot virtual servers in their project.")
                raise Exception("Users can only snapshot virtual servers in their project.")

        #check to make sure non admins can perofrm the task
        self.get_server = None
        self.run_flag = 0
        try:
            self.get_server = {'select':'inst_name,inst_user_id','from':'trans_instances','where':"proj_id='%s'"%(snap_dict['project_id']),'and':"inst_id='%s'"%(snap_dict['server_id'])}
            server = self.db.pg_select(self.get_server)
        except:
            logger.sql_error("Could not find instance %s in project %s"%(snap_dict['server_id'],snap_dict['project_id']))
            raise Exception("Could not find instance %s in project %s"%(snap_dict['server_id'],snap_dict['project_id']))

        if(self.user_level == 0):
            self.run_flag = 1
        elif(self.user_level == 1):
            if(self.project_id == snap_dict['project_id']):
                self.run_flag = 1
        elif(self.user_level == 2):
            if(self.user_id == server[0][1]):
                self.run_flag = 1

        if(self.run_flag == 1):
            if(server[0][0] == ''):
                logger.sys_error('The current user can not perform the backup operation.')
                raise Exception('The current user can not perform the backup operation.')
    
            if (('snapshot_name' not in snap_dict) or (snap_dict['snapshot_name'] == 'none')):
                snap_dict['snapshot_name'] = server[0][0] + '_snapshot'
    
            if (('snapshot_description' not in snap_dict) or (snap_dict['snapshot_description'] == 'none')):
                snap_dict['snapshot_description'] = 'None'
    
            # Create an API connection with the Admin
            try:
                # build an API connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                if(snap_dict['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,snap_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")
    
            try:
                # construct request header and body
                body='{"createImage": {"name": "%s", "metadata": {}}}'%(snap_dict['snapshot_name'])
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2/%s/servers/%s/action' % (snap_dict['project_id'],snap_dict['server_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sys_error("Error in snapshoting instance.")
                raise Exception("Error in snapshoting instance.")
    
            if(rest['response'] == 202):
                snap_id = None
                headers = rest['headers']
                for header in headers:
                    if(header[0] == 'location'):
                        snap_id = header[1].split('/')
                try:
                    #insert the volume info into the DB
                    self.db.pg_transaction_begin()
                    insert_snap = {"name": snap_dict['snapshot_name'],"type": 'snapshot',"inst_id": snap_dict['server_id'],"create_date":datetime.date.today(),"snap_id": snap_id[6],"project_id": snap_dict['project_id'],'description':snap_dict['snapshot_description'],'user_id':self.user_id}
                    self.db.pg_insert("trans_inst_snaps",insert_snap)
                except:
                    self.db.pg_transaction_rollback()
                    self.db.pg_close_connection()
                else:
                    self.db.pg_transaction_commit()
                    self.db.pg_close_connection()

                    # update snapshot visibility and user_level tags
                    try:
                        # wait for snapshot creation
                        while True:
                            try:
                                out = self.glance.get_image(snap_id[6])
                                if out['status'] == "active":
                                    break
                            except Exception as e:
                                time.sleep(.5)
                                continue
                        # update snapshot
                        image_id = snap_id[6]
                        update_array = []

                        if 'visibility' not in snap_dict:
                            # default to private
                            snap_dict['visibility'] = "private"
                        # change visibility
                        make_private_dict = {'operation': "replace", 'property': "visibility", 'value': snap_dict['visibility']}
                        update_array.append(make_private_dict)

                        # add user_level to tags[] for cascading permissions later
                        add_user_level_dict = {'operation': "replace", 'property': "tags", 'value': [str(self.user_level)]}
                        update_array.append(add_user_level_dict)
                        self.glance.update_image(image_id,update_array)
                    except Exception as e:
                        logger.sys_error("Could not make snapshot %s private, error: %s"%(snap_id[6],str(e)))
                        raise Exception("Could not make snapshot %s private, error: %s"%(snap_id[6],str(e)))

                    r_dict = {"snapshot_name": snap_dict['snapshot_name'],"snapshot_id": snap_id[6], "instance_id": snap_dict['server_id']}
                    return r_dict
            else:
                nova_ec.error_codes(rest)
        else:
            logger.sys_error("Could not retrieve the instance snapshots for %s"%(snap_dict['server_id']))
            raise Exception("Could not retrieve the instance snapshots for %s"%(snap_dict['server_id']))

    def delete_instance_snapshot(self,snapshot_id):
        """
        DESC: This will create a new instance snapshot.
        INPUT: snap_dict - image_id - REQ
        OUTPUT: OK
                ERROR
        ACCESS: Cloud Admin - can delete any snapshot
                PU - can delete any snapshot in their project
                User - can only delete snapshots they own.
        NOTE: Any volumes that are attached to the instance will not be snapped,
              you will have to snapshot the environment in order to capture it.
        """
        delete = self.glance.delete_image(snapshot_id)

        try:
            self.db.pg_transaction_begin()
            del_dict = {"table":'trans_inst_snaps',"where":"snap_id='%s'" %(snapshot_id)}
            self.db.pg_delete(del_dict)
        except:
            self.db.pg_transaction_rollback()
            logger.sql_error('Could not remove image %s from Transcirrus DB.'%(snapshot_id))
            raise Exception('Could not remove image %s from Transcirrus DB.'%(snapshot_id))
        else:
            self.db.pg_transaction_commit()

        return delete

    def list_instance_snaps(self,instance_id):
        """
        DESC: List the snapshots for a specific instance
        INPUT: instance_id
        OUTPUT: array of r_dict - snapshot_id
                                - snapshot_name
                                - instance_id
                                - project_id
        ACCESS: Admin- get all instance snapshot info
                PU - get snapshot info for instance snaps in their project
                user - get info for the snaps they own
        NOTE:
        """

        if(self.user_level == 1):
            self.get_inst_snap = {'select':'snap_id,name,project_id','from':'trans_inst_snaps','where':"inst_id='%s'"%(instance_id), 'and':"project_id='%s'"%(self.project_id)}
        elif(self.user_level == 2):
            self.get_inst_snap = {'select':'snap_id,name,project_id','from':'trans_inst_snaps','where':"inst_id='%s'"%(instance_id), 'and':"user_id='%s'"%(self.user_id)}
        elif(self.user_level == 0):
            self.get_inst_snap = {'select':'snap_id,name,project_id','from':'trans_inst_snaps','where':"inst_id='%s'"%(instance_id)}

        snapshots = self.db.pg_select(self.get_inst_snap)

        r_array = []
        for snap in snapshots:
            r_dict ={'snapshot_id':snap[0],'snapshot_name':snap[1], 'instance_id': instance_id, 'project_id':snap[2]}
            r_array.append(r_dict)

        return r_array

    def get_instance_snap_info(self,input_dict):
        """
        DESC: Get the instance snapshot info
        INPUT: input_dict - snapshot_id
                          - project_id
        OUTPUT: r_dict - instance_id
                       - snapshot_id
                       - project_id
                       - snapshot_name
                       - description
                       - date_created
                       - type
        ACCESS: Admin- get all instance snapshot info
                PU - get snapshot info for instance snaps in their project
                user - get info for the snaps they own
        NOTE:
        """
        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(input_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.user_level == 1):
            self.get_inst_snap = {'select':'*','from':'trans_inst_snaps','where':"snap_id='%s'"%(input_dict['snapshot_id']), 'and':"project_id='%s'"%(self.project_id)}
        elif(self.user_level == 2):
            self.get_inst_snap = {'select':'*','from':'trans_inst_snaps','where':"snap_id='%s'"%(input_dict['snapshot_id']), 'and':"user_id='%s'"%(self.user_id)}
        elif(self.user_level == 0):
            self.get_inst_snap = {'select':'*','from':'trans_inst_snaps','where':"snap_id='%s'"%(input_dict['snapshot_id']), 'and':"project_id='%s'"%(input_dict['project_id'])}

        try:
            inst_snapshot = self.db.pg_select(self.get_inst_snap)
        except:
            logger.sys_error('Can not find the snapshot with id %s'%(input_dict['snapshot_id']))
            raise Exception('Can not find the snapshot with id %s'%(input_dict['snapshot_id']))

        r_dict = {'instance_id':inst_snapshot[0][3],'snapshot_id':inst_snapshot[0][5],'project_id':inst_snapshot[0][6],'snapshot_name':inst_snapshot[0][1],'description':inst_snapshot[0][7],'date_created':inst_snapshot[0][4],'type':inst_snapshot[0][2]}

        return r_dict

    def create_instance_backup(self,backup_dict):
        """
        DESC: This will backup an instance, a backup is a full clone of a vm.
        INPUT: backup_dict - server_id - REQ
                           - project_id - REQ
                           - backup_type (weekly/daily) - REQ
                           - rotation - REQ
                           - backup_name - op
                           - backup_description
        OUTPUT: r_dict - backup_name
                       - backup_id
        ACCESS: 
        NOTE: Rotaion refers to how many times per period to do the backup job
                ex. 2 with weekly, would keep two backups of the instance.
            You may loose network connection since the vm must be paused to do a backup.
        """

        if ((backup_dict['server_id'] == '') or ('server_id' not in backup_dict)):
            logger.sys_error("No server id was provided.")
            raise Exception("No server id was provided.")
        if ((backup_dict['project_id'] == '') or ('project_id' not in backup_dict)):
            logger.sys_error("No server id was provided.")
            raise Exception("No server id was provided.")

        #default to daily
        if (('backup_type' not in backup_dict) or (backup_dict['backup_type'] == '')):
            backup_dict['backup_type'] = 'daily'

        #default to 1
        if (('rotation' not in backup_dict) or (backup_dict['rotation'] == '')):
            backup_dict['rotation'] = '1'

        if (('snapshot_description' not in backup_dict) or (backup_dict['snapshot_description'] == '')):
            backup_dict['snapshot_description'] = 'None'

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(backup_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != backup_dict['project_id']):
                logger.sys_error("Users can only backup virtual servers in their project.")
                raise Exception("Users can only backup virtual servers in their project.")

        #check to make sure non admins can perofrm the task
        self.get_server = None
        if(self.is_admin == 0):
            if(self.user_level == 1):
                self.get_server = {'select':'inst_name','from':'trans_instances','where':"proj_id='%s'"%(self.project_id)}
            elif(self.user_level == 2):
                self.get_server = {'select':'inst_name','from':'trans_instances','where':"proj_id='%s'"%(self.project_id),'and':"inst_user_id='%s'"%(self.user_id)}
        self.get_server = {'select':'inst_name','from':'trans_instances','where':"proj_id='%s'"%(backup_dict['project_id'])}
        server = self.db.pg_select(self.get_server)
        if(server[0][0] == ''):
            logger.sys_error('The current user can not perform the backup operation.')
            raise Exception('The current user can not perform the backup operation.')

        if (('backup_name' not in backup_dict) or (backup_dict['backup_name'] == '')):
            backup_dict['backup_name'] = server[0][0] + '_backup'

        # Create an API connection with the Admin
        try:
            # build an API connection for the admin user
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(backup_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,backup_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            # construct request header and body
            body='{"createBackup": {"backup_type": "%s", "rotation": "%s", "name": "%s"}}'%(backup_dict['backup_type'],backup_dict['rotation'],backup_dict['backup_name'])
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (backup_dict['project_id'],backup_dict['server_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            # check the response code
        except:
            logger.sys_error("Error in sending backup request to server.")
            raise Exception("Error in sending backup request to server.")

        if(rest['response'] == 202):
            back_id = None
            headers = rest['headers']
            for header in headers:
                if(header[0] == 'location'):
                    back_id = header[1].split('/')
            try:
                #insert the volume info into the DB
                self.db.pg_transaction_begin()
                insert_back = {"name": backup_dict['backup_name'],"type": 'backup',"inst_id": backup_dict['server_id'],"create_date":datetime.date.today(),"snap_id": back_id[5],"project_id": backup_dict['project_id'],'description':backup_dict['backup_description']}
                self.db.pg_insert("trans_inst_snaps",insert_back)
            except:
                self.db.pg_transaction_rollback()
                self.db.pg_close_connection()
            else:
                self.db.pg_transaction_commit()
                self.db.pg_close_connection()
                r_dict = {"backup_name": backup_dict['backup_name'],"backup_id": back_id[5]}
                return r_dict
        else:
            nova_ec.error_codes(rest)

    def get_instance_console(self,input_dict):
        """
        DESC: Get the novnc console associated with an instance.
        INPUT: input_dict - project_id
                          - instance_id
                          - type vnc/spice
        OUTPUT: NoVnc console address
        ACCESS: Wide open
        NOTES:
        """
        logger.sys_info('\n**Server get console. Component: Nova Def: get_instance_console**\n')
        for key,value in input_dict.items():
            if(key == ''):
                logger.sys_error('Required value not passed.')
                raise Exception('Required value not passed.')
            if(value == ''):
                logger.sys_error('Required value not passed.')
                raise Exception('Required value not passed.')

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
            body='{"os-getVNCConsole": {"type": "novnc"}}'
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (input_dict['project_id'],input_dict['instance_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Error getting server console.")
            raise Exception("Error getting server console.")

        if(rest['response'] == 200):
                # this method does not return any response body
                logger.sys_info("Response %s with Reason %s" % (rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                return load['console']['url']
        elif(rest['response'] == 409):
            logger.sys_error("Could not get server status %s"%(input_dict['instance_id']))
        else:
            util.http_codes(rest['response'],rest['reason'],rest['data'])

    def update_instance_secgroup(self,input_dict):
        """
        DESC: Allows a user to be able to add/remove the security group to an instance.
        INPUT: input_dict - project_id - REQ
                          - instance_id - REQ
                          - secgroup_id - REQ
                          - action add/remove - REQ
        OUTPUT: r_dict - instance_id
                       - secgroup_id
        ACCESS: Admin - Can change the secgroup of any instance
                PU - Can change any instance in his project
                User - Can only chnage instance sec groups they own.
        NOTES: You can only add secgroups you have created.
        """
        logger.sys_info('\n**Server action update security group. Component: Nova Def: update_instance_secgroup**\n')
        for key,value in input_dict.items():
            if(key == ''):
                logger.sys_error('Required value not passed.')
                raise Exception('Required value not passed.')
            if(value == ''):
                logger.sys_error('Required value not passed.')
                raise Exception('Required value not passed.')

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(input_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        #make sure add or remove specifed
        action = input_dict['action']
        if(action.lower() == 'add'):
            logger.sys_info('Valid option add in update_instance_secgroup.')
        elif(action.lower() == 'remove'):
            logger.sys_info('Valid option remove in update_instance_secgroup.')
        else:
            logger.sys_error('An unknow action has been specified for update_instance_secgroup.')
            raise Exception('An unknow action has been specified for update_instance_secgroup.')

        #confirm that the user can modify the instance
        if(self.user_level == 1):
            self.get_inst = {'select':'inst_name','from':'trans_instances','where':"inst_id='%s'"%(input_dict['instance_id']), 'and':"proj_id='%s'"%(self.project_id)}
        elif(self.user_level == 2):
            self.get_inst = {'select':'inst_name','from':'trans_instances','where':"inst_id='%s'"%(input_dict['instance_id']), 'and':"user_id='%s'"%(self.user_id)}
        elif(self.user_level == 0):
            self.get_inst = {'select':'inst_name','from':'trans_instances','where':"inst_id='%s'"%(input_dict['instance_id']), 'and':"proj_id='%s'"%(input_dict['project_id'])}

        try:
            inst = self.db.pg_select(self.get_inst)
        except:
            logger.sys_error('Can not change security group info for the instance with id %s'%(input_dict['instance_id']))
            raise Exception('Can not change security group info for the instance with id %s'%(input_dict['instance_id']))

        #confirm that the user owns the sec group in question.
        if(self.user_level == 1):
            self.get_sec = {'select':'sec_group_name','from':'trans_security_group','where':"sec_group_id='%s'"%(input_dict['secgroup_id']), 'and':"proj_id='%s'"%(self.project_id)}
        elif(self.user_level == 2):
            self.get_sec = {'select':'sec_group_name','from':'trans_security_group','where':"sec_group_id='%s'"%(input_dict['secgroup_id']), 'and':"user_id='%s'"%(self.user_id)}
        elif(self.user_level == 0):
            self.get_sec = {'select':'sec_group_name','from':'trans_security_group','where':"sec_group_id='%s'"%(input_dict['secgroup_id']), 'and':"proj_id='%s'"%(input_dict['project_id'])}

        try:
            sec_group = self.db.pg_select(self.get_sec)
        except:
            logger.sys_error('Can not change security group info for %s'%(input_dict['secgroup_id']))
            raise Exception('Can not change security group info for %s'%(input_dict['secgroup_id']))

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
            if(input_dict['action'] == 'remove'):
                self.body='{"removeSecurityGroup": {"name": "%s"}}'%(sec_group[0][0])
            if(input_dict['action'] == 'add'):
                self.body='{"addSecurityGroup": {"name": "%s"}}'%(sec_group[0][0])
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action' % (input_dict['project_id'],input_dict['instance_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": self.body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Error in server security group update request.")
            raise Exception("Error in server security group update request.")

        if(rest['response'] == 202):
                # this method does not return any response body
                r_dict = {'instance_name':inst[0][0],'instance_id':input_dict['instance_id'],'secgroup_id':input_dict['secgroup_id'],'secgroup_name':sec_group[0][0]}
                return r_dict
        else:
            nova_ec.error_codes(rest)

    def validate_instance(self,input_dict):
        """
        DESC: Get the novnc console associated with an instance.
        INPUT: input_dict - project_id
                          - flavor_id
        OUTPUT: OK - instance can be created
                ERROR - instance can not be created
        ACCESS: Admin - can validate an instance in any project they are an admin of
                PU - can validate an instance only in the project they are in
                User - can validate an instance only in the project they are in
        NOTES: 
        """
        #make sure the dictionaty vals are good
        #make sure the project exists
        #make sure the flavor exists
        
        #get flavor attributes
        #get quota for project
        
        #check if attributes are under granted quota

    #Internal methods
    #this is a hack to overcome a system limitation
    def _check_status(self,project_id=None,server_id=None):
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":project_id}
            if(project_id != self.project_id):
                    self.token = get_token(self.username,self.password,project_id)
            api = caller(api_dict)
        except Exception as e:
            raise e
        
        try:
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'GET'
            api_path = '/v2/%s/servers/%s'%(project_id,server_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error("Could not check status %s" %(e))
            raise e
    
        load = json.loads(rest['data'])
        if(rest['response'] == 200):
            r_dict = {'server_status':load['server']['status']}
            return r_dict
        else:
            nova_ec.error_codes(rest)