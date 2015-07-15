#!/usr/local/bin/python2.7
#######standard impots#######
import sys
import os
import json
import time
import random

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.component.nova.error as ec

from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token

from transcirrus.database.postgres import pgsql

#get the nova libs
from transcirrus.component.nova.image import nova_image_ops
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.nova.server_action import server_actions
from transcirrus.component.nova.storage import server_storage_ops
from transcirrus.component.keystone.keystone_tenants import tenant_ops

#######Special imports#######

class server_ops:
    def __init__(self,user_dict):
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        else:
            self.username = user_dict['username']
            self.user_id = user_dict['user_id']
            self.password = user_dict['password']
            self.project_id = user_dict['project_id']
            self.token = user_dict['token']
            self.status_level = user_dict['status_level']
            self.user_level = user_dict['user_level']
            self.is_admin = user_dict['is_admin']

            if(self.is_admin == 1):
                self.adm_token = user_dict['adm_token']
            else:
                self.adm_token = 'NULL'

            if('sec' in user_dict):
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

        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        self.db = util.db_connect()
        self.layer_three = layer_three_ops(user_dict)
        self.net = neutron_net_ops(user_dict)
        self.server_actions = server_actions(user_dict)
        self.server_storage_ops = server_storage_ops(user_dict)
        self.keystone = tenant_ops(user_dict)

        #random number used if sec group or key name taken
        self.rannum = random.randrange(1000,9000)

    def destructor(self):
        #close any open db connections
        self.db.pg_close_connection()

    def list_servers(self,project_id=None):
        """
        DESC: List the virtual servers in the project.
        INPUT: project_id - op
        OUTPUT: array or r_dict - server_name
                                - server_id
                                - project_id
                                - zone
                                - public_ip
                                - os_ext_inst_name - admin only
                                - status
                                - tc_mgmt (True/False)
        ACCESS: Admins can list all servers in the cloud
                Power users can list the servers in a project.
                Users can list virtual servers in the project they own.
        NOTE:
        """
        #check the user status in the system, if they are not valid in the transcirrus system or enabeld openstack do not allow this operation
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to list virtual servers.")
            raise Exception("Status level not sufficient to list virtual servers.")

        if(project_id is None):
            project_id = self.project_id

        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username,self.password,project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connec to the REST api caller in list_servers operation.")
            raise Exception("Could not connec to the REST api caller in list_servers operation.")

        try:
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'GET'
            api_path = '/v2/%s/servers/detail?tenant_id=%s' %(project_id,project_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            raise e

        if(rest['response'] == 200):
            load = json.loads(rest['data'])
            self.inst_array = []
            for server in load['servers']:
                floating_ip = None
                addr = server['addresses']
                for key,value in addr.items():
                    for val in value:
                        if(val['OS-EXT-IPS:type'] == 'floating'):
                            floating_ip = val['addr']
                #check if the instance is in the TC db
                #users can not get OS-EXT-SRV-ATTR:instance_name openstack rules, looks like only admins can
                r_dict = {'server_name':server['name'],'server_id':server['id'],'project_id':server['tenant_id'],'zone':'nova','public_ip':floating_ip,'status':server['status']}

                get_inst = {'select':"inst_name",'from':"trans_instances",'where':"inst_id='%s'" %(server['id'])}
                instances = self.db.pg_select(get_inst)

                if(len(instances) == 1):
                    r_dict['tc_mgmt'] = True
                else:
                    r_dict['tc_mgmt'] = False

                if((self.user_level == 2) and (self.user_id == server['user_id']) and (self.project_id == server['tenant_id'])):
                    self.inst_array.append(r_dict)
                elif(int(self.user_level) == 1 and self.project_id == server['tenant_id']):
                    self.inst_array.append(r_dict)
                elif(self.is_admin == 1):
                    #admins
                    r_dict['os_ext_inst_name'] = server['OS-EXT-SRV-ATTR:instance_name']
                    self.inst_array.append(r_dict)
        else:
            ec.error_codes(rest)

        return self.inst_array

    def list_servers_status(self, project_id):
        """
        DESC: List the status of all virtual servers in a given project.
        INPUT: project_id
        OUTPUT: array or r_dict - server_id
                                - status
        ACCESS: Admins and Power users can list the servers in a project.
                Users can list virtual servers in the project they own.
        NOTE:
        """
        #check the user status in the system, if they are not valid in the transcirrus system or enabeld openstack do not allow this operation


        inst_array = []
        if (self.user_level > 0):
            if(project_id != self.project_id):
                logger.sys_error("Could not connect to the REST api caller in list_servers_status operation.")
                raise Exception("Could not connect to the REST api caller in list_servers_status operation.")
        else:
            if(project_id != self.project_id):
                self.token = get_token(self.username,self.password,project_id)
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id": project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the REST api caller in list_servers_status operation.")
            raise Exception("Could not connect to the REST api caller in list_servers_status operation.")

        try:
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'GET'
            api_path = '/v2/%s/servers/detail?tenant_id=%s' %(project_id,project_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            raise e

        if(rest['response'] == 200):
            load = json.loads(rest['data'])
            for server in load['servers']:
                r_dict = {'server_id':server['id'], 'status':server['status']}
                inst_array.append(r_dict)
        else:
            ec.error_codes(rest)

        return inst_array

    def list_all_servers(self):
        """
        DESC: List all virtual servers in the system.
        INPUT: None
        OUTPUT: array or r_dict - server_name
                                - server_id
                                - project_id
                                - zone
                                - public_ip
                                - os_ext_inst_name
                                - status
                                - tc_mgmt (True/False)
        ACCESS: Only admins can use this function
        """
        #check the user status in the system, if they are not valid in the transcirrus system or enabeld openstack do not allow this operation
        if(self.is_admin == 0):
            logger.sys_error("Only admins can list all of the servers on the system")
            raise Exception("Only admins can list all of the servers on the system")

        #list the projects in the cloud
        project_list = self.keystone.list_all_tenants()
        self.inst_array = []
        for project in project_list:
            if(project['project_name'] != 'trans_default'):
                self.inst_array = self.inst_array + self.list_servers(project['project_id'])

        return self.inst_array

    def create_server(self,create_dict):
        """
        DESC: Build a new virtual instance.
        INPUT: create_dict - project_id - req
                             instance_name - req - name of the instance
                             sec_group_name - default project security group if none specified
                             sec_key_name - default project security key if none specified.
                             avail_zone - default availability zone - nova
                             network_name - default project net used if none specified
                             config_script - op
                             image_name - op - default system image used if none specified
                             image_id - REQ
                             flavor_name - op
                             flavor_id - REQ
                             volume_id - op - volume to boot the vm from.
        OUTPUT: r_dict - vm_name - vm name
                       - vm_id - vm id
                       - sec_key_name - security key name
                       - sec_group_name - security group name
                       - created_by - name of creater
                       - project_id - id of project
        ACCESS: Users can only build servers in the projects that they are members of includeing admin users.
        NOTE: If no zone is specified then the zone defaults to zone.
        """
        #do variable checks

        if(not create_dict):
            logger.sys_error("No dictionary passed into create_server operation.")
            raise Exception("No dictionary passed into create_server operation.")
        if(('flavor_id' not in create_dict) or ('instance_name' not in create_dict) or ('image_id' not in create_dict) or ('project_id' not in create_dict)):
            logger.sys_error("Required value not passed to create_server operation")
            raise Exception("Required value not passed to create_server operation")
        #account for optional params
        if('config_script' not in create_dict):
            create_dict['config_script'] = 'NULL'

        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to create virtual servers.")
            raise Exception("Status level not sufficient to create virtual servers.")

        #get the name of the project based on the id
        try:
           select = {"select":"proj_name","from":"projects","where":"proj_id='%s'" %(create_dict['project_id'])}
           proj_name = self.db.pg_select(select)
        except:
            logger.sql_error("Could not get the project name from Transcirrus DB.")
            raise Exception("Could not get the project name from Transcirrus DB.")

        #security group verification
        if('sec_group_name' not in create_dict):
            #get the default security group from the transcirrus db
            try:
                select_sec = {"select":'def_security_group_name', "from":'projects', "where":"proj_id='%s'" %(create_dict['project_id'])}
                get_sec = self.db.pg_select(select_sec)
            except:
                logger.sql_error("Could not find the default security group for this project in the database")
                raise Exception("Could not find the default security group for this project in the database")
            create_dict['sec_group_name'] = get_sec[0][0]
        else:
            #check if the group specified is associated with the users project
            try:
                select_sec = {"select":'sec_group_id', "from":'trans_security_group', "where":"proj_id='%s'" %(create_dict['project_id']),"and":"sec_group_name='%s'"%(create_dict['sec_group_name'])}
                get_sec = self.db.pg_select(select_sec)
                if(not get_sec[0][0]):
                    raise Exception("Could not find the specified security group. Please specify a security group for this instance or create a new security group for this instance.")
            except Exception as e:
                logger.sql_error("Error finding security group (%s) in database: %s" %(create_dict['sec_group_name'], e))
                raise Exception("Error finding security group (%s) in database: %s" %(create_dict['sec_group_name'], e))

        #security key verification
        if('sec_key_name' not in create_dict):
            #get the default security key from the transcirrus db
            try:
                select_key = {"select":'def_security_key_name', "from":'projects', "where":"proj_id='%s'" %(create_dict['project_id'])}
                sec_key = self.db.pg_select(select_key)
            except:
                logger.sql_error("Could not find the default security key for this project in the database")
                raise Exception("Could not find the default security key for this project in the database")
            create_dict['sec_key_name'] = sec_key[0][0]
        else:
            #check if the key specified is associated with the users project
            try:
                select_key = {"select":'sec_key_name', "from":'trans_security_keys', "where":"proj_id='%s'" %(create_dict['project_id'])}
                sec_key = self.db.pg_select(select_key)
            except:
                logger.sql_error("Error finding security key (%s) in database: %s" %(create_dict['sec_key_name'], e))
                raise Exception("Error finding security key (%s) in database: %s" %(create_dict['sec_key_name'], e))

        #network verification
        if('network_name' not in create_dict):
            #get the default security group from the transcirrus db
            try:
                select_net = {"select":'def_network_id', "from":'projects', "where":"proj_id='%s'" %(create_dict['project_id'])}
                net = self.db.pg_select(select_key)
                self.net_id = net[0][0]
            except:
                logger.sql_error("Could not find the specified network for create_server operation %s" %(create_dict['network_name']))
                raise Exception("Could not find the specified network for create_server operation %s" %(create_dict['network_name']))
        else:
            #check if the network specified is associated with the users project
            try:
                select_net = {"select":'net_id', "from":'trans_network_settings', "where":"proj_id='%s'"%(create_dict['project_id']), "and":"net_name='%s'" %(create_dict['network_name'])}
                net = self.db.pg_select(select_net)
                self.net_id = net[0][0]
            except:
                logger.sql_error("Could not find the specified network id for create_server operation %s" %(create_dict['network_name']))
                raise Exception("Could not find the specified network id for create_server operation %s" %(create_dict['network_name']))

        #verify the availability zone
        #NOTE: for the prototype zone will always be nova
        if('avail_zone' in create_dict):
            try:
                select_zone = {'select':'index','from':'trans_zones','where':"zone_name='%s'"%(create_dict['avail_zone'])}
                get_zone = self.db.pg_select(select_zone)
            except:
                logger.sql_error('The specifed zone is not defined.')
                raise Exception('The specifed zone is not defined.')
        elif(create_dict['avail_zone'] is None):
            create_dict['avail_zone'] = 'nova'
        else:
            #hack
            create_dict['avail_zone'] = 'nova'

        if('flavor_name' not in create_dict):
            create_dict['flavor_name'] = "flavor_id_" + create_dict['flavor_id']

        if('image_name' not in create_dict):
            create_dict['image_name'] = "image_id_" + create_dict['image_id']

        #check to see if the name is in the project
        servers = self.list_servers(create_dict['project_id'])
        for server in servers:
            if(server['server_name'] == create_dict['instance_name']):
                random.seed()
                #rand_id = random.randrange(0,100000)
                create_dict['instance_name'] = create_dict['instance_name']+'_%s'%(str(self.rannum))

        #connect to the rest api caller
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":create_dict['project_id']}
            if(create_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,create_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connec to the REST api caller in create_server operation.")
            raise Exception("Could not connec to the REST api caller in create_server operation.")

        try:
            self.body = None
            if('volume_id' in create_dict):
                self.body = '{"server": {"name": "%s", "imageRef": "%s", "block_device_mapping":[{"volume_id": "%s", "delete_on_termination": "1", "device_name": "vda"}], "flavorRef": "%s", "max_count": 1, "min_count": 1,"key_name": "%s","networks": [{"uuid": "%s"}],"security_groups": [{"name": "%s"}],"availability_zone":"%s"}}'%(create_dict['instance_name'],create_dict['image_id'],create_dict['volume_id'],
                                                                                                                                                                                                                                                                                                                                            create_dict['flavor_id'],create_dict['sec_key_name'],self.net_id,create_dict['sec_group_name'],
                                                                                                                                                                                                                                                                                                                                            create_dict['avail_zone'])
            else:
                self.body = '{"server": {"name": "%s", "imageRef": "%s", "key_name": "%s", "flavorRef": "%s", "max_count": 1, "min_count": 1,"networks": [{"uuid": "%s"}],"security_groups": [{"name": "%s"}],"availability_zone":"%s"}}' %(create_dict['instance_name'],create_dict['image_id'],create_dict['sec_key_name'],create_dict['flavor_id'],self.net_id,create_dict['sec_group_name'],create_dict['avail_zone'])
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/servers' %(create_dict['project_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": self.body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            raise e

        if(rest['response'] == 202):
            self.load = json.loads(rest['data'])
            #poll the status, if the status is ACTIVE
            server = {'server_id':self.load['server']['id'],'project_id':create_dict['project_id']}
            while(True):
                status = self.get_server(server)
                if(status['server_status'] == 'ACTIVE'):
                    logger.sys_info('Active server with ID %s.'%(self.load['server']['id']))
                    break
                elif(status['server_status'] == 'BUILD'):
                    logger.sys_info('Building server with ID %s.'%(self.load['server']['id']))
                    time.sleep(10)
                elif(status['server_status'] == 'ERROR'):
                    logger.sys_info('Server with ID %s failed to build.'%(self.load['server']['id']))
                    #delete the errored out instance
                    self.delete_server(server)
                    raise Exception("Could not create a new server due to an unknown error. Please contact your TransCirrus support representative %s. ERROR: 555"%(status['fault']))
            try:
                self.db.pg_transaction_begin()
                #add the instance values to the transcirrus DB
                # ALL NONE USED TO BE "NULL"
                ins_dict = {'inst_name':create_dict['instance_name'],'inst_int_ip':None,'inst_floating_ip':None,'proj_id':create_dict['project_id'],
                            'in_use':"1",'floating_ip_id':None,'inst_id':self.load['server']['id'],'inst_port_id':None,'inst_key_name':create_dict['sec_key_name'],
                            'inst_sec_group_name':create_dict['sec_group_name'],'inst_username':self.username,'inst_user_id':self.user_id,'inst_int_net_id':self.net_id,
                            'inst_ext_net_id':None,'inst_flav_name':create_dict['flavor_name'],'inst_image_name':create_dict['image_name'],
                            'inst_int_net_name':create_dict['network_name'],'inst_zone':create_dict['avail_zone']}
                self.db.pg_insert("trans_instances",ins_dict)
            except Exception as e:
                self.db.pg_transaction_rollback()
                logger.sql_error('Could not add the new virtual instance to the Transcirrus DB.')
                raise Exception('Could not add the new virtual instance to the Transcirrus DB. %s'%(e))
            else:
                #commit the db transaction
                self.db.pg_transaction_commit()
                r_dict = {'vm_name':create_dict['instance_name'],'vm_id':self.load['server']['id'],'sec_key_name':create_dict['sec_key_name'],
                          'sec_group_name':create_dict['sec_group_name'],'created_by':self.username,'project_id':create_dict['project_id'],'response':'202'}
                return r_dict
        else:
            ec.error_codes(rest)

    def get_server(self,input_dict):
        """
        DESC:Used to get detailed info for a specific virtual server.
        INPUT: input_dict - server_id
                          - project_id
        OUTPUT: r_dict - server_name
                       - server_id
                       - sec_key_name
                       - sec_group_name
                       - server_flavor
                       - flavor_id
                       - server_os
                       - server_net_id
                       - server_int_net - dict of int net info
                       - server_zone
                       - server_status
                       - server_state
                       - server_node
                       - server_public_ips
                       - floating_ip_id
                       - novnc_console
                       - date_created
                       - boot_from_vol
                       - fault
        ACCESS: All users can get information for a virtual server in their project they own.
                Admins can get info on any virtual server.
        """
        #server_int_net - {"fishnet": [{"version": 4, "addr": "192.0.23.4", "OS-EXT-IPS:type": "fixed"}]}
        if(('server_id' not in input_dict) or (input_dict['server_id'] == "")):
            logger.sys_error("The virtual server id was not specified or is blank.")
            raise Exception("The virtual server id was not specified or is blank.")
        if(('project_id' not in input_dict) or (input_dict['project_id'] == "")):
            logger.sys_error("The project id was not specifed or is blank.")
            raise Exception("The project id was not specifed or is blank.")

        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to get virtual servers.")
            raise Exception("Status level not sufficient to get virtual servers.")

        #get the name of the project based on the id
        try:
            select = {"select":"proj_name","from":"projects","where":"proj_id='%s'" %(input_dict['project_id'])}
            proj_name = self.db.pg_select(select)
        except:
            logger.sql_error("Could not get the project name from Transcirrus DB.")
            raise Exception("Could not get the project name from Transcirrus DB.")

        #get the detailed server info from openstack
        try:
            get_server = None
            if(self.user_level == 0):
                get_server = {'select':"inst_name,inst_id,inst_key_name,inst_sec_group_name,inst_flav_name,inst_image_name,inst_int_net_id,inst_zone,inst_floating_ip,floating_ip_id,proj_id", 'from':"trans_instances", 'where':"inst_id='%s'" %(input_dict['server_id'])}
            elif(self.user_level == 1):
                get_server = {'select':"inst_name,inst_id,inst_key_name,inst_sec_group_name,inst_flav_name,inst_image_name,inst_int_net_id,inst_zone,inst_floating_ip,floating_ip_id,proj_id", 'from':"trans_instances", 'where':"inst_id='%s'" %(input_dict['server_id']), 'and':"proj_id='%s'" %(self.project_id)}
            elif((self.user_level == 2) and (self.project_id == input_dict['project_id'])):
                get_server = {'select':"inst_name,inst_id,inst_key_name,inst_sec_group_name,inst_flav_name,inst_image_name,inst_int_net_id,inst_zone,inst_floating_ip,floating_ip_id,proj_id", 'from':"trans_instances", 'where':"inst_id='%s'" %(input_dict['server_id']), 'and':"inst_user_id='%s'" %(self.user_id)}
            server = self.db.pg_select(get_server)
        except Exception as e:
            logger.sys_error('Could not get server info: get_server %s'%(e))
            raise Exception('Could not get server info: get_server %s'%(e))

        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(input_dict['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the REST API.")
            raise Exception("Could not connect to the REST API.")

        try:
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'GET'
            api_path = '/v2/%s/servers/%s'%(input_dict['project_id'],input_dict['server_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error("Could not remove the instance %s" %(e))
            raise e

        load = json.loads(rest['data'])
        if(rest['response'] == 200):
            if('fault' in load['server']):
                self.fault = load['server']['fault']['message']
            else:
                self.fault = 'None'
            #If the field is empty just return
            if(not server):
                #if no DB entry return the status from Nova - Kind of a hack for the polling in create server
                r_dict = {'server_status':load['server']['status'],'fault':self.fault}
                return r_dict
            input_dict = {'project_id':input_dict['project_id'],'instance_id':input_dict['server_id']}
            novnc = self.server_actions.get_instance_console(input_dict)
            #build the return dictionary
            r_dict = {'server_name':server[0][0],'server_id':server[0][1],'server_key_name':server[0][2],'server_group_name':server[0][3],'server_flavor':server[0][4],'flavor_id':load['server']['flavor']['id'],
                      'server_os':server[0][5],'server_net_id':server[0][6],'server_int_net':load['server']['addresses'],'server_zone':server[0][7],'server_status':load['server']['status'],'server_state':load['server']['OS-EXT-STS:vm_state'],
                      'server_node':load['server']['hostId'],'server_public_ips':server[0][8],'floating_ip_id':server[0][9],'project_id':server[0][10],'novnc_console':novnc,'date_created':load['server']['created'],'fault':self.fault}

            #HACK - need to figure out how to get this from API
            #get if boot from vol
            get_boot = {'select':"vol_set_bootable,vol_attached",'from':"trans_system_vols",'where':"vol_attached_to_inst='%s'"%(server[0][1])}
            boot_from_vol = self.db.pg_select(get_boot)
            r_dict['boot_from_vol'] = 'false'
            if(len(boot_from_vol) >= 1):
                if(boot_from_vol[0][0] == 'true' and boot_from_vol[0][1] == 'true'):
                    r_dict['boot_from_vol'] = 'true'

            return r_dict
        elif(rest['response'] == 409):
            #logger.sys_error("Could not get server status %s"%(input_dict['server_id']))
            logger.sys_error("%s ERROR: 409"%(str(load['itemNotFound']['message'])))
        else:
            ec.error_codes(rest)

    def detach_all_servers_from_network(self,input_dict):
        """
        DESC: Used to detach all servers in a project from a specific network
        INPUT: input_dict - project_id
                          - net_id
        OUTPUT: 'OK' - success
                'ERROR' - fail
                'NA' - unknown
        ACCESS: Admins can detach servers in any project
                Power users can only detach servers in their project
                Users can not detach servers
        NOTE: None
        """

        #get the server ids in the project attached to the network.
        try:
            get_server = {'select':'inst_id','from':'trans_instances','where':"inst_int_net_id='%s'" %(input_dict['net_id']),'and':"proj_id='%s'"%(input_dict['project_id'])}
            servers = self.db.pg_select(get_server)
        except:
            logger.sql_error("Could not get the server in project %s name from Transcirrus DB :detach_all_servers_from_network"%(input_dict['project_id']))
            raise Exception("Could not get the server in project %s name from Transcirrus DB :detach_all_servers_from_network"%(input_dict['project_id']))

        for server in servers:
            server_dict = {'server_id':server[0],
                           'project_id':input_dict['project_id'],
                           'net_id':input_dict['net_id']
                            }
            detach_all = self.detach_server_from_network(server_dict)
            if(detach_all != 'OK'):
                return detach_all

        return 'OK'

    def detach_server_from_network(self,input_dict):
        """
        DESC: Used to detach a server in a project from a specific network
        INPUT: input_dict - server_id
                          - project_id
                          - net_id
        OUTPUT: 'OK' - success
                'ERROR' - fail
        ACCESS: Admins can detach servers in any project
                Power users can only detach servers in their project
                Users can not detach servers
        NOTE: None
        """
        #check if the project exists
        try:
            get_proj = {'select':"proj_name",'from':"projects",'where':"proj_id='%s'" %(input_dict['project_id'])}
            proj_name = self.db.pg_select(get_proj)
        except:
            logger.sql_error("Could not get the project from Transcirrus DB :detach_server_from_network")
            raise Exception("Could not get the project from Transcirrus DB :detach_server_from_network")

        #see if the network exists in the project
        try:
            get_net = {'select':"net_name",'from':"trans_network_settings",'where':"net_id='%s'" %(input_dict['net_id']),'and':"proj_id='%s'"%(input_dict['project_id'])}
            net_name = self.db.pg_select(get_net)
        except:
            logger.sql_error("Could not get the network name from Transcirrus DB :detach_server_from_network")
            raise Exception("Could not get the network name from Transcirrus DB :detach_server_from_network")

        #get the subnet IDs in the given network
        #Only allowing one sub per net for alpha. Will have to account for multiple subnets later.
        try:
            get_subs = {'select':"subnet_id",'from':"trans_subnets",'where':"net_id='%s'"%(input_dict['net_id'])}
            subnets = self.db.pg_select(get_subs)
        except:
            logger.sql_error("Could not get the subnets name from Transcirrus DB :detach_server_from_network")
            raise Exception("Could not get the subnets name from Transcirrus DB :detach_server_from_network")

        #check if the power user is in the project
        if(self.user_level == 1):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error('Power User %s is not in project %s'%(self.username,input_dict['project_id']))
                raise Exception('Power User %s is not in project %s'%(self.username,input_dict['project_id']))
        elif(self.user_level == 2):
            logger.sys_error('Users can not detach servers from networks :detach_serverfrom_network')
            raise Exception('Users can not detach servers from networks :detach_server_from_network')

        #get the server ids in the project attached to the network.
        try:
            get_server = {'select':'inst_name','from':'trans_instances','where':"inst_id='%s' and inst_int_net_id='%s'" %(input_dict['server_id'],input_dict['net_id']),'and':"proj_id='%s'"%(input_dict['project_id'])}
            server = self.db.pg_select(get_server)
        except:
            logger.sql_error("Could not get the server in project %s name from Transcirrus DB :detach_server_from_network"%(input_dict['project_id']))
            raise Exception("Could not get the server in project %s name from Transcirrus DB :detach_server_from_network"%(input_dict['project_id']))

        if(self.user_level <= 1):
            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":input_dict['project_id']}
                if(input_dict['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API: remove_net_port")
                raise Exception("Could not connect to the API: remove_net_port")

            try:
                get_body = ''
                get_header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                get_function = 'GET'
                get_api_path = '/v2/%s/servers/%s/os-interface' %(input_dict['project_id'],input_dict['server_id'])
                g_token = self.token
                get_sec = self.sec
                get_rest_dict = {"body": get_body, "header": get_header, "function":get_function, "api_path":get_api_path, "token": g_token, "sec": get_sec, "port":'8774'}
                get_rest = api.call_rest(get_rest_dict)
            except Exception as e:
                raise e

            #portID
            get_load = json.loads(get_rest['data'])

            if(get_rest['response'] == 200):
                #remove the server from the network
                try:
                    body = ''
                    header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                    function = 'DELETE'
                    #need to account for multiple ports in get_load
                    api_path = '/v2/%s/servers/%s/os-interface/%s' %(input_dict['project_id'],input_dict['server_id'],get_load['interfaceAttachments'][0]['port_id'])
                    token = self.token
                    sec = self.sec
                    rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                    rest = api.call_rest(rest_dict)
                except Exception as e:
                    raise e

                if(rest['response'] == 202):
                    #NOTE: need to add in a polling mechanism to report back status of the creation
                    try:
                        self.db.pg_transaction_begin()
                        # ALL NONE USED TO BE "NULL"
                        up_dict = {'table':"trans_instances",'set':"inst_int_net_id=NULL,inst_int_net_name=NULL",'where':"inst_id='%s'"%(input_dict['server_id'])}
                        self.db.pg_update(up_dict)
                    except:
                        self.db.pg_transaction_rollback()
                        logger.sql_error('Could not add the new virtual instance to the Transcirrus DB.')
                        raise Exception('Could not add the new virtual instance to the Transcirrus DB.')
                    else:
                        #commit the db transaction
                        self.db.pg_transaction_commit()
                        return 'OK'
                else:
                    ec.error_codes(rest)
            else:
                ec.error_codes(get_rest)

    def attach_server_to_network(self,input_dict):
        """
        DESC: Used to attach a server in a project to a specific network
        INPUT: input_dict - server_id
                          - project_id
                          - net_id
        OUTPUT: r_dict - server_ip
                       - server_port_d
                       - server_mac_addr
        ACCESS: Admins can attach servers in any project
                Power users can only attach servers in their project
                Users can not attach servers
        NOTE: None
        """
        try:
            get_proj = {'select':"proj_name",'from':"projects",'where':"proj_id='%s'" %(input_dict['project_id'])}
            proj_name = self.db.pg_select(get_proj)
        except:
            logger.sql_error("Could not get the project from Transcirrus DB :attach_server_from_network")
            raise Exception("Could not get the project from Transcirrus DB :attach_server_from_network")

        #see if the network exists in the project
        try:
            get_net = {'select':"net_name",'from':"trans_network_settings",'where':"net_id='%s'" %(input_dict['net_id']),'and':"proj_id='%s'"%(input_dict['project_id'])}
            net_name = self.db.pg_select(get_net)
        except:
            logger.sql_error("Could not get the project name from Transcirrus DB :attach_server_from_network")
            raise Exception("Could not get the project name from Transcirrus DB :attach_server_from_network")

        #get the subnet IDs in the given network
        #Only allowing one sub per net for alpha. Will have to account for multiple subnets later.
        try:
            get_subs = {'select':"subnet_id",'from':"trans_subnets",'where':"net_id='%s'"%(input_dict['net_id'])}
            subnets = self.db.pg_select(get_subs)
        except:
            logger.sql_error("Could not get the subnets name from Transcirrus DB :attach_server_from_network")
            raise Exception("Could not get the subnets name from Transcirrus DB :attach_server_from_network")

        #check if the power user is in the project
        if(self.user_level == 1):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error('Power User %s is not in project %s'%(self.username,input_dict['project_id']))
                raise Exception('Power User %s is not in project %s'%(self.username,input_dict['project_id']))
        elif(self.user_level == 2):
            logger.sys_error('Users can not detach servers from networks :attach_server_from_network')
            raise Exception('Users can not detach servers from networks :attach_server_from_network')

        #get the server ids in the project attached to the network.
        try:
            get_server = {'select':'inst_name','from':'trans_instances','where':"inst_id='%s' and inst_int_net_id='%s'" %(input_dict['server_id'],input_dict['net_id']),'and':"proj_id='%s'"%(input_dict['project_id'])}
            server = self.db.pg_select(get_server)
        except:
            logger.sql_error("Could not get the server in project %s name from Transcirrus DB :attach_server_from_network"%(input_dict['project_id']))
            raise Exception("Could not get the server in project %s name from Transcirrus DB :attach_server_from_network"%(input_dict['project_id']))

        if(self.user_level <= 1):
        #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":input_dict['project_id']}
                if(input_dict['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API: remove_net_port")
                raise Exception("Could not connect to the API: remove_net_port")

            #remove the server from the network
            try:
                body = '{"interfaceAttachment": {"net_id": "%s"}}'%(input_dict['net_id'])
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2/%s/servers/%s/os-interface' %(input_dict['project_id'],input_dict['server_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                self.db.pg_transaction_rollback()
                logger.sys_error("Could not attach server to network %s" %(e))
                raise e

            if(rest['response'] == 200):
                #NOTE: need to add in a polling mechanism to report back status of the creation
                load = json.loads(rest['data'])
                try:
                    self.db.pg_transaction_begin()
                    #add the instance values to the transcirrus DB
                    up_dict = {'table':"trans_instances",'set':"inst_int_net_id='%s',inst_int_net_name='%s',inst_port_id='%s'"%(input_dict['net_id'],net_name[0][0],load['interfaceAttachment']['port_id']),'where':"inst_id='%s'"%(input_dict['server_id'])}
                    self.db.pg_update(up_dict)
                except:
                    self.db.pg_transaction_rollback()
                    logger.sql_error('Could not add the new virtual instance to the Transcirrus DB: attach_server_from_network')
                    raise Exception('Could not add the new virtual instance to the Transcirrus DB: attach_server_from_network')
                else:
                    #commit the db transaction
                    self.db.pg_transaction_commit()
                    r_dict = {'server_ip': load['interfaceAttachment']['fixed_ips'][0]['ip_address'],
                              'server_port_d':load['interfaceAttachment']['port_id'],
                              'server_mac_addr':load['interfaceAttachment']['mac_addr']
                            }
                    return r_dict
            else:
                #util.http_codes(rest['response'],rest['reason'],rest['data'])
                ec.error_codes(rest)

    def update_server(self,update_dict):
        """
        DESC: Used to update a virtual servers name.
              users can only update their servers admins
              can update any server in the project
        INPUT: update_dict - server_id
                           - project_id
                           - new_server_name
        OUTPUT: r_dict - server_name
                       - server_id
        NOTE: at this time update can only update the server name per the Grizzly Rest API
        """
        if(('new_server_name' not in update_dict) or (update_dict['new_server_name'] == "")):
            logger.sys_error("The virtual server name was not specifed or is blank.")
            raise Exception("The virtual server name was not specifed or is blank.")
        if(('server_id' not in update_dict) or (update_dict['server_id'] == "")):
            logger.sys_error("The virtual server name was not specifed or is blank.")
            raise Exception("The virtual server name was not specifed or is blank.")
        if(('project_id' not in update_dict) or (update_dict['project_id'] == "")):
            logger.sys_error("The virtual server name was not specifed or is blank.")
            raise Exception("The virtual server name was not specifed or is blank.")

        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to get virtual servers.")
            raise Exception("Status level not sufficient to get virtual servers.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(update_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != update_dict['project_id']):
                logger.sys_error("Users can only update virtual serves in their project.")
                raise Exception("Users can only update virtual serves in their project.")

        #get the server id based on the name and the project
        try:
            select_id = {'select':"inst_user_id", 'from':"trans_instances", 'where':"inst_id='%s'" %(update_dict['server_id']), 'and':"proj_id='%s'" %(update_dict['project_id'])}
            serv_id = self.db.pg_select(select_id)
        except:
            logger.sql_error("Could not get the instance id or username from Transcirrus db fo update_server operation")
            raise Exception("Could not get the instance id or username from Transcirrus db fo update_server operation")

        #check the user name can update server name
        if(self.user_level != 0):
            if(self.user_id != serv_id[0][0]):
                logger.sys_error("Users can only update virtual servers they own.")
                raise Exception("Users can only update virtual servers they own.")

        #connect to the rest api caller
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the REST api caller in create_server operation.")
            raise Exception("Could not connect to the REST api caller in create_server operation.")

        #update the server name
        try:
            body = '{"server": {"name": "%s"}}' %(update_dict['new_server_name'])
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'PUT'
            api_path = '/v2/%s/servers/%s' %(update_dict['project_id'],update_dict['server_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            self.db.pg_transaction_rollback()
            logger.sys_error("Could not create the project %s" %(e))
            raise e

        if(rest['response'] == 200):
            load = json.loads(rest['data'])
            try:
                self.db.pg_transaction_begin()
                #add the instance values to the transcirrus DB
                up_dict = {'table':"trans_instances",'set':"inst_name='%s'" %(update_dict['new_server_name']),'where':"proj_id='%s'" %(update_dict['project_id']),'and':"inst_id='%s'" %(update_dict['server_id'])}
                self.db.pg_update(up_dict)
                #commit the db transaction
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error('Could not update instance %s from Transcirrus DB.'%(update_dict['server_id']))
                raise Exception('Could not update instance %s from Transcirrus DB.'%(update_dict['server_id']))
            else:
                self.db.pg_transaction_commit()
                r_dict = {'server_name':update_dict['new_server_name'],'server_id':load['server']['id']}
                return r_dict
        else:
            self.db.pg_transaction_rollback()
            #util.http_codes(rest['response'],rest['reason'],rest['data'])
            ec.error_codes(rest)

    def delete_server(self,delete_dict):
        """
        DESC: Deletes a virtual server. Users can only delete the servers they own.
              Admins can delete any server in their project.
        INPUT: delete_dict - server_id
                           - project_id
        OUTPUT: OK if deleted or error
        """
        if(not delete_dict['server_id']):
            logger.sys_error("The virtual server id was not supplied or is blank.")
            raise Exception("The virtual server id was not supplied or is blank.")

        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to delete virtual servers.")
            raise Exception("Status level not sufficient to delete virtual servers.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(delete_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != delete_dict['project_id']):
                logger.sys_error("Users can only delete virtual serves in their project.")
                raise Exception("Users can only delete virtual serves in their project.")

        #get the server id based on the name and the project
        try:
            select_id = {'select':"inst_user_id", 'from':"trans_instances", 'where':"inst_id='%s'" %(delete_dict['server_id']), 'and':"proj_id='%s'" %(delete_dict['project_id'])}
            user_id = self.db.pg_select(select_id)
        except:
            logger.sql_error("Could not get the instance user id from the TransCirrus DB.")
            raise Exception("Could not get the instance user id from the TransCirrus DB.")

        #check the user name can delete server name
        if(self.user_level != 0):
            if(self.user_id != user_id[0][0]):
                logger.sys_error("Users can only delete virtual servers they own.")
                raise Exception("Users can only delete virtual servers they own.")

        #connect to the rest api caller
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(self.project_id != delete_dict['project_id']):
                self.token = get_token(self.username,self.password,delete_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connec to the REST api caller in create_server operation.")
            raise Exception("Could not connec to the REST api caller in create_server operation.")

        #delete the server
        try:
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'DELETE'
            api_path = '/v2/%s/servers/%s' %(delete_dict['project_id'],delete_dict['server_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            self.db.pg_transaction_rollback()
            logger.sys_error("Could not delete the instance %s" %(e))
            raise e

        #check the response and make sure it is a 204
        if(rest['response'] == 204):
            try:
                self.db.pg_transaction_begin()
                del_dict = {"table":'trans_instances',"where":"inst_id='%s'" %(delete_dict['server_id']), "and":"proj_id='%s'" %(delete_dict['project_id'])}
                self.db.pg_delete(del_dict)
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error('Could not remove instance %s from Transcirrus DB.'%(delete_dict['server_id']))
                raise Exception('Could not remove instance %s from Transcirrus DB.'%(delete_dict['server_id']))
            else:
                self.db.pg_transaction_commit()
                return "OK"
        else:
            #util.http_codes(rest['response'],rest['reason'],rest['data'])
            ec.error_codes(rest)

#######Nova security#######
    def create_sec_group(self,create_sec):
        """
        DESC: Create a new security group with ports the ports specified,
              if no ports are specifed the default ports 22,80,443,3389 are used
              users can create security groups on in their project
        INPUT: dictionary create_sec - ports[] - op
                                     - transport - op - tcp/udp
                                     - enable_ping - op - true/false
                                     - group_name - req
                                     - group_desc - req
                                     - project_id - req
                                     - update - op - true/false
        OUTPUT: r_dict - sec_group_name
                       - sec_group_id
        ACCESS: Admins can create a security group in any prject, users and power
                users can only create security groups in their own projects.
        NOTE: The defualts are ports - 22,80,443,3389
                               transport - tcp
                               enable_ping - false
        """
        logger.sys_info('\n**Creating security group. Nova:server.py Def: create_sec_group**\n')
        #NOTE: after prototype we will want to have the ability to have more then one security group in a project
        #      for now building out 1 in enough. Will also have to make a table in the DB to track them.
        #do variable checks
        if('update' not in create_sec):
            create_sec['update'] = 'false'
        if(not create_sec):
            logger.sys_error("No dictionary passed into create_sec_group operation.")
            raise Exception("No dictionary passed into create_sec_group operation.")
        if(create_sec['update'] == 'false'):
            if('group_name' not in create_sec):
                logger.sys_error("Required value not passed to create_sec_group operation")
                raise Exception("Required value not passed to create_sec_group operation")
            #check if the group name exists, this is a huge hack
            try:
                get_group_name = {'select':'sec_group_id','from':'trans_security_group',"where":"sec_group_name='%s'"%(create_sec['group_name'])}
                group = self.db.pg_select(get_group_name)
                if(group):
                    #raise Exception("Security group already exists in the cloud, please choose a new name.")
                    create_sec['group_name'] = str(create_sec['group_name']) + '_%s'%(self.rannum)
                    logger.sys_error("Security group already exists in the cloud, assigning new name %s."%(create_sec['group_name']))
            except:
                logger.sql_error("Failed while checking security group.")
                raise Exception("Failed while checking security group.")
            if(('group_desc' not in create_sec) or (create_sec['group_desc'] == "")):
                create_sec['group_desc'] = "none"

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(create_sec['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != create_sec['project_id']):
                logger.sys_error("Users can only create security groups in their project.")
                raise Exception("Users can only create security groups in their project.")

        #determin if pings should be enabled.
        if(('enable_ping' not in create_sec) or (create_sec['enable_ping'] == 'true')):
            create_sec['enable_ping'] = 'true'
        else:
            ping = create_sec['enable_ping']
            ping = ping.lower()
            if(ping == 'true'):
                create_sec['enable_ping'] = 'true'
            else:
                create_sec['enable_ping'] = 'false'

        #account for optional params
        ports = []
        if('ports' not in create_sec):
            ports = [443,80,22,3389]
        else:
            ports = create_sec['ports']

        #the transport protocol for the group tcp/udp
        transport = 'tcp'
        if('transport' in create_sec):
            if(create_sec['transport'] == 'tcp' or create_sec['transport'] == 'udp'):
                transport = create_sec['transport']
            else:
                logger.sys_error("Invalid transport for security group %s"%(create_sec['group_name']))
                raise Exception("Invalid transport for security group %s"%(create_sec['group_name']))

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":create_sec['project_id']}
            if(create_sec['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,create_sec['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        #create a new security group in the project
        if(create_sec['update'] == 'false'):
            try:
                body = '{"security_group": {"name": "%s", "description": "%s"}}' %(create_sec['group_name'],create_sec['group_desc'])
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json","X-Auth-Project-Id":project[0][0]}
                function = 'POST'
                api_path = '/v2/%s/os-security-groups' %(create_sec['project_id'])
                logger.sys_info('%s'%(api_path))
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                self.db.pg_transaction_rollback()
                logger.sys_error("Could not create security group %s" %(e))
                raise e

            if((rest['response'] == 200) or (rest['response'] == 203)):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                security = json.loads(rest['data'])
                get_def_group = {"select":"def_security_group_id", "from":"projects", "where":"proj_id='%s'" %(create_sec['project_id'])}
                def_group = self.db.pg_select(get_def_group)
                logger.sys_info("%s"%(def_group))
                try:
                    self.db.pg_transaction_begin()
                    #if the default is empty and the user is an admin add a default
                    if(def_group[0][0] == '0'):
                        if(self.is_admin == 1):
                            update_dict = {'table':"projects",'set':"""def_security_group_id='%s',def_security_group_name='%s'""" %(str(security['security_group']['id']),str(security['security_group']['name'])),'where':"proj_id='%s'" %(create_sec['project_id'])}
                            self.db.pg_update(update_dict)
                    #add the security group info to the database
                    insert_dict = {"proj_id":create_sec['project_id'],"user_name":self.username,"user_id":self.user_id,"sec_group_id":str(security['security_group']['id']),"sec_group_name":str(security['security_group']['name']),"sec_group_desc":create_sec['group_desc']}
                    self.db.pg_insert("trans_security_group",insert_dict)
                except:
                    self.db.pg_transaction_rollback()
                    logger.sql_error("Could not add in the new security group")
                    raise Exception("Could not add in the new security group")
                else:
                    self.db.pg_transaction_commit()
                    self.sec_group_id = str(security['security_group']['id'])
            else:
                util.http_codes(rest['response'],rest['reason'],rest['body'])
        elif(create_sec['update'] == 'true'):
            self.sec_group_id = create_sec['group_id']

        #add the ports to the sec group NOTE need to determin if we move this to the
        #network libs, it uses the quantum REST API for time sake keeping function here
        try:
            for i in range(len(ports)):
                body = '{"security_group_rule": {"direction": "ingress", "port_range_min": "%s", "tenant_id": "%s", "ethertype": "IPv4", "port_range_max": "%s", "protocol": "%s", "security_group_id": "%s"}}' %(ports[i],create_sec['project_id'],ports[i],transport,self.sec_group_id)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json", "Accept": "application/json"}
                function = 'POST'
                api_path = '/v2.0/security-group-rules'
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 200 or 201
                if((rest['response'] == 200) or (rest['response'] == 201)):
                    #build up the return dictionary and return it if everythig is good to go
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    logger.sys_info("Added port %s to security group %s." %(ports[i],self.sec_group_id))
                elif(rest['response'] == 409):
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                else:
                    util.http_codes(rest['response'],rest['reason'],rest['body'])
            if(create_sec['enable_ping'] == 'true'):
                body = '{"security_group_rule": {"ethertype": "IPv4", "direction": "ingress", "tenant_id": "%s", "protocol": "icmp", "security_group_id": "%s"}}' %(create_sec['project_id'],self.sec_group_id)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json", "Accept": "application/json"}
                function = 'POST'
                api_path = '/v2.0/security-group-rules'
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
                rest = api.call_rest(rest_dict)
                if((rest['response'] == 200) or (rest['response'] == 201)):
                    #build up the return dictionary and return it if everythig is good to go
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    logger.sys_info("Added port %s to security group %s." %(ports[i],self.sec_group_id))
                elif(rest['response'] == 409):
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                else:
                    util.http_codes(rest['response'],rest['reason'])
        except:
            logger.sys_error("Could not add ports to security group")
            raise Exception("Could not add ports to security group")

        #return dictionary
        if(create_sec['update'] == 'true'):
            return 'OK'
        else:
            r_dict = {"sec_group_name": create_sec['group_name'],"sec_group_id": self.sec_group_id, "sec_group_ports": ports, "sec_group_transport": transport, "username": self.username }
            return r_dict

    def update_sec_group(self,update_sec):
        """
        DESC: Update an exisitng security group with new tcp/udp ports or enable pings
        INPUT: dictionary update_sec - ports[] - op
                                     - transport - op - tcp/udp
                                     - enable_ping - op - true/false
                                     - group_id - req
                                     - project_id - req
        OUTPUT: OK - success
                Exception - failure
        ACCESS: Admins can update any security group
                power users and users can only update security groups that they own
        """
        # Background info: security group rules are created on a per transport basis
        # (tcp/udp/icmp). So an update is done on a per transport basis.
        # For an update to work properly, in the case of a port (rule) being deleted,
        # we have to delete all the rules for the given transport (tcp/udp). We will
        # then create all new rules for that transport based on the ports we were given.
        # Some of these ports would have already had rules and some may be new ports.
        # The icmp transport is handled a little differently. Since it is a true/false
        # for enabled or disabled, if icmp is to be disabled, we just need to delete
        # the rule (if it exists). If it is to be enabled, we just need to create the rule.

        # Indicate this is an update so the create won't create a new group.
        update_sec['update'] = 'true'

        # Delete all the rules for the transport (tcp or udp) for the group we are updating.
        self.delete_sec_group_rules(update_sec)

        if (update_sec['enable_ping'] == "false"):
            # Delete the rule for icmp.
            self.delete_sec_group_rules(update_sec, delete_icmp=True)

        # Create new rules for tcp or udp (and icmp if requested) for the given group.
        update_group = self.create_sec_group(update_sec)

        if(update_group == "OK"):
            return "OK"
        else:
            return "ERROR"


    def create_sec_keys(self,key_dict):
        """
        DESC: Build out security keys used to connect to the cloud instances. Users and admins
              can only build key in their own project. All project users should have their own
              key especially in the case of VDI setups. If the default fields in the project table are
              empty then a default key will be added to the projects table. The Public and private key
              will be stored in the datbase.
        INPUT: key_dict - key_name
                        - project_id
        OUTPUT: dictionary r_dict - key_name
                                  - key_id
        """
        #sanity
        if((key_dict['key_name'] == '') or ('key_name' not in key_dict)):
            logger.sys_error("Key name was either blank or not specified for create security key operation.")
            raise Exception("Key name was either blank or not specified for create security key operation.")
        if((key_dict['project_id'] == '') or ('project_id' not in key_dict)):
            logger.sys_error("Project id was either blank or not specified for create security key operation.")
            raise Exception("Project id was either blank or not specified for create security key operation.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(key_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != key_dict['project_id']):
                logger.sys_error("Users can only create security groups in their project.")
                raise Exception("Users can only create security groups in their project.")

        get_key = {'select':'sec_key_name','from':'trans_security_keys','where':"sec_key_name='%s'"%(key_dict['key_name'])}
        key = self.db.pg_select(get_key)
        if(key):
            #raise Exception("Security group already exists in the cloud, please choose a new name.")
            key_dict['key_name'] = str(key_dict['key_name']) + '_%s'%(self.rannum)
            logger.sys_error("Security group already exists in the cloud, assigning new name %s."%(key_dict['key_name']))

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":key_dict['project_id']}
            if(key_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,key_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        try:
            body = '{"keypair": {"name": "%s"}}' %(key_dict['key_name'])
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json", "Accept": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/os-keypairs' %(key_dict['project_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            self.db.pg_transaction_rollback()
            logger.sys_error("Could not create the keys pairs %s in project %s: %s" % (key_dict['key_name'], key_dict['project_id'], e))
            raise Exception("Could not create the keys pairs %s in project %s: %s" % (key_dict['key_name'], key_dict['project_id'], e))

        if(rest['response'] == 200):
            #build up the return dictionary and return it if everythig is good to go
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            seckey = json.loads(rest['data'])
            #check to see if there is a default key
            get_def_key = {"select":"def_security_key_id", "from":"projects", "where":"proj_id='%s'" %(key_dict['project_id'])}
            def_key = self.db.pg_select(get_def_key)
            try:
                self.db.pg_transaction_begin()
                #if the default is empty and the user is an admin add a default
                if(def_key[0][0] == '0'):
                    if(self.is_admin == 1):
                        update_dict = {'table':"projects",'set':"""def_security_key_id='%s',def_security_key_name='%s'""" %(str(seckey['keypair']['fingerprint']),str(seckey['keypair']['name'])),'where':"proj_id='%s'" %(key_dict['project_id'])}
                    self.db.pg_update(update_dict)
                #insert all of the relevent info into the transcirrus db
                insert_dict = {"proj_id":key_dict['project_id'],"user_name":self.username,"user_id":self.user_id,"sec_key_id":str(seckey['keypair']['fingerprint']),"sec_key_name":str(seckey['keypair']['name']),"public_key":str(seckey['keypair']['public_key']),"private_key":str(seckey['keypair']['private_key'])}
                self.db.pg_insert("trans_security_keys",insert_dict)
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not add the security key to the Transcirrus DB.")
                raise Exception("Could not add the security key to the Transcirrus DB.")
            else:
                self.db.pg_transaction_commit()
                r_dict = {"key_name":str(seckey['keypair']['name']), "key_id":str(seckey['keypair']['fingerprint'])}
                return r_dict
        else:
            ec.error_codes(rest)

    def delete_sec_group(self,sec_dict):
        """
        DESC: Only an admin can delete the default security group for the project.
              Users can only delete the groups that they have created, admins and
              power users can delete any security group
        INPUT: sec_dict - sec_group_id
                        - project_id
        OUTPUT: OK if deleted or error
        ACCESS: Admins can delete any security group, users and power users can only
                delete security groups in their project.
        """
        #sanity
        if((sec_dict['sec_group_id'] == "") or ('sec_group_id' not in sec_dict)):
            logger.sys_error("Security group id was either blank or not specified for delete security group operation.")
            raise Exception("Security group id was either blank or not specified for delete security group operation.")
        if((sec_dict['project_id'] == "") or ('project_id' not in sec_dict)):
            logger.sys_error("Security group name was either blank or not specified for delete security group operation.")
            raise Exception("Security group name was either blank or not specified for delete security group operation.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(sec_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != sec_dict['project_id']):
                logger.sys_error("Users can only create security groups in their project.")
                raise Exception("Users can only create security groups in their project.")

        #get the security group info from the db.
        try:
            get_group_dict = {'select':"*",'from':"trans_security_group",'where':"sec_group_id='%s'" %(sec_dict['sec_group_id']),'and':"proj_id='%s'" %(sec_dict['project_id'])}
            get_group = self.db.pg_select(get_group_dict)
        except:
            logger.sql_error("Could not get the security group info for sec_group: %s in project: %s" %(get_group[0][4],sec_dict['project_id']))
            raise Exception("Could not get the security group info for sec_group: %s in project: %s" %(get_group[0][4],sec_dict['project_id']))

        #if the group does not belong to the user raise exception
        if(get_group[0][2] != self.username):
            logger.sys_error("The security group %s does not belong to the user %s" %(get_group[0][4],self.username))
            raise Exception("The security group %s does not belong to the user %s" %(get_group[0][4],self.username))

        #if the user is and admin or power user check if the group is the default
        #if so set the flag
        flag = 0
        if((self.user_level == 0) or (self.user_level == 1)):
            check_def_dict = {"select":'def_security_group_id',"from":'projects', "where":"proj_id='%s'" %(sec_dict['project_id']),"and":"def_security_group_id='%s'" %(get_group[0][3])}
            check_def = self.db.pg_select(check_def_dict)
            if(check_def):
                flag = 1

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":sec_dict['project_id']}
            if(sec_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,sec_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        #create a new security group in the project
        try:
            body = ""
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'DELETE'
            api_path = '/v2/%s/os-security-groups/%s' %(sec_dict['project_id'],sec_dict['sec_group_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error("Could not remove the security group %s" %(get_group[0][4]))
            raise e

        #check the response and make sure it is a 200 or 201
        if(rest['response'] == 202):
            #build up the return dictionary and return it if everythig is good to go
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            try:
                self.db.pg_transaction_begin()
                #set the default security group back to NULL
                if(flag == 1):
                    update_dict = {'table':"projects",'set':"""def_security_group_id=NULL,def_security_group_name=NULL""",'where':"proj_id='%s'" %(sec_dict['project_id'])}
                    self.db.pg_update(update_dict)
                #delete the security group from the db
                delete_dict = {"table":'trans_security_group',"where":"sec_group_id='%s'" %(sec_dict['sec_group_id'])}
                self.db.pg_delete(delete_dict)
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error('Could not remove the security group from the Transcirrus DB.')
                raise Exception('Could not remove the security group from the Transcirrus DB.')
            else:
                self.db.pg_transaction_commit()
                return "OK"
        else:
            ec.error_codes(rest)

    def delete_sec_group_rules (self, rule_dict, delete_icmp=False, delete_all=False):
        """
        DESC: Delete security group rules for the given group.
              Only the rules for the given transport will be deleted
              unless delete_all is set to True.
        INPUT: dictionary rule_dict - ports[] - op
                                    - transport - op - tcp/udp
                                    - enable_ping - op - true/false
                                    - group_id - req
                                    - project_id - req
        OUTPUT: OK if deleted or ERROR
        ACCESS: Admins can delete any security group rules, users and power users can only
                delete security group rules in their project.
        """

        # Verify we have the data we need and that it is ok for this user to delete rules.
        if((rule_dict['group_id'] == "") or ('group_id' not in rule_dict)):
            logger.sys_error ("Security group id was either blank or not specified for delete security group rules operation.")
            raise Exception ("Security group id was either blank or not specified for delete security group rules operation.")

        if((rule_dict['project_id'] == "") or ('project_id' not in rule_dict)):
            logger.sys_error ("Project ID was either blank or not specified for delete security group rules operation.")
            raise Exception ("Project ID was either blank or not specified for delete security group rules operation.")

        # Check for ports.
        ports = []
        if ('ports' not in rule_dict):
            logger.sys_error ("No ports given for delete security group rules operation.")
            raise Exception ("No ports given for delete security group rules operation.")
        else:
            ports = rule_dict['ports']

        # Verify the transport protocol tcp or udp
        if ('transport' not in rule_dict):
            logger.sys_error ("No transport given for delete security group rules operation.")
            raise Exception ("No transport given for delete security group rules operation.")

        if (rule_dict['transport'] == 'tcp' or rule_dict['transport'] == 'udp'):
            transport = rule_dict['transport']
        else:
            logger.sys_error ("Invalid transport for security group rule delete %s" % (rule_dict['group_id']))
            raise Exception ("Invalid transport for security group rule delete %s" % (rule_dict['group_id']))

        # If they want to delete the icmp rule, then that is the only rule will delete.
        if (delete_icmp):
            transport = "icmp"

        try:
            get_proj = {'select': 'proj_name', 'from':'projects', 'where':"proj_id='%s'" % (rule_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error ("Project could not be found.")
            raise Exception ("Project could not be found.")

        if (self.is_admin == 0):
            if (self.project_id != rule_dict['project_id']):
                logger.sys_error ("Users can only delete security groups rules in their project.")
                raise Exception ("Users can only delete security groups rules in their project.")

        # Get the security group info from the db.
        try:
            get_group_dict = {'select':"*", 'from':"trans_security_group", 'where':"sec_group_id='%s'" % (rule_dict['group_id']), 'and':"proj_id='%s'" % (rule_dict['project_id'])}
            get_group = self.db.pg_select (get_group_dict)
        except:
            logger.sql_error ("Could not get the security group info for sec_group: %s in project: %s" % (rule_dict['group_id'], rule_dict['project_id']))
            raise Exception("Could not get the security group info for sec_group: %s in project: %s" % (rule_dict['group_id'], rule_dict['project_id']))

        # If we didn't get any data back then we have a bad sec_group_id or project_id.
        if (len(get_group) == 0):
            logger.sys_error ("Security group id %s does not belong to the project id %s" % (rule_dict['group_id'], rule_dict['project_id']))
            raise Exception ("Security group id %s does not belong to the project id %s" % (rule_dict['group_id'], rule_dict['project_id']))

        # If the group does not belong to the user raise exception.
        if (get_group[0][2] != self.username):
            logger.sys_error ("The security group %s does not belong to the user %s" % (get_group[0][4], self.username))
            raise Exception ("The security group %s does not belong to the user %s" % (get_group[0][4], self.username))

        # Connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":rule_dict['project_id']}
            if (rule_dict['project_id'] != self.project_id):
                self.token = get_token (self.username, self.password, rule_dict['project_id'])
            api = caller (api_dict)
        except:
            logger.sys_error ("Could not connect to the API caller")
            raise Exception ("Could not connect to the API caller")

        try:
            rule_dict['sec_group_id'] = rule_dict['group_id']
            group_dict = self.get_sec_group (rule_dict)
        except Exception as e:
            logger.sys_error ("Could not get sec_group list for rule delete: %s" % e)
            raise e

        # Delete the rules for the given transport or all the rules.
        try:
            for port in group_dict['ports']:
                if transport == port['transport'] or delete_all:
                    body = ""
                    header = {'X-Auth-Token': self.token, 'Content-Type': "application/json"}
                    function = "DELETE"
                    api_path = "/v2.0/security-group-rules/%s" % (port['rule_id'])
                    token = self.token
                    sec = self.sec
                    rest_dict = {'body': body, 'header': header, 'function': function, 'api_path': api_path, 'token': token, 'sec': sec, 'port': "9696"}
                    rest = api.call_rest(rest_dict)

                    # Check the response and if its not a 200 or 204 then return an error.
                    if ((rest['response'] != 200) and (rest['response'] != 204)):
                        logger.sys_error ("Error deleting sec_group rule: %s - %s" % (rest['response'], rest['reason']))
                        raise Exception ("Error deleting sec_group rule: %s - %s" % (rest['response'], rest['reason']))

        except Exception as e:
            logger.sys_error ("Exception delete rules for sec_group: %s" % e)
            raise e

        return "OK"


    def delete_sec_keys(self,delete_dict):
        """
        DESC: Delete the specified key
        INPUT: delete_dict - sec_key_name
                           - project_id
        OUTPUT: OK if deleted
        ACCESS: Admins and power users can delete any key in
                the project they are a member of. Users can only delete the keys they own.
                Only an Admin can delete the default security key
        """
        #sanity
        if(('sec_key_name' not in delete_dict) or (delete_dict['sec_key_name'] == "")):
            logger.sys_error("Security key name was either blank or not specified for delete security key operation.")
            raise Exception("Security key name was either blank or not specified for delete security key operation.")
        if(('project_id' not in delete_dict) or (delete_dict['project_id'] == "")):
            logger.sys_error("Security key name was either blank or not specified for delete security key operation.")
            raise Exception("Security key name was either blank or not specified for delete security key operation.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(delete_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != delete_dict['project_id']):
                logger.sys_error("Users can only create security groups in their project.")
                raise Exception("Users can only create security groups in their project.")

        try:
            get_key_dict = {"select":'*',"from":'trans_security_keys',"where":"sec_key_name='%s'" %(delete_dict['sec_key_name']),"and":"user_id='%s'" %(self.user_id)}
            get_key = self.db.pg_select(get_key_dict)
        except:
            logger.sql_error("Could not get the security key info for sec_key: %s in project: %s" %(sec_key_name,self.project_id))
            raise Exception("Could not get the security key info for sec_key: %s in project: %s" %(sec_key_name,self.project_id))

        if(get_key[0][2] != self.user_id):
            logger.sys_error("The security key %s does not belong to the user %s" %(delete_dict['sec_key_name'],self.username))
            raise Exception("The security key %s does not belong to the user %s" %(delete_dict['sec_key_name'],self.username))

        #if the user is and admin or power user check if the group is the default
        #if so set the flag
        flag = 0
        if((self.user_level == 0) or (self.user_level == 1)):
            check_def_dict = {"select":'def_security_key_id',"from":'projects', "where":"proj_id='%s'" %(delete_dict['project_id']),"and":"def_security_key_name='%s'" %(get_key[0][4])}
            check_def = self.db.pg_select(check_def_dict)
            if(check_def):
                flag = 1

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":delete_dict['project_id']}
            if(delete_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,delete_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        #create a new security group in the project
        try:
            body = ""
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'DELETE'
            api_path = '/v2/%s/os-keypairs/%s' %(delete_dict['project_id'],delete_dict['sec_key_name'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            self.db.pg_transaction_rollback()
            logger.sys_error("Could not remove the security key %s" %(delete_dict['sec_key_name']))
            raise e

        if(rest['response'] == 202):
            #build up the return dictionary and return it if everythig is good to go
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            try:
                self.db.pg_transaction_begin()
                #set the default security group back to NULL
                if(flag == 1):
                    update_dict = {'table':"projects",'set':"""def_security_key_id=NULL,def_security_key_name=NULL""",'where':"proj_id='%s'" %(delete_dict['project_id'])}
                    self.db.pg_update(update_dict)
                #delete the security group from the db
                del_dict = {"table":'trans_security_keys',"where":"sec_key_id='%s'" %(get_key[0][3])}
                self.db.pg_delete(del_dict)
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not remove the security key from the Transcirrus DB.")
                raise Exception("Could not remove the security key from the Transcirrus DB.")
            else:
                self.db.pg_transaction_commit()
                return "OK"
        else:
            ec.error_codes(rest)

    def list_sec_group(self,project_id=None):
        """
        DESC: list the security groups that belong to a user
        INPUT: self object
        OUTPUT: array of r_dict - sec_group_name
                                - sec_group_id
                                - owner_name
        ACCESS: admins and power users can list all of the security groups.
        """
        #This only queries the transcirrus db
        #get the security group info from the db.
        get_group_dict = None

        if(self.is_admin == 1):
            proj_id = project_id
            get_group_dict = {"select":'*',"from":'trans_security_group',"where":"proj_id='%s'" %(proj_id),"and":"user_id='%s'"%(self.user_id)}
        elif(self.user_level == 1):
            proj_id = self.project_id
            get_group_dict = {"select":'*',"from":'trans_security_group',"where":"proj_id='%s'" %(proj_id),"and":"user_id='%s'"%(self.user_id)}
        elif(self.user_level == 2):
            proj_id = self.project_id
            #HACK: we need to make it so that only the defaults are shown for a standard user until they make their own groups.
            #get_group_dict = {"select":'*',"from":'trans_security_group',"where":"proj_id='%s'"%(self.project_id),"and":"user_id='%s'" %(self.user_id)}
            get_group_dict = {"select":'*',"from":'trans_security_group',"where":"proj_id='%s'"%(proj_id),"and":"user_id='%s'"%(self.user_id)}
        else:
            logger.sys_error('Could not determin user type for sysgroup listing.')

        try:
            groups = self.db.pg_select(get_group_dict)
        except:
            logger.sql_error("Could not get the security group info for sec_group: %s in project: %s" %(get_group_dict[0][3],proj_id))
            raise Exception("Could not get the security key info for sec_key: %s in project: %s" %(get_group_dict[0][3],proj_id))

        group_array = []
        #build an array of r_dict
        for group in groups:
            r_dict = {"sec_group_name":group[5],"sec_group_id":group[4],"username":group[2], "project_id": proj_id }
            group_array.append(r_dict)

        #return the array
        return group_array

    def list_sec_keys(self,project_id=None):
        """
        DESC: List the security keys that belong to a user
        INPUT: None
        OUTPUT: Array of r_dict - key_name
                                - key_id - sec key fingerprint
                                - owner_name
        ACCESS: Admins can list all of the keys, power users can list all of the
                keys in the project, users can only list their keys.
        """

        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username,self.password,project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        #create a new security group in the project
        try:
            body = ""
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'GET'
            api_path = '/v2/%s/os-keypairs' %(project_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            self.db.pg_transaction_rollback()
            logger.sys_error("Could not list the security key.")
            raise e

        if(rest['response'] == 200):
            load = json.loads(rest['data'])
            key_array = []
            #build an array of r_dict
            for key in load['keypairs']:
                r_dict = {"key_name":key['keypair']['name'],"key_id":key['keypair']['fingerprint'],"username":self.username}
                key_array.append(r_dict)
            return key_array
        else:
            ec.error_codes(rest)

    def get_sec_group(self,sec_dict):
        """
        DESC: Get detailed info for a specific security group
              admins can get info on all groups in a project, users
              can only get info on the groups they own
        INPUT: sec_dict - sec_group_id
                        - project_id
        OUTPUT: r_dict - sec_group_name
                       - sec_group_id
                       - sec_group_desc
                       - transport - tcp/udp
                       - ports - array of ports
        NOTE: we will use a combination of the openstack and transcirrus db
        """
         #sanity
        # if((sec_dict['sec_group_id'] == '') or ('sec_group_id' not in sec_dict)):
        #     logger.sys_error("Security group name was either blank or not specified for delete security group operation.")
        #     raise Exception("Security group name was either blank or not specified for delete security group operation.")
        # if((sec_dict['project_id'] == '') or ('project_id' not in sec_dict)):
        #     logger.sys_error("Security group name was either blank or not specified for delete security group operation.")
        #     raise Exception("Security group name was either blank or not specified for delete security group operation.")

        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(sec_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")

        if(self.is_admin == 0):
            if(self.project_id != sec_dict['project_id']):
                logger.sys_error("Users can only create security groups in their project.")
                raise Exception("Users can only create security groups in their project.")

        #get the security group info from the db.
        try:
            #users can only get their own security groups
            get_group_dict = None
            if(self.user_level != 0):
                get_group_dict = {'select':"*",'from':"trans_security_group",'where':"sec_group_id='%s'" %(str(sec_dict['sec_group_id'])),'and':"user_id='%s'" %(self.user_id)}
            else:
                get_group_dict = {'select':"*",'from':"trans_security_group",'where':"sec_group_id='%s'" %(str(sec_dict['sec_group_id'])),'and':"proj_id='%s'" %(sec_dict['project_id'])}
            get_group = self.db.pg_select(get_group_dict)
        except:
            logger.sql_error("Could not get the security group info for sec_group: %s in project: %s" %(sec_dict['sec_group_id'],sec_dict['project_id']))
            raise Exception("Could not get the security group info for sec_group: %s in project: %s" %(sec_dict['sec_group_id'],sec_dict['project_id']))

        # If we didn't get any data back then we have a bad sec_group_id or user_id.
        if (len(get_group) == 0):
            if(self.user_level != 0):
                logger.sys_error ("Security group id %s does not belong to the user id %s" % (sec_dict['group_id'], self.user_id))
                raise Exception ("Security group id %s does not belong to the user id %s" % (sec_dict['group_id'], self.user_id))
            else:
                logger.sys_error ("Security group id %s does not belong to the project id %s" % (sec_dict['group_id'], sec_dict['project_id']))
                raise Exception ("Security group id %s does not belong to the project id %s" % (sec_dict['group_id'], sec_dict['project_id']))

        sec_group_name = get_group[0][5]

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":sec_dict['project_id']}
            if(sec_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,sec_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        try:
            body = ""
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'GET'
            #api_path = '/v2/%s/os-security-groups/%s' %(sec_dict['project_id'],sec_dict['sec_group_id'])
            api_path = '/v2.0/security-groups/%s' % (sec_dict['sec_group_id'])
            token = self.token
            sec = self.sec
            #rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9696'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error("Could not get listing for security group %s" %(sec_group_name))
            raise e

        #check the response and make sure it is a 200 or 201
        if(rest['response'] == 200):
            #build up the return dictionary and return it if everythig is good to go
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            rule_array = []
            #for rule in load['security_group']['rules']:
            for rule in load['security_group']['security_group_rules']:
                #rule_dict = {'from_port': str(rule['from_port']), 'to_port':str(rule['to_port']), 'cidr':str(rule['ip_range']['cidr']),'transport':str(rule['ip_protocol']),'rule_id':str(rule['id'])}
                rule_dict = {'from_port': str(rule['port_range_min']), 'to_port':str(rule['port_range_max']), 'cidr':str(rule['remote_ip_prefix']),'transport':str(rule['protocol']),'rule_id':str(rule['id'])}
                rule_array.append(rule_dict)
            r_dict = {'sec_group_name':get_group[0][5], 'sec_group_id': sec_dict['sec_group_id'], 'sec_group_desc':get_group[0][6],'ports':rule_array, 'project_id': sec_dict['project_id']}
            return r_dict
        else:
            util.http_codes(rest['response'],rest['reason'])

    def get_sec_keys(self,input_dict):
        """
        DESC: Get detailed info for a specific security key
        INPUT: input_dict - project_id
                          - sec_key_id
        OUTPUT: r_dict - sec_key_name
                       - user_name
                       - sec_key_id
                       - rsa_public_key
        ACCESS: Admins can get info on all keys in the project,
                users and power users can only get info on the keys they own
        """
        logger.sys_info('\n**Getting security key. Component: Nova Def: get_sec_keys**\n')
        if(('sec_key_id' not in input_dict) or (input_dict['sec_key_id'] == "")):
            logger.sys_error("Security key id was either blank or not specified for get security key operation.")
            raise Exception("Security key id was either blank or not specified for get security key operation.")

        #check for the project
        try:
            get_proj = {'select':"proj_name",'from':"projects",'where':"proj_id='%s'"%(input_dict['project_id'])}
            proj = self.db.pg_select(get_proj)
        except:
            logger.sys_error('Could not find project.')
            raise Exception('Could not find project.')

        #get the security group info from the db.
        try:
            #users can only get their own security groups
            get_key_dict = None
            if(self.is_admin == 0):
                #get_key_dict = {'select':"sec_key_name,sec_key_id,public_key,user_name",'from':"trans_security_keys",'where':"proj_id='%s'" %(input_dict['project_id']),'and':"user_id='%s' and sec_key_id='%s'" %(self.user_id,input_dict['sec_key_id'])}
                get_key_dict = {'select':"sec_key_name,sec_key_id,private_key,user_name",'from':"trans_security_keys",'where':"user_id='%s'"%(self.user_id),'and':"sec_key_id='%s'" %(input_dict['sec_key_id'])}
            else:
                #get_key_dict = {'select':"sec_key_name,sec_key_id,public_key,user_name",'from':"trans_security_keys",'where':"proj_id='%s'" %(input_dict['project_id']),'and':"sec_key_id='%s'"%(input_dict['sec_key_id'])}
                get_key_dict = {'select':"sec_key_name,sec_key_id,private_key,user_name",'from':"trans_security_keys",'where':"sec_key_id='%s'"%(input_dict['sec_key_id'])}
            get_key = self.db.pg_select(get_key_dict)
        except:
            logger.sql_error("Could not get the security group info for sec_key_name: %s in project: %s" %(get_key[0][0],input_dict['project_id']))
            raise Exception("Could not get the security group info for sec_key_name: %s in project: %s" %(get_key[0][0],input_dict['project_id']))

        r_dict = {'sec_key_name':get_key[0][0],'user_name':get_key[0][3],'sec_key_id':get_key[0][1],'public_key':get_key[0][2]}
        return r_dict
