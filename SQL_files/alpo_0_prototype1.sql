--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.9
-- Dumped by pg_dump version 9.2.0
-- Started on 2013-09-14 15:24:52 EDT

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 165 (class 1259 OID 18481)
-- Name: cinder; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE TABLE cinder (
    index character varying NOT NULL,
    parameter character varying,
    param_value character varying,
    host_name character varying,
    file_path character varying
);


ALTER TABLE public.cinder OWNER TO cacsystem;

--
-- TOC entry 166 (class 1259 OID 18490)
-- Name: glance; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE TABLE glance (
    parameter character varying,
    param_value character varying,
    host_name character varying,
    file_path character varying,
    index character varying NOT NULL
);


ALTER TABLE public.glance OWNER TO cacsystem;

--
-- TOC entry 161 (class 1259 OID 16411)
-- Name: keystone; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE TABLE keystone (
    index integer NOT NULL,
    paramter character varying,
    param_value character varying,
    host_system character varying,
    file_path character varying
);


ALTER TABLE public.keystone OWNER TO cacsystem;

--
-- TOC entry 168 (class 1259 OID 18506)
-- Name: nova; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE TABLE nova (
    index integer NOT NULL,
    parameter character varying,
    host_name character varying,
    file_path character varying,
    param_value character varying
);


ALTER TABLE public.nova OWNER TO cacsystem;

--
-- TOC entry 172 (class 1259 OID 19798)
-- Name: projects; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
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


ALTER TABLE public.projects OWNER TO cacsystem;

--
-- TOC entry 2026 (class 0 OID 0)
-- Dependencies: 172
-- Name: COLUMN projects.def_security_key_name; Type: COMMENT; Schema: public; Owner: cacsystem
--

COMMENT ON COLUMN projects.def_security_key_name IS 'Default security key made during project creation';


--
-- TOC entry 2027 (class 0 OID 0)
-- Dependencies: 172
-- Name: COLUMN projects.def_security_key_id; Type: COMMENT; Schema: public; Owner: cacsystem
--

COMMENT ON COLUMN projects.def_security_key_id IS 'default security key id made at project creation';


--
-- TOC entry 2028 (class 0 OID 0)
-- Dependencies: 172
-- Name: COLUMN projects.host_system_name; Type: COMMENT; Schema: public; Owner: cacsystem
--

COMMENT ON COLUMN projects.host_system_name IS 'Name of the cloud controller';


--
-- TOC entry 2029 (class 0 OID 0)
-- Dependencies: 172
-- Name: COLUMN projects.host_system_ip; Type: COMMENT; Schema: public; Owner: cacsystem
--

COMMENT ON COLUMN projects.host_system_ip IS 'API ip associated with the cloud controller';


--
-- TOC entry 162 (class 1259 OID 16430)
-- Name: psql_buildout; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE TABLE psql_buildout (
    index bigint DEFAULT 0 NOT NULL,
    component character(1),
    command character varying
);


ALTER TABLE public.psql_buildout OWNER TO cacsystem;

--
-- TOC entry 164 (class 1259 OID 18473)
-- Name: quantum; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE TABLE quantum (
    index integer NOT NULL,
    parameter character varying,
    param_value character varying,
    host_name character varying,
    file_path character varying
);


ALTER TABLE public.quantum OWNER TO cacsystem;

--
-- TOC entry 167 (class 1259 OID 18498)
-- Name: swift; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE TABLE swift (
    index integer NOT NULL,
    paramter character varying,
    param_value character varying,
    host_name character varying,
    file_path character varying
);


ALTER TABLE public.swift OWNER TO cacsystem;

--
-- TOC entry 192 (class 1259 OID 20008)
-- Name: trans_floating_ip; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE TABLE trans_floating_ip (
    index integer NOT NULL,
    floating_ip character varying,
    floating_ip_id character varying,
    proj_id character varying,
    router_id character varying,
    fixed_ip character varying
);


ALTER TABLE public.trans_floating_ip OWNER TO cacsystem;

--
-- TOC entry 191 (class 1259 OID 20006)
-- Name: trans_floating_ip_index_seq; Type: SEQUENCE; Schema: public; Owner: cacsystem
--

CREATE SEQUENCE trans_floating_ip_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_floating_ip_index_seq OWNER TO cacsystem;

--
-- TOC entry 2030 (class 0 OID 0)
-- Dependencies: 191
-- Name: trans_floating_ip_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cacsystem
--

ALTER SEQUENCE trans_floating_ip_index_seq OWNED BY trans_floating_ip.index;


--
-- TOC entry 170 (class 1259 OID 18543)
-- Name: trans_instances; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
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


ALTER TABLE public.trans_instances OWNER TO cacsystem;

--
-- TOC entry 186 (class 1259 OID 19968)
-- Name: trans_network_settings; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
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


ALTER TABLE public.trans_network_settings OWNER TO cacsystem;

--
-- TOC entry 2031 (class 0 OID 0)
-- Dependencies: 186
-- Name: COLUMN trans_network_settings.net_internal; Type: COMMENT; Schema: public; Owner: cacsystem
--

COMMENT ON COLUMN trans_network_settings.net_internal IS '1=true';


--
-- TOC entry 2032 (class 0 OID 0)
-- Dependencies: 186
-- Name: COLUMN trans_network_settings.net_shared; Type: COMMENT; Schema: public; Owner: cacsystem
--

COMMENT ON COLUMN trans_network_settings.net_shared IS '1=true';


--
-- TOC entry 185 (class 1259 OID 19966)
-- Name: trans_network_settings_index_seq; Type: SEQUENCE; Schema: public; Owner: cacsystem
--

CREATE SEQUENCE trans_network_settings_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_network_settings_index_seq OWNER TO cacsystem;

--
-- TOC entry 2033 (class 0 OID 0)
-- Dependencies: 185
-- Name: trans_network_settings_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cacsystem
--

ALTER SEQUENCE trans_network_settings_index_seq OWNED BY trans_network_settings.index;


--
-- TOC entry 190 (class 1259 OID 19993)
-- Name: trans_routers; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
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


ALTER TABLE public.trans_routers OWNER TO cacsystem;

--
-- TOC entry 2034 (class 0 OID 0)
-- Dependencies: 190
-- Name: COLUMN trans_routers.router_status; Type: COMMENT; Schema: public; Owner: cacsystem
--

COMMENT ON COLUMN trans_routers.router_status IS 'Active=1';


--
-- TOC entry 2035 (class 0 OID 0)
-- Dependencies: 190
-- Name: COLUMN trans_routers.router_admin_state; Type: COMMENT; Schema: public; Owner: cacsystem
--

COMMENT ON COLUMN trans_routers.router_admin_state IS 'true=1';


--
-- TOC entry 189 (class 1259 OID 19991)
-- Name: trans_routers_index_seq; Type: SEQUENCE; Schema: public; Owner: cacsystem
--

CREATE SEQUENCE trans_routers_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_routers_index_seq OWNER TO cacsystem;

--
-- TOC entry 2036 (class 0 OID 0)
-- Dependencies: 189
-- Name: trans_routers_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cacsystem
--

ALTER SEQUENCE trans_routers_index_seq OWNED BY trans_routers.index;


--
-- TOC entry 179 (class 1259 OID 19916)
-- Name: trans_security_group; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE TABLE trans_security_group (
    index integer NOT NULL,
    proj_id character varying,
    user_name character varying,
    sec_group_id character varying,
    sec_group_name character varying
);


ALTER TABLE public.trans_security_group OWNER TO cacsystem;

--
-- TOC entry 184 (class 1259 OID 19949)
-- Name: trans_security_group_index_seq1; Type: SEQUENCE; Schema: public; Owner: cacsystem
--

CREATE SEQUENCE trans_security_group_index_seq1
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_security_group_index_seq1 OWNER TO cacsystem;

--
-- TOC entry 2037 (class 0 OID 0)
-- Dependencies: 184
-- Name: trans_security_group_index_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: cacsystem
--

ALTER SEQUENCE trans_security_group_index_seq1 OWNED BY trans_security_group.index;


--
-- TOC entry 178 (class 1259 OID 19908)
-- Name: trans_security_keys; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
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


ALTER TABLE public.trans_security_keys OWNER TO cacsystem;

--
-- TOC entry 2038 (class 0 OID 0)
-- Dependencies: 178
-- Name: COLUMN trans_security_keys.public_key; Type: COMMENT; Schema: public; Owner: cacsystem
--

COMMENT ON COLUMN trans_security_keys.public_key IS 'public key';


--
-- TOC entry 183 (class 1259 OID 19939)
-- Name: trans_security_keys_index_seq1; Type: SEQUENCE; Schema: public; Owner: cacsystem
--

CREATE SEQUENCE trans_security_keys_index_seq1
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_security_keys_index_seq1 OWNER TO cacsystem;

--
-- TOC entry 2039 (class 0 OID 0)
-- Dependencies: 183
-- Name: trans_security_keys_index_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: cacsystem
--

ALTER SEQUENCE trans_security_keys_index_seq1 OWNED BY trans_security_keys.index;


--
-- TOC entry 193 (class 1259 OID 20042)
-- Name: trans_service_settings; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
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


ALTER TABLE public.trans_service_settings OWNER TO cacsystem;

--
-- TOC entry 2040 (class 0 OID 0)
-- Dependencies: 193
-- Name: TABLE trans_service_settings; Type: COMMENT; Schema: public; Owner: cacsystem
--

COMMENT ON TABLE trans_service_settings IS 'ensure that when the install is done all values except service_ip and service_id are filled in';


--
-- TOC entry 188 (class 1259 OID 19980)
-- Name: trans_subnets; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
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


ALTER TABLE public.trans_subnets OWNER TO cacsystem;

--
-- TOC entry 187 (class 1259 OID 19978)
-- Name: trans_subnets_index_seq; Type: SEQUENCE; Schema: public; Owner: cacsystem
--

CREATE SEQUENCE trans_subnets_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_subnets_index_seq OWNER TO cacsystem;

--
-- TOC entry 2041 (class 0 OID 0)
-- Dependencies: 187
-- Name: trans_subnets_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cacsystem
--

ALTER SEQUENCE trans_subnets_index_seq OWNED BY trans_subnets.index;


--
-- TOC entry 169 (class 1259 OID 18521)
-- Name: trans_system_settings; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE TABLE trans_system_settings (
    index integer NOT NULL,
    parameter character varying,
    param_value character varying,
    host_system character varying
);


ALTER TABLE public.trans_system_settings OWNER TO cacsystem;

--
-- TOC entry 177 (class 1259 OID 19875)
-- Name: trans_system_snapshots; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE TABLE trans_system_snapshots (
    snap_id character varying NOT NULL,
    vol_id character varying,
    proj_id character varying,
    snap_name character varying,
    snap_desc character varying
);


ALTER TABLE public.trans_system_snapshots OWNER TO cacsystem;

--
-- TOC entry 176 (class 1259 OID 19852)
-- Name: trans_system_vols; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
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


ALTER TABLE public.trans_system_vols OWNER TO cacsystem;

--
-- TOC entry 174 (class 1259 OID 19838)
-- Name: trans_user_info; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
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


ALTER TABLE public.trans_user_info OWNER TO cacsystem;

--
-- TOC entry 175 (class 1259 OID 19844)
-- Name: trans_user_info_index_seq; Type: SEQUENCE; Schema: public; Owner: cacsystem
--

CREATE SEQUENCE trans_user_info_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trans_user_info_index_seq OWNER TO cacsystem;

--
-- TOC entry 2042 (class 0 OID 0)
-- Dependencies: 175
-- Name: trans_user_info_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cacsystem
--

ALTER SEQUENCE trans_user_info_index_seq OWNED BY trans_user_info.index;


--
-- TOC entry 1969 (class 2604 OID 20011)
-- Name: index; Type: DEFAULT; Schema: public; Owner: cacsystem
--

ALTER TABLE ONLY trans_floating_ip ALTER COLUMN index SET DEFAULT nextval('trans_floating_ip_index_seq'::regclass);


--
-- TOC entry 1963 (class 2604 OID 19971)
-- Name: index; Type: DEFAULT; Schema: public; Owner: cacsystem
--

ALTER TABLE ONLY trans_network_settings ALTER COLUMN index SET DEFAULT nextval('trans_network_settings_index_seq'::regclass);


--
-- TOC entry 1966 (class 2604 OID 19996)
-- Name: index; Type: DEFAULT; Schema: public; Owner: cacsystem
--

ALTER TABLE ONLY trans_routers ALTER COLUMN index SET DEFAULT nextval('trans_routers_index_seq'::regclass);


--
-- TOC entry 1962 (class 2604 OID 19951)
-- Name: index; Type: DEFAULT; Schema: public; Owner: cacsystem
--

ALTER TABLE ONLY trans_security_group ALTER COLUMN index SET DEFAULT nextval('trans_security_group_index_seq1'::regclass);


--
-- TOC entry 1961 (class 2604 OID 19941)
-- Name: index; Type: DEFAULT; Schema: public; Owner: cacsystem
--

ALTER TABLE ONLY trans_security_keys ALTER COLUMN index SET DEFAULT nextval('trans_security_keys_index_seq1'::regclass);


--
-- TOC entry 1964 (class 2604 OID 19983)
-- Name: index; Type: DEFAULT; Schema: public; Owner: cacsystem
--

ALTER TABLE ONLY trans_subnets ALTER COLUMN index SET DEFAULT nextval('trans_subnets_index_seq'::regclass);


--
-- TOC entry 1957 (class 2604 OID 19846)
-- Name: index; Type: DEFAULT; Schema: public; Owner: cacsystem
--

ALTER TABLE ONLY trans_user_info ALTER COLUMN index SET DEFAULT nextval('trans_user_info_index_seq'::regclass);


--
-- TOC entry 1977 (class 2606 OID 18489)
-- Name: cinder_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY cinder
    ADD CONSTRAINT cinder_key PRIMARY KEY (index);


--
-- TOC entry 1979 (class 2606 OID 18505)
-- Name: glance_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY glance
    ADD CONSTRAINT glance_key PRIMARY KEY (index);


--
-- TOC entry 1973 (class 2606 OID 16438)
-- Name: index; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY psql_buildout
    ADD CONSTRAINT index PRIMARY KEY (index);


--
-- TOC entry 1975 (class 2606 OID 18480)
-- Name: index_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY quantum
    ADD CONSTRAINT index_key PRIMARY KEY (index);


--
-- TOC entry 1971 (class 2606 OID 18520)
-- Name: keystone_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY keystone
    ADD CONSTRAINT keystone_key PRIMARY KEY (index);


--
-- TOC entry 1983 (class 2606 OID 18515)
-- Name: nova_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY nova
    ADD CONSTRAINT nova_key PRIMARY KEY (index);


--
-- TOC entry 1991 (class 2606 OID 19805)
-- Name: projects_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (proj_id);


--
-- TOC entry 1994 (class 2606 OID 19807)
-- Name: projects_proj_name_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_proj_name_key UNIQUE (proj_name);


--
-- TOC entry 1981 (class 2606 OID 18513)
-- Name: swift_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY swift
    ADD CONSTRAINT swift_key PRIMARY KEY (index);


--
-- TOC entry 1985 (class 2606 OID 18528)
-- Name: sys_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_system_settings
    ADD CONSTRAINT sys_key PRIMARY KEY (index);


--
-- TOC entry 1989 (class 2606 OID 20038)
-- Name: trans_instances_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_instances
    ADD CONSTRAINT trans_instances_pkey PRIMARY KEY (inst_id);


--
-- TOC entry 2012 (class 2606 OID 19976)
-- Name: trans_network_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_network_settings
    ADD CONSTRAINT trans_network_settings_pkey PRIMARY KEY (index);


--
-- TOC entry 2018 (class 2606 OID 20003)
-- Name: trans_routers_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_routers
    ADD CONSTRAINT trans_routers_pkey PRIMARY KEY (index);


--
-- TOC entry 2010 (class 2606 OID 19961)
-- Name: trans_security_group_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_security_group
    ADD CONSTRAINT trans_security_group_pkey PRIMARY KEY (index);


--
-- TOC entry 2007 (class 2606 OID 19959)
-- Name: trans_security_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_security_keys
    ADD CONSTRAINT trans_security_keys_pkey PRIMARY KEY (index);


--
-- TOC entry 2021 (class 2606 OID 20051)
-- Name: trans_service_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_service_settings
    ADD CONSTRAINT trans_service_settings_pkey PRIMARY KEY (service_name);


--
-- TOC entry 2015 (class 2606 OID 19988)
-- Name: trans_subnets_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_subnets
    ADD CONSTRAINT trans_subnets_pkey PRIMARY KEY (index);


--
-- TOC entry 2005 (class 2606 OID 19882)
-- Name: trans_system_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_system_snapshots
    ADD CONSTRAINT trans_system_snapshots_pkey PRIMARY KEY (snap_id);


--
-- TOC entry 2003 (class 2606 OID 19874)
-- Name: trans_system_vols_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_system_vols
    ADD CONSTRAINT trans_system_vols_pkey PRIMARY KEY (vol_id);


--
-- TOC entry 1996 (class 2606 OID 19848)
-- Name: trans_user_info_keystone_user_uuid_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_keystone_user_uuid_key UNIQUE (keystone_user_uuid);


--
-- TOC entry 1998 (class 2606 OID 19850)
-- Name: trans_user_info_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_pkey PRIMARY KEY (index);


--
-- TOC entry 2001 (class 2606 OID 19928)
-- Name: trans_user_info_user_name_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_user_name_key UNIQUE (user_name);


--
-- TOC entry 1992 (class 1259 OID 19926)
-- Name: projects_proj_id_idx; Type: INDEX; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE INDEX projects_proj_id_idx ON projects USING btree (proj_id);


--
-- TOC entry 1987 (class 1259 OID 20039)
-- Name: trans_instances_inst_name_idx; Type: INDEX; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE INDEX trans_instances_inst_name_idx ON trans_instances USING btree (inst_name);


--
-- TOC entry 2013 (class 1259 OID 19977)
-- Name: trans_network_settings_proj_id_idx; Type: INDEX; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE INDEX trans_network_settings_proj_id_idx ON trans_network_settings USING btree (proj_id);


--
-- TOC entry 2019 (class 1259 OID 20004)
-- Name: trans_routers_router_name_idx; Type: INDEX; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE INDEX trans_routers_router_name_idx ON trans_routers USING btree (router_name);


--
-- TOC entry 2008 (class 1259 OID 19925)
-- Name: trans_security_keys_sec_key_name_sec_key_id_idx; Type: INDEX; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE INDEX trans_security_keys_sec_key_name_sec_key_id_idx ON trans_security_keys USING btree (sec_key_name, sec_key_id);


--
-- TOC entry 2016 (class 1259 OID 19989)
-- Name: trans_subnets_subnet_id_idx; Type: INDEX; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE INDEX trans_subnets_subnet_id_idx ON trans_subnets USING btree (subnet_id);


--
-- TOC entry 1986 (class 1259 OID 19814)
-- Name: trans_system_settings_index_idx; Type: INDEX; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE INDEX trans_system_settings_index_idx ON trans_system_settings USING btree (index);


--
-- TOC entry 1999 (class 1259 OID 19929)
-- Name: trans_user_info_user_name_idx; Type: INDEX; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE INDEX trans_user_info_user_name_idx ON trans_user_info USING btree (user_name);


-- Completed on 2013-09-14 15:24:58 EDT

--
-- PostgreSQL database dump complete
--

