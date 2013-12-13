# Django imports
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import Http404
from django.conf import settings
from django_tables2   import RequestConfig
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError
from django.db import connection
from django.views.decorators.cache import never_cache
from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_tenants import tenant_ops
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template.response import TemplateResponse

# Python imports
from datetime import datetime
from collections import defaultdict
import csv
# Custom imports
from coalesce.coal_beta.models import *
from coalesce.coal_beta.forms import *


def welcome(request):

    return render_to_response('coal/welcome.html', RequestContext(request, ))


def privacy_policy(request):
    return render_to_response('coal/privacy-policy.html', RequestContext(request,))

def disclaimer(request):
    return render_to_response('coal/website-disclaimer.html', RequestContext(request,))


def terms_of_use(request):
    return render_to_response('coal/terms-of-use.html', RequestContext(request,))



def node_view(request, node_name):
    node = Node.objects.get(name=node_name)
    return render_to_response('coal/node_view.html', RequestContext(request, {'node': node, }))

def manage_nodes(request):
    nodes = Node.objects.all()
    nodes_table = NodesTable(nodes)
    RequestConfig(request).configure(nodes_table)
    return render_to_response('coal/manage_nodes.html', RequestContext(request, {'nodes_table':nodes_table}))

def project_view(request, project_name):
    auth = request.session['auth']
    to = tenant_ops(auth)
    project = to.get_tenant(project_name)
    users=to.list_tenant_users(project_name)
    return render_to_response('coal/project_view.html', RequestContext(request, {'project': project, 'users': users}))


def manage_projects(request):
    projects = Project.objects.all()
    projects_table = ProjectsTable(projects)
    RequestConfig(request).configure(projects_table)
    return render_to_response('coal/manage_projects.html', RequestContext(request, { 'projects_table':projects_table}))


def setup(request):
    if request.method == 'POST':
        form = SetupForm(request.POST)
        if form.is_valid():
            management_ip = form.cleaned_data['management_ip']
            uplink_ip = form.cleaned_data['uplink_ip']
            min_vm_ip = form.cleaned_data['min_vm_ip']
            max_vm_ip = form.cleaned_data['max_vm_ip']
            cloud_name  = form.cleaned_data['cloud_name']
            single_node = form.cleaned_data['single_node']
            admin_password = form.cleaned_data['admin_password']
            admin_password_confirm = form.cleaned_data['admin_password_confirm']

            from coalesce.coal_beta.tasks import send_setup_info
            send_setup_info.delay(management_ip, uplink_ip, min_vm_ip, max_vm_ip, cloud_name, single_node, admin_password)

            if request.POST.get('cancel'):
                return HttpResponseRedirect('/')
            else:
                return render_to_response('coal/setup_results.html', RequestContext(request, {'cloud_name':cloud_name, 'management_ip': management_ip}))

    else:
        form = SetupForm()
    return render_to_response('coal/setup.html', RequestContext(request, { 'form':form, }))

# --- Media ---
def logo(request):
    image_data = open(r'%s\static\\transcirrus_weblogo.png' % settings.PROJECT_PATH, 'rb').read()

    return HttpResponse(image_data, mimetype="image/gif")

# --- Javascript ---
def jq(request):
    file = open(r'%s\javascripts\\jquery-latest.pack.js' % settings.PROJECT_PATH, 'rb').read()
    return HttpResponse(file, mimetype="text/javascript")

# ---- Authentication ---

@never_cache
def login_page(request, template_name):

    if request.method == "POST":
        form = authentication_form(request.POST)
        if form.is_valid():

            # Okay, security check complete. Log the user in.
            user = form.cleaned_data['username']
            pw = form.cleaned_data['password']
            a = authorization(user, pw)
            auth = a.get_auth()
            request.session['auth'] = auth
            print auth


            return render_to_response('coal/welcome.html', RequestContext(request, {  }))
    else:
        form = authentication_form()

        return render_to_response('coal/login.html', RequestContext(request, { 'form':form, }))

@never_cache
def logout(request, next_page=None,
           template_name='coal/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           current_app=None, extra_context=None):
    """
    Logs out the user and displays 'You are logged out' message.
    """
    auth_logout(request)

    if redirect_field_name in request.REQUEST:
        next_page = request.REQUEST[redirect_field_name]
        # Security check -- don't allow redirection to a different host.
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    if next_page:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page)

    current_site = get_current_site(request)
    context = {
        'site': current_site,
        'site_name': current_site.name,
        'title': ('Logged out')
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
        current_app=current_app)


@never_cache
def password_change(request):


        return render_to_response('coal/change-password.html', RequestContext(request, {  }))
