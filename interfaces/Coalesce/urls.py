from django.conf.urls import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView

from django.conf.urls.static import static

ROOT_PATH = settings.ROOT_PATH

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

        url(r'^500.html$',
            TemplateView.as_view(template_name="500.html")),

        url(r'^404.html$',
            TemplateView.as_view(template_name="404.html")),

        url(r'^409.html$',
            TemplateView.as_view(template_name="409.html")),

        url(r'^$',
            'coalesce.coal_beta.views.dashboard',
            name='home'),

        url(r'^welcome/$',
            'coalesce.coal_beta.views.welcome',
            name='welcome'),

        url(r'^privacy-policy/$',
            'coalesce.coal_beta.views.privacy_policy',
            name='privacy-policy'),

        url(r'^terms-of-use/$',
            'coalesce.coal_beta.views.terms_of_use',
            name='terms-of-use'),

        url(r'^disclaimer/$',
            'coalesce.coal_beta.views.disclaimer',
            name='disclaimer'),

        url(r'^get_confirm/(?P<title>[^/]+)/(?P<message>[^/]+)/(?P<call>[^/]+)/(?P<notice>[^/]+)/(?P<refresh>[^/]+)/(?P<async>[^/]+)/$',
            'coalesce.coal_beta.views.get_confirm',
            name='get_confirm'),

        # --- Nodes ----

        url(r'^nodes/(?P<node_id>[-\w]+)/view/$',
            'coalesce.coal_beta.views.node_view',
            name='node_view'),

        url(r'^nodes/manage/$',
            'coalesce.coal_beta.views.manage_nodes',
            name='manage_nodes'),

        url(r'^nodes/get_stats/$',
            'coalesce.coal_beta.views.get_node_stats',
            name='get_node_stats'),

        url(r'^cloud/manage/$',
            'coalesce.coal_beta.views.manage_cloud',
            name='manage_cloud'),

        # --- Projects ----

        url(r'^projects/build/$',
            'coalesce.coal_beta.views.build_project',
            name='build_project'),

        url(r'^projects/get/build/$',
            'coalesce.coal_beta.views.get_build_project',
            name='get_build_project'),

        url(r'^projects/(?P<project_id>\w+)/view/$',
            'coalesce.coal_beta.views.project_view',
            name='project_view'),

        url(r'^projects/get_stats/$',
            'coalesce.coal_beta.views.get_project_stats',
            name='get_project_stats'),

        url(r'^projects/(?P<project_id>\w+)/get_project_panel/$',
            'coalesce.coal_beta.views.get_project_panel',
            name='get_project_panel'),

        url(r'^projects/(?P<project_id>\w+)/get_instance_panel/$',
            'coalesce.coal_beta.views.get_instance_panel',
            name='get_instance_panel'),

        url(r'^projects/(?P<project_id>\w+)/get_storage_panel/$',
            'coalesce.coal_beta.views.get_storage_panel',
            name='get_storage_panel'),

        url(r'^projects/(?P<project_id>\w+)/get_networking_panel/$',
            'coalesce.coal_beta.views.get_networking_panel',
            name='get_networking_panel'),


        # --- Quotas ----

        url(r'^projects/(?P<project_id>\w+)/get_project_quota/$',
            'coalesce.coal_beta.views.get_project_quota',
            name='get_project_quota'),

        url(r'^projects/(?P<project_id>\w+)/(?P<quota_settings>[^/]+)/set_project_quota/$',
            'coalesce.coal_beta.views.set_project_quota',
            name='set_project_quota'),

        url(r'^projects/(?P<project_id>\w+)/view/$',
            'coalesce.coal_beta.views.project_view',
            name='project_view'),

        url(r'^projects/(?P<project_id>\w+)/pu_project_view/$',
            'coalesce.coal_beta.views.pu_project_view',
            name='pu_project_view'),

        url(r'^projects/(?P<project_id>\w+)/basic_project_view/$',
            'coalesce.coal_beta.views.basic_project_view',
            name='basic_project_view'),

        url(r'^projects/(?P<project_id>\w+)/(?P<project_name>\w+)/delete/$',
            'coalesce.coal_beta.views.destroy_project',
            name='destroy_project'),

        url(r'^projects/manage/$',
            'coalesce.coal_beta.views.manage_projects',
            name='manage_projects'),

	# --- Instances ----
        url(r'^create_instance/(?P<instance_name>[^/]+)/(?P<sec_group_name>[^/]+)/(?P<avail_zone>[^/]+)/(?P<flavor_id>[^/]+)/(?P<sec_key_name>[^/]+)/(?P<image_id>[^/]+)/(?P<network_name>[^/]+)/(?P<project_id>[^/]+)/(?P<boot_from_vol>[^/]+)/(?P<volume_size>[^/]+)/(?P<volume_name>[^/]+)/(?P<volume_type>[^/]+)/$',
	    'coalesce.coal_beta.views.create_instance',
            name='create_instance'),

        url(r'^(?P<project_id>[^/]+)/list_servers/$',
            'coalesce.coal_beta.views.list_servers',
            name='list_servers'),

        url(r'^(?P<project_id>[^/]+)/list_servers_status/$',
            'coalesce.coal_beta.views.list_servers_status',
            name='list_servers'),

        url(r'^(?P<project_id>[^/]+)/(?P<server_id>[^/]+)/instance_view/$',
            'coalesce.coal_beta.views.instance_view',
            name='instance_view'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/pause_server/$',
            'coalesce.coal_beta.views.pause_server',
            name='pause_server'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/unpause_server/$',
            'coalesce.coal_beta.views.unpause_server',
            name='unpause_server'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/suspend_server/$',
            'coalesce.coal_beta.views.suspend_server',
            name='suspend_server'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/resume_server/$',
            'coalesce.coal_beta.views.resume_server',
            name='resume_server'),

	url(r'server/(?P<project_id>[^/]+)/(?P<server_id>[^/]+)/(?P<delete_boot_vol>[^/]+)/delete_instance/$',
	    'coalesce.coal_beta.views.delete_instance',
            name='delete_instance'),

        # url(r'server/(?P<project_id>[^/]+)/(?P<server_id>[^/]+)/get_server/$',
        #     'coalesce.coal_beta.views.get_server',
        #     name='get_server'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/(?P<flavor_id>[^/]+)/resize_server/$',
            'coalesce.coal_beta.views.resize_server',
            name='resize_server'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/confirm_resize/$',
            'coalesce.coal_beta.views.confirm_resize',
            name='confirm_resize'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/reboot/$',
            'coalesce.coal_beta.views.reboot',
            name='reboot'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/power_cycle/$',
            'coalesce.coal_beta.views.power_cycle',
            name='power_cycle'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/power_off_server/$',
            'coalesce.coal_beta.views.power_off_server',
            name='power_off_server'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/power_on_server/$',
            'coalesce.coal_beta.views.power_on_server',
            name='power_on_server'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/(?P<host_name>[^/]+)/live_migrate_server/$',
            'coalesce.coal_beta.views.live_migrate_server',
            name='live_migrate_server'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/migrate_server/$',
            'coalesce.coal_beta.views.migrate_server',
            name='migrate_server'),

        url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/(?P<host_name>[^/]+)/evacuate_server/$',
            'coalesce.coal_beta.views.evacuate_server',
            name='evacuate_server'),

        url(r'^server/(?P<snapshot_id>[^/]+)/delete_instance_snapshot/$',
            'coalesce.coal_beta.views.delete_instance_snapshot',
            name='delete_instance_snapshot'),

        # --- Images ----
        url(r'^import_local/(?P<image_name>[^/]+)/(?P<container_format>[^/]+)/(?P<disk_format>[^/]+)/(?P<image_type>[^/]+)/(?P<image_location>[^/]+)/(?P<visibility>[^/]+)/(?P<os_type>[^/]+)/(?P<progress_id>[^/]+)/$',
            'coalesce.coal_beta.views.import_local',
            name='import_local'),

        url(r'^import_remote/(?P<image_name>[^/]+)/(?P<container_format>[^/]+)/(?P<disk_format>[^/]+)/(?P<image_type>[^/]+)/(?P<image_location>[^/]+)/(?P<visibility>[^/]+)/(?P<os_type>[^/]+)/(?P<progress_id>[^/]+)/$',
            'coalesce.coal_beta.views.import_remote',
            name='import_remote'),

        url(r'^get_upload_progress/(?P<progress_id>[^/]+)/$',
            'coalesce.coal_beta.views.get_upload_progress',
            name='get_upload_progress'),

        url(r'^delete_image/(?P<project_id>[^/]+)/(?P<image_id>[^/]+)/$',
            'coalesce.coal_beta.views.delete_image',
            name='delete_image'),

        url(r'^create_instance_snapshot/(?P<project_id>[^/]+)/(?P<server_id>[^/]+)/(?P<snapshot_name>[^/]+)/(?P<snapshot_description>[^/]+)/$',
            'coalesce.coal_beta.views.create_instance_snapshot',
            name='create_instance_snapshot'),

        url(r'^revert_instance_snapshot/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/(?P<snapshot_id>[^/]+)/$',
            'coalesce.coal_beta.views.revert_instance_snapshot',
            name='revert_instance_snapshot'),

        # --- Floating IPs ----
        url(r'^floating_ip/(?P<floating_ip_id>[^/]+)/view/$',
            'coalesce.coal_beta.views.floating_ip_view',
            name='floating_ip_view'),

        url(r'^allocate_floating_ip/(?P<project_id>[^/]+)/(?P<ext_net_id>[^/]+)/$',
            'coalesce.coal_beta.views.allocate_floating_ip',
            name='allocate_floating_ip'),

        url(r'^deallocate_floating_ip/(?P<project_id>[^/]+)/(?P<floating_ip>[^/]+)/$',
            'coalesce.coal_beta.views.deallocate_floating_ip',
            name='deallocate_floating_ip'),

        url(r'^assign_floating_ip/(?P<floating_ip>[^/]+)/(?P<instance_id>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.assign_floating_ip',
            name='assign_floating_ip'),

        url(r'^unassign_floating_ip/(?P<floating_ip_id>[^/]+)/$',
            'coalesce.coal_beta.views.unassign_floating_ip',
            name='unassign_floating_ip'),

        # --- Volumes ----
        url(r'^projects/(?P<project_id>\w+)/volumes/(?P<volume_id>[^/]+)/view/$',
            'coalesce.coal_beta.views.volume_view',
            name='volume_view'),

        # REMOVED DESCRIPTION FOR NOW AS IT IS UNUSED
        url(r'^create_volume/(?P<volume_name>[^/]+)/(?P<volume_size>[^/]+)/(?P<volume_type>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.create_volume',
            name='create_volume'),

        url(r'^attach_volume/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/(?P<volume_id>[^/]+)/$',
            'coalesce.coal_beta.views.attach_volume',
            name='attach_volume'),

        url(r'^detach_volume/(?P<project_id>[^/]+)/(?P<volume_id>[^/]+)/$',
            'coalesce.coal_beta.views.detach_volume',
            name='detach_volume'),

        url(r'^delete_volume/(?P<volume_id>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.delete_volume',
            name='delete_volume'),

        # REMOVED DESCRIPTION FOR NOW AS IT IS UNUSED
        url(r'^create_vol_from_snapshot/(?P<project_id>[^/]+)/(?P<snapshot_id>[^/]+)/(?P<volume_size>[^/]+)/(?P<volume_name>[^/]+)/$',
            'coalesce.coal_beta.views.create_vol_from_snapshot',
            name='create_vol_from_snapshot'),

        # REMOVED DESCRIPTION FOR NOW AS IT IS UNUSED
        url(r'^create_vol_clone/(?P<project_id>[^/]+)/(?P<volume_id>[^/]+)/(?P<volume_name>[^/]+)/$',
            'coalesce.coal_beta.views.create_vol_clone',
            name='create_vol_clone'),

        url(r'^revert_volume_snapshot/(?P<project_id>[^/]+)/(?P<volume_id>[^/]+)/(?P<volume_name>[^/]+)/(?P<snapshot_id>[^/]+)/$',
            'coalesce.coal_beta.views.revert_volume_snapshot',
            name='revert_volume_snapshot'),

        # --- Snapshots ----
        url(r'^take_snapshot/(?P<snapshot_name>[^/]+)/(?P<snapshot_desc>[^/]+)/(?P<volume_id>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.take_snapshot',
            name='take_snapshot'),

        url(r'^create_snapshot/(?P<project_id>[^/]+)/(?P<name>[^/]+)/(?P<volume_id>[^/]+)/(?P<desc>[^/]+)/$',
            'coalesce.coal_beta.views.create_snapshot',
            name='create_snapshot'),

        url(r'^delete_snapshot/(?P<project_id>[^/]+)/(?P<snapshot_id>[^/]+)/$',
            'coalesce.coal_beta.views.delete_snapshot',
            name='delete_snapshot'),

        url(r'^snapshot/(?P<snapshot_id>[^/]+)/view/$',
            'coalesce.coal_beta.views.snapshot_view',
            name='snapshot_view'),

        # --- Containers ----
        url(r'^projects/(?P<project_id>\w+)/containers/(?P<container_name>[^/]+)/view/$',
            'coalesce.coal_beta.views.container_view',
            name='container_view'),

        url(r'^create_container/(?P<name>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.create_container',
            name='create_container'),

        url(r'^list_containers/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.list_containers',
            name='list_containers'),

        url(r'^delete_container/(?P<name>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.delete_container',
            name='delete_container'),

        # --- Container Objects ----

        url(r'^upload_local_object/(?P<container>[^/]+)/(?P<filename>[^/]+)/(?P<project_id>[^/]+)/(?P<project_name>[^/]+)/(?P<dummy1>[^/]+)/(?P<dummy2>[^/]+)/(?P<progress_id>[^/]+)/$',
            'coalesce.coal_beta.views.upload_local_object',
            name='upload_local_object'),

        url(r'^upload_remote_object/(?P<container>[^/]+)/(?P<url>[^/]+)/(?P<project_id>[^/]+)/(?P<project_name>[^/]+)/(?P<progress_id>[^/]+)/$',
            'coalesce.coal_beta.views.upload_remote_object',
            name='upload_remote_object'),

        url(r'^get_object/(?P<container>[^/]+)/(?P<filename>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.get_object',
            name='get_object'),

        url(r'^list_objects/(?P<container>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.list_objects',
            name='list_objects'),

        url(r'^delete_object/(?P<container>[^/]+)/(?P<filename>[^/]+)/(?P<project_id>[^/]+)/(?P<project_name>[^/]+)/$',
            'coalesce.coal_beta.views.delete_object',
            name='delete_object'),

        # --- Networks ----
        url(r'^network/(?P<net_id>[^/]+)/view/$',
            'coalesce.coal_beta.views.network_view',
            name='network_view'),

        url(r'^delete_private_network/(?P<project_id>[^/]+)/(?P<net_id>[^/]+)/$',
            'coalesce.coal_beta.views.remove_private_network',
            name='remove_private_network'),

        url(r'^add_private_network/(?P<net_name>[^/]+)/(?P<admin_state>[^/]+)/(?P<shared>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.add_private_network',
            name='add_private_network'),

        # --- Routers ----
        url(r'^create_router/(?P<router_name>[^/]+)/(?P<priv_net>[^/]+)/(?P<default_public>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.create_router',
            name='create_router'),

        url(r'^delete_router/(?P<project_id>[^/]+)/(?P<router_id>[^/]+)/$',
            'coalesce.coal_beta.views.delete_router',
            name='delete_router'),

        url(r'^router/(?P<router_id>[^/]+)/view/$',
            'coalesce.coal_beta.views.router_view',
            name='router_view'),

        # --- Users ----

        url(r'^user/(?P<project_name>\w+)/(?P<project_id>\w+)/(?P<user_name>\w+)/account_view/$',
            'coalesce.coal_beta.views.user_account_view',
            name='user_account_view'),

        url(r'^projects/(?P<project_name>\w+)/(?P<project_id>\w+)/user/(?P<user_name>\w+)/view/$',
            'coalesce.coal_beta.views.user_view',
            name='user_view'),

        url(r'^create_user/(?P<username>[^/]+)/(?P<password>[^/]+)/(?P<user_role>[^/]+)/(?P<email>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.create_user',
            name='create_user'),

        url(r'^add_existing_user/(?P<username>[^/]+)/(?P<user_role>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.add_existing_user',
            name='add_existing_user'),

        url(r'^toggle_user/(?P<username>[^/]+)/(?P<toggle>[^/]+)/$',
            'coalesce.coal_beta.views.toggle_user',
            name='toggle_user'),

        url(r'^delete_user/(?P<username>[^/]+)/(?P<userid>[^/]+)/$',
            'coalesce.coal_beta.views.delete_user',
            name='delete_user'),

        url(r'^remove_user_from_project/(?P<user_id>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.remove_user_from_project',
            name='remove_user_from_project'),

        url(r'^update_user_password/(?P<user_id>[^/]+)/(?P<current_password>[^/]+)/(?P<new_password>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.update_user_password',
            name='update_user_password'),

        url(r'^get_update_account_password/$',
            'coalesce.coal_beta.views.get_update_account_password',
            name='get_update_account_password'),

        # --- Security Groups ----
        url(r'^create_security_group/(?P<groupname>[^/]+)/(?P<groupdesc>[^/]+)/(?P<ports>[^/]+)/(?P<transport>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.create_security_group',
            name='create_security_group'),

        url(r'^delete_sec_group/(?P<sec_group_id>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.delete_sec_group',
            name='delete_sec_group'),

        url(r'^update_security_group/(?P<groupid>[^/]+)/(?P<project_id>[^/]+)/(?P<ports>[^/]+)/(?P<enable_ping>[^/]+)/(?P<transport>[^/]+)/$',
            'coalesce.coal_beta.views.update_security_group',
            name='update_security_group'),

        url(r'^security_group/(?P<groupid>[^/]+)/(?P<project_id>[^/]+)/view/$',
            'coalesce.coal_beta.views.security_group_view',
            name='security_group_view'),

        url(r'^create_sec_keys/(?P<key_name>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.create_keypair',
            name='create_keypair'),

        # --- Security Keys ----
        url(r'^key_pair/(?P<sec_key_id>[^/]+)/(?P<project_id>[^/]+)/view/$',
            'coalesce.coal_beta.views.key_view',
            name='key_view'),

        url(r'^key_pair/(?P<sec_key_name>[^/]+)/(?P<project_id>[^/]+)/delete/$',
            'coalesce.coal_beta.views.key_delete',
            name='key_delete'),

        url(r'^download_public_key/(?P<sec_key_id>[^/]+)/(?P<sec_key_name>[^/]+)/(?P<project_id>[^/]+)/$',
            'coalesce.coal_beta.views.download_public_key',
            name='download_public_key'),

        # --- 3rd Party Storage ----
        url(r'^supported_third_party_storage/$',
            'coalesce.coal_beta.views.supported_third_party_storage',
            name='supported_third_party_storage'),

        url(r'^third_party_storage/get/$',
            'coalesce.coal_beta.views.get_third_party_storage',
            name='get_third_party_storage'),

        url(r'^third_party_storage/get_license/(?P<provider>[^/]+)/$',
            'coalesce.coal_beta.views.get_third_party_storage_license',
            name='get_third_party_storage_license'),

        url(r'^third_party_storage/get_configure/(?P<provider>[^/]+)/$',
            'coalesce.coal_beta.views.get_third_party_storage_configure',
            name='get_third_party_storage_configure'),

        url(r'^third_party_storage/get_configure/(?P<provider>[^/]+)/(?P<update>[^/]+)/$',
            'coalesce.coal_beta.views.get_third_party_storage_configure',
            name='get_third_party_storage_configure'),

        # --- E-Series ---
        url(r'^eseries/get/$',
            'coalesce.coal_beta.views.eseries_get',
            name='eseries_get'),

        url(r'^eseries/delete/$',
            'coalesce.coal_beta.views.eseries_delete',
            name='eseries_delete'),

        url(r'^eseries/web_proxy_srv/set/(?P<pre_existing>[^/]+)/(?P<server>[^/]+)/(?P<srv_port>[^/]+)/(?P<transport>[^/]+)/(?P<login>[^/]+)/(?P<pwd>[^/]+)/$',
            'coalesce.coal_beta.views.eseries_set_web_proxy_srv',
            name='eseries_set_web_proxy_srv'),

        url(r'^eseries/controller/set/(?P<ctrl_ips>[^/]+)/$',
            'coalesce.coal_beta.views.eseries_set_controller',
            name='eseries_set_controller'),

        url(r'^eseries/controller/set/(?P<ctrl_ips>[^/]+)/(?P<ctrl_pwd>[^/]+|)/$',
            'coalesce.coal_beta.views.eseries_set_controller',
            name='eseries_set_controller'),

        url(r'^eseries/config/set/(?P<disk_pools>[^/]+)/$',
            'coalesce.coal_beta.views.eseries_set_config',
            name='eseries_set_config'),

	    url(r'^eseries/config/update/(?P<pre_existing>[^/]+)/(?P<server>[^/]+)/(?P<srv_port>[^/]+)/(?P<transport>[^/]+)/(?P<login>[^/]+)/(?P<pwd>[^/]+)/(?P<ctrl_ips>[^/]+)/(?P<disk_pools>[^/]+)/(?P<ctrl_pwd>[^/]+|)/$',
	        'coalesce.coal_beta.views.eseries_update',
            name='eseries_update'),

	    url(r'^eseries/config/update/(?P<pre_existing>[^/]+)/(?P<server>[^/]+)/(?P<srv_port>[^/]+)/(?P<transport>[^/]+)/(?P<login>[^/]+)/(?P<pwd>[^/]+)/(?P<ctrl_ips>[^/]+)/(?P<disk_pools>[^/]+)/$',
	        'coalesce.coal_beta.views.eseries_update',
            name='eseries_update'),

        url(r'^eseries/get/stats/$',
            'coalesce.coal_beta.views.eseries_stats',
            name='eseries_stats'),

        url(r'^eseries/license/set/(?P<license_key>[^/]+)/$',
            'coalesce.coal_beta.views.eseries_add_license',
            name='eseries_add_license'),

        # --- nfs ----
        url(r'^nfs/get/$',
            'coalesce.coal_beta.views.nfs_get',
            name='nfs_get'),

        url(r'^nfs/delete/$',
            'coalesce.coal_beta.views.nfs_delete',
            name='nfs_delete'),

        url(r'^nfs/set/(?P<mountpoints>[^/]+)/$',
            'coalesce.coal_beta.views.nfs_set',
            name='nfs_set'),

        url(r'^nfs/update/(?P<mountpoints>[^/]+)/$',
            'coalesce.coal_beta.views.nfs_update',
            name='nfs_update'),

        url(r'^nfs/license/set/(?P<license_key>[^/]+)/$',
            'coalesce.coal_beta.views.nfs_add_license',
            name='nfs_add_license'),

        # --- Nimble ---
	    url(r'^nimble/get/$',
	        'coalesce.coal_beta.views.nimble_get',
            name='nimble_get'),

	    url(r'^nimble/delete/$',
	        'coalesce.coal_beta.views.nimble_delete',
            name='nimble_delete'),

	    url(r'^nimble/set/(?P<server>[^/]+)/(?P<login>[^/]+)/(?P<pwd>[^/]+)/$',
	        'coalesce.coal_beta.views.nimble_set',
            name='nimble_set'),

	    url(r'^nimble/update/(?P<server>[^/]+)/(?P<login>[^/]+)/(?P<pwd>[^/]+)/$',
	        'coalesce.coal_beta.views.nimble_update',
            name='nimble_update'),

	    url(r'^nimble/license/set/(?P<license_key>[^/]+)/$',
	        'coalesce.coal_beta.views.nimble_add_license',
            name='nimble_add_license'),

	    url(r'^nimble/get/stats/$',
	        'coalesce.coal_beta.views.nimble_stats',
            name='nimble_stats'),

        # --- Metering ----
	    url(r'^metering/get/$',
	        'coalesce.coal_beta.views.get_metering',
            name='get_metering'),

        # --- Ceilometer Post Third Part Meter ----
        url(r'^ceilometer/post/meter/(?P<counter_type>[^/]+)/(?P<counter_name>[^/]+)/(?P<counter_volume>[^/]+)/(?P<counter_unit>[^/]+)/(?P<resource_id>[^/]+)/$',
            'coalesce.coal_beta.views.get_statistics',
            name='get_statistics'),

        # --- Ceilometer Statistics ----
        url(r'^ceilometer/get/statistics/(?P<ceil_start_time>[^/]+)/(?P<ceil_end_time>[^/]+)/(?P<ceil_meter_list>[^/]+)/$',
            'coalesce.coal_beta.views.get_statistics',
            name='get_statistics'),

        url(r'^ceilometer/get/statistics/(?P<ceil_start_time>[^/]+)/(?P<ceil_end_time>[^/]+)/(?P<ceil_meter_list>[^/]+)/(?P<ceil_tenant_id>[^/]+)/$',
            'coalesce.coal_beta.views.get_statistics',
            name='get_statistics'),

        url(r'^ceilometer/get/statistics/adminresource/(?P<ceil_start_time>[^/]+)/(?P<ceil_end_time>[^/]+)/(?P<ceil_meter_list>[^/]+)/(?P<ceil_resource_id>[^/]+)/$',
            'coalesce.coal_beta.views.get_statistics',
            name='get_statistics'),

        url(r'^ceilometer/get/statistics/(?P<ceil_start_time>[^/]+)/(?P<ceil_end_time>[^/]+)/(?P<ceil_meter_list>[^/]+)/(?P<ceil_tenant_id>[^/]+)/(?P<ceil_resource_id>[^/]+)/$',
            'coalesce.coal_beta.views.get_statistics',
            name='get_statistics'),

        url(r'^(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/instance_view/ceilometer/get/statistics/(?P<ceil_start_time>[^/]+)/(?P<ceil_end_time>[^/]+)/(?P<ceil_meter_list>[^/]+)/(?P<ceil_tenant_id>[^/]+)/(?P<ceil_resource_id>[^/]+)/$',
            'coalesce.coal_beta.views.get_statistics_for_instance',
            name='get_statistics_for_instance'),

        url(r'^ceilometer/get/meters/(?P<meter_group>[^/]+)/$',
            'coalesce.coal_beta.views.get_meters',
            name='get_meters'),

        # --- Version info ----
        url(r'^version/$',
            'coalesce.coal_beta.views.get_version',
            name='get_version'),

        # --- Setup ----
        url(r'^setup/$',
            'coalesce.coal_beta.views.setup',
            name='setup'),

        # --- Maintenance Information ----
        url(r'^phonehome/$',
            'coalesce.coal_beta.views.phonehome',
            name='phonehome'),

        url(r'^phonehome/getmsg/$',
            'coalesce.coal_beta.views.phonehome_msgs',
            name='phonehome_msgs'),

        url(r'^upgrade/$',
            'coalesce.coal_beta.views.upgrade',
            name='upgrade'),

        url(r'^upgrade/getmsg/$',
            'coalesce.coal_beta.views.upgrade_msgs',
            name='upgrade_msgs'),

        # --- User Account Views ----
        url(r'^login/$',
            'coalesce.coal_beta.views.login',
            name='login'),

        url(r'^coal/logout/$',
            'coalesce.coal_beta.views.logout',
            {'template_name': 'coal/welcome.html'},
            name='logout'),

        url(r'^coal/change-password/$',
            'coalesce.coal_beta.views.password_change',
            name='change-password'),

        url(r'^update_admin_password/(?P<current_password>[^/]+)/(?P<new_password>[^/]+)/$',
            'coalesce.coal_beta.views.update_admin_password',
            name='update_admin_password'),

        # --- Admin Views ----
        (r'^admin/', include(admin.site.urls)),

)+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True }))

urlpatterns += staticfiles_urlpatterns()
