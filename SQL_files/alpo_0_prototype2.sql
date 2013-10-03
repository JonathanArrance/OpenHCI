--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.9
-- Dumped by pg_dump version 9.2.0
-- Started on 2013-10-02 17:53:37 EDT

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 210 (class 3079 OID 11677)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2184 (class 0 OID 0)
-- Dependencies: 210
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 161 (class 1259 OID 145804)
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
-- TOC entry 162 (class 1259 OID 145810)
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
-- TOC entry 2185 (class 0 OID 0)
-- Dependencies: 162
-- Name: cinder_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE cinder_default_index_seq OWNED BY cinder_default.index;


--
-- TOC entry 2186 (class 0 OID 0)
-- Dependencies: 162
-- Name: cinder_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('cinder_default_index_seq', 1, false);


--
-- TOC entry 163 (class 1259 OID 145812)
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
-- TOC entry 164 (class 1259 OID 145818)
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
-- TOC entry 2187 (class 0 OID 0)
-- Dependencies: 164
-- Name: cinder_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE cinder_node_index_seq OWNED BY cinder_node.index;


--
-- TOC entry 2188 (class 0 OID 0)
-- Dependencies: 164
-- Name: cinder_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('cinder_node_index_seq', 3, true);


--
-- TOC entry 207 (class 1259 OID 146120)
-- Name: factory_defaults; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE factory_defaults (
    index integer NOT NULL,
    parameter character varying,
    param_value character varying
);


ALTER TABLE public.factory_defaults OWNER TO transuser;

--
-- TOC entry 206 (class 1259 OID 146118)
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
-- TOC entry 2189 (class 0 OID 0)
-- Dependencies: 206
-- Name: factory_defaults_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE factory_defaults_index_seq OWNED BY factory_defaults.index;


--
-- TOC entry 2190 (class 0 OID 0)
-- Dependencies: 206
-- Name: factory_defaults_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('factory_defaults_index_seq', 1, false);


--
-- TOC entry 165 (class 1259 OID 145820)
-- Name: glance; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE glance (
    parameter character varying,
    param_value character varying,
    host_name character varying,
    file_path character varying,
    index character varying NOT NULL
);


ALTER TABLE public.glance OWNER TO transuser;

--
-- TOC entry 166 (class 1259 OID 145826)
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
-- TOC entry 209 (class 1259 OID 146131)
-- Name: net_adapter_settings; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE net_adapter_settings (
    index integer NOT NULL,
    net_adapter character varying,
    net_ip character varying,
    net_mask character varying,
    net_dns1 character varying,
    net_dns2 character varying,
    net_dns3 character varying,
    system_id character varying,
    system_name character varying,
    net_slave_one character varying,
    net_slave_two character varying,
    inet_setting character varying,
    net_gateway character varying,
    net_mtu character varying,
    net_bond_master character varying
);


ALTER TABLE public.net_adapter_settings OWNER TO transuser;

--
-- TOC entry 2191 (class 0 OID 0)
-- Dependencies: 209
-- Name: TABLE net_adapter_settings; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE net_adapter_settings IS 'All of the network settings used in the transcirrus system. This does not include the the virtual machine networks. Only for physical system network adapters. ';


--
-- TOC entry 208 (class 1259 OID 146129)
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
-- TOC entry 2192 (class 0 OID 0)
-- Dependencies: 208
-- Name: network_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE network_settings_index_seq OWNED BY net_adapter_settings.index;


--
-- TOC entry 2193 (class 0 OID 0)
-- Dependencies: 208
-- Name: network_settings_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('network_settings_index_seq', 1, true);


--
-- TOC entry 167 (class 1259 OID 145832)
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
-- TOC entry 168 (class 1259 OID 145838)
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
-- TOC entry 2194 (class 0 OID 0)
-- Dependencies: 168
-- Name: neutron_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE neutron_default_index_seq OWNED BY neutron_default.index;


--
-- TOC entry 2195 (class 0 OID 0)
-- Dependencies: 168
-- Name: neutron_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('neutron_default_index_seq', 2, true);


--
-- TOC entry 169 (class 1259 OID 145840)
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
-- TOC entry 170 (class 1259 OID 145846)
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
-- TOC entry 2196 (class 0 OID 0)
-- Dependencies: 170
-- Name: neutron_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE neutron_node_index_seq OWNED BY neutron_node.index;


--
-- TOC entry 2197 (class 0 OID 0)
-- Dependencies: 170
-- Name: neutron_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('neutron_node_index_seq', 1, true);


--
-- TOC entry 171 (class 1259 OID 145848)
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
-- TOC entry 2198 (class 0 OID 0)
-- Dependencies: 171
-- Name: TABLE nova_default; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE nova_default IS 'The default values for the nova config files. These are generally the values that are used on the ciac node.';


--
-- TOC entry 172 (class 1259 OID 145854)
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
-- TOC entry 2199 (class 0 OID 0)
-- Dependencies: 172
-- Name: nova_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE nova_default_index_seq OWNED BY nova_default.index;


--
-- TOC entry 2200 (class 0 OID 0)
-- Dependencies: 172
-- Name: nova_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('nova_default_index_seq', 11, true);


--
-- TOC entry 173 (class 1259 OID 145856)
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
-- TOC entry 174 (class 1259 OID 145862)
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
-- TOC entry 2201 (class 0 OID 0)
-- Dependencies: 174
-- Name: nova_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE nova_node_index_seq OWNED BY nova_node.index;


--
-- TOC entry 2202 (class 0 OID 0)
-- Dependencies: 174
-- Name: nova_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('nova_node_index_seq', 20, true);


--
-- TOC entry 175 (class 1259 OID 145864)
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
-- TOC entry 2203 (class 0 OID 0)
-- Dependencies: 175
-- Name: COLUMN projects.def_security_key_name; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.def_security_key_name IS 'Default security key made during project creation';


--
-- TOC entry 2204 (class 0 OID 0)
-- Dependencies: 175
-- Name: COLUMN projects.def_security_key_id; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.def_security_key_id IS 'default security key id made at project creation';


--
-- TOC entry 2205 (class 0 OID 0)
-- Dependencies: 175
-- Name: COLUMN projects.host_system_name; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.host_system_name IS 'Name of the cloud controller';


--
-- TOC entry 2206 (class 0 OID 0)
-- Dependencies: 175
-- Name: COLUMN projects.host_system_ip; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.host_system_ip IS 'API ip associated with the cloud controller';


--
-- TOC entry 176 (class 1259 OID 145870)
-- Name: psql_buildout; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE psql_buildout (
    index bigint DEFAULT 0 NOT NULL,
    component character(1),
    command character varying
);


ALTER TABLE public.psql_buildout OWNER TO transuser;

--
-- TOC entry 177 (class 1259 OID 145877)
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
-- TOC entry 178 (class 1259 OID 145883)
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
-- TOC entry 2207 (class 0 OID 0)
-- Dependencies: 178
-- Name: swift_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE swift_default_index_seq OWNED BY swift_default.index;


--
-- TOC entry 2208 (class 0 OID 0)
-- Dependencies: 178
-- Name: swift_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('swift_default_index_seq', 1, false);


--
-- TOC entry 179 (class 1259 OID 145885)
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
-- TOC entry 180 (class 1259 OID 145891)
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
-- TOC entry 2209 (class 0 OID 0)
-- Dependencies: 180
-- Name: swift_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE swift_node_index_seq OWNED BY swift_node.index;


--
-- TOC entry 2210 (class 0 OID 0)
-- Dependencies: 180
-- Name: swift_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('swift_node_index_seq', 1, false);


--
-- TOC entry 181 (class 1259 OID 145893)
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
-- TOC entry 182 (class 1259 OID 145899)
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
-- TOC entry 2211 (class 0 OID 0)
-- Dependencies: 182
-- Name: trans_floating_ip_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_floating_ip_index_seq OWNED BY trans_floating_ip.index;


--
-- TOC entry 2212 (class 0 OID 0)
-- Dependencies: 182
-- Name: trans_floating_ip_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_floating_ip_index_seq', 1, false);


--
-- TOC entry 183 (class 1259 OID 145901)
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
-- TOC entry 184 (class 1259 OID 145907)
-- Name: trans_network_settings; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_network_settings (
    index integer NOT NULL,
    net_name character varying,
    net_id character varying,
    subnet_name character varying,
    subnet_id character varying,
    user_name character varying,
    proj_id character varying,
    net_internal integer,
    net_shared integer
);


ALTER TABLE public.trans_network_settings OWNER TO transuser;

--
-- TOC entry 2213 (class 0 OID 0)
-- Dependencies: 184
-- Name: COLUMN trans_network_settings.net_internal; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_network_settings.net_internal IS '1=true';


--
-- TOC entry 2214 (class 0 OID 0)
-- Dependencies: 184
-- Name: COLUMN trans_network_settings.net_shared; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_network_settings.net_shared IS '1=true';


--
-- TOC entry 185 (class 1259 OID 145913)
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
-- TOC entry 2215 (class 0 OID 0)
-- Dependencies: 185
-- Name: trans_network_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_network_settings_index_seq OWNED BY trans_network_settings.index;


--
-- TOC entry 2216 (class 0 OID 0)
-- Dependencies: 185
-- Name: trans_network_settings_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_network_settings_index_seq', 1, true);


--
-- TOC entry 186 (class 1259 OID 145915)
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
    node_swift_ring character varying
);


ALTER TABLE public.trans_nodes OWNER TO transuser;

--
-- TOC entry 2217 (class 0 OID 0)
-- Dependencies: 186
-- Name: COLUMN trans_nodes.node_controller; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_nodes.node_controller IS 'ciac system node is connected to';


--
-- TOC entry 2218 (class 0 OID 0)
-- Dependencies: 186
-- Name: COLUMN trans_nodes.node_cloud_name; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_nodes.node_cloud_name IS 'cloud name the node belongs to. ex RegionOne';


--
-- TOC entry 187 (class 1259 OID 145921)
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
-- TOC entry 2219 (class 0 OID 0)
-- Dependencies: 187
-- Name: COLUMN trans_routers.router_status; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_routers.router_status IS 'Active=1';


--
-- TOC entry 2220 (class 0 OID 0)
-- Dependencies: 187
-- Name: COLUMN trans_routers.router_admin_state; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_routers.router_admin_state IS 'true=1';


--
-- TOC entry 188 (class 1259 OID 145929)
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
-- TOC entry 2221 (class 0 OID 0)
-- Dependencies: 188
-- Name: trans_routers_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_routers_index_seq OWNED BY trans_routers.index;


--
-- TOC entry 2222 (class 0 OID 0)
-- Dependencies: 188
-- Name: trans_routers_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_routers_index_seq', 1, false);


--
-- TOC entry 189 (class 1259 OID 145931)
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
-- TOC entry 190 (class 1259 OID 145937)
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
-- TOC entry 2223 (class 0 OID 0)
-- Dependencies: 190
-- Name: trans_security_group_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_group_index_seq', 1, false);


--
-- TOC entry 191 (class 1259 OID 145939)
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
-- TOC entry 2224 (class 0 OID 0)
-- Dependencies: 191
-- Name: trans_security_group_index_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_security_group_index_seq1 OWNED BY trans_security_group.index;


--
-- TOC entry 2225 (class 0 OID 0)
-- Dependencies: 191
-- Name: trans_security_group_index_seq1; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_group_index_seq1', 31, true);


--
-- TOC entry 192 (class 1259 OID 145941)
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
-- TOC entry 2226 (class 0 OID 0)
-- Dependencies: 192
-- Name: trans_security_key_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_key_index_seq', 1, false);


--
-- TOC entry 193 (class 1259 OID 145943)
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
-- TOC entry 2227 (class 0 OID 0)
-- Dependencies: 193
-- Name: COLUMN trans_security_keys.public_key; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_security_keys.public_key IS 'public key';


--
-- TOC entry 194 (class 1259 OID 145949)
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
-- TOC entry 2228 (class 0 OID 0)
-- Dependencies: 194
-- Name: trans_security_keys_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_keys_index_seq', 1, false);


--
-- TOC entry 195 (class 1259 OID 145951)
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
-- TOC entry 2229 (class 0 OID 0)
-- Dependencies: 195
-- Name: trans_security_keys_index_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_security_keys_index_seq1 OWNED BY trans_security_keys.index;


--
-- TOC entry 2230 (class 0 OID 0)
-- Dependencies: 195
-- Name: trans_security_keys_index_seq1; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_keys_index_seq1', 23, true);


--
-- TOC entry 196 (class 1259 OID 145953)
-- Name: trans_service_settings; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_service_settings (
    service_name character(255) NOT NULL,
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
-- TOC entry 2231 (class 0 OID 0)
-- Dependencies: 196
-- Name: TABLE trans_service_settings; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE trans_service_settings IS 'ensure that when the install is done all values except service_ip and service_id are filled in';


--
-- TOC entry 197 (class 1259 OID 145959)
-- Name: trans_subnets; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_subnets (
    index integer NOT NULL,
    subnet_id character varying,
    in_use integer DEFAULT 1,
    subnet_class character(1),
    subnet_ip_ver character varying,
    subnet_cidr character varying,
    subnet_gateway character varying,
    subnet_allocation_start character(1),
    subnet_allocation_end character varying,
    subnet_dhcp_enable integer
);


ALTER TABLE public.trans_subnets OWNER TO transuser;

--
-- TOC entry 198 (class 1259 OID 145966)
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
-- TOC entry 2232 (class 0 OID 0)
-- Dependencies: 198
-- Name: trans_subnets_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_subnets_index_seq OWNED BY trans_subnets.index;


--
-- TOC entry 2233 (class 0 OID 0)
-- Dependencies: 198
-- Name: trans_subnets_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_subnets_index_seq', 1, false);


--
-- TOC entry 199 (class 1259 OID 145968)
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
-- TOC entry 205 (class 1259 OID 146085)
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
-- TOC entry 2234 (class 0 OID 0)
-- Dependencies: 205
-- Name: trans_system_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_system_settings_index_seq OWNED BY trans_system_settings.index;


--
-- TOC entry 2235 (class 0 OID 0)
-- Dependencies: 205
-- Name: trans_system_settings_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_system_settings_index_seq', 45, true);


--
-- TOC entry 200 (class 1259 OID 145974)
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
-- TOC entry 201 (class 1259 OID 145980)
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
-- TOC entry 202 (class 1259 OID 145989)
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
-- TOC entry 203 (class 1259 OID 145995)
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
-- TOC entry 2236 (class 0 OID 0)
-- Dependencies: 203
-- Name: trans_user_info_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_user_info_index_seq OWNED BY trans_user_info.index;


--
-- TOC entry 2237 (class 0 OID 0)
-- Dependencies: 203
-- Name: trans_user_info_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_user_info_index_seq', 48, true);


--
-- TOC entry 204 (class 1259 OID 145997)
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
-- TOC entry 2238 (class 0 OID 0)
-- Dependencies: 204
-- Name: user_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('user_seq', 1, false);


--
-- TOC entry 2057 (class 2604 OID 145999)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY cinder_default ALTER COLUMN index SET DEFAULT nextval('cinder_default_index_seq'::regclass);


--
-- TOC entry 2058 (class 2604 OID 146000)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY cinder_node ALTER COLUMN index SET DEFAULT nextval('cinder_node_index_seq'::regclass);


--
-- TOC entry 2080 (class 2604 OID 146123)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY factory_defaults ALTER COLUMN index SET DEFAULT nextval('factory_defaults_index_seq'::regclass);


--
-- TOC entry 2081 (class 2604 OID 146134)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY net_adapter_settings ALTER COLUMN index SET DEFAULT nextval('network_settings_index_seq'::regclass);


--
-- TOC entry 2059 (class 2604 OID 146001)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY neutron_default ALTER COLUMN index SET DEFAULT nextval('neutron_default_index_seq'::regclass);


--
-- TOC entry 2060 (class 2604 OID 146002)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY neutron_node ALTER COLUMN index SET DEFAULT nextval('neutron_node_index_seq'::regclass);


--
-- TOC entry 2061 (class 2604 OID 146003)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY nova_default ALTER COLUMN index SET DEFAULT nextval('nova_default_index_seq'::regclass);


--
-- TOC entry 2062 (class 2604 OID 146004)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY nova_node ALTER COLUMN index SET DEFAULT nextval('nova_node_index_seq'::regclass);


--
-- TOC entry 2064 (class 2604 OID 146005)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY swift_default ALTER COLUMN index SET DEFAULT nextval('swift_default_index_seq'::regclass);


--
-- TOC entry 2065 (class 2604 OID 146006)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY swift_node ALTER COLUMN index SET DEFAULT nextval('swift_node_index_seq'::regclass);


--
-- TOC entry 2066 (class 2604 OID 146007)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_floating_ip ALTER COLUMN index SET DEFAULT nextval('trans_floating_ip_index_seq'::regclass);


--
-- TOC entry 2067 (class 2604 OID 146008)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_network_settings ALTER COLUMN index SET DEFAULT nextval('trans_network_settings_index_seq'::regclass);


--
-- TOC entry 2070 (class 2604 OID 146009)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_routers ALTER COLUMN index SET DEFAULT nextval('trans_routers_index_seq'::regclass);


--
-- TOC entry 2071 (class 2604 OID 146010)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_security_group ALTER COLUMN index SET DEFAULT nextval('trans_security_group_index_seq1'::regclass);


--
-- TOC entry 2072 (class 2604 OID 146011)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_security_keys ALTER COLUMN index SET DEFAULT nextval('trans_security_keys_index_seq1'::regclass);


--
-- TOC entry 2074 (class 2604 OID 146012)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_subnets ALTER COLUMN index SET DEFAULT nextval('trans_subnets_index_seq'::regclass);


--
-- TOC entry 2075 (class 2604 OID 146087)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_system_settings ALTER COLUMN index SET DEFAULT nextval('trans_system_settings_index_seq'::regclass);


--
-- TOC entry 2079 (class 2604 OID 146013)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_user_info ALTER COLUMN index SET DEFAULT nextval('trans_user_info_index_seq'::regclass);


--
-- TOC entry 2150 (class 0 OID 145804)
-- Dependencies: 161
-- Data for Name: cinder_default; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2151 (class 0 OID 145812)
-- Dependencies: 163
-- Data for Name: cinder_node; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO cinder_node VALUES ('sql_connection', 'postgresql://transuser:builder@172.64.28.10/cinder', NULL, NULL, 3);


--
-- TOC entry 2175 (class 0 OID 146120)
-- Dependencies: 207
-- Data for Name: factory_defaults; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2152 (class 0 OID 145820)
-- Dependencies: 165
-- Data for Name: glance; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2153 (class 0 OID 145826)
-- Dependencies: 166
-- Data for Name: keystone; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2176 (class 0 OID 146131)
-- Dependencies: 209
-- Data for Name: net_adapter_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO net_adapter_settings VALUES (1, 'eth0', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


--
-- TOC entry 2154 (class 0 OID 145832)
-- Dependencies: 167
-- Data for Name: neutron_default; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO neutron_default VALUES ('enable_isolated_metadata', 'True', 'dhcp_agent.ini', 1);
INSERT INTO neutron_default VALUES ('enable_metadata_network', 'True', 'dhcp_agent.ini', 2);
INSERT INTO neutron_default VALUES ('auth_url', 'http://localhost:35357/v2.0', 'metadata_agent.ini', 3);
INSERT INTO neutron_default VALUES ('admin_tenant_name', 'service', 'metadata_agent.ini', 4);
INSERT INTO neutron_default VALUES ('admin_user', 'transuser', 'metadata_agent.ini', 5);
INSERT INTO neutron_default VALUES ('metadata_proxy_shared_secret', 'builder', 'metadata_agent.ini', 6);
INSERT INTO neutron_default VALUES ('verbose', 'True', 'quantum.conf', 7);
INSERT INTO neutron_default VALUES ('rabbit_password', 'builder', 'quantum.conf', 8);
INSERT INTO neutron_default VALUES ('rabbit_host', '192.168.10.37', 'quantum.conf', 10);
INSERT INTO neutron_default VALUES ('auth_host', '192.168.10.37', 'quantum.conf', 11);
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
INSERT INTO neutron_default VALUES ('gateway_external_network_id', '7dc3e577-9fcf-4671-8682-501e28d06fef', 'l3_agent.ini', 26);
INSERT INTO neutron_default VALUES ('paste.filter_factory', 'keystoneclient.middleware.auth_token:filter_factory', 'api_paste.ini', 27);
INSERT INTO neutron_default VALUES ('auth_host', '192.168.10.37', 'api_paste.ini', 28);
INSERT INTO neutron_default VALUES ('auth_port', '35357', 'api_paste.ini', 29);
INSERT INTO neutron_default VALUES ('auth_protocol', 'http', 'api_paste.ini', 30);
INSERT INTO neutron_default VALUES ('admin_tenant_name', 'service', 'api_paste.ini', 31);
INSERT INTO neutron_default VALUES ('admin_user', 'tranuser', 'api_paste.ini', 32);
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
INSERT INTO neutron_default VALUES ('sql_connection', 'postgresql://transuser:builder@localhost/quantum', 'ovs_quantum_plugin.ini', 14);
INSERT INTO neutron_default VALUES ('signing_dir', '/var/lib/quantum/keystone-signing', 'quantum.conf', 43);
INSERT INTO neutron_default VALUES ('integration_bridge', 'br-int', 'ovs_quantum_plugin.ini', 44);
INSERT INTO neutron_default VALUES ('tunnel_bridge', 'br-tun', 'ovs_quantum_plugin.ini', 45);
INSERT INTO neutron_default VALUES ('polling_interval', '2', 'ovs_quantum_plugin.ini', 46);


--
-- TOC entry 2155 (class 0 OID 145840)
-- Dependencies: 169
-- Data for Name: neutron_node; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO neutron_node VALUES ('auth_url', 'http://localhost:35357/v2.0', 'metadata_agent.ini', 'ciac-01', 1);
INSERT INTO neutron_node VALUES ('auth_region', 'RegionOne', 'metadata_agent.ini', 'ciac-01', 2);
INSERT INTO neutron_node VALUES ('admin_password', 'builder', 'metadata_agent.ini', 'ciac-01', 3);
INSERT INTO neutron_node VALUES ('nova_metadata_ip', '127.0.0.1', 'metadata_agent.ini', 'ciac-01', 4);
INSERT INTO neutron_node VALUES ('admin_password', 'builder', 'quantum.conf', 'ciac-01', 5);
INSERT INTO neutron_node VALUES ('local_ip', '192.168.10.37', 'ovs_quantum_plugin.ini', 'ciac-01', 6);
INSERT INTO neutron_node VALUES ('admin_password', 'builder', 'api_paste.ini', 'ciac-01', 7);


--
-- TOC entry 2156 (class 0 OID 145848)
-- Dependencies: 171
-- Data for Name: nova_default; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO nova_default VALUES ('jontest', 'shit.blah', 'api-paste.ini', 1);
INSERT INTO nova_default VALUES ('jontest2', 'yo://home', 'nova.conf', 2);
INSERT INTO nova_default VALUES ('jontest3', '192.168.19.1', 'nova.compute', 3);
INSERT INTO nova_default VALUES ('test5', 'yo', 'api-paste.ini', 4);
INSERT INTO nova_default VALUES ('test1', 'virt', 'nova-compute.conf', 5);
INSERT INTO nova_default VALUES ('test3', 'test.yo.yo2', 'nova.conf', 6);
INSERT INTO nova_default VALUES ('yotest', '88888', 'nova.conf', 7);
INSERT INTO nova_default VALUES ('test30', 'host:192.168.10.1', 'api-paste.ini', 8);
INSERT INTO nova_default VALUES ('test2', 'http://192.168.10.1', 'nova.conf', 9);
INSERT INTO nova_default VALUES ('test2', 'host', 'nova-compute.conf', 10);
INSERT INTO nova_default VALUES ('test1', '10', 'nova.conf', 11);


--
-- TOC entry 2157 (class 0 OID 145856)
-- Dependencies: 173
-- Data for Name: nova_node; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO nova_node VALUES ('node222', 'yo.yo2', 'nova.conf', '222', 1);
INSERT INTO nova_node VALUES ('node222', 'yo.yo.yo.yo', 'nova.conf', '222', 2);
INSERT INTO nova_node VALUES ('node333', 'shit', 'nova.conf', '333', 3);
INSERT INTO nova_node VALUES ('node333', 'shit2', 'nova.conf', '333', 4);


--
-- TOC entry 2158 (class 0 OID 145864)
-- Dependencies: 175
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO projects VALUES ('a2ef53c14635446e9903585737b494bc', 'demo', 'keys_new', '01:05:d5:37:ac:f2:04:4c:76:12:f9:3f:ff:79:51:33', '13e863cb-e035-4125-be97-1b6852fc377b', 'jon', 'jon-devstack', '192.168.10.30', 'private', 'b758aed3-52ab-481c-ae65-d0cd6a793602');
INSERT INTO projects VALUES ('c373898aecf3489e9fcfaa405c0ea85f', 'unittest', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


--
-- TOC entry 2159 (class 0 OID 145870)
-- Dependencies: 176
-- Data for Name: psql_buildout; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2160 (class 0 OID 145877)
-- Dependencies: 177
-- Data for Name: swift_default; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2161 (class 0 OID 145885)
-- Dependencies: 179
-- Data for Name: swift_node; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2162 (class 0 OID 145893)
-- Dependencies: 181
-- Data for Name: trans_floating_ip; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2163 (class 0 OID 145901)
-- Dependencies: 183
-- Data for Name: trans_instances; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_instances VALUES ('a2ef53c14635446e9903585737b494bc', 1, '192.168.10.1', '343343333434', '21212121212', 'test', 'testgroup', 'jon', 'flavor1', NULL, NULL, NULL, NULL, NULL, 'ubuntu', 'testtest1');
INSERT INTO trans_instances VALUES ('a2ef53c14635446e9903585737b494bc', 1, '192.168.10.2', '56456546546', '323232323232', 'test', 'testgroup2', 'shit', 'flavor02', NULL, NULL, NULL, NULL, NULL, 'redhat', 'testtest2');


--
-- TOC entry 2164 (class 0 OID 145907)
-- Dependencies: 184
-- Data for Name: trans_network_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_network_settings VALUES (1, 'private', 'b758aed3-52ab-481c-ae65-d0cd6a793602', NULL, '889786580', 'jon', '1415b96437aa4709b4ea4c28209cf18a', 1, 0);


--
-- TOC entry 2165 (class 0 OID 145915)
-- Dependencies: 186
-- Data for Name: trans_nodes; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_nodes VALUES ('222', 'tetcomputer', 'cn', '192.168.10.1', '192.168.11.1', 'ciac-01', 'cloud1', 'nova', 'NULL', 'NULL');
INSERT INTO trans_nodes VALUES ('3333', 'test', 'sn', '192.168.10.3', '192.168.10.5', 'ciac-01', 'cloud1', 'NULL', 'ign-99999', 'tester');
INSERT INTO trans_nodes VALUES ('1', 'node1', 'sn', '192.168.11.1', '192.168.10.1', 'ciac-01', 'test', 'nova', '11111-iqn', 'NULL');
INSERT INTO trans_nodes VALUES ('10', 'node10', 'sn', '192.168.11.1', '192.168.10.1', 'ciac-01', 'test', 'nova', '11111-iqn', 'NULL');


--
-- TOC entry 2166 (class 0 OID 145921)
-- Dependencies: 187
-- Data for Name: trans_routers; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2167 (class 0 OID 145931)
-- Dependencies: 189
-- Data for Name: trans_security_group; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_security_group VALUES (28, '1415b96437aa4709b4ea4c28209cf18a', 'admin', '13e863cb-e035-4125-be97-1b6852fc377b', 'jon');
INSERT INTO trans_security_group VALUES (29, '1415b96437aa4709b4ea4c28209cf18a', 'admin', '9c250af4-e72a-4ffc-8f4c-287f1161b9e4', 'test_group2');
INSERT INTO trans_security_group VALUES (30, '1415b96437aa4709b4ea4c28209cf18a', 'jon', '647f928e-9fbe-4210-9f5f-33fce25edc02', 'jontest');
INSERT INTO trans_security_group VALUES (31, '1415b96437aa4709b4ea4c28209cf18a', 'jon', '27975a4c-45cd-4ba3-a284-a677ab2f21af', 'jontest2');


--
-- TOC entry 2168 (class 0 OID 145943)
-- Dependencies: 193
-- Data for Name: trans_security_keys; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_security_keys VALUES ('1415b96437aa4709b4ea4c28209cf18a', 'admin', 'dc:89:ce:bd:67:39:39:fd:e9:2e:a8:49:55:90:0f:d4', 'default_keys', 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDB0GKrY9XFI/M81aMilp23wS8a+FMB3NWnHg/6i4iS2x0aRR6jar/wDXz9p16L1zmMGt3qkpNNahM9IvwleO2SD/VxFSk1lMy3q9TbQj0MCVn0YobnIwLyYCuXxC/w0AlSYaP4XWLYZhIeM48NP8UOngvcc2geiXWw33WfmgGgaqUhmvnzMUmcVifuydDOh07c8k6Andl7aM0+PSHeOe+fX//OIAltRVGf/hpJnmukTLSpT6bhg2MAsyxO4U0eIwk9O4ZMPJjCM4cG7wYryGKLxVGods7j16a0Y22rCvK7U76Pf5JyvyXsxeueirFYhVxcPqZBABGsfeoplWrgGVzx Generated by Nova
', '-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAwdBiq2PVxSPzPNWjIpadt8EvGvhTAdzVpx4P+ouIktsdGkUe
o2q/8A18/adei9c5jBrd6pKTTWoTPSL8JXjtkg/1cRUpNZTMt6vU20I9DAlZ9GKG
5yMC8mArl8Qv8NAJUmGj+F1i2GYSHjOPDT/FDp4L3HNoHol1sN91n5oBoGqlIZr5
8zFJnFYn7snQzodO3PJOgJ3Ze2jNPj0h3jnvn1//ziAJbUVRn/4aSZ5rpEy0qU+m
4YNjALMsTuFNHiMJPTuGTDyYwjOHBu8GK8hii8VRqHbO49emtGNtqwryu1O+j3+S
cr8l7MXrnoqxWIVcXD6mQQARrH3qKZVq4Blc8QIDAQABAoIBAAjALuRMIqe/Asl5
X98866wTRdwy4BSScvcTrWcDi8wNppe8DTEVrcrZ4Q3W07b+pbOEtwZTTeFN68Zz
4OyUNC3HGK7dZLntmPyl/ntT10vG1E/rbunas9RbsTwt+Hgn/HPCwtOA6+iXWzQP
4eKYQX5ydliiwU23qR+uRzJIktA6TEt7Yo3upCbn9g6Ue0BFQ0H5OjZHgFqGS4ib
/j4Kx36iF55HkzjDR2EkHXNjJJOmq5d7FqsX6sdCvDaCyLM4ZCDVG8q1kcrOPwC1
oKKj94X8mCSd0rNd96T4oXW0lL5/k4OtiVY+Nnqu3muzEhc49Te2tdLbAe9u3Kwi
J/m6YZECgYEA6zGG3qTF2jImnIART6tlBZjOIFWqReXeXXPfznQ2oHjSzlbQmK4k
F9dtM0EOt7CvG2GBhesNzGLvfj6TJDxb94AlICuVnjBhTbXjKx3lRx3Hp96IHUcO
kFQ2zPG2FAmiz31AXNM/VgoALmDLQSrvAYiqDkAnlxsvISo7WDVtao0CgYEA0vW6
0b2TT8oJDGFv7rAGCU+E+bIG/N8cCZ+qrwf9HsCr+JfS0H2B8B9MatcF4vKOWdn1
OJDW19Vvodf73XCbb2pxysLWhOAze/AB9osF9XQJawvyYvQFpbzPESpRSKtC4oEn
2VRxTStqXqFfE+1NTCWwqjWMXPDs1xmUuJ0k9PUCgYBY0D8J3FcKal3CQ2pGF4by
ch2EgFToSEGMMLGXGLN4LagNWyMyRLBEgIkwDaUtIH8/a7aph3WSdNnTZnXR/SkN
cUqTt2GsdsCHw+Og6I0oKcq3TYVA6RBK2EJJag1Dy8+7YqTnaK5GI0imOs8GMNxI
S/9LmlZY7V8Cuxvl12cWEQKBgEcVe/zelzvEhSYB0xingXEztUf53/bnKuhnP7k4
xObO32OlrOiJ0fXaZgJ+L8KYHrVSBxonW+1gQvxS7dBg+E8jm/JJksU1UsPJTLAJ
ill53w6N+P+04A5Hv7I2AyusYZ43DPljRcZOAcqfL41kYa5t6MiBwKk0mWmlegJ3
GRPdAoGADxNQYosegAPG7iisqTs57THKuLkdp2iKKpntd/gwzXmB/0SgIx2YITo4
dt9okPr+uRdnbtZ21XKagzBP9RfbXhQb2nv6ggoetsr2m7bL10vFPwE4I+Q4gPNP
9sSPip1GFY9mvowDU74WMQdk3v7HF1oNwAorOilrMDiGm5A3rEs=
-----END RSA PRIVATE KEY-----
', 22);
INSERT INTO trans_security_keys VALUES ('1415b96437aa4709b4ea4c28209cf18a', 'admin', '01:05:d5:37:ac:f2:04:4c:76:12:f9:3f:ff:79:51:33', 'keys_new', 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCzpAaEq+T9UaTRC/l5CcktPm3ERJUzJ1bNAFKaGgS3RnYSdmOUnTal5Z/nXkHdp5Rqy6sxICQ3n0ZsQE+TMay9sKPHA64ic/cUjp3ejFMRitPN9ZcBTpOhQwniF0ff5ChcuqL1yAGamEFTPDcg+W9kN5EI++Kd0Pg3el4cGPclemjw/4l7xv+yimBF9gWoL0vVV7qDEvrCU+41sx2HcNAkYGwQ5IvxKc8EbWvHZLELD8nS0DLPpM0uwEdh+VsB+WHG1ACLZU1y42m7qDAyvcBCU4SkRqatKinkt6ynIe018bFwCeUAObeE59Yd3+9LM/wAbc8FpXtRFDu3Rm4hUPJF Generated by Nova
', '-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAs6QGhKvk/VGk0Qv5eQnJLT5txESVMydWzQBSmhoEt0Z2EnZj
lJ02peWf515B3aeUasurMSAkN59GbEBPkzGsvbCjxwOuInP3FI6d3oxTEYrTzfWX
AU6ToUMJ4hdH3+QoXLqi9cgBmphBUzw3IPlvZDeRCPvindD4N3peHBj3JXpo8P+J
e8b/sopgRfYFqC9L1Ve6gxL6wlPuNbMdh3DQJGBsEOSL8SnPBG1rx2SxCw/J0tAy
z6TNLsBHYflbAflhxtQAi2VNcuNpu6gwMr3AQlOEpEamrSop5LespyHtNfGxcAnl
ADm3hOfWHd/vSzP8AG3PBaV7URQ7t0ZuIVDyRQIDAQABAoIBAHo5Sa4O/nhUil0p
Vo3B2L0N0sVNHG53f5lvdMQgm8DPEhqxrkM5TCtHtqpG+W2ETXj0JgAArGOj3Nhe
UUYG8E8H1gbcPCh42k2EU2lN9F7lJALn69wZyFxaLmlECcUNiWC+I44yjNTQbvHg
8GlhDScUn3uLVb6mpZupiEp5uf4mzT1uau0qa7/nHOiaieqGJqaLNprEBEuUzDpp
Y9Zgw/yzDFnRoUOjKzovMyc0xVCy/97jI1B68r2vvUBt8XrfLgiGEkQ+XVQnI4tD
EYYpSTkeL0KMaZdeUxMlQYy9LS93D6lp28IHGcyNSK6lVOOr58fbpMX1JrWlBjM3
llEoCQECgYEA3IxtHKsRXB3ST+okTov9xlzDTB3L3BM46ZjORWjzxSVdB9ToPONr
eK65u9VXNeOP1WVpI5DkJnrztGjdy1ssB5u7Z1YebCm55AJOSCR93Whctf3xEtb8
nCynayIS/zdSPt1eANqrYFwu/YSa7+GHECJlh7oDeELpTL5YADIKsuECgYEA0IQ+
DOTLxZQVH8IYl9ZkPmzqGzSuRYgAb/dgnIy9K4diOud5qtkg8W5i+EhDTrthOYGP
U8BUchA6ycoAAQBH2kplgMWSkB0f4P7LD5r/AK4sc2gLTv1Mh9HxYyPmz4RD2JRu
Vr3ddIWEPPd7hM87kf73l0i6bmBwyxO4lGV7z+UCgYEAxQaCV1EPwh42CwReCPmQ
7YtjQPWBcAqQFkdXRrS6yU1Wra9rBTIZiYd2D7JIJbE0hmwBIC/JUgMXAf2I3qmF
TQq3wVoy9WfVVDcnHdXTx177K+4/VhhPNWnC6rdXBz6xr81stBCldwEDTaIQE+qD
EUvZLgZkISSNbOzCivIpkqECgYBoISI7niaEzKaf7XYKnW4CHrHqVCyTXI+bWpZM
l5wAmONdNytzPmtNJisWgj/amYi8Bw9ka6/AJoq1KsNFvLYlNPHrlL7UaTb6TUNq
z6R42oIoP9Ul5SjKyvUY5VzmVM7s4XMYrkhhYCvhplVwxWyiRAmw6wjvBgpN39NV
iDiEYQKBgQDAry/p66fCr+ATtV0Gbqj84mMK1Nk+gtcOsTtIijtmlUNqwkqTUmpz
EzEd+tUj7mMVLgmKuyc8RicM8cDig7NPea6Y2EBMrrQAlX20ysO6VNoy+Je+rHwR
ABG36rPonbVz6PIbmyTfMC/zLLUZBnVwXKnfbYIV+L0PAODuR7TXOg==
-----END RSA PRIVATE KEY-----
', 23);


--
-- TOC entry 2169 (class 0 OID 145953)
-- Dependencies: 196
-- Data for Name: trans_service_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_service_settings VALUES ('glance                                                                                                                                                                                                                                                         ', 9292, NULL, 'image', 'NULL', 'OpenStack Image Service', NULL, NULL, NULL, NULL);
INSERT INTO trans_service_settings VALUES ('keystone                                                                                                                                                                                                                                                       ', 5000, NULL, 'identity', '/v2.0', 'OpenStack Identity', NULL, NULL, NULL, NULL);
INSERT INTO trans_service_settings VALUES ('keystone_admin                                                                                                                                                                                                                                                 ', 35357, NULL, 'identity', '/v2.0', 'OpenStack Identity', NULL, NULL, NULL, NULL);
INSERT INTO trans_service_settings VALUES ('ec2                                                                                                                                                                                                                                                            ', 8773, NULL, 'ec2', '/services/Cloud', 'OpenStack EC2 service', NULL, NULL, NULL, NULL);
INSERT INTO trans_service_settings VALUES ('ec2_admin                                                                                                                                                                                                                                                      ', 8773, NULL, 'ec2', '/services/Admin', 'OpenStack EC2 service', NULL, NULL, NULL, NULL);
INSERT INTO trans_service_settings VALUES ('quantum                                                                                                                                                                                                                                                        ', 9696, NULL, 'network', 'NULL', 'OpenStack Networking service', NULL, NULL, NULL, NULL);
INSERT INTO trans_service_settings VALUES ('cinder                                                                                                                                                                                                                                                         ', 8776, 'NULL', 'volume', '/v1/$(tenant_id)s', 'OpenStack Volume Service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('s3                                                                                                                                                                                                                                                             ', 3333, NULL, 's3', 'NULL', 'OpenStack S3 service', NULL, NULL, NULL, NULL);
INSERT INTO trans_service_settings VALUES ('swift                                                                                                                                                                                                                                                          ', 8080, NULL, 'object-store', '/v1/AUTH_$(tenant_id)s', 'OpenStack Object Store', NULL, NULL, NULL, NULL);
INSERT INTO trans_service_settings VALUES ('swift_admin                                                                                                                                                                                                                                                    ', 8080, NULL, 'object-store', 'NULL', 'OpenStack Object Store', NULL, NULL, NULL, NULL);
INSERT INTO trans_service_settings VALUES ('nova                                                                                                                                                                                                                                                           ', 8774, '7f565f757aac4369aa7477dde94063b5', 'compute', '/v2/$(tenant_id)s', 'OpenStack Compute Service', '192.168.10.30', '192.168.10.30', '192.168.10.30', NULL);


--
-- TOC entry 2170 (class 0 OID 145959)
-- Dependencies: 197
-- Data for Name: trans_subnets; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2171 (class 0 OID 145968)
-- Dependencies: 199
-- Data for Name: trans_system_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_system_settings VALUES ('admin_token', 'cheapass', 'jon-devstack', 2);
INSERT INTO trans_system_settings VALUES ('mgmt_ip', '192.168.10.30', 'jon-devstack', 3);
INSERT INTO trans_system_settings VALUES ('api_ip', '192.168.10.30', 'jon-devstack', 5);
INSERT INTO trans_system_settings VALUES ('node_type', 'cc', 'jon-devstack', 7);
INSERT INTO trans_system_settings VALUES ('admin_api_ip', '192.168.10.30', 'jon-devstack', 22);
INSERT INTO trans_system_settings VALUES ('int_api_ip', '192.168.10.30', 'jon-devstack', 23);
INSERT INTO trans_system_settings VALUES ('cloud_name', 'RegionOne', 'jon-devstack', 30);
INSERT INTO trans_system_settings VALUES ('single_node', '1', 'jon-devstack', 31);
INSERT INTO trans_system_settings VALUES ('transcirrus_db', '192.168.10.30', 'jon-devstack', 33);
INSERT INTO trans_system_settings VALUES ('tran_db_user', 'transuser', 'jon-devstack', 34);
INSERT INTO trans_system_settings VALUES ('tran_db_pass', 'builder', 'jon-devstack', 35);
INSERT INTO trans_system_settings VALUES ('tran_db_name', 'transcirrus', 'jon-devstack', 36);
INSERT INTO trans_system_settings VALUES ('tran_db_port', '5432', 'jon-devstack', 37);
INSERT INTO trans_system_settings VALUES ('vm_ip_min', '0.0.0.0', 'jon-devstack', 41);
INSERT INTO trans_system_settings VALUES ('vm_ip_max', '0.0.0.0', 'jon-devstack', 42);
INSERT INTO trans_system_settings VALUES ('os_db', '192.168.10.30', 'jon-devstack', 40);
INSERT INTO trans_system_settings VALUES ('os_db_user', 'transuser', 'jon-devstack', 43);
INSERT INTO trans_system_settings VALUES ('os_db_pass', 'builder', 'jon-devstack', 44);
INSERT INTO trans_system_settings VALUES ('os_db_port', '5432', 'jon-devstack', 45);
INSERT INTO trans_system_settings VALUES ('member_role_id', '10d138c68dec4a9098ad409931030f25', 'jon-devstack', 1);
INSERT INTO trans_system_settings VALUES ('hosted_flav', '84', 'jon-devstack', 4);
INSERT INTO trans_system_settings VALUES ('admin_role_id', 'acf7dbc6c28f465588a33afa12f1e2f0', 'jon-devstack', 6);
INSERT INTO trans_system_settings VALUES ('cloud_controller_id', '000-12345678-12345', 'jon-devstack', 38);
INSERT INTO trans_system_settings VALUES ('admin_pass_set', '0', 'jon-devstack', 24);
INSERT INTO trans_system_settings VALUES ('first_time_boot', '0', 'jon-devstack', 25);


--
-- TOC entry 2172 (class 0 OID 145974)
-- Dependencies: 200
-- Data for Name: trans_system_snapshots; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_system_snapshots VALUES ('ed6239dc-0b7d-4a5d-9710-af0c6c193be1', '9754ebe5-f13b-4a09-a57d-20ec3b9e1a41', '26c877c1d5f7449c93001cc9187754dd', 'snaptest1', 'this is a test');
INSERT INTO trans_system_snapshots VALUES ('89823c96-4e43-4522-a573-68447a0d8b4c', '9754ebe5-f13b-4a09-a57d-20ec3b9e1a41', '26c877c1d5f7449c93001cc9187754dd', 'snaptest3', 'this is a test');
INSERT INTO trans_system_snapshots VALUES ('04193061-11a0-4633-a168-fb57aee24876', '9754ebe5-f13b-4a09-a57d-20ec3b9e1a41', '26c877c1d5f7449c93001cc9187754dd', 'snaptest3', 'this is a test');


--
-- TOC entry 2173 (class 0 OID 145980)
-- Dependencies: 201
-- Data for Name: trans_system_vols; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_system_vols VALUES ('630a0d7d-e5b0-4366-83b1-92eb70e39fcc', 'a2ef53c14635446e9903585737b494bc', '31a222613b2e4938817063748e996d91', 'test', 1, 'false', 'false', 'false', 'NONE');


--
-- TOC entry 2174 (class 0 OID 145989)
-- Dependencies: 202
-- Data for Name: trans_user_info; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_user_info VALUES (11, 'jon', 'user', 2, 'TRUE', 'e606e83c63f74169b5121c9985009600', 'demo', '1415b96437aa4709b4ea4c28209cf18a', 'Member', NULL);
INSERT INTO trans_user_info VALUES (10, 'admin', 'admin', 0, 'TRUE', '31a222613b2e4938817063748e996d91', 'demo', 'a2ef53c14635446e9903585737b494bc', 'admin', NULL);
INSERT INTO trans_user_info VALUES (48, 'testuser', 'pu', 1, 'TRUE', 'b441e27e99e041799da6ddc6b9cb6826', 'unittest', 'c373898aecf3489e9fcfaa405c0ea85f', 'Member', 'test@domain.com');


--
-- TOC entry 2083 (class 2606 OID 146015)
-- Name: cinder_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY cinder_default
    ADD CONSTRAINT cinder_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2085 (class 2606 OID 146017)
-- Name: cinder_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY cinder_node
    ADD CONSTRAINT cinder_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2087 (class 2606 OID 146019)
-- Name: glance_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY glance
    ADD CONSTRAINT glance_key PRIMARY KEY (index);


--
-- TOC entry 2104 (class 2606 OID 146021)
-- Name: index; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY psql_buildout
    ADD CONSTRAINT index PRIMARY KEY (index);


--
-- TOC entry 2089 (class 2606 OID 146023)
-- Name: keystone_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY keystone
    ADD CONSTRAINT keystone_key PRIMARY KEY (index);


--
-- TOC entry 2149 (class 2606 OID 146139)
-- Name: network_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY net_adapter_settings
    ADD CONSTRAINT network_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2091 (class 2606 OID 146025)
-- Name: neutron_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY neutron_default
    ADD CONSTRAINT neutron_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2093 (class 2606 OID 146027)
-- Name: neutron_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY neutron_node
    ADD CONSTRAINT neutron_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2095 (class 2606 OID 146029)
-- Name: nova_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY nova_default
    ADD CONSTRAINT nova_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2097 (class 2606 OID 146031)
-- Name: nova_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY nova_node
    ADD CONSTRAINT nova_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2099 (class 2606 OID 146033)
-- Name: projects_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (proj_id);


--
-- TOC entry 2102 (class 2606 OID 146035)
-- Name: projects_proj_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_proj_name_key UNIQUE (proj_name);


--
-- TOC entry 2106 (class 2606 OID 146037)
-- Name: swift_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY swift_default
    ADD CONSTRAINT swift_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2108 (class 2606 OID 146039)
-- Name: swift_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY swift_node
    ADD CONSTRAINT swift_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2110 (class 2606 OID 146128)
-- Name: trans_floating_ip_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_floating_ip
    ADD CONSTRAINT trans_floating_ip_pkey PRIMARY KEY (index);


--
-- TOC entry 2113 (class 2606 OID 146043)
-- Name: trans_instances_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_instances
    ADD CONSTRAINT trans_instances_pkey PRIMARY KEY (inst_id);


--
-- TOC entry 2115 (class 2606 OID 146045)
-- Name: trans_network_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_network_settings
    ADD CONSTRAINT trans_network_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2119 (class 2606 OID 146047)
-- Name: trans_nodes_node_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_nodes
    ADD CONSTRAINT trans_nodes_node_name_key UNIQUE (node_name);


--
-- TOC entry 2121 (class 2606 OID 146049)
-- Name: trans_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_nodes
    ADD CONSTRAINT trans_nodes_pkey PRIMARY KEY (node_id);


--
-- TOC entry 2123 (class 2606 OID 146051)
-- Name: trans_routers_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_routers
    ADD CONSTRAINT trans_routers_pkey PRIMARY KEY (index);


--
-- TOC entry 2126 (class 2606 OID 146053)
-- Name: trans_security_group_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_security_group
    ADD CONSTRAINT trans_security_group_pkey PRIMARY KEY (index);


--
-- TOC entry 2128 (class 2606 OID 146055)
-- Name: trans_security_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_security_keys
    ADD CONSTRAINT trans_security_keys_pkey PRIMARY KEY (index);


--
-- TOC entry 2131 (class 2606 OID 146057)
-- Name: trans_service_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_service_settings
    ADD CONSTRAINT trans_service_settings_pkey PRIMARY KEY (service_name);


--
-- TOC entry 2133 (class 2606 OID 146059)
-- Name: trans_subnets_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_subnets
    ADD CONSTRAINT trans_subnets_pkey PRIMARY KEY (index);


--
-- TOC entry 2136 (class 2606 OID 146095)
-- Name: trans_system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_system_settings
    ADD CONSTRAINT trans_system_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2138 (class 2606 OID 146061)
-- Name: trans_system_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_system_snapshots
    ADD CONSTRAINT trans_system_snapshots_pkey PRIMARY KEY (snap_id);


--
-- TOC entry 2140 (class 2606 OID 146063)
-- Name: trans_system_vols_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_system_vols
    ADD CONSTRAINT trans_system_vols_pkey PRIMARY KEY (vol_id);


--
-- TOC entry 2142 (class 2606 OID 146065)
-- Name: trans_user_info_keystone_user_uuid_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_keystone_user_uuid_key UNIQUE (keystone_user_uuid);


--
-- TOC entry 2144 (class 2606 OID 146067)
-- Name: trans_user_info_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_pkey PRIMARY KEY (index);


--
-- TOC entry 2147 (class 2606 OID 146069)
-- Name: trans_user_info_user_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_user_name_key UNIQUE (user_name);


--
-- TOC entry 2100 (class 1259 OID 146070)
-- Name: projects_proj_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX projects_proj_id_idx ON projects USING btree (proj_id);


--
-- TOC entry 2111 (class 1259 OID 146071)
-- Name: trans_instances_inst_name_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_instances_inst_name_idx ON trans_instances USING btree (inst_name);


--
-- TOC entry 2116 (class 1259 OID 146072)
-- Name: trans_network_settings_proj_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_network_settings_proj_id_idx ON trans_network_settings USING btree (proj_id);


--
-- TOC entry 2117 (class 1259 OID 146073)
-- Name: trans_nodes_node_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_nodes_node_id_idx ON trans_nodes USING btree (node_id);


--
-- TOC entry 2124 (class 1259 OID 146074)
-- Name: trans_routers_router_name_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_routers_router_name_idx ON trans_routers USING btree (router_name);


--
-- TOC entry 2129 (class 1259 OID 146075)
-- Name: trans_security_keys_sec_key_name_sec_key_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_security_keys_sec_key_name_sec_key_id_idx ON trans_security_keys USING btree (sec_key_name, sec_key_id);


--
-- TOC entry 2134 (class 1259 OID 146076)
-- Name: trans_subnets_subnet_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_subnets_subnet_id_idx ON trans_subnets USING btree (subnet_id);


--
-- TOC entry 2145 (class 1259 OID 146078)
-- Name: trans_user_info_user_name_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_user_info_user_name_idx ON trans_user_info USING btree (user_name);


--
-- TOC entry 2183 (class 0 OID 0)
-- Dependencies: 6
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2013-10-02 17:53:43 EDT

--
-- PostgreSQL database dump complete
--

