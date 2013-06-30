--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.9
-- Dumped by pg_dump version 9.2.0
-- Started on 2013-06-30 16:44:45 EDT

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
-- TOC entry 171 (class 1259 OID 18543)
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
-- TOC entry 173 (class 1259 OID 19798)
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
-- TOC entry 170 (class 1259 OID 18532)
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
-- TOC entry 1928 (class 0 OID 18481)
-- Dependencies: 165
-- Data for Name: cinder; Type: TABLE DATA; Schema: public; Owner: cacsystem
--

COPY cinder (index, parameter, param_value, host_name, file_path) FROM stdin;
\.


--
-- TOC entry 1929 (class 0 OID 18490)
-- Dependencies: 166
-- Data for Name: glance; Type: TABLE DATA; Schema: public; Owner: cacsystem
--

COPY glance (parameter, param_value, host_name, file_path, index) FROM stdin;
\.


--
-- TOC entry 1934 (class 0 OID 18543)
-- Dependencies: 171
-- Data for Name: instances; Type: TABLE DATA; Schema: public; Owner: cacsystem
--

COPY instances (inst_name, inst_int_ip, inst_floating_ip, inst_proj_id, in_use, cidr, ext_cidr, inst_public_ip, floating_ip_id, inst_id, inst_port_id) FROM stdin;
\.


--
-- TOC entry 1925 (class 0 OID 16411)
-- Dependencies: 161
-- Data for Name: keystone; Type: TABLE DATA; Schema: public; Owner: cacsystem
--

COPY keystone (index, paramter, param_value, host_system, file_path) FROM stdin;
\.


--
-- TOC entry 1931 (class 0 OID 18506)
-- Dependencies: 168
-- Data for Name: nova; Type: TABLE DATA; Schema: public; Owner: cacsystem
--

COPY nova (index, parameter, host_name, file_path, param_value) FROM stdin;
\.


--
-- TOC entry 1935 (class 0 OID 19798)
-- Dependencies: 173
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: cacsystem
--

COPY projects (proj_id, proj_name, internal_net_id, internal_net_name, router_id, router_name, internal_subnet_name, internal_subnet_id, security_key_name, security_key_id, security_group_id, security_group_name, host_system_name, host_system_ip) FROM stdin;
151b7bf79c204ddea25620e0fc1668dd	test_project	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	jon-devstack	192.168.10.30
\.


--
-- TOC entry 1926 (class 0 OID 16430)
-- Dependencies: 162
-- Data for Name: psql_buildout; Type: TABLE DATA; Schema: public; Owner: cacsystem
--

COPY psql_buildout (index, component, command) FROM stdin;
\.


--
-- TOC entry 1927 (class 0 OID 18473)
-- Dependencies: 164
-- Data for Name: quantum; Type: TABLE DATA; Schema: public; Owner: cacsystem
--

COPY quantum (index, parameter, param_value, host_name, file_path) FROM stdin;
\.


--
-- TOC entry 1930 (class 0 OID 18498)
-- Dependencies: 167
-- Data for Name: swift; Type: TABLE DATA; Schema: public; Owner: cacsystem
--

COPY swift (index, paramter, param_value, host_name, file_path) FROM stdin;
\.


--
-- TOC entry 1932 (class 0 OID 18521)
-- Dependencies: 169
-- Data for Name: trans_system_settings; Type: TABLE DATA; Schema: public; Owner: cacsystem
--

COPY trans_system_settings (index, parameter, param_value, host_system) FROM stdin;
1	ext_net_id	\N	jon-devstack
2	default_hosted_os	\N	jon-devstack
5	admin_token	cheapass	jon-devstack
6	default_member_id	\N	jon-devstack
7	default_admin_id	\N	jon-devstack
3	mgmt_ip	192.168.10.30	jon-devstack
4	default_hosted_flav	84	jon-devstack
8	api_ip	192.168.10.30	jon-devstack
\.


--
-- TOC entry 1933 (class 0 OID 18532)
-- Dependencies: 170
-- Data for Name: trans_user_info; Type: TABLE DATA; Schema: public; Owner: cacsystem
--

COPY trans_user_info (index, user_name, user_group_membership, user_group_id, user_enabled, keystone_user_uuid, user_primary_project, user_project_id, keystone_role) FROM stdin;
1	jon	admin	0	TRUE	343334-44efffr	\N	\N	\N
2	keven	pu	1	TRUE	567thgrt56y56	\N	\N	\N
3	rob	user	2	TRUE	020fklmskf	\N	\N	\N
4	testuser	pu	1	TRUE	06db0ed7e7f64747988d58d9f6723edc	test_project	151b7bf79c204ddea25620e0fc1668dd	Member
5	testuser2	admin	0	TRUE	1b195ff2e2f44332b9c89480ca9906d9	test_project	151b7bf79c204ddea25620e0fc1668dd	admin
\.


--
-- TOC entry 1906 (class 2606 OID 18489)
-- Name: cinder_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY cinder
    ADD CONSTRAINT cinder_key PRIMARY KEY (index);


--
-- TOC entry 1908 (class 2606 OID 18505)
-- Name: glance_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY glance
    ADD CONSTRAINT glance_key PRIMARY KEY (index);


--
-- TOC entry 1902 (class 2606 OID 16438)
-- Name: index; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY psql_buildout
    ADD CONSTRAINT index PRIMARY KEY (index);


--
-- TOC entry 1904 (class 2606 OID 18480)
-- Name: index_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY quantum
    ADD CONSTRAINT index_key PRIMARY KEY (index);


--
-- TOC entry 1918 (class 2606 OID 18550)
-- Name: instances_inst_ext_ip_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY instances
    ADD CONSTRAINT instances_inst_ext_ip_key UNIQUE (inst_floating_ip);


--
-- TOC entry 1920 (class 2606 OID 18552)
-- Name: instances_inst_int_ip_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY instances
    ADD CONSTRAINT instances_inst_int_ip_key UNIQUE (inst_int_ip);


--
-- TOC entry 1922 (class 2606 OID 18554)
-- Name: instances_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY instances
    ADD CONSTRAINT instances_pkey PRIMARY KEY (inst_name);


--
-- TOC entry 1900 (class 2606 OID 18520)
-- Name: keystone_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY keystone
    ADD CONSTRAINT keystone_key PRIMARY KEY (index);


--
-- TOC entry 1912 (class 2606 OID 18515)
-- Name: nova_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY nova
    ADD CONSTRAINT nova_key PRIMARY KEY (index);


--
-- TOC entry 1924 (class 2606 OID 19805)
-- Name: projects_pkey; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (proj_id);


--
-- TOC entry 1910 (class 2606 OID 18513)
-- Name: swift_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY swift
    ADD CONSTRAINT swift_key PRIMARY KEY (index);


--
-- TOC entry 1914 (class 2606 OID 18528)
-- Name: sys_key; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_system_settings
    ADD CONSTRAINT sys_key PRIMARY KEY (index);


--
-- TOC entry 1916 (class 2606 OID 18539)
-- Name: user_index; Type: CONSTRAINT; Schema: public; Owner: cacsystem; Tablespace: 
--

ALTER TABLE ONLY trans_user_info
    ADD CONSTRAINT user_index PRIMARY KEY (index);


-- Completed on 2013-06-30 16:44:49 EDT

--
-- PostgreSQL database dump complete
--