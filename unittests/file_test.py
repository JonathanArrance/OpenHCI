import transcirrus.database.node_db as node
import transcirrus.common.util as util

'''
file_array = ['test=testfile','proj=testproject','my_ip=192.168.10.3','sql=postgresql://test:test@localhost/nova']
file_path = '/etc/nova'
file_name = 'jonarrance.conf'
file_owner = 'stack'
file_group = 'stack'
file_permissions = '777'

file_dict = {'file_path':file_path,'file_name':file_name,'file_content':file_array,'file_owner':file_owner,'file_group':file_group,'file_perm':file_permissions}

write = util.write_new_config_file(file_dict)
print write

'''

test = node.get_node_nova_config('222')
print test