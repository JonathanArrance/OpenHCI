#get the libs needed
from transcirrus.component.keystone.keystone_users import user_ops
import transcirrus.common.config as config
import transcirrus.common.logger as logger

def change_admin_password(auth_dict,new_password):
    #change the linux password
    if((auth_dict['is_admin'] == 1) and (auth_dict['adm_token'] != '') and (auth_dict['adm_token'] == config.ADMIN_TOKEN)):
        p = subprocess.Popen(('mkpasswd', '-m', 'sha-512', new_pass), stdout=subprocess.PIPE)
        shadow_password = p.communicate()[0].strip()
        if(p.returncode != 0):
            logger.sys_error('Error creating hash for admin')
            return 'ERROR'
        r = subprocess.call(('usermod', '-p', shadow_password, 'admin'))
        if(r != 0):
            logger.sys_error('Error changing password for admin')
            return 'ERROR'
        elif(r == 0):
            logger.sys_info("Password for admin user successfully changed.")
            #instantiate the object
            new = user_ops(auth_dict)
            change = new.update_user_password(new_password)
    else:
        logger.sys_error("Could not change the admin user passowrd")
        return 'ERROR'
