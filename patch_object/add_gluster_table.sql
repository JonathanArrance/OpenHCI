--
-- PostgreSQL database dump
--

-- Dumped from database version 8.4.18
-- Dumped by pg_dump version 9.2.0
-- Started on 2014-07-07 23:43:46 EDT

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

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


-- Completed on 2014-07-07 23:43:48 EDT

--
-- PostgreSQL database dump complete
--
