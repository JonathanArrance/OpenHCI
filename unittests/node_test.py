import transcirrus.database.node_db as node


print "Inserting a node"
node1 = {'node_id':'13','node_name':'node13','node_type':"cc",'node_data_ip':"192.168.10.3",'node_mgmt_ip':"192.168.11.3",'node_controller':"ciac-03",'node_cloud_name':"test",'avail_zone':'nova'}
inserter = node.insert_node(node1)
print inserter

print "---------------------------------------"

'''
print "listing nodes"
lister = node.list_nodes()
print lister

print "---------------------------------------"


print "checking if node 11 exists"
checker = node.check_node_exists('11')
print checker

print "---------------------------------------"


print "getting node 11 info"
getter = node.get_node('11')
print getter
print "getter status"
print getter['status']

print "---------------------------------------"

print "Updateing node mgmt_ip and node_name"
update = {'node_id':'11','node_mgmt_ip':'172.89.89.10','node_name':'jonarrance'}
up = node.update_node(update)
print up

print "---------------------------------------"


print "getting node 11 info after update"
getter2 = node.get_node('11')
print getter2
print "getter status"
print getter2['status']

print "---------------------------------------"


print "deleteing node 11"
deleter = node.delete_node('11')
print deleter

print "---------------------------------------"

print "checking if node 11 still exists"
checker2 = node.check_node_exists('11')
print checker2
'''
