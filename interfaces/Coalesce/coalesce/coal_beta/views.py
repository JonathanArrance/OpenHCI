
# Django imports
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
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
from django.core import serializers
from django.utils import simplejson
from django.core.cache import cache

import time
import os
import sys

from transcirrus.common.auth import authorization
from transcirrus.common.stats import stat_ops
import transcirrus.common.node_stats as node_stats
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.nova.server import server_ops
from transcirrus.component.nova.storage import server_storage_ops
from transcirrus.component.nova.server_action import server_actions
from transcirrus.component.nova.admin_actions import server_admin_actions
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.cinder.cinder_volume import volume_ops
from transcirrus.component.cinder.cinder_snapshot import snapshot_ops
from transcirrus.component.glance.glance_ops_v2 import glance_ops
from transcirrus.component.nova.flavor import flavor_ops
from transcirrus.component.swift.container_services import container_service_ops
from transcirrus.component.swift.account_services import account_service_ops
from transcirrus.component.swift.object_services import object_service_ops
from transcirrus.component.nova.quota import quota_ops
from transcirrus.component.neutron.admin_actions import admin_ops
from transcirrus.operations.initial_setup import run_setup
import transcirrus.operations.build_complete_project as bcp
import transcirrus.operations.delete_server as ds
from transcirrus.operations.change_adminuser_password import change_admin_password
import transcirrus.common.util as util
import transcirrus.common.wget as wget
from transcirrus.database.node_db import list_nodes, get_node
import transcirrus.operations.destroy_project as destroy
import transcirrus.operations.resize_server as rs_server
import transcirrus.common.logger as logger

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib import messages


# Python imports
from datetime import datetime
from collections import defaultdict
import csv
import json
from urlparse import urlsplit

# Custom imports
#from coalesce.coal_beta.models import *
from coalesce.coal_beta.forms import *

cache_key = None

def welcome(request):
    try:
        auth = request.session['auth']
        if(auth != None and auth['is_admin'] == 1):
            #Cloud/Node stats
            stats = stat_ops(auth)
            ns = node_stats
            tot_users = stats.get_total_cloud_users()
            tot_proj = stats.get_num_project()
            full_stats = ns.node_stats()
            tot_nodes = len(full_stats)
            
            #Project stats
            to = tenant_ops(auth)
            so = server_ops(auth)
            l3 = layer_three_ops(auth)
            vo = volume_ops(auth)
            ao = account_service_ops(auth)
            no = neutron_net_ops(auth)

            tl = to.list_all_tenants()
            tenant_info = []
            for tenant in tl:
                servers = so.list_servers(tenant['project_id'])
                num_servers = len(servers)
                
                fips = l3.list_floating_ips(tenant['project_id'])
                num_fips = len(fips)
                
                volumes = vo.list_volumes(tenant['project_id'])
                num_vol = len(volumes)
                
                #containers = ao.get_account_info(tenant['project_id'])
                #num_cont = len(containers)
                #print num_cont
                num_cont = 0
                
                routers = l3.list_routers(tenant['project_id'])
                num_rout = len(routers)
                
                networks = no.list_internal_networks(tenant['project_id'])
                num_net = len(networks)
                
                users = to.list_tenant_users(tenant['project_id'])
                num_users = len(users)
                
                tenant_info.append({'project_name': tenant['project_name'],
                                    'num_servers': num_servers,
                                    'num_fips': num_fips,
                                    'num_vol': num_vol,
                                    'num_cont': num_cont,
                                    'num_rout': num_rout,
                                    'num_net': num_net,
                                    'num_users': num_users})
            
            return render_to_response('coal/stat_panel.html', RequestContext(request, {'full_stats': full_stats,
                                                                                       'tot_users': tot_users,
                                                                                       'tot_proj': tot_proj,
                                                                                       'tot_nodes': tot_nodes,
                                                                                       'tenant_info': tenant_info,}))
        else:
            return render_to_response('coal/welcome.html', RequestContext(request,))
        
    except Exception as e:
        print e
        return render_to_response('coal/welcome.html', RequestContext(request,))

def privacy_policy(request):
    return render_to_response('coal/privacy-policy.html', RequestContext(request,))

def disclaimer(request):
    return render_to_response('coal/website-disclaimer.html', RequestContext(request,))

def terms_of_use(request):
    return render_to_response('coal/terms-of-use.html', RequestContext(request,))

def node_view(request, node_id):
    node=get_node(node_id)
    return render_to_response('coal/node_view.html', RequestContext(request, {'node': node, }))

def manage_cloud(request):
    node_list = list_nodes()
    node_info = []
    auth = request.session['auth']
    to = tenant_ops(auth)
    project_list = to.list_all_tenants()
    project_info = []
    try:
        for node in node_list:
            nid = node['node_id']
            ni = get_node(nid)
            ni['node_id']= nid
            node_info.append(ni)
    except TypeError:
        pass
    try:
        for proj in project_list:
            pid = proj['project_id']
            dict={}
            pi = to.get_tenant(pid)
            project_info.append(pi)
    except:
        messages.warning(request, "Unable to manage cloud.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render_to_response('coal/manage_cloud.html', RequestContext(request, {'project_info': project_info, 'node_info': node_info}))

def manage_nodes(request):
    node_list = list_nodes()
    node_info = []
    try:
        for node in node_list:
            nid = node['node_id']
            ni = get_node(nid)
            ni['node_id']= nid
            node_info.append(ni)
    except:
        messages.warning(request, "Unable to manage nodes.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render_to_response('coal/manage_nodes.html', RequestContext(request, {'node_info': node_info,}))

def set_project_quota(request,quota_settings):
    """
    quota_settings - dictionary conating all of the settings to be updated.
    """
    auth = request.session['auth']
    ao = admin_ops(auth)
    qo = quota_ops(auth)
    proj = qo.get_project_quotas(quota_settings['project_id'])
    try:
        proj_out = qo.update_project_quotas(quota_settings)
        net_out = ao.update_net_quota(quota_settings)
        out = dict(proj_out.items() + net_out.items())
        out['status'] = 'success'
        out['message'] = "Quotas updated for %s."%(proj['project_name'])
    except Exception, e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def get_project_quota(request,project_id):
    auth = request.session['auth']
    ao = admin_ops(auth)
    qo = quota_ops(auth)
    try:
        proj_out = qo.get_project_quotas(project_id)
        net_out = ao.list_net_quota(project_id)
        out = dict(proj_out.items() + net_out.items())
        #may not have to return this in toastmessages
        out['status'] = 'success'
        out['message'] = "Quotas for %s."%(out['project_name'])
    except Exception, e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def manage_projects(request):
    auth = request.session['auth']
    to = tenant_ops(auth)
    project_list = to.list_all_tenants()
    project_info = []
    try:
        for proj in project_list:
            pid = proj['project_id']
            dict={}
            pi = to.get_tenant(pid)
            project_info.append(pi)
    except:
        messages.warning(request, "Unable to manage projects.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render_to_response('coal/manage_projects.html', RequestContext(request, {'project_info': project_info,}))

def project_view(request, project_id):
    auth = request.session['auth']
    to = tenant_ops(auth)
    so = server_ops(auth)
    no = neutron_net_ops(auth)
    l3o = layer_three_ops(auth)
    vo = volume_ops(auth)
    sno = snapshot_ops(auth)
    go = glance_ops(auth)
    ssa = server_admin_actions(auth)
    fo = flavor_ops(auth)
    cso = container_service_ops(auth)
    aso = account_service_ops(auth)

    project = to.get_tenant(project_id)
    users = to.list_tenant_users(project_id)
    userinfo = {}
    uo = user_ops(auth)

    for user in users:
        user_dict = {'username': user['username'], 'project_name': project['project_name']}
        user_info = uo.get_user_info(user_dict)
        userinfo[user['username']] = user_info

    ouserinfo = []
    try:
        ousers = uo.list_orphaned_users()
        if ousers:
            for ouser in ousers:
                ouserinfo.append(ouser['username'])
    except:
        ousers=[]

    priv_net_list = no.list_internal_networks(project_id)
    pub_net_list  = no.list_external_networks()
    routers       = l3o.list_routers(project_id)
    volumes       = vo.list_volumes(project_id)
    volume_info={}
    snapshots     = sno.list_snapshots(project_id)
    try:
        containers    = aso.get_account_containers(project_id)
    except:
        containers = []
    sec_groups    = so.list_sec_group(project_id)
    sec_keys      = so.list_sec_keys(project_id)
    instances     = so.list_servers(project_id)
    instance_info={}
    flavors       = fo.list_flavors()
    
    hosts=[]
    host_dict     = {'project_id': project_id, 'zone': 'nova'}
    hosts         = ssa.list_compute_hosts(host_dict)
    
    for volume in volumes:
        v_dict = {'volume_id': volume['volume_id'], 'project_id': project['project_id']}
        v_info = vo.get_volume_info(v_dict)
        vid = volume['volume_id']
        volume_info[vid] = v_info
    
    for instance in instances:
        i_dict = {'server_id': instance['server_id'], 'project_id': project['project_id']}
        try:
            i_info = so.get_server(i_dict)
            sname  = instance['server_name']
            instance_info[sname] = i_info
        except Exception:
            sys.exc_clear()
            i_info = {'server_os': '',
                      'server_key_name': '',
                      'server_group_name': '',
                      'server_zone': '',
                      'server_public_ips': {},
                      'server_id': '',
                      'server_name': instance['server_name'],
                      'server_status': u'BUILDING',
                      'server_node': '',
                      'server_int_net': {},
                      'server_net_id': '',
                      'server_flavor': ''}
            sname = instance['server_name']
            instance_info[sname] = i_info
            
    try:
        images    = go.list_images()
    except:
        images =[]

    private_networks={}
    for net in priv_net_list:
        try:
            private_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    public_networks={}
    for net in pub_net_list:
        try:
            public_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    try:
        default_public = public_networks.values()[0]['net_id'] # <<< THIS NEEDS TO CHANGE IF MULTIPLE PUB NETWORKS EXIST
    except:
        default_public = "NO PUBLIC NETWORK"

    floating_ips = l3o.list_floating_ips(project_id)
    for fip in floating_ips:
        if fip["floating_in_use"]:
            ip_info =l3o.get_floating_ip(fip['floating_ip_id'])
            fip['instance_name']=ip_info['instance_name']
        else:
            fip['instance_name']=''

    return render_to_response('coal/project_view.html',
                               RequestContext(request, {'project': project,
                                                        'users': users,
                                                        'ouserinfo': ouserinfo,
                                                        'userinfo':userinfo,
                                                        'sec_groups': sec_groups,
                                                        'sec_keys': sec_keys,
                                                        'private_networks': private_networks,
                                                        'public_networks': public_networks,
                                                        'default_public': default_public,
                                                        'priv_net_list':priv_net_list,
                                                        'pub_net_list':pub_net_list,
                                                        'routers': routers,
                                                        'floating_ips': floating_ips,
                                                        'hosts': hosts,
                                                        'volumes': volumes,
                                                        'volume_info': volume_info,
                                                        'snapshots': snapshots,
                                                        'containers': containers,
                                                        'images': images,
                                                        'instances': instances,
                                                        'instance_info': instance_info,
                                                        'flavors': flavors,
                                                        }))

def pu_project_view(request, project_id):
    auth = request.session['auth']
    to = tenant_ops(auth)
    so = server_ops(auth)
    no = neutron_net_ops(auth)
    l3o = layer_three_ops(auth)
    vo = volume_ops(auth)
    sno = snapshot_ops(auth)
    go = glance_ops(auth)
    fo = flavor_ops(auth)
    cso = container_service_ops(auth)
    aso = account_service_ops(auth)

    project = to.get_tenant(project_id)
    users = to.list_tenant_users(project_id)
    userinfo = {}
    uo = user_ops(auth)

    for user in users:
        user_dict = {'username': user['username'], 'project_name': project['project_name']}
        user_info = uo.get_user_info(user_dict)
        userinfo[user['username']] = user_info

    ouserinfo = []
    try:
        ousers = uo.list_orphaned_users()
        if ousers:
            for ouser in ousers:
                ouserinfo.append(ouser['username'])
    except:
        ousers=[]

    priv_net_list = no.list_internal_networks(project_id)
    pub_net_list  = no.list_external_networks()
    routers       = l3o.list_routers(project_id)
    volumes       = vo.list_volumes(project_id)
    volume_info={}
    snapshots     = sno.list_snapshots(project_id)
    try:
        containers    = aso.get_account_containers(project_id)
    except:
        containers = []
    sec_groups    = so.list_sec_group(project_id)
    sec_keys      = so.list_sec_keys(project_id)
    instances     = so.list_servers(project_id)
    instance_info={}
    flavors       = fo.list_flavors()
    
    for volume in volumes:
        v_dict = {'volume_id': volume['volume_id'], 'project_id': project['project_id']}
        v_info = vo.get_volume_info(v_dict)
        vid = volume['volume_id']
        volume_info[vid] = v_info
    
    for instance in instances:
        i_dict = {'server_id': instance['server_id'], 'project_id': project['project_id']}
        try:
            i_info = so.get_server(i_dict)
            sname  = instance['server_name']
            instance_info[sname] = i_info
        except Exception:
            sys.exc_clear()
            i_info = {'server_os': '',
                      'server_key_name': '',
                      'server_group_name': '',
                      'server_zone': '',
                      'server_public_ips': {},
                      'server_id': '',
                      'server_name': instance['server_name'],
                      'server_status': u'BUILDING',
                      'server_node': '',
                      'server_int_net': {},
                      'server_net_id': '',
                      'server_flavor': ''}
            sname = instance['server_name']
            instance_info[sname] = i_info
            
    try:
        images    = go.list_images()
    except:
        images =[]

    private_networks={}
    for net in priv_net_list:
        try:
            private_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    public_networks={}
    for net in pub_net_list:
        try:
            public_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    try:
        default_public = public_networks.values()[0]['net_id'] # <<< THIS NEEDS TO CHANGE IF MULTIPLE PUB NETWORKS EXIST
    except:
        default_public = "NO PUBLIC NETWORK"

    floating_ips = l3o.list_floating_ips(project_id)
    for fip in floating_ips:
        if fip["floating_in_use"]:
            ip_info =l3o.get_floating_ip(fip['floating_ip_id'])
            fip['instance_name']=ip_info['instance_name']
        else:
            fip['instance_name']=''

    return render_to_response('coal/project_view.html',
                               RequestContext(request, {'project': project,
                                                        'users': users,
                                                        'ouserinfo': ouserinfo,
                                                        'userinfo':userinfo,
                                                        'sec_groups': sec_groups,
                                                        'sec_keys': sec_keys,
                                                        'private_networks': private_networks,
                                                        'public_networks': public_networks,
                                                        'default_public': default_public,
                                                        'priv_net_list':priv_net_list,
                                                        'pub_net_list':pub_net_list,
                                                        'routers': routers,
                                                        'floating_ips': floating_ips,
                                                        'volumes': volumes,
                                                        'volume_info': volume_info,
                                                        'snapshots': snapshots,
                                                        'containers': containers,
                                                        'images': images,
                                                        'instances': instances,
                                                        'instance_info': instance_info,
                                                        'flavors': flavors
                                                        }))
def basic_project_view(request, project_id):
    auth = request.session['auth']
    to = tenant_ops(auth)
    project = to.get_tenant(project_id)
    vo = volume_ops(auth)
    go = glance_ops(auth)
    so = server_ops(auth)
    l3o = layer_three_ops(auth)
    no = neutron_net_ops(auth)
    fo = flavor_ops(auth)
    volumes       = vo.list_volumes(project_id)
    volume_info={}
    sec_groups    = so.list_sec_group(project_id)
    sec_keys      = so.list_sec_keys(project_id)
    instances     = so.list_servers(project_id)
    flavors       = fo.list_flavors()
    #pub_net_list  = no.list_external_networks()

    for volume in volumes:
        v_dict = {'volume_id': volume['volume_id'], 'project_id': project['project_id']}
        v_info = vo.get_volume_info(v_dict)
        vid = volume['volume_id']
        volume_info[vid] = v_info
    
    priv_net_list = no.list_internal_networks(project_id)
    private_networks={}
    for net in priv_net_list:
        try:
            private_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass



    instance_info={}
    for instance in instances:
        i_dict = {'server_id': instance['server_id'], 'project_id': project['project_id']}
        try:
            i_info = so.get_server(i_dict)
            sname  = instance['server_name']
            instance_info[sname] = i_info
        except Exception:
            sys.exc_clear()
            i_info = {'server_os': '',
                      'server_key_name': '',
                      'server_group_name': '',
                      'server_zone': '',
                      'server_public_ips': {},
                      'server_id': '',
                      'server_name': instance['server_name'],
                      'server_status': u'BUILDING',
                      'server_node': '',
                      'server_int_net': {},
                      'server_net_id': '',
                      'server_flavor': ''}
            sname = instance['server_name']
            instance_info[sname] = i_info

    try:
        images    = go.list_images()
    except:
        images =[]

    floating_ips = l3o.list_floating_ips(project_id)
    for fip in floating_ips:
        if fip["floating_in_use"]:
            ip_info =l3o.get_floating_ip(fip['floating_ip_id'])
            fip['instance_name']=ip_info['instance_name']
        else:
            fip['instance_name']=''

    pub_net_list  = no.list_external_networks()

    public_networks={}
    for net in pub_net_list:
        try:
            public_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    try:
        default_public = public_networks.values()[0]['net_id'] # <<< THIS NEEDS TO CHANGE IF MULTIPLE PUB NETWORKS EXIST
    except:
        default_public = "NO PUBLIC NETWORK"

    """
1. create a vm
2. provision a new volume
3. upload download delete swift objects
4. add available floating ip to an instance
5. remove a floating ip from an instance
we need to build a function to request a vm resize
6. delete a vm that they own
7. confirm resize of an instance
8. revert instance back to original size
9. get the status of the instance
10. get the novnc console of an instance
3. delete volumes they own
11 attach volumes to
12 detach vols from instances they own
13 update their password
14. list the vms they own






    sno = snapshot_ops(auth)


    project = to.get_tenant(project_id)
    users = to.list_tenant_users(project_id)
    userinfo = {}
    uo = user_ops(auth)

    for user in users:
        user_dict = {'username': user['username'], 'project_name': project['project_name']}
        user_info = uo.get_user_info(user_dict)
        userinfo[user['username']] = user_info

    try:
        ousers = uo.list_orphaned_users()
    except:
        raise

    ouserinfo = []
    if ousers:
        for ouser in ousers:
            ouserinfo.append(ouser['username'])


    pub_net_list  = no.list_external_networks()
    routers       = l3o.list_routers(project_id)

    snapshots     = sno.list_snapshots(project_id)



    private_networks={}
    for net in priv_net_list:
        try:
            private_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    public_networks={}
    for net in pub_net_list:
        try:
            public_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    try:
        default_public = public_networks.values()[0]['net_id'] # <<< THIS NEEDS TO CHANGE IF MULTIPLE PUB NETWORKS EXIST
    except:
        default_public = "NO PUBLIC NETWORK"


    """

    return render_to_response('coal/basic_project_view.html',
                               RequestContext(request, {'project': project,
                                                        'sec_groups': sec_groups,
                                                        'sec_keys': sec_keys,
                                                        'volumes': volumes,
                                                        'volume_info':volume_info,
                                                        'images': images,
                                                        'instances': instances,
                                                        'instance_info': instance_info,
                                                        'floating_ips': floating_ips,
                                                        'private_networks': private_networks,
                                                        'public_networks': public_networks,
                                                        'priv_net_list':priv_net_list,
                                                        'pub_net_list':pub_net_list,
                                                        'flavors': flavors
                                                        }))

def user_view(request, project_name, project_id, user_name):
    auth = request.session['auth']
    uo = user_ops(auth)
    user_dict = {'username': user_name, 'project_name': project_name}
    user_info = uo.get_user_info(user_dict)

    return render_to_response('coal/user_view.html',
                               RequestContext(request, {'project_name': project_name,
                                                        'current_project_id': project_id,
                                                        'user_info': user_info,
                                                 }))

def key_view(request, sec_key_id, project_id):
    auth = request.session['auth']
    so = server_ops(auth)
    key_dict = {'sec_key_id': sec_key_id, 'project_id': project_id}
    key_info = so.get_sec_keys(key_dict)

    return render_to_response('coal/key_view.html',
                               RequestContext(request, {
                                                        'key_info': key_info,
                                                        'current_project_id': project_id
                                                        }))


def key_delete(request, sec_key_name, project_id):

    try:
        auth = request.session['auth']
        so = server_ops(auth)
        key_dict = {'sec_key_name': sec_key_name, 'project_id': project_id}
        out = so.delete_sec_keys(key_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to delete key pair.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    
    return render_to_response('coal/key_view.html',
                               RequestContext(request, {
                                                        'key_info': key_info,
                                                        'project_id': project_id
                                                        }))



def download_public_key(request, sec_key_id, sec_key_name, project_id):
    auth = request.session['auth']
    so = server_ops(auth)
    key_dict = {'sec_key_id': sec_key_id, 'project_id': project_id}
    key_info = so.get_sec_keys(key_dict)
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename="%s.pem"' % sec_key_name
    response.write(key_info['public_key'])
    return response

def attach_server_to_network(request, server_id, project_id, net_id):
    auth = request.session['auth']
    so = server_ops(auth)

    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    return HttpResponseRedirect(redirect_to)

def volume_view(request, project_id, volume_id):
    auth = request.session['auth']
    vo = volume_ops(auth)
    sno = snapshot_ops(auth)
    so = server_ops(auth)
    instances = so.list_servers(project_id)
    snapshots = sno.list_snapshots()
    vol_dict = {'project_id': project_id, 'volume_id': volume_id}
    volume_info = vo.get_volume_info(vol_dict)
    attached_to = None
    if volume_info['volume_instance']:
        server_dict = {'project_id': project_id, 'server_id': volume_info['volume_instance']}
        attached_to = so.get_server(server_dict)

    return render_to_response('coal/volume_view.html',
                               RequestContext(request, {'current_project_id' : project_id,
                                                        'volume_info': volume_info,
                                                        'snapshots': snapshots,
                                                        'attached_to': attached_to,
                                                        'instances': instances,
                                                        }))

def floating_ip_view(request, floating_ip_id):
    auth = request.session['auth']
    l3o = layer_three_ops(auth)
    fip = l3o.get_floating_ip(floating_ip_id)
    so = server_ops(auth)
    instances = so.list_servers(fip['project_id'])

    return render_to_response('coal/floating_ip_view.html',
                               RequestContext(request, {
                                                        'fip': fip,
                                                        'instances': instances,
                                                 }))

def create_user(request, username, password, user_role, email, project_id):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'password':password, 'user_role':user_role, 'email': email, 'project_id': project_id}
        newuser= uo.create_user(user_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to create user.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_security_group(request, groupname, groupdesc, ports, project_id):
    try:
        portstrings    = ports.split(',')
        portlist = []
        for port in portstrings:
            portlist.append(int(port))
        auth = request.session['auth']
        so = server_ops(auth)
        create_sec = {'group_name': groupname, 'group_desc':groupdesc, 'ports': portlist, 'project_id': project_id}
        newgroup= so.create_sec_group(create_sec)
        return HttpResponseRedirect("/projects/manage")
    except:
        messages.warning(request, "Unable to create security group.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def delete_sec_group(request, sec_group_id, project_id):
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        sec_dict = {'sec_group_id': sec_group_id, 'project_id':project_id}
        so.delete_sec_group(sec_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        messages.warning(request, "Unable to delete security group.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_keypair(request, key_name, project_id):
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        key_dict = {'key_name': key_name, 'project_id': project_id}
        newkey= so.create_sec_keys(key_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        response = HttpResponseRedirect(redirect_to)
        return render_to_response(response)
    except:
        messages.warning(request, "Unable to create keypair.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Import a local (user's laptop) image and add it to glance & database. The image has already been uploaded via the broswer
# to memory or a temp file so we just need to transfer the contents to a file we control.
def import_local (request, image_name, container_format, disk_format, image_type, image_location, visibility, progress_id):
    from coalesce.coal_beta.models import ImportLocal

    try:
        auth = request.session['auth']
        go = glance_ops(auth)

        # Create a temp file to hold the image contents until we give it to glance.
        download_dir   = "/var/lib/glance/images/"
        download_fname = time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".img"
        download_file  = download_dir + download_fname

        # Transfer the content from the temp location to our own file.
        try:
            with open(download_file, 'wb+') as destination:
                for chunk in request.FILES['import_local'].chunks():
                    destination.write(chunk)
        except Exception as e:
            out = {'status' : "error", 'message' : "Error opening local file: %s" % e}
            return HttpResponse(simplejson.dumps(out))

        # Add the image to glance and the database.
        import_dict = {'image_name': image_name, 'container_format': container_format, 'image_type': image_type, 'disk_format': disk_format, 'visibility': visibility, 'image_location': ""}
        import_dict['image_location'] = download_file
        out = go.import_image(import_dict)
        out['status'] = "success"
        out['message'] = "Local image %s was uploaded." % image_name
    except Exception as e:
        out = {'status' : "error", 'message' : "Error uploading local file: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Callback function used to track the progress of a remote upload. The current amount uploaded and total size of the file is
# placed in a cache record so it can be retrieved later. The width param is not used and False must be returned.
# TODO: A global cache_key is used and should be replaced with something else.
def download_progress (current_size, total_size, width):
    global cache_key
    if cache_key:
        data = cache.get(cache_key)
        data['uploaded'] = current_size
        data['length'] = total_size
        cache.set(cache_key, data)
    return (False)


# Import a remote image and add it to glance & database. The image is retrieved via a wget like interface.
# TODO: A global cache_key is used and should be replaced with something else.
def import_remote (request, image_name, container_format, disk_format, image_type, image_location, visibility, progress_id):
    global cache_key
    try:
        auth = request.session['auth']
        go = glance_ops(auth)
        import_dict = {'image_name': image_name, 'container_format': container_format, 'image_type': image_type, 'disk_format': disk_format, 'visibility': visibility, 'image_location': ""}

        # Replace any '%47' with a slash '/'
        image_location = image_location.replace("&47", "/")

        # Setup our cache to track the progress.
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        cache.set (cache_key, {'length': 0, 'uploaded' : 0})

        # Use wget to download the file.
        download_dir   = "/var/lib/glance/images/"
        download_fname = time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".img"
        download_file  = download_dir + download_fname

        # Download the file via a wget like interface to the file called download_file and
        # log the progress via the callback function download_progress.
        filename, content_type = wget.download (image_location, download_file, download_progress)

        # Delete our cached progress.
        cache.delete(cache_key)
        cache_key = None

        # Add the image to glance and the database.
        import_dict['image_location'] = download_file
        out = go.import_image(import_dict)
        out['status'] = "success"
        out['message'] = "Remote image %s was uploaded." % image_name
    except Exception as e:
        cache.delete(cache_key)
        cache_key = None
        out = {'status' : "error", 'message' : "Error uploading remote file: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Return the progress of an operation (most likely an image upload) via its progress id.
def get_upload_progress (request, progress_id):
    try:
        auth = request.session['auth']
        go = glance_ops(auth)
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        out = cache.get(cache_key)
        if out == None:
            # No cache entry so the upload is done so we need to indicate that by setting uploaded & length to -1.
            out = {'uploaded' : -1, 'length' : -1}
        out['status'] = "success"
    except Exception as e:
        out = {'status' : "error", 'message' : "Error getting upload progress: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Delete an image by it's image id.
def delete_image (request, image_id):
    try:
        auth = request.session['auth']
        go = glance_ops(auth)
        out = go.delete_image(image_id)

        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except:
        messages.warning(request, "Unable to create volume.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        ##out['status'] = "success"
        ##out['message'] = "Image was deleted."
    ##except Exception, e:
        ##out = {'status' : "error", 'message' : "Error deleting image: %s" % e}
    ##return HttpResponse(simplejson.dumps(out))

def create_volume(request, volume_name, volume_size, description, volume_type, project_id):
    out = {}
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        create_vol = {'volume_name': volume_name, 'volume_size': volume_size, 'description': description, 'volume_type': volume_type, 'project_id': project_id}
        out = vo.create_volume(create_vol)
        out['status'] = 'success'
        out['message'] = "Volume %s was created."%(volume_name)
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def delete_volume(request, volume_id, project_id):
    #needs to have ajax delete call finished.
    output = {}
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        delete_vol = {'volume_id': volume_id, 'project_id': project_id}
        name = vo.get_volume_info(delete_vol)
        out = vo.delete_volume(delete_vol)
        if(out == 'OK'):
            output['status'] = 'success'
            output['message'] = "Volume %s was deleted."%(name['volume_name'])
    except Exception as e:
        output = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(output))

def list_volumes(request,project_id):
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        #List vols is an array
        out = vo.list_volumes(project_id)
        out['status'] = 'success'
        out['message'] = "Volume list returned for %s."%(project_id)
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def attach_volume(request, project_id, instance_id, volume_id):
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        sso = server_storage_ops(auth)
        attach_vol = {'project_id': project_id, 'instance_id': instance_id, 'volume_id': volume_id, 'mount_point': "/dev/vdc"}
        att = sso.attach_vol_to_server(attach_vol)
        get_vol = {'project_id': project_id, 'volume_id': volume_id}
        out = vo.get_volume_info(get_vol)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        messages.warning(request, 'The volume %s has been attached to %s'%(out['volume_name'],out['volume_instance_name']))
        #return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return HttpResponse(out)
    except Exception as e:
        messages.warning(request, "%s"%(e))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def detach_volume(request, project_id, volume_id):
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        sso = server_storage_ops(auth)
        v_dict = {'volume_id': volume_id, 'project_id': project_id}
        v_info = vo.get_volume_info(v_dict)
        detach_vol = {'project_id': project_id, 'instance_id': v_info['volume_instance'], 'volume_id': volume_id}
        out = sso.detach_vol_from_server(detach_vol)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        #messages.warning(request, 'Volume %s has been detached from .'%(v_info['volume_name'],v_info['volume_instance_name']))
        #return HttpResponseRedirect(redirect_to)
        return HttpResponse(simplejson.dumps(out))
    except Exception as e:
        messages.warning(request, "%s"%(e))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_snapshot(request, project_id, name, volume_id, desc):
    try:
        auth = request.session['auth']
        sno = snapshot_ops(auth)
        create_snap = {'project_id': project_id, 'snapshot_name': name, 'volume_id': volume_id, 'snapshot_desc': desc}
        out = sno.create_snapshot(create_snap)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        messages.warning(request, 'The snapshot %s has been created for volume id %s'%(name,volume_id))
        return HttpResponseRedirect(redirect_to)
    except Exception as e:
        messages.warning(request, "%s"%(e))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def delete_snapshot(request, project_id, snapshot_id):
    try:
        auth = request.session['auth']
        sno = snapshot_ops(auth)
        delete_snap = {'project_id': project_id, 'snapshot_id': snapshot_id}
        out = sno.delete_snapshot(delete_snap)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        messages.warning(request, 'The snapshot with id %s has been deleted.'%(snapshot_id))
        return HttpResponseRedirect(redirect_to)
    except Exception as e:
        messages.warning(request, "%s"%(e))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_router(request, router_name, priv_net, default_public, project_id):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        no = neutron_net_ops(auth)
        netinfo = no.get_network(priv_net)
        subnet = netinfo["net_subnet_id"][0]['subnet_id']

        create_router = {'router_name': router_name, 'project_id': project_id}
        router = l3o.add_router(create_router)

        add_dict = {'router_id': router['router_id'], 'ext_net_id': default_public, 'project_id': project_id}
        l3o.add_router_gateway_interface(add_dict)

        internal_dict = {'router_id': router['router_id'], 'project_id': project_id, 'subnet_id': subnet}
        l3o.add_router_internal_interface(internal_dict)

        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except Exception as e:
        messages.warning(request, "%s"%(e))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def delete_router(request, project_id, router_id):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        router=l3o.get_router(router_id)
        proj_rout_dict = {'router_id': router_id, 'project_id': project_id}
        l3o.delete_router_gateway_interface(proj_rout_dict)
        subnet_id=router["router_int_sub_id"]
        if subnet_id:
            remove_dict = {'router_id': router_id, 'subnet_id': subnet_id, 'project_id': project_id}
            l3o.delete_router_internal_interface(remove_dict)
        l3o.delete_router(proj_rout_dict)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except:
        messages.warning(request, "Unable to delete router.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def destroy_project(request, project_id, project_name):
    try:
        auth = request.session['auth']
        proj_dict = {'project_name': project_name, 'project_id': project_id, 'keep_users': False}
        des_proj = destroy.destroy_project(auth, proj_dict)
        print des_proj
        return HttpResponseRedirect('/')

    except:
        messages.warning(request, "Unable to destroy project.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def allocate_floating_ip(request, project_id, ext_net_id):
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        input_dict = {'ext_net_id': ext_net_id, 'project_id': project_id}
        l3o.allocate_floating_ip(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to allocate IP.  The IP range may be used up.")
        return HttpResponseRedirect(redirect_to)

def deallocate_floating_ip(request, project_id, floating_ip):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        input_dict = {'floating_ip': floating_ip, 'project_id': project_id}
        l3o.deallocate_floating_ip(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to deallocate floating ip.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def list_floating_ip(request,project_id):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        #array of dictionary
        out = l3o.list_floating_ips(project_id)
        out['status'] = 'success'
        out['message'] = "Floating ips %s returned."%(project_id)
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def take_snapshot(request, snapshot_name, snapshot_desc, volume_id, project_id):
    try:
        auth = request.session['auth']
        sno = snapshot_ops(auth)
        create_snap = {'snapshot_name': snapshot_name, 'snapshot_desc': snapshot_desc, 'volume_id': volume_id, 'project_id': project_id}
        sno.create_snapshot(create_snap)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to take snapshots.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_vm_spec(request,name,ram,boot_disk,cpus,swap=None,ephemeral=None,public=None,description=None):
    try:
        auth = request.session['auth']
        fo = flavor_ops(auth)
        input_dict = {'name':name,'ram':ram,'boot_disk':boot_disk,'cpus':cpus}
        if(swap):
            input_dict['swap'] = swap
        if(ephemeral):
            input_dict['ephemeral'] = ephemeral
        if(public):
            input_dict['public'] = public
        if(description):
            input_dict['description'] = description
        out = fo.create_flavor(input_dict)
        out['status'] = 'success'
        out['message'] = "New vm spec %s created."%(name)
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))
        

def delete_vm_spec(request,flavor_id):
    output = {}
    try:
        auth = request.session['auth']
        fo = flavor_ops(auth)
        spec = fo.get_flavor(flavor_id)
        out = fo.delete_flavor(flavor_id)
        if(out == 'OK'):
            output['status'] = 'success'
            output['message'] = "Vm spec %s deleted."%(spec['flavor_name'])
    except Exception as e:
        output = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(output))

def create_image(request, name, sec_group_name, avail_zone, flavor_name, sec_key_name, image_name, network_name, project_id):
    #this is used to create new instance. Not sure why it is called create image
    #if(amount is None):
    #    amount = '1'
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        no = neutron_net_ops(auth)
        instance = {    'project_id':project_id, 'sec_group_name':sec_group_name,
                        'avail_zone':avail_zone, 'sec_key_name': sec_key_name,
                        'network_name': network_name,'image_name': image_name,
                        'flavor_name':flavor_name, 'name':name}
        out = so.create_server(instance)
        priv_net_list = no.list_internal_networks(project_id)
        default_priv = priv_net_list[0]['net_id']
        input_dict = {'server_id':out['vm_id'], 'net_id': default_priv, 'project_id': project_id}
        net_info = so.attach_server_to_network(input_dict)
        out['server_info']= so.get_server(input_dict)
        out['status'] = 'success'
        out['message'] = "New server %s was created."%(out['vm_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))


# def get_server(request, project_id, instance_id):
#    try:
#        auth = request.session['auth']
#        so = server_ops(auth)
#        input_dict = {'project_id':project_id, 'instance_id':instance_id}
#        out = so.get_server(input_dict)
#        out['status'] = 'success'
#        out['message'] = 'Successfully retrieved instance %s info.'%(serv_info['server_name'])
#    except Exception as e:
#        out = {"status":"error","message":"%s"%(e)}
#        return HttpResponse(simplejson.dumps(out))

def list_servers(request,project_id):
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        #array of dictionaries
        out = so.list_servers(project_id)
        out['status'] = 'success'
        out['message'] = "Server list returned for %s."%(project_id)
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

'''
def pause_server(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'instance_id':instance_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        saa.pause_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to pause server.")
        return HttpResponseRedirect(redirect_to)
'''

def pause_server(request, project_id, instance_id):
    out = {}
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        so = server_ops(auth)
        input_dict = {'project_id':project_id, 'instance_id':instance_id, 'server_id':instance_id}
        serv_info = so.get_server(input_dict)
        pause = saa.pause_server(input_dict)
        if(pause == 'OK'):
            out['status'] = 'success'
            out['message'] = 'Successfully paused instance %s.'%(serv_info['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

'''
def unpause_server(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'instance_id':instance_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        saa.unpause_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to unpause server.")
        return HttpResponseRedirect(redirect_to)
'''
def unpause_server(request, project_id, instance_id):
    out = {}
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        so = server_ops(auth)
        #input_dict = {'project_id':project_id, 'instance_id':instance_id}
        input_dict = {'project_id':project_id, 'instance_id':instance_id, 'server_id':instance_id}
        serv_info = so.get_server(input_dict)
        unpause = saa.unpause_server(input_dict)
        if(unpause == 'OK'):
            out['status'] = 'success'
            out['message'] = 'Successfully unpaused instance %s.'%(serv_info['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

'''
def suspend_server(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'instance_id':instance_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        saa.suspend_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to suspend server.")
        return HttpResponseRedirect(redirect_to)
'''

def suspend_server(request, project_id, instance_id):
    out = {}
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        so = server_ops(auth)
        input_dict = {'project_id':project_id, 'instance_id':instance_id, 'server_id':instance_id}
        suspend = saa.suspend_server(input_dict)
        serv_info = so.get_server(input_dict)
        if(suspend == 'OK'):
            out['status'] = 'success'
            out['message'] = 'Successfully suspended instance %s.'%(serv_info['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

'''
def resume_server(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'instance_id':instance_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        saa.resume_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to resume server.")
        return HttpResponseRedirect(redirect_to)
'''

def resume_server(request, project_id, instance_id):
    out = {}
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        so = server_ops(auth)
        input_dict = {'project_id':project_id, 'instance_id':instance_id, 'server_id':instance_id}
        resume = saa.resume_server(input_dict)
        serv_info = so.get_server(input_dict)
        if(resume == 'OK'):
            out['status'] = 'success'
            out['message'] = 'Successfully resumed instance %s.'%(serv_info['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

"""
def delete_server(request, project_id, server_id):
    input_dict = {'project_id':project_id, 'server_id':server_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        del_serv = ds.delete_server(auth, input_dict)
        return HttpResponseRedirect(redirect_to)
    except Exception as e:
        messages.warning(request, "Unable to delete instance.")
        return HttpResponseRedirect(redirect_to)
"""
def delete_server(request, project_id, server_id):
    out = {}
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        input_dict = {'project_id':project_id, 'server_id':server_id}
        serv_info = so.get_server(input_dict)
        del_serv = ds.delete_server(auth, input_dict)
        if(del_serv == 'OK'):
            out['status'] = 'success'
            out['message'] = 'Successfully deleted instance %s'%(serv_info['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))
'''
def resize_server(request, project_id, instance_id, flavor_id):
    input_dict = {'project_id':project_id, 'server_id':instance_id, 'flavor_id': flavor_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        rs = rs_server.resize_and_confirm(auth, input_dict)
        print "   ---   resize_and_confirm   ---"
        print rs
        print
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to resize server.")
        return HttpResponseRedirect(redirect_to)
'''

def confirm_resize(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'instance_id':instance_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        sa = server_actions(auth)
        sa.confirm_resize(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to confirm resize.")
        return HttpResponseRedirect(redirect_to)


def resize_server(request, project_id, instance_id, flavor_id):
    out = {}
    try:
        auth = request.session['auth']
        input_dict = {'project_id':project_id, 'server_id':instance_id, 'flavor_id': flavor_id}
        so = server_ops(auth)
        serv_info = so.get_server(input_dict)
        rs = rs_server.resize_and_confirm(auth, input_dict)
        if(rs == 'OK'):
            out['status'] = 'success'
            out['message'] = 'Successfully resized instance %s'%(serv_info['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))
'''
def reboot(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'server_id':instance_id, 'action_type':"SOFT"}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        sa = server_actions(auth)
        out = sa.reboot_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to reboot server.")
        return HttpResponseRedirect(redirect_to)
'''

def reboot(request, project_id, instance_id):
    try:
        auth = request.session['auth']
        sa = server_actions(auth)
        so = server_ops(auth)
        input_dict = {'project_id':project_id, 'server_id':instance_id, 'action_type':"SOFT"}
        serv_info = so.get_server(input_dict)
        reboot = sa.reboot_server(input_dict)
        if(reboot == 'OK'):
            out['status'] = 'success'
            out['message'] = 'Successfully rebooted instance %s'%(serv_info['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

'''
def power_cycle(request, project_id, instance_id):
    #this needs to be changed to the new power cycle method
    input_dict = {'project_id':project_id, 'server_id':instance_id, 'action_type':"HARD"}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        sa = server_actions(auth)
        sa.reboot_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to power cycle server.")
        return HttpResponseRedirect(redirect_to)
'''

def power_cycle(request, project_id, instance_id):
    out = {}
    try:
        auth = request.session['auth']
        sa = server_actions(auth)
        so = server_ops(auth)
        input_dict = {'project_id':project_id, 'server_id':instance_id}
        serv_info = so.get_server(input_dict)
        ps = sa.power_cycle_server(input_dict)
        if(ps == 'OK'):
            out['status'] = 'success'
            out['message'] = 'Successfully deleted instance %s'%(serv_info['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))


def power_off_server(request,project_id,server_id):
    out = {}
    try:
        auth = request.session['auth']
        input_dict = {'project_id':project_id, 'server_id':instance_id}
        sa = server_actions(auth)
        so = server_ops(auth)
        get = so.get_server(input_dict)
        po = sa.power_off_server(input_dict)
        if(po == 'OK'):
            out['status'] = 'success'
            out['message'] = "Instance %s powered off."%(get['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def power_on_server(request,project_id,server_id):
    out = {}
    try:
        auth = request.session['auth']
        input_dict = {'project_id':project_id, 'server_id':instance_id}
        sa = server_actions(auth)
        so = server_ops(auth)
        get = so.get_server(input_dict)
        po = sa.power_on_server(input_dict)
        if(po == 'OK'):
            out['status'] = 'success'
            out['message'] = "Instance %s powered on."%(get['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def live_migrate_server(request, project_id, instance_id, host_name):
    input_dict = {'project_id':project_id, 'instance_id':instance_id, 'openstack_host_id':host_name}
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        out = ssa.live_migrate_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to live migrate server.")
        return HttpResponseRedirect(redirect_to)

def migrate_server(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'instance_id':instance_id}
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        out = ssa.migrate_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to migrate server.")
        return HttpResponseRedirect(redirect_to)

def evacuate_server(request, project_id, instance_id, host_name):
    input_dict = {'project_id':project_id, 'instance_id':instance_id, 'openstack_host_id':host_name}
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        out = ssa.evacuate_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to evacuate server.")
        return HttpResponseRedirect(redirect_to)

def assign_floating_ip(request, floating_ip, instance_id, project_id):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        update_dict = {'floating_ip':floating_ip, 'instance_id':instance_id, 'project_id':project_id, 'action': 'add'}
        try:
            out = l3o.update_floating_ip(update_dict)
        except Exception as e:
            referer = request.META.get('HTTP_REFERER', None)
            redirect_to = urlsplit(referer, 'http', False)[2]
            return HttpResponseRedirect(redirect_to)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to assign floating ip.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 

def unassign_floating_ip(request, floating_ip_id):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        ip = l3o.get_floating_ip(floating_ip_id)
        update_dict = {'floating_ip':ip['floating_ip'], 'instance_id':ip['instance_id'], 'project_id':ip['project_id'], 'action': 'remove'}
        l3o.update_floating_ip(update_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to assign floating ip.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def toggle_user(request, username, toggle):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'toggle':toggle}
        uo.toggle_user(user_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        messages.warning(request, "Unable to toggle user.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def delete_user(request, username, userid):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'user_id':userid}
        out = uo.delete_user(user_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        messages.warning(request, "Unable to delete user.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_user_from_project(request, user_id, project_id):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'user_id': user_id, 'project_id':project_id}
        uo.remove_user_from_project(user_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        messages.warning(request, "Unable to remove user from project.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def add_existing_user(request, username, user_role, project_id):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'user_role':user_role, 'project_id': project_id}
        uo.add_user_to_project(user_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        messages.warning(request, "Unable to add existing user.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def update_user_password(request, user_id, project_id, password):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        passwd_dict = {'user_id': user_id, 'project_id':project_id, 'new_password': password }
        uo.update_user_password(passwd_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        messages.warning(request, 'Password updated.')
        return HttpResponseRedirect('/')

    except:
        messages.warning(request, "Unable to update user password.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def network_view(request, net_id):
    auth = request.session['auth']
    no = neutron_net_ops(auth)
    nw = no.get_network(net_id)
    sn = {}
    if nw['net_name'] != "DefaultPublic":
        sn = no.get_net_subnet(nw['net_subnet_id'][0]['subnet_id'])

    return render_to_response('coal/network_view.html',
                               RequestContext(request, {
                                                        'nw': nw,
                                                        'sn': sn,
                                                        }))

def router_view(request, router_id):
    auth = request.session['auth']
    l3o = layer_three_ops(auth)
    router = l3o.get_router(router_id)

    return render_to_response('coal/router_view.html',
                               RequestContext(request, {
                                                        'router': router,
                                                        }))

def instance_view(request, project_id, server_id):
    auth = request.session['auth']
    so = server_ops(auth)
    fo = flavor_ops(auth)
    i_dict = {'server_id': server_id, 'project_id': project_id}
    server = so.get_server(i_dict)
    flavors = fo.list_flavors()

    return render_to_response('coal/instance_view.html',
                               RequestContext(request, {
                                                        'server': server,
                                                        'flavors': flavors,
                                                        'current_project_id': project_id,
                                                        }))

def add_private_network(request, net_name, admin_state, shared, project_id):
    try:
        auth = request.session['auth']
        no = neutron_net_ops(auth)
        create_dict = {"net_name": net_name, "admin_state": admin_state, "shared": shared, "project_id": project_id}
        network = no.add_private_network(create_dict)
        subnet_dict={"net_id": network['net_id'], "subnet_dhcp_enable": "true", "subnet_dns": ["8.8.8.8"]}
        subnet = no.add_net_subnet(subnet_dict)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except:
        messages.warning(request, "Unable to add private network.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_private_network(request, project_id, net_id):
    try:
        auth    = request.session['auth']
        no      = neutron_net_ops(auth)
        l3o     = layer_three_ops(auth)
        network = no.get_network(net_id)
        subnets = network['net_subnet_id']

        for subnet in subnets:
            subnet_id = subnet['subnet_id']
            sub_proj_dict = {'net_id': net_id, 'subnet_id': subnet_id, 'project_id': project_id}
            if network['router_id']:
                remove_dict = {'router_id': network['router_id'], 'subnet_id': subnet_id, 'project_id': project_id}
                l3o.delete_router_internal_interface(remove_dict)
            #ports = no.list_net_ports(sub_proj_dict)
                #for port in ports:
                #remove_port_dict = {'subnet_id': subnet_id, 'project_id': project_id, 'port_id': port['port_id']}
                #no.remove_net_port(remove_port_dict)
            no.remove_net_subnet(sub_proj_dict)

        remove_dict={'net_id': net_id, 'project_id': project_id }
        no.remove_network(remove_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        messages.warning(request, "Unable to remove private network.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def container_view(request, project_id, container_name):
    auth = request.session['auth']
    cso = container_service_ops(auth)
    container_dict = {'project_id': project_id, 'container_name': container_name}
    container_objects = cso.list_container_objects(container_dict)

    return render_to_response('coal/container_view.html',
                               RequestContext(request, {'current_project_id' : project_id,
                                                        'container_name': container_name,
                                                        'container_objects': container_objects,
                                                        }))


# Create an OpenStack container with the given name for the given project ID.
def create_container (request, name, project_id):
    from transcirrus.component.swift.containerconnection import Args
    from transcirrus.component.swift.containerconnection import ContainerConnection
    sys.path.append("/usr/lib/python2.6/site-packages/")

    try:
        auth = request.session['auth']
        if auth['user_level'] > 0:
            if auth['project_id'] != project_id:
                logger.sys_error("Project IDs do not match %s - %s" % (args.project_id, project_id))
                out = {'status' : "error", 'message' : "Project IDs do not match %s - %s" % (auth['project_id'], project_id)}
                return HttpResponse(simplejson.dumps(out))
        auth['project_id'] = project_id
        args = Args (auth, name)

        container_con = ContainerConnection (args)
        if container_con.exists (name):
            out = {'status' : "error", 'message' : "Container %s already exists for this project" % name}
            return HttpResponse(simplejson.dumps(out))
        container_con.create (name)
        out = {'status' : "success", 'message' : "Container %s was created." % name}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error creating container: %s" % e}
    sys.path.remove("/usr/lib/python2.6/site-packages/")
    return HttpResponse(simplejson.dumps(out))


# List all OpenStack containers for the given project ID.
def list_containers (request, project_id):
    from transcirrus.component.swift.containerconnection import Args
    from transcirrus.component.swift.containerconnection import ContainerConnection
    sys.path.append("/usr/lib/python2.6/site-packages/")

    try:
        auth = request.session['auth']
        auth['project_id'] = project_id
        args = Args (auth, "")

        container_con = ContainerConnection (args)
        container_list = container_con.list()
        out = {'status' : "success", 'containers' : container_list}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error getting list of containers: %s" % e}
    sys.path.remove("/usr/lib/python2.6/site-packages/")
    return HttpResponse(simplejson.dumps(out))


# Delete an OpenStack container with the given name for the given project ID.
def delete_container (request, name, project_id):
    from transcirrus.component.swift.containerconnection import Args
    from transcirrus.component.swift.containerconnection import ContainerConnection
    sys.path.append("/usr/lib/python2.6/site-packages/")

    try:
        auth = request.session['auth']
        if auth['user_level'] > 0:
            if auth['project_id'] != project_id:
                logger.sys_error("Project IDs do not match %s - %s" % (args.project_id, project_id))
                out = {'status' : "error", 'message' : "Project IDs do not match %s - %s" % (auth['project_id'], project_id)}
                return HttpResponse(simplejson.dumps(out))
        auth['project_id'] = project_id
        args = Args (auth, name)

        container_con = ContainerConnection (args)
        if not container_con.exists (name):
            out = {'status' : "error", 'message' : "Container %s does not exist for this project" % name}
            return HttpResponse(simplejson.dumps(out))
        container_con.delete (name)
        out = {'status' : "success", 'message' : "Container %s was deleted." % name}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error deleting container: %s" % e}
    sys.path.remove("/usr/lib/python2.6/site-packages/")
    return HttpResponse(simplejson.dumps(out))

# Upload a local file (object) to the given container.
def upload_local_object (request, container, filename, project_id, project_name, dummy1, dummy2, progress_id):
    from coalesce.coal_beta.models import ImportLocal

    from transcirrus.component.swift.containerconnection import Args
    from transcirrus.component.swift.containerconnection import ContainerConnection
    from transcirrus.component.swift.swiftconnection import SwiftConnection
    sys.path.append("/usr/lib/python2.6/site-packages/")

    try:
        auth = request.session['auth']
        if auth['user_level'] > 0:
            if auth['project_id'] != project_id:
                logger.sys_error("Project IDs do not match %s - %s" % (args.project_id, project_id))
                out = {'status' : "error", 'message' : "Project IDs do not match %s - %s" % (auth['project_id'], project_id)}
                return HttpResponse(simplejson.dumps(out))
        auth['project_id'] = project_id
        args = Args (auth, container)

        container_con = ContainerConnection (args)
        if not container_con.exists (container):
            out = {'status' : "error", 'message' : "Container %s does not exist for this project" % container}
            return HttpResponse(simplejson.dumps(out))

        object_con = SwiftConnection (args)

        print "content filename: %s" % request.FILES['import_local'].name
        print "sent filename: %s" % filename
        content_type = request.FILES['import_local'].content_type
        if request.FILES['import_local'].size >= 5 * 1024 ** 3:     # is the file >= 5GB
            large_file = True
        else:
            large_file = False

        object_con.put (filename, request.FILES['import_local'], content_type, large=large_file)
        out = {'status' : "success", 'message' : "Local file/object %s was uploaded." % filename,
               'object_id' : container + "/" + filename}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error uploading local file/object: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Upload a remote file (object) to the given container.
def upload_remote_object (request, container, url, project_id, project_name, progress_id):
    from transcirrus.component.swift.containerconnection import Args
    from transcirrus.component.swift.containerconnection import ContainerConnection
    from transcirrus.component.swift.swiftconnection import SwiftConnection
    sys.path.append("/usr/lib/python2.6/site-packages/")

    global cache_key
    try:
        auth = request.session['auth']
        if auth['user_level'] > 0:
            if auth['project_id'] != project_id:
                logger.sys_error("Project IDs do not match %s - %s" % (args.project_id, project_id))
                out = {'status' : "error", 'message' : "Project IDs do not match %s - %s" % (auth['project_id'], project_id)}
                return HttpResponse(simplejson.dumps(out))
        auth['project_id'] = project_id
        args = Args (auth, container)

        container_con = ContainerConnection (args)
        if not container_con.exists (container):
            out = {'status' : "error", 'message' : "Container %s does not exist for this project" % container}
            return HttpResponse(simplejson.dumps(out))

        # Replace any '%47' with a slash '/'
        url = url.replace("&47", "/")

        # Setup our cache to track the progress.
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        cache.set (cache_key, {'length': 0, 'uploaded' : 0})

        # Use wget to download the file.
        download_dir   = "/tmp/"
        download_fname = time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".img"
        download_file  = download_dir + download_fname

        # Download the file via a wget like interface to the file called download_file and
        # log the progress via the callback function download_progress.
        filename, content_type = wget.download (url, download_file, download_progress)

        # Delete our cached progress.
        cache.delete(cache_key)
        cache_key = None

        # Add the object to swift.
        object_con = SwiftConnection (args)

        if content_type == None:
            content_type = "application/octet-stream"

        filesize = os.stat(download_file).st_size

        if filesize >= 5 * 1024 ** 3:     # is the file >= 5GB
            large_file = True
        else:
            large_file = False

        stream = io.open (download_file, mode='r+b')
        object_con.put (filename, stream, content_type, large=large_file)
        stream.close()

        # Delete the temp file and only log any errors since the file was successfully added to the container.
        try:
            os.remove (download_file)
        except Exception as e:
            logger.sys_error ("Unable to delete temp remote object file %s, msg: %s" % (download_file, e))

        out = {'status' : "success", 'message' : "Remote file/object %s was uploaded." % filename,
               'object_id' : container + "/" + filename}
    except Exception as e:
        cache.delete(cache_key)
        cache_key = None
        out = {'status' : "error", 'message' : "Error uploading remote file/object: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Get an object from the given container.
def get_object (request, container, filename, project_id):
    from transcirrus.component.swift.containerconnection import Args
    from transcirrus.component.swift.containerconnection import ContainerConnection
    from transcirrus.component.swift.swiftconnection import SwiftConnection
    sys.path.append("/usr/lib/python2.6/site-packages/")

    try:
        auth = request.session['auth']
        if auth['user_level'] > 0:
            if auth['project_id'] != project_id:
                logger.sys_error("Project IDs do not match %s - %s" % (args.project_id, project_id))
                out = {'status' : "error", 'message' : "Project IDs do not match %s - %s" % (auth['project_id'], project_id)}
                return HttpResponse(simplejson.dumps(out))
        auth['project_id'] = project_id
        args = Args (auth, container)

        container_con = ContainerConnection (args)
        if not container_con.exists (container):
            out = {'status' : "error", 'message' : "Container %s does not exist for this project" % container}
            return HttpResponse(simplejson.dumps(out))

        object_con = SwiftConnection (args)
        if not object_con.exists (filename):
            out = {'status' : "error", 'message' : "File/object %s does not exist in the containter %s" % (filename, container)}
            return HttpResponse(simplejson.dumps(out))

        content = object_con.get (filename)

        if content is None:
            out = {'status' : "error", 'message' : "Error retrieving file/object %s from the containter %s" % (filename, container)}
            return HttpResponse(simplejson.dumps(out))

        response = HttpResponse (content, content_type="")
        response['Content-Length'] = ""
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
    except Exception, e:
        out = {'status' : "error", 'message' : "Error deleting file/object: %s" % e}
        return HttpResponse(simplejson.dumps(out))


# List all objects for the given container.
def list_objects (request, container, project_id):
    from transcirrus.component.swift.containerconnection import Args
    from transcirrus.component.swift.containerconnection import ContainerConnection
    from transcirrus.component.swift.swiftconnection import SwiftConnection
    sys.path.append("/usr/lib/python2.6/site-packages/")

    try:
        auth = request.session['auth']
        if auth['user_level'] > 0:
            if auth['project_id'] != project_id:
                logger.sys_error("Project IDs do not match %s - %s" % (args.project_id, project_id))
                out = {'status' : "error", 'message' : "Project IDs do not match %s - %s" % (auth['project_id'], project_id)}
                return HttpResponse(simplejson.dumps(out))
        auth['project_id'] = project_id
        args = Args (auth, container)

        container_con = ContainerConnection (args)
        if not container_con.exists (container):
            out = {'status' : "error", 'message' : "Container %s does not exist for this project" % container}
            return HttpResponse(simplejson.dumps(out))

        object_con = SwiftConnection (args)
        object_list = object_con.list (exclude_segments=True)
        out = {'status' : "success", 'objects' : object_list}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error getting list of objects in the container: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Delete an object from the given container.
def delete_object (request, container, filename, project_id, project_name):
    from transcirrus.component.swift.containerconnection import Args
    from transcirrus.component.swift.containerconnection import ContainerConnection
    from transcirrus.component.swift.swiftconnection import SwiftConnection
    sys.path.append("/usr/lib/python2.6/site-packages/")

    try:
        auth = request.session['auth']
        if auth['user_level'] > 0:
            if auth['project_id'] != project_id:
                logger.sys_error("Project IDs do not match %s - %s" % (args.project_id, project_id))
                out = {'status' : "error", 'message' : "Project IDs do not match %s - %s" % (auth['project_id'], project_id)}
                return HttpResponse(simplejson.dumps(out))
        auth['project_id'] = project_id
        args = Args (auth, container)

        container_con = ContainerConnection (args)
        if not container_con.exists (container):
            out = {'status' : "error", 'message' : "Container %s does not exist for this project" % container}
            return HttpResponse(simplejson.dumps(out))

        object_con = SwiftConnection (args)
        if not object_con.exists (filename):
            out = {'status' : "error", 'message' : "File/object %s does not exist in the containter %s" % (filename, container)}
            return HttpResponse(simplejson.dumps(out))

        object_con.delete (filename)
        out = {'status' : "success", 'message' : "File/object %s was deleted." % filename}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error deleting file/object: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Call the routine that will collect all the data from all nodes and send it back to us.
def phonehome (request):
    import transcirrus.operations.support_create as support_create
    try:
        support_create.EnableSim()         ### DEBUG ONLY! REMOVE!!
        support_create.EnableCaching()
        support_create.DoCreate()
        support_create.DisableCaching()
        out = {'status' : "success", 'message' : "Support data has been sent to TransCirrus."}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error collecting/sending support data: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Call the routine that will upgrade all nodes to the given version of software.
def upgrade (request, version="stable"):
    import transcirrus.operations.upgrade as upgrade
    try:
        upgrade.EnableSim()         ### DEBUG ONLY! REMOVE!!
        upgrade.ReleaseToDownload = version
        upgrade.EnableCaching()
        upgrade.DoUpgrade()
        upgrade.DisableCaching()
        out = {'status' : "success", 'message' : "Software upgrade has completed successfully."}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error upgrading software: %s" % e}
    return HttpResponse(simplejson.dumps(out))


def setup(request):
    if request.method == 'POST':
        if request.POST.get('cancel'):
            return HttpResponseRedirect('/')
        form = SetupForm(request.POST)
        if form.is_valid():
            management_ip          = form.cleaned_data['management_ip']
            uplink_ip              = form.cleaned_data['uplink_ip']
            vm_ip_min              = form.cleaned_data['vm_ip_min']
            vm_ip_max              = form.cleaned_data['vm_ip_max']
            uplink_dns             = form.cleaned_data['uplink_dns']
            uplink_gateway         = form.cleaned_data['uplink_gateway']
            uplink_domain_name     = form.cleaned_data['uplink_domain_name']
            uplink_subnet      = form.cleaned_data['uplink_subnet']
            mgmt_domain_name       = form.cleaned_data['mgmt_domain_name']
            mgmt_subnet            = form.cleaned_data['mgmt_subnet']
            mgmt_dns               = form.cleaned_data['mgmt_dns']
            #cloud_name             = form.cleaned_data['cloud_name']
            single_node            = False
            admin_password         = form.cleaned_data['admin_password']
            admin_password_confirm = form.cleaned_data['admin_password_confirm']

            auth = request.session['auth']
            system = util.get_cloud_controller_name()
            system_var_array = [
                                {"system_name": system, "parameter": "api_ip",             "param_value": uplink_ip},
                                {"system_name": system, "parameter": "mgmt_ip",            "param_value": management_ip},
                                {"system_name": system, "parameter": "admin_api_ip",       "param_value": uplink_ip},
                                {"system_name": system, "parameter": "int_api_id",         "param_value": uplink_ip},
                                {"system_name": system, "parameter": "uplink_ip",          "param_value": uplink_ip},
                                {"system_name": system, "parameter": "vm_ip_min",          "param_value": vm_ip_min},
                                {"system_name": system, "parameter": "vm_ip_max",          "param_value": vm_ip_max},
                                {"system_name": system, "parameter": "single_node",        "param_value": single_node},
                                {"system_name": system, "parameter": "uplink_dns",         "param_value": uplink_dns},
                                {"system_name": system, "parameter": "uplink_gateway",     "param_value": uplink_gateway},
                                {"system_name": system, "parameter": "uplink_domain_name", "param_value": uplink_domain_name},
                                {"system_name": system, "parameter": "uplink_subnet",      "param_value": uplink_subnet},
                                {"system_name": system, "parameter": "mgmt_domain_name",   "param_value": mgmt_domain_name},
                                {"system_name": system, "parameter": "mgmt_subnet",        "param_value": mgmt_subnet},
                                {"system_name": system, "parameter": "mgmt_dns",           "param_value": mgmt_dns},
                                ]

            run_setup(system_var_array, auth)
            change_admin_password (auth, admin_password)
            return render_to_response('coal/setup_results.html', RequestContext(request, {'management_ip': management_ip}))
        else:
            return render_to_response('coal/setup.html', RequestContext(request, { 'form':form, }))
    else:
        form = SetupForm()
    return render_to_response('coal/setup.html', RequestContext(request, { 'form':form, }))

def build_project(request):
    if request.method == 'POST':
        if request.POST.get('cancel'):
            return HttpResponseRedirect('/')
        form = BuildProjectForm(request.POST)
        if form.is_valid():
            proj_name        = form.cleaned_data['proj_name']
            username         = form.cleaned_data['username']
            password         = form.cleaned_data['password']
            password_confirm = form.cleaned_data['password_confirm']
            email           = form.cleaned_data['email']
            net_name        = form.cleaned_data['net_name']
            subnet_dns      = form.cleaned_data['subnet_dns']
            #ports[] - op
            group_name      = form.cleaned_data['group_name']
            group_desc      = form.cleaned_data['group_desc']
            sec_keys_name   = form.cleaned_data['sec_keys_name']
            router_name     = form.cleaned_data['router_name']

            #get the advanced props flag
            #advanced        = form.cleaned_data['advanced'] #TRUE/FALSE
            advanced = None

            auth = request.session['auth']
            project_var_array = {'project_name': proj_name,
                                 'user_dict': { 'username': username,
                                                'password': password,
                                                'user_role': 'pu',
                                                'email': email,
                                                'project_id': ''},

                                 'net_name':net_name,
                                 'subnet_dns': subnet_dns,
                                 'sec_group_dict':  { 'ports': '',
                                                     'group_name': group_name,
                                                     'group_desc': 'group_desc',
                                                     'project_id': ''},

                                 'sec_keys_name': sec_keys_name,
                                 'router_name': router_name
                            }

            #add in the advanced quota options
            if(advanced):
                cores           = form.cleaned_data['core']
                fixed_ips       = form.cleaned_data['fixed_ips']
                floating_ips    = form.cleaned_data['floating_ips']
                injected_file_content_bytes = form.cleaned_data['injected_file_content_bytes']
                injected_file_path_bytes = form.cleaned_data['injected_file_path_bytes']
                injected_files  = form.cleaned_data['injected_files']
                instances       = form.cleaned_data['instances']
                key_pairs       = form.cleaned_data['key_pairs']
                metadata_items  = form.cleaned_data['metadata_items']
                ram             = form.cleaned_data['ram']
                security_group_rules = form.cleaned_data['security_group_rules']
                security_groups = form.cleaned_data['security_groups']
                storage         = form.cleaned_data['storage']
                snapshots       = form.cleaned_data['snapshots']
                volumes         = form.cleaned_data['volumes']
                subnet_quota    = form.cleaned_data['subnet_quota']
                router_quota    = form.cleaned_data['router_quota']
                network_quota   = form.cleaned_data['network_quota']
                floatingip_quota = form.cleaned_data['floatingip_quota']
                port_quota      = form.cleaned_data['port_quota']

                quota = {
                        'cores':cores,
                        'fixed_ips':fixed_ips,
                        'floating_ips':floating_ips,
                        'injected_file_content_bytes':injected_file_content_bytes,
                        'injected_file_path_bytes':injected_file_path_bytes,
                        'injected_files':injected_files,
                        'instances':instances,
                        'key_pairs':key_pairs,
                        'metadata_items':metadata_items,
                        'ram':ram,
                        'security_group_rules':security_group_rules,
                        'security_groups':security_groups,
                        'storage':storage,
                        'snapshots':snapshots,
                        'volumes':volumes
                }

                project_var_array['advanced_ops']['quota'] = quota

            pid = bcp.build_project(auth, project_var_array)

            redirect_to = "/projects/%s/view/" % (pid)
            return HttpResponseRedirect(redirect_to)

        else:
            return render_to_response('coal/build_project.html', RequestContext(request, { 'form':form, }))

    else:
        form = BuildProjectForm()
    return render_to_response('coal/build_project.html', RequestContext(request, { 'form':form, }))


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
            try:
                user = form.cleaned_data['username']
                pw = form.cleaned_data['password']
                a = authorization(user, pw)
                auth = a.get_auth()
                if auth['token'] == None:
                    form = authentication_form()
                    messages.warning(request, 'Login failed.  Please verify your username and password.')
                    return render_to_response('coal/login.html', RequestContext(request, { 'form':form, }))
                request.session['auth'] = auth
                return render_to_response('coal/welcome.html', RequestContext(request, {  }))
            except:
                form = authentication_form()
                messages.warning(request, 'Login failed.  Please verify your username and password.')
                return render_to_response('coal/login.html', RequestContext(request, { 'form':form, }))
        else:
                form = authentication_form()
                messages.warning(request, 'Login failed.  Please verify your username and password.')
                return render_to_response('coal/login.html', RequestContext(request, { 'form':form, }))
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


def handle_uploaded_file(f):
    print ("Uploading local file: " + f)
    with open('/tmp/upload.img', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    print ("Uploaded local file done")
    return

@never_cache
def password_change(request):
    return render_to_response('coal/change-password.html', RequestContext(request, {  }))

