import os.path, time, subprocess
import transcirrus.common.logger as logger


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
    has_ldap = os.path.isfile("/usr/local/lib/python2.7/transcirrus/operations/third_party_auth/ldap/ldap_config.py")

    # check other
    has_other = False

    r_dict = {'has_shib': has_shib, 'has_ldap': has_ldap, 'has_other': has_other}
    return r_dict


def reload_apache():
    time.sleep(5)
    subprocess.call(["sudo", "/etc/init.d/httpd", "reload"])
