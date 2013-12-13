import transcirrus.database.node_db as node
import transcirrus.common.util as util
import time

#print "Building a dummy test config file"
#file_array = ['test=testfile','proj=testproject','my_ip=192.168.10.3','sql=postgresql://test:test@localhost/nova']
#file_path = '/tmp/test'
#file_name = 'test.conf'
#file_owner = 'transuser'
#file_group = 'transystem'
#file_permissions = '777'
#file_op = 'append'

#file_dict = {'file_path':file_path,'file_name':file_name,'file_content':file_array,'file_owner':file_owner,'file_group':file_group,'file_perm':file_permissions,'file_op':file_op}

#write = util.write_new_config_file(file_dict)
#print write


time.sleep(1)
print "-------------------------------------------"
print "Getting Nova config info for a dummy node"
#test will be an array
test = node.get_node_nova_config('000-12345678-12345')
print test

time.sleep(1)
print "-------------------------------------------"
print "Writing out the nova config files"
for x in test:
    write = util.write_new_config_file(x)
    print write

'''
time.sleep(1)
print "-------------------------------------------"
print "Getting the neutron config info for a dummy node"
neu - node.get_node_neutron_config('222')
print neu

ime.sleep(1)
print "-------------------------------------------"
print "Writing out the neutron config files"
write = node.write_new_config_file(neu)
'''
