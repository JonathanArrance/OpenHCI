import transcirrus.common.util as util
import transcirrus.common.extras as extras
import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.operations.third_party_auth.shibboleth.build_shib_project as bsp

from transcirrus.database.postgres import pgsql
from transcirrus.component.keystone.keystone_users import user_ops


def add_user(input_dict):
    """
    DESC:   add a shibboleth user to transcirrus/openstack, either adding to default project or building a new one
    INPUT:  input_dict: {
                            username    -   req
                            email       -   req
                            project_id  -   op, provide project_id of default project, else new project will be created
                        }
    OUTPUT: user_dict:  {
                            username
                            user_id
                            project_id
                        }
    ACCESS:
    NOTE:   this automatically generates everything for the new user/project including passwords which are encrypted
            using AES and stored in the trans_user_info db
    """
    username = input_dict['username']
    # generate password
    pwd = extras.make_password()
    # encrypt password
    cipher = extras.encrypt(pwd)
    shadow_auth = extras.shadow_auth()
    uo = user_ops(shadow_auth)

    user_dict = {
                    'username': input_dict['username'],
                    'password': pwd,
                    'email':    input_dict['email']
                }
    # if project_id in input_dict, add user to provided default project
    if 'project_id' in input_dict:
        user_dict['user_role'] = 'user'
        user_dict['project_id'] = input_dict['project_id']
        # create user and add to project
        try:
            user = uo.create_user(user_dict)
        except Exception as e:
            logger.sys_error("add shib user error, add to project section: %s" % str(e))
            raise e
    # else build an entire project for user
    else:
        user_dict['user_role'] = 'admin'
        # get uplink dns and set as subnet_dns for project
        node_id = util.get_node_id()
        sys_vars = util.get_system_variables(node_id)
        subnet_array = []
        subnet_array.append(sys_vars['UPLINK_DNS'])
        project_dict = {
                            'project_name':     username + "_project",
                            'user_dict':        user_dict,
                            'net_name':         username + "_network",
                            'subnet_dns':       subnet_array,
                            'sec_group_dict':   {
                                                    'ports':        '',
                                                    'group_name':   username + "_security_group",
                                                    'group_desc':   username + "_security_group",
                                                    'project_id':   ''
                                                },
                            'sec_keys_name':    username + "_security_keys",
                            'router_name':      username + "_router"
                       }
        # create project and user
        try:
            proj, user = bsp.build_project(shadow_auth, project_dict)
            user['project_id'] = proj
        except Exception as e:
            logger.sys_error("add shib user error, build project section: %s" % str(e))
            raise e

    # instantiate db
    db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
    try:
        db.pg_transaction_begin()
        # add encrypted password to db
        update_dict = {'table':"trans_user_info",'set':"encrypted_password='%s'" %(cipher),'where':"keystone_user_uuid='%s'" %(user['user_id'])}
        db.pg_update(update_dict)
    except Exception as e:
        db.pg_transaction_rollback()
        db.pg_close_connection()
        logger.sql_error("%s"%(e))
        raise e
    else:
        db.pg_transaction_commit()
        db.pg_close_connection()

    return user