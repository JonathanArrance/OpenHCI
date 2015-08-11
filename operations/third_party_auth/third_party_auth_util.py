import os.path


def detect_auth():
    """
    DESC:   determine third party authentication protocols
    INPUT:  none
    OUTPUT: r_dict: {
                        has_shib    -   boolean, True if shibboleth exists, else False
                        has_ldap    -   boolean, True is LDAP exists, else False
                        has_other   -   boolean, place-holder
                    }
    ACCESS: wide open
    NOTE:
    """
    # check shib
    has_shib = os.path.exists("/etc/shibboleth")

    # check LDAP
    has_ldap = False

    # check other
    has_other = False

    r_dict = {'has_shib': has_shib, 'has_ldap': has_ldap, 'has_other': has_other}
    return r_dict