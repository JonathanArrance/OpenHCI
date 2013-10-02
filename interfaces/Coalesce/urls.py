from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

ROOT_PATH = settings.ROOT_PATH

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
        # views that are not customer specific
        # ====================================
        # these views may (should) take a request that may have a logged-in
        # user and make template descisions to customize based on the user
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
        url(r'^projects/(?P<project_id>\w+)/view/$',
            'coalesce.coal_beta.views.project_view',
            name='project_view'),


        url(r'^projects/manage/$',
            'coalesce.coal_beta.views.manage_projects',
            name='manage_projects'),

        # user account views
        # ==================
        url(r'^accounts/login/$',
            'django.contrib.auth.views.login',
            {'template_name': 'coal/login.html'},
            name='login'),

        url(r'^accounts/logout/$',
            'django.contrib.auth.views.logout',
            {'template_name': 'coal/logged_out.html'},
            name='logout'),

	    url(r'^accounts/change-password/$',
            'django.contrib.auth.views.password_change',
            {'template_name': 'coal/change-password.html', 'post_change_redirect': '/'},
            name='change-password'),

        # admin views
        # ===========
        # Uncomment the next line to enable the admin:
        (r'^admin/', include(admin.site.urls)),


)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True }))

urlpatterns += staticfiles_urlpatterns()
