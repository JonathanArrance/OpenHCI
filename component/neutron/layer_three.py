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

    #DESC: List the routers that are present in a project. All user types
    #      can list the routers in a project.
    #INPUT: self object
    #OUTPUT: array of r_dict - router_name
    #                        - router_status
    #                        - router_id
    #NOTE: this info can be gathered from the transcirrus db
    def list_routers(self):
        print "not implemented"
        
    #DESC: Get the information for a specific router. All user types can get
    #      the information for a router.
    #INPUT: router_name
    #OUTPUT: r_dict - router_name
    #               - router_status
    #               - router_id
    #               - project_id
    #               - networks - array of attached network ids
    #NOTE: this info can be gathered from the transcirrus db
    def get_router(self,router_name):
        print "not implemented"
        
    #DESC: Add a new router to a project. Only admins can add a new
    #      router to their project.
    #INPUT: router_name
    #OUTPUT: r_dict - router_name
    #               - router_id
    def add_routers(self,router_name):
        print "not implemented"
        
    #DESC: Update the basic router information. Only an admin can
    #      update a routers info. 
    #INPUT: toggle_dict - router_name - req
    #                   - router_admin_state(up/down) - op
    #OUTPUT: r_dict - router_name
    #               - router_admin_state
    def update_routers(self,toggle_dict):
        print "not implemented"

    #DESC: Remove a router from the project. Only admins can remove
    #      routers from a project. If any networks are attached an error
    #      will occure.
    #INPUT: router_name
    #OUTPUT: OK or error
    def delete_routers(self,router_name):
        print "not implemented"
        
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
