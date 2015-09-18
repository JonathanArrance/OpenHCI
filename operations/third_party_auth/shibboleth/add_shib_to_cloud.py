import subprocess
import xml.etree.ElementTree as etree
import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.operations.third_party_auth.util as auth_util
from multiprocessing import Process

def add_centos6_shib(input_dict):
    """
    DESC:   install and configure shibboleth for a centos6.x system
    INPUT:  input_dict: {
                            sso_entity_id           - url of idp - ex: "https://idp.testshib.org/idp/shibboleth"
                            mp_backing_file_path    - MetadataProvider backingFilePath - ex: "testshib-two-idp-metadata.xml"
                            mp_uri                  - MetadataProvider uri - ex: "http://www.testshib.org/metadata/testshib-providers.xml"
                        }
    OUTPUT: 'OK' if task completed successfully, else 'ERROR'
    ACCESS: admins only
    NOTE:   admin must upload metadata to idp after this
            metadata can be found at https://<uplink_ip>/Shibboleth.sso/Metadata
    """
    # check to see if shibboleth is already installed
    protocols = auth_util.detect_auth()
    if protocols['has_shib'] == True:
        logger.sys_error("shibboleth already installed.")
        # shibboleth already installed
        raise Exception("Shibboleth is already installed.")

    # get distro and version
    issue = subprocess.check_output(["cat", "/etc/issue"])
    issue_parts = issue.split()

    # make sure this is centos6.x, add shibboleth repo and yum install shibboleth
    if issue_parts[0] == "CentOS" and issue_parts[2][0].startswith('6'):
        try:
            subprocess.call(["sudo", "wget", "http://download.opensuse.org/repositories/security://shibboleth/CentOS_CentOS-6/security:shibboleth.repo",  "-P", "/etc/yum.repos.d"])
            yum = subprocess.call(["sudo", "yum", "-y", "install", "shibboleth.x86_64"])
            if yum != 0:
                yum = subprocess.call(["sudo", "yum", "-y", "install", "/usr/local/lib/python2.7/transcirrus/upgrade_resources/shibboleth-2.5.5-3.1.x86_64.rpm"])
            logger.sys_info("add shib to cloud, yum install, %s" %(str(yum)))
        except Exception as e:
            logger.sys_error("SHIB: add shib error, wget section: %s" % str(e))
            raise Exception("Could not add shibboleth, error: %s" %(str(e)))

        # modify shibboleth config, updating:
        #   * ApplicationDefaults entityID  ->  uplink_ip
        #   * SSO entityID                  ->  input_dict['sso_entity_id']
        # and adding:
        #   * MetadataProvider              ->  input_dict['mp_backing_file_path'], input_dict['mp_uri']
        try:
            subprocess.call(["sudo", "chmod", "777", "/etc/shibboleth/shibboleth2.xml"])
            shib_tree = etree.parse('/etc/shibboleth/shibboleth2.xml')
            shib_root = shib_tree.getroot()
            for app_def in shib_root.findall("{urn:mace:shibboleth:2.0:native:sp:config}ApplicationDefaults"):
                for session in app_def.findall("{urn:mace:shibboleth:2.0:native:sp:config}Sessions"):
                    for sso in session.findall("{urn:mace:shibboleth:2.0:native:sp:config}SSO"):
                        sso.set("entityID", input_dict['sso_entity_id'])
                app_def.set("entityID", "https://%s/shibboleth" %(util.get_cloud_controller_uplink_ip()))
                meta_prov = etree.SubElement(app_def,"ns0:MetadataProvider")
                meta_prov.set("backingFilePath", input_dict['mp_backing_file_path'])
                meta_prov.set("reloadInterval", "180000")
                meta_prov.set("type", "XML")
                meta_prov.set("uri", input_dict['mp_uri'])
            shib_tree.write('/etc/shibboleth/shibboleth2.xml')
            logger.sys_info("add shib to cloud, write shibboleth2.xml")
        except Exception as e:
            logger.sys_error("SHIB: add shib error, etree section: %s" % str(e))
            raise Exception("Could not add shibboleth, error: %s" %(str(e)))

        # sync time settings to avoid shibboleth timing errors, restart shibd after modifying config
        try:
            subprocess.call(["sudo","service", "ntpd", "stop"])
            subprocess.call(["sudo","ntpdate", "pool.ntp.org"])
            subprocess.call(["sudo","service", "ntpd", "start"])
            subprocess.call(["sudo", "service", "shibd", "start"])
            logger.sys_info("add shib to cloud, ntpd updated")
        except Exception as e:
            logger.sys_error("SHIB: add shib error, service section: %s" % str(e))
            raise Exception("Could not add shibboleth, error: %s" %(str(e)))

        # modify apache's httpd.conf, adding shibboleth wrapper
        try:
            subprocess.call(["sudo", "chmod", "777", "/etc/httpd/conf/httpd.conf"])
            with open("/etc/httpd/conf/httpd.conf", "a") as httpd_conf:
                httpd_conf.write(("<Location /Shibboleth.sso>\n"
                                  "    SetHandler shib\n"
                                  "</Location>\n"
                                  "\n"
                                  "<Location /shib>\n"
                                  "    AuthType shibboleth\n"
                                  "    ShibRequestSetting requireSession 1\n"
                                  "    Require valid-user\n"
                                  "</Location>\n"))
            logger.sys_info("add shib to cloud, write httpd.conf")
        except Exception as e:
            logger.sys_error("SHIB: add shib error, xml section: %s" % str(e))
            raise Exception("Could not add shibboleth, error: %s" %(str(e)))


        # reload httpd
        try:
            logger.sys_info("add shib to cloud, begin reload httpd")
            p = Process(target=auth_util.reload_apache)
            p.start()
            logger.sys_info("add shib to cloud, end reload httpd, process launched")
            
        except Exception as e:
            logger.sys_error("SHIB: add shib error, httpd section: %s" % str(e))
            raise Exception("Could not add shibboleth, error: %s" %(str(e)))

        logger.sys_info("add shib to cloud, return OK")
        return 'OK'

    # this means not centos6.x
    return 'ERROR'
