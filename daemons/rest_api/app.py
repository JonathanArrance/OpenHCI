# base
import ast, json, sys
# flask
from flask import Flask, jsonify, abort, make_response, request
from werkzeug.exceptions import HTTPException
from flasgger import Swagger
# django
from django.conf import settings
from transcirrus.interfaces.Coalesce import settings as tc_settings
settings.configure(default_settings=tc_settings, DEBUG=True, LOGGING_CONFIG=None, DATABASE_ROUTERS=[], USE_TZ=False, DEFAULT_INDEX_TABLESPACE="", CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',}},
                   DEFAULT_TABLESPACE="", USE_L10N=True, LOCALE_PATHS=(), FORMAT_MODULE_PATH=None, DEFAULT_CHARSET="utf-8", DEFAULT_CONTENT_TYPE="text/html")
sys.path.append("/usr/local/lib/python2.7/transcirrus/interfaces/Coalesce/")
from transcirrus.interfaces.Coalesce.coalesce.coal_beta import views
# common
from transcirrus.common import util
from transcirrus.common.auth import authorization
from transcirrus.common import extras
# projects
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.operations import build_complete_project
# instances
from transcirrus.component.nova.server import server_ops
# networks
from transcirrus.component.neutron.network import neutron_net_ops

# --- API Setup ----

app = Flask(__name__)
Swagger(app)
node_id = util.get_node_id()
api_ip = util.get_system_variables(node_id)['MGMT_IP']


# --- Error Handlers ----

@app.errorhandler(401)
def not_authorized(error):
    return make_response(jsonify({'error': {'message': "Not authorized.  Check your credentials and user privileges.", 'number': 401}}), 401)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': {'message': "Not found.", 'number': 404}}), 404)


@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': {'message': "Internal server error.", 'number': 500}}), 500)


# --- Version Info ----

@app.route("/v1.0/version", methods=['GET'])
def get_version():
    request = ""
    ver_json = views.get_version(request)
    ver_dict = ast.literal_eval(ver_json.content)
    version = {'success': {}}
    version['success'] = {'release': ver_dict['data']['release'], 'major': ver_dict['data']['major'], 'full_str': ver_dict['data']['full_str'], 'short_str': ver_dict['data']['short_str'], 'minor': ver_dict['data']['minor']}
    #print "version: %s" % version
    return jsonify({'version': version})
    #return (ver_json.content)


# --- Projects ----

# get all
@app.route('/v1.0/projects', methods=['GET'])
def get_projects():
    """
    Lists all projects.
    Only returns projects to which the specified user has access.
    ---
    tags:
      - projects
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: Useranme of user making request.
      - name: password
        in: header
        type: string
        required: true
        description: Password of user making request.
    responses:
        200:
            description: Projects listed.
            schema:
                type: array
                id: Projects
                items:
                    schema:
                        type: object
                        id: Project
                        required:
                            - name
                            - id
                        properties:
                            name:
                                type: string
                                description: name of project
                                default: Project_1
                            id:
                                type: string
                                description: ID of project
                                default: abcd12e3f456789012345a678b9cde01
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        to = tenant_ops(auth)
        projects = []
        if auth['is_admin'] == 1:
            projects = to.list_all_tenants()
        else:
            project = to.get_tenant(auth['project_id'])
            projects = [{
                            'name': project['project_name'],
                            'id':   project['project_id']
                       }]
        projects[:] = [p for p in projects if p.get('project_name') != "trans_default"]
        return jsonify({'projects': projects})
    except HTTPException as e:
        raise e
    except:
        abort(500)


# get
@app.route('/v1.0/projects/<string:project_id>', methods=['GET'])
def get_project(project_id):
    """
    Gets detailed information about a specified project by ID.
    Only returns project information to which the specified user has access.
    ---
    tags:
      - projects
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: Useranme of user making request.
      - name: password
        in: header
        type: string
        required: true
        description: Password of user making request.
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of desired project.
    responses:
        200:
            description: Project found.
            schema:
                type: object
                id: ProjectDetails
                required:
                    - name
                    - id
                    - security_key_name
                    - security_key_id
                    - security_group_name
                    - security_group_id
                    - host_system_name
                    - host_system_ip
                    - network_name
                    - network_id
                    - is_default
                properties:
                    name:
                        type: string
                        description: name of project
                        default: Project_1
                    id:
                        type: string
                        description: ID of project
                        default: abcd12e3f456789012345a678b9cde01
                    security_key_name:
                        type: string
                        description: name of default security key
                        default: Security_Key_1
                    security_key_id:
                        type: string
                        description: ID of default security key
                        default: a1:23:45:b6:78:90:12:34:5c:d6:e7:fa:bc:de:fa:89
                    security_group_name:
                        type: string
                        description: name of default security group
                        default: Security_Group_1
                    security_group_id:
                        type: string
                        description: ID of default security group
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    host_system_name:
                        type: string
                        description: name of host system
                        default: transcirrus-core
                    host_system_ip:
                        type: string
                        description: ip address of host system
                        default: 127.0.0.1
                    network_name:
                        type: string
                        description: name of default network
                        default: Network_1
                    network_id:
                        type: string
                        description: ID of default network
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    is_default:
                        type: string
                        description: third party authentication default type
                        default: LDAP
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        to = tenant_ops(auth)
        project_info = to.get_tenant(project_id)
        project = {
                        'name':                     project_info['project_name'],
                        'id':                       project_info['project_id'],
                        'security_key_name':        project_info['def_security_key_name'],
                        'security_key_id':          project_info['def_security_key_id'],
                        'security_group_name':      project_info['def_security_group_name'],
                        'security_group_id':        project_info['def_security_group_id'],
                        'host_system_name':         project_info['host_system_name'],
                        'host_system_ip':           project_info['host_system_ip'],
                        'network_name':             project_info['def_network_name'],
                        'network_id':               project_info['def_network_id'],
                        'is_default':               project_info['is_default']
                   }
        return jsonify({'project': project})
    except HTTPException as e:
        raise e
    except:
        abort(500)


# create
@app.route('/v1.0/projects', methods=['POST'])
def create_project():
    """
    Creates a specified a project.
    Only available to admins.
    ---
    tags:
      - projects
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: Useranme of user making request.
      - name: password
        in: header
        type: string
        required: true
        description: Password of user making request.
      - name: project_parameters
        in: body
        description: Parameters for project creation.
        required: true
        schema:
            id: ProjectParameters
            type: object
            required:
              - project_name
              - admin_username
              - admin_password
              - admin_email
              - security_group_name
              - security_key_name
              - network_name
              - router_name
              - dns_address
            properties:
                project_name:
                    type: string
                    description: Name for project.
                admin_username:
                    type: string
                    description: Username for project admin.
                admin_password:
                    type: string
                    description: Password for project admin.
                admin_email:
                    type: string
                    description: Email for project admin.
                security_group_name:
                    type: string
                    description: Nanme for project's default security group.
                security_key_name:
                    type: string
                    description: Name for project's default security key.
                network_name:
                    type: string
                    description: Name for project's default network.
                router_name:
                    type: string
                    description: Name for project's default router.
                dns_address:
                    type: string
                    description: Subnet DNS address for project.
    responses:
        200:
            description: Project created.
            schema:
                id: Project
                type: object
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        data = request.get_data()
        json_data = json.loads(data)
        project_name = json_data['project_name']
        admin_username = json_data['admin_username']
        admin_password = json_data['admin_password']
        admin_email = json_data['admin_email']
        security_group_name = json_data['security_group_name']
        security_key_name = json_data['security_key_name']
        network_name = json_data['network_name']
        router_name = json_data['router_name']
        dns_address = json_data['dns_address']
        project_create =   {
                        'project_name':     project_name,
                        'user_dict':        {
                                                'username':     admin_username,
                                                'password':     admin_password,
                                                'user_role':    "admin",
                                                'email':        admin_email,
                                                'project_id':   ""
                                            },
                        'net_name':         network_name,
                        'subnet_dns':       dns_address,
                        'sec_group_dict':   {
                                                'ports':        "",
                                                'group_name':   security_group_name,
                                                'group_desc':   "none",
                                                'project_id':   ""
                                            },
                        'sec_keys_name':    security_key_name,
                        'router_name':      router_name
                    }
        project_id = build_complete_project.build_project(auth, project_create)
        project =   {
                        'name': project_name,
                        'id':   project_id
                    }
        return jsonify(project)
    except HTTPException as e:
        raise e
    except:
        abort(500)


# --- Instances ----

# get all
@app.route('/v1.0/instances', methods=['GET'])
def get_instances():
    """
    Lists all instances.
    Only returns instances to which the specified user has access.
    ---
    tags:
      - instances
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: Useranme of user making request.
      - name: password
        in: header
        type: string
        required: true
        description: Password of user making request.
    responses:
        200:
            description: Instances listed.
            schema:
                type: array
                id: Instances
                items:
                    schema:
                        type: object
                        id: Instance
                        required:
                            - name
                            - id
                            - project_id
                            - floating_ip
                            - status
                            - zone
                        properties:
                            name:
                                type: string
                                description: name of instance
                                default: Instance_1
                            id:
                                type: string
                                description: ID of instance
                                default: 1234a56b-8901-2345-67c8-90de12f34ab5
                            project_id:
                                type: string
                                description: ID of project
                                default: abcd12e3f456789012345a678b9cde01
                            floating_ip:
                                type: string
                                description: floating ip address of instance
                                default: 127.0.0.1
                            status:
                                type: string
                                description: status of instance
                                default: ACTIVE
                            zone:
                                type: string
                                description: availability zone of instance
                                default: nova
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        so = server_ops(auth)
        instances = []
        instances_info = []
        if auth['is_admin'] == 1:
            instances_info = so.list_all_servers()
        else:
            instances_info = so.list_servers(auth['project_id'])
        for instance in instances_info:
            instance =  {
                            "project_id":       instance['project_id'],
                            "floating_ip":      instance['public_ip'],
                            "instance_id":      instance['server_id'],
                            "instance_name":    instance['server_name'],
                            "status":           instance['status'],
                            "zone":             instance['zone']
                        }
            instances.append(instance)
        return jsonify({'instances': instances})
    except HTTPException as e:
        raise e
    except:
        abort(500)


# get
@app.route('/v1.0/instances/<string:instance_id>', methods=['GET'])
def get_instance(instance_id):
    """
    Gets detailed information about a specified instance by ID.
    Only returns project information to which the specified user has access.
    ---
    tags:
      - instances
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: Useranme of user making request.
      - name: password
        in: header
        type: string
        required: true
        description: Password of user making request.
      - name: instance_id
        in: path
        type: string
        required: true
        description: ID of desired instance.
    responses:
        200:
            description: Instance found.
            schema:
                type: object
                id: InstanceDetails
                required:
                    - name
                    - id
                    - project_id
                    - security_key_name
                    - security_group_name
                    - specification_name
                    - specification_id
                    - os
                    - external_network_id
                    - network_info
                    - zone
                    - status
                    - state
                    - physical_node_id
                    - floating_ip
                    - floating_ip_id
                    - novnc_console
                    - date_created
                    - boot_from_volume
                    - fault
                properties:
                    name:
                        type: string
                        description: name of instance
                        default: Instance_1
                    id:
                        type: string
                        description: ID of instance
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    project_id:
                        type: string
                        description: ID of instance's project
                        default: abcd12e3f456789012345a678b9cde01
                    security_key_name:
                        type: string
                        description: name of instance's security key
                        default: Security_Key_1
                    security_group_name:
                        type: string
                        description: name of instance's security group
                        default: Security_Group_1
                    specification_name:
                        type: string
                        description: name of instance's specification
                        default: m1.tiny
                    specification_id:
                        type: string
                        description: ID of instance's specification
                        default: "1"
                    os:
                        type: string
                        description: OS of instance
                        default: CentOS-65-x86_64
                    network_info:
                        type: object
                        description: network information of instance
                        schema:
                            type: object
                            id: NetworkInfo
                            required:
                              - InternalNetworks
                              - ExternalNetworks
                            properties:
                                InternalNetworks:
                                    type: array
                                    items:
                                        schema:
                                            type: object
                                            id: InternalNetwork
                                            required:
                                              - name
                                              - id
                                              - OS-EXT-IPS-MAC:mac_addr
                                              - OS-EXT-IPS:type
                                              - addr
                                              - version
                                            properties:
                                                name:
                                                    type: string
                                                    description: name of network
                                                    default: Network_1
                                                id:
                                                    type: string
                                                    description: ID of network
                                                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                                                OS-EXT-IPS-MAC:mac_addr:
                                                    type: string
                                                    description: mac address of network port
                                                    default: ab:12:3c:4d:ef:5a
                                                OS-EXT-IPS:type:
                                                    type: string
                                                    description: address type
                                                    default: fixed
                                                addr:
                                                    type: string
                                                    description: ip address of instance
                                                    default: 10.0.1.7
                                                version:
                                                    type: integer
                                                    description: ip version
                                                    default: 4
                                ExternalNetworks:
                                    type: array
                                    items:
                                        schema:
                                            type: object
                                            id: ExternalNetwork
                                            required:
                                              - name
                                              - id
                                              - OS-EXT-IPS-MAC:mac_addr
                                              - OS-EXT-IPS:type
                                              - addr
                                              - version
                                            properties:
                                                name:
                                                    type: string
                                                    description: name of network
                                                    default: Network_1
                                                id:
                                                    type: string
                                                    description: ID of network
                                                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                                                OS-EXT-IPS-MAC:mac_addr:
                                                    type: string
                                                    description: mac address of network port
                                                    default: ab:12:3c:4d:ef:5a
                                                OS-EXT-IPS:type:
                                                    type: string
                                                    description: address type
                                                    default: floating
                                                addr:
                                                    type: string
                                                    description: ip address of instance
                                                    default: 10.0.1.7
                                                version:
                                                    type: integer
                                                    description: ip version
                                                    default: 4
                    zone:
                        type: string
                        description: availability zone of instance
                        default: nova
                    status:
                        type: string
                        description: status of instance
                        default: ACTIVE
                    state:
                        type: string
                        description: state of instance
                        default: active
                    physical_node_id:
                        type: string
                        description: ID of physical node hosting instance
                        default: abc1def2ab34567890cd12ef34abc56d789012ef3456a78901bc2de3
                    floating_ip:
                        type: string
                        description: floating ip address of instance
                        default: 127.0.0.1
                    floating_ip_id:
                        type: string
                        description: ID of instance's floating ip address
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    novnc_console:
                        type: string
                        description: url of instance's novnc console
                        default: http://127.0.0.1:6080/vnc_auto.html?token=1234a56b-8901-2345-67c8-90de12f34ab5
                    date_created:
                        type: string
                        description: date of instance creation
                        default: "2015-10-02T19:28:33Z"
                    boot_from_volume:
                        type: boolean
                        description: conveying if instance boots from volume
                        default: false
                    fault:
                        type: string
                        description: fault of instance
                        default: None
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        so = server_ops(auth)
        nno = neutron_net_ops(auth)
        get_server_dict =   {
                                'server_id':    instance_id,
                                'project_id':   auth['project_id']
                            }
        instance_info = so.get_server(get_server_dict)
        internal = []
        external = []
        net_id = instance_info['server_net_id']
        net_name = nno.get_network(net_id)['net_name']
        for info in instance_info['server_int_net'][net_name]:
            if info['OS-EXT-IPS:type'] == "fixed":
                info['name'] = net_name
                info['id'] = net_id
                internal.append(info)
            elif info['OS-EXT-IPS:type'] == "floating":
                info['name'] = net_name
                info['id'] = net_id
                external.append(info)
        boot_from_volume = False
        if instance_info['boot_from_vol'] == "true":
            boot_from_volume = True
        instance = {
                        'name':                 instance_info['server_name'],
                        'id':                   instance_info['server_id'],
                        'project_id':           instance_info['project_id'],
                        'security_key_name':    instance_info['server_key_name'],
                        'security_group_name':  instance_info['server_group_name'],
                        'specification_id':     instance_info['flavor_id'],
                        'specification_name':   instance_info['server_flavor'],
                        'os':                   instance_info['server_os'],
                        'network_info':         {
                                                    'internal': internal,
                                                    'external': external
                                                },
                        'zone':                 instance_info['server_zone'],
                        'status':               instance_info['server_status'],
                        'state':                instance_info['server_state'],
                        'physical_node_id':     instance_info['server_node'],
                        'floating_ip_id':       instance_info['floating_ip_id'],
                        'floating_ip':          instance_info['server_public_ips'],
                        'novnc_console':        instance_info['novnc_console'],
                        'date_created':         instance_info['date_created'],
                        'boot_from_volume':     boot_from_volume
                   }
        return jsonify({'instance': instance})
    except HTTPException as e:
        raise e
    except Exception as fe:
        print fe
        abort(500)


# --- Helper Functions ----

def authorize(username, password):
    try:
        a = authorization(username,password)
        auth = a.get_auth()
        if auth['token'] != None and auth['token'] != "":
            return auth
        abort(401)
    except:
        abort(401)


if __name__ == '__main__':
    app.run(host=api_ip, port=6969, debug=True)
