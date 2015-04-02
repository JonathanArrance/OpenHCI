from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.conf.urls.static import static

ROOT_PATH = settings.ROOT_PATH

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

        url(r'^$',
            'coalesce.coal_beta.views.welcome',
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


        # --- Nodes ----
        url(r'^nodes/(?P<node_id>[-\w]+)/view/$',
            'coalesce.coal_beta.views.node_view',
            name='node_view'),

        url(r'^nodes/manage/$',
            'coalesce.coal_beta.views.manage_nodes',
            name='manage_nodes'),

        url(r'^cloud/manage/$',
            'coalesce.coal_beta.views.manage_cloud',
            name='manage_cloud'),

        # --- Projects ----

        url(r'^projects/build/$',
            'coalesce.coal_beta.views.build_project',
            name='build_project'),

        url(r'^projects/(?P<project_id>\w+)/view/$',
            'coalesce.coal_beta.views.project_view',
            name='project_view'),

        #quotas
        url(r'^projects/(?P<project_id>\w+)/get_project_quota/$',
            'coalesce.coal_beta.views.get_project_quota',
            name='project_quota'),

        url(r'^projects/(?P<project_id>\w+)/set_project_quota/$',
            'coalesce.coal_beta.views.set_project_quota',
            name='project_quota'),

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
        url(r'^create_image/(?P<name>[^/]+)/(?P<sec_group_name>[^/]+)/(?P<avail_zone>[^/]+)/(?P<flavor_name>[^/]+)/(?P<sec_key_name>[^/]+)/(?P<image_name>[^/]+)/(?P<network_name>[^/]+)/(?P<project_id>[^/]+)/$',
	    'coalesce.coal_beta.views.create_image',
            name='create_image'),

    url(r'^(?P<project_id>[^/]+)/list_servers/$',
        'coalesce.coal_beta.views.list_servers',
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

	url(r'server/(?P<project_id>[^/]+)/(?P<server_id>[^/]+)/delete_server/$',
	    'coalesce.coal_beta.views.delete_server',
            name='delete_server'),

    # url(r'server/(?P<project_id>[^/]+)/(?P<server_id>[^/]+)/get_server/$',
    #     'coalesce.coal_beta.views.get_server',
    #         name='get_server'),

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

	url(r'^delete_image/(?P<image_id>[^/]+)/$',
	    'coalesce.coal_beta.views.delete_image',
            name='delete_image'),

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

        url(r'^create_volume/(?P<volume_name>[^/]+)/(?P<volume_size>[^/]+)/(?P<description>[^/]+)/(?P<volume_type>[^/]+)/(?P<project_id>[^/]+)/$',
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

        url(r'^projects/(?P<project_name>\w+)/(?P<project_id>\w+)/user/(?P<user_name>\w+)/view/',
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

	url(r'^update_user_password/(?P<user_id>[^/]+)/(?P<password>[^/]+)/(?P<project_id>[^/]+)/$',
	    'coalesce.coal_beta.views.update_user_password',
            name='update_user_password'),

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

	url(r'^eseries/get/$',
	    'coalesce.coal_beta.views.eseries_get',
            name='eseries_get'),

	url(r'^eseries/delete/$',
	    'coalesce.coal_beta.views.eseries_delete',
            name='eseries_delete'),

	url(r'^eseries/web_proxy_srv/set/(?P<pre_existing>[^/]+)/(?P<server>[^/]+)/(?P<srv_port>[^/]+)/(?P<transport>[^/]+)/(?P<login>[^/]+)/(?P<pwd>[^/]+)/$',
	    'coalesce.coal_beta.views.eseries_set_web_proxy_srv',
            name='eseries_set_web_proxy_srv'),

	url(r'^eseries/controller/set/(?P<ctrl_pwd>[^/]+)/(?P<ctrl_ips>[^/]+)/$',
	    'coalesce.coal_beta.views.eseries_set_controller',
            name='eseries_set_controller'),

	url(r'^eseries/config/set/(?P<disk_pools>[^/]+)/$',
	    'coalesce.coal_beta.views.eseries_set_config',
            name='eseries_set_config'),

        # --- Setup ----
        url(r'^setup/$',
            'coalesce.coal_beta.views.setup',
            name='setup'),

        # --- Maintenance stuff ----
        url(r'^phonehome/$',
            'coalesce.coal_beta.views.phonehome',
            name='phonehome'),

        url(r'^upgrade/(?P<version>[^/]+)/$',
            'coalesce.coal_beta.views.upgrade',
            name='upgrade'),

        # user account views
        url(r'^coal/login_page/$',
            'coalesce.coal_beta.views.login_page',
            {'template_name': 'coal/login.html'},
            name='login_page'),

        url(r'^coal/logout/$',
            'coalesce.coal_beta.views.logout',
            {'template_name': 'coal/logged_out.html'},
            name='logout'),

	    url(r'^coal/change-password/$',
            'coalesce.coal_beta.views.password_change',
            name='change-password'),

        url(r'^update_admin_password/(?P<password>[^/]+)/$',
	    'coalesce.coal_beta.views.update_admin_password',
            name='update_admin_password'),

        # admin views

        (r'^admin/', include(admin.site.urls)),


)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True }))

urlpatterns += staticfiles_urlpatterns()
