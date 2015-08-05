from lxml import etree

import transcirrus.common.config as config
import transcirrus.common.logger as logger

from transcirrus.component.ceilometer.ceilometer_meters import meter_ops

libvirt = None


class ThirdPartyMeters:
    # per_type_uris = dict(uml='uml:///system', xen='xen:///', lxc='lxc:///')

    def __init__(self, user_dict):
        reload(config)
        self.userdict = user_dict
        if (not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        else:
            self.username = user_dict['username']
            self.password = user_dict['password']
            self.project_id = user_dict['project_id']
            if ((self.project_id == 'NULL') or (not user_dict['project_id'])):
                logger.sys_error("In order to perform user operations, Admin user must be assigned to project")
                raise Exception("In order to perform user operations, Admin user must be assigned to project")
            self.token = user_dict['token']
            self.status_level = user_dict['status_level']
            self.user_level = user_dict['user_level']
            self.is_admin = user_dict['is_admin']
            self.adm_token = user_dict['adm_token']
            if 'sec' in user_dict:
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'

            # used to overide the value in the DB, mostly used during setup or re init
            if ('api_ip' in user_dict):
                # NOTE may have to add an IP check
                self.api_ip = user_dict['api_ip']
            else:
                self.api_ip = config.API_IP

            # get the default cloud controller info
            self.controller = config.CLOUD_CONTROLLER

        if ((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if (self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")

        if ((self.token == 'error') or (self.token == '')):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" % self.username)
            raise Exception("Invalid status level passed for user: %s" % self.username)

        self.uri = self._get_uri()
        self.connection = None

    def _get_uri(self):
        # I know this is a statically assigned variable.  This will be resolved once we migrate to Openstack Kilo
        return 'qemu:///system'

    def _get_connection(self):
        if not self.connection or not self._test_connection():
            global libvirt
            if libvirt is None:
                libvirt = __import__('libvirt')
            logger.sys_error('Connecting to libvirt: %s' % self.uri)
            self.connection = libvirt.openReadOnly(self.uri)

        return self.connection

    def _test_connection(self):
        try:
            self.connection.getCapabilities()
            return True
        except libvirt.libvirtError as e:
            if (e.get_error_code() == libvirt.VIR_ERR_SYSTEM_ERROR and
                        e.get_error_domain() in (libvirt.VIR_FROM_REMOTE,
                                                 libvirt.VIR_FROM_RPC)):
                logger.sys_error('Connection to libvirt broke')
                return False
            raise

    def _lookup_by_name(self, instance_name):
        try:
            return self._get_connection().lookupByName(instance_name)
        except Exception as ex:
            if not libvirt or not isinstance(ex, libvirt.libvirtError):
                raise Exception(unicode(ex))

            msg = ('Error from libvirt while looking up instance <name=%(name)s, '
                   'can not get info from libvirt.') % {'name': instance_name}
            raise Exception(msg)

    def manual_inspect_memory_usage(self, instance_virsh_name, project_id, instance_id):
        domain = self._lookup_by_name(instance_virsh_name)

        try:
            memory_stats = domain.memoryStats()
            if (memory_stats and
                    memory_stats.get('actual') and
                    memory_stats.get('rss')):
                memory_used = (memory_stats.get('actual') -
                               memory_stats.get('rss'))
                # Stat provided from libvirt is in KB, converting it to MB.
                megabyte = float(0.000976562)
                memory_used *= megabyte
                mo = meter_ops(self.userdict)
                mo.post_meter(project_id, "gauge", "memory.usage", memory_used, "MB", instance_id)
            else:
                msg = ('Failed to inspect memory usage of instance <name=%(name)s, id=%(id)s>, '
                       'can not get info from libvirt.') % {
                          'name': instance_virsh_name, 'instance-id': instance_id, 'project-id': project_id}
                raise Exception(msg)
        # memoryStats might launch an exception if the method is not supported
        # by the underlying hypervisor being used by libvirt.
        except libvirt.libvirtError as e:

            msg = ('Failed to inspect memory usage of %(instance_uuid)s,'
                   'can not get info from libvirt: %(error)s') % {
                      'instance_uuid': instance_id, 'error': e}

            raise Exception(msg)

    def manual_inspect_disk_info(self, instance_virsh_name, project_id, instance_id):
        domain = self._lookup_by_name(instance_virsh_name)

        tree = etree.fromstring(domain.XMLDesc(0))
        mo = meter_ops(self.userdict)

        total_capacity = 0
        total_allocation = 0
        total_physical = 0

        for device in filter(bool, [target.get("dev") for target in tree.findall('devices/disk/target')]):
            block_info = domain.blockInfo(device, 0)

            total_capacity += block_info[0]
            total_allocation += block_info[1]
            total_physical += block_info[2]

        mo.post_meter(project_id, "gauge", "disk.capacity", total_capacity, "B", instance_id)
        mo.post_meter(project_id, "gauge", "disk.allocation", total_allocation, "B", instance_id)
        mo.post_meter(project_id, "gauge", "disk.physical", total_physical, "B", instance_id)

    def manual_inspect_memory_resident(self, instance_virsh_name, project_id, instance_id):
        domain = self._lookup_by_name(instance_virsh_name)
        memory = domain.memoryStats()['rss']
        megabyte = float(0.000976562)
        memory *= megabyte

        mo = meter_ops(self.userdict)
        mo.post_meter(project_id, "gauge", "memory.resident", memory, "MB", instance_id)
