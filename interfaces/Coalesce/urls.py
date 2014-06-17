from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

ROOT_PATH = settings.ROOT_PATH

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

        url(r'^$',
            'coalesce.coal_beta.views.welcome',
            name='home'),

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

	url(r'^projects/(?P<project_id>\w+)/pu_project_view/$',
            'coalesce.coal_beta.views.pu_project_view',
            name='pu_project_view'),

        url(r'^projects/(?P<project_id>\w+)/basic_project_view/$',
            'coalesce.coal_beta.views.basic_project_view',
            name='basic_project_view'),

        url(r'^projects/(?P<project_id>\w+)/(?P<project_name>\w+)/delete/$',
            'coalesce.coal_beta.views.destroy_project',
            name='destroy_project'),

        url(r'^projects/(?P<project_name>\w+)/(?P<project_id>\w+)/user/(?P<user_name>\w+)/view/',
            'coalesce.coal_beta.views.user_view',
            name='user_view'),

        url(r'^projects/manage/$',
            'coalesce.coal_beta.views.manage_projects',
            name='manage_projects'),

        url(r'^projects/(?P<project_id>\w+)/volumes/(?P<volume_id>[^/]+)/view/$',
            'coalesce.coal_beta.views.volume_view',
            name='volume_view'),
        
	url(r'^import_image/(?P<image_name>[^/]+)/(?P<container_format>[^/]+)/(?P<disk_format>[^/]+)/(?P<image_type>[^/]+)/(?P<image_location>[^/]+)/(?P<visibility>[^/]+)/$',
	    'coalesce.coal_beta.views.import_image',
            name='import_image'),

	url(r'^delete_image/(?P<image_id>[^/]+)/$',
	    'coalesce.coal_beta.views.delete_image',
            name='delete_image'),

        url(r'^create_volume/(?P<volume_name>[^/]+)/(?P<volume_size>[^/]+)/(?P<description>[^/]+)/(?P<project_id>[^/]+)/$',
	    'coalesce.coal_beta.views.create_volume',
            name='create_volume'),

        url(r'^attach_volume/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/(?P<volume_id>[^/]+)/$',
        'coalesce.coal_beta.views.attach_volume',
            name='attach_volume'),

        url(r'^create_snapshot/(?P<project_id>[^/]+)/(?P<name>[^/]+)/(?P<volume_id>[^/]+)/(?P<desc>[^/]+)/$',
        'coalesce.coal_beta.views.create_snapshot',
            name='create_snapshot'),

        url(r'^delete_snapshot/(?P<project_id>[^/]+)/(?P<snapshot_id>[^/]+)/$',
        'coalesce.coal_beta.views.delete_snapshot',
            name='delete_snapshot'),

        url(r'^detach_volume/(?P<project_id>[^/]+)/(?P<volume_id>[^/]+)/$',
        'coalesce.coal_beta.views.detach_volume',
            name='detach_volume'),
	
	url(r'^delete_volume/(?P<volume_id>[^/]+)/(?P<project_id>[^/]+)/$',
        'coalesce.coal_beta.views.delete_volume',
            name='delete_volume'),

        url(r'^take_snapshot/(?P<snapshot_name>[^/]+)/(?P<snapshot_desc>[^/]+)/(?P<volume_id>[^/]+)/(?P<project_id>[^/]+)/$',
	    'coalesce.coal_beta.views.take_snapshot',
            name='take_snapshot'),

        url(r'^create_image/(?P<name>[^/]+)/(?P<sec_group_name>[^/]+)/(?P<avail_zone>[^/]+)/(?P<flavor_name>[^/]+)/(?P<sec_key_name>[^/]+)/(?P<image_name>[^/]+)/(?P<network_name>[^/]+)/(?P<project_id>[^/]+)/$',
	    'coalesce.coal_beta.views.create_image',
            name='create_image'),


	# --- Network stuff ----

	url(r'^network/(?P<net_id>[^/]+)/view/$',
	    'coalesce.coal_beta.views.network_view',
            name='network_view'),

	url(r'^delete_private_network/(?P<project_id>[^/]+)/(?P<net_id>[^/]+)/$',
	    'coalesce.coal_beta.views.remove_private_network',
            name='remove_private_network'),

	url(r'^add_private_network/(?P<net_name>[^/]+)/(?P<admin_state>[^/]+)/(?P<shared>[^/]+)/(?P<project_id>[^/]+)/$',
	    'coalesce.coal_beta.views.add_private_network',
            name='add_private_network'),

	url(r'^create_router/(?P<router_name>[^/]+)/(?P<priv_net>[^/]+)/(?P<default_public>[^/]+)/(?P<project_id>[^/]+)/$',
	    'coalesce.coal_beta.views.create_router',
            name='create_router'),

	url(r'^delete_router/(?P<project_id>[^/]+)/(?P<router_id>[^/]+)/$',
	    'coalesce.coal_beta.views.delete_router',
            name='delete_router'),

	url(r'^router/(?P<router_id>[^/]+)/view/$',
	    'coalesce.coal_beta.views.router_view',
            name='router_view'),

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

	# --- Server actions ----
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

	url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/(?P<host_name>[^/]+)/live_migrate_server/$',
	    'coalesce.coal_beta.views.live_migrate_server',
            name='live_migrate_server'),
	
	url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/migrate_server/$',
	    'coalesce.coal_beta.views.migrate_server',
            name='migrate_server'),

	url(r'server/(?P<project_id>[^/]+)/(?P<instance_id>[^/]+)/(?P<host_name>[^/]+)/evacuate_server/$',
	    'coalesce.coal_beta.views.evacuate_server',
            name='evacuate_server'),

	# --- User actions ----
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

	# --- Security actions ----
	url(r'^create_security_group/(?P<groupname>[^/]+)/(?P<groupdesc>[^/]+)/(?P<ports>[^/]+)/(?P<project_id>[^/]+)/$',
	    'coalesce.coal_beta.views.create_security_group',
            name='create_security_group'),

        url(r'^delete_sec_group/(?P<sec_group_id>[^/]+)/(?P<project_id>[^/]+)/$',
	    'coalesce.coal_beta.views.delete_sec_group',
            name='delete_sec_group'),

	url(r'^create_sec_keys/(?P<key_name>[^/]+)/(?P<project_id>[^/]+)/$',
	    'coalesce.coal_beta.views.create_keypair',
            name='create_keypair'),

	url(r'^key_pair/(?P<sec_key_id>[^/]+)/(?P<project_id>[^/]+)/view/$',
	    'coalesce.coal_beta.views.key_view',
            name='key_view'),

	url(r'^key_pair/(?P<sec_key_name>[^/]+)/(?P<project_id>[^/]+)/delete/$',
	    'coalesce.coal_beta.views.key_delete',
            name='key_delete'),

	url(r'^download_public_key/(?P<sec_key_id>[^/]+)/(?P<sec_key_name>[^/]+)/(?P<project_id>[^/]+)/$',
	    'coalesce.coal_beta.views.download_public_key',
            name='download_public_key'),

        # --- Setup ----
        url(r'^setup/$',
            'coalesce.coal_beta.views.setup',
            name='setup'),

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

        # admin views

        (r'^admin/', include(admin.site.urls)),


)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True }))

urlpatterns += staticfiles_urlpatterns()
