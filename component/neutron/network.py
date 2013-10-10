#!/usr/bin/python
# Used manage all Neutron(Quantum) Networks, subnets and network ports
# Refer to http://docs.openstack.org/api/openstack-network/2.0/content/API_Operations.html
# for all API information.

import sys
import json
import socket

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

class neutron_net_ops:
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
            self.adm_token = user_dict['adm_token']
            self.user_id = user_dict['user_id']
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

        #if(self.adm_token == ''):
        #    logger.sys_error("No admin tokens passed.")
        #    raise Exception("No admin tokens passed.")
            #self.adm_token = config.ADMIN_TOKEN

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

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def destructor(self):
        #close any open db connections
        self.db.close_connection()

    def list_networks(self):
        """
        DESC: List the networks available in a project. All user types can only
              list the networks that are available in their project.Admin can list
              all of the networks
        INPUT: self object
        OUTPUT: array of r_dict - net_name
                                - net_id
                                - proj_id
        ACCESS: All users. Admin can list all networks.
        NOTE:none
        """
        get_nets = {}
        if(self.is_admin == 1):
            get_nets = {'select':"net_name,net_id,proj_id",'from':"trans_network_settings"}
        else:
            get_nets = {'select':"net_name,net_id,proj_id",'from':"trans_network_settings",'where':"proj_id='%s'"%(self.project_id)}

        nets = self.db.pg_select(get_nets)

        r_dict = {}
        r_array = []
        for net in nets:
            r_dict['net_name'] = net[0]
            r_dict['net_id'] = net[1]
            r_dict['project_id'] = net[2]
            r_array.append(r_dict)

        return r_array

    def get_network(self,net_name):
        """
        DESC: Get the information on a specific network. All user types can only
              get the information on networks in their project. Admin can get info on
              any network.
        INPUT: net_name
        OUTPUT: r_dict - net_id
                       - net_creator_id
                       - net_admin_state
                       - net_shared
                       - net_internal
                       - net_subnet_id[]
        """
        if(net_name == ''):
            logger.sys_error("No net name was specified for the new network.")
            raise Exception("No net name was specified for the new network.")

        get_net = {}
        try:
            if(self.is_admin == 1):
                get_net = {'select':"net_id,user_id,net_admin_state,net_internal,net_shared",'from':"trans_network_settings",'where':"net_name='%s'" %(net_name)}
            else:
                get_net = {'select':"net_id,user_id,net_admin_state,net_internal,net_shared",'from':"trans_network_settings",'where':"net_name='%s'" %(net_name),'and':"proj_id='%s'" %(self.project_id)}
    
            net = self.db.pg_select(get_net)
        except:
            logger.sql_error("Could not connect to the Transcirrus db.")
            raise Exception("Could not connect to the Transcirrus db.")

        #get the subnets
        get_sub = {'select':"subnet_id",'from':"trans_subnets",'where':"net_id='%s'" %(net[0][0]),'and':"proj_id='%s'" %(self.project_id)}
        subs = self.db.pg_select(get_sub)

        #build a better array
        new_array = []
        for sub in subs:
            new_array.append(sub[0])

        r_dict = {'net_id':net[0][0],'net_creator_id':net[0][1],'net_admin_state':net[0][2],'net_shared':net[0][4],'net_internal':net[0][3],'net_subnet_id':new_array}
        return r_dict

    def add_private_network(self,create_dict):
        """
        DESC: Create a network in the project. Only an admin or project power user can create
              a new private network. Users can not create networks.
        INPUT: create_dict - net_name
                           - admin_state (true/false)
                           - shared (true/false)
        OUTPUT: r_dict - net_name
                       - net_id
        NOTE: need to update the transcirrus db with the new network.
        """
        if((create_dict['net_name'] == '') or ('net_name' not in create_dict)):
            logger.sys_error("No net name was specified for the new network.")
            raise Exception("No net name was specified for the new network.")
        if((create_dict['admin_state'] == '') or ('admin_state' not in create_dict)):
            logger.sys_error("No admin state was specified for the new network.")
            raise Exception("No admin state was specified for the new network.")
        if((create_dict['shared'] == '') or ('shared' not in create_dict)):
            logger.sys_error("No shared pref was specified for the new network.")
            raise Exception("No shared pref was specified for the new network.")

        #set the strings
        admin_state = create_dict['admin_state']
        shared = create_dict['shared']

        if((admin_state.lower() == 'true') or (admin_state.lower() == 'false')):
            logger.sys_info("Admin flag passed to neutron.")
        else:
            logger.sys_error("Invalid property given for admin state.")
            raise Exception("Invalid property given for admin state.")

        if((shared.lower() == 'true') or (shared.lower() == 'false')):
            logger.sys_info("Shared property was passed to neutron.")
        else:
            logger.sys_error("Invalid property given for shared flag.")
            raise Exception("Invalid property given for shared flag.")

        #see if the netname already exists in the project
        get_net = {'select':"net_id",'from':"trans_network_settings",'where':"proj_id='%s'" %(self.project_id),'and':"net_name='%s'"%(create_dict['net_name'])}
        net = self.db.pg_select(get_net)
        if(net):
            #may change to error
            logger.sys_warning("Can not have two networks with the same net name in the same project.")
            raise Exception("Can not have two networks with the same net name in the same project.")

        if(self.user_level <= 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            r_dict = {}
            try:
                #add the new user to openstack
                body = '{"network": {"tenant_id": "%s", "name": "%s", "admin_state_up": %s, "shared": "%s"}}' %(self.project_id,create_dict['net_name'],admin_state.lower(),shared.lower())
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2.0/networks'
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
                    insert_dict = {"net_name":create_dict['net_name'],"net_id":load['network']['id'],"user_id":self.user_id,"proj_id":self.project_id,"net_internal":"true","net_shared":create_dict['shared'],"net_admin_state":create_dict['admin_state']}
                    self.db.pg_insert("trans_network_settings",insert_dict)
                    self.db.pg_transaction_commit()
                    r_dict = {'net_name':create_dict['net_name'],'net_id':load['network']['id']}
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not add a new private network to Neutron.")
                raise Exception("Could not add a new private network to Neutron.")
        else:
            logger.sys_error("Only an admin or a power user can create a new network.")
            raise Exception("Only an admin or a power user can create a new network.")

        return r_dict

    def add_public_network(self,create_dict):
        """
        DESC: Create a public network in the project. Only an admin can create
              a new public network. Public networks allow vms and virtual routers to
              recieve floating ips on the external. Users and power users can not
              create networks.
        INPUT: create_dict - net_name
                           - admin_state (up/down)
                           - shared (true/false)
        OUTPUT: r_dict - net_name
                       - net_id
        NOTE: need to update the transcirrus db with the new network.
        """
        if((create_dict['net_name'] == '') or ('net_name' not in create_dict)):
            logger.sys_error("No net name was specified for the new network.")
            raise Exception("No net name was specified for the new network.")
        if((create_dict['admin_state'] == '') or ('admin_state' not in create_dict)):
            logger.sys_error("No admin state was specified for the new network.")
            raise Exception("No admin state was specified for the new network.")
        if((create_dict['shared'] == '') or ('shared' not in create_dict)):
            logger.sys_error("No shared pref was specified for the new network.")
            raise Exception("No shared pref was specified for the new network.")

        #set the strings
        admin_state = create_dict['admin_state']
        shared = create_dict['shared']

        if((admin_state.lower() == 'true') or (admin_state.lower() == 'false')):
            logger.sys_info("Admin flag passed to neutron.")
        else:
            logger.sys_error("Invalid property given for admin state.")
            raise Exception("Invalid property given for admin state.")

        if((shared.lower() == 'true') or (shared.lower() == 'false')):
            logger.sys_info("Shared property was passed to neutron.")
        else:
            logger.sys_error("Invalid property given for shared flag.")
            raise Exception("Invalid property given for shared flag.")

        #see if the netname already exists in the project
        get_net = {'select':"net_id",'from':"trans_network_settings",'where':"proj_id='%s'" %(self.project_id),'and':"net_name='%s'"%(create_dict['net_name'])}
        net = self.db.pg_select(get_net)
        if(net):
            #may change to error
            logger.sys_warning("Can not have two networks with the same net name in the same project.")
            raise Exception("Can not have two networks with the same net name in the same project.")

        if(self.user_level == 0):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            r_dict = {}
            try:
                #add the new user to openstack
                body = '{"network": {"router:external": "True", "tenant_id": "%s", "name": "%s", "admin_state_up": %s, "shared": "%s"}}' %(self.project_id,create_dict['net_name'],admin_state.lower(),shared.lower())
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2.0/networks'
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
                    insert_dict = {"net_name":create_dict['net_name'],"net_id":load['network']['id'],"user_id":self.user_id,"proj_id":self.project_id,"net_internal":"false","net_shared":create_dict['shared'],"net_admin_state":create_dict['admin_state']}
                    self.db.pg_insert("trans_network_settings",insert_dict)
                    self.db.pg_transaction_commit()
                    r_dict = {'net_name':create_dict['net_name'],'net_id':load['network']['id']}
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not add a new public network to Neutron.")
                raise Exception("Could not add a new public network to Neutron.")
        else:
            logger.sys_error("Only an admin or a power user can create a new network.")
            raise Exception("Only an admin or a power user can create a new network.")

        return r_dict
        #-d '{"network": {"router:external": "True", "name": "jon", "admin_state_up": true}}'

    def remove_network(self,net_name):
        """
        DESC: Remove a network from a project.
        INPUT: net_name
        OUTPUT: "OK" if removed or error
        ACCESS: Admin can remove any network, power user can remove a network in their project
                users can not remove a network.
        NOTE: networks in use can not be removed. API throws 409 error.
        """
        #curl -i http://192.168.10.30:9696/v2.0/networks/33e29046-f98d-4748-967e-02e976a059a7.json -X DELETE 
        
        if(net_name == ''):
            logger.sys_error("Can not have a blank name when deleteing a network")
            raise Exception("Can not have a blank name when deleteing a network")

        #get the network. Make sure it exists
        net = self.get_network(net_name)
        if(net):
            if(len(net['net_subnet_id']) >= 1):
                logger.error('Can not remove network %s, it has subnets attached.' %(net_name))
                raise Exception('Can not remove network %s, it has subnets attached.' %(net_name))
        else:
            logger.error("Network with the name %s in project %s does not exist."%(net_name,self.project_id))
            raise("Network with the name %s in project %s does not exist."%(net_name,self.project_id))

        if(self.user_level <= 1):
            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            #if(self.is_admin == 1):
            #    new_token = self.adm_token
            #else:
            #    new_token = self.token

            try:
                #add the new user to openstack
                body = ''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'DELETE'
                api_path = '/v2.0/networks/%s' %(net['net_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 204
                if(rest['response'] == 204):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    self.db.pg_transaction_begin()
                    #insert new net info
                    del_dict = {"table":'trans_network_settings',"where":"net_id='%s'"%(net['net_id']), "and":"proj_id='%s'" %(self.project_id)}
                    self.db.pg_delete(del_dict)
                    self.db.pg_transaction_commit()
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not remove the network from Neutron.")
                raise Exception("Could not remove the network from Neutron.")
        else:
            logger.sys_error("Only an admin or a power user can remove a new network.")
            raise Exception("Only an admin or a power user can remove a new network.")

        return 'OK'

    def update_network(self,toggle_dict):
        """
        DESC: Toggles the network admin state from up to down or down to
              up. Only admins can toggle the network state
        INPUT: toggle_dict - admin_state_up - true/false
                           - net_name
        OUTPUT: r_dict - net_name
                       - net_id
                       - admin_state_up
        ACCESS: Only an admin can update the network admin status
        """

        if(('admin_state_up' not in toggle_dict) or (toggle_dict['admin_state_up'] == '')):
            logger.sys_error("No admin state was give")
            raise Exception("No admin state was give")
        if(('net_name' not in toggle_dict) or (toggle_dict['net_name'] == '')):
            logger.sys_error("No network name was give")
            raise Exception("No network name was give")

        #set the state string
        state = toggle_dict['admin_state_up']

        #get the network info
        net = self.get_network(net_name)
        if(len(net) == 0):
            logger.sys_error("Could not find the network %s" %(net_name))
            raise Exception("Could not find the network %s" %(net_name))
        if(net['net_admin_state'] == state.lower()):
            r_dict = {'net_name':net['net_name'],'net_id':net['net_id'],'admin_state_up':state}
            return r_dict

        if(state.lower() == 'true'):
            self.admin_state = 'UP'
        elif(state.lower() == 'false'):
            self.admin_state = 'DOWN'

        if(self.is_admin == 1):
            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #add the new user to openstack
                body = '{"network": {"name": "%s", "admin_state_up": %s}}'%(net['net_name'],self.admin_state)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'PUT'
                api_path = '/v2.0/networks/%s' %(net['net_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                print rest_dict
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 204
                print rest
                if(rest['response'] == 200):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    self.db.pg_transaction_begin()
                    #insert new net info
                    update_dict = {'table':"trans_network_settings",'set':"net_admin_state='%s'"%(state.lower()),'where':"net_id='%s'"%(net['net_id'])}
                    self.db.pg_delete(del_dict)
                    self.db.pg_transaction_commit()
                    r_dict = {'net_name':net['net_name'],'net_id':net['net_id'],'admin_state_up':state}
                    return r_dict
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not remove the network from Neutron.")
                raise Exception("Could not remove the network from Neutron.")
        else:
            logger.sys_error("Only an admin or a power user can remove a new network.")
            raise Exception("Only an admin or a power user can remove a new network.")

    def list_net_subnet(self,net_name):
        """
        DESC: Lists the subnets for the specified network. All user types can
              list the subnets in the project networks.
        INPUT: net_name
        OUTPUT: array of r_dict - subnet_name
                                - subnet_id
        NOTE: all of the return info can be quried from the transcirrus db. May use
              rest api to verify subent exsists(not required).
        """

        print "not implemented"

    def get_net_subnet(self,subnet_name):
        """
        DESC: Get all of the information for a specific subnet. All user types
              can get information for subnets in the project networks.
        INPUT: subnet_name
        OUTPUT: r_dict - subnet_id
                       - subnet_class
                       - subnet_ip_ver
                       - subnet_cidr
                       - subnet_gateway
                       - subnet_allocation_start
                       - subnet_allocation_end
                       - subnet_dhcp_enable
        NOTE: all of the return info can be quried from the transcirrus db. May use
              rest api to verify subent exsists(not required).
        """
        print "not implemented"

    def add_net_subnet(self,subnet_dict):
        """
        DESC: Add a new subnet to a project subnet. Only admins can add a subnet to
              a network in their project.
        INPUT: subnet_dict - net_name
                           - subnet_dhcp_enable true/false
                           - subnet_dns[]
        OUTPUT: r_dict - subnet_name
                       - subnet_id
                       - subnet_cidr
                       - subnet_start_range
                       - subnet_end_range
                       - subnet_mask
                       - subnet_gateway
        ACCESS: Admins can create a subnet in any network, powerusers can create a subnet
                only a subnet in their project.
        NOTE: REST API will throw a 409 error if there is a conflict. Default google dns used if no DNS server specified.
              Up to 2 more DNS servers can be specified.
        """

        if(('net_name' not in subnet_dict) or (subnet_dict['net_name'] == '')):
            logger.sys_error("Could not create subnet. No network name given.")
            raise Exception("Could not create subnet. No network name given.")
        if(('subnet_dhcp_enable' not in subnet_dict) or (subnet_dict['subnet_dhcp_enable'] == '')):
            logger.sys_error("Could not activate the dhcp service.")
            raise Exception("Could not activate the dhcp service.")
        
        #strings
        self.enable_dhcp = subnet_dict['subnet_dhcp_enable'].lower()
        if((self.enable_dhcp == 'true') or (self.enable_dhcp == 'false')):
            logger.sys_info("enable_dhcp passed")
        else:
            #HACK hate this
            logger.sys_error("Invalid value given for enable_dhcp.")
            raise Exception("Invalid value given for enable_dhcp.")

        self.dns_string = '["8.8.8.8", "8.8.4.4"]'
        if('subnet_dns' in subnet_dict):
            """
            for sub in subnet_dict['subnet_dns']:
                try:
                    socket.inet_aton(sub)
                    self.dns + sub
                except socket.error:
                    logger.sys_error("The dns ip address %s was not valid." %(sub))
                    raise Exception("The dns ip address %s was not valid." %(sub))
            """
            #HACK this needs to be fixed
            logger.sys_warning("Need to be able to add more dns servers.")

        #get the network info
        net = self.get_network(subnet_dict['net_name'])
        if(len(net) == 0):
            logger.sys_error("No network with the name %s was found."%(subnet_dict['net_name']))
            raise Exception("No network with the name %s was found."%(subnet_dict['net_name']))
    
        #get the next available subnet from the database
        try:
            get_sub = {'select':"*",'from':"trans_subnets",'where':"in_use=0 order by index ASC"}
            sub = self.db.pg_select(get_sub)
        except:
            logger.sql_error("Could not get subnet information from the Transcirrus db.")
            raise Exception("Could not get subnet information from the Transcirrus db.")

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
                body = '{"subnet": {"ip_version": %s, "gateway_ip": "%s", "name": "%s", "enable_dhcp": %s, "network_id": "%s", "tenant_id": "%s", "cidr": "%s", "dns_nameservers": %s}}'%(sub[0][3],sub[0][6],sub[0][13],self.enable_dhcp,net['net_id'],self.project_id,sub[0][4],self.dns_string)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2.0/subnets'
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
                    update_dict = {'table':"trans_subnets",'set':"in_use='1',proj_id='%s',subnet_dhcp_enable='%s',subnet_id='%s',net_id='%s',subnet_dns='8.8.8.8'"%(self.project_id,self.enable_dhcp,load['subnet']['id'],net['net_id']),'where':"index='%s'"%(sub[0][0])}
                    self.db.pg_update(update_dict)
                    self.db.pg_transaction_commit()
                    r_dict = {'subnet_name':sub[0][13],'subnet_id':sub[0][1],'subnet_cidr':sub[0][4],'subnet_start_range':sub[0][6],'subnet_end_range':sub[0][7],'subnet_mask':sub[0][14],'subnet_gateway':sub[0][5]}
                    return r_dict
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not add a new subnet to Neutron.")
                raise Exception("Could not add a new subnet to Neutron.")
        else:
            logger.sys_error("Only an admin or a power user can create a new network.")
            raise Exception("Only an admin or a power user can create a new network.")

    def update_net_subnet(self,update_dict):
        """
        #DESC: used to clean up after the
        #INPUT: update_dict - subnet_name - req
        #                   - subnet_class - op
        #                   - subnet_ip_ver - op
        #                   - subnet_cidr - op
        #                   - subnet_gateway - op
        #                   - subnet_allocation_start - op
        #                   - subnet_allocation_end - op
        #                   - subnet_dhcp_enable - op
        #OUTPUT: r_dict - subnet_name
        #               - subne_id
        #               - net_id
        """
        print "not implemented"

    #DESC: Remove a subnet from a network. Only admins can delete subnets from networks
    #      in their projects.
    #INPUT: subnet_name
    #OUTPUT: OK if deleted or error code
    #NOTE: REST api operation will give 409 error if ips from subnet are still allocated
    def remove_net_subnet(self,subnet_name):
        print "not implemented"


#######reserved for alpo.1#######
#not needed for the prototype
#http://docs.openstack.org/api/openstack-network/2.0/content/Ports.html

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def list_net_ports():
        print "not implemented"

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def get_net_port():
        print "not implemented"

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def add_net_port():
        print "not implemented"

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def update_net_port():
        print "not implemented"

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def remove_net_port():
        print "not implemented"
