import sys
import json

import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

class admin_ops:
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
                if(self.adm_token == ''):
                    logger.sys_error('Admin user had no admin token passed.')
                    raise Exception('Admin user had no admin token passed.')
            else:
                self.adm_token = 'NULL'

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

    def list_net_quota(self,project_id):
        """
        DESC: List non-default quotas for networks on a tenant. 
        INPUT: project_id
        OUTPUT: r_dict - networks
                       - subnets
                       - floatingips
                       - routers
                       - ports
        ACCESS: Only Admins can list quotas for tenants.
        """
        logger.sys_info('\n**Listing network quotas. Component: Neutron Def: list_net_quota**\n')
        network = 10
        subnet = 10
        port = 50
        floating = None
        router = None

        if(self.user_level <= 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                body = ''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'GET'
                api_path = '/v2.0/quotas'
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sql_error("Could not get the quota info.")
                raise Exception("Could not get the quota info.")

            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                r_array = None
                for quota in load['quotas']:
                    if('network' in quota):
                        network = quota['network']
                    if('subnet' in quota):
                        subnet = quota['subnet']
                    if('floatingip' in quota):
                        floatingip = quota['floatingip']
                    if('router' in quota):
                        network = quota['router']
                    if('port' in quota):
                        network = quota['port']
                    r_dict = {'networks': network,'subnets': subnet,'floatingips':floating,'routers': router,'ports': port,'project_id':quota['tenant_id']}
                    r_array.append(r_dict)
                return r_array
            else:
                util.http_codes(rest['response'],rest['reason'])
                return 'ERROR'
        else:
            logger.sys_error("Users can not get network quota info.")
            raise Exception("Users can not get network quota info.")

    def get_net_quota(self,project_id):
        """
        DESC: Show a tenants network quotas
        INPUT: project_id
        OUTPUT: r_dict - subnet
                       - network
                       - floatingip
                       - security_group_rule
                       - security_group
                       - router
                       - port
        ACCESS: Admins can get the quota info on any network.
                Power users can only get quota info on networks in their project.
        """
        logger.sys_info('\n**Listing network quotas. Component: Neutron Def: get_net_quota**\n')
        if(self.user_level <= 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":project_id}
                if(project_id != self.project_id):
                    self.token = get_token(self.username,self.password,project_id)
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                body = ''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'GET'
                api_path = '/v2.0/quotas/%s'%(project_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sql_error("Could not get the quota info.")
                raise Exception("Could not get the quota info.")

            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                return load['quota']
            else:
                util.http_codes(rest['response'],rest['reason'])
                return 'ERROR'
        else:
            logger.sys_error("Users can not get network quota info.")
            raise Exception("Users can not get network quota info.")

    def update_net_quota(self,input_dict):
        """
        DESC: List non-default quotas for networks on a tenant. 
        INPUT: input_dict - port_id - req
                          - project_id - req
        OUTPUT: r_dict - r_dict - subnet
                       - network
                       - floatingip
                       - security_group_rule
                       - security_group
                       - router
                       - port
        ACCESS: Only admins can set a network quota on a project
        """
        logger.sys_info('\n**Listing network quotas. Component: Neutron Def: update_net_quota**\n')
        if(self.is_admin == 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":input_dict['project_id']}
                if(input_dict['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                body = '{"quota": {"subnet": %d,"router": %d,"network": %d,"floatingip": %d,"port": %d}'%()
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'PUT'
                api_path = '/v2.0/quotas/%s'%(project_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sql_error("Could not get the quota info.")
                raise Exception("Could not get the quota info.")

            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                return load['quota']
            else:
                util.http_codes(rest['response'],rest['reason'])
                return 'ERROR'
        else:
            logger.sys_error("Users can not update network quota info.")
            raise Exception("Users can not update network quota info.")

    def delete_net_quota(self,input_dict):
        """
        DESC: List non-default quotas for networks on a tenant. 
        INPUT: input_dict - port_id - req
                          - project_id - req
        OUTPUT: OK - success
                ERROR - fail
                NA - unknown
        ACCESS: Admins can get the info on any port
                Power users can only get info on ports in their project.
        """
        logger.sys_info('\n**Listing network quotas. Component: Neutron Def: delete_net_quota**\n')