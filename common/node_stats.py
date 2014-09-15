import xml.dom.minidom
import random
import urllib                         
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql

# Global variables.
xmldoc = None
disk_list = []


# Main entry point for this file.
# This function will return the statistics for all nodes in the cloud, for a specific node in the cloud or dummy stats for testing.
def node_stats (node="all"):
    # Get the stats for all nodes in the cloud.
    if node == "all":
        node_list = get_list_of_nodes()
        stats_dict = get_node_stats (node_list)

    # Get dummy stats for testing purposes.
    elif node == "demo":
        stats_dict = get_demo_stats()

    # Get the stats for the given node.
    else:
        # Determine if we were given a name or IP address.
        if node.split('.')[-1].isdigit():
            # We have an IP address so just use it for the name and address.
            node_list = []
            node_list.append({'node_name': node, 'node_data_ip': node, 'node_type': "unknown"})
        else:
            # We have a name so go lookup the the IP address in the database.
            node_list = get_list_of_nodes (node)
        stats_dict = get_node_stats (node_list)

    return (stats_dict)


# Return some random stats for 3 simulated nodes.
def get_demo_stats():
    stats_dict = {}

    # We will simulate the stats for 3 nodes (core, compute & storage) in a cloud.
    host_name         = "demo_core-1"
    host_type         = "core"
    load_avg01        = "%.2f" % random.uniform(1, 10)
    load_avg05        = "%.2f" % random.uniform(1, 10)
    load_avg15        = "%.2f" % random.uniform(1, 10)
    cpu_user          = "%.1f" % random.uniform(1, 45)
    cpu_system        = "%.1f" % random.uniform(1, 45)
    cpu_wait          = "%.1f" % random.uniform(0, 5)
    mem_used_percent  = "%.1f" % random.uniform(0, 90)
    swap_used_percent = "%.1f" % random.uniform(0, 25)

    rootfs_name       = "rootfs"
    rootfs_total      = "49214.7"
    rootfs_usage      = "%.1f" % (float(rootfs_total) - random.uniform(0, 40000))
    rootfs_precent    = "%.1f" % (float(rootfs_usage) / float(rootfs_total) * 100)

    gluster_name      = "gluster"
    gluster_total     = "1428548.1"
    gluster_usage     = "%.1f" % (float(gluster_total) - random.uniform(0, 1400000))
    gluster_precent   = "%.1f" % (float(gluster_usage) / float(gluster_total) * 100)

    stats_dict['node0'] = {'name': host_name, 'type': host_type, 'load_avg01': load_avg01, 'load_avg05': load_avg05,
                           'load_avg15': load_avg15, 'cpu_user': cpu_user, 'cpu_system': cpu_system,
                           'cpu_wait': cpu_wait, 'mem_used_percent': mem_used_percent, 'swap_used_percent': swap_used_percent}

    stats_dict['node0']['disk0'] = {'name': rootfs_name, 'total_space': rootfs_total, 'space_usage_mb': rootfs_usage, 'space_usage_precent': rootfs_precent}
    stats_dict['node0']['disk1'] = {'name': gluster_name, 'total_space': gluster_total, 'space_usage_mb': gluster_usage, 'space_usage_precent': gluster_precent}
    
    host_name         = "demo_compute-1"
    host_type         = "compute"
    load_avg01        = "%.2f" % random.uniform(1, 10)
    load_avg05        = "%.2f" % random.uniform(1, 10)
    load_avg15        = "%.2f" % random.uniform(1, 10)
    cpu_user          = "%.1f" % random.uniform(1, 45)
    cpu_system        = "%.1f" % random.uniform(1, 45)
    cpu_wait          = "%.1f" % random.uniform(0, 5)
    mem_used_percent  = "%.1f" % random.uniform(0, 90)
    swap_used_percent = "%.1f" % random.uniform(0, 25)

    rootfs_name       = "rootfs"
    rootfs_total      = "49214.7"
    rootfs_usage      = "%.1f" % (float(rootfs_total) - random.uniform(0, 40000))
    rootfs_precent    = "%.1f" % (float(rootfs_usage) / float(rootfs_total) * 100)

    stats_dict['node1'] = {'name': host_name, 'type': host_type, 'load_avg01': load_avg01, 'load_avg05': load_avg05,
                           'load_avg15': load_avg15, 'cpu_user': cpu_user, 'cpu_system': cpu_system,
                           'cpu_wait': cpu_wait, 'mem_used_percent': mem_used_percent, 'swap_used_percent': swap_used_percent}

    stats_dict['node1']['disk0'] = {'name': rootfs_name, 'total_space': rootfs_total, 'space_usage_mb': rootfs_usage, 'space_usage_precent': rootfs_precent}
    
    host_name         = "demo_storage-1"
    host_type         = "storage"
    load_avg01        = "%.2f" % random.uniform(1, 10)
    load_avg05        = "%.2f" % random.uniform(1, 10)
    load_avg15        = "%.2f" % random.uniform(1, 10)
    cpu_user          = "%.1f" % random.uniform(1, 45)
    cpu_system        = "%.1f" % random.uniform(1, 45)
    cpu_wait          = "%.1f" % random.uniform(0, 5)
    mem_used_percent  = "%.1f" % random.uniform(0, 90)
    swap_used_percent = "%.1f" % random.uniform(0, 25)

    rootfs_name       = "rootfs"
    rootfs_total      = "49214.7"
    rootfs_usage      = "%.1f" % (float(rootfs_total) - random.uniform(0, 40000))
    rootfs_precent    = "%.1f" % (float(rootfs_usage) / float(rootfs_total) * 100)

    gluster_name      = "gluster"
    gluster_total     = "1428548.1"
    gluster_usage     = "%.1f" % (float(gluster_total) - random.uniform(0, 1400000))
    gluster_precent   = "%.1f" % (float(gluster_usage) / float(gluster_total) * 100)

    stats_dict['node2'] = {'name': host_name, 'type': host_type, 'load_avg01': load_avg01, 'load_avg05': load_avg05,
                           'load_avg15': load_avg15, 'cpu_user': cpu_user, 'cpu_system': cpu_system,
                           'cpu_wait': cpu_wait, 'mem_used_percent': mem_used_percent, 'swap_used_percent': swap_used_percent}

    stats_dict['node2']['disk0'] = {'name': rootfs_name, 'total_space': rootfs_total, 'space_usage_mb': rootfs_usage, 'space_usage_precent': rootfs_precent}
    stats_dict['node2']['disk1'] = {'name': gluster_name, 'total_space': gluster_total, 'space_usage_mb': gluster_usage, 'space_usage_precent': gluster_precent}

    return (stats_dict)


# Get the stats for each node in the node_list.
def get_node_stats (node_list):
    stats_dict = {}

    # Loop through the node(s) and get the stats for each.
    node_idx = 0
    for node in node_list:
        node_name = node['node_name']
        node_ip   = node['node_data_ip']
        node_type = node['node_type']
        dict_name = "node%d" % node_idx

        # Get and parse the xml from the node.
        if (get_and_parse_xml (node_ip) != None):
            # There was a problem getting the xml.
            stats_dict[dict_name] = {'name': node_name, 'type': "error"}
            continue

        host_name         = get_host_name()
        host_type         = get_host_type(node_type)
        load_avg01        = get_load_avg01()
        load_avg05        = get_load_avg05()
        load_avg15        = get_load_avg15()
        cpu_user          = get_cpu_user()
        cpu_system        = get_cpu_system()
        cpu_wait          = get_cpu_wait()
        mem_used_percent  = get_mem_used_percent()
        swap_used_percent = get_swap_used_percent()

        stats_dict[dict_name] = {'name': host_name, 'type': host_type, 'load_avg01': load_avg01, 'load_avg05': load_avg05,
                                 'load_avg15': load_avg15, 'cpu_user': cpu_user, 'cpu_system': cpu_system,
                                 'cpu_wait': cpu_wait, 'mem_used_percent': mem_used_percent, 'swap_used_percent': swap_used_percent}

        # Get the stats for each disk in the xml.
        num_disks = find_disks()
        for i in range(0, num_disks):
            disk_dict_name = "disk%d" % i
            disk_name    = get_disk_name(i)
            disk_usage   = get_disk_usage(i)
            disk_percent = get_disk_percent(i)
            disk_total   = get_disk_total(i)
            stats_dict[dict_name][disk_dict_name] = {'name': disk_name, 'total_space': disk_total, 'space_usage_mb': disk_usage, 'space_usage_precent': disk_percent}

    return (stats_dict)


# Goes through the database and returns a dictonary of all nodes with the node's name and data IP address
# OR just the name and IP address of the given node.
def get_list_of_nodes (node_name=None):
    try:
        handle = pgsql (config.TRANSCIRRUS_DB, config.TRAN_DB_PORT, config.TRAN_DB_NAME, config.TRAN_DB_USER, config.TRAN_DB_PASS)
    except Exception as e:
        print "Could not connect to db with error: %s" % (e)
        raise Exception ("Could not connect to db with error: %s" %(e))

    if node_name == None:
        select_nodes = {'select':'node_name,node_data_ip,node_type','from':'trans_nodes'}
    else:
        select_nodes = {'select':'node_name,node_data_ip,node_type','from':'trans_nodes','where':"node_name='%s'" % (node_name)}

    nodes_data = handle.pg_select (select_nodes)
    if len(nodes_data) == 0:
        handle.pg_close_connection()
        if node_name == None:
            print "No other nodes where found in the database"
        else:
            print "Could not find a node in the database with a name of %s" % node_name
        nodes_list = []
        return (nodes_list)

    nodes_list = []
    for node in nodes_data:
        nodes_list.append(node)

    handle.pg_close_connection()
    return (nodes_list)


# Get the xml via http from the given IP address.
def get_and_parse_xml (host_ip):
    global xmldoc
    url = "http://admin:monit@" + host_ip + ":2812/_status?format=xml"
    try:                                  
        xmldoc = xml.dom.minidom.parse (urllib.urlopen(url))
        return None
    except Exception, e:            
        return (e.message)

# Return the hostname from the xml.
def get_host_name():
    service_list = xmldoc.getElementsByTagName ('service')
    for service in service_list:
        if service.attributes['type'].value == "5":
            host_name = str(service.getElementsByTagName('name')[0].firstChild.data)
            break
    return (host_name)

# Return the hosttype based on the short type name.
def get_host_type (type):
    if type == "cc":
        type_name = "core"
    elif type == "cn":
        type_name = "compute"
    elif type == "sn":
        type_name = "storage"
    else:
        type_name = "unknown"
    return (type_name)

# Return the 1min load average from the xml.
def get_load_avg01():
    service_list = xmldoc.getElementsByTagName ('service')
    for service in service_list:
        if service.attributes['type'].value == "5":
            load = service.getElementsByTagName('load')[0]
            load_avg01 = str(load.getElementsByTagName('avg01')[0].firstChild.data)
            break
    return (load_avg01)

# Return the 5min load average from the xml.
def get_load_avg05():
    service_list = xmldoc.getElementsByTagName ('service')
    for service in service_list:
        if service.attributes['type'].value == "5":
            load = service.getElementsByTagName('load')[0]
            load_avg05 = str(load.getElementsByTagName('avg05')[0].firstChild.data)
            break
    return (load_avg05)

# Return the 15min load average from the xml.
def get_load_avg15():
    service_list = xmldoc.getElementsByTagName ('service')
    for service in service_list:
        if service.attributes['type'].value == "5":
            load = service.getElementsByTagName('load')[0]
            load_avg15 = str(load.getElementsByTagName('avg15')[0].firstChild.data)
            break
    return (load_avg15)

# Return the % cpu user from the xml.
def get_cpu_user():
    service_list = xmldoc.getElementsByTagName ('service')
    for service in service_list:
        if service.attributes['type'].value == "5":
            cpu = service.getElementsByTagName("cpu")[0]
            cpu_user = str(cpu.getElementsByTagName('user')[0].firstChild.data)
            break
    return (cpu_user)

# Return the % cpu system from the xml.
def get_cpu_system():
    service_list = xmldoc.getElementsByTagName ('service')
    for service in service_list:
        if service.attributes['type'].value == "5":
            cpu = service.getElementsByTagName('cpu')[0]
            cpu_system = str(cpu.getElementsByTagName('system')[0].firstChild.data)
            break
    return (cpu_system)

# Return the % cpu wait from the xml.
def get_cpu_wait():
    service_list = xmldoc.getElementsByTagName ('service')
    for service in service_list:
        if service.attributes['type'].value == "5":
            cpu = service.getElementsByTagName('cpu')[0]
            cpu_wait = str(cpu.getElementsByTagName('wait')[0].firstChild.data)
            break
    return (cpu_wait)

# Return the % of memory used from the xml.
def get_mem_used_percent():
    service_list = xmldoc.getElementsByTagName ('service')
    for service in service_list:
        if service.attributes['type'].value == "5":
            memory = service.getElementsByTagName('memory')[0]
            mem_used_percent = str(memory.getElementsByTagName('percent')[0].firstChild.data)
            break
    return (mem_used_percent)

# Return the % of swap space used from the xml.
def get_swap_used_percent():
    service_list = xmldoc.getElementsByTagName ('service')
    for service in service_list:
        if service.attributes['type'].value == "5":
            swap = service.getElementsByTagName('swap')[0]
            swap_used_percent = str(swap.getElementsByTagName('percent')[0].firstChild.data)
            break
    return (swap_used_percent)

# Return the number of disks from the xml and keep the list of disks for later use.
def find_disks():
    service_list = xmldoc.getElementsByTagName ('service')
    for service in service_list:
        if service.attributes['type'].value == "0":
            disk_list.append(service)
    return (len(disk_list))

# Return the disk name based on the index into the disk_list.
def get_disk_name(index):
    disk = disk_list[index]
    name = str(disk.getElementsByTagName('name')[0].firstChild.data)
    return (name)

# Return the disk usage (in MB) based on the index into the disk_list.
def get_disk_usage(index):
    disk = disk_list[index]
    block = disk.getElementsByTagName('block')[0]
    usage = str(block.getElementsByTagName('usage')[0].firstChild.data)
    return (usage)

# Return the disk usage (as a percentage) based on the index into the disk_list.
def get_disk_percent(index):
    disk = disk_list[index]
    block = disk.getElementsByTagName('block')[0]
    percent = str(block.getElementsByTagName('percent')[0].firstChild.data)
    return (percent)

# Return the total disk size (in MB) based on the index into the disk_list.
def get_disk_total(index):
    disk = disk_list[index]
    block = disk.getElementsByTagName('block')[0]
    total = str(block.getElementsByTagName('total')[0].firstChild.data)
    return (total)