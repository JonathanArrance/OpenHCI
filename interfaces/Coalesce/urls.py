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
        url(r'^nodes/(?P<node_name>\w+)/view/$',
            'coalesce.coal_beta.views.node_view',
            name='node_view'),


        url(r'^nodes/manage/$',
            'coalesce.coal_beta.views.manage_nodes',
            name='manage_nodes'),

        # --- Projects ----
        url(r'^projects/(?P<project_name>\w+)/view/$',
            'coalesce.coal_beta.views.project_view',
            name='project_view'),

        url(r'^projects/(?P<project_name>\w+)/user/(?P<user_name>\w+)/view/$',
            'coalesce.coal_beta.views.user_view',
            name='user_view'),


        url(r'^projects/manage/$',
            'coalesce.coal_beta.views.manage_projects',
            name='manage_projects'),
	
	# --- User actions ----
	url(r'^AJAX/create_user/(?P<username>[^/]+)/(?P<password>[^/]+)/(?P<userrole>[^/]+)/(?P<email>[^/]+)/(?P<project_name>[^/]+)/$',
	    'coalesce.coal_beta.views.ajax_create_user',
            name='create_user'),
	
	url(r'^AJAX/toggle_user/(?P<username>[^/]+)/(?P<toggle>[^/]+)/$',
	    'coalesce.coal_beta.views.ajax_toggle_user',
            name='toggle_user'),


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
            {'template_name': 'coal/change-password.html', 'post_change_redirect': '/'},
            name='change-password'),

        # admin views

        (r'^admin/', include(admin.site.urls)),


)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True }))

urlpatterns += staticfiles_urlpatterns()
