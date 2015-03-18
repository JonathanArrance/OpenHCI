--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.10
-- Dumped by pg_dump version 9.2.0
-- Started on 2013-12-04 20:49:37 EST

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 2198 (class 1262 OID 16390)
-- Name: transcirrus; Type: DATABASE; Schema: -; Owner: transuser
--

CREATE DATABASE transcirrus WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';


ALTER DATABASE transcirrus OWNER TO transuser;

\connect transcirrus

--SET statement_timeout = 0;
--SET client_encoding = 'UTF8';
--SET standard_conforming_strings = on;
--SET check_function_bodies = false;
--SET client_min_messages = warning;

--
-- TOC entry 213 (class 3079 OID 11677)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2201 (class 0 OID 0)
-- Dependencies: 213
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 161 (class 1259 OID 16391)
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
-- TOC entry 162 (class 1259 OID 16397)
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
-- TOC entry 2202 (class 0 OID 0)
-- Dependencies: 162
-- Name: cinder_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE cinder_default_index_seq OWNED BY cinder_default.index;


--
-- TOC entry 2203 (class 0 OID 0)
-- Dependencies: 162
-- Name: cinder_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('cinder_default_index_seq', 23, true);


--
-- TOC entry 163 (class 1259 OID 16399)
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
-- TOC entry 164 (class 1259 OID 16405)
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
-- TOC entry 2204 (class 0 OID 0)
-- Dependencies: 164
-- Name: cinder_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE cinder_node_index_seq OWNED BY cinder_node.index;


--
-- TOC entry 2205 (class 0 OID 0)
-- Dependencies: 164
-- Name: cinder_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('cinder_node_index_seq', 23, true);


--
-- TOC entry 165 (class 1259 OID 16407)
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
-- TOC entry 166 (class 1259 OID 16413)
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
-- TOC entry 2206 (class 0 OID 0)
-- Dependencies: 166
-- Name: factory_defaults_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE factory_defaults_index_seq OWNED BY factory_defaults.index;


--
-- TOC entry 2207 (class 0 OID 0)
-- Dependencies: 166
-- Name: factory_defaults_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('factory_defaults_index_seq', 35, true);


--
-- TOC entry 167 (class 1259 OID 16415)
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
-- TOC entry 168 (class 1259 OID 16421)
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
-- TOC entry 2208 (class 0 OID 0)
-- Dependencies: 168
-- Name: glance_defaults_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE glance_defaults_index_seq OWNED BY glance_defaults.index;


--
-- TOC entry 2209 (class 0 OID 0)
-- Dependencies: 168
-- Name: glance_defaults_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('glance_defaults_index_seq', 5, true);


--
-- TOC entry 169 (class 1259 OID 16423)
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
-- TOC entry 170 (class 1259 OID 16429)
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
-- TOC entry 2210 (class 0 OID 0)
-- Dependencies: 170
-- Name: TABLE net_adapter_settings; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE net_adapter_settings IS 'All of the network settings used in the transcirrus system. This does not include the the virtual machine networks. Only for physical system network adapters. Table is set for all bonds when the system is installed';


--
-- TOC entry 2211 (class 0 OID 0)
-- Dependencies: 170
-- Name: COLUMN net_adapter_settings.net_alias; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN net_adapter_settings.net_alias IS 'this is an alias name ex. mgmt - management, uplink - uplink adapter - data - datanet adapter';


--
-- TOC entry 171 (class 1259 OID 16436)
-- Name: network_settings_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE net_adapter_settings_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.net_adapter_settings_index_seq OWNER TO transuser;

--
-- TOC entry 2212 (class 0 OID 0)
-- Dependencies: 171
-- Name: network_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE network_settings_index_seq OWNED BY net_adapter_settings.index;


--
-- TOC entry 2213 (class 0 OID 0)
-- Dependencies: 171
-- Name: network_settings_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('network_settings_index_seq', 1, true);


--
-- TOC entry 172 (class 1259 OID 16438)
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
-- TOC entry 173 (class 1259 OID 16444)
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
-- TOC entry 2214 (class 0 OID 0)
-- Dependencies: 173
-- Name: neutron_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE neutron_default_index_seq OWNED BY neutron_default.index;


--
-- TOC entry 2215 (class 0 OID 0)
-- Dependencies: 173
-- Name: neutron_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('neutron_default_index_seq', 3, true);


--
-- TOC entry 174 (class 1259 OID 16446)
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
-- TOC entry 175 (class 1259 OID 16452)
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
-- TOC entry 2216 (class 0 OID 0)
-- Dependencies: 175
-- Name: neutron_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE neutron_node_index_seq OWNED BY neutron_node.index;


--
-- TOC entry 2217 (class 0 OID 0)
-- Dependencies: 175
-- Name: neutron_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('neutron_node_index_seq', 43, true);


--
-- TOC entry 176 (class 1259 OID 16454)
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
-- TOC entry 2218 (class 0 OID 0)
-- Dependencies: 176
-- Name: TABLE nova_default; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE nova_default IS 'The default values for the nova config files. These are generally the values that are used on the ciac node.';


--
-- TOC entry 177 (class 1259 OID 16460)
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
-- TOC entry 2219 (class 0 OID 0)
-- Dependencies: 177
-- Name: nova_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE nova_default_index_seq OWNED BY nova_default.index;


--
-- TOC entry 2220 (class 0 OID 0)
-- Dependencies: 177
-- Name: nova_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('nova_default_index_seq', 16, true);


--
-- TOC entry 178 (class 1259 OID 16462)
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
-- TOC entry 179 (class 1259 OID 16468)
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
-- TOC entry 2221 (class 0 OID 0)
-- Dependencies: 179
-- Name: nova_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE nova_node_index_seq OWNED BY nova_node.index;


--
-- TOC entry 2222 (class 0 OID 0)
-- Dependencies: 179
-- Name: nova_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('nova_node_index_seq', 56, true);

--
-- TOC entry 209 (class 1259 OID 27521)
-- Name: ceilometer_default; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE ceilometer_default (
    parameter character varying,
    param_value character varying,
    file_name character varying,
    index integer NOT NULL
);


ALTER TABLE public.ceilometer_default OWNER TO transuser;

--
-- TOC entry 208 (class 1259 OID 27519)
-- Name: ceilometer_default_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE ceilometer_default_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ceilometer_default_index_seq OWNER TO transuser;

--
-- TOC entry 1999 (class 0 OID 0)
-- Dependencies: 208
-- Name: ceilometer_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE ceilometer_default_index_seq OWNED BY ceilometer_default.index;


--
-- TOC entry 2000 (class 0 OID 0)
-- Dependencies: 208
-- Name: ceilometer_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('ceilometer_default_index_seq', 1, false);


--
-- TOC entry 211 (class 1259 OID 27532)
-- Name: ceilometer_node; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE ceilometer_node (
    parameter character varying,
    param_value character varying,
    file_name character varying,
    node character varying,
    index integer NOT NULL
);


ALTER TABLE public.ceilometer_node OWNER TO transuser;

--
-- TOC entry 210 (class 1259 OID 27530)
-- Name: ceilometer_node_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE ceilometer_node_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ceilometer_node_index_seq OWNER TO transuser;

--
-- TOC entry 2001 (class 0 OID 0)
-- Dependencies: 210
-- Name: ceilometer_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE ceilometer_node_index_seq OWNED BY ceilometer_node.index;


--
-- TOC entry 2002 (class 0 OID 0)
-- Dependencies: 210
-- Name: ceilometer_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('ceilometer_node_index_seq', 1, false);


--
-- TOC entry 207 (class 1259 OID 27510)
-- Name: heat_default; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE heat_default (
    parameter character varying,
    param_value character varying,
    file_name character varying,
    index integer NOT NULL
);


ALTER TABLE public.heat_default OWNER TO transuser;

--
-- TOC entry 206 (class 1259 OID 27508)
-- Name: heat_default_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE heat_default_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.heat_default_index_seq OWNER TO transuser;

--
-- TOC entry 2003 (class 0 OID 0)
-- Dependencies: 206
-- Name: heat_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE heat_default_index_seq OWNED BY heat_default.index;


--
-- TOC entry 2004 (class 0 OID 0)
-- Dependencies: 206
-- Name: heat_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('heat_default_index_seq', 1, false);


--
-- TOC entry 1986 (class 2604 OID 27524)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY ceilometer_default ALTER COLUMN index SET DEFAULT nextval('ceilometer_default_index_seq'::regclass);


--
-- TOC entry 1987 (class 2604 OID 27535)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY ceilometer_node ALTER COLUMN index SET DEFAULT nextval('ceilometer_node_index_seq'::regclass);


--
-- TOC entry 1985 (class 2604 OID 27513)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY heat_default ALTER COLUMN index SET DEFAULT nextval('heat_default_index_seq'::regclass);

--
-- TOC entry 1991 (class 2606 OID 27529)
-- Name: ceilometer_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY ceilometer_default
    ADD CONSTRAINT ceilometer_default_pkey PRIMARY KEY (index);


--
-- TOC entry 1991 (class 2606 OID 27529)
-- Name: ceilometer_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY ceilometer_node
    ADD CONSTRAINT ceilometer_node_pkey PRIMARY KEY (index);

--
-- TOC entry 1989 (class 2606 OID 27518)
-- Name: heat_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY heat_default
    ADD CONSTRAINT heat_default_pkey PRIMARY KEY (index);

--
-- TOC entry 180 (class 1259 OID 16470)
-- Name: projects; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE projects (
    proj_id character varying NOT NULL,
    proj_name character varying,
    def_security_key_name character varying,
    def_security_key_id character varying DEFAULT 0,
    def_security_group_id character varying DEFAULT 0,
    def_security_group_name character varying,
    host_system_name character varying,
    host_system_ip character varying,
    def_network_name character varying,
    def_network_id character varying DEFAULT 0
);


ALTER TABLE public.projects OWNER TO transuser;

--
-- TOC entry 2223 (class 0 OID 0)
-- Dependencies: 180
-- Name: COLUMN projects.def_security_key_name; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.def_security_key_name IS 'Default security key made during project creation';


--
-- TOC entry 2224 (class 0 OID 0)
-- Dependencies: 180
-- Name: COLUMN projects.def_security_key_id; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.def_security_key_id IS 'default security key id made at project creation';


--
-- TOC entry 2225 (class 0 OID 0)
-- Dependencies: 180
-- Name: COLUMN projects.host_system_name; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.host_system_name IS 'Name of the cloud controller';


--
-- TOC entry 2226 (class 0 OID 0)
-- Dependencies: 180
-- Name: COLUMN projects.host_system_ip; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN projects.host_system_ip IS 'API ip associated with the cloud controller';


--
-- TOC entry 181 (class 1259 OID 16476)
-- Name: psql_buildout; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE psql_buildout (
    index bigint DEFAULT 0 NOT NULL,
    component character(1),
    command character varying
);


ALTER TABLE public.psql_buildout OWNER TO transuser;

--
-- TOC entry 182 (class 1259 OID 16483)
-- Name: swift_default; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE swift_default (
    paramter character varying,
    param_value character varying,
    file_name character varying,
    index integer NOT NULL
);


ALTER TABLE public.swift_default OWNER TO transuser;

--
-- TOC entry 183 (class 1259 OID 16489)
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
-- TOC entry 2227 (class 0 OID 0)
-- Dependencies: 183
-- Name: swift_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE swift_default_index_seq OWNED BY swift_default.index;


--
-- TOC entry 2228 (class 0 OID 0)
-- Dependencies: 183
-- Name: swift_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('swift_default_index_seq', 1, false);


--
-- TOC entry 184 (class 1259 OID 16491)
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
-- TOC entry 185 (class 1259 OID 16497)
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
-- TOC entry 2229 (class 0 OID 0)
-- Dependencies: 185
-- Name: swift_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE swift_node_index_seq OWNED BY swift_node.index;


--
-- TOC entry 2230 (class 0 OID 0)
-- Dependencies: 185
-- Name: swift_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('swift_node_index_seq', 1, false);


--
-- TOC entry 186 (class 1259 OID 16499)
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
-- TOC entry 2231 (class 0 OID 0)
-- Dependencies: 186
-- Name: TABLE system_default_settings; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE system_default_settings IS 'A read only system default table used to set the system back to the factory default settings.';


--
-- TOC entry 187 (class 1259 OID 16505)
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
-- TOC entry 2232 (class 0 OID 0)
-- Dependencies: 187
-- Name: system_default_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE system_default_settings_index_seq OWNED BY system_default_settings.index;


--
-- TOC entry 2233 (class 0 OID 0)
-- Dependencies: 187
-- Name: system_default_settings_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('system_default_settings_index_seq', 1, false);


--
-- TOC entry 188 (class 1259 OID 16507)
-- Name: trans_floating_ip; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_floating_ip (
    index integer NOT NULL,
    floating_ip character varying,
    floating_ip_id character varying,
    proj_id character varying,
    router_id character varying,
    fixed_ip character varying,
    in_use character varying DEFAULT false
);


ALTER TABLE public.trans_floating_ip OWNER TO transuser;

--
-- TOC entry 189 (class 1259 OID 16513)
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
-- TOC entry 2234 (class 0 OID 0)
-- Dependencies: 189
-- Name: trans_floating_ip_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_floating_ip_index_seq OWNED BY trans_floating_ip.index;


--
-- TOC entry 2235 (class 0 OID 0)
-- Dependencies: 189
-- Name: trans_floating_ip_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_floating_ip_index_seq', 1, false);


--
-- TOC entry 190 (class 1259 OID 16515)
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
    inst_user_id character varying,
    inst_flav_name character varying,
    inst_floating_ip character varying,
    inst_ext_net_id character varying,
    inst_int_ip character varying,
    inst_int_net_id character varying,
    inst_int_net_name character varying,
    inst_image_name character varying,
    inst_name character varying,
    inst_zone character varying DEFAULT 'nova'::character varying,
    inst_confirm_resize integer DEFAULT 0,
    inst_resize_julian_date character varying,
    inst_resize_hr_date character varying
);


ALTER TABLE public.trans_instances OWNER TO transuser;

--
-- TOC entry 191 (class 1259 OID 16521)
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
-- TOC entry 192 (class 1259 OID 16527)
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
-- TOC entry 2236 (class 0 OID 0)
-- Dependencies: 192
-- Name: trans_network_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_network_settings_index_seq OWNED BY trans_network_settings.index;


--
-- TOC entry 2237 (class 0 OID 0)
-- Dependencies: 192
-- Name: trans_network_settings_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_network_settings_index_seq', 43, true);


--
-- TOC entry 193 (class 1259 OID 16529)
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
    node_fault_flag character varying,
    node_ready_flag character varying,
    node_gluster_peer character varying,
    node_gluster_disks character varying
);


ALTER TABLE public.trans_nodes OWNER TO transuser;

--
-- TOC entry 2238 (class 0 OID 0)
-- Dependencies: 193
-- Name: COLUMN trans_nodes.node_controller; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_nodes.node_controller IS 'ciac system node is connected to';


--
-- TOC entry 2239 (class 0 OID 0)
-- Dependencies: 193
-- Name: COLUMN trans_nodes.node_cloud_name; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_nodes.node_cloud_name IS 'cloud name the node belongs to. ex RegionOne';


--
-- TOC entry 194 (class 1259 OID 16535)
-- Name: trans_routers; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_routers (
    index integer NOT NULL,
    router_name character varying,
    router_id character varying,
    net_id character varying,
    proj_id character varying,
    router_status character varying,
    router_int_subnet_id character varying,
    router_int_conn_id character varying,
    router_int_port_id character varying,
    router_admin_state_up character varying,
    router_ext_gateway character varying,
    router_ext_ip character varying
);


ALTER TABLE public.trans_routers OWNER TO transuser;


--
-- TOC entry 195 (class 1259 OID 16543)
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
-- TOC entry 2242 (class 0 OID 0)
-- Dependencies: 195
-- Name: trans_routers_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_routers_index_seq OWNED BY trans_routers.index;


--
-- TOC entry 2243 (class 0 OID 0)
-- Dependencies: 195
-- Name: trans_routers_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_routers_index_seq', 1, false);


--
-- TOC entry 196 (class 1259 OID 16545)
-- Name: trans_security_group; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_security_group (
    index integer NOT NULL,
    proj_id character varying,
    user_name character varying,
    user_id character varying,
    sec_group_id character varying,
    sec_group_name character varying,
    sec_group_desc character varying
);


ALTER TABLE public.trans_security_group OWNER TO transuser;

--
-- TOC entry 197 (class 1259 OID 16551)
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
-- TOC entry 2244 (class 0 OID 0)
-- Dependencies: 197
-- Name: trans_security_group_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_group_index_seq', 1, false);


--
-- TOC entry 198 (class 1259 OID 16553)
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
-- TOC entry 2245 (class 0 OID 0)
-- Dependencies: 198
-- Name: trans_security_group_index_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_security_group_index_seq1 OWNED BY trans_security_group.index;


--
-- TOC entry 2246 (class 0 OID 0)
-- Dependencies: 198
-- Name: trans_security_group_index_seq1; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_group_index_seq1', 31, true);


--
-- TOC entry 199 (class 1259 OID 16555)
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
-- TOC entry 2247 (class 0 OID 0)
-- Dependencies: 199
-- Name: trans_security_key_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_key_index_seq', 1, false);


--
-- TOC entry 200 (class 1259 OID 16557)
-- Name: trans_security_keys; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_security_keys (
    proj_id character varying,
    user_name character varying,
    user_id character varying,
    sec_key_id character varying,
    sec_key_name character varying,
    public_key text,
    private_key text,
    index integer NOT NULL
);


ALTER TABLE public.trans_security_keys OWNER TO transuser;

--
-- TOC entry 2248 (class 0 OID 0)
-- Dependencies: 200
-- Name: COLUMN trans_security_keys.public_key; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON COLUMN trans_security_keys.public_key IS 'public key';


--
-- TOC entry 201 (class 1259 OID 16563)
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
-- TOC entry 2249 (class 0 OID 0)
-- Dependencies: 201
-- Name: trans_security_keys_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_keys_index_seq', 1, false);


--
-- TOC entry 202 (class 1259 OID 16565)
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
-- TOC entry 2250 (class 0 OID 0)
-- Dependencies: 202
-- Name: trans_security_keys_index_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_security_keys_index_seq1 OWNED BY trans_security_keys.index;


--
-- TOC entry 2251 (class 0 OID 0)
-- Dependencies: 202
-- Name: trans_security_keys_index_seq1; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_security_keys_index_seq1', 23, true);


--
-- TOC entry 203 (class 1259 OID 16567)
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
-- TOC entry 2252 (class 0 OID 0)
-- Dependencies: 203
-- Name: TABLE trans_service_settings; Type: COMMENT; Schema: public; Owner: transuser
--

COMMENT ON TABLE trans_service_settings IS 'ensure that when the install is done all values except service_ip and service_id are filled in';


--
-- TOC entry 204 (class 1259 OID 16573)
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
-- TOC entry 205 (class 1259 OID 16580)
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
-- TOC entry 2253 (class 0 OID 0)
-- Dependencies: 205
-- Name: trans_subnets_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_subnets_index_seq OWNED BY trans_subnets.index;


--
-- TOC entry 2254 (class 0 OID 0)
-- Dependencies: 205
-- Name: trans_subnets_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_subnets_index_seq', 2, true);


--
-- TOC entry 206 (class 1259 OID 16582)
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
-- TOC entry 207 (class 1259 OID 16588)
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
-- TOC entry 2255 (class 0 OID 0)
-- Dependencies: 207
-- Name: trans_system_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_system_settings_index_seq OWNED BY trans_system_settings.index;


--
-- TOC entry 2256 (class 0 OID 0)
-- Dependencies: 207
-- Name: trans_system_settings_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_system_settings_index_seq', 86, true);


--
-- TOC entry 208 (class 1259 OID 16590)
-- Name: trans_system_snapshots; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_system_snapshots (
    snap_id character varying NOT NULL,
    vol_id character varying,
    proj_id character varying,
    user_id character varying,
    snap_name character varying,
    snap_desc character varying
);


ALTER TABLE public.trans_system_snapshots OWNER TO transuser;

--
-- TOC entry 209 (class 1259 OID 16596)
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
    vol_attached_to_inst character varying,
    vol_mount_location character varying,
    vol_type character varying(15),
    vol_zone character varying
);


ALTER TABLE public.trans_system_vols OWNER TO transuser;

--
-- TOC entry 210 (class 1259 OID 16605)
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
-- TOC entry 211 (class 1259 OID 16611)
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
-- TOC entry 2257 (class 0 OID 0)
-- Dependencies: 211
-- Name: trans_user_info_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_user_info_index_seq OWNED BY trans_user_info.index;


--
-- TOC entry 2258 (class 0 OID 0)
-- Dependencies: 211
-- Name: trans_user_info_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_user_info_index_seq', 49, true);


--
-- TOC entry 212 (class 1259 OID 16613)
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
-- TOC entry 2259 (class 0 OID 0)
-- Dependencies: 212
-- Name: user_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('user_seq', 1, false);


--
-- TOC entry 213 (class 1259 OID 25179)
-- Name: trans_public_subnets; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_public_subnets (
    index integer NOT NULL,
    subnet_name character varying,
    subnet_id character varying,
    subnet_dhcp_enable character varying,
    subnet_range_start character varying,
    subnet_range_end character varying,
    subnet_gateway character varying,
    subnet_mask character varying,
    subnet_ip_ver character(1) DEFAULT 4,
    proj_id character varying,
    net_id character varying
);


ALTER TABLE public.trans_public_subnets OWNER TO transuser;

--
-- TOC entry 214 (class 1259 OID 25182)
-- Name: trans_public_subnets_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_public_subnets_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_public_subnets_index_seq OWNER TO transuser;

--
-- TOC entry 2054 (class 0 OID 0)
-- Dependencies: 214
-- Name: trans_public_subnets_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_public_subnets_index_seq OWNED BY trans_public_subnets.index;


--
-- TOC entry 2055 (class 0 OID 0)
-- Dependencies: 214
-- Name: trans_public_subnets_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_public_subnets_index_seq', 1, false);


--
-- TOC entry 2044 (class 2604 OID 25184)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_public_subnets ALTER COLUMN index SET DEFAULT nextval('trans_public_subnets_index_seq'::regclass);

--
-- TOC entry 2047 (class 2606 OID 25193)
-- Name: trans_public_subnets_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_public_subnets
    ADD CONSTRAINT trans_public_subnets_pkey PRIMARY KEY (index);


--
-- TOC entry 2048 (class 1259 OID 25194)
-- Name: trans_public_subnets_subnet_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_public_subnets_subnet_id_idx ON trans_public_subnets USING btree (subnet_id);


--
-- TOC entry 200 (class 1259 OID 19357)
-- Name: ha_default; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE ha_default (
    parameter character varying,
    param_value character varying,
    file_name character varying,
    index integer NOT NULL
);


ALTER TABLE public.ha_default OWNER TO transuser;

--
-- TOC entry 203 (class 1259 OID 19372)
-- Name: ha_default_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE ha_default_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ha_default_index_seq OWNER TO transuser;

--
-- TOC entry 1973 (class 0 OID 0)
-- Dependencies: 203
-- Name: ha_default_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE ha_default_index_seq OWNED BY ha_default.index;


--
-- TOC entry 1974 (class 0 OID 0)
-- Dependencies: 203
-- Name: ha_default_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('ha_default_index_seq', 1, false);


--
-- TOC entry 202 (class 1259 OID 19362)
-- Name: ha_node; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE ha_node (
    parameter character varying,
    param_value character varying,
    file_name character varying,
    node character varying,
    index integer NOT NULL
);


ALTER TABLE public.ha_node OWNER TO transuser;

--
-- TOC entry 201 (class 1259 OID 19360)
-- Name: ha_node_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE ha_node_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ha_node_index_seq OWNER TO transuser;

--
-- TOC entry 1975 (class 0 OID 0)
-- Dependencies: 201
-- Name: ha_node_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE ha_node_index_seq OWNED BY ha_node.index;


--
-- TOC entry 1976 (class 0 OID 0)
-- Dependencies: 201
-- Name: ha_node_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('ha_node_index_seq', 1, false);


--
-- TOC entry 1961 (class 2604 OID 19374)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY ha_default ALTER COLUMN index SET DEFAULT nextval('ha_default_index_seq'::regclass);


--
-- TOC entry 1962 (class 2604 OID 19365)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY ha_node ALTER COLUMN index SET DEFAULT nextval('ha_node_index_seq'::regclass);

--
-- TOC entry 1964 (class 2606 OID 19382)
-- Name: ha_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY ha_default
    ADD CONSTRAINT ha_default_pkey PRIMARY KEY (index);


--
-- TOC entry 1966 (class 2606 OID 19384)
-- Name: ha_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY ha_node
    ADD CONSTRAINT ha_node_pkey PRIMARY KEY (index);



--
-- TOC entry 2066 (class 2604 OID 16615)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY cinder_default ALTER COLUMN index SET DEFAULT nextval('cinder_default_index_seq'::regclass);


--
-- TOC entry 2067 (class 2604 OID 16616)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY cinder_node ALTER COLUMN index SET DEFAULT nextval('cinder_node_index_seq'::regclass);


--
-- TOC entry 2068 (class 2604 OID 16617)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY factory_defaults ALTER COLUMN index SET DEFAULT nextval('factory_defaults_index_seq'::regclass);


--
-- TOC entry 2069 (class 2604 OID 16618)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY glance_defaults ALTER COLUMN index SET DEFAULT nextval('glance_defaults_index_seq'::regclass);


--
-- TOC entry 2071 (class 2604 OID 16619)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY net_adapter_settings ALTER COLUMN index SET DEFAULT nextval('network_settings_index_seq'::regclass);


--
-- TOC entry 2072 (class 2604 OID 16620)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY neutron_default ALTER COLUMN index SET DEFAULT nextval('neutron_default_index_seq'::regclass);


--
-- TOC entry 2073 (class 2604 OID 16621)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY neutron_node ALTER COLUMN index SET DEFAULT nextval('neutron_node_index_seq'::regclass);


--
-- TOC entry 2074 (class 2604 OID 16622)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY nova_default ALTER COLUMN index SET DEFAULT nextval('nova_default_index_seq'::regclass);


--
-- TOC entry 2075 (class 2604 OID 16623)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY nova_node ALTER COLUMN index SET DEFAULT nextval('nova_node_index_seq'::regclass);


--
-- TOC entry 2077 (class 2604 OID 16624)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY swift_default ALTER COLUMN index SET DEFAULT nextval('swift_default_index_seq'::regclass);


--
-- TOC entry 2078 (class 2604 OID 16625)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY swift_node ALTER COLUMN index SET DEFAULT nextval('swift_node_index_seq'::regclass);


--
-- TOC entry 2079 (class 2604 OID 16626)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY system_default_settings ALTER COLUMN index SET DEFAULT nextval('system_default_settings_index_seq'::regclass);


--
-- TOC entry 2080 (class 2604 OID 16627)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_floating_ip ALTER COLUMN index SET DEFAULT nextval('trans_floating_ip_index_seq'::regclass);


--
-- TOC entry 2081 (class 2604 OID 16628)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_network_settings ALTER COLUMN index SET DEFAULT nextval('trans_network_settings_index_seq'::regclass);


--
-- TOC entry 2084 (class 2604 OID 16629)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_routers ALTER COLUMN index SET DEFAULT nextval('trans_routers_index_seq'::regclass);


--
-- TOC entry 2085 (class 2604 OID 16630)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_security_group ALTER COLUMN index SET DEFAULT nextval('trans_security_group_index_seq1'::regclass);


--
-- TOC entry 2086 (class 2604 OID 16631)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_security_keys ALTER COLUMN index SET DEFAULT nextval('trans_security_keys_index_seq1'::regclass);


--
-- TOC entry 2088 (class 2604 OID 16632)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_subnets ALTER COLUMN index SET DEFAULT nextval('trans_subnets_index_seq'::regclass);


--
-- TOC entry 2089 (class 2604 OID 16633)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_system_settings ALTER COLUMN index SET DEFAULT nextval('trans_system_settings_index_seq'::regclass);


--
-- TOC entry 2093 (class 2604 OID 16634)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_user_info ALTER COLUMN index SET DEFAULT nextval('trans_user_info_index_seq'::regclass);

--
-- TOC entry 2166 (class 0 OID 16391)
-- Dependencies: 161
-- Data for Name: heat_default; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO heat_default VALUES ('verbose', 'False', 'heat.conf', 1);
INSERT INTO heat_default VALUES ('debug', 'False', 'heat.conf', 2);
INSERT INTO heat_default VALUES ('rabbit_userid', 'guest', 'heat.conf', 3);
INSERT INTO heat_default VALUES ('rabbit_password', 'transcirrus1', 'heat.conf', 4);
INSERT INTO heat_default VALUES ('admin_user', 'heat', 'heat.conf', 5);
INSERT INTO heat_default VALUES ('admin_password', 'transcirrus1', 'heat.conf', 6);


--
-- TOC entry 2166 (class 0 OID 16391)
-- Dependencies: 161
-- Data for Name: ceilometer_default; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO ceilometer_default VALUES ('verbose', 'False', 'ceilometer.conf', 1);
INSERT INTO ceilometer_default VALUES ('debug', 'False', 'ceilometer.conf', 2);
INSERT INTO ceilometer_default VALUES ('rabbit_userid', 'guest', 'ceilometer.conf', 3);
INSERT INTO ceilometer_default VALUES ('rabbit_password', 'transcirrus1', 'ceilometer.conf', 4);
INSERT INTO ceilometer_default VALUES ('admin_user', 'ceilometer', 'ceilometer.conf', 5);
INSERT INTO ceilometer_default VALUES ('admin_password', 'transcirrus1', 'ceilometer.conf', 6);
INSERT INTO ceilometer_default VALUES ('os_username', 'ceilometer', 'ceilometer.conf', 7);
INSERT INTO ceilometer_default VALUES ('os_password', 'transcirrus1', 'ceilometer.conf', 8);



--
-- TOC entry 2166 (class 0 OID 16391)
-- Dependencies: 161
-- Data for Name: cinder_default; Type: TABLE DATA; Schema: public; Owner: transuser
--

--INSERT INTO cinder_default VALUES ('auth_host', '172.24.24.10', 'api-paste.ini', 1);
--INSERT INTO cinder_default VALUES ('auth_port', '35357', 'api-paste.ini', 2);
INSERT INTO cinder_default VALUES ('auth_protocol', 'http', 'api-paste.ini', 3);
--INSERT INTO cinder_default VALUES ('auth_uri', '172.24.24.10:5000', 'api-paste.ini', 4);
INSERT INTO cinder_default VALUES ('service_protocol', 'http', 'api-paste.ini', 5);
--INSERT INTO cinder_default VALUES ('admin_tenant_name', 'service', 'api-paste.ini', 6);
--INSERT INTO cinder_default VALUES ('admin_user', 'cinder', 'api-paste.ini', 7);
--INSERT INTO cinder_default VALUES ('signing_dir', '/var/lib/cinder', 'api-paste.ini', 8);
INSERT INTO cinder_default VALUES ('admin_password', 'transcirrus1', 'api-paste.ini', 9);
INSERT INTO cinder_default VALUES ('verbose', 'False', 'cinder.conf', 10);
INSERT INTO cinder_default VALUES ('debug', 'False', 'cinder.conf', 11);
--INSERT INTO cinder_default VALUES ('auth_stratagy', 'keystone', 'cinder.conf', 12);
--INSERT INTO cinder_default VALUES ('auth_uri', 'http://172.24.24.10:5000', 'cinder.conf', 13);
INSERT INTO cinder_default VALUES ('auth_protocol', 'http', 'cinder.conf', 14);
--INSERT INTO cinder_default VALUES ('auth_port', '35357', 'cinder.conf', 15);
--INSERT INTO cinder_default VALUES ('auth_host', '172.24.24.10', 'cinder.conf', 16);
--INSERT INTO cinder_default VALUES ('admin_user', 'cinder', 'cinder.conf', 17);
--INSERT INTO cinder_default VALUES ('admin_tenant_name', 'service', 'cinder.conf', 18);
INSERT INTO cinder_default VALUES ('admin_password', 'transcirrus1', 'cinder.conf', 19);
INSERT INTO cinder_default VALUES ('state_path', '/var/lib/cinder', 'cinder.conf', 20);
INSERT INTO cinder_default VALUES ('lock_path', '/var/lib/cinder', 'cinder.conf', 21);
INSERT INTO cinder_default VALUES ('volumes_dir', '/var/lib/cinder/volumes', 'cinder.conf', 22);
INSERT INTO cinder_default VALUES ('rpc_backend', 'rabbit', 'cinder.conf', 23);
--INSERT INTO cinder_default VALUES ('rabbit_host', '172.24.24.10', 'cinder.conf', 24);
--INSERT INTO cinder_default VALUES ('rabbit_port', '5672', 'cinder.conf', 25);
INSERT INTO cinder_default VALUES ('rabbit_userid', 'guest', 'cinder.conf', 26);
INSERT INTO cinder_default VALUES ('rabbit_password', 'transcirrus1', 'cinder.conf', 27);
INSERT INTO cinder_default VALUES ('default_availability_zone', 'nova', 'cinder.conf', 28);
INSERT INTO cinder_default VALUES ('scheduler_default_filters', 'AvailabilityZoneFilter,CapacityFilter,CapabilitiesFilter', 'cinder.conf', 29);
--INSERT INTO cinder_default VALUES ('storage_availability_zone', 'nova', 'cinder.conf', 30);
INSERT INTO cinder_default VALUES ('volume_name_template', 'TransCirrus-volume-%s', 'cinder.conf', 31);

--
-- TOC entry 2169 (class 0 OID 16415)
-- Dependencies: 167
-- Data for Name: glance_defaults; Type: TABLE DATA; Schema: public; Owner: transuser
--
INSERT INTO glance_defaults VALUES ('verbose', 'False', 'NULL', 'glance-api.conf', 1);
INSERT INTO glance_defaults VALUES ('debug', 'False', 'NULL', 'glance-api.conf', 2);
INSERT INTO glance_defaults VALUES ('bind_host', '0.0.0.0', 'NULL', 'glance-api.conf', 3);
INSERT INTO glance_defaults VALUES ('bind_port', '9292', 'NULL', 'glance-api.conf', 4);
INSERT INTO glance_defaults VALUES ('enable_v1_api', 'True', 'NULL', 'glance-api.conf', 5);
INSERT INTO glance_defaults VALUES ('enable_v2_api', 'True', 'NULL', 'glance-api.conf', 6);
INSERT INTO glance_defaults VALUES ('show_image_direct_url', 'True', 'NULL', 'glance-api.conf', 7);
INSERT INTO glance_defaults VALUES ('container_formats', 'ami,ari,aki,bare,ovf,ova', 'NULL', 'glance-api.conf', 8);
INSERT INTO glance_defaults VALUES ('disk_formats', 'ami,ari,aki,vhd,vmdk,raw,qcow2,vdi,iso', 'NULL', 'glance-api.conf', 9);
INSERT INTO glance_defaults VALUES ('registry_host', '0.0.0.0', 'NULL', 'glance-api.conf', 10);
INSERT INTO glance_defaults VALUES ('registry_port', '9191', 'NULL', 'glance-api.conf', 11);
INSERT INTO glance_defaults VALUES ('rabbit_host', 'localhost', 'NULL', 'glance-api.conf', 12);
INSERT INTO glance_defaults VALUES ('rabbit_port', '5672', 'NULL', 'glance-api.conf', 13);
INSERT INTO glance_defaults VALUES ('rabbit_userid', 'guest', 'NULL', 'glance-api.conf', 14);
INSERT INTO glance_defaults VALUES ('rabbit_password', 'transcirrus1', 'NULL', 'glance-api.conf', 15);
INSERT INTO glance_defaults VALUES ('rabbit_notification_exchange', 'glance', 'NULL', 'glance-api.conf', 16);
INSERT INTO glance_defaults VALUES ('auth_host', 'localhost', 'NULL', 'glance-api.conf', 17);
INSERT INTO glance_defaults VALUES ('auth_uri', 'localhost:5000', 'NULL', 'glance-api.conf', 18);
INSERT INTO glance_defaults VALUES ('auth_port', '35357', 'NULL', 'glance-api.conf', 19);
INSERT INTO glance_defaults VALUES ('auth_protocol', 'http', 'NULL', 'glance-api.conf', 20);
INSERT INTO glance_defaults VALUES ('admin_tenant_name', 'service', 'NULL', 'glance-api.conf', 21);
INSERT INTO glance_defaults VALUES ('admin_user', 'glance', 'NULL', 'glance-api.conf', 22);
INSERT INTO glance_defaults VALUES ('admin_password', 'transcirrus1', 'NULL', 'glance-api.conf', 23);
INSERT INTO glance_defaults VALUES ('flavor', 'keystone', 'NULL', 'glance-api.conf', 24);
INSERT INTO glance_defaults VALUES ('workers', '6', 'NULL', 'glance-api.conf', 25);
INSERT INTO glance_defaults VALUES ('verbose', 'False', 'NULL', 'glance-registry.conf', 26);
INSERT INTO glance_defaults VALUES ('debug', 'False', 'NULL', 'glance-registry.conf', 27);
INSERT INTO glance_defaults VALUES ('bind_host', '0.0.0.0', 'NULL', 'glance-registry.conf', 28);
INSERT INTO glance_defaults VALUES ('bind_port', '9191', 'NULL', 'glance-registry.conf', 29);
INSERT INTO glance_defaults VALUES ('enable_v1_registry', 'True', 'NULL', 'glance-registry.conf', 30);
INSERT INTO glance_defaults VALUES ('enable_v2_registry', 'True', 'NULL', 'glance-registry.conf', 31);
INSERT INTO glance_defaults VALUES ('auth_host', 'localhost', 'NULL', 'glance-registry.conf', 32);
INSERT INTO glance_defaults VALUES ('auth_uri', 'localhost:5000', 'NULL', 'glance-registry.conf', 33);
INSERT INTO glance_defaults VALUES ('auth_port', '35357', 'NULL', 'glance-registry.conf', 34);
INSERT INTO glance_defaults VALUES ('auth_protocol', 'http', 'NULL', 'glance-registry.conf', 35);
INSERT INTO glance_defaults VALUES ('admin_tenant_name', 'service', 'NULL', 'glance-registry.conf', 36);
INSERT INTO glance_defaults VALUES ('admin_user', 'glance', 'NULL', 'glance-registry.conf', 37);
INSERT INTO glance_defaults VALUES ('admin_password', 'transcirrus1', 'NULL', 'glance-registry.conf', 38);
INSERT INTO glance_defaults VALUES ('flavor', 'keystone', 'NULL', 'glance-registry.conf', 39);
INSERT INTO glance_defaults VALUES ('verbose', 'False', 'NULL', 'glance-scrubber.conf', 40);
INSERT INTO glance_defaults VALUES ('debug', 'False', 'NULL', 'glance-scrubber.conf', 41);
INSERT INTO glance_defaults VALUES ('use_syslog', 'False', 'NULL', 'glance-scrubber.conf', 42);
INSERT INTO glance_defaults VALUES ('registry_host', '0.0.0.0', 'NULL', 'glance-scrubber.conf', 43);
INSERT INTO glance_defaults VALUES ('registry_port', '9191', 'NULL', 'glance-scrubber.conf', 44);
INSERT INTO glance_defaults VALUES ('auth_url', 'http://localhost:5000/v2.0/', 'NULL', 'glance-scrubber.conf', 45);
INSERT INTO glance_defaults VALUES ('admin_tenant_name', 'service', 'NULL', 'glance-scrubber.conf', 46);
INSERT INTO glance_defaults VALUES ('admin_user', 'glance', 'NULL', 'glance-scrubber.conf', 47);
INSERT INTO glance_defaults VALUES ('admin_password', 'transcirrus1', 'NULL', 'glance-scrubber.conf', 48);
--INSERT INTO glance_defaults VALUES ('connection', 'postgresql://transuser:transcirrus1@localhost/glance', 'NULL', 'glance-api.conf', 1);
--INSERT INTO glance_defaults VALUES ('connection', 'postgresql://transuser:transcirrus1@localhost/glance', 'NULL', 'glance-registry.conf', 6);

--
-- TOC entry 2170 (class 0 OID 16423)
-- Dependencies: 169
-- Data for Name: keystone; Type: TABLE DATA; Schema: public; Owner: transuser
--

--
-- TOC entry 2172 (class 0 OID 16438)
-- Dependencies: 172
-- Data for Name: neutron_default; Type: TABLE DATA; Schema: public; Owner: transuser
--
INSERT INTO neutron_default VALUES ('verbose', 'False', 'dhcp_agent.ini', 1);
INSERT INTO neutron_default VALUES ('debug', 'False', 'dhcp_agent.ini', 2);
INSERT INTO neutron_default VALUES ('enable_isolated_metadata', 'True', 'dhcp_agent.ini', 3);
INSERT INTO neutron_default VALUES ('enable_metadata_network', 'True', 'dhcp_agent.ini', 4);
INSERT INTO neutron_default VALUES ('interface_driver', 'neutron.agent.linux.interface.OVSInterfaceDriver', 'dhcp_agent.ini', 5);
INSERT INTO neutron_default VALUES ('dhcp_driver', 'neutron.agent.linux.dhcp.Dnsmasq', 'dhcp_agent.ini', 6);
INSERT INTO neutron_default VALUES ('verbose', 'False', 'l3_agent.ini', 7);
INSERT INTO neutron_default VALUES ('debug', 'False', 'l3_agent.ini', 8);
INSERT INTO neutron_default VALUES ('interface_driver', 'neutron.agent.linux.interface.OVSInterfaceDriver', 'l3_agent.ini', 9);
INSERT INTO neutron_default VALUES ('use_namespaces', 'True', 'l3_agent.ini', 10);
INSERT INTO neutron_default VALUES ('external_network_bridge', 'br-ex', 'l3_agent.ini', 11);
INSERT INTO neutron_default VALUES ('enable_metadata_proxy', 'True', 'l3_agent.ini', 12);
INSERT INTO neutron_default VALUES ('debug', 'False', 'metadata_agent.ini', 13);
INSERT INTO neutron_default VALUES ('verbose', 'False', 'metadata_agent.ini', 14);
--INSERT INTO neutron_default VALUES ('auth_url', 'http://172.24.24.10:35357/v2.0', 'metadata_agent.ini', 15);
--INSERT INTO neutron_default VALUES ('auth_region', 'TransCirrusCloud', 'metadata_agent.ini', 16);
INSERT INTO neutron_default VALUES ('admin_tenant_name', 'service', 'metadata_agent.ini', 17);
INSERT INTO neutron_default VALUES ('admin_user', 'neutron', 'metadata_agent.ini', 18);
INSERT INTO neutron_default VALUES ('admin_password', 'transcirrus1', 'metadata_agent.ini', 19);
--INSERT INTO neutron_default VALUES ('nova_metadata_ip', '172.24.24.10', 'metadata_agent.ini', 20);
INSERT INTO neutron_default VALUES ('nova_metadata_port', '8775', 'metadata_agent.ini', 21);
INSERT INTO neutron_default VALUES ('metadata_proxy_shared_secret', 'transcirrus1', 'metadata_agent.ini', 22);
--INSERT INTO neutron_default VALUES ('metadata_workers', '1', 'metadata_agent.ini', 23);
INSERT INTO neutron_default VALUES ('verbose', 'False', 'neutron.conf', 24);
INSERT INTO neutron_default VALUES ('debug', 'False', 'neutron.conf', 25);
INSERT INTO neutron_default VALUES ('bind_host', '0.0.0.0', 'neutron.conf', 26);
INSERT INTO neutron_default VALUES ('bind_port', '9696', 'neutron.conf', 27);
INSERT INTO neutron_default VALUES ('core_plugin', 'ml2', 'neutron.conf', 28);
INSERT INTO neutron_default VALUES ('service_plugins', 'router,metering', 'neutron.conf', 29);
INSERT INTO neutron_default VALUES ('auth_strategy', 'keystone', 'neutron.conf', 30);
INSERT INTO neutron_default VALUES ('control_exchange', 'neutron', 'neutron.conf', 31);
--INSERT INTO neutron_default VALUES ('rabbit_host', '172.24.24.10', 'neutron.conf', 32);
INSERT INTO neutron_default VALUES ('rabbit_password', 'transcirrus1', 'neutron.conf', 33);
--INSERT INTO neutron_default VALUES ('rabbit_port', '5672', 'neutron.conf', 34);
INSERT INTO neutron_default VALUES ('rabbit_userid', 'guest', 'neutron.conf', 35);
--INSERT INTO neutron_default VALUES ('notification_driver', 'neutron.openstack.common.notifier.rpc_notifier', 'neutron.conf', 36);
--INSERT INTO neutron_default VALUES ('agent_down_time', '75', 'neutron.conf', 37);
--INSERT INTO neutron_default VALUES ('notify_nova_on_port_status_changes', 'True', 'neutron.conf', 38);
--INSERT INTO neutron_default VALUES ('notify_nova_on_port_data_changes', 'True', 'neutron.conf', 39);
--INSERT INTO neutron_default VALUES ('nova_url', 'http://172.24.24.10:8774/v2', 'neutron.conf', 40);
--INSERT INTO neutron_default VALUES ('nova_admin_username', 'nova', 'neutron.conf', 41);
INSERT INTO neutron_default VALUES ('nova_admin_password', 'transcirrus1', 'neutron.conf', 42);
--INSERT INTO neutron_default VALUES ('nova_admin_auth_url', 'http://172.24.24.10:35357/v2.0', 'neutron.conf', 43);
--INSERT INTO neutron_default VALUES ('root_helper', 'sudo neutron-rootwrap /etc/neutron/rootwrap.conf', 'neutron.conf', 44);
--INSERT INTO neutron_default VALUES ('auth_host', '172.24.24.10', 'neutron.conf', 45);
--INSERT INTO neutron_default VALUES ('auth_port', '35357', 'neutron.conf', 46);
--INSERT INTO neutron_default VALUES ('auth_uri', '172.24.24.10:5000', 'neutron.conf', 47);
INSERT INTO neutron_default VALUES ('auth_protocol', 'http', 'neutron.conf', 48);
INSERT INTO neutron_default VALUES ('admin_tenant_name', 'service', 'neutron.conf', 49);
--INSERT INTO neutron_default VALUES ('admin_user', 'neutron', 'neutron.conf', 50);
INSERT INTO neutron_default VALUES ('admin_password', 'transcirrus1', 'neutron.conf', 51);
--INSERT INTO neutron_default VALUES ('connection', 'postgresql://transuser:transcirrus1@172.24.24.10/neutron', 'neutron.conf', 52);
INSERT INTO neutron_default VALUES ('type_drivers', 'gre', 'ml2_conf.ini', 53);
INSERT INTO neutron_default VALUES ('tenant_network_types', 'gre', 'ml2_conf.ini', 54);
INSERT INTO neutron_default VALUES ('mechanism_drivers', 'openvswitch', 'ml2_conf.ini', 55);
INSERT INTO neutron_default VALUES ('tunnel_id_ranges', '1:1000', 'ml2_conf.ini', 56);
--INSERT INTO neutron_default VALUES ('firewall_driver', 'neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver', 'ml2_conf.ini', 57);
INSERT INTO neutron_default VALUES ('tunnel_types', 'gre', 'ml2_conf.ini', 58);
--INSERT INTO neutron_default VALUES ('local_ip', '172.24.24.10', 'ml2_conf.ini', 59);
INSERT INTO neutron_default VALUES ('type_drivers', 'gre', 'ovs_neutron_plugin.ini', 60);
INSERT INTO neutron_default VALUES ('tenant_network_types', 'gre', 'ovs_neutron_plugin.ini', 61);
INSERT INTO neutron_default VALUES ('mechanism_drivers', 'openvswitch', 'ovs_neutron_plugin.ini', 62);
INSERT INTO neutron_default VALUES ('tunnel_id_ranges', '1:1000', 'ovs_neutron_plugin.ini', 63);
INSERT INTO neutron_default VALUES ('enable_security_group', 'True', 'ovs_neutron_plugin.ini', 64);
--INSERT INTO neutron_default VALUES ('firewall_driver', 'neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver', 'ovs_neutron_plugin.ini', 65);
INSERT INTO neutron_default VALUES ('tunnel_types', 'gre', 'ovs_neutron_plugin.ini', 66);
--INSERT INTO neutron_default VALUES ('local_ip', '172.24.24.10', 'ovs_neutron_plugin.ini', 67);

--
-- TOC entry 2173 (class 0 OID 16446)
-- Dependencies: 174
-- Data for Name: neutron_node; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2174 (class 0 OID 16454)
-- Dependencies: 176
-- Data for Name: nova_default; Type: TABLE DATA; Schema: public; Owner: transuser
--
--INSERT INTO nova_default VALUES ('rabbit_host', '172.24.24.10', 'nova.conf', 1);
--INSERT INTO nova_default VALUES ('rabbit_port', '5672', 'nova.conf', 2);
INSERT INTO nova_default VALUES ('rabbit_userid', 'guest', 'nova.conf', 3);
INSERT INTO nova_default VALUES ('rabbit_password', 'transcirrus1', 'nova.conf', 4);
INSERT INTO nova_default VALUES ('internal_service_availability_zone', 'internal', 'nova.conf', 5);
INSERT INTO nova_default VALUES ('default_availability_zone', 'nova', 'nova.conf', 6);
INSERT INTO nova_default VALUES ('use_ipv6', 'False', 'nova.conf', 7);
INSERT INTO nova_default VALUES ('enabled_apis', 'ec2,osapi_compute', 'nova.conf', 8);
--INSERT INTO nova_default VALUES ('logdir', '/var/log/nova', 'nova.conf', 9);
--INSERT INTO nova_default VALUES ('state_path', '/var/lib/nova', 'nova.conf', 10);
INSERT INTO nova_default VALUES ('lock_path', '/var/lock/nova', 'nova.conf', 11);
INSERT INTO nova_default VALUES ('ec2_listen', '0.0.0.0', 'nova.conf', 12);
INSERT INTO nova_default VALUES ('ec2_listen_port', '8773', 'nova.conf', 13);
INSERT INTO nova_default VALUES ('osapi_compute_listen', '0.0.0.0', 'nova.conf', 14);
INSERT INTO nova_default VALUES ('osapi_compute_listen_port', '8774', 'nova.conf', 15);
INSERT INTO nova_default VALUES ('metadata_listen_port', '8775', 'nova.conf', 16);
--INSERT INTO nova_default VALUES ('metadata_listen', '172.24.24.10', 'nova.conf', 17);
INSERT INTO nova_default VALUES ('service_neutron_metadata_proxy', 'True', 'nova.conf', 28);
INSERT INTO nova_default VALUES ('neutron_metadata_proxy_shared_secret', 'transcirrus1', 'nova.conf', 29);
INSERT INTO nova_default VALUES ('allow_instance_snapshots', 'True', 'nova.conf', 30);
INSERT INTO nova_default VALUES ('enable_instance_password', 'true', 'nova.conf', 31);
--INSERT INTO nova_default VALUES ('novncproxy_port', '6080', 'nova.conf', 32);
--INSERT INTO nova_default VALUES ('spicehtml5proxy_port', '6082', 'nova.conf', 33);
INSERT INTO nova_default VALUES ('allow_resize_to_same_host', 'True', 'nova.conf', 34);
INSERT INTO nova_default VALUES ('allow_migrate_to_same_host', 'False', 'nova.conf', 35);
INSERT INTO nova_default VALUES ('default_schedule_zone', 'nova', 'nova.conf', 36);
--INSERT INTO nova_default VALUES ('multi_instance_display_name_template', '%(name)s-%(uuid)s', 'nova.conf', 37);
--INSERT INTO nova_default VALUES ('default_flavor', 'm1.small', 'nova.conf', 38);
--INSERT INTO nova_default VALUES ('linuxnet_interface_driver', 'nova.network.linux_net.LinuxOVSInterfaceDriver', 'nova.conf', 39);
--INSERT INTO nova_default VALUES ('firewall_driver', 'nova.virt.firewall.NoopFirewallDriver', 'nova.conf', 40);
--INSERT INTO nova_default VALUES ('metadata_host', '172.24.24.10', 'nova.conf', 41);
--INSERT INTO nova_default VALUES ('neutron_url', 'http://172.24.24.10:9696', 'nova.conf', 42);
INSERT INTO nova_default VALUES ('neutron_admin_username', 'neutron', 'nova.conf', 43);
INSERT INTO nova_default VALUES ('neutron_admin_password', 'transcirrus1', 'nova.conf', 44);
--INSERT INTO nova_default VALUES ('neutron_admin_tenant_name', 'service', 'nova.conf', 45);
INSERT INTO nova_default VALUES ('neutron_region_name', 'TransCirrusCloud', 'nova.conf', 46);
--INSERT INTO nova_default VALUES ('neutron_admin_auth_url', 'http://172.24.24.10:35357/v2.0', 'nova.conf', 47);
INSERT INTO nova_default VALUES ('neutron_auth_strategy', 'keystone', 'nova.conf', 48);
INSERT INTO nova_default VALUES ('neutron_ovs_bridge', 'br-int', 'nova.conf', 49);
INSERT INTO nova_default VALUES ('security_group_api', 'neutron', 'nova.conf', 50);
INSERT INTO nova_default VALUES ('verbose', 'False', 'nova.conf', 51);
INSERT INTO nova_default VALUES ('debug', 'False', 'nova.conf', 52);
INSERT INTO nova_default VALUES ('cpu_allocation_ratio', '16.0', 'nova.conf', 53);
INSERT INTO nova_default VALUES ('disk_allocation_ratio', '1.0', 'nova.conf', 54);
INSERT INTO nova_default VALUES ('max_instances_per_host', '50', 'nova.conf', 55);
INSERT INTO nova_default VALUES ('ram_allocation_ratio', '1.5', 'nova.conf', 56);
INSERT INTO nova_default VALUES ('scheduler_default_filters', 'AvailabilityZoneFilter,ComputeFilter,DifferentHostFilter', 'nova.conf', 57);
INSERT INTO nova_default VALUES ('compute_driver', 'libvirt.LibvirtDriver', 'nova.conf', 58);
INSERT INTO nova_default VALUES ('vnc_enabled', 'true', 'nova.conf', 59);
INSERT INTO nova_default VALUES ('vnc_keymap', 'en-us', 'nova.conf', 60);
--INSERT INTO nova_default VALUES ('volume_api_class', 'nova.volume.cinder.API', 'nova.conf', 61);
--INSERT INTO nova_default VALUES ('connection', 'postgresql://transuser:transcirrus1@172.24.24.10/nova', 'nova.conf', 62);
--INSERT INTO nova_default VALUES ('auth_host', '172.24.24.10', 'nova.conf', 63);
--INSERT INTO nova_default VALUES ('auth_port', '35357', 'nova.conf', 64);
INSERT INTO nova_default VALUES ('auth_protocol', 'http', 'nova.conf', 65);
--INSERT INTO nova_default VALUES ('auth_uri', '172.24.24.10:5000', 'nova.conf', 66);
INSERT INTO nova_default VALUES ('auth_version', 'v2.0', 'nova.conf', 67);
INSERT INTO nova_default VALUES ('admin_user', 'nova', 'nova.conf', 68);
INSERT INTO nova_default VALUES ('admin_password', 'transcirrus1', 'nova.conf', 69);
--INSERT INTO nova_default VALUES ('admin_tenant_name', 'service', 'nova.conf', 70);
--INSERT INTO nova_default VALUES ('memcached_servers', '172.24.24.10:11211', 'nova.conf', 70);
--INSERT INTO nova_default VALUES ('live_migration_uri', 'qemu+tcp://%s/system', 'nova.conf', 71);
--INSERT INTO nova_default VALUES ('live_migration_flag', 'VIR_MIGRATE_UNDEFINE_SOURCE,VIR_MIGRATE_PEER2PEER,VIR_MIGRATE_LIVE', 'nova.conf', 72);
--INSERT INTO nova_default VALUES ('block_migration_flag', 'VIR_MIGRATE_UNDEFINE_SOURCE,VIR_MIGRATE_PEER2PEER,VIR_MIGRATE_NON_SHARED_INC', 'nova.conf', 73);
INSERT INTO nova_default VALUES ('qemu_allowed_storage_drivers', 'gluster', 'nova.conf', 74);

--
-- TOC entry 215 (class 1259 OID 19290)
-- Name: trans_user_projects; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_user_projects (
    proj_name character varying,
    proj_id character varying,
    user_name character varying,
    user_id character varying,
    index integer NOT NULL
);


ALTER TABLE public.trans_user_projects OWNER TO transuser;

--
-- TOC entry 216 (class 1259 OID 19314)
-- Name: trans_user_projects_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_user_projects_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_user_projects_index_seq OWNER TO transuser;

--
-- TOC entry 2058 (class 0 OID 0)
-- Dependencies: 216
-- Name: trans_user_projects_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_user_projects_index_seq OWNED BY trans_user_projects.index;


--
-- TOC entry 2059 (class 0 OID 0)
-- Dependencies: 216
-- Name: trans_user_projects_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_user_projects_index_seq', 5, true);


--
-- TOC entry 2050 (class 2604 OID 19316)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_user_projects ALTER COLUMN index SET DEFAULT nextval('trans_user_projects_index_seq'::regclass);


--
-- TOC entry 2052 (class 2606 OID 19324)
-- Name: trans_user_projects_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_projects
    ADD CONSTRAINT trans_user_projects_pkey PRIMARY KEY (index);

--
-- TOC entry 2188 (class 0 OID 16567)
-- Dependencies: 203
-- Data for Name: trans_service_settings; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_service_settings VALUES ('ec2_admin           ', 8773, NULL, 'ec2', '/services/Admin', 'OpenStack EC2 service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('ec2                 ', 8773, NULL, 'ec2', '/services/Cloud', 'OpenStack EC2 service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('s3                  ', 3333, NULL, 's3', 'NULL', 'OpenStack S3 service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('keystone            ', 5000, NULL, 'identity', '/v2.0', 'OpenStack Identity', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('keystone_admin      ', 35357, NULL, 'identity', '/v2.0', 'OpenStack Identity', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('nova                ', 8774, NULL, 'compute', '/v2/$(tenant_id)s', 'OpenStack Compute Service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('cinder              ', 8776, NULL, 'volume', '/v1/$(tenant_id)s', 'OpenStack Volume Service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('cinder_v2           ', 8776, NULL, 'volume', '/v2/$(tenant_id)s', 'OpenStack Volume Service V2', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('glance              ', 9292, NULL, 'image', 'NULL', 'OpenStack Image Service', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('swift               ', 8080, NULL, 'object-store', '/v1/AUTH_$(tenant_id)s', 'OpenStack Object Store', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('swift_admin         ', 8080, NULL, 'object-store', '/v1', 'OpenStack Object Store', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('heat                ', 8004, NULL, 'orchestration', '/v1/$(tenant_id)s', 'Orchestration', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('heat_cfn            ', 8000, NULL, 'cloudformation', '/v1', 'Orchestration CloudFormation', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('ceilometer          ', 8777, NULL, 'metering', 'NULL', 'Telemetry', 'NULL', 'NULL', 'NULL', 'NULL');
INSERT INTO trans_service_settings VALUES ('neutron             ', 9696, NULL, 'network', 'NULL', 'OpenStack Networking service', 'NULL', 'NULL', 'NULL', 'NULL');

--
-- TOC entry 2189 (class 0 OID 16573)
-- Dependencies: 204
-- Data for Name: trans_subnets; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 2191 (class 0 OID 16590)
-- Dependencies: 208
-- Data for Name: trans_system_snapshots; Type: TABLE DATA; Schema: public; Owner: transuser
--

CREATE TABLE trans_swift_containers (
    index integer NOT NULL,
    proj_id character varying,
    container_name character varying,
    container_user_id character varying
);


ALTER TABLE public.trans_swift_containers OWNER TO transuser;

--
-- TOC entry 196 (class 1259 OID 26897)
-- Name: trans_swift_containers_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_swift_containers_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_swift_containers_index_seq OWNER TO transuser;

--
-- TOC entry 1951 (class 0 OID 0)
-- Dependencies: 196
-- Name: trans_swift_containers_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_swift_containers_index_seq OWNED BY trans_swift_containers.index;


--
-- TOC entry 1952 (class 0 OID 0)
-- Dependencies: 196
-- Name: trans_swift_containers_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_swift_containers_index_seq', 2, true);


--
-- TOC entry 1943 (class 2604 OID 26902)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_swift_containers ALTER COLUMN index SET DEFAULT nextval('trans_swift_containers_index_seq'::regclass);

--
-- TOC entry 1945 (class 2606 OID 26907)
-- Name: trans_swift_containers_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_swift_containers
    ADD CONSTRAINT trans_swift_containers_pkey PRIMARY KEY (index);

--
-- TOC entry 2192 (class 0 OID 16596)
-- Dependencies: 209
-- Data for Name: trans_system_vols; Type: TABLE DATA; Schema: public; Owner: transuser
--
--
-- TOC entry 215 (class 1259 OID 19290)
-- Name: trans_user_projects; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_user_projects (
    proj_name character varying,
    proj_id character varying,
    user_name character varying,
    user_id character varying,
    index integer NOT NULL
);


ALTER TABLE public.trans_user_projects OWNER TO transuser;

--
-- TOC entry 216 (class 1259 OID 19314)
-- Name: trans_user_projects_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_user_projects_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_user_projects_index_seq OWNER TO transuser;

--
-- TOC entry 2058 (class 0 OID 0)
-- Dependencies: 216
-- Name: trans_user_projects_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_user_projects_index_seq OWNED BY trans_user_projects.index;


--
-- TOC entry 2059 (class 0 OID 0)
-- Dependencies: 216
-- Name: trans_user_projects_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_user_projects_index_seq', 5, true);


--
-- TOC entry 2050 (class 2604 OID 19316)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_user_projects ALTER COLUMN index SET DEFAULT nextval('trans_user_projects_index_seq'::regclass);


--
-- TOC entry 2052 (class 2606 OID 19324)
-- Name: trans_user_projects_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_projects
    ADD CONSTRAINT trans_user_projects_pkey PRIMARY KEY (index);

--
-- TOC entry 198 (class 1259 OID 49346)
-- Name: trans_zones; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--
CREATE TABLE trans_zones (
    index integer NOT NULL,
    zone_name character varying,
    zone_description text
);


ALTER TABLE public.trans_zones OWNER TO transuser;

--
-- TOC entry 197 (class 1259 OID 49344)
-- Name: trans_zones_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_zones_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_zones_index_seq OWNER TO transuser;

--
-- TOC entry 1955 (class 0 OID 0)
-- Dependencies: 197
-- Name: trans_zones_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_zones_index_seq OWNED BY trans_zones.index;


--
-- TOC entry 1956 (class 0 OID 0)
-- Dependencies: 197
-- Name: trans_zones_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_zones_index_seq', 1, false);


--
-- TOC entry 1945 (class 2604 OID 49349)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_zones ALTER COLUMN index SET DEFAULT nextval('trans_zones_index_seq'::regclass);


--
-- TOC entry 1950 (class 0 OID 49346)
-- Dependencies: 198
-- Data for Name: trans_zones; Type: TABLE DATA; Schema: public; Owner: transuser
--

INSERT INTO trans_zones VALUES (0, 'nova', 'The default availability zone');


--
-- TOC entry 1947 (class 2606 OID 49354)
-- Name: trans_zones_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_zones
    ADD CONSTRAINT trans_zones_pkey PRIMARY KEY (index);


--
-- TOC entry 1949 (class 2606 OID 49356)
-- Name: trans_zones_zone_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_zones
    ADD CONSTRAINT trans_zones_zone_name_key UNIQUE (zone_name);


--
-- TOC entry 215 (class 1259 OID 21659)
-- Name: trans_inst_enviro; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_inst_enviro (
    index integer NOT NULL,
    inst_image_id character varying,
    vol_snap_id character varying,
    orig_vol_id character varying,
    orig_inst_id character varying,
    orig_vol_mount_location character varying(20)
);


ALTER TABLE public.trans_inst_enviro OWNER TO transuser;

--
-- TOC entry 214 (class 1259 OID 21657)
-- Name: trans_inst_enviro_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_inst_enviro_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_inst_enviro_index_seq OWNER TO transuser;

--
-- TOC entry 2009 (class 0 OID 0)
-- Dependencies: 214
-- Name: trans_inst_enviro_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_inst_enviro_index_seq OWNED BY trans_inst_enviro.index;


--
-- TOC entry 2010 (class 0 OID 0)
-- Dependencies: 214
-- Name: trans_inst_enviro_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_inst_enviro_index_seq', 1, false);


--
-- TOC entry 213 (class 1259 OID 20987)
-- Name: trans_inst_snaps; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_inst_snaps (
    index integer NOT NULL,
    name character varying,
    type character varying(10),
    inst_id character varying,
    create_date timestamp without time zone,
    snap_id character varying,
    project_id character varying,
    description text
);


ALTER TABLE public.trans_inst_snaps OWNER TO transuser;

--
-- TOC entry 212 (class 1259 OID 20985)
-- Name: trans_inst_snaps_index_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_inst_snaps_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_inst_snaps_index_seq OWNER TO transuser;

--
-- TOC entry 2011 (class 0 OID 0)
-- Dependencies: 212
-- Name: trans_inst_snaps_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_inst_snaps_index_seq OWNED BY trans_inst_snaps.index;


--
-- TOC entry 2012 (class 0 OID 0)
-- Dependencies: 212
-- Name: trans_inst_snaps_index_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_inst_snaps_index_seq', 1, false);


--
-- TOC entry 1998 (class 2604 OID 21662)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_inst_enviro ALTER COLUMN index SET DEFAULT nextval('trans_inst_enviro_index_seq'::regclass);


--
-- TOC entry 1997 (class 2604 OID 20990)
-- Name: index; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_inst_snaps ALTER COLUMN index SET DEFAULT nextval('trans_inst_snaps_index_seq'::regclass);

--
-- TOC entry 2002 (class 2606 OID 21784)
-- Name: trans_inst_enviro_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_inst_enviro
    ADD CONSTRAINT trans_inst_enviro_pkey PRIMARY KEY (index);


--
-- TOC entry 2000 (class 2606 OID 21786)
-- Name: trans_inst_snaps_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_inst_snaps
    ADD CONSTRAINT trans_inst_snaps_pkey PRIMARY KEY (index);


--
-- TOC entry 2095 (class 2606 OID 16636)
-- Name: cinder_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY cinder_default
    ADD CONSTRAINT cinder_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2097 (class 2606 OID 16638)
-- Name: cinder_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY cinder_node
    ADD CONSTRAINT cinder_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2099 (class 2606 OID 16696)
-- Name: factory_defaults_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY factory_defaults
    ADD CONSTRAINT factory_defaults_pkey PRIMARY KEY (index);


--
-- TOC entry 2101 (class 2606 OID 16640)
-- Name: glance_defaults_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY glance_defaults
    ADD CONSTRAINT glance_defaults_pkey PRIMARY KEY (index);


--
-- TOC entry 2120 (class 2606 OID 16642)
-- Name: index; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY psql_buildout
    ADD CONSTRAINT index PRIMARY KEY (index);


--
-- TOC entry 2103 (class 2606 OID 16644)
-- Name: keystone_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY keystone
    ADD CONSTRAINT keystone_key PRIMARY KEY (index);


--
-- TOC entry 2105 (class 2606 OID 16646)
-- Name: network_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY net_adapter_settings
    ADD CONSTRAINT network_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2107 (class 2606 OID 16648)
-- Name: neutron_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY neutron_default
    ADD CONSTRAINT neutron_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2109 (class 2606 OID 16650)
-- Name: neutron_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY neutron_node
    ADD CONSTRAINT neutron_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2111 (class 2606 OID 16652)
-- Name: nova_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY nova_default
    ADD CONSTRAINT nova_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2113 (class 2606 OID 16654)
-- Name: nova_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY nova_node
    ADD CONSTRAINT nova_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2115 (class 2606 OID 16656)
-- Name: projects_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (proj_id);


--
-- TOC entry 2118 (class 2606 OID 16658)
-- Name: projects_proj_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_proj_name_key UNIQUE (proj_name);


--
-- TOC entry 2122 (class 2606 OID 16660)
-- Name: swift_default_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY swift_default
    ADD CONSTRAINT swift_default_pkey PRIMARY KEY (index);


--
-- TOC entry 2124 (class 2606 OID 16662)
-- Name: swift_node_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY swift_node
    ADD CONSTRAINT swift_node_pkey PRIMARY KEY (index);


--
-- TOC entry 2126 (class 2606 OID 16664)
-- Name: system_default_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY system_default_settings
    ADD CONSTRAINT system_default_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2128 (class 2606 OID 16666)
-- Name: trans_floating_ip_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_floating_ip
    ADD CONSTRAINT trans_floating_ip_pkey PRIMARY KEY (index);


--
-- TOC entry 2131 (class 2606 OID 16668)
-- Name: trans_instances_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_instances
    ADD CONSTRAINT trans_instances_pkey PRIMARY KEY (inst_id);


--
-- TOC entry 2134 (class 2606 OID 16670)
-- Name: trans_network_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_network_settings
    ADD CONSTRAINT trans_network_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2137 (class 2606 OID 16672)
-- Name: trans_nodes_node_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_nodes
    ADD CONSTRAINT trans_nodes_node_name_key UNIQUE (node_name);


--
-- TOC entry 2139 (class 2606 OID 16674)
-- Name: trans_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_nodes
    ADD CONSTRAINT trans_nodes_pkey PRIMARY KEY (node_id);


--
-- TOC entry 2141 (class 2606 OID 16676)
-- Name: trans_routers_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_routers
    ADD CONSTRAINT trans_routers_pkey PRIMARY KEY (index);


--
-- TOC entry 2144 (class 2606 OID 16678)
-- Name: trans_security_group_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_security_group
    ADD CONSTRAINT trans_security_group_pkey PRIMARY KEY (index);


--
-- TOC entry 2146 (class 2606 OID 16680)
-- Name: trans_security_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_security_keys
    ADD CONSTRAINT trans_security_keys_pkey PRIMARY KEY (index);


--
-- TOC entry 2149 (class 2606 OID 16682)
-- Name: trans_service_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_service_settings
    ADD CONSTRAINT trans_service_settings_pkey PRIMARY KEY (service_name);


--
-- TOC entry 2151 (class 2606 OID 16684)
-- Name: trans_subnets_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_subnets
    ADD CONSTRAINT trans_subnets_pkey PRIMARY KEY (index);


--
-- TOC entry 2154 (class 2606 OID 16686)
-- Name: trans_system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_system_settings
    ADD CONSTRAINT trans_system_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2156 (class 2606 OID 16688)
-- Name: trans_system_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_system_snapshots
    ADD CONSTRAINT trans_system_snapshots_pkey PRIMARY KEY (snap_id);


--
-- TOC entry 2158 (class 2606 OID 16690)
-- Name: trans_system_vols_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_system_vols
    ADD CONSTRAINT trans_system_vols_pkey PRIMARY KEY (vol_id);


--
-- TOC entry 2160 (class 2606 OID 16692)
-- Name: trans_user_info_keystone_user_uuid_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_keystone_user_uuid_key UNIQUE (keystone_user_uuid);


--
-- TOC entry 2162 (class 2606 OID 16694)
-- Name: trans_user_info_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_pkey PRIMARY KEY (index);


--
-- TOC entry 2165 (class 2606 OID 16698)
-- Name: trans_user_info_user_name_key; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_user_name_key UNIQUE (user_name);


--
-- TOC entry 2116 (class 1259 OID 16699)
-- Name: projects_proj_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX projects_proj_id_idx ON projects USING btree (proj_id);


--
-- TOC entry 2129 (class 1259 OID 16700)
-- Name: trans_instances_inst_name_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_instances_inst_name_idx ON trans_instances USING btree (inst_name);


--
-- TOC entry 2132 (class 1259 OID 16701)
-- Name: trans_network_settings_net_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_network_settings_net_id_idx ON trans_network_settings USING btree (net_id);


--
-- TOC entry 2135 (class 1259 OID 16702)
-- Name: trans_nodes_node_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_nodes_node_id_idx ON trans_nodes USING btree (node_id);


--
-- TOC entry 2142 (class 1259 OID 16703)
-- Name: trans_routers_router_name_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_routers_router_name_idx ON trans_routers USING btree (router_name);


--
-- TOC entry 2147 (class 1259 OID 16704)
-- Name: trans_security_keys_sec_key_name_sec_key_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_security_keys_sec_key_name_sec_key_id_idx ON trans_security_keys USING btree (sec_key_name, sec_key_id);


--
-- TOC entry 2152 (class 1259 OID 16705)
-- Name: trans_subnets_subnet_id_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_subnets_subnet_id_idx ON trans_subnets USING btree (subnet_id);


--
-- TOC entry 2163 (class 1259 OID 16706)
-- Name: trans_user_info_user_name_idx; Type: INDEX; Schema: public; Owner: transuser; Tablespace: 
--

CREATE INDEX trans_user_info_user_name_idx ON trans_user_info USING btree (user_name);


-- add the gluster table 07092014
--
-- TOC entry 205 (class 1259 OID 27591)
-- Name: trans_gluster_vols; Type: TABLE; Schema: public; Owner: transuser; Tablespace: 
--

CREATE TABLE trans_gluster_vols (
    gluster_vol_id integer NOT NULL,
    gluster_vol_name character varying,
    gluster_brick_name character varying,
    gluster_vol_sync_state character varying,
    gluster_vol_state character varying
);


ALTER TABLE public.trans_gluster_vols OWNER TO transuser;

--
-- TOC entry 204 (class 1259 OID 27589)
-- Name: trans_gluster_vols_gluster_vol_id_seq; Type: SEQUENCE; Schema: public; Owner: transuser
--

CREATE SEQUENCE trans_gluster_vols_gluster_vol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_gluster_vols_gluster_vol_id_seq OWNER TO transuser;

--
-- TOC entry 1975 (class 0 OID 0)
-- Dependencies: 204
-- Name: trans_gluster_vols_gluster_vol_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: transuser
--

ALTER SEQUENCE trans_gluster_vols_gluster_vol_id_seq OWNED BY trans_gluster_vols.gluster_vol_id;


--
-- TOC entry 1976 (class 0 OID 0)
-- Dependencies: 204
-- Name: trans_gluster_vols_gluster_vol_id_seq; Type: SEQUENCE SET; Schema: public; Owner: transuser
--

SELECT pg_catalog.setval('trans_gluster_vols_gluster_vol_id_seq', 1, false);


--
-- TOC entry 1967 (class 2604 OID 27594)
-- Name: gluster_vol_id; Type: DEFAULT; Schema: public; Owner: transuser
--

ALTER TABLE ONLY trans_gluster_vols ALTER COLUMN gluster_vol_id SET DEFAULT nextval('trans_gluster_vols_gluster_vol_id_seq'::regclass);


--
-- TOC entry 1970 (class 0 OID 27591)
-- Dependencies: 205
-- Data for Name: trans_gluster_vols; Type: TABLE DATA; Schema: public; Owner: transuser
--



--
-- TOC entry 1969 (class 2606 OID 27599)
-- Name: trans_gluster_vols_pkey; Type: CONSTRAINT; Schema: public; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY trans_gluster_vols
    ADD CONSTRAINT trans_gluster_vols_pkey PRIMARY KEY (gluster_vol_id);


--
-- TOC entry 2200 (class 0 OID 0)
-- Dependencies: 6
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2013-12-04 20:49:51 EST

--
-- PostgreSQL database dump complete
--

