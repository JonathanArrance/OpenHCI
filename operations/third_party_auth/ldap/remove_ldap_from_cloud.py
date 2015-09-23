import os
import transcirrus.common.logger as logger
import transcirrus.operations.third_party_auth.util as auth_util


def remove_ldap():
    """
    DESC:   remove ldap_config.py
    INPUT:  none
    OUTPUT: 'OK' if task completed successfully, else 'ERROR'
    ACCESS: admins only
    NOTE:
    """
    # check to see if ldap is already configured
    protocols = auth_util.detect_auth()
    if protocols['has_ldap'] == True:
        logger.sys_info("remove ldap from cloud, ldap is configured, ok to remove")
        
        # remove ldap_config.py
        try:
            removed = os.remove("/usr/local/lib/python2.7/transcirrus/operations/third_party_auth/ldap/ldap_config.py")
            if removed is None:
                return 'OK'
        except Exception as e:
            # problem removing ldap_config.py
            logger.sys_error("remove ldap from cloud, error: %s" %e)
            raise Exception("Could not remove ldap, error: %s" %e)

    else:
        # ldap not configured
        logger.sys_info("remove ldap from cloud, ldap not installed")
        raise Exception("LDAP not configured, cannot remove.")