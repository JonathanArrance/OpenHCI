#!/usr/bin/python
#######standard impots#######
import sys
import json

sys.path.append('../../common')
import logger
import config

#get the transcirrus api caller
from api_caller import caller

#get the db library path from the config file
sys.path.append(config.DB_PATH)
from postgres import pgsql
import flavor

#######Special imports#######
sys.path.append('/home/jonathan/alpo.0/component/neutron')
from security import net_security_ops

class server_ops:
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

    #DESC:
    #INPUT:
    #OUTPUT:
    def list_servers(self):
        print "not implemented"
        
    #DESC: Build a nee virtual instance. Users can only build servers
    #      in the projects that they are members of includeing admin users
    #INPUT: create_dict - config_script - op
    #                     security_group - default project group if none specified
    #                     avail_zone - default availability zone - nova
    #                     server - Server
    #                     image - req - image name
    #                     flavor - req - flavor name
    #                     name - req - name of the server
    #                     
    #OUTPUT: r_dict - name - vm name
    #                 id - vm id
    #                 key_name - security key name
    #                 security_group - security group name
    #                 created - time created
    #                 created_by - name of creater
    #                 creater_id - id of creater
    #                 project_id - id of project
    def create_server(self,create_dict):
        #do variable checks
        if(not create_dict):
            logger.sys_error("No dictionary passed into create_server operation.")
            raise Exception("No dictionary passed into create_server operation.")
        if(('image' not in create_dict) or ('flavor' not in create_dict) or ('name' not in create_dict)):
            logger.sys_error("Required value not passed to create_server operation")
            raise Exception("Required value not passed to create_server operation")
        #account for optional params
        if('config_script' not in create_dict):
            create_dict['config_script'] = 'NULL'

        #security group verification
        if('sec_group' not in create_dict):
            #check the security group
            try:
                select_sec = {"select":'security_group_name', "from":'projects', "where":"proj_id='%s'" %(self.project_id)}
                get_sec = self.db.pg_select(select_sec)
            except:
                logger.sql_error("Could not find the specified security key for create_server operation %s" %(create_dict['name']))
                raise Exception("Could not find the specified security key for create_server operation %s" %(create_dict['name']))
            create_dict['security_group'] = get_sec[0][0]
        else:
            #check if the group specified is associated with the users project
            try:
                select_sec = {"select":'sec_group_id', "from":'trans_sec_group', "where":"proj_id='%s'" %(self.project_id), "and":"sec_group_name='%s'" %(create_dict['security_group'])}
                get_sec = self.db.pg_select(select_sec)
            except:
                logger.sql_error("Could not find the specified security key for create_server operation %s" %(create_dict['name']))
                raise Exception("Could not find the specified security key for create_server operation %s" %(create_dict['name']))

        #verify the availability zone
        #NOTE: for the prototype zone will always be nova
        if(('avail_zone' not in create_dict) or ('avail_zone' in create_dict)):
            create_dict['avail_zone'] = 'nova'

        #connect to the rest api caller
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connec to the REST api caller in create_server operation.")
            raise Esception("Could not connec to the REST api caller in create_server operation.")

        #verify that the flavor requested exists
        #get the flavor from the list
        flav_list = flavor.list_flavors()
        flav_name = ""
        info = ""
        for flav in flav_list:
            if(flav['flavor_name'] == create_dict['flavor']):
                info = flavor.get_flavor(create_dict['flavor'])
            else:
                logger.sys_error("The flavor: %s was not found" %(create_dict['flavor']))
                raise Exception("The flavor: %s was not found" %(create_dict['flavor']))
        print info


        #verify the image requested exsists
        
        #build the server
        
    #DESC:Used to ge the status of the server
    #     if the poll option is specified in the dictionary
    #     only the server progress is returned
    #INPUT:
    #OUTPUT:
    def get_server(self,server_dict):
        print "not implemted"
        
    #DESC:
    #INPUT:
    #OUTPUT:
    def update_server(self,update_dict):
        print "not implemented"
        
    #DESC:
    #INPUT:
    #OUTPUT:
    def delete_server(self,server_name):
        print "not implemented"
        

#######Nova security#######

    #DESC:Create a new security group with ports the ports specified,
    #     if no ports are specifed the default ports 22,80,443 are used
    #     users can create security groups on in their project
    #INPUT: dictionary create_sec - ports[] - op
    #                             - group_name - req
    #                             - group_desc - req
    #OUTPUT: r_dict - group_name
    #               - group_id
    def create_sec_group(self,create_sec):
        #NOTE: after prototype we will want to have the ability to have more then one security group in a project
        #      for now building out 1 in enough. Will also have to make a table in the DB to track them.
        #do variable checks
        if(not create_sec):
            logger.sys_error("No dictionary passed into create_sec_group operation.")
            raise Exception("No dictionary passed into create_sec_group operation.")
        if(('group_name' not in create_sec) or ('group_desc' not in create_sec)):
            logger.sys_error("Required value not passed to create_sec_group operation")
            raise Exception("Required value not passed to create_sec_group operation")
        #account for optional params
        ports = []
        if('ports' not in create_sec):
            ports = [443,80,22]
        else:
            ports = create_sec['ports']

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        #create a new security group in the project
        try:
            body = '{"security_group": {"name": "%s", "description": "%s"}}' %(create_sec['group_name'],create_sec['group_desc'])
            header = headers = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/os-security-groups' %(self.project_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200 or 201
            if((rest['response'] == 200) or (rest['response'] == 203)):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                security = json.loads(rest['data'])
                #add the security group info to the database
                update_dict = {'table':"projects",'set':"""security_group_id='%s',security_group_name='%s_sec'""" %(str(security['security_group']['id']),create_sec['group_name']),'where':"proj_id='%s'" %(self.project_id)}
                self.db.pg_update(update_dict)
                self.sec_group_id = str(security['security_group']['id'])
            else:
                _http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not remove the project %s" %(e))

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
        r_dict = {"group_name": create_sec['group_name'],"group_id": self.sec_group_id}
        return r_dict


    #DESC: Build out security keys used to connect to the cloud instances. Users and admins
    #      can only build key in their own project a default key will be built when the project is
    #      created. All project users should have their own key especially in the case of VDI setups
    #INPUT: key_name
    #OUTPUT: dictionary r_dict - pub_key
    #                          - private_key
    #                          - key_id
    def create_sec_keys(self,key_name):
        print "not implemented"
        
    #DESC: Only ab admin can delete the default security group for the project.
    #INPUT:
    #OUTPUT:
    def delete_sec_group(self,server_name):
        print "not implemented"
        
    #DESC: Delete the specified key admins and power users can delete any key in
    #      the project they are a member of. Users can only delete the keys they own.
    #      Only an Admin can delete the default security key
    #INPUT:
    #OUTPUT:
    def delete_sec_keys(self,server_name):
        print "not implemented"
        
    #DESC:
    #INPUT:
    #OUTPUT:
    def list_sec_group(self,server_name):
        print "not implemented"
        
    #DESC:
    #INPUT:
    #OUTPUT:
    def list_sec_keys(self,server_name):
        print "not implemented"
        
    #DESC:
    #INPUT:
    #OUTPUT:
    def get_sec_group(self,server_name):
        print "not implemented"
        
    #DESC:
    #INPUT:
    #OUTPUT:
    def get_sec_keys(self,server_name):
        print "not implemented"
        
    #DESC:
    #INPUT:
    #OUTPUT:
    def update_sec_group(self,server_name):
        print "not implemented"
        
    #DESC:
    #INPUT:
    #OUTPUT:
    def update_sec_keys(self,server_name):
        print "not implemented"

######Internal defs#######
def _http_codes(code,reason):
    if(code):
        logger.sys_error("Response %s with Reason %s" %(code,reason))
        raise Exception("Response %s with Reason %s" %(code,reason))
    else:
        logger.sys_error("Error for unknown reason.")
        raise Exception("Error for unknown reason.")
