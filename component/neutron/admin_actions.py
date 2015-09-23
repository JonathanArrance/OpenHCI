import sys
import json

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token
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
        ACCESS: Only admins can list network quotas.
        """
        logger.sys_info('\n**Listing network quotas. Component: Neutron Def: list_net_quota**\n')
        if(project_id == ''):
            logger.sys_error("Project id not given.")
            raise Exception("Project id not given.")
        
        network = 10
        subnet = 10
        port = 50
        floating = None
        router = None

        if(self.is_admin == 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                if(self.project_id != project_id):
                    self.token = get_token(self.username,self.password,project_id)
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
                r_array = []
                if(load['quotas']):
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
                else:
                    r_dict = {'networks': network,'subnets': subnet,'floatingips':floating,'routers': router,'ports': port,'project_id':project_id}
                    r_array.append(r_dict)
                return r_array
            else:
                util.http_codes(rest['response'],rest['reason'],rest['data'])
                return 'ERROR'
        else:
            logger.sys_error("Users can not get network quota info.")
            r_dict = {'networks': 'NA','subnets': 'NA','floatingips': 'NA','routers': 'NA','ports': 'NA','project_id': self.project_id}
            return r_array

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
        logger.sys_info('\n**Get network quotas. Component: Neutron Def: get_net_quota**\n')
        if(project_id == ''):
            logger.sys_error("Project id not given.")
            raise Exception("Project id not given.")
        if(self.user_level <= 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
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
        INPUT: input_dict - project_id - req
                          - subnet_quota - op
                          - router_quota - op
                          - network_quota - op
                          - floatingip_quota - op
                          - port_quota - op
                          - security_group_rule_quota - op
                          - security_group_quota - op
        OUTPUT: r_dict - r_dict - subnet
                       - network
                       - floatingip
                       - security_group_rule
                       - security_group
                       - router
                       - port
        ACCESS: Only admins can set a network quota on a project
        NOTE: If no quotas are specifed nothing is done, return 'OK'
        """
        logger.sys_info('\n**Updateing network quotas. Component: Neutron Def: update_net_quota**\n')
        for key,value in input_dict.items():
            if(key == '' and key == 'project_id'):
                logger.sys_error('Reguired value not passed.')
                raise Exception('Reguired value not passed.')
            if(key == 'project_id' and value == ''):
                logger.sys_error('Reguired value not passed.')
                raise Exception('Reguired value not passed.')
        if(('subnet_quota' not in input_dict) and ('router_quota' not in input_dict) and ('network_quota' not in input_dict) and ('floatingip_quota' not in input_dict) and ('port_quota' not in input_dict)):
            return 'OK'

        if(self.is_admin == 1):
            #get the current quota vals
            current_quota = self.get_net_quota(input_dict['project_id'])
            if('subnet_quota' not in input_dict or input_dict['subnet_quota'] == ''):
                input_dict['subnet_quota'] = current_quota['subnet']
            if('router_quota' not in input_dict or input_dict['router_quota'] == ''):
                input_dict['router_quota'] = current_quota['router']
            if('network_quota' not in input_dict or input_dict['network_quota'] == ''):
                input_dict['network_quota'] = current_quota['network']
            if('floatingip_quota' not in input_dict or input_dict['floatingip_quota'] == ''):
                input_dict['floatingip_quota'] = current_quota['floatingip']
            if('port_quota' not in input_dict or input_dict['port_quota'] == ''):
                input_dict['port_quota'] = current_quota['port']
            if('security_group_rule_quota' not in input_dict or input_dict['security_group_rule_quota'] == ''):
                input_dict['security_group_rule_quota'] = current_quota['security_group_rule']
            if('security_group_quota' not in input_dict or input_dict['security_group_quota'] == ''):
                input_dict['security_group_quota'] = current_quota['security_group']

            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                if(input_dict['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                body = '{"quota": {"subnet": %d,"router": %d,"network": %d,"floatingip": %d,"port": %d, "security_group_rule": %d, "security_group": %d}}'%(int(input_dict['subnet_quota']),int(input_dict['router_quota']),int(input_dict['network_quota']),
                                                                                                          int(input_dict['floatingip_quota']),int(input_dict['port_quota']),int(input_dict['security_group_rule_quota']),int(input_dict['security_group_quota']))
                header = {"X-Auth-Token":self.token}
                function = 'PUT'
                api_path = '/v2.0/quotas/%s'%(input_dict['project_id'])
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
                util.http_codes(rest['response'],rest['reason'],rest['data'])
        else:
            logger.sys_error("Users can not update network quota info.")
            raise Exception("Users can not update network quota info.")

    def reset_net_quota(self,project_id):
        """
        DESC: Reset network quotas to defaults.
        INPUT: project_id
        OUTPUT: OK - success
        ACCESS: Only Admins can reset network quotas.
        """
        logger.sys_info('\n**Resetting network quotas. Component: Neutron Def: reset_net_quota**\n')
        if(project_id == ''):
            logger.sys_error("Project id not given.")
            raise Exception("Project id not given.")
        if(self.is_admin == 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                if(project_id != self.project_id):
                    self.token = get_token(self.username,self.password,project_id)
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                body = ''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'DELETE'
                api_path = '/v2.0/quotas/%s'%(project_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sql_error("Could not reset the quota info.")
                raise Exception("Could not reset the quota info.")

            if(rest['response'] == 204):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                return 'OK'
            else:
                util.http_codes(rest['response'],rest['reason'],rest['data'])
        else:
            logger.sys_error("Users can not reset network quota info.")
            raise Exception("Users can not reset network quota info.")