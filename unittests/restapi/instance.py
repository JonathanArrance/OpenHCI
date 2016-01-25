from transcirrus.common import extras
from transcirrus.common.auth import authorization
from transcirrus.component.nova.server import server_ops
from transcirrus.component.nova.flavor import flavor_ops
from transcirrus.component.nova.image import nova_image_ops
from transcirrus.operations import boot_new_instance as boot_from_vol_ops

INSTANCE_PREFIX = "UT_Instance_"

class Instance:
    def __init__(self):
        self.auth = extras.shadow_auth()
        self.instances = []
        return

    def get_instance_by_index(self, index):
        if len(self.instances) > index:
            return (self.instances[index])
        else:
            return (None)

    def get_instances(self, all_instances=False):
        if all_instances:
            so = server_ops(self.auth)
            instance_list = []
            instance_list = so.list_all_servers()
            return (instance_list)
        else:
            return (self.instances)

    def get_instance_data(self, instance_id, project_id):
        input = {}
        input['server_id']  = instance_id
        input['project_id'] = project_id
        so = server_ops(self.auth)
        instance_data = so.get_server(input)
        return (instance_data)

    def get_num_instances(self, all_instances=False):
        if all_instances:
            so = server_ops(self.auth)
            instance_list = []
            instance_list = so.list_all_servers()
            return (len(instance_list))
        else:
            print "num instances %s" % len(self.instances)
            return (len(self.instances))

    def delete_instance_by_id(self, instance_id):
        so = server_ops(self.auth)
        instance_list = so.list_all_servers()
        instance = {}
        instance['server_id'] = instance_id
        instance['project_id'] = None
        for inst in instance_list:
            if inst[server_id] == instance_id:
                instance['project_id'] = inst['project_id']
        if inst['project_id'] == None:
            raise Exception("Could not find project_id for given instance_id (%s)" % instance_id)
        instance_info = so.delete_server(instance)
        return (True)

    def cleanup(self, delete_all=False):
        so = server_ops(self.auth)
        instance_list = so.list_all_servers()
        for instance in instance_list:
            if instance['server_name'].startswith(INSTANCE_PREFIX) or delete_all:
                self.delete_instance_by_id(instance['instance_id'])
        return (True)

    def get_image_id(self, project_id):
        io = nova_image_ops(self.auth)
        images = io.nova_list_images(project_id)
        for image in images:
            if "CirrOS" in image['image_name']:
                return (image['image_id'])
        return (None)

    def get_flavor_id(self):
        fo = flavor_ops(self.auth)
        flavors = fo.list_flavors()
        for flavor in flavors:
            if "m1.tiny" in flavor['name']:
                return (flavor['id'])
        return

    def build_instance(self, postfix, project, alt_auth=None):
        instance = {}
        instance['project_id'] = project['project_id']
        instance['instance_name'] = INSTANCE_PREFIX + postfix
        instance['image_id'] = self.get_image_id(project['project_id'])
        instance['flavor_id'] = self.get_flavor_id()
        instance['sec_group_name'] = project['def_security_group_name']
        instance['sec_key_name'] = project['def_security_key_name']

        if 'def_network_name' in project:
            instance['network_name'] = project['def_network_name']
        if 'zone' in project:
            instance['avail_zone'] = project['zone']
        if 'is_boot_from_volume' in project:
            instance['boot_from_vol'] = project['is_boot_from_volume']
        if 'volume_size' in project:
            instance['volume_size'] = project['volume_size']
        if 'volume_name' in project:
            instance['volume_name'] = project['volume_name']
        if 'volume_type' in project:
            instance['volume_type'] = project['volume_type']

        if alt_auth != None:
            auth = alt_auth
        else:
            auth = self.auth

        instance_info = boot_from_vol_ops.boot_instance(instance, auth)['instance']
        self.instances.append(instance_info['vm_id'])
        return (instance_info['vm_id'])
