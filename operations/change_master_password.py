#get the libs needed
#from celery import Celery
#from celery import task
from transcirrus.component.keystone.keystone_users import user_ops
import os,sys
import subprocess
import transcirrus.common.config as config
import transcirrus.common.logger as logger
import transcirrus.common.util as util
import transcirrus.database.node_db as node_db
import transcirrus.common.service_control as sc

#@celery.task(name='change_admin_password')
def change_master_password(new_password):
    #change the linux password
    os.system('echo \''+new_password+'\n'+new_password+'\n\' | sudo passwd root')
    logger.sys_info("Password for root user successfully changed.")
    os.system('echo \''+new_password+'\n'+new_password+'\n\' | sudo passwd transuser')
    logger.sys_info("Password for transuser successfully changed.")

    update_array= []
    write_creds = os.system("""sudo sed -i 's/MASTER_PWD=.*/MASTER_PWD="%s"/g' /usr/local/lib/python2.7/transcirrus/common/config.py"""%(new_password))
    if(write_creds != 0):
        logger.sys_warning('Could not write the config.py and update the master password.')
    else:
        update_array.append({'system_name':config.NODE_NAME,'parameter':'master_pwd','param_value':new_password})

    rabbit = os.system("""sudo rabbitmqctl change_password guest %s"""%(new_password))
    if(rabbit != 0):
        logger.sys_warning('Could not write the config.py and update the master password.')

    if(config.NODE_TYPE == 'cc' or config.NODE_TYPE == 'ha'):
        if(config.NODE_TYPE == 'ha'):
            ip = config.TRANSCIRRUS_DB
        else:
            ip = 'localhost'
        #glance
        write_glance_api = os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/glance/g' /etc/glance/glance-api.conf"""%(new_password,ip))
        if(write_glance_api != 0):
            logger.sys_warning('Could not write the glance-api.conf and update the master password.')
        write_glance_reg = os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/glance/g' /etc/glance/glance-registry.conf"""%(new_password,ip))
        if(write_glance_reg != 0):
            logger.sys_warning('Could not write the glance-registry.conf and update the master password.')
        write_glance_rabbit = os.system("""sudo sed -i 's/rabbit_password=.*/rabbit_password=%s/g' /etc/glance/glance-api.conf"""%(new_password))
        if(write_glance_rabbit!= 0):
            logger.sys_warning('Could not write the glance-api.conf rabbit master password.')
        #heat
        write_heat = os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/heat/g' /etc/heat/heat.conf"""%(new_password,ip))
        if(write_heat != 0):
            logger.sys_warning('Could not write the heat.conf and update the master password.')
        write_heat_rabbit = os.system("""sudo sed -i 's/rabbit_password=.*/rabbit_password=%s/g' /etc/heat/heat.conf"""%(new_password))
        if(write_heat_rabbit != 0):
            logger.sys_warning('Could not write the heat.conf and update the rabbit master password.')
        #keystone
        write_keystone = os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/keystone/g' /etc/keystone/keystone.conf"""%(new_password,ip))
        if(write_keystone != 0):
            logger.sys_warning('Could not write the keystone.conf and update the master password.')
        #mongo
        write_mongo = os.system("""sudo sed -i 's/db.changeUserPassword.*/db.changeUserPassword("ceilometer", "%s")/g' /transcirrus/update_mongo_pwd.js"""%(new_password))
        if(write_mongo != 0):
            logger.sys_warning('Could not write the keystone.conf and update the master password.')
        else:
            run_mongo = os.system("""sudo mongo --host 172.24.24.10 ceilometer /transcirrus/update_mongo_pwd.js""")
            if(run_mongo != 0):
                logger.sys_warning('Could not update the mongo master password.')
        #pqsql
        write_pgsql = os.system('psql -U postgres -c "ALTER USER transuser WITH PASSWORD '"'%s'"';"'%(new_password))
        if(write_pgsql != 0):
            logger.sys_warning('Could not update the pgsql password.')
        else:
            update_array.append({'system_name':config.NODE_NAME,'parameter':'tran_db_pass','param_value':new_password})
            update_array.append({'system_name':config.NODE_NAME,'parameter':'os_db_pass','param_value':new_password})
            write_tranDB = os.system("""sudo sed -i 's/TRAN_DB_PASS=.*/TRAN_DB_PASS="'"%s"'"/g' /usr/local/lib/python2.7/transcirrus/common/config.py"""%(new_password))
            if(write_tranDB != 0):
                logger.sys_warning('Could not write the TRAN_DB_PASS and update the master password.')
            write_osDB = os.system("""sudo sed -i 's/OS_DB_PASS=.*/OS_DB_PASS="'"%s"'"/g' /usr/local/lib/python2.7/transcirrus/common/config.py"""%(new_password))
            if(write_osDB != 0):
                logger.sys_warning('Could not write the OS_DB_PASS and update the master password.')
            #os.system('sudo rm /usr/local/lib/python2.7/transcirrus/common/config.pyc')
            reload(config)
        #apersona
        write_apersona = os.system("""sudo sed -i 's/db.password=.*/db.password=%s/g' /var/lib/tomcat6/webapps/apkv/WEB-INF/classes/apersona-db.properties"""%(new_password))
        if(write_apersona != 0):
            logger.sys_warning('Could not update the apersona password.')
        write_apersona2 = os.system("""sudo sed -i 's/db.password=.*/db.password=%s/g' /var/lib/tomcat6/webapps/api_portal/WEB-INF/classes/apersona-db.properties"""%(new_password))
        if(write_apersona2 != 0):
            logger.sys_warning('Could not update the apersona password.')
        #support
        write_support = os.system("""sudo sed -i 's/pgsql.password=.*/pgsql.password='%s'/g' /usr/local/lib/python2.7/transcirrus/operations/support-collect.sh"""%(new_password))
        if(write_support != 0):
            logger.sys_warning('Could not update the support password.')

    if(config.NODE_TYPE == 'cc' or config.NODE_TYPE == 'cn' or config.NODE_TYPE == 'ha'):
        if(config.NODE_TYPE == 'cn' or config.NODE_TYPE == 'ha'):
            ip = config.TRANSCIRRUS_DB
        else:
            ip = 'localhost'
        #nova
        write_nova = os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/nova/g' /etc/nova/nova.conf"""%(new_password,ip))
        if(write_nova != 0):
            logger.sys_warning('Could not write the nova.conf and update the master password.')
        write_nova_rabbit = os.system("""sudo sed -i 's/rabbit_password=.*/rabbit_password=%s/g' /etc/nova/nova.conf"""%(new_password))
        if(write_nova_rabbit != 0):
            logger.sys_warning('Could not write the nova.conf and update the rabbit master password.')
        #ceilometer
        write_ceilometer = os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/ceilometer/g' /etc/ceilometer/ceilometer.conf"""%(new_password,ip))
        if(write_ceilometer != 0):
            logger.sys_warning('Could not write the ceilometer.conf and update the master password.')
        write_ceilometer_rabbit = os.system("""sudo sed -i 's/rabbit_password=.*/rabbit_password=%s/g' /etc/ceilometer/ceilometer.conf"""%(new_password))
        if(write_ceilometer_rabbit != 0):
            logger.sys_warning('Could not write the nova.conf and update the rabbit master password.')
        #neutron
        write_neutron = os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/neutron/g' /etc/neutron/neutron.conf"""%(new_password,ip))
        if(write_neutron != 0):
            logger.sys_warning('Could not write the neutron.conf and update the master password.')
        write_neutron_rabbit = os.system("""sudo sed -i 's/rabbit_password=.*/rabbit_password=%s/g' /etc/neutron/neutron.conf"""%(new_password))
        if(write_neutron_rabbit != 0):
            logger.sys_warning('Could not write the neutron.conf and update the rabbit master password.')

    if(config.NODE_TYPE == 'cc' or config.NODE_TYPE == 'sn' or config.NODE_TYPE == 'ha'):
        if(config.NODE_TYPE == 'sn' or config.NODE_TYPE == 'ha'):
            ip = config.TRANSCIRRUS_DB
        else:
            ip = 'localhost'
        #cinder
        write_cinder = os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/cinder/g' /etc/cinder/cinder.conf"""%(new_password,ip))
        if(write_cinder != 0):
            logger.sys_warning('Could not write the cinder.conf and update the master password.')
        write_cinder_rabbit = os.system("""sudo sed -i 's/rabbit_password=.*/rabbit_password=%s/g' /etc/cinder/cinder.conf"""%(new_password))
        if(write_cinder_rabbit != 0):
            logger.sys_warning('Could not write the cinder.conf and update the rabbit master password.')

    #update the DB entries with the new passwords
    util.update_system_variables(update_array)
    #update the node master pass
    node_db.update_node_master_pass(new_password)

    #restart the openstack services
    logger.sys_info("Restarting all OpenStack Services.")
    if(config.NODE_TYPE == 'cc' or config.NODE_TYPE == 'ha'):
        #restart pgsql
        try:
            sc.postgresql('restart')
            logger.sys_info('Postgres restarted.')
        except Exception as e:
            logger.sys_error('Could not restart postgres db %s.'%(e))

        #restart mongo
        try:
            sc.mongo('restart')
            logger.sys_info('Mongo restarted.')
        except Exception as e:
            logger.sys_error('Could not restart mongo db %s.'%(e))

        #rabbit
        try:
            sc.rabbit('restart')
            logger.sys_info('Rabbit MQ restarted.')
        except Exception as e:
            logger.sys_error('Could not restart rabbit mq %s.'%(e))

        try:
            sc.tomcat('restart')
            logger.sys_info('Tomcat restarted.')
        except Exception as e:
            logger.sys_error('Could not restart tomcat %s.'%(e))

        try:
            sc.keystone('restart')
            logger.sys_info('Keystone restarted.')
        except Exception as e:
            logger.sys_error('Could not restart keystone %s.'%(e))

        try:
            sc.neutron('restart')
            logger.sys_info('Neutron restarted.')
        except Exception as e:
            logger.sys_error('Could not restart neutron %s.'%(e))

        try:
            sc.glance('restart')
            logger.sys_info('Glance restarted.')
        except Exception as e:
            logger.sys_error('Could not restart glance %s.'%(e))

        try:
            sc.heat('restart')
            logger.sys_info('Heat restarted.')
        except Exception as e:
            logger.sys_error('Could not restart Heat %s.'%(e))

        try:
            sc.ceilometer('restart')
            logger.sys_info('Ceilometer restarted.')
        except Exception as e:
            logger.sys_error('Could not restart Ceilometer %s.'%(e))

    if(config.NODE_TYPE == 'cc' or config.NODE_TYPE == 'cn' or config.NODE_TYPE == 'ha'):
        try:
            sc.nova('restart')
            logger.sys_info('Nova restarted.')
        except Exception as e:
            logger.sys_error('Could not restart nova %s.'%(e))
            
        try:
            sc.cinder('restart')
            logger.sys_info('Cinder restarted.')
        except Exception as e:
            logger.sys_error('Could not restart cinder %s.'%(e))

    if(config.NODE_TYPE == 'cn'):
        try:
            sc.ceilometer_cn('restart')
            logger.sys_info('Ceilometer restarted.')
        except Exception as e:
            logger.sys_error('Could not restart Ceilometer on compute node %s.'%(e))

    if(config.NODE_TYPE == 'cc' or config.NODE_TYPE == 'sn' or config.NODE_TYPE == 'ha'):
        try:
            sc.cinder_sn('restart')
            logger.sys_info('Cinder restarted.')
        except Exception as e:
            logger.sys_error('Could not restart cinder %s.'%(e))

    return 'OK'


# Main entry point for this script.
# is passed in and call the routine that will find the gluster volume(s) to the disks.conf
# file so monit can start monitoring it.
if __name__ == "__main__":
    # If we aren't given a node type then go figure it out else use what we were given.
    change_master_password(sys.argv[1])
    sys.exit()
