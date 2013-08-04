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
#sys.path.append('/home/jonathan/alpo.0/component/neutron')
#from security import net_security_ops

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
            #raise Exception("No admin tokens passed.")

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
    #OUTPUT: r_dict - sec_group_name
    #               - sec_group_id
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
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
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
                get_def_group = {"select":"def_security_group_id", "from":"projects", "where":"proj_id='%s'" %(self.project_id)}
                def_group = self.db.pg_select(get_def_group)
                self.db.pg_transaction_begin()
                #if the default is empty and the user is an admin add a default
                if((def_group[0][0] == "NULL") and (self.is_admin == 1)):
                    update_dict = {'table':"projects",'set':"""def_security_group_id='%s',def_security_group_name='%s'""" %(str(security['security_group']['id']),str(security['security_group']['name'])),'where':"proj_id='%s'" %(self.project_id)}
                    self.db.pg_update(update_dict)
                #add the security group info to the database
                insert_dict = {"proj_id":self.project_id,"user_name":self.username,"sec_group_id":str(security['security_group']['id']),"sec_group_name":str(security['security_group']['name'])}
                self.db.pg_insert("trans_security_group",insert_dict)
                self.sec_group_id = str(security['security_group']['id'])
            else:
                self.db.pg_transaction_rollback()
                _http_codes(rest['response'],rest['reason'])
        except Exception as e:
            self.db.pg_transaction_rollback()
            logger.sys_error("Could not remove the project %s" %(e))
            raise e

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
            raise e

        #return dictionary
        r_dict = {"sec_group_name": create_sec['group_name'],"sec_group_id": self.sec_group_id}
        return r_dict


    #DESC: Build out security keys used to connect to the cloud instances. Users and admins
    #      can only build key in their own project. All project users should have their own
    #      key especially in the case of VDI setups. If the default fields in the project table are
    #      empty then a default key will be added to the projects table. The Public and private key
    #      will be stored in the datbase.
    #INPUT: key_name
    #OUTPUT: dictionary r_dict - key_name
    #                          - key_id
    def create_sec_keys(self,key_name):
        #sanity
        if((not key_name) or (key_name == "")):
            logger.sys_error("Key name was either blank or not specified for create security key operation.")
            raise Exception("Key name was either blank or not specified for create security key operation.")

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        try:
            body = '{"keypair": {"name": "%s"}}' %(key_name)
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json", "Accept": "application/json"}
            function = 'POST'
            api_path = '/v2/%s/os-keypairs' %(self.project_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200 or 201
            if(rest['response'] == 200):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                seckey = json.loads(rest['data'])
                #check to see if there is a default key
                get_def_key = {"select":"def_security_key_id", "from":"projects", "where":"proj_id='%s'" %(self.project_id)}
                def_key = self.db.pg_select(get_def_key)
                self.db.pg_transaction_begin()
                #if the default is empty and the user is an admin add a default
                if((def_key[0][0] == "NULL") and (self.is_admin == 1)):
                    update_dict = {'table':"projects",'set':"""def_security_key_id='%s',def_security_key_name='%s'""" %(str(seckey['keypair']['fingerprint']),str(seckey['keypair']['name'])),'where':"proj_id='%s'" %(self.project_id)}
                    self.db.pg_update(update_dict)
                #insert all of the relevent info into the transcirrus db
                insert_dict = {"proj_id":self.project_id,"user_name":self.username,"sec_key_id":str(seckey['keypair']['fingerprint']),"sec_key_name":str(seckey['keypair']['name']),"public_key":str(seckey['keypair']['public_key']),"private_key":str(seckey['keypair']['private_key'])}
                self.db.pg_insert("trans_security_keys",insert_dict)
                self.db.pg_transaction_commit()

                r_dict = {"key_name":str(seckey['keypair']['name']), "key_id":str(seckey['keypair']['fingerprint'])}
                return r_dict
            else:
                self.db.pg_transaction_rollback()
                _http_codes(rest['response'],rest['reason'])
        except Exception as e:
            self.db.pg_transaction_rollback()
            logger.sys_error("Could not create the keys %s in project %s" %(key_name, self.project_id))
            raise e

    #DESC: Only an admin can delete the default security group for the project.
    #      Users can only delete the groups that they have created, admins and
    #      power users can delete any security group
    #INPUT: sec_group_name - string containing the security group name
    #OUTPUT: OK if deleted or error
    def delete_sec_group(self,sec_group_name):
        #sanity
        if((not sec_group_name) or (sec_group_name == "")):
            logger.sys_error("Security group name was either blank or not specified for delete security group operation.")
            raise Exception("Security group name was either blank or not specified for delete security group operation.")

        #get the security group info from the db.
        try:
            get_group_dict = {'select':"*",'from':"trans_security_group",'where':"sec_group_name='%s'" %(str(sec_group_name)),'and':"proj_id='%s'" %(self.project_id)}
            get_group = self.db.pg_select(get_group_dict)
        except:
            logger.sql_error("Could not get the security group info for sec_group: %s in project: %s" %(sec_group_name,self.project_id))
            raise Exception("Could not get the security group info for sec_group: %s in project: %s" %(sec_group_name,self.project_id))

        #if the group does not belong to the user raise exception
        if(get_group[0][2] != self.username):
            logger.sys_error("The security group %s does not belong to the user %s" %(sec_group_name,self.username))
            raise Exception("The security group %s does not belong to the user %s" %(sec_group_name,self.username))

        #if the user is and admin or power user check if the group is the default
        #if so set the flag
        flag = 0
        if((self.user_level == 0) or (self.user_level == 1)):
            check_def_dict = {"select":'def_security_group_id',"from":'projects', "where":"proj_id='%s'" %(self.project_id),"and":"def_security_group_name='%s'" %(get_group[0][4])}
            check_def = self.db.pg_select(check_def_dict)
            if(check_def):
                flag = 1

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        #create a new security group in the project
        try:
            body = ""
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'DELETE'
            api_path = '/v2/%s/os-security-groups/%s' %(self.project_id,get_group[0][3])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200 or 201
            if(rest['response'] == 202):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                self.db.pg_transaction_begin()
                #set the default security group back to NULL
                if(flag == 1):
                    update_dict = {'table':"projects",'set':"""def_security_group_id='%s',def_security_group_name='%s'""" %('NULL','NULL'),'where':"proj_id='%s'" %(self.project_id)}
                    self.db.pg_update(update_dict)
                #delete the security group from the db
                delete_dict = {"table":'trans_security_group',"where":"sec_group_id='%s'" %(get_group[0][3])}
                self.db.pg_delete(delete_dict)
            else:
                self.db.pg_transaction_rollback()
                _http_codes(rest['response'],rest['reason'])
        except Exception as e:
            self.db.pg_transaction_rollback()
            logger.sys_error("Could not remove the security group %s" %(sec_group_name))
            raise e

        return "OK"

    #DESC: Delete the specified key admins and power users can delete any key in
    #      the project they are a member of. Users can only delete the keys they own.
    #      Only an Admin can delete the default security key
    #INPUT: sec_key_name - string containing the security key name
    #OUTPUT: OK if deleted
    def delete_sec_keys(self,sec_key_name):
        #sanity
        if((not sec_key_name) or (sec_key_name == "")):
            logger.sys_error("Security key name was either blank or not specified for delete security key operation.")
            raise Exception("Security key name was either blank or not specified for delete security key operation.")

        #get the security group info from the db.
        #try:
        get_key_dict = {"select":'*',"from":'trans_security_keys',"where":"sec_key_name='%s'" %(sec_key_name),"and":"proj_id='%s'" %(self.project_id)}
        print get_key_dict
        get_key = self.db.pg_select(get_key_dict)
        print get_key
        #except:
        #    logger.sql_error("Could not get the security key info for sec_key: %s in project: %s" %(sec_key_name,self.project_id))
        #    raise Exception("Could not get the security key info for sec_key: %s in project: %s" %(sec_key_name,self.project_id))

        #if the group does not belong to the user raise exception
        if(get_key[0][1] != self.username):
            logger.sys_error("The security key %s does not belong to the user %s" %(sec_key_name,self.username))
            raise Exception("The security key %s does not belong to the user %s" %(sec_key_name,self.username))

        #if the user is and admin or power user check if the group is the default
        #if so set the flag
        flag = 0
        if((self.user_level == 0) or (self.user_level == 1)):
            check_def_dict = {"select":'def_security_key_id',"from":'projects', "where":"proj_id='%s'" %(self.project_id),"and":"def_security_key_name='%s'" %(get_key[0][3])}
            check_def = self.db.pg_select(check_def_dict)
            if(check_def):
                flag = 1

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        #create a new security group in the project
        try:
            body = ""
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'DELETE'
            api_path = '/v2/%s/os-keypairs/%s' %(self.project_id,sec_key_name)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200 or 201
            if(rest['response'] == 202):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                self.db.pg_transaction_begin()
                #set the default security group back to NULL
                if(flag == 1):
                    update_dict = {'table':"projects",'set':"""def_security_key_id='%s',def_security_key_name='%s'""" %('NULL','NULL'),'where':"proj_id='%s'" %(self.project_id)}
                    self.db.pg_update(update_dict)
                #delete the security group from the db
                delete_dict = {"table":'trans_security_keys',"where":"sec_key_id='%s'" %(get_key[0][3])}
                print delete_dict
                self.db.pg_delete(delete_dict)
            else:
                self.db.pg_transaction_rollback()
                _http_codes(rest['response'],rest['reason'])
        except Exception as e:
            self.db.pg_transaction_rollback()
            logger.sys_error("Could not remove the security key %s" %(sec_key_name))
            raise e

        return "OK"
    #DESC: list the security groups that belong to a user
    #      admins and power users can list all of the security groups.
    #INPUT: self object
    #OUTPUT: array of r_dict - sec_group_name
    #                        - sec_group_id
    #                        - owner_name
    def list_sec_group(self):
        #This only queries the transcirrus db
        #get the security group info from the db.
        get_group_dict = ""
        if((self.user_level == 0) or (self.user_level == 1)):
            get_group_dict = {"select":'*',"from":'trans_security_group',"where":"proj_id='%s'" %(self.project_id)}
        else:
            get_group_dict = {"select":'*',"from":'trans_security_group',"where":"proj_id='%s'","and":"user_name='%s'" %(self.project_id,self.username)}

        try:
            groups = self.db.pg_select(get_group_dict)
        except:
            logger.sql_error("Could not get the security group info for sec_group: %s in project: %s" %(get_group_dict[0][3],self.project_id))
            raise("Could not get the security key info for sec_key: %s in project: %s" %(get_group_dict[0][3],self.project_id))

        group_array = []
        #build an array of r_dict
        for group in groups:
            r_dict = {"sec_group_name":group[4],"sec_group_id":group[3],"username":group[2]}
            group_array.append(r_dict)
            
        #return the array
        return group_array

    #DESC: list the security keys that belong to a user
    #      admins and power users can list all of the keys.
    #INPUT: self object
    #OUTPUT: array of r_dict - key_name
    #                        - key_id - sec key fingerprint
    #                        - owner_name
    def list_sec_keys(self):
        #This only queries the transcirrus db
        #get the security group info from the db.
        get_key_dict = ""
        if((self.user_level == 0) or (self.user_level == 1)):
            get_key_dict = {"select":'*',"from":'trans_security_keys',"where":"proj_id='%s'" %(self.project_id)}
        else:
            get_key_dict = {"select":'*',"from":'trans_security_keys',"where":"proj_id='%s'","and":"user_name='%s'" %(self.project_id,self.username)}

        try:
            keys = self.db.pg_select(get_key_dict)
        except:
            logger.sql_error("Could not get the security key info for sec_key: %s in project: %s" %(get_key_dict[0][3],self.project_id))
            raise("Could not get the security key info for sec_key: %s in project: %s" %(get_key_dict[0][3],self.project_id))

        key_array = []
        #build an array of r_dict
        for key in keys:
            r_dict = {"key_name":key[3],"key_id":key[2],"username":key[1]}
            key_array.append(r_dict)

        #return the array
        return key_array

    #DESC: Get detailed info for a specific security group
    #      admins can get info on all groups in a project, users
    #      can only get info on the groups they own
    #INPUT: sec_group_name
    #OUTPUT: r_dict - sec_group_name
    #               - sec_group_id
    #               - sec_group_desc
    #               - ports - array of ports
    #NOTE: we will use a combination of the openstack and transcirrus db
    def get_sec_group(self,sec_group_name):
         #sanity
        if((not sec_group_name) or (sec_group_name == "")):
            logger.sys_error("Security group name was either blank or not specified for delete security group operation.")
            raise Exception("Security group name was either blank or not specified for delete security group operation.")

        #get the security group info from the db.
        try:
            #users can only get their own security groups
            get_group_dict = ""
            if(self.user_level != 0):
                get_group_dict = {'select':"*",'from':"trans_security_group",'where':"sec_group_name='%s'" %(str(sec_group_name)),'and':"user_name='%s'" %(self.username)}
            else:
                get_group_dict = {'select':"*",'from':"trans_security_group",'where':"sec_group_name='%s'" %(str(sec_group_name)),'and':"proj_id='%s'" %(self.project_id)}
            get_group = self.db.pg_select(get_group_dict)
        except:
            logger.sql_error("Could not get the security group info for sec_group: %s in project: %s" %(sec_group_name,self.project_id))
            raise Exception("Could not get the security group info for sec_group: %s in project: %s" %(sec_group_name,self.project_id))

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        #create a new security group in the project
        try:
            body = ""
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'GET'
            api_path = '/v2/%s/os-security-groups/%s' %(self.project_id,get_group[0][3])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200 or 201
            if(rest['response'] == 200):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                rule_array = []
                for rule in load['security_group']['rules']:
                    rule_dict = {'from_port': str(rule['from_port']), 'to_port':str(rule['to_port']), 'cidr':str(rule['ip_range']['cidr'])}
                    rule_array.append(rule_dict)
                r_dict = {'sec_group_name':sec_group_name, 'sec_group_id': get_group[0][3], 'sec_group_desc':str(load['security_group']['description']),'ports':rule_array}
                return r_dict
            else:
                _http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not remove the security group %s" %(sec_group_name))
            raise e

    #DESC: Get detailed info for a specific security key
    #      admins can get info on all keys in the project,
    #      users can only get info on the keys they own admins 
    #INPUT: sec_key_name
    #OUTPUT: r_dict - sec_key_name
    #               - sec_key_id
    #               - rsa_public_key
    def get_sec_keys(self,sec_key_name):
         #sanity
        if((not sec_key_name) or (sec_key_name == "")):
            logger.sys_error("Security key name was either blank or not specified for get security key operation.")
            raise Exception("Security key name was either blank or not specified for get security key operation.")

        #get the security group info from the db.
        try:
            #users can only get their own security groups
            get_key_dict = ""
            if(self.user_level != 0):
                get_key_dict = {'select':"sec_key_name,sec_key_id,public_key",'from':"trans_security_keys",'where':"proj_id='%s'" %(self.project_id),'and':"user_name='%s'" %(self.username)}
            else:
                get_key_dict = {'select':"sec_key_name,sec_key_id,public_key",'from':"trans_security_keys",'where':"proj_id='%s'" %(self.project_id)}
            get_key = self.db.pg_select(get_key_dict)
        except:
            logger.sql_error("Could not get the security group info for sec_group: %s in project: %s" %(sec_group_name,self.project_id))
            raise Exception("Could not get the security group info for sec_group: %s in project: %s" %(sec_group_name,self.project_id))

        r_dict = {'sec_key_name':get_key[0][0],'sec_key_id':get_key[0][1],'public_key':get_key[0][2]}
        return r_dict

######Internal defs#######
def _http_codes(code,reason):
    if(code):
        logger.sys_error("Response %s with Reason %s" %(code,reason))
        raise Exception("Response %s with Reason %s" %(code,reason))
    else:
        logger.sys_error("Error for unknown reason.")
        raise Exception("Error for unknown reason.")
