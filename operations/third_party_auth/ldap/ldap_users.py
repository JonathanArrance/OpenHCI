import ldap
import transcirrus.common.logger as logger
from transcirrus.operations.third_party_auth.ldap import ldap_config


def validate_user(username, password):
    """
    DESC:   validate ldap user credentials
    INPUT:  username    - ldap username - ex: nbrust
            password    - ldap password
    OUTPUT: 'OK' if task completed successfully, else 'ERROR'
    ACCESS: 
    NOTE:
    """
    # initialize, check ssl usage and bind
    l = ldap.initialize(ldap_config.HOSTNAME)
    if ldap_config.USE_SSL == "True":
        l.start_tls_s()
    if ldap_config.MANAGER_DN == "ANONYMOUS":
        # bind anonymously
        l.simple_bind_s("","")
    else:
        # bind as manager
        l.simple_bind_s( ldap_config.MANAGER_DN, ldap_config.MANAGER_PW )

    # search for user dn based on uid
    uid = '(%s=%s)' %(ldap_config.UID_ATTR,username)
    attrs = []
    search = l.search_s( ldap_config.BASE_DN, ldap.SCOPE_SUBTREE, uid, attrs )

    # make sure user exists
    if len(search) != 0:
        user_dn = search[0][0]
        user_pw = password
        success = (-1,-1)
        try: 
            success = l.simple_bind_s(user_dn, user_pw)
        # invalid credentials
        except ldap.INVALID_CREDENTIALS:
            logger.sys_error("ldap username or password is incorrect")
            raise Exception("LDAP username or password is incorrect.")
        # other ldap error
        except ldap.LDAPError, e:
            if type(e.message) == dict and e.message.has_key('desc'):
                logger.sys_error("LDAP error: %s" %(e.message['desc']))
                raise Exception("LDAP error: %s" %(e.message['desc']))
            else: 
                logger.sys_error("LDAP error: %s" %(e))
                raise Exception("LDAP error: %s" %(e))
        if success[0] == 97:
            return 'OK'
        return 'ERROR'

    # user does not exist
    else:
        logger.sys_error("ldap user %s not found" %username)
        raise Exception("LDAP user %s not found." %username)


def generate_email(username):
    """
    DESC:   best effort to try to guess ldap user email based on BASE_DN, if not possible default to username@transcirrus.com
    INPUT:  username    - ldap username     - ex: nbrust
    OUTPUT: email       - in the form of:   username@<base_dn_first_part>.<base_dn_second_part>
                                            - OR -
                                            usernaem@transcirrus.com 
    ACCESS: 
    NOTE:
    """
    base_dn_parts = ldap_config.BASE_DN.split(",")
    dc_parts = []
    for part in base_dn_parts:
        if part.startswith("dc="):
            dc_parts.append(part[3:])
    if len(dc_parts) == 2:
        return username+"@"+dc_parts[0]+"."+dc_parts[1]
    else:
        return username+"@transcirrus.com"