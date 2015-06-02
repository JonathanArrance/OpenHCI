
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Implementation of Inspector abstraction for libvirt."""

import six
import sys

# sys.path.append("/usr/lib/python2.6/site-packages")

from ceilometer.compute.pollsters import util
from ceilometer.compute.virt import inspector as virt_inspector
from ceilometer.openstack.common.gettextutils import _
from ceilometer.openstack.common import log as logging
from oslo.config import cfg

libvirt = None

LOG = logging.getLogger(__name__)

libvirt_opts = [
    cfg.StrOpt('libvirt_type',
               default='kvm',
               help='Libvirt domain type (valid options are: '
                    'kvm, lxc, qemu, uml, xen).'),
    cfg.StrOpt('libvirt_uri',
               default='',
               help='Override the default libvirt URI '
                    '(which is dependent on libvirt_type).'),
]

CONF = cfg.CONF
CONF.register_opts(libvirt_opts)

def retry_on_disconnect(function):
    def decorator(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except libvirt.libvirtError as e:
            if (e.get_error_code() == libvirt.VIR_ERR_SYSTEM_ERROR and
                e.get_error_domain() in (libvirt.VIR_FROM_REMOTE,
                                         libvirt.VIR_FROM_RPC)):
                LOG.debug(_('Connection to libvirt broken'))
                self.connection = None
                return function(self, *args, **kwargs)
            else:
                raise
    return decorator

class LibvirtInspector(virt_inspector.Inspector):

    per_type_uris = dict(uml='uml:///system', xen='xen:///', lxc='lxc:///')

    def __init__(self):
        self.uri = self._get_uri()
        self.connection = None

    def _get_uri(self):
        return CONF.libvirt_uri or self.per_type_uris.get(CONF.libvirt_type,
                                                          'qemu:///system')

    def _get_connection(self):
        if not self.connection or not self._test_connection():
            global libvirt
            if libvirt is None:
                libvirt = __import__('libvirt')

            LOG.debug(_('Connecting to libvirt: %s'), self.uri)
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
                LOG.debug(_('Connection to libvirt broke'))
                return False
            raise

    def _lookup_by_name(self, instance_name):
        try:
            return self._get_connection().lookupByName(instance_name)
        except Exception as ex:
            if not libvirt or not isinstance(ex, libvirt.libvirtError):
                raise virt_inspector.InspectorException(unicode(ex))
            error_code = ex.get_error_code()
            msg = ("Error from libvirt while looking up %(instance_name)s: "
                   "[Error Code %(error_code)s] "
                   "%(ex)s" % {'instance_name': instance_name,
                               'error_code': error_code,
                               'ex': ex})
            raise virt_inspector.InstanceNotFoundException(msg)

    @retry_on_disconnect
    def _lookup_by_uuid(self, instance):
        instance_name = util.instance_name(instance)
        try:
            return self._get_connection().lookupByUUIDString(instance.id)
        except Exception as ex:
            if not libvirt or not isinstance(ex, libvirt.libvirtError):
                raise virt_inspector.InspectorException(six.text_type(ex))
            error_code = ex.get_error_code()
            if (error_code == libvirt.VIR_ERR_SYSTEM_ERROR and
                ex.get_error_domain() in (libvirt.VIR_FROM_REMOTE,
                                          libvirt.VIR_FROM_RPC)):
                raise
            msg = _("Error from libvirt while looking up instance "
                    "<name=%(name)s, id=%(id)s>: "
                    "[Error Code %(error_code)s] "
                    "%(ex)s") % {'name': instance_name,
                                 'id': instance.id,
                                 'error_code': error_code,
                                 'ex': ex}
            raise virt_inspector.InstanceNotFoundException(msg)
# This method belongs in the /usr/lib/python2.6/site-packages/ceilometer/compute/virt/libvirt/inspector.py class
    def inspect_memory_usage(self, instance):
        instance_name = util.instance_name(instance)
        domain = self._lookup_by_name(instance_name)

        try:
            memory_stats = domain.memoryStats()
            if (memory_stats and
                    memory_stats.get('actual') and
                    memory_stats.get('rss')):
                memory_used = (memory_stats.get('actual') -
                               memory_stats.get('rss'))
                # Stat provided from libvirt is in KB, converting it to MB.
                megabyte = float(0.000976562)
                memory_used = megabyte * memory_used
                LOG.error("LibvirtIF_USED: %s" % memory_used)
                return virt_inspector.MemoryUsageStats(usage=memory_used)
            else:
                LOG.error("LibvirtELSE: %s" % memory_stats)
                msg = _('Failed to inspect memory usage of instance '
                        '<name=%(name)s, id=%(id)s>, '
                        'can not get info from libvirt.') % {
                    'name': instance_name, 'id': instance.id}
                raise virt_inspector.NoDataException(msg)
        # memoryStats might launch an exception if the method is not supported
        # by the underlying hypervisor being used by libvirt.
        except libvirt.libvirtError as e:

            msg = _('Failed to inspect memory usage of %(instance_uuid)s, '
                    'can not get info from libvirt: %(error)s') % {
                'instance_uuid': instance.id, 'error': e}

            raise virt_inspector.NoDataException(msg)

    def inspect_memory_usage_by_virsh_name(self, instance_virsh_name, instance_op_uuid):
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
                memory_used = megabyte * memory_used
                LOG.error("LibvirtIF_USED: %s" % memory_used)
                return virt_inspector.MemoryUsageStats(usage=memory_used)
            else:
                LOG.error("LibvirtELSE: %s" % memory_stats)
                msg = _('Failed to inspect memory usage of instance '
                        '<name=%(name)s, id=%(id)s>, '
                        'can not get info from libvirt.') % {
                    'name': instance_virsh_name, 'id': instance_op_uuid}
                raise virt_inspector.NoDataException(msg)
        # memoryStats might launch an exception if the method is not supported
        # by the underlying hypervisor being used by libvirt.
        except libvirt.libvirtError as e:

            msg = _('Failed to inspect memory usage of %(instance_uuid)s, '
                    'can not get info from libvirt: %(error)s') % {
                'instance_uuid': instance_op_uuid, 'error': e}

            raise virt_inspector.NoDataException(msg)

    def manual_inspect_memory_usage_by_virsh_name_write_to_ceilometer(self, instance_virsh_name, instance_op_uuid):
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
                memory_used = megabyte * memory_used
                LOG.error("LibvirtIF_USED: %s" % memory_used)
                return virt_inspector.MemoryUsageStats(usage=memory_used)
            else:
                LOG.error("LibvirtELSE: %s" % memory_stats)
                msg = _('Failed to inspect memory usage of instance '
                        '<name=%(name)s, id=%(id)s>, '
                        'can not get info from libvirt.') % {
                    'name': instance_virsh_name, 'id': instance_op_uuid}
                raise virt_inspector.NoDataException(msg)
        # memoryStats might launch an exception if the method is not supported
        # by the underlying hypervisor being used by libvirt.
        except libvirt.libvirtError as e:

            msg = _('Failed to inspect memory usage of %(instance_uuid)s, '
                    'can not get info from libvirt: %(error)s') % {
                'instance_uuid': instance_op_uuid, 'error': e}

            raise virt_inspector.NoDataException(msg)