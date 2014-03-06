#!/usr/local/bin/python2.7
import sys
import json

import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

#######Reference#######
#http://docs.openstack.org/api/openstack-network/2.0/content/security-groups-ext.html

class net_security_ops:
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
        
    #DESC: Add ports to the specified security group. Users can add ports
    #      to the group they own admins can add ports to any group in the
    #      project
    #INPUT: port_dict - sec_group_name
    #                 - ports - array of port(s) to add
    #OUTPUT: r_dict - sec_group_name
    #               - sec_group_id
    def add_sec_group_rule(self,port_dict):
        #add the ports to the sec group NOTE need to determin if we move this to the
        #network libs, it uses the quantum REST API for time sake keeping function here
        try:
            for i in range(len(ports)):
                body = '{"security_group_rule": {"direction": "ingress", "port_range_min": "%s", "tenant_id": "%s", "ethertype": "IPv4", "port_range_max": "%s", "protocol": "tcp", "security_group_id": "%s"}}' %(ports[i],self.project_id,ports[i],self.sec_group_id)
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
                else:
                    _http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not remove the project %s" %(e))

        #return dictionary
        r_dict = {"sec_group_name": create_sec['group_name'],"sec_group_id": self.sec_group_id}
        return r_dict

    #DESC: Remove pots from a security group. Users can only remove ports from
    #      the security groups they own. Admins can remove ports from any security group
    #      in their project
    #INPUT: port_dict - sec_group_name
    #                 - ports - array of port(s) to remove
    #OUTPUT: OK on success.
    def remove_sec_group_rule(self,port_dict):
        print "not implemented"
        
    #DESC: List all rules for a security group. Users can only list ports from
    #      the security groups they own. Admins and power users can list ports
    #      from any security group in the project
    #INPUT: Self object
    #OUTPUT: array of r_dict - sec_group_name
    #                        - sec_group_id
    #                        - rule_id
    def list_sec_group_rules(self):
        print "not implemented"
        
    #DESC: Get the specifics on a rule in a security group. Users can only get rule info
    #      for security groups they made inthe project. Admins and power users can get info
    #      on any rule in any group in the project.
    #INPUT: rule_dict - sec_group_name
    #                 - rule_id
    #OUTPUT: r_dict - sec_group_name
    #               - sec_group_name
    #               - port_range_min
    #               - port_range_max
    #               - direction
    #               - ip_version
    def get_sec_group_rule(self,rule_dict):
        print "not implemented"
        
    #DESC: Remove a security group. Users can only remove the security groups they own.
    #      Admins can remove any security group in their project.
    #INPUT: port_dict - sec_group_name
    #OUTPUT: OK on success.
    #NOTE: All security groups need to be removed from the Transcirrus DB as well.
    def remove_sec_group(self,port_dict):
        print "not implemented"
        
    #DESC: List all security groups. Users can only list ports from the security groups
    #      they own. Admins and power users can list all security groups in the project
    #INPUT: Self object
    #OUTPUT: array of r_dict - sec_group_name
    #                        - sec_group_id
    def list_sec_groups(self):
        print "not implemented"
        
    #DESC: Get the specifics on a security group. Users can only get info
    #      for security groups they made inthe project. Admins and power users
    #      can get info on any group in the project.
    #INPUT: rule_dict - sec_group_name
    #OUTPUT: r_dict - sec_group_name
    #               - description
    #               - sec_group_id
    #               - array rule_dict - rule_id
    #                                 - port_range_min
    #                                 - port_range_max
    #                                 - direction
    #                                 - ip_version
    def get_sec_group(self,sec_group_name):
        print "not implemented"
        
    #DESC: Add the specified security group. Users, Admins and Power Users
    #      can only add security groups to the projects that the belong to.
    #INPUT: group_dict - sec_group_name
    #                 - description
    #OUTPUT: r_dict - sec_group_name
    #               - sec_group_id
    #NOTE: All new security groups need to be tracked in the Transcirrus DB.
    def add_sec_group(self,group_dict):
        print "not implemented"
