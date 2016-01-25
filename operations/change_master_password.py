#get the libs needed
#from celery import Celery
#from celery import task
from transcirrus.component.keystone.keystone_users import user_ops
import os
import subprocess
import transcirrus.common.config as config
import transcirrus.common.logger as logger
import transcirrus.common.util as util
import transcirrus.database.node_db as node_db
import transcirrus.common.service_control as sc

#@celery.task(name='change_admin_password')
def change_master_password(auth_dict,new_password):
    
    #change the linux password
    if((auth_dict['is_admin'] == 1) and (auth_dict['adm_token'] != '') and (auth_dict['adm_token'] == config.ADMIN_TOKEN)):
        #null_fds = [os.open(os.devnull, os.O_RDWR) for x in xrange(2)]
        # save the current file descriptors to a tuple
        #save = os.dup(1), os.dup(2)
        # put /dev/null fds on 1 and 2
        #os.dup2(null_fds[0], 1)
        #os.dup2(null_fds[1], 2)
        
        #print ('echo -e '+new_password+'\n'+new_password+'\n | sudo passwd admin')
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
            #heat
            write_heat = os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/heat/g' /etc/heat/heat.conf"""%(new_password,ip))
            if(write_heat != 0):
                logger.sys_warning('Could not write the heat.conf and update the master password.')
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
            #apersona
            write_apersona = os.system("""sudo sed -i 's/db.password=.*/db.password=%s/g' /var/lib/tomcat6/webapps/apkv/WEB-INF/classes/apersona-db.properties"""%(new_password))
            if(write_apersona != 0):
                logger.sys_warning('Could not update the apersona password.')
            write_apersona2 = os.system("""sudo sed -i 's/db.password=.*/db.password=%s/g' /var/lib/tomcat6/webapps/api_portal/WEB-INF/classes/apersona-db.properties"""%(new_password))
            if(write_apersona2 != 0):
                logger.sys_warning('Could not update the apersona password.')

        if(config.NODE_TYPE == 'cc' or config.NODE_TYPE == 'cn' or config.NODE_TYPE == 'ha'):
            if(config.NODE_TYPE == 'cn' or config.NODE_TYPE == 'ha'):
                ip = config.TRANSCIRRUS_DB
            else:
                ip = 'localhost'
            #nova
            write_nova = os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/nova/g' /etc/nova/nova.conf"""%(new_password,ip))
            if(write_nova != 0):
                logger.sys_warning('Could not write the nova.conf and update the master password.')
            #ceilometer
            write_ceilometer = os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/ceilometer/g' /etc/ceilometer/ceilometer.conf"""%(new_password,ip))
            if(write_ceilometer != 0):
                logger.sys_warning('Could not write the ceilometer.conf and update the master password.')
            #neutron
            write_neutron= os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/neutron/g' /etc/neutron/neutron.conf"""%(new_password,ip))
            if(write_neutron != 0):
                logger.sys_warning('Could not write the neutron.conf and update the master password.')

        if(config.NODE_TYPE == 'cc' or config.NODE_TYPE == 'sn' or config.NODE_TYPE == 'ha'):
            if(config.NODE_TYPE == 'sn' or config.NODE_TYPE == 'ha'):
                ip = config.TRANSCIRRUS_DB
            else:
                ip = 'localhost'
            #cinder
            write_cinder = os.system("""sudo sed -i 's/connection=postgresql.*/connection=postgresql:\/\/transuser:%s@%s\/cinder/g' /etc/cinder/cinder.conf"""%(new_password,ip))
            if(write_cinder != 0):
                logger.sys_warning('Could not write the cinder.conf and update the master password.')

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

        elif(config.NODE_TYPE == 'cc' or config.NODE_TYPE == 'cn' or config.NODE_TYPE == 'ha'):
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

        elif(config.NODE_TYPE == 'cn'):
            try:
                sc.ceilometer_cn('restart')
                logger.sys_info('Ceilometer restarted.')
            except Exception as e:
                logger.sys_error('Could not restart Ceilometer on compute node %s.'%(e))

        elif(config.NODE_TYPE == 'cc' or config.NODE_TYPE == 'sn' or config.NODE_TYPE == 'ha'):
            try:
                sc.cinder_sn('restart')
                logger.sys_info('Cinder restarted.')
            except Exception as e:
                logger.sys_error('Could not restart cinder %s.'%(e))

        return 'OK'
    else:
        logger.sys_error("Could not change the admin user passowrd")
        return 'ERROR'
