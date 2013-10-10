#!/usr/bin/python

#ONLY CREATING AND DELETEING SERVICE ENDPOINTS IS NECCESSARY FOR PROTOTYPE

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import json

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

class endpoint_ops:

    #DESC: Constructor to build out the tokens object
    #INPUT: user_dict dictionary containing - built in auth.py
    def __init__(self,user_dict):
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        # user_dict = {"username":self.username,"password":self.user_pass,"project_id":exist[0][7],"status_level":status_level,"user_level":user_level,"is_admin": is_admin,"token":token}
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
            self.adm_token = user_dict['adm_token']
            if 'sec' in user_dict:
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'
                
            #get the default cloud controller info
            self.controller = config.DEFAULT_CLOUD_CONTROLER

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")

        if((self.token == 'error') or (self.token == '')):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        try:
            #use util.close_db when you no longer need o have the connection open.
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
            logger.sql_info("Connected to the Transcirrus DB to do keystone user operations.")
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB, %s" %(e))
            raise

    #DESC: create a new cloud service endpoint. This function will also
    #      add the service to the service catalog. Only the cloud admin can
    #      create a new cloud service endpoint.
    #INPUT: input_dict -cloud_name - op ciac cloud name is used
    #                  -service_name - req
    #OUPUT: r_dict -endpoint_id
    #              -service_name
    #              -service_id
    #              -admin_url
    #              -internal_url
    #              -public_url
    def create_endpoint(self,input_dict):
        if('service_name' not in input_dict):
            logger.sys_error("The service name was not specified while createing an endpoint.")
            raise Exception("The service name was not specified while createing an endpoint.")
        if(self.is_admin == 0):
            logger.sys_logger("Endpoints can only be crearted by the admin.")
            raise Exception("Endpoints can only be crearted by the admin.")

        #get the cloud name (Region)
        if('cloud_name' not in input_dict):
            try:
                get_name = {'select':"param_value",'from':"trans_system_settings",'where':"host_system='%s'" %(self.controller),'and':"parameter='cloud_name'"}
                input_dict['cloud_name'] = self.db.pg_select(get_name)
            except:
                logger.sys_error("Could not retrieve the cloud name from the trans_system_settings db.")
                raise Exception("Could not retrieve the cloud name from the trans_system_settings db.")

        #get ip info from the DB for the endpoint creaton
        try:
            #get_ips = {'select':"admin_api_ip,int_api_ip,api_ip",'from':"trans_system_settings",'where':"host_system='%s'" %(self.controller)}
            get_ips = {'select':"param_value",'from':"trans_system_settings",'where':"host_system='%s'" %(self.controller),'and':"parameter='api_ip'"}
            self.api_ips = self.db.pg_select(get_ips)
        except:
            logger.sql_error("Could not retrieve the api ips to create endpoints with.")
            raise Exception("Could not retrieve the api ips to create endpoints with.")
        
        #Build the endpoints for the service in question
        #get the service info from the DB
        try:
            #Get pre populated values from the transcirrus db. Needed to build service catalog and endpoints in OpenStack
            get_serv_info = {'select':"service_port,service_api_version,service_desc,service_type",'from':"trans_service_settings",'where':"service_name='%s'" %(input_dict['service_name'])}
            self.get_service = self.db.pg_select(get_serv_info)
            if(not self.get_service):
                #if the service name is bogus it will fail
                logger.sys_error("Could not find the service %s." %(input_dict['service_name']))
                raise Exception("Could not find the service %s." %(input_dict['service_name']))
        except:
            logger.sql_error("Could not get the service info for OpenStack %s service from database." %(input_dict['service_name']))
            raise Exception("Could not get the service info for OpenStack %s service from database." %(input_dict['service_name']))

        #build the endpoints
        if(self.get_service[0][1] == 'NULL'):
            self.get_service[0][1] = ""
        public_api = "http://%s:%s%s" %(self.api_ips[0][0],self.get_service[0][0],self.get_service[0][1])
        internal_api = "http://%s:%s%s" %(self.api_ips[0][0],self.get_service[0][0],self.get_service[0][1])
        admin_api = "http://%s:%s%s" %(self.api_ips[0][0],self.get_service[0][0],self.get_service[0][1])
        
        #connect to the API
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        #add the service to the service catalog
        body = '{"OS-KSADM:service": {"type": "%s", "name": "%s", "description": "%s"}}' %(self.get_service[0][3],input_dict['service_name'],self.get_service[0][2])
        header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json"}
        function = 'POST'
        api_path = '/v2.0/OS-KSADM/services'
        token = self.adm_token
        sec = 'FALSE'
        rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
        rest = api.call_rest(rest_dict)
        if(rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            #update service table with ips and service id
            self.service_id = load['OS-KSADM:service']['id']
            self.db.pg_transaction_begin()
            update = {'table':"trans_service_settings",'set':"service_id='%s',service_admin_ip='%s',service_int_ip='%s',service_public_ip='%s'" %(self.service_id,self.api_ips[0][0],self.api_ips[0][0],self.api_ips[0][0]),'where':"service_name='%s'" %(input_dict['service_name'])}
            self.db.pg_update(update)
            self.db.pg_transaction_commit()
        else:
            self.db.pg_transaction_rollback()
            util.http_codes(rest['response'],rest['reason'])

        ep_body = '{"endpoint": {"adminurl": "%s", "service_id": "%s", "region": "%s", "internalurl": "%s", "publicurl": "%s"}}' %(admin_api,self.service_id,input_dict['cloud_name'],internal_api,public_api)
        ep_header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json"}
        ep_function = 'POST'
        ep_api_path = '/v2.0/endpoints'
        ep_token = self.adm_token
        ep_sec = 'FALSE'
        ep_rest_dict = {"body":ep_body, "header":ep_header, "function":ep_function, "api_path":ep_api_path, "token":ep_token, "sec":ep_sec}
        ep_rest = api.call_rest(ep_rest_dict)
        if(ep_rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(ep_rest['response'],ep_rest['reason']))
            load = json.loads(ep_rest['data'])
            ep_id = load['endpoint']['id']
            update = {'table':"trans_service_settings",'set':"service_endpoint_id='%s'" %(ep_id),'where':"service_name='%s'" %(input_dict['service_name'])}
            self.db.pg_update(update)
            self.db.pg_transaction_commit()
            r_dict = {'service_name':input_dict['service_name'],'endpoint_id':ep_id,'service_id':self.service_id,'admin_url':admin_api,'internal_url':internal_api,'public_url':public_api}
            return r_dict
        else:
            self.db.pg_transaction_rollback()
            util.http_codes(ep_rest['response'],ep_rest['reason'])

    #DESC: Delete a cloud service endpoint. Only an admin can delete an endpoint.
    #INPUT: input_dict -service_name - req
    #OUTPUT: OK if deleted else error
    def delete_endpoint(self,input_dict):
        if('service_name' not in input_dict):
            logger.sys_error("The service name was not specified while createing an endpoint.")
            raise Exception("The service name was not specified while createing an endpoint.")
        if(self.is_admin == 0):
            logger.sys_logger("Endpoints can only be crearted by the cloud admin.")
            raise Exception("Endpoints can only be crearted by the cloud admin.")

        #get the cloud name (Region)
        #if('cloud_name' not in input_dict):
        #    try:
        #        get_name = {'select':"param_value",'from':"trans_system_settings",'where':"host_system='%s'" %(self.controller),'and':"parameter='cloud_name'"}
        #        input_dict['cloud_name'] = self.db.pg_select(get_name)
        #    except:
        #        logger.sys_error("Could not retrieve the cloud name from the trans_system_settings db.")
        #        raise Exception("Could not retrieve the cloud name from the trans_system_settings db.")

        #get ip info from the DB for the endpoint creaton
        try:
            #get_ips = {'select':"admin_api_ip,int_api_ip,api_ip",'from':"trans_system_settings",'where':"host_system='%s'" %(self.controller)}
            get_ips = {'select':"param_value",'from':"trans_system_settings",'where':"host_system='%s'" %(self.controller),'and':"parameter='api_ip'"}
            self.api_ips = self.db.pg_select(get_ips)
        except:
            logger.sql_error("Could not retrieve the api ips to create endpoints with.")
            raise Exception("Could not retrieve the api ips to create endpoints with.")

        #Build the endpoints for the service in question
        #get the service info from the DB
        try:
            #Get pre populated values from the transcirrus db. Needed to build service catalog and endpoints in OpenStack
            get_serv_info = {'select':"service_id,service_endpoint_id",'from':"trans_service_settings",'where':"service_name='%s'" %(input_dict['service_name'])}
            self.get_service = self.db.pg_select(get_serv_info)
            if(not self.get_service):
                #if the service name is bogus it will fail
                logger.sys_error("Could not find the service %s." %(input_dict['service_name']))
                raise Exception("Could not find the service %s." %(input_dict['service_name']))
        except:
            logger.sql_error("Could not get the service info for OpenStack %s service from database." %(input_dict['service_name']))
            raise Exception("Could not get the service info for OpenStack %s service from database." %(input_dict['service_name']))

        #connect to the API
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")
        
        #add the service to the service catalog
        body = ""
        header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json"}
        function = 'DELETE'
        api_path = '/v2.0/OS-KSADM/services/%s' %(self.get_service[0][0])
        token = self.adm_token
        sec = 'FALSE'
        rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
        rest = api.call_rest(rest_dict)
        if(rest['response'] == 204):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            #update service table with ips and service id
            self.db.pg_transaction_begin()
            update = {'table':"trans_service_settings",'set':"service_id='NULL',service_admin_ip='NULL',service_int_ip='NULL',service_public_ip='NULL',service_endpoint_id='NULL'",'where':"service_name='%s'" %(input_dict['service_name'])}
            self.db.pg_update(update)
            self.db.pg_transaction_commit()
            return 'OK'
        else:
            self.db.pg_transaction_rollback()
            util.http_codes(rest['response'],rest['reason'])
        """
        WHEN THE SERVICE IS DELETED IT APPEARS AS THOUGH THE ENDPOINT IS DELETED AUTOMATICALLY
        KEEPING THIS JUST IN CASE SOMETHING CHANGES
        ep_body = ""
        ep_header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json"}
        ep_function = 'DELETE'
        ep_api_path = '/v2.0/endpoints/%s' %(self.get_service[0][1])
        ep_token = self.adm_token
        ep_sec = 'FALSE'
        ep_rest_dict = {"body": ep_body, "header": ep_header, "function":ep_function, "api_path":ep_api_path, "token":ep_token, "sec":ep_sec}
        ep_rest = api.call_rest(ep_rest_dict)
        print ep_rest
        if(ep_rest['response'] == 204):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(ep_rest['response'],ep_rest['reason']))
            update = {'table':"trans_service_settings",'set':"service_endpoint_id='NULL'",'where':"service_name='%s'" %(input_dict['service_name'])}
            self.db.pg_update(update)
            return "OK"
        else:
            util.http_codes(ep_rest['response'],ep_rest['reason'])
        """
    
    def get_endpoint(self,input_dict):
        """
        DESC: Get the attribute info for a specific cloud service endpoint
        INPUT: input_dict -cloud_name - op ciac cloud name is used
                          -service_name - req
        OUTPUT: r_dict - endpoint_id
                       - endpoint_version
                       - service_name
                       - admin_url
                       - internal_url
                       - public_url
        """
        if(('cloud_name' not in input_dict) or (input_dict['cloud_name'] == '')):
            #Get the defualt cloud name from the config.py file
            input_dict['cloud_name'] == config.CLOUD_NAME
        
        print "not implemented"

    #DESC: List the cloud endpoints for the services configured in openstack
    #INPUT: self object
    #OUTPUT: array of r_dict -service_name
    #                        -service_id
    #                        -admin_url
    #                        -internal_url
    #                        -public_url
    def list_endpoints(self):
        print "not implemented"
        
    #DESC: update a cloud service endpoint configured in openstack
    #      function will actually delete that endpoint and then
    #      recreate the endpoint.
    #INPUT: update_dict -cloud_name
    #                   -service_name
    #                   -admin_url
    #                   -internal_url
    #                   -public_url
    #OUTPUT: array of r_dict -service_name
    #                        -service_id
    #                        -admin_url
    #                        -internal_url
    #                        -public_url
    def update_endpoint(self,update_dict):
        print "not implemented"
        """
#REQ: curl -i -X GET http://192.168.10.30:35357/v2.0/endpoints -H "User-Agent: python-keystoneclient" -H "X-Auth-Token: cheapass"
        #submit the values passed in 
        api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
        api = caller(api_dict)
        logger.sys_info("Tenant id was passed in %s." %(self.username))
        body = '{"auth":{"passwordCredentials":{"username": "%s", "password":"%s"}, "tenantId":"%s"}}' %(self.username,self.password,self.project_id)
        headers = {"X-Auth-Token":token, "Content-Type": "application/json", "Accept": "application/json"}
        function = 'GET'
        api_path = '/v2.0/tokens/%s/endpoints' %(permissions['token'])
        token = permissions['token']
        sec = 'FALSE'
        #security - http/https
        if(permissions['sec'] and permission['sec'] == 'TRUE'):
            logger.sys_info("Security paramters have been passed sec: %s" %(permissions['sec']))
            sec = 'TRUE'
        rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
        rest = api.call_rest(rest_dict)

        if((rest['response'] == 200) or (rest['response'] == 203)):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            apitoken = load['access']['token']['id']
            return apitoken
        else:
            _http_codes(rest['response'],rest['reason'])
        """
