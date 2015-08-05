import subprocess
import xml.etree.ElementTree as etree
import transcirrus.common.util as util


def add_centos6_shib(input_dict):
    """
    DESC:   install and configure shibboleth for a centos6.x system
    INPUT:  input_dict: {
                            sso_entity_id           - url of idp - ex: "https://idp.testshib.org/idp/shibboleth"
                            mp_backing_file_path    - MetadataProvider backingFilePath - ex: "testshib-two-idp-metadata.xml"
                            mp_uri                  - MetadataProvider uri - ex: "http://www.testshib.org/metadata/testshib-providers.xml"
                        }
    OUTPUT: 'OK' if task completed successfully
    ACCESS: admins only
    NOTE:   admin must upload metadata to idp after this
            metadata can be found at https://<uplink_ip>/Shibboleth.sso/Metadata
    """
    # get distro and version
    issue = subprocess.check_output(["cat", "/etc/issue"])
    issue_parts = issue.split()

    # make sure this is centos6.x, add shibboleth repo and yum install shibboleth
    if issue_parts[0] == "CentOS" and issue_parts[2][0].startswith('6'):
        try:
            subprocess.call(["sudo", "wget", "http://download.opensuse.org/repositories/security://shibboleth/CentOS_CentOS-6/security:shibboleth.repo",  "-P", "/etc/yum.repos.d"])
            subprocess.call(["sudo", "yum", "-y", "install", "shibboleth.x86_64"])
        except Exception as e:
            print "ERROR: " + str(e)

        # modify shibboleth config, updating:
        #   * ApplicationDefaults entityID  ->  uplink_ip
        #   * SSO entityID                  ->  input_dict['sso_entity_id']
        # and adding:
        #   * MetadataProvider              ->  input_dict['mp_backing_file_path'], input_dict['mp_uri']
        try:
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
        except Exception as e:
            print "ERROR: " + str(e)

        # sync time settings to avoid shibboleth timing errors, restart shibd after modifying config,
        # and stop httpd before modifying config
        try:
            subprocess.call(["sudo","service", "ntpd", "stop"])
            subprocess.call(["sudo","ntpdate", "pool.ntp.org"])
            subprocess.call(["sudo","service", "ntpd", "start"])
            subprocess.call(["sudo", "service", "shibd", "start"])
            subprocess.call(["sudo", "service", "httpd", "stop"])
        except Exception as e:
            print "ERROR: " + str(e)

        # modify apache's httpd.conf, adding shibboleth wrapper
        try:
            with open("/etc/httpd/conf/httpd.conf", "a") as httpd_conf:
                httpd_conf.write("<Location /Shibboleth.sso>\n \
                                    SetHandler shib\n \
                                  </Location>\n \
                                  \n \
                                  <Location />\n \
                                    AuthType shibboleth\n \
                                    ShibRequestSetting requireSession 1\n \
                                    Require valid-user\n \
                                  </Location>")
        except Exception as e:
            print "ERROR: " + str(e)


        # restart httpd and reset rabbitmq (behaves strangely after shibboleth install) after modifying config
        try:
            subprocess.call(["sudo", "service", "httpd", "start"])
            """
            subprocess.call(["sudo", "rabbitmqctl", "change_password", "guest", "transcirrus1"])
            subprocess.call(["sudo", "service", "rabbitmq-server", "restart"])
            subprocess.call(["sudo", "service", "neutron-server", "restart"])
            """
        except Exception as e:
            print "ERROR: " + str(e)

    return 'OK'