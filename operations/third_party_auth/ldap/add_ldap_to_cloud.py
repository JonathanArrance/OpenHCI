import transcirrus.common.logger as logger
import transcirrus.operations.third_party_auth.util as auth_util


def add_ldap(input_dict, manager_dict=None):
    """
    DESC:   configure ldap for system
    INPUT:  input_dict: {
                            hostname        - url of ldap server - ex: "ldap.transcirrus.com" or "192.168.2.148"
                            use_ssl         - boolean - True means port 389 will be used, False means port 636
                            base_dn         - base distinguished name - ex: "dc=transcirrus,dc=com"
                            uid_attr        - user name attribute - ex: "uid" (attribute for <first_letter><last_name>)
                        }
            manager_dict:   {               - op - manager account used for binding, if None, binding will be anonymous
                                manager_dn  - manager distinguished name - ex: "cn=Manager,dc=transcirrus,dc=com"
                                manager_pw  - manager password
                            }
    OUTPUT: 'OK' if task completed successfully, else 'ERROR'
    ACCESS: admins only
    NOTE:   
    """
    # check to see if ldap is already configured
    protocols = auth_util.detect_auth()
    if protocols['has_ldap'] == True:
        logger.sys_error("ldap already configured.")
        # ldap already configured
        raise Exception("LDAP is already configured.")

    # determine binding
    if manager_dict is None:
        manager_dict = {}
        manager_dict['manager_dn'] = "ANONYMOUS"
        manager_dict['manager_pw'] = "ANONYMOUS"

    # write ldap_config.py
    with open("/usr/local/lib/python2.7/transcirrus/operations/third_party_auth/ldap/ldap_config.py","a+") as ldap_config:
        ldap_config.write((
                            "HOSTNAME=\"%s\"\n"
                            "USE_SSL=\"%s\"\n"
                            "BASE_DN=\"%s\"\n"
                            "UID_ATTR=\"%s\"\n"
                            "MANAGER_DN=\"%s\"\n"
                            "MANAGER_PW=\"%s\"\n"
                            %(input_dict['hostname'], input_dict['use_ssl'], input_dict['base_dn'], input_dict['uid_attr'], manager_dict['manager_dn'], manager_dict['manager_pw'])
                        ))
    return 'OK'