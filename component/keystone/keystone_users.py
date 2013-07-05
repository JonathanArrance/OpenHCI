#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys

sys.path.append('../../common')
import logger
import config

from api_caller import caller

sys.path.append('%s') %(config.DB_PATH)
from postgres import pgsql

class tokens:
    
    #DESC: Constructor to build out the tokens object
    #INPUT: auth_dict dictionary containing
    #           username
    #           password
    #           project_id - could be blank
    def __init__(self,auth_dict):
        if(not auth_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        else:
            self.username = auth_dict['username']
            self.password = auth_dict['password']
            self.project_id = auth_dict['project_id']
        
        if((self.username == "")or(self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")
        
    def create_user():
        
    def remove_user():
        
    def create_user_role():
        
    def remove_user_role():
        
    def update_user():
        
    def update_user_role():
        
    def list_user_tenants():
        
    def list_user_roles():
        
    def add_role_to_user():
        
    def remove_role_from_user():
        
    def get_user_credentials():
        
    def update_user_credentials():
        
    def remove_user_credentials():