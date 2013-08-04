#!/usr/bin/python
# Used manage agents that check in withthe network sever. This may be postponed until
#the alpo.1 release
# Refer to http://docs.openstack.org/api/openstack-network/2.0/content/agent_ext.html
# for all API information.

import sys
import json

sys.path.append('../../common')
import logger
import config

#get the db library path from the config file
sys.path.append(config.DB_PATH)
from postgres import pgsql

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

    #DESC: Lists all of the agents that report into the neutron(quantum) server
    #INPUT:
    #OUTPUT: array of r_dict - agent_name
    #                        - agent_id
    #                        - description
    #                        - agent_host
    def list_network_agents(self):
        print "not implemented"
        
    #DESC: Get the information for a specific agent that report into the neutron(quantum) server
    #INPUT: 
    #OUTPUT: r_dict - agent_name
    #               - description
    #               - last_heartbeat
    #               - agent_alive (true/false)
    #               - agent_host
    #               - agent_type
    def get_network_agents(self):
        print "not implemented"
        
    #DESC: Used to update the admin status or description of the agent checking into the network server
    #INPUT:
    #OUTPUT:
    def update_network_agent(self):
        print "not implemented"
        
    #DESC: Deletes the given network agent.
    #INPUT:
    #OUTPUT:
    def remove_network_agent(self):
        print "not implemented"