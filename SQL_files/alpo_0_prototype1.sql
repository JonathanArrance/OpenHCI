--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.9
-- Dumped by pg_dump version 9.2.0
-- Started on 2013-07-17 19:56:23 EDT

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
-- TOC entry 170 (class 1259 OID 18543)
-- Name: instances; Type: TABLE; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE TABLE instances (
    inst_name character varying NOT NULL,
    inst_int_ip character varying NOT NULL,
    inst_floating_ip character varying,
    inst_proj_id character varying NOT NULL,
    in_use integer,
    cidr character varying,
    ext_cidr character varying,
    inst_public_ip character varying,
    floating_ip_id character varying,
    inst_id character varying,
    inst_port_id character varying
);


ALTER TABLE public.instances OWNER TO cacsystem;

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
    internal_net_id character varying,
    internal_net_name character varying,
    router_id character varying,
    router_name character varying,
    internal_subnet_name character varying,
    internal_subnet_id character varying,
    security_key_name character varying,
    security_key_id character varying,
    security_group_id character varying,
    security_group_name character varying,
    host_system_name character varying,
    host_system_ip character varying
);


ALTER TABLE public.projects OWNER TO cacsystem;

--
-- TOC entry 1956 (class 0 OID 0)
-- Dependencies: 172
-- Name: COLUMN projects.host_system_name; Type: COMMENT; Schema: public; Owner: cacsystem
--

COMMENT ON COLUMN projects.host_system_name IS 'Name of the cloud controller';


--
-- TOC entry 1957 (class 0 OID 0)
-- Dependencies: 172
-- Name: COLUMN projects.host_system_ip; Type: COMMENT; Schema: public; Owner: cacsystem
--

COMMENT ON COLUMN projects.host_system_ip IS 'API ip associated with the ';


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
    keystone_role character varying
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
-- TOC entry 1958 (class 0 OID 0)
-- Dependencies: 175
-- Name: trans_user_info_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cacsystem
--

ALTER SEQUENCE trans_user_info_index_seq OWNED BY trans_user_info.index;


--
-- TOC entry 1911 (class 2604 OID 19846)
-- Name: index; Type: DEFAULT; Schema: public; Owner: cacsystem
--

ALTER TABLE ONLY trans_user_info ALTER COLUMN index SET DEFAULT nextval('trans_user_info_index_seq'::regclass);


--
-- TOC entry 1922 (class 2606 OID 18489)
-- Name: cinder_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY cinder
    ADD CONSTRAINT cinder_key PRIMARY KEY (index);


--
-- TOC entry 1924 (class 2606 OID 18505)
-- Name: glance_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY glance
    ADD CONSTRAINT glance_key PRIMARY KEY (index);


--
-- TOC entry 1918 (class 2606 OID 16438)
-- Name: index; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY psql_buildout
    ADD CONSTRAINT index PRIMARY KEY (index);


--
-- TOC entry 1920 (class 2606 OID 18480)
-- Name: index_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY quantum
    ADD CONSTRAINT index_key PRIMARY KEY (index);


--
-- TOC entry 1933 (class 2606 OID 18550)
-- Name: instances_inst_ext_ip_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY instances
    ADD CONSTRAINT instances_inst_ext_ip_key UNIQUE (inst_floating_ip);


--
-- TOC entry 1935 (class 2606 OID 18552)
-- Name: instances_inst_int_ip_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY instances
    ADD CONSTRAINT instances_inst_int_ip_key UNIQUE (inst_int_ip);


--
-- TOC entry 1937 (class 2606 OID 18554)
-- Name: instances_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY instances
    ADD CONSTRAINT instances_pkey PRIMARY KEY (inst_name);


--
-- TOC entry 1916 (class 2606 OID 18520)
-- Name: keystone_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY keystone
    ADD CONSTRAINT keystone_key PRIMARY KEY (index);


--
-- TOC entry 1928 (class 2606 OID 18515)
-- Name: nova_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY nova
    ADD CONSTRAINT nova_key PRIMARY KEY (index);


--
-- TOC entry 1939 (class 2606 OID 19809)
-- Name: projects_internal_net_id_internal_net_name_router_id_router_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_internal_net_id_internal_net_name_router_id_router_key UNIQUE (internal_net_id, internal_net_name, router_id, router_name, internal_subnet_name, internal_subnet_id, security_key_name, security_key_id, security_group_id, security_group_name);


--
-- TOC entry 1941 (class 2606 OID 19805)
-- Name: projects_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (proj_id);


--
-- TOC entry 1943 (class 2606 OID 19807)
-- Name: projects_proj_name_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_proj_name_key UNIQUE (proj_name);


--
-- TOC entry 1926 (class 2606 OID 18513)
-- Name: swift_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY swift
    ADD CONSTRAINT swift_key PRIMARY KEY (index);


--
-- TOC entry 1930 (class 2606 OID 18528)
-- Name: sys_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_system_settings
    ADD CONSTRAINT sys_key PRIMARY KEY (index);


--
-- TOC entry 1951 (class 2606 OID 19882)
-- Name: trans_system_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_system_snapshots
    ADD CONSTRAINT trans_system_snapshots_pkey PRIMARY KEY (snap_id);


--
-- TOC entry 1949 (class 2606 OID 19874)
-- Name: trans_system_vols_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_system_vols
    ADD CONSTRAINT trans_system_vols_pkey PRIMARY KEY (vol_id);


--
-- TOC entry 1945 (class 2606 OID 19848)
-- Name: trans_user_info_keystone_user_uuid_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_keystone_user_uuid_key UNIQUE (keystone_user_uuid);


--
-- TOC entry 1947 (class 2606 OID 19850)
-- Name: trans_user_info_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT trans_user_info_pkey PRIMARY KEY (index);


--
-- TOC entry 1931 (class 1259 OID 19814)
-- Name: trans_system_settings_index_idx; Type: INDEX; Schema: public; Owner: cacsystem; Tablespace: 
--

CREATE INDEX trans_system_settings_index_idx ON trans_system_settings USING btree (index);


-- Completed on 2013-07-17 19:56:27 EDT

--
-- PostgreSQL database dump complete
--

