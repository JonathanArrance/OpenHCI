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
        reload(config)

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

            #used to overide the value in the DB, mostly used during setup or reinit
            if('api_ip' in user_dict):
                #NOTE may have to add an IP check
                self.api_ip = user_dict['api_ip']
            else:
                self.api_ip = config.API_IP

            #get the default cloud controller info
            self.controller = config.CLOUD_CONTROLLER

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

    def __del__(self):
        self.db.pg_close_connection()


    def create_endpoint(self,input_dict):
        """
        DESC: create a new cloud service endpoint. This function will also
              add the service to the service catalog. Only the cloud admin can
              create a new cloud service endpoint.
        INPUT: input_dict -cloud_name - op ciac cloud name is used
                          -service_name - req
        OUPUT: r_dict -endpoint_id
                      -service_name
                      -service_id
                      -admin_url
                      -internal_url
                      -public_url
        ACCESS: Only the admin can create a service endpoint.
        NOTES: This will also create the service catalog entry!
        """
        if('service_name' not in input_dict):
            logger.sys_error("The service name was not specified while createing an endpoint.")
            raise Exception("The service name was not specified while createing an endpoint.")
        if(self.is_admin == 0):
            logger.sys_error("Endpoints can only be crearted by the admin.")
            raise Exception("Endpoints can only be crearted by the admin.")

        #get the cloud name (Region)
        if('cloud_name' not in input_dict):
            input_dict['cloud_name'] = config.CLOUD_NAME
            #try:
            #    get_name = {'select':"param_value",'from':"trans_system_settings",'where':"host_system='%s'" %(self.controller),'and':"parameter='cloud_name'"}
            #    input_dict['cloud_name'] = self.db.pg_select(get_name)
            #except:
            #    logger.sys_error("Could not retrieve the cloud name from the trans_system_settings db.")
            #    raise Exception("Could not retrieve the cloud name from the trans_system_settings db.")

        #get ip info from the DB for the endpoint creaton
        try:
            #this will need to be chabged if we use different ips for endpoints
            #get_ips = {'select':"admin_api_ip,int_api_ip,api_ip",'from':"trans_system_settings",'where':"host_system='%s'" %(self.controller)}
            #HACK - we need to use the api ip - better yet use the api ips for admin, public,internal
            get_ips = {'select':"param_value",'from':"trans_system_settings",'where':"host_system='%s'" %(self.controller),'and':"parameter='int_api_ip'"}#was api_ip caused error in multinde system. Needs to be locked to 172.24.24.10
            self.ep_ip = self.db.pg_select(get_ips)
        except:
            logger.sql_error("Could not retrieve the api ips to create endpoints with.")
            raise Exception("Could not retrieve the api ips to create endpoints with.")

        try:
            get_public_ips = {'select':"param_value",'from':"trans_system_settings",'where':"host_system='%s'" %(self.controller),'and':"parameter='api_ip'"}
            self.pub_ip = self.db.pg_select(get_public_ips)
        except:
            logger.sql_error("Could not retrieve the public api ip to create endpoints with.")
            raise Exception("Could not retrieve the public api ip to create endpoints with.")

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

            if(input_dict['service_name'] == 'keystone'):
                get_serv_info = {'select':"service_port,service_api_version",'from':"trans_service_settings",'where':"service_name='keystone_admin'"}
                get_service = self.db.pg_select(get_serv_info)
                self.admin_api = "http://%s:%s%s" %(self.ep_ip[0][0],get_service[0][0],get_service[0][1])

            if(input_dict['service_name'] == 'swift'):
                get_serv_info = {'select':"service_port,service_api_version",'from':"trans_service_settings",'where':"service_name='swift_admin'"}
                get_service = self.db.pg_select(get_serv_info)
                self.admin_api = "http://%s:%s%s" %(self.ep_ip[0][0],get_service[0][0],get_service[0][1])

            if(input_dict['service_name'] == 'heat'):
                get_serv_info = {'select':"service_port,service_api_version",'from':"trans_service_settings",'where':"service_name='heat_cfn'"}
                get_service = self.db.pg_select(get_serv_info)
                self.admin_api = "http://%s:%s%s" %(self.ep_ip[0][0],get_service[0][0],get_service[0][1])

            if(input_dict['service_name'] == 'ec2'):
                get_serv_info = {'select':"service_port,service_api_version",'from':"trans_service_settings",'where':"service_name='ec2_admin'"}
                get_service = self.db.pg_select(get_serv_info)
                self.admin_api = "http://%s:%s%s" %(self.ep_ip[0][0],get_service[0][0],get_service[0][1])

            if(input_dict['service_name'] == 'nova'):
                self.admin_api = "http://%s:%s%s" %(self.ep_ip[0][0],self.get_service[0][0],self.get_service[0][1])
        except:
            logger.sql_error("Could not get the service info for OpenStack %s service from database." %(input_dict['service_name']))
            raise Exception("Could not get the service info for OpenStack %s service from database." %(input_dict['service_name']))

        #build the endpoints
        if(self.get_service[0][1] == 'NULL'):
            self.get_service[0][1] = ""

        self.public_api = "http://%s:%s%s" %(self.ep_ip[0][0],self.get_service[0][0],self.get_service[0][1])
        if(input_dict['service_name'] == 'swift'):
            self.public_api = "http://%s:%s%s" %(self.pub_ip[0][0],self.get_service[0][0],self.get_service[0][1])
        if(input_dict['service_name'] == 'nova'):
            self.public_api = "http://%s:%s%s" %(self.pub_ip[0][0],self.get_service[0][0],self.get_service[0][1])

        internal_api = "http://%s:%s%s" %(self.ep_ip[0][0],self.get_service[0][0],self.get_service[0][1])

        #HUGE HACK
        if(input_dict['service_name'] != 'keystone'):
            if(input_dict['service_name'] != 'swift'):
                self.admin_api = "http://%s:%s%s" %(self.ep_ip[0][0],self.get_service[0][0],self.get_service[0][1])

        #connect to the API
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            #add the service to the service catalog
            body = '{"OS-KSADM:service": {"type": "%s", "name": "%s", "description": "%s"}}' %(self.get_service[0][3],input_dict['service_name'],self.get_service[0][2])
            header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json"}
            function = 'POST'
            api_path = '/v2.0/OS-KSADM/services'
            token = self.adm_token
            sec = 'FALSE'
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
            if(self.ep_ip):
                rest_dict['api_ip'] = self.ep_ip[0][0]
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not add a new service catalog entry.")
            raise Exception("Could not add a new service catalog entry.")

        if(rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            #update service table with ips and service id
            self.service_id = load['OS-KSADM:service']['id']
            try:
                self.db.pg_transaction_begin()
                update = {'table':"trans_service_settings",'set':"service_id='%s',service_admin_ip='%s',service_int_ip='%s',service_public_ip='%s'" %(self.service_id,self.ep_ip[0][0],self.ep_ip[0][0],self.ep_ip[0][0]),'where':"service_name='%s'" %(input_dict['service_name'])}
                self.db.pg_update(update)
                if(input_dict['service_name'] == 'keystone'):
                    update = {'table':"trans_service_settings",'set':"service_id='%s',service_admin_ip='%s',service_int_ip='%s',service_public_ip='%s'" %(self.service_id,self.ep_ip[0][0],self.ep_ip[0][0],self.pub_ip[0][0]),'where':"service_name='keystone_admin'"}
                    self.db.pg_update(update)
                if(input_dict['service_name'] == 'swift'):
                    update = {'table':"trans_service_settings",'set':"service_id='%s',service_admin_ip='%s',service_int_ip='%s',service_public_ip='%s'" %(self.service_id,self.ep_ip[0][0],self.ep_ip[0][0],self.pub_ip[0][0]),'where':"service_name='swift_admin'"}
                    self.db.pg_update(update)
            except Exception as e:
                self.db.pg_transaction_rollback()
                logger.sql_error("%s"%(e))
                raise
            else:
                self.db.pg_transaction_commit()
        else:
            util.http_codes(rest['response'],rest['reason'])

        try:
            ep_body = '{"endpoint": {"adminurl": "%s", "service_id": "%s", "region": "%s", "internalurl": "%s", "publicurl": "%s"}}' %(self.admin_api,self.service_id,input_dict['cloud_name'],internal_api,self.public_api)
            ep_header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json"}
            ep_function = 'POST'
            ep_api_path = '/v2.0/endpoints'
            ep_token = self.adm_token
            ep_sec = 'FALSE'
            ep_rest_dict = {"body":ep_body, "header":ep_header, "function":ep_function, "api_path":ep_api_path, "token":ep_token, "sec":ep_sec}
            ep_rest = api.call_rest(ep_rest_dict)
        except:
            logger.sys_error("Could not add a new service endpoint.")
            raise Exception("Could not add a new service endpoint.")

        if(ep_rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(ep_rest['response'],ep_rest['reason']))
            load = json.loads(ep_rest['data'])
            ep_id = load['endpoint']['id']
            try:
                self.db.pg_transaction_begin()
                update = {'table':"trans_service_settings",'set':"service_endpoint_id='%s'" %(ep_id),'where':"service_name='%s'" %(input_dict['service_name'])}
                self.db.pg_update(update)
                if(input_dict['service_name'] == 'keystone'):
                    update = {'table':"trans_service_settings",'set':"service_endpoint_id='%s'" %(ep_id),'where':"service_name='keystone_admin'"}
                    self.db.pg_update(update)
                if(input_dict['service_name'] == 'swift'):
                    update = {'table':"trans_service_settings",'set':"service_endpoint_id='%s'" %(ep_id),'where':"service_name='swift_admin'"}
                    self.db.pg_update(update)
            except Exception as e:
                logger.sql_error("%s"%(e))
                raise
            else:
                self.db.pg_transaction_commit()
                r_dict = {'service_name':input_dict['service_name'],'endpoint_id':ep_id,'service_id':self.service_id,'admin_url':self.admin_api,'internal_url':internal_api,'public_url':self.public_api}
                return r_dict
        else:
            self.db.pg_transaction_rollback()
            util.http_codes(ep_rest['response'],ep_rest['reason'])

    def delete_endpoint(self,service_name):
        """
        DESC: Delete a cloud service endpoint. Only an admin can delete an endpoint.
        INPUT: service_name - req
        OUTPUT: OK if deleted else error
        ACCESS: Only the admin can delete a service endpoint
        NOTES: using an input dictionary because I may need to add a few more
               vars when we expand to multiple cloud controllers in the future.
               Deleteing an endpoint implicitly deletes a service catalog entry
        """
        if(service_name == ''):
            logger.sys_error('The service name was blank')
            raise Exception('The service name was blank')
        if(self.is_admin == 0):
            logger.sys_error("Endpoints can only be crearted by the cloud admin.")
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
            self.api_ip = self.db.pg_select(get_ips)
        except:
            logger.sql_error("Could not retrieve the api ips to create endpoints with.")
            raise Exception("Could not retrieve the api ips to create endpoints with.")

        #Build the endpoints for the service in question
        #get the service info from the DB
        try:
            #Get pre populated values from the transcirrus db. Needed to build service catalog and endpoints in OpenStack
            get_serv_info = {'select':"service_id,service_endpoint_id",'from':"trans_service_settings",'where':"service_name='%s'" %(service_name)}
            self.get_service = self.db.pg_select(get_serv_info)
            #print self.get_service
            if(not self.get_service):
                #if the service name is bogus it will fail
                logger.sys_error("Could not find the service %s." %(service_name))
                raise Exception("Could not find the service %s." %(service_name))
        except:
            logger.sql_error("Could not get the service info for OpenStack %s service from database." %(service_name))
            raise Exception("Could not get the service info for OpenStack %s service from database." %(service_name))

        #connect to the API
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")
        
        try:
            body = ""
            header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json"}
            function = 'DELETE'
            api_path = '/v2.0/OS-KSADM/services/%s' %(self.get_service[0][0])
            token = self.adm_token
            sec = 'FALSE'
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
            if(self.api_ip):
                rest_dict['api_ip'] = self.api_ip[0][0]
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error("Could not delete the %s endpoint. %s"%(service_name,e))
            raise Exception("Could not delete the %s endpoint. %s"%(service_name,e))

        if(rest['response'] == 204):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            #update service table with ips and service id
            try:
                self.db.pg_transaction_begin()
                update = {'table':"trans_service_settings",'set':"service_id='NULL',service_admin_ip='NULL',service_int_ip='NULL',service_public_ip='NULL',service_endpoint_id='NULL'",'where':"service_name='%s'" %(service_name)}
                self.db.pg_update(update)
            except Exception as e:
                self.db.pg_transaction_rollback()
                logger.sql_error("%s"%(e))
                raise
            else:
                self.db.pg_transaction_commit()
                return 'OK'
        else:
            util.http_codes(rest['response'],rest['reason'])

    def get_endpoint(self,service_name):
        """
        DESC: Get the attribute info for a specific cloud service endpoint
        INPUT: service_name - req
        OUTPUT: r_dict - endpoint_id
                       - service_id
                       - service_type
                       - admin_url
                       - internal_url
                       - public_url
        ACCESS: only an admin can list the api endpoints on the system
        NOTES: May need to add cloud name as we expand to support more cloud name spaces
        """
        if(service_name == ''):
            logger.sys_error('The service name was blank')
            raise Exception('The service name was blank')

        try:
            get_endpoint = {'select':"service_type,service_admin_ip,service_int_ip,service_public_ip,service_api_version,service_endpoint_id,service_port,service_id",
                            'from':'trans_service_settings','where':"service_name='%s'"%(service_name)}
            endpoint = self.db.pg_select(get_endpoint)
        except:
            logger.sys_error("Could not get endpoint for service %s"%(service_name))
            raise Exception("Could not get endpoint for service %s"%(service_name))

        #the port is an int???
        #that has to be changed
        if(endpoint[0][4] == 'NULL'):
            api = ""
        else:
            api = endpoint[0][4]

        admin_url ="http://"+endpoint[0][1]+":"+str(endpoint[0][6])+api
        public_url ="http://"+endpoint[0][3]+":"+str(endpoint[0][6])+api
        int_url = "http://"+endpoint[0][2]+":"+str(endpoint[0][6])+api

        r_dict = {'endpoint_id':endpoint[0][5],'service_id':endpoint[0][7],'service_type':endpoint[0][0],'admin_url':admin_url,'internal_url':int_url,'public_url':public_url}
        return r_dict

    def list_endpoints(self):
        """
        DESC: List the cloud endpoints for the services configured in openstack
        INPUT: self object
        OUTPUT: array of r_dict -service_name
                                -endpoint_id
                                -endpoint_desc
        ACCESS: Only admins can list the service endpoints
        NOTE:
        """
        if(self.is_admin == 1):
            try:
                #only get the service public ip since as of now admin,internal,public are all the same
                endpoints = {'select':"service_name,service_endpoint_id,service_desc",'from':"trans_service_settings"}
                ends = self.db.pg_select(endpoints)
            except:
                logger.sql_error("Could not connect to the Transcirrus db.")
                raise Exception("Could not connect to the Transcirrus db.")

            r_array = []
            for end in ends:
                r_dict = {}
                r_dict['service_name'] = end[0].rstrip()
                r_dict['endpoint_id'] = end[1].rstrip()
                r_dict['endpoint_desc'] = end[2].rstrip()
                r_array.append(r_dict)

            return r_array

    def update_endpoint(self,update_dict):
        print "not implemented"
        """
        DESC: update a cloud service endpoint configured in openstack
          function will actually delete that endpoint and then
          recreate the endpoint.
        INPUT: update_dict -cloud_name
                           -service_name
                           -admin_url
                           -internal_url
                           -public_url
        OUTPUT: array of r_dict -service_name
                                -service_id
                                -admin_url
                                -internal_url
                                -public_url
        """

    def list_service_catalog(self):
        """
        DESC: List the service endpoints available
        INPUT: None
        OUTPUT: Array of dictionaries r_dict - service_name
                                             - service_id
                                             - service_type
        ACCESS: Only admins can list the service catalog
        NOTES: none
        """
        if(self.is_admin == 1):
            try:
                get_catalog = {'select':"service_name,service_id,service_type",'from':"trans_service_settings",'where':"service_endpoint_id != '%s'"%('NULL')}
                catalog = self.db.pg_select(get_catalog)
            except:
                logger.sql_error("Could not get the list of service names form the Transcirrus db.")
                raise Exception("Could not get the list of service names form the Transcirrus db.")

        r_array = []
        for x in catalog:
            r_dict = {'service_name':x[0].rstrip(),'service_id':x[1].rstrip(),'service_type':x[2].rstrip()}
            r_array.append(r_dict)
        return r_array
    '''
    def create_service_entry(self,service_name):
        """
        DESC: create a new service catalog entry, if one exsists raise an error.
        INPUT: service_name
        OUTPUT: r_dict - service_name
                       - service_id
                       - service_type
        ACCESS: Only admins can list the service catalog
        NOTES: This should allways be called before creating and endpoint.
        """
        if('service_name' == ''):
            logger.sys_error('The service name was blank')
            raise Exception('The service name was blank')

        if(self.is_admin == 1):
            #get all fo the serivce names
            try:
                get_services = {'select':"service_type,service_desc",'from':"trans_service_settings",'where':"service_name='%s'"%(service_name)}
                services = self.db.pg_select(get_services)
                print services
            except:
                logger.sql_error("Could not get the list of service names form the Transcirrus db.")
                raise Exception("Could not get the list of service names form the Transcirrus db.")

            #connect to the API
            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the Keystone API")
                raise Exception("Could not connect to the Keystone API")
    
            try:
                #add the service to the service catalog
                body = '{"OS-KSADM:service": {"type": "%s", "name": "%s", "description": "%s"}}'%(services[0][0],service_name,services[0][1])
                print body
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json"}
                function = 'POST'
                api_path = '/v2.0/OS-KSADM/services'
                token = self.adm_token
                print token
                sec = 'FALSE'
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
                print rest
                if(rest['response'] == 200):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    #update service table with ips and service id
                    #load = json.load(rest['data'])
                    #print load
                    #self.db.pg_transaction_begin()
                    #update = {'table':"trans_service_settings",'set':"service_id='%s'",'where':"service_name='%s'" %(service_name)}
                    #self.db.pg_update(update)
                    #self.db.pg_transaction_commit()
                    #r_dict = {'service_name':service_name,'service_id':load['OS-KSADM:service']['id'],'service_type':services[0][0]}
                    #return r_dict
                else:
                    self.db.pg_transaction_rollback()
                    util.http_codes(rest['response'],rest['reason'])
            except:
                logger.sys_error("Could not add a new service catalog entry.")
                raise Exception("Could not add a new service catalog entry.")
    '''

    def delete_service_entry(self,service_name):
        """
        DESC: delete a service catalog entry.
        INPUT: service_name
        OUTPUT: OK - success
                ERROR - fail
        ACCESS: Only admins can delete the service catalog entry
        NOTES: If an endpoint is set up for the serivce entry an error will be raised.
               You will have to delete the endpoint first.
        """
        if('service_name' == ''):
            logger.sys_error('The service name was blank')
            raise Exception('The service name was blank')

        if(self.is_admin == 1):
            #check if the service nameis valid
            try:
                get_service_id = {'select':"service_id",'from':"trans_service_settings",'where':"service_name='%s'"%(service_name)}
                service_id = self.db.pg_select(get_service_id)
            except:
                logger.sql_error("Could not get the list of service names form the Transcirrus db.")
                raise Exception("Could not get the list of service names form the Transcirrus db.")

            #make sure an endpoint is not set up
            try:
                check_endpoint = {'select':"service_endpoint_id",'from':"trans_service_settings",'where':"service_name='%s'"%(service_name)}
                endpoint_id = self.db.pg_select(check_endpoint)
            except:
                logger.sql_error("Could not get the list of service names form the Transcirrus db.")
                raise Exception("Could not get the list of service names form the Transcirrus db.")

            #if(endpoint_id[0][0] != 'NULL'):
            #    return 'ERROR'

            #connect to the API
            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the Keystone API")
                raise Exception("Could not connect to the Keystone API")

            try:
                body = ''
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json"}
                function = 'DELETE'
                api_path = '/v2.0/OS-KSADM/services/%s'%(service_id[0][0])
                token = self.adm_token
                sec = 'FALSE'
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                if(self.api_ip):
                    rest_dict['api_ip'] = self.api_ip
                rest = api.call_rest(rest_dict)
            except:
                logger.sys_error("Could not remove the service catalog entry.")
                raise Exception("Could not remove the service catalog entry.")

            if(rest['response'] == 204):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                #update service table with ips and service id
                load = json.load(rest['data'])
                try:
                    self.db.pg_transaction_begin()
                    update = {'table':"trans_service_settings",'set':"service_id='NULL'",'where':"service_name='%s'" %(service_name)}
                    self.db.pg_update(update)
                except Exception as e:
                    self.db.pg_transaction_rollback()
                    logger.sql_error("%s"%(e))
                    raise
                else:
                    self.db.pg_transaction_commit()
                    return 'OK'
            else:
                util.http_codes(rest['response'],rest['reason'])
