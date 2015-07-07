import sys
import json

import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token
from transcirrus.database.postgres import pgsql

class port_ops:
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

    def get_net_port(self,input_dict):
        """
        DESC: Get the port info.
        INPUT: input_dict - port_id - req
                          - project_id - req
        OUTPUT: OK - success
                ERROR - fail
                NA - unknown
        ACCESS: Admins can get the info on any port
                Power users can only get info on ports in their project.
        """
        if(self.user_level <= 1):
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
                body = ''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'GET'
                api_path = '/v2.0/ports/%s'%(input_dict['port_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
                if(rest['response'] == 200):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    load = json.loads(rest['data'])
                    r_dict = {'admin_state_up': load['port']['admin_state_up'],'device_id':load['port']['device_id'],'device_owner':load['port']['device_owner'],'fixed_ips': load['port']['fixed_ips'],'mac': load['port']['mac_address']}
                    return r_dict
                else:
                    util.http_codes(rest['response'],rest['reason'],rest['data'])
                    return 'ERROR'
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not get the port info.")
                raise Exception("Could not get the port info.")
        else:
            logger.sys_error("Users can not get the port info.")
            raise Exception("Users can not get the port info.")

    def remove_net_port(self,input_dict):
        """
        DESC: used to clean up after the
        INPUT: input_dict  - subnet_id - req
                           - port_id - req
                           - project_id - req
        OUTPUT: OK - success
                ERROR - fail
                NA - unknown
        ACCESS: Admins can remove a port in any project
                power users can remove a port in their own project
                users can not remove ports
        """
        if(('subnet_id' not in input_dict) or (input_dict['subnet_id'] == '')):
            logger.sys_error("Could not remove port. No subnet id given.")
            raise Exception("Could not remove port. No subnet id given.")
        if(('port_id' not in input_dict) or (input_dict['port_id'] == '')):
            logger.sys_error("No port id given. Can not remove port.")
            raise Exception("No port id given. Can not remove port.")
        if(('project_id' not in input_dict) or (input_dict['project_id'] == '')):
            logger.sys_error("No project id given. Can not remove port.")
            raise Exception("No project id given. Can not remove port.")

        #make sure the project exists
        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(input_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error('The project doest not exist: remove_net_port')
            raise Exception('The project doest not exist: remove_net_port')

        if(self.is_admin == 0):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error('Power user can only remove ports in their project: remove_net_port')
                raise Exception('Power user can only remove ports in their project: remove_net_port')

        #make sure the subnet is in the project
        try:
            get_sub = None
            if(self.user_level <= 1):
                get_sub = {'select':'subnet_id','from':'trans_subnets','where':"proj_id='%s'"%(input_dict['project_id'])}
                subnet = self.db.pg_select(get_sub)
            else:
                logger.sys_error('Could not get subnet, invalid user level: remove_net_port')
                raise Exception('Could not get subnet, invalid user level: remove_net_port')
        except:
            logger.sys_error('Could not get subnet, invalid user level: remove_net_port')
            raise Exception('Could not get subnet, invalid user level: remove_net_port')


        if(self.user_level <= 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                if(input_dict['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API: remove_net_port")
                raise Exception("Could not connect to the API: remove_net_port")
            try:
                body = ''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'DELETE'
                api_path = '/v2.0/ports/%s'%(input_dict['port_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sql_error("Could not remove the port with api: remove_net_port")
                raise Exception("Could not remove the port with api: remove_net_port")

            #check the response and make sure it is a 201
            if(rest['response'] == 204):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            else:
                util.http_codes(rest['response'],rest['reason'],rest['data'])
        else:
            logger.sys_error("Only an admin or a power user can remove a port: remove_net_port")
            raise Exception("Only an admin or a power user can remove a port: remove_net_port")

    def list_net_ports(self,input_dict):
        """
        DESC: used to list the 'in use' ports (ips) on a subnet
        INPUT: input_dict  - net_id - req
                           - subnet_id - req
                           - project_id - req
        OUTPUT: array of r_dict - port_status
                                - port_mac
                                - port_id
        ACCESS: Admins can list ports in any project
                power users can list ports in their own project
                users can not remove ports
        """
        if(('subnet_id' not in input_dict) or (input_dict['subnet_id'] == '')):
            logger.sys_error("Could not remove port. No subnet id given.")
            raise Exception("Could not remove port. No subnet id given.")
        if(('project_id' not in input_dict) or (input_dict['project_id'] == '')):
            logger.sys_error("No project id given. Can not remove port.")
            raise Exception("No project id given. Can not remove port.")

        #make sure the project exists
        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(input_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error('The project doest not exist: remove_net_port')
            raise Exception('The project doest not exist: remove_net_port')

        #make sure the subnet is in project
        try:
            get_sub = {'select':'subnet_name','from':'trans_subnets','where':"subnet_id='%s'"%(input_dict['subnet_id']),'and':"proj_id='%s'"%(input_dict['project_id'])}
            subnet = self.db.pg_select(get_sub)
        except:
            logger.sys_error('The subnet doest not existin project %s: remove_net_port'%(input_dict['project_id']))
            raise Exception('The subnet doest not existin project %s: remove_net_port'%(input_dict['project_id']))

        #make sure the subnet is in the network
        try:
            get_sub2 = {'select':'subnet_name','from':'trans_subnets','where':"subnet_id='%s'"%(input_dict['subnet_id']),'and':"net_id='%s'"%(input_dict['net_id'])}
            subnet2 = self.db.pg_select(get_sub2)
        except:
            logger.sys_error('The subnet doest not exist in network %s: remove_net_port'%(input_dict['net_id']))
            raise Exception('The subnet doest not exist in network %s: remove_net_port'%(input_dict['net_id']))

        if(self.is_admin == 0):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error('Power user can only remove ports in their project: remove_net_port')
                raise Exception('Power user can only remove ports in their project: remove_net_port')

        if(self.user_level <= 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                if(input_dict['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API: list_net_port")
                raise Exception("Could not connect to the API: list_net_port")
            try:
                body = ''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'GET'
                api_path = '/v2.0/ports'
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sql_error("Could not remove the port with api: remove_net_port")
                raise Exception("Could not remove the port with api: remove_net_port")

            #check the response and make sure it is a 201
            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                r_dict = None
                r_array = []
                for port in load['ports']:
                    fixed_ip = port['fixed_ips']
                    for ip in fixed_ip:
                        if(port['network_id'] == input_dict['net_id']):
                            if(ip['subnet_id'] == input_dict['subnet_id']):
                                r_dict = {'port_status':str(port['status']),'port_mac':str(port['mac_address']),'port_id':str(port['id']),'port_ip':str(ip['ip_address'])}
                                r_array.append(r_dict)
                return r_array
            else:
                util.http_codes(rest['response'],rest['reason'])
        else:
            logger.sys_error("Only an admin or a power user can remove a port: remove_net_port")
            raise Exception("Only an admin or a power user can remove a port: remove_net_port")

    
    def add_net_port():
        """
        DESC: used to clean up after the
        INPUT: input_dict  - subnet_id - req
                           - port_id - req
                           - project_id - req
        OUTPUT: OK - success
                ERROR - fail
                NA - unknown
        ACCESS: Admins can remove a port in any project
                power users can remove a port in their own project
                users can not remove ports
        """

    def update_net_port():
        print "not implemented"