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
        null_fds = [os.open(os.devnull, os.O_RDWR) for x in xrange(2)]
        # save the current file descriptors to a tuple
        save = os.dup(1), os.dup(2)
        # put /dev/null fds on 1 and 2
        os.dup2(null_fds[0], 1)
        os.dup2(null_fds[1], 2)
        
        #print ('echo -e '+new_password+'\n'+new_password+'\n | sudo passwd admin')
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
        #file_dict = {'file_path':'/home/transuser',
        #             'file_name':'factory_creds',
        #             'file_content':['export OS_PASSWORD='+pass_dict['new_password']],
        #             'file_owner':'transuser',
        #             'file_group':'transuser',
        #             'file_perm':666,
        #             'op':'append'
        #            } 
        #os.system('sudo chown -R transuser:transystem /home/transuser')
        #write_creds = util.write_new_config_file(file_dict)
        write_creds = os.system("""sudo sed -i 's/OS_PASSWORD=.*/OS_PASSWORD=%s/g' /home/transuser/factory_creds"""%(new_password))
        if(write_creds != 0):
            logger.sys_warning('Could not write the new credentials file in transuser home directory.')
        
        # restore file descriptors so I can print the results
        os.dup2(save[0], 1)
        os.dup2(save[1], 2)
        # close the temporary fds
        os.close(null_fds[0])
        os.close(null_fds[1])
        
        return 'OK'
    else:
        logger.sys_error("Could not change the admin user passowrd")
        return 'ERROR'
