
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
from transcirrus.operations.revert_instance_snapshot import revert_inst_snap
from transcirrus.operations.revert_volume_snapshot import revert_vol_snap
import transcirrus.common.util as util
import transcirrus.common.wget as wget
from transcirrus.database.node_db import list_nodes, get_node
import transcirrus.operations.destroy_project as destroy
import transcirrus.operations.resize_server as rs_server
import transcirrus.operations.migrate_server as migration
import transcirrus.operations.server_volume_ops as svo
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

from transcirrus.component.swift.containerconnection import Args
from transcirrus.component.swift.containerconnection import ContainerConnection
from transcirrus.component.swift.swiftconnection import SwiftConnection
#import transcirrus.operations.support_create as support_create
#import transcirrus.operations.upgrade as upgrade
#sys.path.append("/usr/lib/python2.6/site-packages/")

import transcirrus.operations.third_party_storage.third_party_config as tpc
from transcirrus.operations.third_party_storage.eseries.mgmt import eseries_mgmt

# Custom imports
#from coalesce.coal_beta.models import *
from coalesce.coal_beta.forms import *

# Globals
cache_key = None
eseries_config = None
nfs_config = None


def stats(request):
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

def welcome(request):
    return render_to_response('coal/welcome.html', RequestContext(request,))

def node_view(request, node_id):
    node=get_node(node_id)
    node['status'] = node_stats.node_status (node['node_mgmt_ip'], node['node_data_ip'])
    node['mgmt_ip_issue'] = False
    node['data_ip_issue'] = False
    if node['status'] == "Issue":
        if not node_stats.is_node_up (node['node_mgmt_ip']):
            node['mgmt_ip_issue'] = True
        else:
            node['data_ip_issue'] = True
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
            ni['node_id'] = nid
            ni['status'] = node_stats.node_status (ni['node_mgmt_ip'], ni['node_data_ip'])
            ni['mgmt_ip_issue'] = False
            ni['data_ip_issue'] = False
            if ni['status'] == "Issue":
                if not node_stats.is_node_up (ni['node_mgmt_ip']):
                    ni['mgmt_ip_issue'] = True
                else:
                    ni['data_ip_issue'] = True
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
        out = {}
        if(auth[is_admin == 1]):
            net_out = ao.list_net_quota(project_id)
            out = dict(proj_out.items() + net_out[0].items())
        else:
            out = dict(proj_out.items())
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
    qo = quota_ops(auth)
    #do not call until version2
    #aso = account_service_ops(auth)

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
                ouserinfo.append({'username': ouser['username'], 'user_role': ouser['user_group'],
                                  'user_enabled': ouser['user_enabled'], 'keystone_user_id': ouser['keystone_user_id'],
                                  'email': ouser['user_email']})
    except:
        ousers=[]

    priv_net_list = no.list_internal_networks(project_id)
    pub_net_list  = no.list_external_networks()
    routers       = l3o.list_routers(project_id)
    volumes       = vo.list_volumes(project_id)
    volume_info={}
    snapshots     = sno.list_snapshots(project_id)

    #do not call until version2
    #try:
    #    containers    = aso.get_account_containers(project_id)
    #except:
    #    containers = []
    containers = []

    sec_groups    = so.list_sec_group(project_id)
    sec_keys      = so.list_sec_keys(project_id)
    instances     = so.list_servers(project_id)
    instance_info = {}
    flavors       = fo.list_flavors()

    hosts=[]
    host_dict     = {'project_id': project_id, 'zone': 'nova'}
    hosts         = ssa.list_compute_hosts(host_dict)

    volume_types = []
    volume_types = vo.list_volume_types()

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
                                                        'volume_types': volume_types,
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
    #do not use until version2
    #aso = account_service_ops(auth)

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

    #do not use until version2
    #try:
    #    containers    = aso.get_account_containers(project_id)
    #except:
    #    containers = []
    containers = []


    sec_groups    = so.list_sec_group(project_id)
    sec_keys      = so.list_sec_keys(project_id)
    instances     = so.list_servers(project_id)
    instance_info={}
    flavors       = fo.list_flavors()

    volume_types = []
    volume_types = vo.list_volume_types()

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
                                                        'volume_types': volume_types,
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

    volume_types = []
    volume_types = vo.list_volume_types()

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
                                                        'volume_types': volume_types,
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
    out = {}
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        key_dict = {'sec_key_name': sec_key_name, 'project_id': project_id}
        del_key = so.delete_sec_keys(key_dict)
        if(del_key == 'OK'):
            out['status'] = 'success'
            out['message'] = 'Successfully removed key %s.'%(sec_key_name)
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not delete key: %s"%(e)}
    return HttpResponse(simplejson.dumps(out))



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
    snapshots = sno.list_snapshots(project_id)
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
        out = uo.create_user(user_dict)
        out['status'] = 'success'
        out['message'] = 'The new user %s was added to the project.'%(username)
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not create user %s: %s" %(username,e)}
    return HttpResponse(simplejson.dumps(out))

def create_security_group(request, groupname, groupdesc, ports, transport, project_id):
    try:
        portstrings    = ports.split(',')
        portlist = []
        for port in portstrings:
            portlist.append(int(port))
        auth = request.session['auth']
        so = server_ops(auth)
        create_sec = {'group_name': groupname, 'group_desc':groupdesc, 'ports': portlist, 'transport': transport, 'project_id': project_id}
        out = so.create_sec_group(create_sec)
        out['status'] = 'success'
        out['message'] = 'The security group %s was created'%(groupname)
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not create security group %s: %s" %(groupname,e)}
    return HttpResponse(simplejson.dumps(out))

def update_security_group(request, groupid, project_id, ports, enable_ping, transport):
    output = {}
    try:
        portstrings = ports.split(',')
        portlist = []
        for port in portstrings:
            portlist.append(int(port))
        auth = request.session['auth']
        so = server_ops(auth)
        update_sec = {'group_id': groupid, 'enable_ping': enable_ping, 'ports': portlist, 'project_id': project_id, 'transport': transport, 'update':'true'}
        out = so.update_sec_group(update_sec)
        if(out == 'OK'):
            grp = { 'project_id': project_id, 'sec_group_id': groupid }
            output = so.get_sec_group(grp)
            output['status'] = 'success'
            output['message'] = "The security group %s was updated"%(output['sec_group_name'])
    except Exception as e:
        output = {'status' : "error", 'message' : "Could not update security group: %s" %(e)}
    return HttpResponse(simplejson.dumps(output))

def delete_sec_group(request, sec_group_id, project_id):
    out = {}
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        sec_dict = {'sec_group_id': sec_group_id, 'project_id':project_id}
        del_sec = so.delete_sec_group(sec_dict)
        if(del_sec == 'OK'):
            out['status'] = 'success'
            out['message'] = 'Successfully removed security group.'
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not delete security group: %s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def security_group_view(request, groupid, project_id):
    auth = request.session['auth']
    so = server_ops(auth)
    grp = { 'project_id': project_id, 'sec_group_id': groupid }
    sec_group = so.get_sec_group(grp)
    return render_to_response('coal/security_group_view.html',
                               RequestContext(request, {
                                                        'sec_group': sec_group,
                                                        }))

def create_keypair(request, key_name, project_id):
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        key_dict = {'key_name': key_name, 'project_id': project_id}
        out = so.create_sec_keys(key_dict)
        out['status'] = 'success'
        out['message'] = 'The new security key %s was created.'%(key_name)
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not create the security key: %s"%(e)}
    return HttpResponse(simplejson.dumps(out))

# Import a local (user's laptop) image and add it to glance & database. The image has already been uploaded via the broswer
# to memory or a temp file so we just need to transfer the contents to a file we control.
def import_local (request, image_name, container_format, disk_format, image_type, image_location, visibility, os_type, progress_id):
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

        # Add the image to glance.
        import_dict = {'image_name': image_name, 'container_format': container_format, 'image_type': image_type, 'disk_format': disk_format, 'visibility': visibility, 'image_location': "", 'os_type': os_type}
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
def import_remote (request, image_name, container_format, disk_format, image_type, image_location, visibility, os_type, progress_id):
    global cache_key
    try:
        auth = request.session['auth']
        go = glance_ops(auth)
        import_dict = {'image_name': image_name, 'container_format': container_format, 'image_type': 'image_file', 'disk_format': disk_format, 'visibility': visibility, 'image_location': image_location, 'os_type': os_type}

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
        filename, content_type = wget.download (image_location,download_file, download_progress)
        # Delete our cached progress.
        cache.delete(cache_key)
        cache_key = None

        # Add the image to glance.
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
    out = {}
    try:
        auth = request.session['auth']
        go = glance_ops(auth)
        del_image = go.delete_image(image_id)
        if(del_image == 'OK'):
            out['status'] = "success"
            out['message'] = "Image was deleted."
    except Exception, e:
        out = {'status' : "error", 'message' : "Error deleting image: %s" % e}
    return HttpResponse(simplejson.dumps(out))

def create_instance_snapshot(request, project_id, server_id, snapshot_name, snapshot_description=None):
    try:
        auth = request.session['auth']
        sa = server_actions(auth)
        create = {'project_id': project_id, 'server_id': server_id, 'snapshot_name': snapshot_name, 'snapshot_description': snapshot_description}
        out = sa.create_instance_snapshot(create)
        out['status'] = 'success'
        out['message'] = "Snapshot %s has been created."%(snapshot_name)
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def revert_instance_snapshot(request, project_id, instance_id, snapshot_id):
    out = {}
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        create = {'project_id': project_id, 'instance_id': instance_id, 'snapshot_id': snapshot_id}
        out = revert_inst_snap(create, auth)
        new_server = {'server_id':out['instance']['vm_id'],'project_id':project_id}
        out['server_info'] = so.get_server(new_server)
        out['status'] = 'success'
        out['message'] = "Instance has been reverted."
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def revert_volume_snapshot(request, project_id, volume_id, volume_name, snapshot_id):
    out = {}
    try:
        auth = request.session['auth']
        create = {'project_id': project_id, 'volume_id': volume_id, 'volume_name': volume_name, 'snapshot_id': snapshot_id}
        vol = revert_vol_snap(create, auth)
        out['volume_info'] = vol['volume_info']
        out['attach_info'] = vol['attach_info']
        out['status'] = 'success'
        out['message'] = "Volume has been reverted."
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

# REMOVED DESCRIPTION FOR NOW AS IT IS UNUSED
def create_volume(request, volume_name, volume_size, volume_type, project_id):
    out = {}
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        create_vol = {'volume_name': volume_name, 'volume_size': volume_size, 'volume_type': volume_type, 'project_id': project_id}
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

# REMOVED DESCRIPTION FOR NOW AS IT IS UNUSED
def create_vol_from_snapshot(request, project_id, snapshot_id, volume_size, volume_name):
    out = {}
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        create = { 'project_id':project_id, 'snapshot_id': snapshot_id, 'volume_size': volume_size, 'volume_name': volume_name }
        out = vo.create_vol_from_snapshot(create)
        out['status'] = 'success'
        out['message'] = "Volume %s was created from snapshot."%(volume_name)
    except Exception as e:
        out = {"status": "error", "message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

# REMOVED DESCRIPTION FOR NOW AS IT IS UNUSED
def create_vol_clone(request, project_id, volume_id, volume_name):
    out = {}
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        create = { 'project_id': project_id, 'volume_id': volume_id, 'volume_name': volume_name }
        out = vo.create_vol_clone(create)
        out['status'] = 'success'
        out['message'] = "Volume clone %s was created."%(volume_name)
    except Exception as e:
        out = {"status": "error", "message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

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
    output = {}
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        attach_vol = {'project_id': project_id, 'instance_id': instance_id, 'volume_id': volume_id, 'mount_point': "/dev/vdc",'action':'mount'}
        att = svo.server_vol_ops(auth,attach_vol)
        get_vol = {'project_id': project_id, 'volume_id': volume_id}
        vol = vo.get_volume_info(get_vol)
        if(att == 'OK'):
            output['status'] = 'success'
            output['message'] = "Volume %s attached to %s."%(vol['volume_name'],vol['volume_instance_name'])
    except Exception, e:
        output = {'status' : "error", 'message' : "Could not attach the volume: %s" %(e)}
    return HttpResponse(simplejson.dumps(output))

def detach_volume(request, project_id, volume_id):
    output = {}
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        v_dict = {'volume_id': volume_id, 'project_id': project_id}
        vol = vo.get_volume_info(v_dict)
        detach_vol = {'project_id': project_id, 'instance_id': vol['volume_instance'], 'volume_id': volume_id,'action':'unmount'}
        detach = svo.server_vol_ops(auth,detach_vol)
        if(detach == 'OK'):
            output['status'] = 'success'
            output['message'] = "Volume %s detached from %s."%(vol['volume_name'],vol['volume_instance_name'])
    except Exception, e:
        output = {'status' : "error", 'message' : "Could not detach the volume: %s."%(e)}
    return HttpResponse(simplejson.dumps(output))

def create_snapshot(request, project_id, name, volume_id, desc):
    try:
        auth = request.session['auth']
        sno = snapshot_ops(auth)
        create_snap = {'project_id': project_id, 'snapshot_name': name, 'volume_id': volume_id, 'snapshot_desc': desc}
        out = sno.create_snapshot(create_snap)
        out['status'] = 'success'
        out['message'] = "The snapshot %s has been created for volume id %s"%(out['snapshot_name'], out['volume_id'])
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not create snapshot : %s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def delete_snapshot(request, project_id, snapshot_id):
    output = {}
    try:
        auth = request.session['auth']
        sno = snapshot_ops(auth)
        delete_snap = {'project_id': project_id, 'snapshot_id': snapshot_id}
        out = sno.delete_snapshot(delete_snap)
        if(out == 'OK'):
            output['status'] = 'success'
            output['message'] = "The snapshot with id %s has been deleted."%(snapshot_id)
    except Exception as e:
        output = {'status' : "error", 'message' : "Could not delete snapshot: %s"%(e)}
    return HttpResponse(simplejson.dumps(output))

def snapshot_view(request, snapshot_id):
    auth = request.session['auth']
    sno = snapshot_ops(auth)
    snapshot = sno.get_snapshot(snapshot_id)
    return render_to_response('coal/snapshot_view.html',
                               RequestContext(request, {
                                                        'snapshot': snapshot,
                                                        }))

def create_router(request, router_name, priv_net, default_public, project_id):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        no = neutron_net_ops(auth)
        netinfo = no.get_network(priv_net)
        subnet = netinfo["net_subnet_id"][0]['subnet_id']

        create_router = {'router_name': router_name, 'project_id': project_id}
        out = l3o.add_router(create_router)

        add_dict = {'router_id': out['router_id'], 'ext_net_id': default_public, 'project_id': project_id}
        argi = l3o.add_router_gateway_interface(add_dict)
        if(argi == 'OK'):
            out['add_router_gateway_interface'] = 'success'

        internal_dict = {'router_id': out['router_id'], 'project_id': project_id, 'subnet_id': subnet}
        out = l3o.add_router_internal_interface(internal_dict)
        out['status'] = 'success'
        out['message'] = 'Created new router %s'%(router_name)
    except Exception, e:
        out = {'status' : "error", 'message' : "Could not create the router %s."%(router_name)}
    return HttpResponse(simplejson.dumps(out))

def delete_router(request, project_id, router_id):
    out = {}
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
        del_router = l3o.delete_router(proj_rout_dict)
        if(del_router == 'OK'):
            out['status'] = 'success'
            out['message'] = 'The router has been deleted.'
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not delete the router %s."%(e)}
    return HttpResponse(simplejson.dumps(out))


def destroy_project(request, project_id, project_name=None):
    out = {}
    try:
        auth = request.session['auth']
        proj_dict = {'project_name': project_name, 'project_id': project_id, 'keep_users': True}
        des = destroy.destroy_project(auth, proj_dict)
        if(des == 'OK'):
            out = {'status' : "success", 'message' : "Project %s has been deleted." %(proj_dict['project_name'])}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error deleteing project %s with error %s" % (proj_dict['project_name'], e)}
    return HttpResponse(simplejson.dumps(out))

def allocate_floating_ip(request, project_id, ext_net_id):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        input_dict = {'ext_net_id': ext_net_id, 'project_id': project_id}
        floater = l3o.allocate_floating_ip(input_dict)
        out = {'status' : "success", 'message' : "Floating IP address %s was allocated." % ext_net_id}
        out['ip_info'] = floater
    except Exception, e:
        out = {'status' : "error", 'message' : "Error allocating Floating IP %s address, error: %s" % (ext_net_id, e)}
    return HttpResponse(simplejson.dumps(out))

def deallocate_floating_ip(request, project_id, floating_ip):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        input_dict = {'floating_ip': floating_ip, 'project_id': project_id}
        l3o.deallocate_floating_ip(input_dict)
        out = {'status' : "success", 'message' : "Floating IP address %s was deallocated." % floating_ip}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error deallocating Floating IP %s address, error: %s" % (floating_ip, e)}
    return HttpResponse(simplejson.dumps(out))

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
        #net_info = so.attach_server_to_network(input_dict)
        out['server_info']= so.get_server(input_dict)
        out['status'] = 'success'
        out['message'] = "New server %s was created."%(out['vm_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

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

def delete_server(request, project_id, server_id):
    out = {}
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        input_dict = {'project_id':project_id, 'server_id':server_id}
        serv_info = so.get_server(input_dict)
        del_serv = ds.delete_server(auth, input_dict)
        if(del_serv['delete'] == 'OK'):
            out['vols'] = del_serv['vols']
            out['floating_ip_id'] = del_serv['floating_ip_id']
            out['floating_ip'] = del_serv['floating_ip']
            out['status'] = 'success'
            out['message'] = 'Successfully deleted instance %s'%(serv_info['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

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
        fo = flavor_ops(auth)
        serv_info = so.get_server(input_dict)
        flavor_info = fo.get_flavor(flavor_id)
        server_flav = fo.get_flavor(serv_info['flavor_id'])
        if(flavor_info['disk_space(GB)'] < server_flav['disk_space(GB)']):
            logger.sys_error('Could not resize instance, disk space is less than current spec.')
            raise Exception('Could not resize instance, disk space is less than current spec.')
        rs = rs_server.resize_and_confirm(auth, input_dict)
        if(rs == 'OK'):
            out['status'] = 'success'
            out['message'] = 'Successfully resized instance %s'%(serv_info['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def reboot(request, project_id, instance_id):
    out = {}
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

def power_off_server(request,project_id,instance_id):
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

def power_on_server(request,project_id,instance_id):
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
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        input_dict = {'project_id':project_id, 'instance_id':instance_id, 'migration_type':'live', 'openstack_host_id':host_name}
        out = migration.migrate_instance(auth, input_dict)
        out['status'] = 'success'
        out['message'] = 'Successfully live migrated instance %s'%(out['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def migrate_server(request, project_id, instance_id):
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        input_dict = {'project_id':project_id, 'instance_id':instance_id}
        out = migration.migrate_instance(auth, input_dict)
        out['status'] = 'success'
        out['message'] = 'Successfully offline migrated instance %s'%(out['server_name'])
    except Exception as e:
        out = {"status":"error","message":"%s"%(e)}
    return HttpResponse(simplejson.dumps(out))

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
        out = l3o.update_floating_ip(update_dict)
        out['status'] = 'success'
        out['message'] = "Floating IP address %s was assigned to instance %s." % (floating_ip, out['instance_name'])
    except Exception, e:
        out = {'status' : "error", 'message' : "Error assigning Floating IP address %s, error: %s" % (floating_ip, e)}
    return HttpResponse(simplejson.dumps(out))

def unassign_floating_ip(request, floating_ip_id):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        ip = l3o.get_floating_ip(floating_ip_id)
        update_dict = {'floating_ip':ip['floating_ip'], 'instance_id':ip['instance_id'], 'project_id':ip['project_id'], 'action': 'remove'}
        out = l3o.update_floating_ip(update_dict)
        out['status'] = "success"
        out['message'] = "Floating IP address %s was unassigned from %s." %(ip['floating_ip'],out['instance_name'])
    except Exception as e:
        out = {'status' : "error", 'message' : "Error unassigning Floating IP %s address, error: %s" % (ip['floating_ip'], e)}
    return HttpResponse(simplejson.dumps(out))

def toggle_user(request, username, toggle):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'toggle':toggle}
        out = uo.toggle_user(user_dict)
        out['status'] = 'success'
        out['message'] = 'The user has been toggled to %s'%(toggle)
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not toggle the user %s to %s: %s"%(toggle,username,e)}
    return HttpResponse(simplejson.dumps(out))

def delete_user(request, username, userid):
    out = {}
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'user_id':userid}
        del_user = uo.delete_user(user_dict)
        if(del_user == 'OK'):
            out['status'] = 'success'
            out['message'] = 'The user %s has been deleted'%(username)
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not delete the user %s: %s"%(username,e)}
    return HttpResponse(simplejson.dumps(out))

def remove_user_from_project(request, user_id, project_id):
    out = {}
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'user_id': user_id, 'project_id':project_id}
        ru = uo.remove_user_from_project(user_dict)
        if(ru == 'OK'):
            out['status'] = 'success'
            out['message'] = 'The user has been removed from the project, but not deleted.'
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not remove the user from the project: %s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def add_existing_user(request, username, user_role, project_id):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'user_role':user_role, 'project_id': project_id, 'update_primary':True}
        out = uo.add_user_to_project(user_dict)
        out['status'] = 'success'
        out['message'] = 'The user %s has been added to the project.'%(username)
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not add the user %s to the project: %s"%(username,e)}
    return HttpResponse(simplejson.dumps(out))

def update_user_password(request, user_id, project_id, password):
    out = {}
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        passwd_dict = {'user_id': user_id, 'project_id':project_id, 'new_password': password }
        up = uo.update_user_password(passwd_dict)
        if(up == 'OK'):
            out['status'] = 'success'
            out['message'] = 'The password has been successfully updated.'
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not update the user password.: %s"%(e)}
    return HttpResponse(simplejson.dumps(out))

def update_admin_password(request, password):
    out = {}
    try:
        auth = request.session['auth']
        if auth['user_level'] == 0:
            ap = change_admin_password (auth, password)
            if(ap == 'OK'):
                out['status'] = 'success'
                out['message'] = 'The password has been successfully updated.'
        else:
            out = {'status' : "error", 'message' : "Only admins can update admin password"}
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not update admin password.: %s"%(e)}
    return HttpResponse(simplejson.dumps(out))

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
    sa = server_actions(auth)
    fo = flavor_ops(auth)
    i_dict = {'server_id': server_id, 'project_id': project_id}
    server = so.get_server(i_dict)
    flavors = fo.list_flavors()
    snapshots = sa.list_instance_snaps(server_id)

    return render_to_response('coal/instance_view.html',
                               RequestContext(request, {
                                                        'server': server,
                                                        'flavors': flavors,
                                                        'snapshots': snapshots,
                                                        'current_project_id': project_id,
                                                        }))

def add_private_network(request, net_name, admin_state, shared, project_id):
    try:
        auth = request.session['auth']
        no = neutron_net_ops(auth)
        create_dict = {"net_name": net_name, "admin_state": admin_state, "shared": shared, "project_id": project_id}
        out = no.add_private_network(create_dict)
        subnet_dict={"net_id": out['net_id'], "subnet_dhcp_enable": "true", "subnet_dns": ["8.8.8.8"]}
        out['subnet'] = no.add_net_subnet(subnet_dict)
        out['status'] = 'success'
        out['message'] = 'The network %s has been created.'%(net_name)
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not add the private network %s to the project: %s"%(net_name,e)}
    return HttpResponse(simplejson.dumps(out))

def remove_private_network(request, project_id, net_id):
    out = {}
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
        rn = no.remove_network(remove_dict)
        if(rn == 'OK'):
            out['status'] = 'success'
            out['message'] = 'The network has been removed.'
    except Exception as e:
        out = {'status' : "error", 'message' : "Could not remove the private network from the project: %s"%(e)}
    return HttpResponse(simplejson.dumps(out))

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
    return HttpResponse(simplejson.dumps(out))


# List all OpenStack containers for the given project ID.
def list_containers (request, project_id):
    try:
        auth = request.session['auth']
        auth['project_id'] = project_id
        args = Args (auth, "")

        container_con = ContainerConnection (args)
        container_list = container_con.list()
        out = {'status' : "success", 'containers' : container_list}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error getting list of containers: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Delete an OpenStack container with the given name for the given project ID.
def delete_container (request, name, project_id):
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
    return HttpResponse(simplejson.dumps(out))

# Upload a local file (object) to the given container.
def upload_local_object (request, container, filename, project_id, project_name, dummy1, dummy2, progress_id):
    from coalesce.coal_beta.models import ImportLocal

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
    try:
        support_create.DoCreate()
        out = {'status' : "success", 'message' : "Support data has been sent to TransCirrus."}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error collecting/sending support data: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Call the routine that will upgrade all nodes to the given version of software.
def upgrade (request, version="stable"):
    try:
        upgrade.ReleaseToDownload = version
        upgrade.DoUpgrade()
        out = {'status' : "success", 'message' : "Nodes have been upgraded."}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error upgrading nodes: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# --- Routines for 3rd party storage ---

# Return the names of supported 3rd party storage providers and if they are configured (enabled).
def supported_third_party_storage (request):
    '''
        returns json:
            status:
                success
                    providers: array of dict [{'name': "nfs", 'configured': "0"},
                                              {'name': "NetApp E-Series", 'configured': "1"}
                                             ]
                                             name: 3rd party storage name
                                             configured: 0/1
                                                         0 - storage provider is not currently configured
                                                         1 - storage provider is currently configured
                error
                    message: error message
    '''
    try:
        providers = tpc.get_supported_third_party_storage()
        out = {'status' : "success", 'providers' : providers}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error getting supported 3rd party storage providers: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# --- Routines for E-Series ---

# Return E-Series configuration data.
def eseries_get (request):
    '''
        returns json:
            status:
                success
                    data: dict {'enabled':      "0/1",           "0" not enabled or "1" is enabled
                                'pre_existing': "0/1",            "0" - not using pre-existing server; "1" - using pre-existing web proxy srv
                                'server':  "server hostname/IP",  web proxy server IP address/hostname
                                'srv_port': "listen port",        normally 8080 or 8443
                                'transport': "transport",         http/https
                                'login': "username",              username into web proxy
                                'pwd': "password",                password for user
                                'ctrl_pwd': "ctrl-password",      password into storage controller(s); "" is valid if no password is set
                                'ctrl_ips': ["ip1", "ip2"],       mgmt IP/hostnames for storage controllers
                                'disk_pools': ["pool1", "pool2"]  disk/storage pools
                               }
                error
                    message: error message
    '''
    try:
        data = tpc.get_eseries()
        out = {'status' : "success", 'data' : data}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error getting NetApp E-Series configuration data: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Delete E-Series configuration.
def eseries_delete (request):
    '''
        returns json:
            status:
                success
                    message: success message
                error
                    message: error message
    '''
    try:
        auth = request.session['auth']
        tpc.delete_eseries (auth)
        out = {'status' : "success", 'message' : "NetApp E-Series configuration has been deleted."}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error deleting NetApp E-Series configuration: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Setup the E-Series web proxy server with the given data and return the configured IP addresses.
# If we are using a pre-existing web proxy then the remaining input is ignored.
def eseries_set_web_proxy_srv (request, pre_existing, server, srv_port, transport, login, pwd):
    '''
        input:
            pre_existing: "0/1"                 0 - not using pre-existing web proxy; 1 using pre-existy web proxy
            The remaining inputs are relevant only if pre_existing = "1"
            server:       "server hostname/IP"  web proxy server IP address/hostname
            srv_port:     "listen port"         normally 8080 or 8443
            transport:    "transport"           http/https
            login:        "username"            username into web proxy
            pwd:          "password"            password for user
        returns json:
            status:
                success
                    ips: array of IP addresses ["ip1", "ip2", "ip3"]
                error
                    message: error message
    '''
    global eseries_config
    service_path = "/devmgr/v2"         # Hard coded path since most users will not change the default

    try:
        if pre_existing == "1":
            eseries_config = eseries_mgmt (transport, server, srv_port, service_path, login, pwd)
        else:
            data = {}
            data = tpc.get_eseries_pre_existing_data (data)
            eseries_config = eseries_mgmt (data['transport'], data['server'], data['srv_port'], data['service_path'], data['login'], data['pwd'])

        storage_systems = eseries_config.get_storage_systems()
        for system in storage_systems:
            if system['name'] == "":
                continue
            found_ips = eseries_config.get_storage_system_ips (system['id'])

        out = {'status' : "success", 'ips' : found_ips}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error setting NetApp E-Series web proxy configuration: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Set the E-Series controller password and IP addresses and return the configured disk/storage pools.
def eseries_set_controller (request, ctrl_ips, ctrl_pwd=None):
    '''
        input:
            ctrl_pwd: "ctrl-password"   password for storage controller(s); "" is valid if no password is set
            ctrl_ips: "ip1,ip2"         mgmt IP/hostnames for storage controllers
        returns json:
            status:
                success
                    disk_pools: array of dict [{'name': "pool1", 'free': "10", 'total': "100"},
                                               {'name': "pool2", 'free': "10", 'total': "100"}
                                               {'name': "pool3", 'free': "10", 'total': "100"}
                                              ]
                                              name: disk/storage pool name
                                              free: free space on disk pool in GigaBytes
                                              total: total space on disk pool in GigaBytes
                error
                    message: error message
    '''
    global eseries_config

    try:
        ips = ctrl_ips.split(",")
        if (ctrl_pwd == None):
            password = ""
        else:
            password = ctrl_pwd

        eseries_config.set_ctrl_password_and_ips (password, ips)
        disks = eseries_config.get_storage_pools()

        pools = []
        for disk in disks:
            free_capacity_gb = 0
            total_capacity_gb = 0
            usage = eseries_config.get_pool_usage (disk['id'])
            pools.append ({'name': disk['label'], 'free': usage['free_capacity_gb'], 'total': usage['total_capacity_gb']})

        out = {'status' : "success", 'pools' : pools}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error setting NetApp E-Series controller data: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Set the E-Series disk pools and commit the configuration.
def eseries_set_config (request, disk_pools):
    '''
        input:
            disk_pools: "pool1,pool2"   disk/storage pools
        returns json:
            status:
                success
                    message: success message
                error
                    message: error message
    '''
    try:
        auth = request.session['auth']

        storage_pools = disk_pools.split(",")
        eseries_config.set_storage_pools (storage_pools)

        data = {'server':     eseries_config.server,
                'srv_port':   eseries_config.port,
                'transport':  eseries_config.scheme,
                'login':      eseries_config.username,
                'pwd':        eseries_config.password,
                'ctrl_pwd':   eseries_config.ctrl_password,
                'ctrl_ips':   eseries_config.ctrl_ips,
                'disk_pools': eseries_config.storage_pools}
        if eseries_config.server == "localhost":
            pre_existing = False
        else:
            pre_existing = True
        tpc.add_eseries (data, auth, pre_existing=pre_existing)

        out = {'status' : "success", 'message' : "NetApp E-Series storage has been successfully added"}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error applying NetApp E-Series configuration: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Update the E-Series web proxy server and cinder with the given data.
# If we are using a pre-existing web proxy then the web proxy server data is ignored.
def eseries_update (request, pre_existing, server, srv_port, transport, login, pwd, ctrl_pwd, ctrl_ips, disk_pools):
    '''
        input:
            pre_existing: "0/1"                 0 - not using pre-existing web proxy; 1 using pre-existy web proxy
            The following are relevant only if pre_existing = "1"
              server:     "server hostname/IP"  web proxy server IP address/hostname
              srv_port:   "listen port"         normally 8080 or 8443
              transport:  "transport"           http/https
              login:      "username"            username into web proxy
              pwd:        "password"            password for user
            The remaining are required
              ctrl_pwd:   "ctrl-password"       password for storage controller(s); "" is valid if no password is set
              ctrl_ips:   "ip1,ip2"             mgmt IP/hostnames for storage controllers
              disk_pools: "pool1,pool2"         disk/storage pools
        returns json:
            status:
                success
                    message: success message
                error
                    message: error message
    '''
    global eseries_config

    try:
        if pre_existing == "1":
            existing = True
        else:
            existing = False

        ips = ctrl_ips.split(",")
        storage_pools = disk_pools.split(",")

        data = {'server': server, 'srv_port': srv_port, 'transport': transport,  'login': login, 'pwd': pwd, 'ctrl_pwd': ctrl_pwd, 'disk_pools': storage_pools, 'ctrl_ips': ips}
        tpc.update_eseries (data, existing)

        out = {'status' : "success", 'message' : "NetApp E-Series storage has been successfully updated"}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error updating NetApp E-Series configuration: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Get E-Series statistics for disk pools.
def eseries_stats (request):
    '''
        input:
        returns json:
            status:
                success
                    stats: dict - defination TBD
                error
                    message: error message
    '''
    global eseries_config
    service_path = "/devmgr/v2"         # Hard coded path since most users will not change the default

    try:
        auth = request.session['auth']

        if eseries_config == None:
            data = tpc.get_eseries()
            if data['enabled'] != "1":
                out = {'status' : "error", 'message' : "Error getting E-Series statistics, web proxy server is not configured"}
                return HttpResponse(simplejson.dumps(out))

            eseries_config = eseries_mgmt (data['transport'], data['server'], data['srv_port'], service_path, data['login'], data['pwd'])
            eseries_config.set_ctrl_password_and_ips (data['ctrl_pwd'], data['ctrl_ips'])
            eseries_config.set_storage_pools (data['disk_pools'])

        stats = {}
        stats['title'] = "Disk Pool Usage"
        data  = []

        pools = eseries_config.get_storage_pools()
        for pool in pools:
            pool_usage = eseries_config.get_pool_usage (pool['id'])

            vol_stats = {}
            vol_stats['origin'] = pool['label']
            vol_stats['volumeName'] = "free-space"
            vol_stats['usage'] = pool_usage['free_capacity_gb']
            vol_stats['type'] = "thick"
            data.append(vol_stats)

            volumes = eseries_config.get_volumes()
            for volume in volumes:
                if volume['volumeGroupRef'] == pool['volumeGroupRef']:
                    vol_capacity_gb = int(volume['capacity'], 0) / eseries_config.GigaBytes

                    vol_name = eseries_config.convert_vol_name(volume['label'], auth)
                    vol_stats = {}
                    vol_stats['origin'] = pool['label']
                    vol_stats['volumeName'] = vol_name
                    vol_stats['usage'] = vol_capacity_gb
                    vol_stats['max'] = 0
                    vol_stats['type'] = "thick"
                    data.append(vol_stats)

                    if volume['label'].find("repos_") == 0:                     # THIS IS A HACK! Must find a better method of
                        thin_volumes = eseries_config.get_thin_volumes()        # determining if the volume is for holding TP volumes.
                        for thin in thin_volumes:
                            if thin['storageVolumeRef'] == volume['volumeRef']:
                                capacity_gb = vol_capacity_gb
                                provisioned_gb = int(thin['currentProvisionedCapacity'], 0) / eseries_config.GigaBytes
                                quota_gb = int(thin['provisionedCapacityQuota'], 0) / eseries_config.GigaBytes

                                thin_name = eseries_config.convert_vol_name(thin['label'], auth)
                                vol_stats = {}
                                vol_stats['origin'] = vol_name
                                vol_stats['volumeName'] = thin_name
                                vol_stats['usage'] = capacity_gb
                                vol_stats['max'] = quota_gb
                                data.append(vol_stats)

                        vol_stats = {}
                        vol_stats['origin'] = volume['label']
                        vol_stats['volumeName'] = "provisioned"
                        vol_stats['usage'] = quota_gb - provisioned_gb
                        vol_stats['max'] = quota_gb
                        data.append(vol_stats)

        stats['data'] = data
        out = {'status' : "success", 'stats' : stats}

    except Exception, e:
        out = {'status' : "error", 'message' : "Error getting NetApp E-Series statistics: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Get E-Series statistics for disk pools.
def eseries_add_license (request, license_key):
    '''
        input:
            license_key - a valid E-Series license key
        returns json:
            status:
                success
                    message: success message
                error
                    message: error message
    '''
    try:
        if tpc.add_eseries_license (license_key):
            out = {'status' : "success", 'message' : "NetApp E-Series storage license has been added."}
        else:
            out = {'status' : "error", 'message' : "Error: Invalid NetApp E-Series storage license key."}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error adding NetApp E-Series storage license: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# --- Routines for NFS ---

# Return NFS configuration data.
def nfs_get (request):
    '''
        returns json:
            status:
                success
                    data: dict {'enabled':    "0/1",                "0" not enabled or "1" is enabled
                                'mountpoint': ["mntpt1", "mntpt2"]  array of mountpoints
                error
                    message: error message
    '''
    try:
        data = tpc.get_nfs()
        out = {'status' : "success", 'data' : data}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error getting NFS configuration data: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Delete NFS configuration.
def nfs_delete (request):
    '''
        returns json:
            status:
                success
                    message: success message
                error
                    message: error message
    '''
    try:
        auth = request.session['auth']
        tpc.delete_nfs (auth)
        out = {'status' : "success", 'message' : "NFS configuration has been deleted."}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error deleting NFS configuration: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Setup NFS in cinder with the given mountpoint(s).
def nfs_set (request, mountpoints):
    '''
        input:
            mountpoints: array of mountpoints ["mntpt1", "mntpt2", "mntpt3"]
        returns json:
            status:
                success
                    message: success message
                error
                    message: error message
    '''
    try:
        auth = request.session['auth']
        mntpts = mountpoints.split(",")
        tpc.add_nfs (mntpts, auth)
        out = {'status' : "success", 'message' : "NFS storage has been successfully added"}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error adding NFS storage: %s" % e}
    return HttpResponse(simplejson.dumps(out))


# Update NFS in cinder with the given mountpoint(s).
def nfs_update (request, mountpoints):
    '''
        input:
            mountpoints: array of mountpoints ["mntpt1", "mntpt2", "mntpt3"]
        returns json:
            status:
                success
                    message: success message
                error
                    message: error message
    '''
    try:
        mntpts = mountpoints.split(",")
        tpc.update_nfs (mntpts)
        out = {'status' : "success", 'message' : "NFS storage has been successfully updated"}
    except Exception, e:
        out = {'status' : "error", 'message' : "Error updating NFS storage: %s" % e}
    return HttpResponse(simplejson.dumps(out))

# ---

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
            uplink_subnet          = form.cleaned_data['uplink_subnet']
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
                                {"system_name": system, "parameter": "admin_api_ip",       "param_value": "172.24.24.10"},
                                {"system_name": system, "parameter": "int_api_id",         "param_value": "172.24.24.10"},
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
            dns = []
            dns.append(subnet_dns)

            dns = []
            dns.append(subnet_dns)
            auth = request.session['auth']
            project_var_array = {'project_name': proj_name,
                                 'user_dict': { 'username': username,
                                                'password': password,
                                                'user_role': 'pu',
                                                'email': email,
                                                'project_id': ''},

                                 'net_name':net_name,
                                 'subnet_dns': dns,
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

#HTTP Status Codes
#
# def handler404(request):
#     response = render_to_response('404/', {},
#                                   context_instance=RequestContext(request))
#     response.status_code = 404
#     return response
#
#
# def handler500(request):
#     response = render_to_response('500/', {},
#                                   context_instance=RequestContext(request))
#     response.status_code = 500
#     return response