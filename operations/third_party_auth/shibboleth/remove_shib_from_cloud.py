import subprocess
import transcirrus.common.logger as logger
import transcirrus.operations.third_party_auth.util as auth_util
from multiprocessing import Process


def remove_shib():
    """
    DESC:   uninstall shibboleth and remove all components
    INPUT:  none
    OUTPUT: 'OK' if task completed successfully, else 'ERROR'
    ACCESS: admins only
    NOTE:
    """
    # check to see if shibboleth is already installed
    protocols = auth_util.detect_auth()
    if protocols['has_shib'] == True:
        logger.sys_info("remove shib from cloud, shibboleth is installed, ok to remove")

        # uninstall shibboleth
        try:
            subprocess.call(["sudo", "service", "shibd", "stop"])
            rpm = subprocess.call(["sudo", "rpm", "-e", "--noscripts", "shibboleth-2.5.5-3.1.x86_64"])
            subprocess.call(["sudo", "rm", "-rf", "/etc/shibboleth/"])
            subprocess.call(["sudo", "rm", "-f", "/etc/yum.repos.d/security:shibboleth.repo"])
            subprocess.call(["sudo", "rm", "-rf", "/usr/lib64/shibboleth"])
            subprocess.call(["sudo", "rm", "-f", "/etc/httpd/conf.d/shib.conf"])
            logger.sys_info("remove shib from cloud, yum remove, %s" %(str(rpm)))
        except Exception as e:
            logger.sys_error("SHIB: remove shib error, yum section: %s" % str(e))
            raise Exception("Could not remove shibboleth, error: %s" %(str(e)))

        # modify apache's httpd.conf, removing shibboleth wrapper
        try:
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
            logger.sys_info("remove shib from cloud, rewrote httpd.conf")
        except Exception as e:
            logger.sys_error("SHIB: remove shib error, httpd.conf section: %s" % str(e))
            raise Exception("Could not remove shibboleth, error: %s" %(str(e)))

        # reload httpd
        try:
            logger.sys_info("remove shib from cloud, begin reload httpd")
            p = Process(target=auth_util.reload_apache)
            p.start()
            logger.sys_info("remove shib from cloud, end reload httpd, process launched")

        except Exception as e:
            logger.sys_error("SHIB: remove shib error, httpd section: %s" % str(e))
            raise Exception("Could not remove shibboleth, error: %s" %(str(e)))

        logger.sys_info("remove shib from cloud, return OK")
        return 'OK'

    else:
        # shibboleth not installed
        logger.sys_info("remove shib from cloud, shibboleth not installed")
        raise Exception("Shibboleth not installed.")
