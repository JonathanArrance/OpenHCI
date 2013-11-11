#!/usr/bin/python
# Used manage all layer 3 operations(routing,floating ip)
# Refer to http://docs.openstack.org/api/openstack-network/2.0/content/router_ext.html
# for all API information.

import sys
import json

import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

class routing_ops:
    #DESC:
    #INPUT:
    #OUTPUT:
    def __init__(self,user_dict):
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        # user_dict = {"username":self.username,"password":self.user_pass,"project_id":exist[0][7],"status_level":status_level,"user_level":user_level,"is_admin": is_admin,"token":token}
        else:
            self.username = user_dict['username']
            self.password = user_dict['password']
            self.project_id = user_dict['project_id']
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
            self.api_ip = config.DEFAULT_API_IP

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")
            raise Exception("No admin tokens passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if ((self.status_level > 2) or (self.status_level < 0)):
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

    def list_routers(self):
        """
        DESC: List the routers that are present in a project.
        INPUT: self object
        OUTPUT: array of r_dict - router_name
                                - router_status
                                - router_id
        ACCESS:All user types can list the routers in a project. Admin can list all virtual routers.
        NOTE: this info can be gathered from the transcirrus db
        """
        try:
            if(self.is_admin == 1):
                self.select_router = {'select':"router_name,router_id,router_status",'from':"trans_routers"}
            else:
                self.select_router = {'select':"router_name,router_id,router_status",'from':"trans_routers",'where':"proj_id='%s'"%(self.project_id)}
            routers = self.db.pg_select(self.select_router)
        except:
            logger.sql_error("Could not find routers in project %s"%(self.project_id))
            raise Exception("Could not find routers in project %s"%(self.project_id))

        r_array = []
        for router in routers:
            r_dict = {'router_name':router['router_name'],'router_id':router['router_id'],'router_status':router['router_status']}
            r_array.append(r_dict)

        if(len(r_array) == 0):
            logger.sys_info('No routers were found in project %s' %(self.project_id))

        return r_array

    def get_router(self,router_id):
        """
        DESC: Get the information for a specific router.
        INPUT: router_id
        OUTPUT: r_dict - router_name
                       - router_status
                       - router_id
                       - project_id
                       - network_id
                       - external_gateway
                       - external_ip
                       - admin_state_up
        ACCESS: All user types can get the information for a router in their project. Admin can
                get info on any router.
        NOTE: this info can be gathered from the transcirrus db
        """
        try:
            if(self.is_admin == 1):
                self.get_router = {'select':"*",'from':"trans_routers",'where':"router_id='%s'"%(router_id)}
            else:
                self.get_router = {'select':"*",'from':"trans_routers",'where':"router_id='%s'"%(router_id),'and':"proj_id='%s'"%(self.project_id)}
            router = self.db.pg_select(self.get_router)
        except:
            logger.sql_error("Could not find router %s"%(router_id))
            raise Exception("Could not find router %s"%(router_id))

        r_dict = {'router_name':router[0][1],'router_status':router[0][8],'router_id':router[0][2],'project_id':self.project_id,'network_id':router[0][3],'external_gateway':router[0][5],
                  'external_ip':router[0][6],'admin_state_up':router[0][9],'internal_port':router[0][7]}

        return r_dict

    def add_router(self,router_name):
        """
        DESC: Add a new router to a project.
        INPUT: - router_name
        OUTPUT: r_dict - router_name
                       - router_id
        ACCESS: Admin can create a router in their project
        NOTES:
        """
        #curl -i http://192.168.10.30:9696/v2.0/routers.json -X POST -d '{"router": {"tenant_id": "cfc66ab189244f66bf3de56f55ebe72d", "name": "jonarrance", "admin_state_up": true}}'
        if(router_name == ''):
            logger.sys_error("A router name was not specified.")
            raise Exception("A router name was not specified.")

        if(self.user_level <= 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #add the new user to openstack
                body = '{"router": {"tenant_id": "%s", "name": "%s", "admin_state_up": true}}' %(self.project_id,router_name)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2.0/routers'
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 201
                if(rest['response'] == 201):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    load = json.loads(rest['data'])
                    self.db.pg_transaction_begin()
                    #insert new net info
                    insert_dict = {"router_name":router_name,"router_id":load['router']['id'],"proj_id":self.project_id,"router_status":'ACTIVE',
                                   "router_admin_state_up":"true"}
                    self.db.pg_insert("trans_network_settings",insert_dict)
                    self.db.pg_transaction_commit()
                    r_dict = {'router_name':router_name,'router_id':load['router']['id']}
                    return r_dict
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not add a new public network to Neutron.")
                raise Exception("Could not add a new public network to Neutron.")
        else:
            logger.sys_error("Only an admin or a power user can create a new router.")
            raise Exception("Only an admin or a power user can create a new router.")

    def update_router(self,update_dict):
        """
        DESC: Update the basic router information.
        INPUT: update_dict - router_id - req
                           - router_name - op
                           - router_external_gateway - op - ext_netwok_id
                           - router_snat - not used
                           - router_admin_state_up(true/false) - op - default true
        OUTPUT: r_dict - router_name
                       - router_admin_state
        ACCESS: Only an admin can update a routers info.
        NOTES:
        """
        if(('router_id' not in update_dict) or (update_dict['router_id'] == '')):
            logger.sys_error("No router id given.")
            raise Exception("No router id given.")

        if(self.user_level <= 1):
            #get the original info
            router = self.get_router(update_dict['router_id'])
            if(router['router_name'] != update_dict['router_name']):
                self.name = update_dict['router_name']
            else:
                self.name = router['router_name']

            if('router_external_gateway' not in update_dict):
                self.ext_gateway = router['external_gateway']
            else:
                self.ext_gateway = update['external_gateway']

            if('router_admin_state_up' not in update_dict):
                self.state == 'true'
            else:
                self.state = update_dict['router_admin_state_up'].lower()

            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #add the new user to openstack
                body = '{"router": {"external_gateway_info": {"network_id": "%s","enable_snat": true}, "name": "%s", "admin_state_up": "%s"}}' %(self.ext_gateway,self.name,self.state)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'PUT'
                api_path = '/v2.0/routers/%s' %(update_dict['router_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 201
                if(rest['response'] == 200):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    load = json.loads(rest['data'])
                    self.db.pg_transaction_begin()
                    #insert new net info
                    update = {'table':'trans_router','set':"router_name='%s',router_ext_gateway='%s',router_admin_state_up='%s'"%(self.name,self.ext_gateway,self.state),'where':"router_id='%s'"%(update_dict['router_id'])}
                    self.db.pg_update(update)
                    self.db.pg_transaction_commit()
                    r_dict = {'router_name':self.name,'router_admin_state':self.state}
                    return r_dict
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not add a new public network to Neutron.")
                raise Exception("Could not add a new public network to Neutron.")
        else:
            logger.sys_error("Only an admin or a power user can create a new network.")
            raise Exception("Only an admin or a power user can create a new network.")

    #DESC: Remove a router from the project. Only admins can remove
    #      routers from a project. If any networks are attached an error
    #      will occure.
    #INPUT: router_name
    #OUTPUT: OK or error
    def delete_router(self,router_name):
        """
        DESC: Remove a router from the project.
        INPUT: router_name
        OUTPUT: OK or ERROR
        ACCESS: Only admins can remove routers from a project. If any networks are attached an error
                will occure.
        NOTES: none
        """
        
    #DESC: Add an internal router network interface to the virtual layer3
    #      router. Only admins can add an internal interface to the router.
    #INPUT: add_dict - router_name
    #                - subnet_name
    #OUTPUT: r_dict - subnet_name
    #               - subnet_id
    #               - router_id
    #NOTE: transcirrus db will have to be updated accordingly
    def add_router_internal_interface(self,add_dict):
        print "not implemented"
        
    #DESC: Remove an internal router network interface to the virtual layer3
    #      router. Only admins can remove an internal interface to the router.
    #INPUT: remove_dict - router_name
    #                   - subnet_name
    #OUTPUT: r_dict - router_name
    #               - subnet_name
    #               - subnet_id
    #NOTE: transcirrus db will have to be updated accordingly
    def delete_router_internal_interface(self,remove_dict):
        print "not implemented"
        
    #DESC: Add an external gateway network interface to the virtual layer3
    #      router. Only admins can add an extrnal interface to the router.
    #INPUT: add_dict - router_name
    #                - ext_net_name
    #OUTPUT: r_dict - router_name
    #               - ext_net_name
    #               - ext_net_id
    #NOTE: transcirrus db will have to be updated accordingly
    def add_router_external_interface(self,add_dict):
        print "not implemented"
        
    #DESC: Remove an external gateway network interface from the virtual layer3
    #      router. Only admins can remove an extrnal interface from the router.
    #INPUT: remove_dict - router_name
    #                   - ext_net_name
    #OUTPUT: r_dict - router_name
    #               - ext_net_name
    #               - ext_net_id
    #NOTE: transcirrus db will have to be updated accordingly
    def delete_router_external_interface(self,remove_dict):
        print "not implemented"
    

#Refer to http://docs.openstack.org/api/openstack-network/2.0/content/router_ext_ops_floatingip.html

    #DESC: List the availabel floating ips in a project. Any user type can list
    #      the floating ips in a project.
    #INPUT: self object
    #OUTPUT: array of r_dict - fixed_ip
    #                        - floating_ip
    #                        - router_id
    #                        - floating_ip_id
    #NOTE: this info can be obtained from the transcirrus db
    def list_floating_ips(self):
        print "not implemented"
        
    #DESC: Return the mappings between the floating ip and the virtual instance
    #      fixed ip.
    #INPUT: floating_ip_id
    #OUTPUT: r_dict - floating_ip
    #               - fixed_ip
    def get_floating_ip(self,floating_ip_id):
        print "not implemented"
        
    #DESC: Add a new floating ip to a project. Only admins can add a new floating ip
    #      to the project.
    #INPUT: ext_network_name
    #OUTPUT: r_dict - floating_ip
    #               - floating_ip_id
    #NOTE: update the transcirrus db accoridingly
    def add_floating_ip(self):
        print "not implemented"
        
    #DESC: Update the floating ip attachments in the project. Admins and power users can
    #      attach floating ip addresses to instances in their project.
    #INPUT: update_dict - floating_ip - req
    #                   - instance_name - req
    #OUTPUT: r_dict - floating_ip
    #               - instance_name
    #               - instance_id
    #NOTE: since the ports are not implemented in alpo.0 we will use the nova call.
    #body = '{"addFloatingIp": {"address": "%s"}}' port 8774
    def update_floating_ip(self,update_dict):
        print "not implemented"
        
    #DESC: Removes a floating ip from the tenant. Only admins can delete a floating
    #      ip from the project
    #INPUT: floating_ip
    #OUTPUT: OK is successful or error
    #NOTE: the nova api is used to remove a floating ip from a specific virtual instance.
    def remove_floating_ip(self,floating_ip):
        print "not implemented"
