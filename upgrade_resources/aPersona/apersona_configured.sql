--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

CREATE DATABASE apersona WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';


ALTER DATABASE apersona OWNER TO transuser;

\connect apersona

--
-- Name: apersona; Type: SCHEMA; Schema: -; Owner: transuser
--

CREATE SCHEMA apersona;


ALTER SCHEMA apersona OWNER TO transuser;

SET search_path = apersona, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: alert_types; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE alert_types (
    alert_type_id integer NOT NULL,
    alert_type character varying(50) NOT NULL
);


ALTER TABLE apersona.alert_types OWNER TO transuser;

--
-- Name: alert_types_alert_type_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE alert_types_alert_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.alert_types_alert_type_id_seq OWNER TO transuser;

--
-- Name: alert_types_alert_type_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE alert_types_alert_type_id_seq OWNED BY alert_types.alert_type_id;


--
-- Name: alert_types_alert_type_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('alert_types_alert_type_id_seq', 1, false);


--
-- Name: alerts; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE alerts (
    alert_id integer NOT NULL,
    alert_type_id integer NOT NULL,
    user_id integer NOT NULL,
    value character varying(50) NOT NULL,
    verification_code character varying(10),
    is_active integer DEFAULT 0 NOT NULL,
    is_primary integer DEFAULT 0 NOT NULL
);


ALTER TABLE apersona.alerts OWNER TO transuser;

--
-- Name: alerts_alert_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE alerts_alert_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.alerts_alert_id_seq OWNER TO transuser;

--
-- Name: alerts_alert_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE alerts_alert_id_seq OWNED BY alerts.alert_id;


--
-- Name: alerts_alert_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('alerts_alert_id_seq', 1, false);


--
-- Name: device_geo; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE device_geo (
    device_geo_id integer NOT NULL,
    user_id integer NOT NULL,
    server_id integer NOT NULL,
    device_id character varying(255),
    device_type character varying(50),
    ip_address character varying(50),
    base_device_geo character varying(255),
    master_device_geo character varying(100),
    key_timeout timestamp without time zone,
    processed_at timestamp without time zone,
    domain character varying(250),
    login_count integer
);


ALTER TABLE apersona.device_geo OWNER TO transuser;

--
-- Name: device_geo_device_geo_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE device_geo_device_geo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.device_geo_device_geo_id_seq OWNER TO transuser;

--
-- Name: device_geo_device_geo_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE device_geo_device_geo_id_seq OWNED BY device_geo.device_geo_id;


--
-- Name: device_geo_device_geo_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('device_geo_device_geo_id_seq', 1, false);


--
-- Name: email_service; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE email_service (
    email_service_id integer NOT NULL,
    provider_id integer,
    smtpout_url character varying(255) NOT NULL,
    port_number integer NOT NULL,
    login_id character varying(200) NOT NULL,
    password character varying(200),
    from_addr character varying(200) NOT NULL,
    protocol character varying(45) DEFAULT 'ssl'::character varying NOT NULL,
    smtp character varying(45) DEFAULT 'smtps'::character varying NOT NULL
);


ALTER TABLE apersona.email_service OWNER TO transuser;

--
-- Name: email_service_email_service_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE email_service_email_service_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.email_service_email_service_id_seq OWNER TO transuser;

--
-- Name: email_service_email_service_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE email_service_email_service_id_seq OWNED BY email_service.email_service_id;


--
-- Name: email_service_email_service_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('email_service_email_service_id_seq', 2, true);


--
-- Name: failed_logins; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE failed_logins (
    id integer NOT NULL,
    user_id integer,
    server_id integer,
    failed_on timestamp without time zone DEFAULT now(),
    reason character varying(255),
    email character varying(50)
);


ALTER TABLE apersona.failed_logins OWNER TO transuser;

--
-- Name: failed_logins_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE failed_logins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.failed_logins_id_seq OWNER TO transuser;

--
-- Name: failed_logins_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE failed_logins_id_seq OWNED BY failed_logins.id;


--
-- Name: failed_logins_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('failed_logins_id_seq', 1, false);


--
-- Name: history_store; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE history_store (
    timemark timestamp without time zone NOT NULL,
    table_name character varying(50) NOT NULL,
    pk_date_src character varying(400) NOT NULL,
    pk_date_dest character varying(400) NOT NULL,
    record_state smallint NOT NULL
);


ALTER TABLE apersona.history_store OWNER TO transuser;

--
-- Name: installation_tracker; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE installation_tracker (
    id integer NOT NULL,
    installation_key character varying(100),
    eff_from_dt timestamp without time zone,
    eff_until_dt timestamp without time zone,
    updated_by character varying(100),
    updated_dt timestamp without time zone
);


ALTER TABLE apersona.installation_tracker OWNER TO transuser;

--
-- Name: installation_tracker_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE installation_tracker_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.installation_tracker_id_seq OWNER TO transuser;

--
-- Name: installation_tracker_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE installation_tracker_id_seq OWNED BY installation_tracker.id;


--
-- Name: installation_tracker_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('installation_tracker_id_seq', 1, true);


--
-- Name: keyvault_license; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE keyvault_license (
    kv_license_id integer NOT NULL,
    provider_id integer NOT NULL,
    keyvault_name character varying(100) NOT NULL,
    keyvault_license_key character varying(250) NOT NULL,
    auto_register character(1) DEFAULT 'N'::bpchar,
    exp_date date,
    public_ip character varying(45),
    private_ip character varying(45),
    auto_register_end_date date,
    allowed_users integer DEFAULT (5)::numeric,
    license_hash character varying(250),
    license_enc_key character varying(250),
    updated_by character varying(100),
    updated_at timestamp without time zone
);


ALTER TABLE apersona.keyvault_license OWNER TO transuser;

--
-- Name: keyvault_license_kv_license_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE keyvault_license_kv_license_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.keyvault_license_kv_license_id_seq OWNER TO transuser;

--
-- Name: keyvault_license_kv_license_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE keyvault_license_kv_license_id_seq OWNED BY keyvault_license.kv_license_id;


--
-- Name: keyvault_license_kv_license_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('keyvault_license_kv_license_id_seq', 1, true);


--
-- Name: provider; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE provider (
    provider_id integer NOT NULL,
    provider_name character varying(100) NOT NULL,
    provider_url character varying(255) NOT NULL,
    key_timeout integer,
    identifier character varying(200),
    created_at timestamp without time zone,
    status character varying(10)
);


ALTER TABLE apersona.provider OWNER TO transuser;

--
-- Name: provider_provider_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE provider_provider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.provider_provider_id_seq OWNER TO transuser;

--
-- Name: provider_provider_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE provider_provider_id_seq OWNED BY provider.provider_id;


--
-- Name: provider_provider_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('provider_provider_id_seq', 1, true);


--
-- Name: questions; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE questions (
    question_id integer NOT NULL,
    question character varying(255) NOT NULL,
    user_id integer,
    is_custom integer DEFAULT (1)::numeric NOT NULL
);


ALTER TABLE apersona.questions OWNER TO transuser;

--
-- Name: questions_question_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE questions_question_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.questions_question_id_seq OWNER TO transuser;

--
-- Name: questions_question_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE questions_question_id_seq OWNED BY questions.question_id;


--
-- Name: questions_question_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('questions_question_id_seq', 1, false);


--
-- Name: req_resp_log; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE req_resp_log (
    id integer NOT NULL,
    provider_id integer,
    email character varying(200),
    server_id integer,
    server_name character varying(100),
    req character varying(4000),
    response character varying(4000),
    details character varying(4000),
    processed_at timestamp without time zone
);


ALTER TABLE apersona.req_resp_log OWNER TO transuser;

--
-- Name: req_resp_log_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE req_resp_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.req_resp_log_id_seq OWNER TO transuser;

--
-- Name: req_resp_log_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE req_resp_log_id_seq OWNED BY req_resp_log.id;


--
-- Name: req_resp_log_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('req_resp_log_id_seq', 1, false);


--
-- Name: roles; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE roles (
    role_id integer NOT NULL,
    role_name character varying(50) NOT NULL
);


ALTER TABLE apersona.roles OWNER TO transuser;

--
-- Name: roles_role_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE roles_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.roles_role_id_seq OWNER TO transuser;

--
-- Name: roles_role_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE roles_role_id_seq OWNED BY roles.role_id;


--
-- Name: roles_role_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('roles_role_id_seq', 2, true);


--
-- Name: server; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE server (
    server_id integer NOT NULL,
    svr_service_name character varying(255) NOT NULL,
    server_public_nat_ip character varying(500) NOT NULL,
    api_key character varying(255),
    provider_id integer NOT NULL,
    pc_timeout_1 double precision DEFAULT (5)::numeric,
    pc_timeout_2 double precision DEFAULT (15)::numeric,
    pc_timeout_3 double precision DEFAULT (45)::numeric,
    mobile_timeout_1 double precision DEFAULT (7)::numeric,
    mobile_timeout_2 double precision DEFAULT (15)::numeric,
    mobile_timeout_3 double precision DEFAULT (30)::numeric,
    expiry_date timestamp without time zone,
    server_private_ip character varying(50),
    server_time_zone character varying(50),
    geo_filter character varying(50),
    confirm_method character varying(45),
    auto_conf_type character varying(45),
    auto_conf_end_date date,
    auto_conf_logins integer,
    forensic_domain character varying(50),
    server_group_id character varying(50),
    forensic_method character varying(45),
    force_enhanced character varying(45),
    force_enh_cidr character varying(45),
    otp_verify_method_1 character varying(50),
    otp_verify_method_2 character varying(50),
    otp_verify_subject character varying(255),
    otp_verify_body character varying(4000),
    otp_conf_retry integer,
    otp_conf_retry_notify character varying(100),
    otp_conf_timeout integer,
    otp_conf_timeout_notify character varying(100),
    otp_conf_subject character varying(255),
    otp_conf_body character varying(4000),
    server_label character varying(45) NOT NULL,
    geo_inlcude_countries character varying(4000),
    geo_exclude_countries character varying(4000),
    otp_length integer,
    mitm_checing character varying(45),
    bypass character varying(1000),
    param1 character varying(500),
    param2 character varying(500),
    policy_vs_appl_cond character varying(45),
    is_appl_field1 character varying(5),
    appl_field1_oper character varying(45),
    appl_field1_value character varying(45),
    is_appl_field2 character varying(5),
    appl_field2_oper character varying(45),
    appl_field2_val character varying(45),
    appl_field1_vs_field2_cond character varying(45)
);


ALTER TABLE apersona.server OWNER TO transuser;

--
-- Name: server_group; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE server_group (
    server_group_id integer NOT NULL,
    server_group_name character varying(55) NOT NULL
);


ALTER TABLE apersona.server_group OWNER TO transuser;

--
-- Name: server_group_mapping; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE server_group_mapping (
    server_group_mapping_id integer NOT NULL,
    server_group_id integer NOT NULL,
    server_id integer NOT NULL,
    is_primary character varying(45) DEFAULT 'N'::character varying NOT NULL,
    notes character varying(200)
);


ALTER TABLE apersona.server_group_mapping OWNER TO transuser;

--
-- Name: server_group_mapping_server_group_mapping_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE server_group_mapping_server_group_mapping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.server_group_mapping_server_group_mapping_id_seq OWNER TO transuser;

--
-- Name: server_group_mapping_server_group_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE server_group_mapping_server_group_mapping_id_seq OWNED BY server_group_mapping.server_group_mapping_id;


--
-- Name: server_group_mapping_server_group_mapping_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('server_group_mapping_server_group_mapping_id_seq', 1, false);


--
-- Name: server_group_server_group_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE server_group_server_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.server_group_server_group_id_seq OWNER TO transuser;

--
-- Name: server_group_server_group_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE server_group_server_group_id_seq OWNED BY server_group.server_group_id;


--
-- Name: server_group_server_group_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('server_group_server_group_id_seq', 1, false);


--
-- Name: server_server_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE server_server_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.server_server_id_seq OWNER TO transuser;

--
-- Name: server_server_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE server_server_id_seq OWNED BY server.server_id;


--
-- Name: server_server_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('server_server_id_seq', 2, true);


--
-- Name: user; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE "user" (
    user_id integer NOT NULL,
    provider_id integer NOT NULL,
    email character varying(50) NOT NULL,
    email_hash character varying(255) NOT NULL,
    password character varying(50),
    is_first_login integer DEFAULT (1)::numeric,
    is_pwd_reset integer DEFAULT 0,
    verification_code character varying(10),
    created_on timestamp without time zone DEFAULT now(),
    is_verified integer DEFAULT 0,
    is_hint_set integer DEFAULT 0,
    is_active integer DEFAULT 0,
    force_enhanced character varying(45) DEFAULT 'N'::character varying,
    verification_code_type character varying(45),
    is_super_admin integer DEFAULT 0,
    user_login_id character varying(50) NOT NULL,
    otp_sent_time timestamp without time zone
);


ALTER TABLE apersona."user" OWNER TO transuser;

--
-- Name: user_login_counter; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE user_login_counter (
    user_login_countrol_id integer NOT NULL,
    user_id integer,
    server_id integer,
    counter integer,
    identifier character varying(100)
);


ALTER TABLE apersona.user_login_counter OWNER TO transuser;

--
-- Name: user_login_counter_user_login_countrol_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE user_login_counter_user_login_countrol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.user_login_counter_user_login_countrol_id_seq OWNER TO transuser;

--
-- Name: user_login_counter_user_login_countrol_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE user_login_counter_user_login_countrol_id_seq OWNED BY user_login_counter.user_login_countrol_id;


--
-- Name: user_login_counter_user_login_countrol_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('user_login_counter_user_login_countrol_id_seq', 1, false);


--
-- Name: user_questions; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE user_questions (
    user_question_id integer NOT NULL,
    user_id integer NOT NULL,
    question_id integer NOT NULL,
    answer character varying(255) NOT NULL
);


ALTER TABLE apersona.user_questions OWNER TO transuser;

--
-- Name: user_questions_user_question_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE user_questions_user_question_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.user_questions_user_question_id_seq OWNER TO transuser;

--
-- Name: user_questions_user_question_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE user_questions_user_question_id_seq OWNED BY user_questions.user_question_id;


--
-- Name: user_questions_user_question_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('user_questions_user_question_id_seq', 1, false);


--
-- Name: user_roles; Type: TABLE; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE TABLE user_roles (
    user_role_id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    is_accessed integer DEFAULT 0
);


ALTER TABLE apersona.user_roles OWNER TO transuser;

--
-- Name: user_roles_user_role_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE user_roles_user_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.user_roles_user_role_id_seq OWNER TO transuser;

--
-- Name: user_roles_user_role_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE user_roles_user_role_id_seq OWNED BY user_roles.user_role_id;


--
-- Name: user_roles_user_role_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('user_roles_user_role_id_seq', 2, true);


--
-- Name: user_user_id_seq; Type: SEQUENCE; Schema: apersona; Owner: transuser
--

CREATE SEQUENCE user_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE apersona.user_user_id_seq OWNER TO transuser;

--
-- Name: user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: transuser
--

ALTER SEQUENCE user_user_id_seq OWNED BY "user".user_id;


--
-- Name: user_user_id_seq; Type: SEQUENCE SET; Schema: apersona; Owner: transuser
--

SELECT pg_catalog.setval('user_user_id_seq', 2, true);


--
-- Name: alert_type_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY alert_types ALTER COLUMN alert_type_id SET DEFAULT nextval('alert_types_alert_type_id_seq'::regclass);


--
-- Name: alert_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY alerts ALTER COLUMN alert_id SET DEFAULT nextval('alerts_alert_id_seq'::regclass);


--
-- Name: device_geo_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY device_geo ALTER COLUMN device_geo_id SET DEFAULT nextval('device_geo_device_geo_id_seq'::regclass);


--
-- Name: email_service_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY email_service ALTER COLUMN email_service_id SET DEFAULT nextval('email_service_email_service_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY failed_logins ALTER COLUMN id SET DEFAULT nextval('failed_logins_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY installation_tracker ALTER COLUMN id SET DEFAULT nextval('installation_tracker_id_seq'::regclass);


--
-- Name: kv_license_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY keyvault_license ALTER COLUMN kv_license_id SET DEFAULT nextval('keyvault_license_kv_license_id_seq'::regclass);


--
-- Name: provider_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY provider ALTER COLUMN provider_id SET DEFAULT nextval('provider_provider_id_seq'::regclass);


--
-- Name: question_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY questions ALTER COLUMN question_id SET DEFAULT nextval('questions_question_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY req_resp_log ALTER COLUMN id SET DEFAULT nextval('req_resp_log_id_seq'::regclass);


--
-- Name: role_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY roles ALTER COLUMN role_id SET DEFAULT nextval('roles_role_id_seq'::regclass);


--
-- Name: server_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY server ALTER COLUMN server_id SET DEFAULT nextval('server_server_id_seq'::regclass);


--
-- Name: server_group_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY server_group ALTER COLUMN server_group_id SET DEFAULT nextval('server_group_server_group_id_seq'::regclass);


--
-- Name: server_group_mapping_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY server_group_mapping ALTER COLUMN server_group_mapping_id SET DEFAULT nextval('server_group_mapping_server_group_mapping_id_seq'::regclass);


--
-- Name: user_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY "user" ALTER COLUMN user_id SET DEFAULT nextval('user_user_id_seq'::regclass);


--
-- Name: user_login_countrol_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY user_login_counter ALTER COLUMN user_login_countrol_id SET DEFAULT nextval('user_login_counter_user_login_countrol_id_seq'::regclass);


--
-- Name: user_question_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY user_questions ALTER COLUMN user_question_id SET DEFAULT nextval('user_questions_user_question_id_seq'::regclass);


--
-- Name: user_role_id; Type: DEFAULT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY user_roles ALTER COLUMN user_role_id SET DEFAULT nextval('user_roles_user_role_id_seq'::regclass);


--
-- Data for Name: alert_types; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY alert_types (alert_type_id, alert_type) FROM stdin;
\.


--
-- Data for Name: alerts; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY alerts (alert_id, alert_type_id, user_id, value, verification_code, is_active, is_primary) FROM stdin;
\.


--
-- Data for Name: device_geo; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY device_geo (device_geo_id, user_id, server_id, device_id, device_type, ip_address, base_device_geo, master_device_geo, key_timeout, processed_at, domain, login_count) FROM stdin;
\.


--
-- Data for Name: email_service; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY email_service (email_service_id, provider_id, smtpout_url, port_number, login_id, password, from_addr, protocol, smtp) FROM stdin;
1	0	smtp.office365.com	587	tc-admin@apersona.com	ENC-Mq/XWyi1qncQeEYS2wUkzA==	tc-admin@apersona.com	tls	smtp
2	1	smtp.office365.com	587	transcirrus@apersona.com	ENC-t8RuCPVuSmZXJvOKj+og8g==	transcirrus@apersona.com	tls	smtp
\.


--
-- Data for Name: failed_logins; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY failed_logins (id, user_id, server_id, failed_on, reason, email) FROM stdin;
\.


--
-- Data for Name: history_store; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY history_store (timemark, table_name, pk_date_src, pk_date_dest, record_state) FROM stdin;
\.


--
-- Data for Name: installation_tracker; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY installation_tracker (id, installation_key, eff_from_dt, eff_until_dt, updated_by, updated_dt) FROM stdin;
1	8911d597c5354e9f89768e83fbb63526	2015-11-20 10:57:20.512	2999-12-31 00:00:00	superadmin@domain.com	2015-11-20 10:57:20.513
\.


--
-- Data for Name: keyvault_license; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY keyvault_license (kv_license_id, provider_id, keyvault_name, keyvault_license_key, auto_register, exp_date, public_ip, private_ip, auto_register_end_date, allowed_users, license_hash, license_enc_key, updated_by, updated_at) FROM stdin;
1	1	transcirrus_lic	aPV-613448a024444705a9420c10d157c875	Y	2099-12-31	\N	\N	\N	100000	\N	\N	superadmin@domain.com	2015-11-20 10:54:14.063
\.


--
-- Data for Name: provider; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY provider (provider_id, provider_name, provider_url, key_timeout, identifier, created_at, status) FROM stdin;
0	Admin Provider	admin.com	200	\N	\N	\N
1	transcirrus_admin_portal	localhost	0	\N	2015-11-20 10:51:15.693	\N
\.


--
-- Data for Name: questions; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY questions (question_id, question, user_id, is_custom) FROM stdin;
\.


--
-- Data for Name: req_resp_log; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY req_resp_log (id, provider_id, email, server_id, server_name, req, response, details, processed_at) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY roles (role_id, role_name) FROM stdin;
1	Admin
2	User
\.


--
-- Data for Name: server; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY server (server_id, svr_service_name, server_public_nat_ip, api_key, provider_id, pc_timeout_1, pc_timeout_2, pc_timeout_3, mobile_timeout_1, mobile_timeout_2, mobile_timeout_3, expiry_date, server_private_ip, server_time_zone, geo_filter, confirm_method, auto_conf_type, auto_conf_end_date, auto_conf_logins, forensic_domain, server_group_id, forensic_method, force_enhanced, force_enh_cidr, otp_verify_method_1, otp_verify_method_2, otp_verify_subject, otp_verify_body, otp_conf_retry, otp_conf_retry_notify, otp_conf_timeout, otp_conf_timeout_notify, otp_conf_subject, otp_conf_body, server_label, geo_inlcude_countries, geo_exclude_countries, otp_length, mitm_checing, bypass, param1, param2, policy_vs_appl_cond, is_appl_field1, appl_field1_oper, appl_field1_value, is_appl_field2, appl_field2_oper, appl_field2_val, appl_field1_vs_field2_cond) FROM stdin;
2	TransCirrus Cloud Appliance	172.24.24.10	tc-user-084rjt24p3ohtwqrpoif	1	60	60	60	60	60	60	\N	\N	EDT	\N	DEFAULT_LOGIN	UNTIL	\N	0	\N	\N	ENHANCED	\N		EMAIL	\N	ID Code for [ServiceName]: [OTPCode]	Enter your ID Code: <b><span style="color:white; background:green;">[OTPCode]</span></b> to verify your access.\r\n<p>This transaction originated from: [IPGEO].<br/>(If you are not accessing [ServiceName], you should reset your password immediately.)</p>	3	LOG_FAIL_KVDB	300	LOG_FAIL_KVDB	Failed Verification for [ServiceName]	There was a failed transaction attempt for user: [UserEmail]\r\nService Name: [ServiceName]\r\nTransaction originated from [IPGEO]\r\nAction may be needed.\r\n\r\n	transcirrus_user	\N	\N	4	Off		\N	\N	OR	\N	=		\N	=		OR
1	TransCirrus Cloud Appliance	172.24.24.10	tc-admin-084rjt24p3ohtwqrpoif	1	60	60	60	60	60	60	\N	\N	EDT	\N	DEFAULT_LOGIN	UNTIL	\N	0	\N	\N	STANDARD	\N		EMAIL	\N	ID Code for [ServiceName]: [OTPCode]	Enter your ID Code: <b><span style="color:white; background:green;">[OTPCode]</span></b> to verify your access.\r\n<p>This transaction originated from: [IPGEO].<br/>(If you are not accessing [ServiceName], you should reset your password immediately.)</p>	3	LOG_FAIL_KVDB	300	LOG_FAIL_KVDB	Failed Verification for [ServiceName]	There was a failed transaction attempt for user: [UserEmail]\r\nService Name: [ServiceName]\r\nTransaction originated from [IPGEO]\r\nAction may be needed.\r\n\r\n	transcirrus_admin	\N	\N	4	Off		\N	\N	OR	\N	=		\N	=		OR
\.


--
-- Data for Name: server_group; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY server_group (server_group_id, server_group_name) FROM stdin;
\.


--
-- Data for Name: server_group_mapping; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY server_group_mapping (server_group_mapping_id, server_group_id, server_id, is_primary, notes) FROM stdin;
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY "user" (user_id, provider_id, email, email_hash, password, is_first_login, is_pwd_reset, verification_code, created_on, is_verified, is_hint_set, is_active, force_enhanced, verification_code_type, is_super_admin, user_login_id, otp_sent_time) FROM stdin;
2	0	bugs@transcirrus.com	646465982	2f8cc17bfcc3727ac1eaf7b6fc02bcd8	0	\N	\N	2015-11-20 10:51:28.482	1	\N	1	Y	\N	1	bugs@transcirrus.com	\N
\.


--
-- Data for Name: user_login_counter; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY user_login_counter (user_login_countrol_id, user_id, server_id, counter, identifier) FROM stdin;
\.


--
-- Data for Name: user_questions; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY user_questions (user_question_id, user_id, question_id, answer) FROM stdin;
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: apersona; Owner: transuser
--

COPY user_roles (user_role_id, user_id, role_id, is_accessed) FROM stdin;
2	2	1	\N
\.


--
-- Name: alert_types_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY alert_types
    ADD CONSTRAINT alert_types_pkey PRIMARY KEY (alert_type_id);


--
-- Name: alerts_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (alert_id);


--
-- Name: device_geo_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY device_geo
    ADD CONSTRAINT device_geo_pkey PRIMARY KEY (device_geo_id);


--
-- Name: email_service_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY email_service
    ADD CONSTRAINT email_service_pkey PRIMARY KEY (email_service_id);


--
-- Name: failed_logins_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY failed_logins
    ADD CONSTRAINT failed_logins_pkey PRIMARY KEY (id);


--
-- Name: history_store_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY history_store
    ADD CONSTRAINT history_store_pkey PRIMARY KEY (table_name, pk_date_dest);


--
-- Name: installation_tracker_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY installation_tracker
    ADD CONSTRAINT installation_tracker_pkey PRIMARY KEY (id);


--
-- Name: keyvault_license_keyvault_license_key_key; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY keyvault_license
    ADD CONSTRAINT keyvault_license_keyvault_license_key_key UNIQUE (keyvault_license_key);


--
-- Name: keyvault_license_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY keyvault_license
    ADD CONSTRAINT keyvault_license_pkey PRIMARY KEY (kv_license_id);


--
-- Name: provider_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY provider
    ADD CONSTRAINT provider_pkey PRIMARY KEY (provider_id);


--
-- Name: questions_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (question_id);


--
-- Name: req_resp_log_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY req_resp_log
    ADD CONSTRAINT req_resp_log_pkey PRIMARY KEY (id);


--
-- Name: roles_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (role_id);


--
-- Name: server_api_key_key; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY server
    ADD CONSTRAINT server_api_key_key UNIQUE (api_key);


--
-- Name: server_group_mapping_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY server_group_mapping
    ADD CONSTRAINT server_group_mapping_pkey PRIMARY KEY (server_group_mapping_id);


--
-- Name: server_group_mapping_server_id_key; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY server_group_mapping
    ADD CONSTRAINT server_group_mapping_server_id_key UNIQUE (server_id);


--
-- Name: server_group_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY server_group
    ADD CONSTRAINT server_group_pkey PRIMARY KEY (server_group_id);


--
-- Name: server_group_server_group_name_key; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY server_group
    ADD CONSTRAINT server_group_server_group_name_key UNIQUE (server_group_name);


--
-- Name: server_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY server
    ADD CONSTRAINT server_pkey PRIMARY KEY (server_id);


--
-- Name: user_login_counter_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY user_login_counter
    ADD CONSTRAINT user_login_counter_pkey PRIMARY KEY (user_login_countrol_id);


--
-- Name: user_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (user_id);


--
-- Name: user_provider_id_email_is_super_admin_user_login_id_key; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_provider_id_email_is_super_admin_user_login_id_key UNIQUE (provider_id, email, is_super_admin, user_login_id);


--
-- Name: user_questions_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY user_questions
    ADD CONSTRAINT user_questions_pkey PRIMARY KEY (user_question_id);


--
-- Name: user_roles_pkey; Type: CONSTRAINT; Schema: apersona; Owner: transuser; Tablespace: 
--

ALTER TABLE ONLY user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_role_id);


--
-- Name: alerts_alert_type_id; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX alerts_alert_type_id ON alerts USING btree (alert_type_id);


--
-- Name: alerts_user_id; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX alerts_user_id ON alerts USING btree (user_id);


--
-- Name: device_geo_server_id_idx; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX device_geo_server_id_idx ON device_geo USING btree (server_id);


--
-- Name: device_geo_user_id; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX device_geo_user_id ON device_geo USING btree (user_id);


--
-- Name: email_service_emial_config_provider_fk_idx; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX email_service_emial_config_provider_fk_idx ON email_service USING btree (provider_id);


--
-- Name: failed_logins_server_id; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX failed_logins_server_id ON failed_logins USING btree (server_id);


--
-- Name: failed_logins_user_id; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX failed_logins_user_id ON failed_logins USING btree (user_id);


--
-- Name: keyvault_license_kv_lic_provider_fk_idx; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX keyvault_license_kv_lic_provider_fk_idx ON keyvault_license USING btree (provider_id);


--
-- Name: questions_user_id; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX questions_user_id ON questions USING btree (user_id);


--
-- Name: server_group_mapping_srv_mapping_grp_id_fk_idx; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX server_group_mapping_srv_mapping_grp_id_fk_idx ON server_group_mapping USING btree (server_group_id);


--
-- Name: server_provider_id; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX server_provider_id ON server USING btree (provider_id);


--
-- Name: user_fk_provider_idx; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX user_fk_provider_idx ON "user" USING btree (provider_id);


--
-- Name: user_login_counter_usr_login_server_id_idx; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX user_login_counter_usr_login_server_id_idx ON user_login_counter USING btree (server_id);


--
-- Name: user_questions_question_id; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX user_questions_question_id ON user_questions USING btree (question_id);


--
-- Name: user_questions_user_id; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX user_questions_user_id ON user_questions USING btree (user_id, question_id);


--
-- Name: user_roles_provider_id; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX user_roles_provider_id ON user_roles USING btree (user_id, role_id);


--
-- Name: user_roles_role_id; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX user_roles_role_id ON user_roles USING btree (role_id);


--
-- Name: user_roles_user_id; Type: INDEX; Schema: apersona; Owner: transuser; Tablespace: 
--

CREATE INDEX user_roles_user_id ON user_roles USING btree (user_id);


--
-- Name: alerts_ibfk_1; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY alerts
    ADD CONSTRAINT alerts_ibfk_1 FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: alerts_ibfk_2; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY alerts
    ADD CONSTRAINT alerts_ibfk_2 FOREIGN KEY (alert_type_id) REFERENCES alert_types(alert_type_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: device_geo_ibfk_1; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY device_geo
    ADD CONSTRAINT device_geo_ibfk_1 FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: emial_config_provider_fk; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY email_service
    ADD CONSTRAINT emial_config_provider_fk FOREIGN KEY (provider_id) REFERENCES provider(provider_id);


--
-- Name: fk_provider; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT fk_provider FOREIGN KEY (provider_id) REFERENCES provider(provider_id);


--
-- Name: kv_lic_provider_fk; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY keyvault_license
    ADD CONSTRAINT kv_lic_provider_fk FOREIGN KEY (provider_id) REFERENCES provider(provider_id);


--
-- Name: questions_ibfk_1; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY questions
    ADD CONSTRAINT questions_ibfk_1 FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: server_ibfk_1; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY server
    ADD CONSTRAINT server_ibfk_1 FOREIGN KEY (provider_id) REFERENCES provider(provider_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: server_id; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY device_geo
    ADD CONSTRAINT server_id FOREIGN KEY (server_id) REFERENCES server(server_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: srv_mapping_grp_id_fk; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY server_group_mapping
    ADD CONSTRAINT srv_mapping_grp_id_fk FOREIGN KEY (server_group_id) REFERENCES server_group(server_group_id);


--
-- Name: srv_mapping_server_id_fk; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY server_group_mapping
    ADD CONSTRAINT srv_mapping_server_id_fk FOREIGN KEY (server_id) REFERENCES server(server_id);


--
-- Name: user_questions_ibfk_1; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY user_questions
    ADD CONSTRAINT user_questions_ibfk_1 FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: user_questions_ibfk_2; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY user_questions
    ADD CONSTRAINT user_questions_ibfk_2 FOREIGN KEY (question_id) REFERENCES questions(question_id) ON UPDATE RESTRICT ON DELETE CASCADE;


--
-- Name: user_role_roleId_fk; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY user_roles
    ADD CONSTRAINT "user_role_roleId_fk" FOREIGN KEY (role_id) REFERENCES roles(role_id);


--
-- Name: user_role_userId_fk; Type: FK CONSTRAINT; Schema: apersona; Owner: transuser
--

ALTER TABLE ONLY user_roles
    ADD CONSTRAINT "user_role_userId_fk" FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON DELETE CASCADE;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO transuser;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

