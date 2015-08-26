import subprocess
import transcirrus.common.logger as logger


def remove_shib():
    """
    DESC:   uninstall shibboleth and remove all components
    INPUT:  none
    OUTPUT: 'OK' if task completed successfully, else 'ERROR'
    ACCESS: admins only
    NOTE:
    """
    try:
        # uninstall shibboleth
        subprocess.call(["sudo", "yum", "-y", "remove", "shibboleth"])
        subprocess.call(["sudo", "rm", "-rf", "/etc/shibboleth/"])

        # stop httpd
        subprocess.call(["sudo", "service", "httpd", "stop"])

        conf = open("/etc/httpd/conf/httpd.conf").read()

        # finds shibboleth part
        shib = conf.find(("<Location /Shibboleth.sso>\n"
                           "    SetHandler shib\n"
                           "</Location>\n"
                           "\n"
                           "<Location /shib>\n"
                           "    AuthType shibboleth\n"
                           "    ShibRequestSetting requireSession 1\n"
                           "    Require valid-user\n"
                           "</Location>\n"))


        # sets text as everything except shibboleth part
        text = conf[:shib] + conf[shib+len(("<Location /Shibboleth.sso>\n"
                                            "    SetHandler shib\n"
                                            "</Location>\n"
                                            "\n"
                                            "<Location /shib>\n"
                                            "    AuthType shibboleth\n"
                                            "    ShibRequestSetting requireSession 1\n"
                                            "    Require valid-user\n"
                                            "</Location>\n")):]

        # rewrites httpd.conf
        out = open("/etc/httpd/conf/httpd.conf", 'w')
        out.write(text)
        out.close()

        # start httpd
        subprocess.call(["sudo", "service", "httpd", "start"])
        return 'OK'
    except Exception as e:
        logger.sys_error("SHIB: could not remove shibboleth from cloud, error: %s" %(str(e)))
        raise Exception("Could not remove shibboleth from cloud, error: %s" %(str(e)))
