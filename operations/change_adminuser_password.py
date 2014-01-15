#get the libs needed
#from celery import Celery
#from celery import task
from transcirrus.component.keystone.keystone_users import user_ops
import os
import subprocess
import transcirrus.common.config as config
import transcirrus.common.logger as logger
import transcirrus.common.util as util

#Activate the amqp
#celery = Celery('change_adminuser_password', backend='amqp', broker='amqp://guest:transcirrus1@%s/'%(config.API_IP))

#@celery.task(name='change_admin_password')
def change_admin_password(auth_dict,new_password):
    #change the linux password
    if((auth_dict['is_admin'] == 1) and (auth_dict['adm_token'] != '') and (auth_dict['adm_token'] == config.ADMIN_TOKEN)):
        #p = subprocess.Popen(('mkpasswd', '-m', 'sha-512','new_password'), stdout=subprocess.PIPE)
        #shadow_password = p.communicate()[0].strip()
        #if(p.returncode != 0):
        #    logger.sys_error('Error creating hash for admin')
        #    return 'ERROR'
        #r = subprocess.call(('sudo', 'usermod', '-p', shadow_password, 'admin'))
        #if(r != 0):
        #    logger.sys_error('Error changing password for admin')
        #    return 'ERROR'
        #elif(r == 0):
        print ('echo -e '+new_password+'\n'+new_password+'\n | sudo passwd admin')
        os.system('echo \''+new_password+'\n'+new_password+'\n\' | sudo passwd admin')
        logger.sys_info("Password for admin user successfully changed.")
        #instantiate the object
        new = user_ops(auth_dict)
        pass_dict = {'new_password':new_password,
                     'project_id':auth_dict['project_id'],
                     'user_id':auth_dict['user_id']
                    }
        change = new.update_user_password(pass_dict)
        #update the factory default credentials file in transuser
        file_dict = {'file_path':'/home/transuser',
                     'file_name':'factory_creds',
                     'file_content':['export OS_PASSWORD='+pass_dict['new_password']],
                     'file_owner':'transuser',
                     'file_group':'transuser',
                     'file_perm':664,
                     'op':'append'
                    }
        write_creds = util.write_new_config_file(file_dict)
        if(write_creds != 'OK'):
            logger.sys_warning('Could not write the new credentials file in transuser home directory.')
        return 'OK'
    else:
        logger.sys_error("Could not change the admin user passowrd")
        return 'ERROR'
