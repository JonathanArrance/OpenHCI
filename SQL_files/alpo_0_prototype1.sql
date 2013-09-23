--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.9
-- Dumped by pg_dump version 9.2.0
-- Started on 2013-09-22 20:52:40 EDT

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 2125 (class 1262 OID 16386)
-- Name: transcirrus; Type: DATABASE; Schema: -; Owner: transuser
--

CREATE DATABASE transcirrus WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';


ALTER DATABASE transcirrus OWNER TO transuser;

\connect transcirrus

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 205 (class 3079 OID 11645)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2128 (class 0 OID 0)
-- Dependencies: 205
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 164 (class 1259 OID 18481)
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
-- TOC entry 198 (class 1259 OID 26804)
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
-- TOC entry 2129 (class 0 OID 0)
-- Dependencies: 198
-- Name: cinder_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE cinder_default_index_seq OWNED BY cinder_default.index;


--
-- TOC entry 2130 (class 0 OID 0)
-- Dependencies: 198
-- Name: cinder_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('cinder_default_index_seq', 1, false);


--
-- TOC entry 195 (class 1259 OID 26781)
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
-- TOC entry 197 (class 1259 OID 26793)
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
-- TOC entry 2131 (class 0 OID 0)
-- Dependencies: 197
-- Name: cinder_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE cinder_node_index_seq OWNED BY cinder_node.index;


--
-- TOC entry 2132 (class 0 OID 0)
-- Dependencies: 197
-- Name: cinder_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('cinder_node_index_seq', 3, true);


--
-- TOC entry 165 (class 1259 OID 18490)
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
-- TOC entry 161 (class 1259 OID 16411)
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
-- TOC entry 163 (class 1259 OID 18473)
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
-- TOC entry 199 (class 1259 OID 26815)
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
-- TOC entry 2133 (class 0 OID 0)
-- Dependencies: 199
-- Name: neutron_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE neutron_default_index_seq OWNED BY neutron_default.index;


--
-- TOC entry 2134 (class 0 OID 0)
-- Dependencies: 199
-- Name: neutron_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('neutron_default_index_seq', 1, false);


--
-- TOC entry 194 (class 1259 OID 26775)
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
-- TOC entry 200 (class 1259 OID 26827)
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
-- TOC entry 2135 (class 0 OID 0)
-- Dependencies: 200
-- Name: neutron_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE neutron_node_index_seq OWNED BY neutron_node.index;


--
-- TOC entry 2136 (class 0 OID 0)
-- Dependencies: 200
-- Name: neutron_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('neutron_node_index_seq', 1, false);


--
-- TOC entry 167 (class 1259 OID 18506)
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
-- TOC entry 2137 (class 0 OID 0)
-- Dependencies: 167
-- Name: TABLE nova_default; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE nova_default IS 'The default values for the nova config files. These are generally the values that are used on the ciac node.';


--
-- TOC entry 201 (class 1259 OID 26838)
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
-- TOC entry 2138 (class 0 OID 0)
-- Dependencies: 201
-- Name: nova_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE nova_default_index_seq OWNED BY nova_default.index;


--
-- TOC entry 2139 (class 0 OID 0)
-- Dependencies: 201
-- Name: nova_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('nova_default_index_seq', 11, true);


--
-- TOC entry 193 (class 1259 OID 26767)
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
-- TOC entry 202 (class 1259 OID 26849)
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
-- TOC entry 2140 (class 0 OID 0)
-- Dependencies: 202
-- Name: nova_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE nova_node_index_seq OWNED BY nova_node.index;


--
-- TOC entry 2141 (class 0 OID 0)
-- Dependencies: 202
-- Name: nova_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('nova_node_index_seq', 20, true);


--
-- TOC entry 170 (class 1259 OID 19798)
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
-- TOC entry 2142 (class 0 OID 0)
-- Dependencies: 170
-- Name: COLUMN projects.def_security_key_name; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.def_security_key_name IS 'Default security key made during project creation';


--
-- TOC entry 2143 (class 0 OID 0)
-- Dependencies: 170
-- Name: COLUMN projects.def_security_key_id; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.def_security_key_id IS 'default security key id made at project creation';


--
-- TOC entry 2144 (class 0 OID 0)
-- Dependencies: 170
-- Name: COLUMN projects.host_system_name; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.host_system_name IS 'Name of the cloud controller';


--
-- TOC entry 2145 (class 0 OID 0)
-- Dependencies: 170
-- Name: COLUMN projects.host_system_ip; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.host_system_ip IS 'API ip associated with the cloud controller';


--
-- TOC entry 162 (class 1259 OID 16430)
-- Name: psql_buildout; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE psql_buildout (
    index bigint DEFAULT 0 NOT NULL,
    component character(1),
    command character varying
);


ALTER TABLE public.psql_buildout OWNER TO transuser;

--
-- TOC entry 166 (class 1259 OID 18498)
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
-- TOC entry 203 (class 1259 OID 26860)
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
-- TOC entry 2146 (class 0 OID 0)
-- Dependencies: 203
-- Name: swift_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE swift_default_index_seq OWNED BY swift_default.index;


--
-- TOC entry 2147 (class 0 OID 0)
-- Dependencies: 203
-- Name: swift_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('swift_default_index_seq', 1, false);


--
-- TOC entry 196 (class 1259 OID 26787)
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
-- TOC entry 204 (class 1259 OID 26871)
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
-- TOC entry 2148 (class 0 OID 0)
-- Dependencies: 204
-- Name: swift_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE swift_node_index_seq OWNED BY swift_node.index;


--
-- TOC entry 2149 (class 0 OID 0)
-- Dependencies: 204
-- Name: swift_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('swift_node_index_seq', 1, false);


--
-- TOC entry 190 (class 1259 OID 20008)
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
-- TOC entry 189 (class 1259 OID 20006)
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
-- TOC entry 2150 (class 0 OID 0)
-- Dependencies: 189
-- Name: trans_floating_ip_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_floating_ip_index_seq OWNED BY trans_floating_ip.index;


--
-- TOC entry 2151 (class 0 OID 0)
-- Dependencies: 189
-- Name: trans_floating_ip_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_floating_ip_index_seq', 1, false);


--
-- TOC entry 169 (class 1259 OID 18543)
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
-- TOC entry 184 (class 1259 OID 19968)
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
-- TOC entry 2152 (class 0 OID 0)
-- Dependencies: 184
-- Name: COLUMN trans_network_settings.net_internal; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_network_settings.net_internal IS '1=true';


--
-- TOC entry 2153 (class 0 OID 0)
-- Dependencies: 184
-- Name: COLUMN trans_network_settings.net_shared; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_network_settings.net_shared IS '1=true';


--
-- TOC entry 183 (class 1259 OID 19966)
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
-- TOC entry 2154 (class 0 OID 0)
-- Dependencies: 183
-- Name: trans_network_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_network_settings_index_seq OWNED BY trans_network_settings.index;


--
-- TOC entry 2155 (class 0 OID 0)
-- Dependencies: 183
-- Name: trans_network_settings_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_network_settings_index_seq', 1, true);


--
-- TOC entry 192 (class 1259 OID 26756)
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
-- TOC entry 2156 (class 0 OID 0)
-- Dependencies: 192
-- Name: COLUMN trans_nodes.node_controller; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_nodes.node_controller IS 'ciac system node is connected to';


--
-- TOC entry 2157 (class 0 OID 0)
-- Dependencies: 192
-- Name: COLUMN trans_nodes.node_cloud_name; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_nodes.node_cloud_name IS 'cloud name the node belongs to. ex RegionOne';


--
-- TOC entry 188 (class 1259 OID 19993)
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
-- TOC entry 2158 (class 0 OID 0)
-- Dependencies: 188
-- Name: COLUMN trans_routers.router_status; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_routers.router_status IS 'Active=1';


--
-- TOC entry 2159 (class 0 OID 0)
-- Dependencies: 188
-- Name: COLUMN trans_routers.router_admin_state; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_routers.router_admin_state IS 'true=1';


--
-- TOC entry 187 (class 1259 OID 19991)
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
-- TOC entry 2160 (class 0 OID 0)
-- Dependencies: 187
-- Name: trans_routers_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_routers_index_seq OWNED BY trans_routers.index;


--
-- TOC entry 2161 (class 0 OID 0)
-- Dependencies: 187
-- Name: trans_routers_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_routers_index_seq', 1, false);


--
-- TOC entry 177 (class 1259 OID 19916)
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
-- TOC entry 179 (class 1259 OID 19934)
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
-- TOC entry 2162 (class 0 OID 0)
-- Dependencies: 179
-- Name: trans_security_group_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_group_index_seq', 1, false);


--
-- TOC entry 182 (class 1259 OID 19949)
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
-- TOC entry 2163 (class 0 OID 0)
-- Dependencies: 182
-- Name: trans_security_group_index_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_security_group_index_seq1 OWNED BY trans_security_group.index;


--
-- TOC entry 2164 (class 0 OID 0)
-- Dependencies: 182
-- Name: trans_security_group_index_seq1; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_group_index_seq1', 31, true);


--
-- TOC entry 180 (class 1259 OID 19937)
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
-- TOC entry 2165 (class 0 OID 0)
-- Dependencies: 180
-- Name: trans_security_key_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_key_index_seq', 1, false);


--
-- TOC entry 176 (class 1259 OID 19908)
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
-- TOC entry 2166 (class 0 OID 0)
-- Dependencies: 176
-- Name: COLUMN trans_security_keys.public_key; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_security_keys.public_key IS 'public key';


--
-- TOC entry 178 (class 1259 OID 19932)
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
-- TOC entry 2167 (class 0 OID 0)
-- Dependencies: 178
-- Name: trans_security_keys_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_keys_index_seq', 1, false);


--
-- TOC entry 181 (class 1259 OID 19939)
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
-- TOC entry 2168 (class 0 OID 0)
-- Dependencies: 181
-- Name: trans_security_keys_index_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_security_keys_index_seq1 OWNED BY trans_security_keys.index;


--
-- TOC entry 2169 (class 0 OID 0)
-- Dependencies: 181
-- Name: trans_security_keys_index_seq1; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_keys_index_seq1', 23, true);


--
-- TOC entry 191 (class 1259 OID 20042)
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
-- TOC entry 2170 (class 0 OID 0)
-- Dependencies: 191
-- Name: TABLE trans_service_settings; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE trans_service_settings IS 'ensure that when the install is done all values except service_ip and service_id are filled in';


--
-- TOC entry 186 (class 1259 OID 19980)
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
-- TOC entry 185 (class 1259 OID 19978)
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
-- TOC entry 2171 (class 0 OID 0)
-- Dependencies: 185
-- Name: trans_subnets_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_subnets_index_seq OWNED BY trans_subnets.index;


--
-- TOC entry 2172 (class 0 OID 0)
-- Dependencies: 185
-- Name: trans_subnets_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_subnets_index_seq', 1, false);


--
-- TOC entry 168 (class 1259 OID 18521)
-- Name: trans_system_settings; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_system_settings (
    index integer NOT NULL,
    parameter character varying,
    param_value character varying,
    host_system character varying
);


ALTER TABLE public.trans_system_settings OWNER TO transuser;

--
-- TOC entry 175 (class 1259 OID 19875)
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
-- TOC entry 174 (class 1259 OID 19852)
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
-- TOC entry 172 (class 1259 OID 19838)
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
-- TOC entry 173 (class 1259 OID 19844)
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
-- TOC entry 2173 (class 0 OID 0)
-- Dependencies: 173
-- Name: trans_user_info_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_user_info_index_seq OWNED BY trans_user_info.index;


--
-- TOC entry 2174 (class 0 OID 0)
-- Dependencies: 173
-- Name: trans_user_info_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_user_info_index_seq', 48, true);


--
-- TOC entry 171 (class 1259 OID 19812)
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
-- TOC entry 2175 (class 0 OID 0)
-- Dependencies: 171
-- Name: user_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('user_seq', 1, false);


--
-- TOC entry 2011 (class 2604 OID 26806)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY cinder_default ALTER COLUMN index SET DEFAULT nextval('cinder_default_index_seq'::regclass);


--
-- TOC entry 2029 (class 2604 OID 26795)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY cinder_node ALTER COLUMN index SET DEFAULT nextval('cinder_node_index_seq'::regclass);


--
-- TOC entry 2010 (class 2604 OID 26817)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY neutron_default ALTER COLUMN index SET DEFAULT nextval('neutron_default_index_seq'::regclass);


--
-- TOC entry 2028 (class 2604 OID 26829)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY neutron_node ALTER COLUMN index SET DEFAULT nextval('neutron_node_index_seq'::regclass);


--
-- TOC entry 2013 (class 2604 OID 26840)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY nova_default ALTER COLUMN index SET DEFAULT nextval('nova_default_index_seq'::regclass);


--
-- TOC entry 2027 (class 2604 OID 26851)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY nova_node ALTER COLUMN index SET DEFAULT nextval('nova_node_index_seq'::regclass);


--
-- TOC entry 2012 (class 2604 OID 26862)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY swift_default ALTER COLUMN index SET DEFAULT nextval('swift_default_index_seq'::regclass);


--
-- TOC entry 2030 (class 2604 OID 26873)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY swift_node ALTER COLUMN index SET DEFAULT nextval('swift_node_index_seq'::regclass);


--
-- TOC entry 2026 (class 2604 OID 20011)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_floating_ip ALTER COLUMN index SET DEFAULT nextval('trans_floating_ip_index_seq'::regclass);


--
-- TOC entry 2020 (class 2604 OID 19971)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_network_settings ALTER COLUMN index SET DEFAULT nextval('trans_network_settings_index_seq'::regclass);


--
-- TOC entry 2023 (class 2604 OID 19996)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_routers ALTER COLUMN index SET DEFAULT nextval('trans_routers_index_seq'::regclass);


--
-- TOC entry 2019 (class 2604 OID 19951)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_security_group ALTER COLUMN index SET DEFAULT nextval('trans_security_group_index_seq1'::regclass);


--
-- TOC entry 2018 (class 2604 OID 19941)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_security_keys ALTER COLUMN index SET DEFAULT nextval('trans_security_keys_index_seq1'::regclass);


--
-- TOC entry 2021 (class 2604 OID 19983)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_subnets ALTER COLUMN index SET DEFAULT nextval('trans_subnets_index_seq'::regclass);


--
-- TOC entry 2014 (class 2604 OID 19846)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_user_info ALTER COLUMN index SET DEFAULT nextval('trans_user_info_index_seq'::regclass);


--
-- TOC entry 2099 (class 0 OID 18481)
-- Dependencies: 164
-- Data for Name: cinder_default; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY cinder_default (parameter, param_value, file_name, index) FROM stdin;
\.


--
-- TOC entry 2119 (class 0 OID 26781)
-- Dependencies: 195
-- Data for Name: cinder_node; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY cinder_node (parameter, param_value, file_name, node, index) FROM stdin;
sql_connection	postgresql://transuser:builder@172.64.28.10/cinder	\N	\N	3
\.


--
-- TOC entry 2100 (class 0 OID 18490)
-- Dependencies: 165
-- Data for Name: glance; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY glance (parameter, param_value, host_name, file_path, index) FROM stdin;
\.


--
-- TOC entry 2096 (class 0 OID 16411)
-- Dependencies: 161
-- Data for Name: keystone; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY keystone (index, paramter, param_value, host_system, file_path) FROM stdin;
\.


--
-- TOC entry 2098 (class 0 OID 18473)
-- Dependencies: 163
-- Data for Name: neutron_default; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY neutron_default (parameter, param_value, file_name, index) FROM stdin;
\.


--
-- TOC entry 2118 (class 0 OID 26775)
-- Dependencies: 194
-- Data for Name: neutron_node; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY neutron_node (parameter, param_value, file_name, node, index) FROM stdin;
\.


--
-- TOC entry 2102 (class 0 OID 18506)
-- Dependencies: 167
-- Data for Name: nova_default; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY nova_default (parameter, param_value, file_name, index) FROM stdin;
jontest	shit.blah	api-paste.ini	1
jontest2	yo://home	nova.conf	2
jontest3	192.168.19.1	nova.compute	3
test5	yo	api-paste.ini	4
test1	virt	nova-compute.conf	5
test3	test.yo.yo2	nova.conf	6
yotest	88888	nova.conf	7
test30	host:192.168.10.1	api-paste.ini	8
test2	http://192.168.10.1	nova.conf	9
test2	host	nova-compute.conf	10
test1	10	nova.conf	11
\.


--
-- TOC entry 2117 (class 0 OID 26767)
-- Dependencies: 193
-- Data for Name: nova_node; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY nova_node (parameter, param_value, file_name, node, index) FROM stdin;
node222	yo.yo2	nova.conf	222	1
node222	yo.yo.yo.yo	nova.conf	222	2
node333	shit	nova.conf	333	3
node333	shit2	nova.conf	333	4
\.


--
-- TOC entry 2105 (class 0 OID 19798)
-- Dependencies: 170
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY projects (proj_id, proj_name, def_security_key_name, def_security_key_id, def_security_group_id, def_security_group_name, host_system_name, host_system_ip, def_network_name, def_network_id) FROM stdin;
a2ef53c14635446e9903585737b494bc	demo	keys_new	01:05:d5:37:ac:f2:04:4c:76:12:f9:3f:ff:79:51:33	13e863cb-e035-4125-be97-1b6852fc377b	jon	jon-devstack	192.168.10.30	private	b758aed3-52ab-481c-ae65-d0cd6a793602
c373898aecf3489e9fcfaa405c0ea85f	unittest	\N	\N	\N	\N	\N	\N	\N	\N
\.


--
-- TOC entry 2097 (class 0 OID 16430)
-- Dependencies: 162
-- Data for Name: psql_buildout; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY psql_buildout (index, component, command) FROM stdin;
\.


--
-- TOC entry 2101 (class 0 OID 18498)
-- Dependencies: 166
-- Data for Name: swift_default; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY swift_default (paramter, param_value, host_name, file_path, index) FROM stdin;
\.


--
-- TOC entry 2120 (class 0 OID 26787)
-- Dependencies: 196
-- Data for Name: swift_node; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY swift_node (parameter, param_value, file_name, node, index) FROM stdin;
\.


--
-- TOC entry 2114 (class 0 OID 20008)
-- Dependencies: 190
-- Data for Name: trans_floating_ip; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_floating_ip (index, floating_ip, floating_ip_id, proj_id, router_id, fixed_ip) FROM stdin;
\.


--
-- TOC entry 2104 (class 0 OID 18543)
-- Dependencies: 169
-- Data for Name: trans_instances; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_instances (proj_id, in_use, floating_ip_id, inst_id, inst_port_id, inst_key_name, inst_sec_group_name, inst_username, inst_flav_name, inst_floating_ip, inst_ext_net_id, inst_int_ip, inst_int_net_id, inst_int_net_name, inst_image_name, inst_name) FROM stdin;
a2ef53c14635446e9903585737b494bc	1	192.168.10.1	343343333434	21212121212	test	testgroup	jon	flavor1	\N	\N	\N	\N	\N	ubuntu	testtest1
a2ef53c14635446e9903585737b494bc	1	192.168.10.2	56456546546	323232323232	test	testgroup2	shit	flavor02	\N	\N	\N	\N	\N	redhat	testtest2
\.


--
-- TOC entry 2111 (class 0 OID 19968)
-- Dependencies: 184
-- Data for Name: trans_network_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_network_settings (index, net_name, net_id, subnet_name, subnet_id, user_name, proj_id, net_internal, net_shared) FROM stdin;
1	private	b758aed3-52ab-481c-ae65-d0cd6a793602	\N	889786580	jon	1415b96437aa4709b4ea4c28209cf18a	1	0
\.


--
-- TOC entry 2116 (class 0 OID 26756)
-- Dependencies: 192
-- Data for Name: trans_nodes; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_nodes (node_id, node_name, node_type, node_mgmt_ip, node_data_ip, node_controller, node_cloud_name, node_nova_zone, node_iscsi_iqn, node_swift_ring) FROM stdin;
222	tetcomputer	cn	192.168.10.1	192.168.11.1	ciac-01	cloud1	nova	NULL	NULL
3333	test	sn	192.168.10.3	192.168.10.5	ciac-01	cloud1	NULL	ign-99999	tester
1	node1	sn	192.168.11.1	192.168.10.1	ciac-01	test	nova	11111-iqn	NULL
10	node10	sn	192.168.11.1	192.168.10.1	ciac-01	test	nova	11111-iqn	NULL
\.


--
-- TOC entry 2113 (class 0 OID 19993)
-- Dependencies: 188
-- Data for Name: trans_routers; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_routers (index, router_name, router_id, net_id, proj_id, router_status, router_admin_state, router_ext_gateway, router_ext_ip) FROM stdin;
\.


--
-- TOC entry 2110 (class 0 OID 19916)
-- Dependencies: 177
-- Data for Name: trans_security_group; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_security_group (index, proj_id, user_name, sec_group_id, sec_group_name) FROM stdin;
28	1415b96437aa4709b4ea4c28209cf18a	admin	13e863cb-e035-4125-be97-1b6852fc377b	jon
29	1415b96437aa4709b4ea4c28209cf18a	admin	9c250af4-e72a-4ffc-8f4c-287f1161b9e4	test_group2
30	1415b96437aa4709b4ea4c28209cf18a	jon	647f928e-9fbe-4210-9f5f-33fce25edc02	jontest
31	1415b96437aa4709b4ea4c28209cf18a	jon	27975a4c-45cd-4ba3-a284-a677ab2f21af	jontest2
\.


--
-- TOC entry 2109 (class 0 OID 19908)
-- Dependencies: 176
-- Data for Name: trans_security_keys; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_security_keys (proj_id, user_name, sec_key_id, sec_key_name, public_key, private_key, index) FROM stdin;
1415b96437aa4709b4ea4c28209cf18a	admin	dc:89:ce:bd:67:39:39:fd:e9:2e:a8:49:55:90:0f:d4	default_keys	ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDB0GKrY9XFI/M81aMilp23wS8a+FMB3NWnHg/6i4iS2x0aRR6jar/wDXz9p16L1zmMGt3qkpNNahM9IvwleO2SD/VxFSk1lMy3q9TbQj0MCVn0YobnIwLyYCuXxC/w0AlSYaP4XWLYZhIeM48NP8UOngvcc2geiXWw33WfmgGgaqUhmvnzMUmcVifuydDOh07c8k6Andl7aM0+PSHeOe+fX//OIAltRVGf/hpJnmukTLSpT6bhg2MAsyxO4U0eIwk9O4ZMPJjCM4cG7wYryGKLxVGods7j16a0Y22rCvK7U76Pf5JyvyXsxeueirFYhVxcPqZBABGsfeoplWrgGVzx Generated by Nova\n	-----BEGIN RSA PRIVATE KEY-----\nMIIEogIBAAKCAQEAwdBiq2PVxSPzPNWjIpadt8EvGvhTAdzVpx4P+ouIktsdGkUe\no2q/8A18/adei9c5jBrd6pKTTWoTPSL8JXjtkg/1cRUpNZTMt6vU20I9DAlZ9GKG\n5yMC8mArl8Qv8NAJUmGj+F1i2GYSHjOPDT/FDp4L3HNoHol1sN91n5oBoGqlIZr5\n8zFJnFYn7snQzodO3PJOgJ3Ze2jNPj0h3jnvn1//ziAJbUVRn/4aSZ5rpEy0qU+m\n4YNjALMsTuFNHiMJPTuGTDyYwjOHBu8GK8hii8VRqHbO49emtGNtqwryu1O+j3+S\ncr8l7MXrnoqxWIVcXD6mQQARrH3qKZVq4Blc8QIDAQABAoIBAAjALuRMIqe/Asl5\nX98866wTRdwy4BSScvcTrWcDi8wNppe8DTEVrcrZ4Q3W07b+pbOEtwZTTeFN68Zz\n4OyUNC3HGK7dZLntmPyl/ntT10vG1E/rbunas9RbsTwt+Hgn/HPCwtOA6+iXWzQP\n4eKYQX5ydliiwU23qR+uRzJIktA6TEt7Yo3upCbn9g6Ue0BFQ0H5OjZHgFqGS4ib\n/j4Kx36iF55HkzjDR2EkHXNjJJOmq5d7FqsX6sdCvDaCyLM4ZCDVG8q1kcrOPwC1\noKKj94X8mCSd0rNd96T4oXW0lL5/k4OtiVY+Nnqu3muzEhc49Te2tdLbAe9u3Kwi\nJ/m6YZECgYEA6zGG3qTF2jImnIART6tlBZjOIFWqReXeXXPfznQ2oHjSzlbQmK4k\nF9dtM0EOt7CvG2GBhesNzGLvfj6TJDxb94AlICuVnjBhTbXjKx3lRx3Hp96IHUcO\nkFQ2zPG2FAmiz31AXNM/VgoALmDLQSrvAYiqDkAnlxsvISo7WDVtao0CgYEA0vW6\n0b2TT8oJDGFv7rAGCU+E+bIG/N8cCZ+qrwf9HsCr+JfS0H2B8B9MatcF4vKOWdn1\nOJDW19Vvodf73XCbb2pxysLWhOAze/AB9osF9XQJawvyYvQFpbzPESpRSKtC4oEn\n2VRxTStqXqFfE+1NTCWwqjWMXPDs1xmUuJ0k9PUCgYBY0D8J3FcKal3CQ2pGF4by\nch2EgFToSEGMMLGXGLN4LagNWyMyRLBEgIkwDaUtIH8/a7aph3WSdNnTZnXR/SkN\ncUqTt2GsdsCHw+Og6I0oKcq3TYVA6RBK2EJJag1Dy8+7YqTnaK5GI0imOs8GMNxI\nS/9LmlZY7V8Cuxvl12cWEQKBgEcVe/zelzvEhSYB0xingXEztUf53/bnKuhnP7k4\nxObO32OlrOiJ0fXaZgJ+L8KYHrVSBxonW+1gQvxS7dBg+E8jm/JJksU1UsPJTLAJ\nill53w6N+P+04A5Hv7I2AyusYZ43DPljRcZOAcqfL41kYa5t6MiBwKk0mWmlegJ3\nGRPdAoGADxNQYosegAPG7iisqTs57THKuLkdp2iKKpntd/gwzXmB/0SgIx2YITo4\ndt9okPr+uRdnbtZ21XKagzBP9RfbXhQb2nv6ggoetsr2m7bL10vFPwE4I+Q4gPNP\n9sSPip1GFY9mvowDU74WMQdk3v7HF1oNwAorOilrMDiGm5A3rEs=\n-----END RSA PRIVATE KEY-----\n	22
1415b96437aa4709b4ea4c28209cf18a	admin	01:05:d5:37:ac:f2:04:4c:76:12:f9:3f:ff:79:51:33	keys_new	ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCzpAaEq+T9UaTRC/l5CcktPm3ERJUzJ1bNAFKaGgS3RnYSdmOUnTal5Z/nXkHdp5Rqy6sxICQ3n0ZsQE+TMay9sKPHA64ic/cUjp3ejFMRitPN9ZcBTpOhQwniF0ff5ChcuqL1yAGamEFTPDcg+W9kN5EI++Kd0Pg3el4cGPclemjw/4l7xv+yimBF9gWoL0vVV7qDEvrCU+41sx2HcNAkYGwQ5IvxKc8EbWvHZLELD8nS0DLPpM0uwEdh+VsB+WHG1ACLZU1y42m7qDAyvcBCU4SkRqatKinkt6ynIe018bFwCeUAObeE59Yd3+9LM/wAbc8FpXtRFDu3Rm4hUPJF Generated by Nova\n	-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAs6QGhKvk/VGk0Qv5eQnJLT5txESVMydWzQBSmhoEt0Z2EnZj\nlJ02peWf515B3aeUasurMSAkN59GbEBPkzGsvbCjxwOuInP3FI6d3oxTEYrTzfWX\nAU6ToUMJ4hdH3+QoXLqi9cgBmphBUzw3IPlvZDeRCPvindD4N3peHBj3JXpo8P+J\ne8b/sopgRfYFqC9L1Ve6gxL6wlPuNbMdh3DQJGBsEOSL8SnPBG1rx2SxCw/J0tAy\nz6TNLsBHYflbAflhxtQAi2VNcuNpu6gwMr3AQlOEpEamrSop5LespyHtNfGxcAnl\nADm3hOfWHd/vSzP8AG3PBaV7URQ7t0ZuIVDyRQIDAQABAoIBAHo5Sa4O/nhUil0p\nVo3B2L0N0sVNHG53f5lvdMQgm8DPEhqxrkM5TCtHtqpG+W2ETXj0JgAArGOj3Nhe\nUUYG8E8H1gbcPCh42k2EU2lN9F7lJALn69wZyFxaLmlECcUNiWC+I44yjNTQbvHg\n8GlhDScUn3uLVb6mpZupiEp5uf4mzT1uau0qa7/nHOiaieqGJqaLNprEBEuUzDpp\nY9Zgw/yzDFnRoUOjKzovMyc0xVCy/97jI1B68r2vvUBt8XrfLgiGEkQ+XVQnI4tD\nEYYpSTkeL0KMaZdeUxMlQYy9LS93D6lp28IHGcyNSK6lVOOr58fbpMX1JrWlBjM3\nllEoCQECgYEA3IxtHKsRXB3ST+okTov9xlzDTB3L3BM46ZjORWjzxSVdB9ToPONr\neK65u9VXNeOP1WVpI5DkJnrztGjdy1ssB5u7Z1YebCm55AJOSCR93Whctf3xEtb8\nnCynayIS/zdSPt1eANqrYFwu/YSa7+GHECJlh7oDeELpTL5YADIKsuECgYEA0IQ+\nDOTLxZQVH8IYl9ZkPmzqGzSuRYgAb/dgnIy9K4diOud5qtkg8W5i+EhDTrthOYGP\nU8BUchA6ycoAAQBH2kplgMWSkB0f4P7LD5r/AK4sc2gLTv1Mh9HxYyPmz4RD2JRu\nVr3ddIWEPPd7hM87kf73l0i6bmBwyxO4lGV7z+UCgYEAxQaCV1EPwh42CwReCPmQ\n7YtjQPWBcAqQFkdXRrS6yU1Wra9rBTIZiYd2D7JIJbE0hmwBIC/JUgMXAf2I3qmF\nTQq3wVoy9WfVVDcnHdXTx177K+4/VhhPNWnC6rdXBz6xr81stBCldwEDTaIQE+qD\nEUvZLgZkISSNbOzCivIpkqECgYBoISI7niaEzKaf7XYKnW4CHrHqVCyTXI+bWpZM\nl5wAmONdNytzPmtNJisWgj/amYi8Bw9ka6/AJoq1KsNFvLYlNPHrlL7UaTb6TUNq\nz6R42oIoP9Ul5SjKyvUY5VzmVM7s4XMYrkhhYCvhplVwxWyiRAmw6wjvBgpN39NV\niDiEYQKBgQDAry/p66fCr+ATtV0Gbqj84mMK1Nk+gtcOsTtIijtmlUNqwkqTUmpz\nEzEd+tUj7mMVLgmKuyc8RicM8cDig7NPea6Y2EBMrrQAlX20ysO6VNoy+Je+rHwR\nABG36rPonbVz6PIbmyTfMC/zLLUZBnVwXKnfbYIV+L0PAODuR7TXOg==\n-----END RSA PRIVATE KEY-----\n	23
\.


--
-- TOC entry 2115 (class 0 OID 20042)
-- Dependencies: 191
-- Data for Name: trans_service_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_service_settings (service_name, service_port, service_id, service_type, service_api_version, service_desc, service_admin_ip, service_int_ip, service_public_ip, service_endpoint_id) FROM stdin;
glance                                                                                                                                                                                                                                                         	9292	\N	image	NULL	OpenStack Image Service	\N	\N	\N	\N
keystone                                                                                                                                                                                                                                                       	5000	\N	identity	/v2.0	OpenStack Identity	\N	\N	\N	\N
keystone_admin                                                                                                                                                                                                                                                 	35357	\N	identity	/v2.0	OpenStack Identity	\N	\N	\N	\N
ec2                                                                                                                                                                                                                                                            	8773	\N	ec2	/services/Cloud	OpenStack EC2 service	\N	\N	\N	\N
ec2_admin                                                                                                                                                                                                                                                      	8773	\N	ec2	/services/Admin	OpenStack EC2 service	\N	\N	\N	\N
quantum                                                                                                                                                                                                                                                        	9696	\N	network	NULL	OpenStack Networking service	\N	\N	\N	\N
cinder                                                                                                                                                                                                                                                         	8776	NULL	volume	/v1/$(tenant_id)s	OpenStack Volume Service	NULL	NULL	NULL	NULL
s3                                                                                                                                                                                                                                                             	3333	\N	s3	NULL	OpenStack S3 service	\N	\N	\N	\N
swift                                                                                                                                                                                                                                                          	8080	\N	object-store	/v1/AUTH_$(tenant_id)s	OpenStack Object Store	\N	\N	\N	\N
swift_admin                                                                                                                                                                                                                                                    	8080	\N	object-store	NULL	OpenStack Object Store	\N	\N	\N	\N
nova                                                                                                                                                                                                                                                           	8774	7f565f757aac4369aa7477dde94063b5	compute	/v2/$(tenant_id)s	OpenStack Compute Service	192.168.10.30	192.168.10.30	192.168.10.30	\N
\.


--
-- TOC entry 2112 (class 0 OID 19980)
-- Dependencies: 186
-- Data for Name: trans_subnets; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_subnets (index, subnet_id, in_use, subnet_class, subnet_ip_ver, subnet_cidr, subnet_gateway, subnet_allocation_start, subnet_allocation_end, subnet_dhcp_enable) FROM stdin;
\.


--
-- TOC entry 2103 (class 0 OID 18521)
-- Dependencies: 168
-- Data for Name: trans_system_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_system_settings (index, parameter, param_value, host_system) FROM stdin;
6	default_member_role_id	10d138c68dec4a9098ad409931030f25	jon-devstack
5	admin_token	cheapass	jon-devstack
3	mgmt_ip	192.168.10.30	jon-devstack
4	default_hosted_flav	84	jon-devstack
8	api_ip	192.168.10.30	jon-devstack
7	default_admin_role_id	acf7dbc6c28f465588a33afa12f1e2f0	jon-devstack
10	node_type	cc	jon-devstack
11	node_type	cn	jon-compute
12	node_type	sn	jon-store
13	ext_net_id	7dc3e577-9fcf-4671-8682-501e28d06fef	cheapass001
14	default_hosted_os	ebf92ed4-bfb5-4b91-85f9-933870d8c147	cheapass001
15	mgmt_ip	192.168.10.25	cheapass001
16	default_hosted_flav	3	cheapass001
17	admin_token	cacappliance	cheapass001
18	default_member_id	725e0e2894c24667888bcaf2d28afb62	cheapass001
19	default_admin_id	f572fb5120ed4536ab7503097cbc8f53	cheapass001
20	api_ip	192.168.3.7	cheapass001
21	default_region	RegionOne	cheapass001
22	node_type	cc	cheapass001
1	ext_net_id	cdc6ad1d-73a5-4f5d-a48e-7dd1946ee565	jon-devstack
2	default_hosted_os	97267148-3db1-4c4d-8a4f-57260abccf4c	jon-devstack
23	admin_api_ip	192.168.10.30	jon-devstack
24	int_api_ip	192.168.10.30	jon-devstack
25	admin_pass_set	1	jon-devstack
26	first_time_boot	0	jon-devstack
27	admin_api_ip	192.168.10.25	cheapass001
28	int_api_ip	192.168.10.25	cheapass001
29	admin_pass_set	1	cheapass001
30	first_time_boot	0	cheapass001
9	cloud_name	RegionOne	jon-devstack
\.


--
-- TOC entry 2108 (class 0 OID 19875)
-- Dependencies: 175
-- Data for Name: trans_system_snapshots; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_system_snapshots (snap_id, vol_id, proj_id, snap_name, snap_desc) FROM stdin;
ed6239dc-0b7d-4a5d-9710-af0c6c193be1	9754ebe5-f13b-4a09-a57d-20ec3b9e1a41	26c877c1d5f7449c93001cc9187754dd	snaptest1	this is a test
89823c96-4e43-4522-a573-68447a0d8b4c	9754ebe5-f13b-4a09-a57d-20ec3b9e1a41	26c877c1d5f7449c93001cc9187754dd	snaptest3	this is a test
04193061-11a0-4633-a168-fb57aee24876	9754ebe5-f13b-4a09-a57d-20ec3b9e1a41	26c877c1d5f7449c93001cc9187754dd	snaptest3	this is a test
\.


--
-- TOC entry 2107 (class 0 OID 19852)
-- Dependencies: 174
-- Data for Name: trans_system_vols; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_system_vols (vol_id, proj_id, keystone_user_uuid, vol_name, vol_size, vol_from_snapshot, vol_set_bootable, vol_attached, vol_attached_to_inst) FROM stdin;
630a0d7d-e5b0-4366-83b1-92eb70e39fcc	a2ef53c14635446e9903585737b494bc	31a222613b2e4938817063748e996d91	test	1	false	false	false	NONE
\.


--
-- TOC entry 2106 (class 0 OID 19838)
-- Dependencies: 172
-- Data for Name: trans_user_info; Type: TABLE DATA; Schema: public; Owner: transuser
--

COPY trans_user_info (index, user_name, user_group_membership, user_group_id, user_enabled, keystone_user_uuid, user_primary_project, user_project_id, keystone_role, user_email) FROM stdin;
11	jon	user	2	TRUE	e606e83c63f74169b5121c9985009600	demo	1415b96437aa4709b4ea4c28209cf18a	Member	\N
10	admin	admin	0	TRUE	31a222613b2e4938817063748e996d91	demo	a2ef53c14635446e9903585737b494bc	admin	\N
48	testuser	pu	1	TRUE	b441e27e99e041799da6ddc6b9cb6826	unittest	c373898aecf3489e9fcfaa405c0ea85f	Member	test@domain.com
\.


--
-- TOC entry 2038 (class 2606 OID 26814)
-- Name: cinder_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY cinder_default
    ADD CONSTRAINT cinder_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2093 (class 2606 OID 26803)
-- Name: cinder_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY cinder_node
    ADD CONSTRAINT cinder_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2040 (class 2606 OID 18505)
-- Name: glance_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY glance
    ADD CONSTRAINT glance_key PRIMARY KEY (index);


--
-- TOC entry 2034 (class 2606 OID 16438)
-- Name: index; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY psql_buildout
    ADD CONSTRAINT index PRIMARY KEY (index);


--
-- TOC entry 2032 (class 2606 OID 18520)
-- Name: keystone_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY keystone
    ADD CONSTRAINT keystone_key PRIMARY KEY (index);


--
-- TOC entry 2036 (class 2606 OID 26825)
-- Name: neutron_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY neutron_default
    ADD CONSTRAINT neutron_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2091 (class 2606 OID 26837)
-- Name: neutron_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY neutron_node
    ADD CONSTRAINT neutron_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2044 (class 2606 OID 26848)
-- Name: nova_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY nova_default
    ADD CONSTRAINT nova_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2089 (class 2606 OID 26859)
-- Name: nova_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY nova_node
    ADD CONSTRAINT nova_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2052 (class 2606 OID 19805)
-- Name: projects_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (proj_id);


--
-- TOC entry 2055 (class 2606 OID 19807)
-- Name: projects_proj_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_proj_name_key UNIQUE (proj_name);


--
-- TOC entry 2042 (class 2606 OID 26870)
-- Name: swift_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY swift_default
    ADD CONSTRAINT swift_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2095 (class 2606 OID 26881)
-- Name: swift_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY swift_node
    ADD CONSTRAINT swift_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2046 (class 2606 OID 18528)
-- Name: sys_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_system_settings
    ADD CONSTRAINT sys_key PRIMARY KEY (index);


--
-- TOC entry 2050 (class 2606 OID 20038)
-- Name: trans_instances_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_instances
    ADD CONSTRAINT trans_instances_pkey PRIMARY KEY (inst_id);


--
-- TOC entry 2073 (class 2606 OID 19976)
-- Name: trans_network_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_network_settings
    ADD CONSTRAINT trans_network_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2085 (class 2606 OID 26766)
-- Name: trans_nodes_node_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_nodes
    ADD CONSTRAINT trans_nodes_node_name_key UNIQUE (node_name);


--
-- TOC entry 2087 (class 2606 OID 26764)
-- Name: trans_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_nodes
    ADD CONSTRAINT trans_nodes_pkey PRIMARY KEY (node_id);


--
-- TOC entry 2079 (class 2606 OID 20003)
-- Name: trans_routers_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_routers
    ADD CONSTRAINT trans_routers_pkey PRIMARY KEY (index);


--
-- TOC entry 2071 (class 2606 OID 19961)
-- Name: trans_security_group_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_security_group
    ADD CONSTRAINT trans_security_group_pkey PRIMARY KEY (index);


--
-- TOC entry 2068 (class 2606 OID 19959)
-- Name: trans_security_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_security_keys
    ADD CONSTRAINT trans_security_keys_pkey PRIMARY KEY (index);


--
-- TOC entry 2082 (class 2606 OID 20051)
-- Name: trans_service_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_service_settings
    ADD CONSTRAINT trans_service_settings_pkey PRIMARY KEY (service_name);


--
-- TOC entry 2076 (class 2606 OID 19988)
-- Name: trans_subnets_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_subnets
    ADD CONSTRAINT trans_subnets_pkey PRIMARY KEY (index);


--
-- TOC entry 2066 (class 2606 OID 19882)
-- Name: trans_system_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_system_snapshots
    ADD CONSTRAINT trans_system_snapshots_pkey PRIMARY KEY (snap_id);


--
-- TOC entry 2064 (class 2606 OID 19874)
-- Name: trans_system_vols_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_system_vols
    ADD CONSTRAINT trans_system_vols_pkey PRIMARY KEY (vol_id);


--
-- TOC entry 2057 (class 2606 OID 19848)
-- Name: trans_user_info_keystone_user_uuid_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_keystone_user_uuid_key UNIQUE (keystone_user_uuid);


--
-- TOC entry 2059 (class 2606 OID 19850)
-- Name: trans_user_info_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_pkey PRIMARY KEY (index);


--
-- TOC entry 2062 (class 2606 OID 19928)
-- Name: trans_user_info_user_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_user_name_key UNIQUE (user_name);


--
-- TOC entry 2053 (class 1259 OID 19926)
-- Name: projects_proj_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX projects_proj_id_idx ON projects USING btree (proj_id);


--
-- TOC entry 2048 (class 1259 OID 20039)
-- Name: trans_instances_inst_name_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_instances_inst_name_idx ON trans_instances USING btree (inst_name);


--
-- TOC entry 2074 (class 1259 OID 19977)
-- Name: trans_network_settings_proj_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_network_settings_proj_id_idx ON trans_network_settings USING btree (proj_id);


--
-- TOC entry 2083 (class 1259 OID 26762)
-- Name: trans_nodes_node_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_nodes_node_id_idx ON trans_nodes USING btree (node_id);


--
-- TOC entry 2080 (class 1259 OID 20004)
-- Name: trans_routers_router_name_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_routers_router_name_idx ON trans_routers USING btree (router_name);


--
-- TOC entry 2069 (class 1259 OID 19925)
-- Name: trans_security_keys_sec_key_name_sec_key_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_security_keys_sec_key_name_sec_key_id_idx ON trans_security_keys USING btree (sec_key_name, sec_key_id);


--
-- TOC entry 2077 (class 1259 OID 19989)
-- Name: trans_subnets_subnet_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_subnets_subnet_id_idx ON trans_subnets USING btree (subnet_id);


--
-- TOC entry 2047 (class 1259 OID 19814)
-- Name: trans_system_settings_index_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_system_settings_index_idx ON trans_system_settings USING btree (index);


--
-- TOC entry 2060 (class 1259 OID 19929)
-- Name: trans_user_info_user_name_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_user_info_user_name_idx ON trans_user_info USING btree (user_name);


--
-- TOC entry 2127 (class 0 OID 0)
-- Dependencies: 5
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2013-09-22 20:52:48 EDT

--
-- PostgreSQL database dump complete
--

