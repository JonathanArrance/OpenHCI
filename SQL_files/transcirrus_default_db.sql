--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.10
-- Dumped by pg_dump version 9.2.0
-- Started on 2013-11-04 21:45:58 EST

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 213 (class 3079 OID 11645)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2167 (class 0 OID 0)
-- Dependencies: 213
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 161 (class 1259 OID 41404)
-- Name: cinder_default; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE cinder_default (
    parameter character varying,
    param_value character varying,
    file_name character varying,
    index integer NOT NULL
);


ALTER TABLE public.cinder_default OWNER TO transuser;

--
-- TOC entry 162 (class 1259 OID 41410)
-- Name: cinder_default_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE cinder_default_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cinder_default_index_seq OWNER TO transuser;

--
-- TOC entry 2168 (class 0 OID 0)
-- Dependencies: 162
-- Name: cinder_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE cinder_default_index_seq OWNED BY cinder_default.index;


--
-- TOC entry 2169 (class 0 OID 0)
-- Dependencies: 162
-- Name: cinder_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('cinder_default_index_seq', 23, true);


--
-- TOC entry 163 (class 1259 OID 41412)
-- Name: cinder_node; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE cinder_node (
    parameter character varying,
    param_value character varying,
    file_name character varying,
    node character varying,
    index integer NOT NULL
);


ALTER TABLE public.cinder_node OWNER TO transuser;

--
-- TOC entry 164 (class 1259 OID 41418)
-- Name: cinder_node_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE cinder_node_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cinder_node_index_seq OWNER TO transuser;

--
-- TOC entry 2170 (class 0 OID 0)
-- Dependencies: 164
-- Name: cinder_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE cinder_node_index_seq OWNED BY cinder_node.index;


--
-- TOC entry 2171 (class 0 OID 0)
-- Dependencies: 164
-- Name: cinder_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('cinder_node_index_seq', 3, true);


--
-- TOC entry 165 (class 1259 OID 41420)
-- Name: factory_defaults; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE factory_defaults (
    parameter character varying,
    param_value character varying,
    host_system character varying,
    index integer NOT NULL
);


ALTER TABLE public.factory_defaults OWNER TO transuser;

--
-- TOC entry 166 (class 1259 OID 41426)
-- Name: factory_defaults_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE factory_defaults_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.factory_defaults_index_seq OWNER TO transuser;

--
-- TOC entry 2172 (class 0 OID 0)
-- Dependencies: 166
-- Name: factory_defaults_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE factory_defaults_index_seq OWNED BY factory_defaults.index;


--
-- TOC entry 2173 (class 0 OID 0)
-- Dependencies: 166
-- Name: factory_defaults_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('factory_defaults_index_seq', 1, false);


--
-- TOC entry 167 (class 1259 OID 41428)
-- Name: glance_defaults; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE glance_defaults (
    parameter character varying,
    param_value character varying,
    host_name character varying,
    file_name character varying,
    index integer NOT NULL
);


ALTER TABLE public.glance_defaults OWNER TO transuser;

--
-- TOC entry 212 (class 1259 OID 49923)
-- Name: glance_defaults_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE glance_defaults_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.glance_defaults_index_seq OWNER TO transuser;

--
-- TOC entry 2174 (class 0 OID 0)
-- Dependencies: 212
-- Name: glance_defaults_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE glance_defaults_index_seq OWNED BY glance_defaults.index;


--
-- TOC entry 2175 (class 0 OID 0)
-- Dependencies: 212
-- Name: glance_defaults_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('glance_defaults_index_seq', 3, true);


--
-- TOC entry 168 (class 1259 OID 41434)
-- Name: keystone; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE keystone (
    index integer NOT NULL,
    paramter character varying,
    param_value character varying,
    host_system character varying,
    file_path character varying
);


ALTER TABLE public.keystone OWNER TO transuser;

--
-- TOC entry 169 (class 1259 OID 41440)
-- Name: net_adapter_settings; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE net_adapter_settings (
    index integer NOT NULL,
    net_adapter character varying,
    net_ip character varying,
    net_mask character varying,
    net_dns1 character varying DEFAULT '8.8.8.8'::character varying,
    net_dns2 character varying,
    net_dns3 character varying,
    node_id character varying,
    system_name character varying,
    net_slave_one character varying,
    net_slave_two character varying,
    inet_setting character varying,
    net_gateway character varying,
    net_mtu character varying,
    net_bond_master character varying,
    net_alias character varying,
    net_dns_domain character varying
);


ALTER TABLE public.net_adapter_settings OWNER TO transuser;

--
-- TOC entry 2176 (class 0 OID 0)
-- Dependencies: 169
-- Name: TABLE net_adapter_settings; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE net_adapter_settings IS 'All of the network settings used in the transcirrus system. This does not include the the virtual machine networks. Only for physical system network adapters. Table is set for all bonds when the system is installed';


--
-- TOC entry 2177 (class 0 OID 0)
-- Dependencies: 169
-- Name: COLUMN net_adapter_settings.net_alias; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN net_adapter_settings.net_alias IS 'this is an alias name ex. mgmt - management, uplink - uplink adapter - data - datanet adapter';


--
-- TOC entry 170 (class 1259 OID 41447)
-- Name: network_settings_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE network_settings_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.network_settings_index_seq OWNER TO transuser;

--
-- TOC entry 2178 (class 0 OID 0)
-- Dependencies: 170
-- Name: network_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE network_settings_index_seq OWNED BY net_adapter_settings.index;


--
-- TOC entry 2179 (class 0 OID 0)
-- Dependencies: 170
-- Name: network_settings_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('network_settings_index_seq', 1, true);


--
-- TOC entry 171 (class 1259 OID 41449)
-- Name: neutron_default; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE neutron_default (
    parameter character varying,
    param_value character varying,
    file_name character varying,
    index integer NOT NULL
);


ALTER TABLE public.neutron_default OWNER TO transuser;

--
-- TOC entry 172 (class 1259 OID 41455)
-- Name: neutron_default_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE neutron_default_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.neutron_default_index_seq OWNER TO transuser;

--
-- TOC entry 2180 (class 0 OID 0)
-- Dependencies: 172
-- Name: neutron_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE neutron_default_index_seq OWNED BY neutron_default.index;


--
-- TOC entry 2181 (class 0 OID 0)
-- Dependencies: 172
-- Name: neutron_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('neutron_default_index_seq', 3, true);


--
-- TOC entry 173 (class 1259 OID 41457)
-- Name: neutron_node; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE neutron_node (
    parameter character varying,
    param_value character varying,
    file_name character varying,
    node character varying,
    index integer NOT NULL
);


ALTER TABLE public.neutron_node OWNER TO transuser;

--
-- TOC entry 174 (class 1259 OID 41463)
-- Name: neutron_node_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE neutron_node_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.neutron_node_index_seq OWNER TO transuser;

--
-- TOC entry 2182 (class 0 OID 0)
-- Dependencies: 174
-- Name: neutron_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE neutron_node_index_seq OWNED BY neutron_node.index;


--
-- TOC entry 2183 (class 0 OID 0)
-- Dependencies: 174
-- Name: neutron_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('neutron_node_index_seq', 1, true);


--
-- TOC entry 175 (class 1259 OID 41465)
-- Name: nova_default; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE nova_default (
    parameter character varying,
    param_value character varying,
    file_name character varying,
    index integer NOT NULL
);


ALTER TABLE public.nova_default OWNER TO transuser;

--
-- TOC entry 2184 (class 0 OID 0)
-- Dependencies: 175
-- Name: TABLE nova_default; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE nova_default IS 'The default values for the nova config files. These are generally the values that are used on the ciac node.';


--
-- TOC entry 176 (class 1259 OID 41471)
-- Name: nova_default_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE nova_default_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.nova_default_index_seq OWNER TO transuser;

--
-- TOC entry 2185 (class 0 OID 0)
-- Dependencies: 176
-- Name: nova_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE nova_default_index_seq OWNED BY nova_default.index;


--
-- TOC entry 2186 (class 0 OID 0)
-- Dependencies: 176
-- Name: nova_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('nova_default_index_seq', 16, true);


--
-- TOC entry 177 (class 1259 OID 41473)
-- Name: nova_node; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE nova_node (
    parameter character varying,
    param_value character varying,
    file_name character varying,
    node character varying,
    index integer NOT NULL
);


ALTER TABLE public.nova_node OWNER TO transuser;

--
-- TOC entry 178 (class 1259 OID 41479)
-- Name: nova_node_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE nova_node_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.nova_node_index_seq OWNER TO transuser;

--
-- TOC entry 2187 (class 0 OID 0)
-- Dependencies: 178
-- Name: nova_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE nova_node_index_seq OWNED BY nova_node.index;


--
-- TOC entry 2188 (class 0 OID 0)
-- Dependencies: 178
-- Name: nova_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('nova_node_index_seq', 54, true);


--
-- TOC entry 179 (class 1259 OID 41481)
-- Name: projects; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE projects (
    proj_id character varying NOT NULL,
    proj_name character varying,
    def_security_key_name character varying,
    def_security_key_id character varying,
    def_security_group_id character varying,
    def_security_group_name character varying,
    host_system_name character varying,
    host_system_ip character varying,
    def_network_name character varying,
    def_network_id character varying
);


ALTER TABLE public.projects OWNER TO transuser;

--
-- TOC entry 2189 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN projects.def_security_key_name; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.def_security_key_name IS 'Default security key made during project creation';


--
-- TOC entry 2190 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN projects.def_security_key_id; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.def_security_key_id IS 'default security key id made at project creation';


--
-- TOC entry 2191 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN projects.host_system_name; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.host_system_name IS 'Name of the cloud controller';


--
-- TOC entry 2192 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN projects.host_system_ip; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.host_system_ip IS 'API ip associated with the cloud controller';


--
-- TOC entry 180 (class 1259 OID 41487)
-- Name: psql_buildout; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE psql_buildout (
    index bigint DEFAULT 0 NOT NULL,
    component character(1),
    command character varying
);


ALTER TABLE public.psql_buildout OWNER TO transuser;

--
-- TOC entry 181 (class 1259 OID 41494)
-- Name: swift_default; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE swift_default (
    paramter character varying,
    param_value character varying,
    host_name character varying,
    file_path character varying,
    index integer NOT NULL
);


ALTER TABLE public.swift_default OWNER TO transuser;

--
-- TOC entry 182 (class 1259 OID 41500)
-- Name: swift_default_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE swift_default_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.swift_default_index_seq OWNER TO transuser;

--
-- TOC entry 2193 (class 0 OID 0)
-- Dependencies: 182
-- Name: swift_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE swift_default_index_seq OWNED BY swift_default.index;


--
-- TOC entry 2194 (class 0 OID 0)
-- Dependencies: 182
-- Name: swift_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('swift_default_index_seq', 1, false);


--
-- TOC entry 183 (class 1259 OID 41502)
-- Name: swift_node; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE swift_node (
    parameter character varying,
    param_value character varying,
    file_name character varying,
    node character varying,
    index integer NOT NULL
);


ALTER TABLE public.swift_node OWNER TO transuser;

--
-- TOC entry 184 (class 1259 OID 41508)
-- Name: swift_node_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE swift_node_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.swift_node_index_seq OWNER TO transuser;

--
-- TOC entry 2195 (class 0 OID 0)
-- Dependencies: 184
-- Name: swift_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE swift_node_index_seq OWNED BY swift_node.index;


--
-- TOC entry 2196 (class 0 OID 0)
-- Dependencies: 184
-- Name: swift_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('swift_node_index_seq', 1, false);


--
-- TOC entry 210 (class 1259 OID 49899)
-- Name: system_default_settings; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE system_default_settings (
    parameter character varying,
    param_value character varying,
    host_system character varying,
    index integer NOT NULL
);


ALTER TABLE public.system_default_settings OWNER TO transuser;

--
-- TOC entry 2197 (class 0 OID 0)
-- Dependencies: 210
-- Name: TABLE system_default_settings; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE system_default_settings IS 'A read only system default table used to set the system back to the factory default settings.';


--
-- TOC entry 211 (class 1259 OID 49905)
-- Name: system_default_settings_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE system_default_settings_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.system_default_settings_index_seq OWNER TO transuser;

--
-- TOC entry 2198 (class 0 OID 0)
-- Dependencies: 211
-- Name: system_default_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE system_default_settings_index_seq OWNED BY system_default_settings.index;


--
-- TOC entry 2199 (class 0 OID 0)
-- Dependencies: 211
-- Name: system_default_settings_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('system_default_settings_index_seq', 1, false);


--
-- TOC entry 185 (class 1259 OID 41510)
-- Name: trans_floating_ip; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_floating_ip (
    index integer NOT NULL,
    floating_ip character varying,
    floating_ip_id character varying,
    proj_id character varying,
    router_id character varying,
    fixed_ip character varying
);


ALTER TABLE public.trans_floating_ip OWNER TO transuser;

--
-- TOC entry 186 (class 1259 OID 41516)
-- Name: trans_floating_ip_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_floating_ip_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_floating_ip_index_seq OWNER TO transuser;

--
-- TOC entry 2200 (class 0 OID 0)
-- Dependencies: 186
-- Name: trans_floating_ip_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_floating_ip_index_seq OWNED BY trans_floating_ip.index;


--
-- TOC entry 2201 (class 0 OID 0)
-- Dependencies: 186
-- Name: trans_floating_ip_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_floating_ip_index_seq', 1, false);


--
-- TOC entry 187 (class 1259 OID 41518)
-- Name: trans_instances; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_instances (
    proj_id character varying NOT NULL,
    in_use integer,
    floating_ip_id character varying,
    inst_id character varying NOT NULL,
    inst_port_id character varying,
    inst_key_name character varying,
    inst_sec_group_name character varying,
    inst_username character varying,
    inst_flav_name character varying,
    inst_floating_ip character varying,
    inst_ext_net_id character varying,
    inst_int_ip character varying,
    inst_int_net_id character varying,
    inst_int_net_name character varying,
    inst_image_name character varying,
    inst_name character varying
);


ALTER TABLE public.trans_instances OWNER TO transuser;

--
-- TOC entry 188 (class 1259 OID 41524)
-- Name: trans_network_settings; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_network_settings (
    net_name character varying,
    net_id character varying,
    user_id character varying,
    proj_id character varying,
    index integer NOT NULL,
    net_admin_state character varying,
    net_internal character varying,
    net_shared character varying
);


ALTER TABLE public.trans_network_settings OWNER TO transuser;

--
-- TOC entry 189 (class 1259 OID 41530)
-- Name: trans_network_settings_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_network_settings_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_network_settings_index_seq OWNER TO transuser;

--
-- TOC entry 2202 (class 0 OID 0)
-- Dependencies: 189
-- Name: trans_network_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_network_settings_index_seq OWNED BY trans_network_settings.index;


--
-- TOC entry 2203 (class 0 OID 0)
-- Dependencies: 189
-- Name: trans_network_settings_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_network_settings_index_seq', 43, true);


--
-- TOC entry 190 (class 1259 OID 41532)
-- Name: trans_nodes; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_nodes (
    node_id character varying NOT NULL,
    node_name character varying,
    node_type character varying,
    node_mgmt_ip character varying,
    node_data_ip character varying,
    node_controller character varying,
    node_cloud_name character varying,
    node_nova_zone character varying,
    node_iscsi_iqn character varying,
    node_swift_ring character varying,
    node_fault_flag character varying,
    node_ready_flag character varying
);


ALTER TABLE public.trans_nodes OWNER TO transuser;

--
-- TOC entry 2204 (class 0 OID 0)
-- Dependencies: 190
-- Name: COLUMN trans_nodes.node_controller; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_nodes.node_controller IS 'ciac system node is connected to';


--
-- TOC entry 2205 (class 0 OID 0)
-- Dependencies: 190
-- Name: COLUMN trans_nodes.node_cloud_name; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_nodes.node_cloud_name IS 'cloud name the node belongs to. ex RegionOne';


--
-- TOC entry 191 (class 1259 OID 41538)
-- Name: trans_routers; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_routers (
    index integer NOT NULL,
    router_name character varying,
    router_id character varying,
    net_id character varying,
    proj_id character varying,
    router_status integer DEFAULT 1,
    router_admin_state integer DEFAULT 1,
    router_ext_gateway character varying,
    router_ext_ip character varying
);


ALTER TABLE public.trans_routers OWNER TO transuser;

--
-- TOC entry 2206 (class 0 OID 0)
-- Dependencies: 191
-- Name: COLUMN trans_routers.router_status; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_routers.router_status IS 'Active=1';


--
-- TOC entry 2207 (class 0 OID 0)
-- Dependencies: 191
-- Name: COLUMN trans_routers.router_admin_state; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_routers.router_admin_state IS 'true=1';


--
-- TOC entry 192 (class 1259 OID 41546)
-- Name: trans_routers_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_routers_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_routers_index_seq OWNER TO transuser;

--
-- TOC entry 2208 (class 0 OID 0)
-- Dependencies: 192
-- Name: trans_routers_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_routers_index_seq OWNED BY trans_routers.index;


--
-- TOC entry 2209 (class 0 OID 0)
-- Dependencies: 192
-- Name: trans_routers_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_routers_index_seq', 1, false);


--
-- TOC entry 193 (class 1259 OID 41548)
-- Name: trans_security_group; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_security_group (
    index integer NOT NULL,
    proj_id character varying,
    user_name character varying,
    sec_group_id character varying,
    sec_group_name character varying
);


ALTER TABLE public.trans_security_group OWNER TO transuser;

--
-- TOC entry 194 (class 1259 OID 41554)
-- Name: trans_security_group_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_security_group_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_security_group_index_seq OWNER TO transuser;

--
-- TOC entry 2210 (class 0 OID 0)
-- Dependencies: 194
-- Name: trans_security_group_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_group_index_seq', 1, false);


--
-- TOC entry 195 (class 1259 OID 41556)
-- Name: trans_security_group_index_seq1; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_security_group_index_seq1
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_security_group_index_seq1 OWNER TO transuser;

--
-- TOC entry 2211 (class 0 OID 0)
-- Dependencies: 195
-- Name: trans_security_group_index_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_security_group_index_seq1 OWNED BY trans_security_group.index;


--
-- TOC entry 2212 (class 0 OID 0)
-- Dependencies: 195
-- Name: trans_security_group_index_seq1; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_group_index_seq1', 31, true);


--
-- TOC entry 196 (class 1259 OID 41558)
-- Name: trans_security_key_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_security_key_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_security_key_index_seq OWNER TO transuser;

--
-- TOC entry 2213 (class 0 OID 0)
-- Dependencies: 196
-- Name: trans_security_key_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_key_index_seq', 1, false);


--
-- TOC entry 197 (class 1259 OID 41560)
-- Name: trans_security_keys; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_security_keys (
    proj_id character varying,
    user_name character varying,
    sec_key_id character varying,
    sec_key_name character varying,
    public_key text,
    private_key text,
    index integer NOT NULL
);


ALTER TABLE public.trans_security_keys OWNER TO transuser;

--
-- TOC entry 2214 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN trans_security_keys.public_key; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_security_keys.public_key IS 'public key';


--
-- TOC entry 198 (class 1259 OID 41566)
-- Name: trans_security_keys_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_security_keys_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_security_keys_index_seq OWNER TO transuser;

--
-- TOC entry 2215 (class 0 OID 0)
-- Dependencies: 198
-- Name: trans_security_keys_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_keys_index_seq', 1, false);


--
-- TOC entry 199 (class 1259 OID 41568)
-- Name: trans_security_keys_index_seq1; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_security_keys_index_seq1
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_security_keys_index_seq1 OWNER TO transuser;

--
-- TOC entry 2216 (class 0 OID 0)
-- Dependencies: 199
-- Name: trans_security_keys_index_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_security_keys_index_seq1 OWNED BY trans_security_keys.index;


--
-- TOC entry 2217 (class 0 OID 0)
-- Dependencies: 199
-- Name: trans_security_keys_index_seq1; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_keys_index_seq1', 23, true);


--
-- TOC entry 200 (class 1259 OID 41570)
-- Name: trans_service_settings; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_service_settings (
    service_name character(20) NOT NULL,
    service_port integer,
    service_id character varying,
    service_type character varying,
    service_api_version character varying,
    service_desc character varying,
    service_admin_ip character varying,
    service_int_ip character varying,
    service_public_ip character varying,
    service_endpoint_id character varying
);


ALTER TABLE public.trans_service_settings OWNER TO transuser;

--
-- TOC entry 2218 (class 0 OID 0)
-- Dependencies: 200
-- Name: TABLE trans_service_settings; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE trans_service_settings IS 'ensure that when the install is done all values except service_ip and service_id are filled in';


--
-- TOC entry 201 (class 1259 OID 41576)
-- Name: trans_subnets; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_subnets (
    index integer NOT NULL,
    subnet_id character varying,
    subnet_class character(1),
    subnet_ip_ver character varying,
    subnet_cidr character varying,
    subnet_gateway character varying,
    subnet_allocation_start character varying,
    subnet_allocation_end character varying,
    subnet_dns character varying,
    net_id character varying,
    proj_id character varying,
    subnet_dhcp_enable character varying,
    in_use integer DEFAULT 0,
    subnet_name character varying,
    subnet_mask character varying
);


ALTER TABLE public.trans_subnets OWNER TO transuser;

--
-- TOC entry 202 (class 1259 OID 41583)
-- Name: trans_subnets_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_subnets_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_subnets_index_seq OWNER TO transuser;

--
-- TOC entry 2219 (class 0 OID 0)
-- Dependencies: 202
-- Name: trans_subnets_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_subnets_index_seq OWNED BY trans_subnets.index;


--
-- TOC entry 2220 (class 0 OID 0)
-- Dependencies: 202
-- Name: trans_subnets_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_subnets_index_seq', 2, true);


--
-- TOC entry 203 (class 1259 OID 41585)
-- Name: trans_system_settings; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_system_settings (
    parameter character varying,
    param_value character varying,
    host_system character varying,
    index integer NOT NULL
);


ALTER TABLE public.trans_system_settings OWNER TO transuser;

--
-- TOC entry 204 (class 1259 OID 41591)
-- Name: trans_system_settings_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_system_settings_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_system_settings_index_seq OWNER TO transuser;

--
-- TOC entry 2221 (class 0 OID 0)
-- Dependencies: 204
-- Name: trans_system_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_system_settings_index_seq OWNED BY trans_system_settings.index;


--
-- TOC entry 2222 (class 0 OID 0)
-- Dependencies: 204
-- Name: trans_system_settings_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_system_settings_index_seq', 51, true);


--
-- TOC entry 205 (class 1259 OID 41593)
-- Name: trans_system_snapshots; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_system_snapshots (
    snap_id character varying NOT NULL,
    vol_id character varying,
    proj_id character varying,
    snap_name character varying,
    snap_desc character varying
);


ALTER TABLE public.trans_system_snapshots OWNER TO transuser;

--
-- TOC entry 206 (class 1259 OID 41599)
-- Name: trans_system_vols; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_system_vols (
    vol_id character varying NOT NULL,
    proj_id character varying,
    keystone_user_uuid character varying,
    vol_name character varying,
    vol_size integer,
    vol_from_snapshot character varying DEFAULT false,
    vol_set_bootable character varying DEFAULT false,
    vol_attached character varying DEFAULT false,
    vol_attached_to_inst character varying
);


ALTER TABLE public.trans_system_vols OWNER TO transuser;

--
-- TOC entry 207 (class 1259 OID 41608)
-- Name: trans_user_info; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_user_info (
    index integer NOT NULL,
    user_name character varying,
    user_group_membership character varying,
    user_group_id integer,
    user_enabled character varying,
    keystone_user_uuid character varying,
    user_primary_project character varying,
    user_project_id character varying,
    keystone_role character varying,
    user_email character varying
);


ALTER TABLE public.trans_user_info OWNER TO transuser;

--
-- TOC entry 208 (class 1259 OID 41614)
-- Name: trans_user_info_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_user_info_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_user_info_index_seq OWNER TO transuser;

--
-- TOC entry 2223 (class 0 OID 0)
-- Dependencies: 208
-- Name: trans_user_info_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_user_info_index_seq OWNED BY trans_user_info.index;


--
-- TOC entry 2224 (class 0 OID 0)
-- Dependencies: 208
-- Name: trans_user_info_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_user_info_index_seq', 49, true);


--
-- TOC entry 209 (class 1259 OID 41616)
-- Name: user_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE user_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_seq OWNER TO transuser;

--
-- TOC entry 2225 (class 0 OID 0)
-- Dependencies: 209
-- Name: user_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('user_seq', 1, false);


--
-- TOC entry 2034 (class 2604 OID 41618)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY cinder_default ALTER COLUMN index SET DEFAULT nextval('cinder_default_index_seq'::regclass);


--
-- TOC entry 2035 (class 2604 OID 41619)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY cinder_node ALTER COLUMN index SET DEFAULT nextval('cinder_node_index_seq'::regclass);


--
-- TOC entry 2036 (class 2604 OID 41620)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY factory_defaults ALTER COLUMN index SET DEFAULT nextval('factory_defaults_index_seq'::regclass);


--
-- TOC entry 2037 (class 2604 OID 49925)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY glance_defaults ALTER COLUMN index SET DEFAULT nextval('glance_defaults_index_seq'::regclass);


--
-- TOC entry 2039 (class 2604 OID 41621)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY net_adapter_settings ALTER COLUMN index SET DEFAULT nextval('network_settings_index_seq'::regclass);


--
-- TOC entry 2040 (class 2604 OID 41622)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY neutron_default ALTER COLUMN index SET DEFAULT nextval('neutron_default_index_seq'::regclass);


--
-- TOC entry 2041 (class 2604 OID 41623)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY neutron_node ALTER COLUMN index SET DEFAULT nextval('neutron_node_index_seq'::regclass);


--
-- TOC entry 2042 (class 2604 OID 41624)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY nova_default ALTER COLUMN index SET DEFAULT nextval('nova_default_index_seq'::regclass);


--
-- TOC entry 2043 (class 2604 OID 41625)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY nova_node ALTER COLUMN index SET DEFAULT nextval('nova_node_index_seq'::regclass);


--
-- TOC entry 2045 (class 2604 OID 41626)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY swift_default ALTER COLUMN index SET DEFAULT nextval('swift_default_index_seq'::regclass);


--
-- TOC entry 2046 (class 2604 OID 41627)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY swift_node ALTER COLUMN index SET DEFAULT nextval('swift_node_index_seq'::regclass);


--
-- TOC entry 2061 (class 2604 OID 49907)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY system_default_settings ALTER COLUMN index SET DEFAULT nextval('system_default_settings_index_seq'::regclass);


--
-- TOC entry 2047 (class 2604 OID 41628)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_floating_ip ALTER COLUMN index SET DEFAULT nextval('trans_floating_ip_index_seq'::regclass);


--
-- TOC entry 2048 (class 2604 OID 41629)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_network_settings ALTER COLUMN index SET DEFAULT nextval('trans_network_settings_index_seq'::regclass);


--
-- TOC entry 2051 (class 2604 OID 41630)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_routers ALTER COLUMN index SET DEFAULT nextval('trans_routers_index_seq'::regclass);


--
-- TOC entry 2052 (class 2604 OID 41631)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_security_group ALTER COLUMN index SET DEFAULT nextval('trans_security_group_index_seq1'::regclass);


--
-- TOC entry 2053 (class 2604 OID 41632)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_security_keys ALTER COLUMN index SET DEFAULT nextval('trans_security_keys_index_seq1'::regclass);


--
-- TOC entry 2055 (class 2604 OID 41633)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_subnets ALTER COLUMN index SET DEFAULT nextval('trans_subnets_index_seq'::regclass);


--
-- TOC entry 2056 (class 2604 OID 41634)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_system_settings ALTER COLUMN index SET DEFAULT nextval('trans_system_settings_index_seq'::regclass);


--
-- TOC entry 2060 (class 2604 OID 41635)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_user_info ALTER COLUMN index SET DEFAULT nextval('trans_user_info_index_seq'::regclass);


--
-- TOC entry 2132 (class 0 OID 41404)
-- Dependencies: 161
-- Data for Name: cinder_default; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO cinder_default VALUES ('paste.filter_factory', 'keystoneclient.middleware.auth_token:filter_factory', 'api-paste.ini', 1);
INSERT INTO cinder_default VALUES ('auth_host', '172.38.24.10', 'api-paste.ini', 2);
INSERT INTO cinder_default VALUES ('auth_port', '35357', 'api-paste.ini', 3);
INSERT INTO cinder_default VALUES ('auth_protocol', 'http', 'api-paste.ini', 4);
INSERT INTO cinder_default VALUES ('service_host', '172.38.24.10', 'api-paste.ini', 5);
INSERT INTO cinder_default VALUES ('service_port', '5000', 'api-paste.ini', 6);
INSERT INTO cinder_default VALUES ('service_protocol', 'http', 'api-paste.ini', 7);
INSERT INTO cinder_default VALUES ('admin_tenant_name', 'service', 'api-paste.ini', 8);
INSERT INTO cinder_default VALUES ('admin_user', 'transuser', 'api-paste.ini', 9);
INSERT INTO cinder_default VALUES ('admin_passowrd', 'transcirrus1', 'api-paste.ini', 10);
INSERT INTO cinder_default VALUES ('signing_dir', '/var/lib/cinder', 'api-paste.ini', 11);
INSERT INTO cinder_default VALUES ('rootwrap_config', '/etc/cinder/rootwrap.conf', 'cinder.conf', 12);
INSERT INTO cinder_default VALUES ('api_paste_config', '/etc/cinder/api-paste.ini', 'cinder.conf', 13);
INSERT INTO cinder_default VALUES ('iscsi_helper', 'tgtadm', 'cinder.conf', 14);
INSERT INTO cinder_default VALUES ('volume_name_template', 'volume-%s', 'cinder.conf', 15);
INSERT INTO cinder_default VALUES ('volume_group', 'cinder-volumes', 'cinder.conf', 16);
INSERT INTO cinder_default VALUES ('verbose', 'True', 'cinder.conf', 17);
INSERT INTO cinder_default VALUES ('auth_stratagy', 'keystone', 'cinder.conf', 18);
INSERT INTO cinder_default VALUES ('state_path', '/var/lib/cinder', 'cinder.conf', 19);
INSERT INTO cinder_default VALUES ('lock_path', '/var/lib/cinder', 'cinder.conf', 20);
INSERT INTO cinder_default VALUES ('rabbit_username', 'transuser', 'cinder.conf', 21);
INSERT INTO cinder_default VALUES ('rabbit_password', 'transcirrus1', 'cinder.conf', 22);
INSERT INTO cinder_default VALUES ('rabbit_host', '172.38.24.10', 'cinder.conf', 23);


--
-- TOC entry 2133 (class 0 OID 41412)
-- Dependencies: 163
-- Data for Name: cinder_node; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2134 (class 0 OID 41420)
-- Dependencies: 165
-- Data for Name: factory_defaults; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2135 (class 0 OID 41428)
-- Dependencies: 167
-- Data for Name: glance_defaults; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO glance_defaults VALUES ('sql_connection', 'postgresql://transuser:transcirrus1@localhost/glance', 'NULL', 'glance-api.conf', 1);
INSERT INTO glance_defaults VALUES ('admin_tenant_name', 'service', 'NULL', 'glance-api.conf', 2);
INSERT INTO glance_defaults VALUES ('admin_user', 'transuser', 'NULL', 'glance-api.conf', 3);
INSERT INTO glance_defaults VALUES ('admin_password', 'transcirrus1', 'NULL', 'glance-api.conf', 4);
INSERT INTO glance_defaults VALUES ('flavor', 'keystone', 'NULL', 'glance-api.conf', 5);
INSERT INTO glance_defaults VALUES ('sql_connection', 'postgresql://transuser:transcirrus1@localhost/glance', 'NULL', 'glance-registry.conf', 6);
INSERT INTO glance_defaults VALUES ('admin_tenant_name', 'service', 'NULL', 'glance-registry.conf', 7);
INSERT INTO glance_defaults VALUES ('admin_user', 'transuser', 'NULL', 'glance-registry.conf', 8);
INSERT INTO glance_defaults VALUES ('admin_password', 'transcirrus1', 'NULL', 'glance-registry.conf', 9);
INSERT INTO glance_defaults VALUES ('flavor', 'keystone', 'NULL', 'glance-registry.conf', 10);


--
-- TOC entry 2136 (class 0 OID 41434)
-- Dependencies: 168
-- Data for Name: keystone; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2137 (class 0 OID 41440)
-- Dependencies: 169
-- Data for Name: net_adapter_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2138 (class 0 OID 41449)
-- Dependencies: 171
-- Data for Name: neutron_default; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO neutron_default VALUES ('enable_isolated_metadata', 'True', 'dhcp_agent.ini', 1);
INSERT INTO neutron_default VALUES ('enable_metadata_network', 'True', 'dhcp_agent.ini', 2);
INSERT INTO neutron_default VALUES ('admin_tenant_name', 'service', 'metadata_agent.ini', 4);
INSERT INTO neutron_default VALUES ('admin_user', 'transuser', 'metadata_agent.ini', 5);
INSERT INTO neutron_default VALUES ('verbose', 'True', 'quantum.conf', 7);
INSERT INTO neutron_default VALUES ('admin_tenant_name', 'service', 'quantum.conf', 12);
INSERT INTO neutron_default VALUES ('admin_user', 'transuser', 'quantum.conf', 13);
INSERT INTO neutron_default VALUES ('tenant_network_type', 'gre', 'ovs_qauntum_plugin.ini', 15);
INSERT INTO neutron_default VALUES ('tunnel_id_ranges', '1:1000', 'ovs_qauntum_plugin.ini', 16);
INSERT INTO neutron_default VALUES ('enable_tunneling', 'True', 'ovs_qauntum_plugin.ini', 17);
INSERT INTO neutron_default VALUES ('firewall_driver', 'quantum.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver', 'ovs_qauntum_plugin.ini', 18);
INSERT INTO neutron_default VALUES ('interface_driver', 'quantum.agent.linux.interface.OVSInterfaceDriver', 'dhcp_agent.ini', 19);
INSERT INTO neutron_default VALUES ('dhcp_driver', 'quantum.agent.linux.dhcp.Dnsmasq', 'dhcp_agent.ini', 20);
INSERT INTO neutron_default VALUES ('debug', 'False', 'metadata_agent.ini', 21);
INSERT INTO neutron_default VALUES ('nova_metadata_port', '8775', 'metadata_agent.ini', 22);
INSERT INTO neutron_default VALUES ('interface_driver', 'quantum.agent.linux.interface.OVSInterfaceDriver', 'l3_agent.ini', 23);
INSERT INTO neutron_default VALUES ('debug', 'False', 'l3_agent.ini', 24);
INSERT INTO neutron_default VALUES ('external_network_bridge', 'br-ex', 'l3_agent.ini', 25);
INSERT INTO neutron_default VALUES ('paste.filter_factory', 'keystoneclient.middleware.auth_token:filter_factory', 'api-paste.ini', 27);
INSERT INTO neutron_default VALUES ('auth_port', '35357', 'api-paste.ini', 29);
INSERT INTO neutron_default VALUES ('auth_protocol', 'http', 'api-paste.ini', 30);
INSERT INTO neutron_default VALUES ('admin_tenant_name', 'service', 'api-paste.ini', 31);
INSERT INTO neutron_default VALUES ('admin_user', 'tranuser', 'api-paste.ini', 32);
INSERT INTO neutron_default VALUES ('rabbit_userid', 'transuser', 'quantum.conf', 9);
INSERT INTO neutron_default VALUES ('rabbit_port', '5672', 'quantum.conf', 33);
INSERT INTO neutron_default VALUES ('lock_path', '$state_path/lock', 'quantum.conf', 34);
INSERT INTO neutron_default VALUES ('bind_host', '0.0.0.0', 'quantum.conf', 35);
INSERT INTO neutron_default VALUES ('core_plugin', 'quantum.plugins.openvswitch.ovs_quantum_plugin.OVSQuantumPluginV2', 'quantum.conf', 36);
INSERT INTO neutron_default VALUES ('api_paste_config', '/etc/quantum/api-paste.ini', 'quantum.conf', 37);
INSERT INTO neutron_default VALUES ('control_exchange', 'quantum', 'quantum.conf', 38);
INSERT INTO neutron_default VALUES ('notification_driver', 'quantum.openstack.common.notifier.rpc_notifier', 'quantum.conf', 39);
INSERT INTO neutron_default VALUES ('default_notification_level', 'INFO', 'quantum.conf', 40);
INSERT INTO neutron_default VALUES ('notification_topics', 'notifications', 'quantum.conf', 41);
INSERT INTO neutron_default VALUES ('root_helper', 'sudo quantum-rootwrap /etc/quantum/rootwrap.conf', 'quantum.conf', 42);
INSERT INTO neutron_default VALUES ('signing_dir', '/var/lib/quantum/keystone-signing', 'quantum.conf', 43);
INSERT INTO neutron_default VALUES ('integration_bridge', 'br-int', 'ovs_quantum_plugin.ini', 44);
INSERT INTO neutron_default VALUES ('tunnel_bridge', 'br-tun', 'ovs_quantum_plugin.ini', 45);
INSERT INTO neutron_default VALUES ('polling_interval', '2', 'ovs_quantum_plugin.ini', 46);
INSERT INTO neutron_default VALUES ('auth_url', 'http://172.38.24.10:35357/v2.0', 'metadata_agent.ini', 3);
INSERT INTO neutron_default VALUES ('metadata_proxy_shared_secret', 'transcirrus1', 'metadata_agent.ini', 6);
INSERT INTO neutron_default VALUES ('rabbit_password', 'transcirrus1', 'quantum.conf', 8);
INSERT INTO neutron_default VALUES ('rabbit_host', '172.38.24.10', 'quantum.conf', 10);
INSERT INTO neutron_default VALUES ('auth_host', '172.38.24.10', 'quantum.conf', 11);
INSERT INTO neutron_default VALUES ('sql_connection', 'postgresql://transuser:builder@172.38.24.10/quantum', 'ovs_quantum_plugin.ini', 14);
INSERT INTO neutron_default VALUES ('auth_host', '172.38.24.10', 'api_paste.ini', 28);
INSERT INTO neutron_default VALUES ('auth_url', 'http://172.38.24.10:35357/v2.0', 'metadata_agent.ini', 47);
INSERT INTO neutron_default VALUES ('nova_metadata_ip', '172.38.24.10', 'metadata_agent.ini', 48);
INSERT INTO neutron_default VALUES ('admin_password', 'transcirrus1', 'quantum.conf', 49);
INSERT INTO neutron_default VALUES ('admin_password', 'transcirrus1', 'metadata_agent.ini', 50);
INSERT INTO neutron_default VALUES ('admin_passowrd', 'transcirrus1', 'api_paste.ini', 51);


--
-- TOC entry 2139 (class 0 OID 41457)
-- Dependencies: 173
-- Data for Name: neutron_node; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2140 (class 0 OID 41465)
-- Dependencies: 175
-- Data for Name: nova_default; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO nova_default VALUES ('enabled_apis', 'ec2,osapi_compute,metadata', 'nova.conf', 1);
INSERT INTO nova_default VALUES ('logdir', '/var/log/nova', 'nova.conf', 2);
INSERT INTO nova_default VALUES ('state_path', '/var/lib/nova', 'nova.conf', 3);
INSERT INTO nova_default VALUES ('lock_path', '/run/lock/nova', 'nova.conf', 4);
INSERT INTO nova_default VALUES ('verbose', 'True', 'nova.conf', 5);
INSERT INTO nova_default VALUES ('api_paste_config', '/etc/nova/api-paste.ini', 'nova.conf', 6);
INSERT INTO nova_default VALUES ('compute_scheduler_driver', 'nova.scheduler.simple.SimpleScheduler', 'nova.conf', 7);
INSERT INTO nova_default VALUES ('rabbit_password', 'transcirrus1!', 'nova.conf', 10);
INSERT INTO nova_default VALUES ('rabbit_user', 'transuser', 'nova.conf', 9);
INSERT INTO nova_default VALUES ('novncproxy_base_url', 'http://172.24.38.10:6080/vnc_auto.html', 'nova.conf', 18);
INSERT INTO nova_default VALUES ('root_helper', 'sudo nova-rootwrap /etc/nova/rootwrap.conf', 'nova.conf', 11);
INSERT INTO nova_default VALUES ('multi_host', 'False', 'nova.conf', 12);
INSERT INTO nova_default VALUES ('enable_instance_password', 'true', 'nova.conf', 13);
INSERT INTO nova_default VALUES ('use_deprecated_auth', 'false', 'nova.conf', 14);
INSERT INTO nova_default VALUES ('auth_stratagy', 'keystone', 'nova.conf', 15);
INSERT INTO nova_default VALUES ('vncserver_proxyclient_address', '172.24.38.10', 'nova.conf', 20);
INSERT INTO nova_default VALUES ('rabbit_host', '172.24.38.10', 'nova.conf', 8);
INSERT INTO nova_default VALUES ('image_service', 'nova.image.glance.GlanceImageService', 'nova.conf', 16);
INSERT INTO nova_default VALUES ('novnc_enabled', 'true', 'nova.conf', 17);
INSERT INTO nova_default VALUES ('novncproxy_port', '6080', 'nova.conf', 19);
INSERT INTO nova_default VALUES ('vncserver_listen', '0.0.0.0', 'nova.conf', 21);
INSERT INTO nova_default VALUES ('network_api_class', 'nova.network.quantumv2.api.API', 'nova.conf', 22);
INSERT INTO nova_default VALUES ('quantum_url', 'http://172.24.38.10:9696', 'nova.conf', 23);
INSERT INTO nova_default VALUES ('quantum_auth_strategy', 'keystone', 'nova.conf', 25);
INSERT INTO nova_default VALUES ('quantum_admin_tenant_name', 'service', 'nova.conf', 26);
INSERT INTO nova_default VALUES ('quantum_admin_username', 'transuser', 'nova.conf', 27);
INSERT INTO nova_default VALUES ('quantum_admin_passowrd', 'builder', 'nova.conf', 28);
INSERT INTO nova_default VALUES ('libvirt_vif_driver', 'nova.virt.libvirt.vif.LibvirtHybridOVSBridgeDriver', 'nova.conf', 30);
INSERT INTO nova_default VALUES ('linuxnet_interface_driver', 'nova.network.linux_net.LinuxOVSInterfaceDriver', 'nova.conf', 31);
INSERT INTO nova_default VALUES ('firewall_driver', 'nova.virt.firewall.NoopFirewallDriver', 'nova.conf', 32);
INSERT INTO nova_default VALUES ('security_group_api', 'quantum', 'nova.conf', 33);
INSERT INTO nova_default VALUES ('service_quantum_metadata_proxy', 'True', 'nova.conf', 34);
INSERT INTO nova_default VALUES ('quantum_metadata_proxy_shared_secret', 'builder', 'nova.conf', 35);
INSERT INTO nova_default VALUES ('metadata_listen_port', '8775', 'nova.conf', 38);
INSERT INTO nova_default VALUES ('compute_driver', 'libvirt.LibvirtDriver', 'nova.conf', 39);
INSERT INTO nova_default VALUES ('connection_type', 'libvirt', 'nova.conf', 40);
INSERT INTO nova_default VALUES ('volume_api_class', 'nova.volume.cinder.API', 'nova.conf', 41);
INSERT INTO nova_default VALUES ('osapi_volume_listen_port', '5900', 'nova.conf', 42);
INSERT INTO nova_default VALUES ('glance_api_servers', '172.24.38.10:9292', 'nova.conf', 24);
INSERT INTO nova_default VALUES ('quantum_admin_auth_url', 'http://172.24.38.10:35357/v2.0', 'nova.conf', 29);
INSERT INTO nova_default VALUES ('metadata_host', '172.24.38.10', 'nova.conf', 36);
INSERT INTO nova_default VALUES ('metadata_listen', '172.24.38.10', 'nova.conf', 37);
INSERT INTO nova_default VALUES ('paste.filter_factory', 'keystoneclient.middleware.auth_token:filter_factory', 'api-paste.ini', 43);
INSERT INTO nova_default VALUES ('auth_host', '172.38.24.10', 'api-paste.ini', 44);
INSERT INTO nova_default VALUES ('auth_port', '35357', 'api-paste.ini', 45);
INSERT INTO nova_default VALUES ('auth_protocol', 'http', 'api-paste.ini', 46);
INSERT INTO nova_default VALUES ('admin_tenant_name', 'service', 'api-paste.ini', 47);
INSERT INTO nova_default VALUES ('admin_user', 'transuser', 'api-paste.ini', 48);
INSERT INTO nova_default VALUES ('admin_password', 'transcirrus1', 'api-paste.ini', 49);
INSERT INTO nova_default VALUES ('signing_dir', '/tmp/keystone-signing-nova', 'api-paste.ini', 50);
INSERT INTO nova_default VALUES ('auth_version', 'v2.0', 'api-paste.ini', 51);
INSERT INTO nova_default VALUES ('libvirt_type', 'kvm', 'nova-compute.conf', 52);
INSERT INTO nova_default VALUES ('libvirt_ovs_bridge', 'br-int', 'nova-compute.conf', 53);
INSERT INTO nova_default VALUES ('libvirt_vif_type', 'ethernet', 'nova-compute.conf', 54);
INSERT INTO nova_default VALUES ('libvirt_vif_driver', 'nova.virt.libvirt.vif.LibvirtHybridOVSBridgeDriver', 'nova-compute.conf', 55);
INSERT INTO nova_default VALUES ('libvirt_use_virtio_for_bridges', 'True', 'nova-compute.conf', 56);


--
-- TOC entry 2141 (class 0 OID 41473)
-- Dependencies: 177
-- Data for Name: nova_node; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2142 (class 0 OID 41481)
-- Dependencies: 179
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: transuser
--

--
-- TOC entry 2143 (class 0 OID 41487)
-- Dependencies: 180
-- Data for Name: psql_buildout; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2144 (class 0 OID 41494)
-- Dependencies: 181
-- Data for Name: swift_default; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2145 (class 0 OID 41502)
-- Dependencies: 183
-- Data for Name: swift_node; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2159 (class 0 OID 49899)
-- Dependencies: 210
-- Data for Name: system_default_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--

--
-- TOC entry 2146 (class 0 OID 41510)
-- Dependencies: 185
-- Data for Name: trans_floating_ip; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2147 (class 0 OID 41518)
-- Dependencies: 187
-- Data for Name: trans_instances; Type: TABLE DATA; Schema: public; Owner: transuser
--


--
-- TOC entry 2148 (class 0 OID 41524)
-- Dependencies: 188
-- Data for Name: trans_network_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--


--
-- TOC entry 2149 (class 0 OID 41532)
-- Dependencies: 190
-- Data for Name: trans_nodes; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2150 (class 0 OID 41538)
-- Dependencies: 191
-- Data for Name: trans_routers; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2151 (class 0 OID 41548)
-- Dependencies: 193
-- Data for Name: trans_security_group; Type: TABLE DATA; Schema: public; Owner: transuser
--


--
-- TOC entry 2152 (class 0 OID 41560)
-- Dependencies: 197
-- Data for Name: trans_security_keys; Type: TABLE DATA; Schema: public; Owner: transuser
--


--
-- TOC entry 2153 (class 0 OID 41570)
-- Dependencies: 200
-- Data for Name: trans_service_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_service_settings VALUES ('ec2_admin', 8773, NULL, 'ec2', '/services/Admin', 'OpenStack EC2 service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('ec2', 8773, NULL, 'ec2', '/services/Cloud', 'OpenStack EC2 service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('s3', 3333, NULL, 's3', 'NULL', 'OpenStack S3 service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('keystone_admin', 35357, NULL, 'identity', '/v2.0', 'OpenStack Identity', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('nova', 8774, NULL, 'compute', '/v2/$(tenant_id)s', 'OpenStack Compute Service', 'NULL', 'NULL', 'NULL','NULL');
INSERT INTO trans_service_settings VALUES ('quantum', 9696, NULL, 'network', 'NULL', 'OpenStack Networking service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('cinder', 8776, NULL, 'volume', '/v1/$(tenant_id)s', 'OpenStack Volume Service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('glance', 9292, NULL, 'image', 'NULL', 'OpenStack Image Service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('swift', 8080, NULL, 'object-store', '/v1/AUTH_$(tenant_id)s', 'OpenStack Object Store', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('keystone', 5000, NULL, 'identity', '/v2.0', 'OpenStack Identity', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('swift_admin', 8080, NULL, 'object-store', '/v1', 'OpenStack Object Store', 'NULL', 'NULL', 'NULL', 'NULL');


--
-- TOC entry 2154 (class 0 OID 41576)
-- Dependencies: 201
-- Data for Name: trans_subnets; Type: TABLE DATA; Schema: public; Owner: transuser
--
-- Need to populate with 1024 subnet prototypes


--
-- TOC entry 2155 (class 0 OID 41585)
-- Dependencies: 203
-- Data for Name: trans_system_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--


--
-- TOC entry 2156 (class 0 OID 41593)
-- Dependencies: 205
-- Data for Name: trans_system_snapshots; Type: TABLE DATA; Schema: public; Owner: transuser
--

--
-- TOC entry 2157 (class 0 OID 41599)
-- Dependencies: 206
-- Data for Name: trans_system_vols; Type: TABLE DATA; Schema: public; Owner: transuser
--

--
-- TOC entry 2158 (class 0 OID 41608)
-- Dependencies: 207
-- Data for Name: trans_user_info; Type: TABLE DATA; Schema: public; Owner: transuser
--

--
-- TOC entry 2063 (class 2606 OID 41639)
-- Name: cinder_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY cinder_default
    ADD CONSTRAINT cinder_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2065 (class 2606 OID 41641)
-- Name: cinder_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY cinder_node
    ADD CONSTRAINT cinder_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2067 (class 2606 OID 49933)
-- Name: glance_defaults_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY glance_defaults
    ADD CONSTRAINT glance_defaults_pkey PRIMARY KEY (index);


--
-- TOC entry 2086 (class 2606 OID 41645)
-- Name: index; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY psql_buildout
    ADD CONSTRAINT index PRIMARY KEY (index);


--
-- TOC entry 2069 (class 2606 OID 41647)
-- Name: keystone_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY keystone
    ADD CONSTRAINT keystone_key PRIMARY KEY (index);


--
-- TOC entry 2071 (class 2606 OID 41649)
-- Name: network_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY net_adapter_settings
    ADD CONSTRAINT network_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2073 (class 2606 OID 41651)
-- Name: neutron_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY neutron_default
    ADD CONSTRAINT neutron_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2075 (class 2606 OID 41653)
-- Name: neutron_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY neutron_node
    ADD CONSTRAINT neutron_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2077 (class 2606 OID 41655)
-- Name: nova_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY nova_default
    ADD CONSTRAINT nova_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2079 (class 2606 OID 41657)
-- Name: nova_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY nova_node
    ADD CONSTRAINT nova_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2081 (class 2606 OID 41659)
-- Name: projects_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (proj_id);


--
-- TOC entry 2084 (class 2606 OID 41661)
-- Name: projects_proj_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_proj_name_key UNIQUE (proj_name);


--
-- TOC entry 2088 (class 2606 OID 41663)
-- Name: swift_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY swift_default
    ADD CONSTRAINT swift_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2090 (class 2606 OID 41665)
-- Name: swift_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY swift_node
    ADD CONSTRAINT swift_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2131 (class 2606 OID 49915)
-- Name: system_default_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY system_default_settings
    ADD CONSTRAINT system_default_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2092 (class 2606 OID 41667)
-- Name: trans_floating_ip_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_floating_ip
    ADD CONSTRAINT trans_floating_ip_pkey PRIMARY KEY (index);


--
-- TOC entry 2095 (class 2606 OID 41669)
-- Name: trans_instances_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_instances
    ADD CONSTRAINT trans_instances_pkey PRIMARY KEY (inst_id);


--
-- TOC entry 2098 (class 2606 OID 41671)
-- Name: trans_network_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_network_settings
    ADD CONSTRAINT trans_network_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2101 (class 2606 OID 41673)
-- Name: trans_nodes_node_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_nodes
    ADD CONSTRAINT trans_nodes_node_name_key UNIQUE (node_name);


--
-- TOC entry 2103 (class 2606 OID 41675)
-- Name: trans_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_nodes
    ADD CONSTRAINT trans_nodes_pkey PRIMARY KEY (node_id);


--
-- TOC entry 2105 (class 2606 OID 41677)
-- Name: trans_routers_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_routers
    ADD CONSTRAINT trans_routers_pkey PRIMARY KEY (index);


--
-- TOC entry 2108 (class 2606 OID 41679)
-- Name: trans_security_group_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_security_group
    ADD CONSTRAINT trans_security_group_pkey PRIMARY KEY (index);


--
-- TOC entry 2110 (class 2606 OID 41681)
-- Name: trans_security_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_security_keys
    ADD CONSTRAINT trans_security_keys_pkey PRIMARY KEY (index);


--
-- TOC entry 2113 (class 2606 OID 41683)
-- Name: trans_service_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_service_settings
    ADD CONSTRAINT trans_service_settings_pkey PRIMARY KEY (service_name);


--
-- TOC entry 2115 (class 2606 OID 41685)
-- Name: trans_subnets_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_subnets
    ADD CONSTRAINT trans_subnets_pkey PRIMARY KEY (index);


--
-- TOC entry 2118 (class 2606 OID 41687)
-- Name: trans_system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_system_settings
    ADD CONSTRAINT trans_system_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2120 (class 2606 OID 41689)
-- Name: trans_system_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_system_snapshots
    ADD CONSTRAINT trans_system_snapshots_pkey PRIMARY KEY (snap_id);


--
-- TOC entry 2122 (class 2606 OID 41691)
-- Name: trans_system_vols_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_system_vols
    ADD CONSTRAINT trans_system_vols_pkey PRIMARY KEY (vol_id);


--
-- TOC entry 2124 (class 2606 OID 41693)
-- Name: trans_user_info_keystone_user_uuid_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_keystone_user_uuid_key UNIQUE (keystone_user_uuid);


--
-- TOC entry 2126 (class 2606 OID 41695)
-- Name: trans_user_info_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_pkey PRIMARY KEY (index);


--
-- TOC entry 2032 (class 2606 OID 150082)
-- Name: factory_defaults_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY factory_defaults
    ADD CONSTRAINT factory_defaults_pkey PRIMARY KEY (index);

--
-- TOC entry 2129 (class 2606 OID 41697)
-- Name: trans_user_info_user_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_user_name_key UNIQUE (user_name);


--
-- TOC entry 2082 (class 1259 OID 41698)
-- Name: projects_proj_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX projects_proj_id_idx ON projects USING btree (proj_id);


--
-- TOC entry 2093 (class 1259 OID 41700)
-- Name: trans_instances_inst_name_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_instances_inst_name_idx ON trans_instances USING btree (inst_name);


--
-- TOC entry 2096 (class 1259 OID 41701)
-- Name: trans_network_settings_net_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_network_settings_net_id_idx ON trans_network_settings USING btree (net_id);


--
-- TOC entry 2099 (class 1259 OID 41702)
-- Name: trans_nodes_node_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_nodes_node_id_idx ON trans_nodes USING btree (node_id);


--
-- TOC entry 2106 (class 1259 OID 41703)
-- Name: trans_routers_router_name_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_routers_router_name_idx ON trans_routers USING btree (router_name);


--
-- TOC entry 2111 (class 1259 OID 41704)
-- Name: trans_security_keys_sec_key_name_sec_key_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_security_keys_sec_key_name_sec_key_id_idx ON trans_security_keys USING btree (sec_key_name, sec_key_id);


--
-- TOC entry 2116 (class 1259 OID 41705)
-- Name: trans_subnets_subnet_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_subnets_subnet_id_idx ON trans_subnets USING btree (subnet_id);


--
-- TOC entry 2127 (class 1259 OID 41706)
-- Name: trans_user_info_user_name_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_user_info_user_name_idx ON trans_user_info USING btree (user_name);


--
-- TOC entry 2166 (class 0 OID 0)
-- Dependencies: 6
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2013-11-04 21:46:46 EST

--
-- PostgreSQL database dump complete
--

