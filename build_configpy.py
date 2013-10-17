import os
import transcirrus.common.util as util
from transcirrus.common.auth import authorization


hostname = os.system('hostname')
print hostname
try:
    #use util.close_db when you no longer need o have the connection open.
    #Try to connect to the transcirrus db
    db = pgsql('%s','5432','transcirrus','transuser','builder')%(hostname)
    print db
except Exception as e:
    print 'ERROR'

try:
    select_id = {'select':"param_value", 'from':"trans_system_settings", 'where':"parameter='cloud_controller_id'", 'and':"host_system='%s'"%(hostname)}
    nodeid = db.pg_select(select_id)
except:
    print 'ERROR'

system_vars = util.get_system_variables(nodeid[0][0])

#build a file descriptor for config.py
#NODE - check quantum version make path based on that.

config_array = []
conf = {}
for key,val in system_vars.items():
    row = key.upper()+"="+'"%s"'%(val)
    print row
    config_array.append(row)
conf['op'] = 'new'
conf['file_owner'] = 'transuser'
conf['file_group'] = 'transystem'
conf['file_perm'] = '644'
conf['file_path'] = 'user/home/'
conf['file_name'] = 'config.py'
conf['file_content'] = config_array

#build the new config.py out
write = write_new_config_file(conf)