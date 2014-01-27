#!/usr/bin/python
# Used manage all layer 3 operations(routing,floating ip)
# Refer to http://docs.openstack.org/api/openstack-network/2.0/content/router_ext.html
# for all API information.

import sys
import json

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
from transcirrus.common.api_caller import caller
from transcirrus.component.neutron.ports import port_ops
from transcirrus.common.auth import get_token

from transcirrus.database.postgres import pgsql

class layer_three_ops:
    #DESC:
    #INPUT:
    #OUTPUT:
    def __init__(self,user_dict):
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        # user_dict = {"username":self.username,"password":self.user_pass,"project_id":exist[0][7],"status_level":status_level,"user_level":user_level,"is_admin": is_admin,"token":token}
        else:
            #used to call other classes
            self.auth = user_dict
            self.username = user_dict['username']
            self.password = user_dict['password']
            self.project_id = user_dict['project_id']
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
                
            #get the default cloud controller info
            self.controller = config.CLOUD_CONTROLLER
            self.api_ip = config.API_IP

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if(self.user_level > 1):
            logger.sys_error("Users can not perform Layer 3 operations.")
            raise Exception("Users can not perform Layer 3 operations.")

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

    def list_routers(self,project_id=None):
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
                if(project_id):
                    self.select_router = {'select':"router_name,router_id,router_status",'from':"trans_routers",'where':"proj_id='%s'"%(project_id)}
                else:
                    self.select_router = {'select':"router_name,router_id,router_status",'from':"trans_routers"}
            else:
                self.select_router = {'select':"router_name,router_id,router_status",'from':"trans_routers",'where':"proj_id='%s'"%(self.project_id)}
            routers = self.db.pg_select(self.select_router)
        except:
            logger.sql_error("Could not find routers.")
            raise Exception("Could not find routers.")

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
                       - router_int_sub_id
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

        r_dict = {'router_name':router[0][1],'router_status':router[0][5],'router_id':router[0][2],'project_id':router[0][4],'network_id':router[0][3],'router_int_sub_id':router[0][6],'external_gateway':router[0][10],
                  'external_ip':router[0][11],'admin_state_up':router[0][9],'internal_port':router[0][8]}

        return r_dict

    def add_router(self,router_dict):
        """
        DESC: Add a new router to a project.
        INPUT: router_dict - router_name
                           - project_id
        OUTPUT: r_dict - router_name
                       - router_id
        ACCESS: Admin can create a router in any network
                Power users can create a router in their network.
                Users can not create routers
        NOTES:
        """
        #curl -i http://192.168.10.30:9696/v2.0/routers.json -X POST -d '{"router": {"tenant_id": "cfc66ab189244f66bf3de56f55ebe72d", "name": "jonarrance", "admin_state_up": true}}'
        if((router_dict['router_name'] == '') or ('router_name' not in router_dict)):
            logger.sys_error("A router name was not specified.")
            raise Exception("A router name was not specified.")
        if((router_dict['project_id'] == '') or ('project_id' not in router_dict)):
            logger.sys_error("A project id was not specified.")
            raise Exception("A project id was not specified.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(router_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.user_level == 1):
            if(self.project_id != router_dict['project_id']):
                logger.sys_error("Power user can only create networks in their project.")
                raise Exception("Power user can only create networks in their project.")
        elif(self.user_level == 2):
            logger.sys_error("Users can not remove networks in their project.")
            raise Exception("Users can not remove networks in their project.")

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
                body = '{"router": {"tenant_id": "%s", "name": "%s", "admin_state_up": true}}' %(router_dict['project_id'],router_dict['router_name'])
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2.0/routers'
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not add a new layer 3 device to Neutron.")
                raise Exception("Could not add a new layer 3 device to Neutron.")

            #check the response and make sure it is a 201
            if(rest['response'] == 201):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                try:
                    self.db.pg_transaction_begin()
                    #insert new net info
                    insert_dict = {"router_name":router_dict['router_name'],"router_id":load['router']['id'],"proj_id":router_dict['project_id'],"router_status":'ACTIVE',
                                   "router_admin_state_up":'true'}
                    self.db.pg_insert("trans_routers",insert_dict)
                except:
                    self.db.pg_transaction_rollback()
                    logger.sql_error("Could not add a new layer 3 device to the Transcirrus DB.")
                    raise Exception("Could not add a new layer 3 device to the Transcirrus DB.")
                else:
                    self.db.pg_transaction_commit()
                    r_dict = {'router_name':router_dict['router_name'],'router_id':load['router']['id']}
                    return r_dict
            else:
                util.http_codes(rest['response'],rest['reason'])
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
        NOTES: THIS IS NOT TESTED AND WILL NOT WORK.
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
                body = '{"router": {"external_gateway_info": {"network_id": "%s","enable_snat": true}, "name": "%s", "admin_state_up": "%s"}}' %(self.ext_gateway,self.name,self.state)
                print body
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'PUT'
                api_path = '/v2.0/routers/%s' %(update_dict['router_id'])
                print api_path
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not update router params.")
                raise Exception("Could not update router params.")

            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                try:
                    self.db.pg_transaction_begin()
                    #insert new net info
                    update = {'table':'trans_routers','set':"router_name='%s',router_ext_gateway='%s',router_admin_state_up='%s'"%(self.name,self.ext_gateway,self.state),'where':"router_id='%s'"%(update_dict['router_id'])}
                    self.db.pg_update(update)
                except:
                    self.db.pg_rollback_commit()
                    logger.sql_error("Could not update router params in Transcirrus DB.")
                    raise Exception("Could not update router params in Transcirrus DB.")
                else:
                    self.db.pg_transaction_commit()
                    r_dict = {'router_name':self.name,'router_admin_state':self.state}
                    return r_dict
            else:
                util.http_codes(rest['response'],rest['reason'])
        else:
            logger.sys_error("Only admins and power users can update router params.")
            raise Exception("Only admins and power users can update router params.")

    def delete_router(self,router_id):
        """
        DESC: Remove a router from the project.
        INPUT: router_id
        OUTPUT: OK or ERROR
        ACCESS: Admins can remove a router from any project, power users can only remove a router from their own project.
                If any networks are attached an error will occure.
        NOTES: none
        """
        if(router_id == ''):
            logger.sys_error("No router id was specified.")
            raise Exception("No router id was specified.")

        if(self.user_level <= 1):
            self.flag = True
            try:
                if(self.user_level == 1):
                    #check if the router_id is in the power user project
                    check_router = {'select':"router_name",'from':"trans_routers",'where':"proj_id='%s'"%(self.project_id)}
                    get_router = self.db.pg_select(check_router)
                    if(not get_router):
                        self.flag = False
            except:
                logger.sys_error("Power user could not delete the router %s." %(router_id))
                raise Exception("Power user could not delete router %s." %(router_id))

            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                #if(get_router[0][1] != self.project_id):
                #    self.token = get_token(self.username,self.password,get_router[0][1])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #add the new user to openstack
                body = ''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'DELETE'
                api_path = '/v2.0/routers/%s'%(router_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sql_error("Could not delete the router.")
                raise Exception("Could not delete the router.")

            if(rest['response'] == 204):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                try:
                    self.db.pg_transaction_begin()
                    #insert new net info
                    delete = {"table":'trans_routers',"where":"router_id='%s'"%(router_id)}
                    self.db.pg_delete(delete)
                except:
                    self.db.pg_transaction_rollback()
                    logger.sql_error("Could not delete the router from Transcirrus DB.")
                    raise Exception("Could not delete the router from Transcirrus DB.")
                else:
                    self.db.pg_transaction_commit()
                    return 'OK'
            else:
                util.http_codes(rest['response'],rest['reason'])
                return 'ERROR'
        else:
            logger.sys_error("Only an admin or a power user can delete a router.")
            raise Exception("Only an admin or a power user can delete a router.")

    def add_router_internal_interface(self,add_dict):
        """
        DESC: Add an internal router network interface to the virtual layer3
              router.
        INPUT: add_dict - router_id
                        - subnet_id
                        - project_id
        OUTPUT: r_dict - router_id
                       - router_name
                       - subnet_name
                       - subnet_id
                       - port_id
        ACCESS: Admins can add an internal interface to any router,
                power users can only add internal interfaces for routers
                in their project.
        NOTE: transcirrus db will have to be updated accordingly
        """
        if(('router_id' not in add_dict) or (add_dict['router_id'] == '')):
            logger.sys_error("Can not add internal port to router, no router id given.")
            raise Exception("Can not add internal port to router, no router id given.")
        if(('subnet_id' not in add_dict) or (add_dict['subnet_id'] == '')):
            logger.sys_error("Can not add internal port to router, no subnet id given.")
            raise Exception("Can not add internal port to router, no subnet id given.")
        if(('project_id' not in add_dict) or (add_dict['project_id'] == '')):
            logger.sys_error("Can not add internal port to router, no project id given.")
            raise Exception("Can not add internal port to router, no project id given.")


        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(add_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.user_level == 1):
            if(self.project_id != add_dict['project_id']):
                logger.sys_error("Power user can only create networks in their project.")
                raise Exception("Power user can only create networks in their project.")
        elif(self.user_level == 2):
            logger.sys_error("Users can not add interfaces to routers.")
            raise Exception("Users can not add interfaces to routers.")

        #get the subnet info
        get_sub = None
        try:
            if(self.is_admin == 1):
                get_sub = {'select':"subnet_name,proj_id,net_id",'from':"trans_subnets",'where':"subnet_id='%s'"%(add_dict['subnet_id'])}
            elif(self.user_level == 1):
                get_sub = {'select':"subnet_name,proj_id,net_id",'from':"trans_subnets",'where':"subnet_id='%s'"%(add_dict['subnet_id']),'and':"proj_id='%s'"%(add_dict['project_id'])}
            self.subnet = self.db.pg_select(get_sub)
        except:
            logger.sys_error("No subnet found in project %s."%(add_dict['project_id']))
            raise Exception("No subnet found in project %s."%(add_dict['project_id']))

        try:
            if(self.is_admin == 1):
                get_router = {'select':"*",'from':"trans_routers",'where':"router_id='%s'"%(add_dict['router_id'])}
                self.router = self.db.pg_select(get_router)
            elif(self.user_level):
                get_router = {'select':"*",'from':"trans_routers",'where':"router_id='%s'"%(add_dict['router_id']),'and':"proj_id='%s'"%(add_dict['project_id'])}
                self.router = self.db.pg_select(get_router)
        except:
            logger.sys_error("No router found in project %s."%(add_dict['project_id']))
            raise Exception("No router found in project %s."%(add_dict['project_id']))

        #check if router and subnet are in the same project
        if(self.subnet[0][1] != self.router[0][4]):
            logger.sys_error("Router %s and subnet %s not in project %s."%(add_dict['router_id'],self.subnet[0][0],add_dict['project_id']))
            raise Exception("Router %s and subnet %s not in project %s."%(add_dict['router_id'],self.subnet[0][0],add_dict['project_id']))

        if(self.user_level <= 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":add_dict['project_id']}
                if(self.project_id != add_dict['project_id']):
                    self.token = get_token(self.username,self.password,add_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #add the new user to openstack
                body = '{"subnet_id": "%s"}'%(add_dict['subnet_id'])
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'PUT'
                api_path = '/v2.0/routers/%s/add_router_interface'%(add_dict['router_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sql_error("Could not add an internal port to router.")
                raise Exception("Could not add an internal port to router.")

            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                try:
                    self.db.pg_transaction_begin()
                    #insert new net info
                    update = {'table':'trans_routers','set':"router_int_subnet_id='%s',router_int_conn_id='%s',router_int_port_id='%s',net_id='%s'"%(load['subnet_id'],load['id'],load['port_id'],self.subnet[0][2]),'where':"router_id='%s'"%(add_dict['router_id'])}
                    self.db.pg_update(update)
                except:
                    self.db.pg_transaction_rollback()
                    logger.sql_error("Could not add an internal port to router in Transcirrus DB.")
                    raise Exception("Could not add an internal port to router in Transcirrus DB.")
                else:
                    self.db.pg_transaction_commit()
                    r_dict = {'router_id': add_dict['router_id'],'router_name':self.router[0][1],'subnet_name': self.subnet[0][0],'subnet_id': load['subnet_id'],'port_id': load['port_id']}
                    return r_dict
            else:
                util.http_codes(rest['response'],rest['reason'])
        else:
            logger.sys_error("Users can not add ports to routers.")
            raise Exception("Users can not add ports to routers.")

    def delete_router_internal_interface(self,remove_dict):
        """
        DESC: Remove an internal router network interface to the virtual layer3
              router.
        INPUT: remove_dict - router_id
                           - subnet_id
                           - project_id
        OUTPUT: OK - success
                ERROR - failure
        ACCESS: Admins can remove an internal interface to the router. Power users
                can only remove interfaces for routers in their project.
        NOTE: transcirrus db will have to be updated accordingly
        """
        if(('router_id' not in remove_dict) or (remove_dict['router_id'] == '')):
            logger.sys_error("Can not add internal port to router, no router id given.")
            raise Exception("Can not add internal port to router, no router id given.")
        if(('subnet_id' not in remove_dict) or (remove_dict['subnet_id'] == '')):
            logger.sys_error("Can not add internal port to router, no subnet id given.")
            raise Exception("Can not add internal port to router, no subnet id given.")
        if(('project_id' not in remove_dict) or (remove_dict['project_id'] == '')):
            logger.sys_error("Can not add internal port to router, no project id given.")
            raise Exception("Can not add internal port to router, no project id given.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(remove_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        #verify the subnet exisits
        try:
            get_sub = None
            if(self.is_admin == 1):
                get_sub = {'select':"proj_id,subnet_name",'from':"trans_subnets",'where':"subnet_id='%s'"%(remove_dict['subnet_id'])}
            elif(self.user_level):
                get_sub = {'select':"proj_id,subnet_name",'from':"trans_subnets",'where':"subnet_id='%s'"%(remove_dict['subnet_id']),'and':"proj_id='%s'"%(self.project_id)}
            self.subnet = self.db.pg_select(get_sub)
        except:
            logger.sys_error("No subnet found in project %s."%(self.project_id))
            raise Exception("No subnet found in project %s."%(self.project_id))

        #verify the router id
        try:
            if(self.is_admin == 1):
                get_router = {'select':"*",'from':"trans_routers",'where':"router_id='%s'"%(remove_dict['router_id'])}
                self.router = self.db.pg_select(get_router)
            elif(self.user_level):
                get_router = {'select':"*",'from':"trans_routers",'where':"router_id='%s'"%(remove_dict['router_id']),'and':"proj_id='%s'"%(self.project_id)}
                self.router = self.db.pg_select(get_router)
        except:
            logger.sys_error("No router found in project %s."%(remove_dict['project_id']))
            raise Exception("No router found in project %s."%(remove_dict['project_id']))

        #check if router and subnet are in the same project
        if(self.subnet[0][0] != self.router[0][4]):
            logger.sys_error("Router %s and subnet %s not in project %s."%(remove_dict['router_id'],self.subnet[0][1],remove_dict['project_id']))
            raise Exception("Router %s and subnet %s not in project %s."%(remove_dict['router_id'],self.subnet[0][1],remove_dict['project_id']))

        if(self.user_level <= 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":remove_dict['project_id']}
                if(self.project_id != remove_dict['project_id']):
                    self.token = get_token(self.username,self.password,remove_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #add the new user to openstack
                body = '{"subnet_id": "%s"}'%(remove_dict['subnet_id'])
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'PUT'
                api_path = '/v2.0/routers/%s/remove_router_interface'%(remove_dict['router_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sql_error("Could not remove an internal port to the router.")
                raise Exception("Could not remove an internal port to the router.")

            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                try:
                    self.db.pg_transaction_begin()
                    #insert new net info
                    update = {'table':'trans_routers','set':"net_id=NULL,router_int_subnet_id=NULL,router_int_conn_id=NULL,router_int_port_id=NULL",'where':"router_id='%s'"%(remove_dict['router_id'])}
                    self.db.pg_update(update)
                except:
                    self.db.pg_transaction_rollback()
                    logger.sql_error("Could not update the transcirrus DB.")
                    raise Exception("Could not update the transcirrus DB.")
                else:
                    self.db.pg_transaction_commit()
                    return 'OK'
            else:
                util.http_codes(rest['response'],rest['reason'])

        else:
            logger.sys_error("Users can not remove ports to routers.")
            raise Exception("Users can not remove ports to routers.")

    def add_router_gateway_interface(self,add_dict):
        """
        DESC: Add an external gateway network interface to the virtual layer3
              router.
        INPUT: add_dict - router_id
                        - ext_net_id
                        - project_id
        OUTPUT: OK -success
                ERROR - failure
        ACCESS: Admins and power users can add an extrnal interface to the router.
        NOTE: If an external net name is not specified the default_public will be used.
        """
        if(('router_id' not in add_dict) or (add_dict['router_id'] == '')):
            logger.sys_error("Can not add external gateway to router, no router id given.")
            raise Exception("Can not add external gateway to router, no router id given.")
        if(('ext_net_id' not in add_dict) or (add_dict['ext_net_id'] == '')):
            logger.sys_error("Can not add external gateway to router, no subnet id given.")
            raise Exception("Can not add external_gateway to router, no subnet id given.")

        if(self.user_level <= 1):
            try:
                get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(add_dict['project_id'])}
                project = self.db.pg_select(get_proj)
            except:
                logger.sys_error("Project could not be found.")
                raise Exception("Project could not be found.")

            #get the extnet info - confirmation
            if('ext_net_id' in add_dict):
                try:
                    get_ext_net = {'select':"net_name",'from':"trans_network_settings",'where':"net_internal='false'",'and':"net_id='%s'"%(add_dict['ext_net_id'])}
                    ext = self.db.pg_select(get_ext_net)
                    self.ext_net = add_dict['ext_net_id']
                except:
                    logger.sys_error("No external net found in project")
                    raise Exception("No external net found in project")
            else:
                self.ext_net = config.DEFAULT_PUB_NET_ID

            try:
                get_router = {'select':"*",'from':"trans_routers",'where':"router_id='%s'"%(add_dict['router_id'])}
                self.router = self.db.pg_select(get_router)
            except:
                logger.sys_error("No router found in project.")
                raise Exception("No router found in project.")

            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":add_dict['project_id']}
                if(self.project_id != add_dict['project_id']):
                    self.token = get_token(self.username,self.password,add_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                body = '{"router": {"external_gateway_info": {"network_id": "%s", "enable_snat": true}}}'%(self.ext_net)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'PUT'
                api_path = '/v2.0/routers/%s'%(add_dict['router_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
            except:
                logger.sql_error("Could not add a gateway port to router.")
                raise Exception("Could not add an gateway port to router.")

            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                try:
                    self.db.pg_transaction_begin()
                    #get port device info - THIS NEEDS TO BE FIXED. NEED TO USE PORT ID
                    #port = port_ops(self.auth)
                    #get_port = port.get_port(PORT ID)
                    #raw = get_port['fixed_ips']
                    #possible to have multiple ip in the future
                    #for x in raw:
                    #    self.ip = x['ip_address']
                    #update the transcirrus router
                    update = {'table':'trans_routers','set':"router_ext_gateway='%s',router_ext_ip=NULL"%(load['router']['id']),'where':"router_id='%s'"%(add_dict['router_id'])}
                    self.db.pg_update(update)
                except:
                    self.db.pg_transaction_rollback()
                    logger.sql_error("Could not add a gateway port to router in Transcirrus DB.")
                    raise Exception("Could not add an gateway port to router in Transcirrus DB.")
                else:
                    self.db.pg_transaction_commit()
                    return 'OK'
            else:
                util.http_codes(rest['response'],rest['reason'])
        else:
            logger.sys_error("Users can not add gateways to routers.")
            raise Exception("Users can not add gateways to routers.")

    def delete_router_gateway_interface(self,remove_dict):
        """
        DESC: Remove an external gateway network interface from the virtual layer3
              router.
        INPUT: remove_dict - router_id
                           - project_id
        OUTPUT: OK - success
                ERROR - failure
        ACCESS: Only admins can remove an extrnal interface from the router.
        NOTE: transcirrus db will have to be updated accordingly - Haveing issues removeing gateways, bug in Grizzly
        """
        if(remove_dict['router_id'] == ''):
            logger.sys_error("Can not add external gateway to router, no router id given.")
            raise Exception("Can not add external gateway to router, no router id given.")

        if(self.is_admin == 1):
            try:
                get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(remove_dict['project_id'])}
                project = self.db.pg_select(get_proj)
            except:
                logger.sys_error("Project could not be found.")
                raise Exception("Project could not be found.")

            #make sure router_id is valid
            try:
                get_router = {'select':"router_name",'from':"trans_routers",'where':"router_id='%s'"%(remove_dict['router_id'])}
                router = self.db.pg_select(get_router)
            except:
                logger.sys_error("No router found in project.")
                raise Exception("No router found in project.")
            
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":remove_dict['project_id']}
                if(self.project_id != remove_dict['project_id']):
                    self.token = get_token(self.username,self.password,remove_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                body = '{"router": {"external_gateway_info": {}}}'
                logger.sys_info("body " + body)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'PUT'
                api_path = '/v2.0/routers/%s'%(remove_dict['router_id'])
                logger.sys_info("api_path " + api_path)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
                logger.sys_info(rest)
            except:
                logger.sql_error("Could not remove gateway from router.")
                raise Exception("Could not remove gateway from router.")

            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                try:
                    self.db.pg_transaction_begin()
                    #update the transcirrus router
                    update = {'table':'trans_routers','set':"router_ext_gateway=NULL,router_ext_ip=NULL",'where':"router_id='%s'"%(remove_dict['router_id'])}
                    self.db.pg_update(update)
                except:
                    self.db.pg_transaction_rollback()
                    logger.sql_error("Could not remove gateway from router in Transcirrus DB.")
                    raise Exception("Could not remove gateway from router in Transcirrus DB.")
                else:
                    self.db.pg_transaction_commit()
                    return 'OK'
            else:
                util.http_codes(rest['response'],rest['reason'])
        else:
            logger.sys_error("Users can not remove ports to routers.")
            raise Exception("Users can not remove ports to routers.")

#Refer to http://docs.openstack.org/api/openstack-network/2.0/content/router_ext_ops_floatingip.html

    #ALL floating iP stuff updated/UNITTESTED
    def list_floating_ips(self,project_id=None):
        """
        DESC: List the availabel floating ips in a project. Any user type can list
              the floating ips in a project.
        INPUT: self object
        OUTPUT: array of r_dict - floating_ip
                                - floating_ip_id
        ACCESS: Admin will be able to list floatingips in the system,
                power users and standard users will only be able to list
                floating ips in their project.
        NOTE: This info can be obtained from the transcirrus db
        """
        get_floating = None
        try:
            if(self.is_admin == 1):
                if(project_id):
                    get_floating = {'select':"*",'from':"trans_floating_ip",'where':"proj_id='%s'order by index ASC"%(project_id)}
                else:
                    get_floating = {'select':"*",'from':"trans_floating_ip order by index ASC"}
            else:
                get_floating = {'select':"*",'from':"trans_floating_ip",'where':"proj_id='%s' order by index ASC"%(self.project_id)}
            floating = self.db.pg_select(get_floating)
        except:
            sys_error("Could not get list of floating ips.")
            raise Exception("Could not get list of floating ips.")

        r_array = []
        for floater in floating:
            r_dict = {'floating_ip':floater[1],'floating_ip_id':floater[2]}
            r_array.append(r_dict)

        return r_array

    def get_floating_ip(self,floating_ip_id):
        """
        DESC: Return the mappings between the floating ip and the virtual instance
              fixed ip.
        INPUT: floating_ip_id
        ACCESS: Admins can get the info for any floating ip. Power users and standard
                users can only get info for floating ip in their project.
        OUTPUT: r_dict - floating_ip
                       - floating_ip_id
                       - instance_name
                       - instance_id
                       - internal_net_name
                       - internal_net_id
                       - project_id
        NOTE: none
        """
        if(floating_ip_id == ''):
            logger.sys_error('No floating ip ID given.')
            raise Exception('No floating ip ID given.')

        get_floating = None
        r_dict = None
        if(self.is_admin == 1):
            get_floating = {'select':"proj_id,inst_id,inst_name,inst_floating_ip,floating_ip_id,inst_int_net_id,inst_int_net_name",'from':"trans_instances",'where':"floating_ip_id='%s'"%(floating_ip_id)}
        else:
            get_floating = {'select':"proj_id,inst_id,inst_name,inst_floating_ip,floating_ip_id,inst_int_net_id,inst_int_net_name",'from':"trans_instances",'where':"proj_id='%s'"
                            %(self.project_id),'and':"floating_ip_id='%s'"%(floating_ip_id)
                            }
        floating = self.db.pg_select(get_floating)

        if(len(floating) == 0):
            #need to build a join function if db lib
            try:
                get_floating = {'select':"floating_ip,proj_id",'from':"trans_floating_ip",'where':"floating_ip_id='%s'"%(floating_ip_id)}
                floating = self.db.pg_select(get_floating)
            except:
                logger.sys_error("Could not get of floating ip with id %s."%(floating_ip_id))
                raise Exception("Could not get of floating ip with id %s."%(floating_ip_id))
            floating = self.db.pg_select(get_floating)
            r_dict = {'floating_ip':floating[0][0],
                      'floating_ip_id':floating_ip_id,
                      'instance_name':'',
                      'instance_id':'',
                      'internal_net_name':'',
                      'internal_net_id':'',
                      'project_id':floating[0][1]
                    }
        elif(len(floating) == 1):
            r_dict = {'floating_ip':floating[0][3],
              'floating_ip_id':floating[0][4],
              'instance_name':floating[0][2],
              'instance_id':floating[0][1],
              'internal_net_name':floating[0][6],
              'internal_net_id':floating[0][5],
              'project_id':floating[0][0]
              }
    
        return r_dict

    def allocate_floating_ip(self,input_dict):
        """
        DESC: Allocate a new floating ip to a project. Only admins can allocate a new floating ip
              to the project.
        INPUT: input_dict - ext_net_id
                          - project_id
        OUTPUT: r_dict - floating_ip
                       - floating_ip_id
        ACCESS: Admins can allocate a floating ip to any project, power users
                can only allocate a floating ip to their project. Standard users
                can not allocate a floating IP.
        NOTE: update the transcirrus db accoridingly
        """
        if((input_dict['ext_net_id'] == '') or ('ext_net_id' not in input_dict)):
            logger.sys_error('No external net id given.')
            raise Exception('No external net id given.')
        if((input_dict['project_id'] == '') or ('project_id' not in input_dict)):
            logger.sys_error('No project id given.')
            raise Exception('No project id given.')

        #if a power user make sure given id is the same as the user id
        if(self.user_level == 1):
            if(input_dict['project_id'] != self.project_id):
                    logger.sys_error('User project ID is invalid.')
                    raise Exception('User project ID is invalid.')
        elif(self.user_level == 2):
            logger.sys_error('Users can not allocate floating ip addresses.')
            raise Exception('Users can not allocate floating ip addresses.')

        #make sure the project ID is valid and the user can allocate floating ip - sanity
        get_proj = None
        try:
            get_proj = {'select':"proj_name",'from':"projects",'where':"proj_id='%s'"%(input_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error('Project does not exist.')
            raise Exception('Project does not exist.')

        #Create an API connection with the admin
        try:
            #build an api connection for the admin user
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_logger("Could not connect to the API")
            raise Exception("Could not connect to the API")

        #New way to do API calls - experiment
        try:
            body = '{"floatingip": {"floating_network_id": "%s", "tenant_id": "%s"}}'%(input_dict['ext_net_id'],input_dict['project_id'])
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2.0/floatingips'
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not assign a floating ip to %s."%(input_dict['project_id']))
            raise Exception("Could not assign a floating ip to %s."%(input_dict['project_id']))

        #new way to process db transaction after API call - experiment
        load = None
        if(rest['response'] == 201):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            self.db.pg_transaction_begin()
            load = json.loads(rest['data'])
            try:
                insert_dict = {"floating_ip":load['floatingip']['floating_ip_address'],"floating_ip_id":load['floatingip']['id'],"proj_id":input_dict['project_id'],"router_id":"",
                               "fixed_ip":""}
                self.db.pg_insert("trans_floating_ip",insert_dict)
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not update Transcirrus DB with floating Ip info")
                raise Exception("Could not update Transcirrus DB with floating Ip info")
            else:
                self.db.pg_transaction_commit()
                r_dict = {'floating_ip':load['floatingip']['floating_ip_address'],"floating_ip_id":load['floatingip']['id']}
                return r_dict
        else:
            util.http_codes(rest['response'],rest['reason'])

    def update_floating_ip(self,update_dict):
        """
        DESC: Update the floating ip attachments in the project to a virtual server.
              Admins and power users can attach floating ip addresses to instances in their project.
        INPUT: update_dict - floating_ip - req
                           - instance_id - req
                           - project_id - req
                           - action - req add/remove
        OUTPUT: r_dict - floating_ip
                       - floating_ip_id
                       - instance_name
                       - instance_id
        ACCESS: Admin can add a floating ip to any instance
                power users can add a floating ip to any instance in their project
                users can only add a floating ip to an instance they own
        NOTE: since the ports are not implemented in alpo.0 we will use the nova call.
        body = '{"addFloatingIp": {"address": "%s"}}' port 8774
        {"removeFloatingIp": {"address": "192.168.10.14"}}
        """
        if((update_dict['floating_ip'] == '') or ('floating_ip' not in update_dict)):
            logger.sys_error('No floating ip given.')
            raise Exception('No floating ip given.')
        if((update_dict['instance_id'] == '') or ('instance_id' not in update_dict)):
            logger.sys_error('No instance id given.')
            raise Exception('No instance id given.')
        if((update_dict['action'] == '') or ('action' not in update_dict)):
            logger.sys_error('No action given.')
            raise Exception('No action given.')

        action = update_dict['action'].lower()
        if((action == 'add') or (action == 'remove')):
            logger.sys_info('%s action specified for update floating ip.'%(action))
        else:
            logger.sys_error('%s is not a valid floating ip action.'%(action))
            raise Exception('%s is not a valid floating ip action.'%(action))

        #see if the instance exists
        try:
            get_inst = {'select':"inst_name,inst_user_id",'from':"trans_instances",'where':"inst_id='%s'"%(update_dict['instance_id'])}
            inst = self.db.pg_select(get_inst)
        except:
            logger.sys_error('%s does not exist.'%(update_dict['instance_id']))
            raise Exception('%s does not exist.'%(update_dict['instance_id']))

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(update_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.user_level >= 1):
            if(self.project_id != update_dict['project_id']):
                logger.sys_error("Power user can only update floating ips in their project.")
                raise Exception("Power user can only update floating ips in their project.")
        elif(self.user_level == 2):
            #check to see if the instance belongs to the user
            if(self.user_id != inst[0][1]):
                logger.sys_error("User can only update floating ips in their project on instances they own.")
                raise Exception("User can only update floating ips in their project on instances they own.")

        #make sure the floating ip is in the project
        try:
            get_float = {'select':"floating_ip_id",'from':"trans_floating_ip",'where':"proj_id='%s'"%(update_dict['project_id']),'and':"floating_ip='%s'"%(update_dict['floating_ip'])}
            floater = self.db.pg_select(get_float)
        except:
            logger.sys_error("Floating ip no in project %s"%(update_dict['project_id']))
            raise Exception("Floating ip no in project %s"%(update_dict['project_id']))

        #Create an API connection with the admin
        try:
            #build an api connection for the admin user
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_logger("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            body = None
            if(action == 'remove'):
                body = '{"removeFloatingIp": {"address": "%s"}}'%(update_dict['floating_ip'])
            elif(action == 'add'):
                body = '{"addFloatingIp": {"address": "%s"}}'%(update_dict['floating_ip'])
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json","X-Auth-Project-Id": project[0][0]}
            function = 'POST'
            api_path = '/v2/%s/servers/%s/action'%(update_dict['project_id'],update_dict['instance_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": str(body), "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not assign a floating ip to %s."%(update_dict['project_id']))
            raise Exception("Could not assign a floating ip to %s."%(update_dict['project_id']))

        if(rest['response'] == 202):
            update = None
            try:
                self.db.pg_transaction_begin()
                if(action == 'add'):
                    update = {'table':'trans_instances','set':"floating_ip_id='%s',inst_floating_ip='%s'"%(floater[0][0],update_dict['floating_ip']),'where':"inst_id='%s'"%(update_dict['instance_id'])}
                elif(action == 'remove'):
                    update = {'table':'trans_instances','set':"floating_ip_id=NULL,inst_floating_ip=NULL",'where':"inst_id='%s'"%(update_dict['instance_id'])}
                print update
                self.db.pg_update(update)
            except:
                self.db.pg_transaction_rollback()
                logger.sys_error("Could not update floating ip in the Transcirrus DB")
                raise Exception("Could not update floating ip in the Transcirrus DB")
            else:
                self.db.pg_transaction_commit()
                r_dict = {'floating_ip':update_dict['floating_ip'],'floating_ip_id':floater[0][0],'instance_name':inst[0][0],'instance_id':inst[0][1]}
                return r_dict
        else:
            util.http_codes(rest['response'],rest['reason'])

    def deallocate_floating_ip(self,del_dict):
        """
        DESC: Removes a floating ip from the tenant. Only admins can delete a floating
              ip from the project
        INPUT: del_dict - floating_ip
                        - project_id
        OUTPUT: OK is successful or error
        ACCESS: Admins can deallocate a floating ip to any project
                Power users can only deallocate a floating ip to their project
                Standard users can not deallocate a floating IP.
        NOTE: the nova api is used to remove a floating ip from a specific virtual instance.
        """
        if((del_dict['floating_ip'] == '') or ('floating_ip' not in del_dict)):
            logger.sys_error('No floating ip given.')
            raise Exception('No floating ip given.')
        if((del_dict['project_id'] == '') or ('project_id' not in del_dict)):
            logger.sys_error('No project id given.')
            raise Exception('No project id given.')

        get_proj = None
        try:
            get_proj = {'select':"proj_name",'from':"projects",'where':"proj_id='%s'"%(del_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error('Project does not exist.')
            raise Exception('Project does not exist.')

        #make sure the floating ip is in the project
        try:
            get_float = {'select':"floating_ip_id",'from':"trans_floating_ip",'where':"proj_id='%s'"%(del_dict['project_id']),'and':"floating_ip='%s'"%(del_dict['floating_ip'])}
            floater = self.db.pg_select(get_float)
        except:
            logger.sys_error("Floating ip no in project %s"%(del_dict['project_id']))
            raise Exception("Floating ip no in project %s"%(del_dict['project_id']))

        #see if the floating ip is attached
        inst_name = None
        get_inst = {'select':"inst_name",'from':"trans_instances",'where':"floating_ip_id='%s'"%(floater[0][0])}
        inst_name = self.db.pg_select(get_inst)
        print inst_name
        if(inst_name):
            logger.sys_error("Floating ip attached to instance %s"%(inst_name[0][0]))
            raise Exception("Floating ip attached to inst %s"%(inst_name[0][0]))

        #Create an API connection with the admin
        try:
            #build an api connection for the admin user
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_logger("Could not connect to the API")
            raise Exception("Could not connect to the API")
        
        #New way to do API calls - experiment
        #try:
        body = ''
        header = {"X-Auth-Token":self.token, "Content-Type": "application/json","X-Auth-Project-Id": project[0][0]}
        function = 'DELETE'
        api_path = '/v2.0/floatingips/%s'%(floater[0][0])
        print api_path
        token = self.token
        sec = self.sec
        rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
        print rest_dict
        rest = api.call_rest(rest_dict)
        #except:
        #    logger.sys_error("Could not deallocate the floating ip.")
        #    raise Exception("Could not deallocate the floating ip.")

        #new way to process db transaction after API call - experiment
        load = None
        if(rest['response'] == 204):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            self.db.pg_transaction_begin()
            try:
                delete = {"table":'trans_floating_ip',"where":"floating_ip_id='%s'"%(floater[0][0])}
                self.db.pg_delete(delete) 
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not remove the floating ip from the Transcirrus DB.")
                raise Exception("Could not remove the floating ip from the Transcirrus DB.")
            else:
                self.db.pg_transaction_commit()
                return "OK"
        else:
            util.http_codes(rest['response'],rest['reason'])
