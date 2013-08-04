#!/usr/bin/python
# Used manage all Neutron(Quantum) Networks, subnets and network ports
# Refer to http://docs.openstack.org/api/openstack-network/2.0/content/API_Operations.html
# for all API information.

import sys
import json

sys.path.append('../../common')
import logger
import config

#get the db library path from the config file
sys.path.append(config.DB_PATH)
from postgres import pgsql

class neutron_ops:
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
        
    #DESC: List the networks available in a project. All user types can only
    #      list the networks that are availabel in their project.
    #INPUT: self object
    #OUTPUT: array of r_dict - net_name
    #                        - net_id
    #                        - shared (true/false)
    #                        - status
    def list_networks(self):
        print "not implemented"
        
    #DESC: Get the information on a specific network. All user types can only
    #      get the information on networks in their project.
    #INPUT: net_name
    #OUTPUT: r_dict - net_id
    #               - shared (true/false)
    #               - status
    #               - subnet_array[]
    def get_network(self,net_name):
        print "not implemented"

    #DESC: Create a network in the project. Only a project admin can create
    #      a new network. Users and power users can not create networks.
    #INPUT: create_dict - net_name
    #                   - admin_state (up/down)
    #                   - shared (true/false)
    #OUTPUT: r_dict - net_name
    #               - net_id
    #NOTE: need to update the transcirrus db with the new network.
    def add_network(self,create_dict):
        print "not implemented"

    #DESC: Remove a network from a project. Only project admin can remove
    #      a network. Can not remove default system networks.
    #INPUT: net_name
    #OUTPUT: "OK" if removed or error
    #NOTE: networks in use can not be removed. API throws 409 error. Also
    #      need to update transcirrus db
    def remove_network(self,net_name):
        print "not implemented"

    #DESC: Toggles the network admin state from up to down or down to
    #      up. Only admins can toggle the network state
    #INPUT: toggle_dict
    #OUTPUT: r_dict - net_id
    #               - net_status
    #               - admin_state
    def update_network(self,toggle_dict):
        print "not implemented"

    #DESC: Lists the subnets for the specified network. All user types can
    #      list the subnets in the project networks.
    #INPUT: net_name
    #OUTPUT: array of r_dict - subnet_name
    #                        - subnet_id
    #NOTE: all of the return info can be quried from the transcirrus db. May use
    #      rest api to verify subent exsists(not required).
    def list_net_subnet(self,net_name):
        print "not implemented"

    #DESC: Get all of the information for a specific subnet. All user types
    #      can get information for subnets in the project networks.
    #INPUT: subnet_name
    #OUTPUT: r_dict - subnet_id
    #               - subnet_class
    #               - subnet_ip_ver
    #               - subnet_cidr
    #               - subnet_gateway
    #               - subnet_allocation_start
    #               - subnet_allocation_end
    #               - subnet_dhcp_enable
    #NOTE: all of the return info can be quried from the transcirrus db. May use
    #      rest api to verify subent exsists(not required).
    def get_net_subnet(self,subnet_name):
        print "not implemented"

    #DESC: Add a new subnet to a project subnet. Only admins can add a subnet to
    #      a network in their project.
    #INPUT: subnet_dict - subnet_id
    #                   - subnet_class
    #                   - subnet_ip_ver
    #                   - subnet_cidr
    #                   - subnet_gateway
    #                   - subnet_allocation_start
    #                   - subnet_allocation_end
    #                   - subnet_dhcp_enable
    #OUTPUT: r_dict - subnet_name
    #               - subnet_id
    #NOTE: REST API will throw a 409 error if there is a conflict
    def add_net_subnet(self,subnet_dict):
        print "not implemented"

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
    def update_net_subnet(self,update_dict):
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