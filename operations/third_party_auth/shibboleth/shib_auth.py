import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common import extras as extras
from transcirrus.common.auth import authorization
from transcirrus.database.postgres import pgsql


class shibboleth_authorization:
    """
    DESC:   initialize the connection to the DB and set the username
    INPUT:  username
    OUTPUT: none
    ACCESS:
    NOTE:
    """
    def __init__(self,username):
        reload(config)
        # setting username in logger dict
        logger.sys_info ("Setting username in logger to %s" % username)
        logger.SetUserDict (username, "0")

        # connect to the transcirrus and keystone databases
        try:
            # transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
            # keystone db
            self.key = pgsql(config.OS_DB,config.OS_DB_PORT,"keystone",config.OS_DB_USER,config.OS_DB_PASS)
        except StandardError as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        # assign the username
        self.username = username


    def get_auth(self):
        """
        DESC:   get all authorization information for the user
        INPUT:  none
        OUTPUT: auth_dict:  {
                                username
                                status_level    -   0 = not enabled, 1 = transcirrus only, 2 = transcirrus and keystone (mostly don't worry about this)
                                token
                                project_id
                                user_id
                                is_admin        -   0 = not admin, 1 = is admin
                                user_level      -   0 = admin, 1 = power user, 2 = user
                                password
                                db_object
                                adm_token       -   "" if not admin, otherwise some token
                            }
        ACCESS: wide open, but with great power comes great responsibility
        NOTE:
        """
        # get encrypted password, decrypt and authenticate
        try:
            get_pass = {'select':'encrypted_password','from':'trans_user_info','where':"user_name='%s'"%(self.username)}
            cipher = self.db.pg_select(get_pass)
            plaintext = extras.decrypt(cipher[0][0])
            a = authorization(self.username, plaintext)
            auth = a.get_auth()
            return auth
        except Exception as e:
            logger.sys_error("Error during authentication of shibboleth user, %s." %(str(e)))
            raise Exception("Error during authentication of shibboleth user, %s." %(str(e)))