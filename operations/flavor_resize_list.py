from transcirrus.component.nova.server import server_ops
from transcirrus.component.nova.flavor import flavor_ops

def get_list_of_valid_resizeable_flavors(auth_dict, project_id, instance_id):

    master_list = []
    # auth_dict = extras.shadow_auth()
    so = server_ops(auth_dict)
    fo = flavor_ops(auth_dict)
    instance_dictionary = {"server_id": instance_id, "project_id": project_id}
    instance_info = so.get_server(instance_dictionary)
    current_flavor_info = fo.get_flavor(instance_info["flavor_id"])
    current_flavor_disk_size = current_flavor_info["disk_space(GB)"]

    flavor_array = fo.list_flavors()
    for flavor in flavor_array:
        checking_flavor_disk = fo.get_flavor(flavor["id"])["disk_space(GB)"]
        print checking_flavor_disk
        if int(checking_flavor_disk) >= int(current_flavor_disk_size):
            master_list.append(flavor)
        else:
            print "failed" + str(flavor)
    return master_list
