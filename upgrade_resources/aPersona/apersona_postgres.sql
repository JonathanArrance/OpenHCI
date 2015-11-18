--
-- PostgreSQL database dump
--

-- Dumped from database version 9.4.5
-- Dumped by pg_dump version 9.4.5
-- Started on 2015-11-09 15:11:01

SET statement_timeout = 0;
--SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--DROP DATABASE apersona;
--
-- TOC entry 2340 (class 1262 OID 16394)
-- Name: apersona; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE apersona WITH TEMPLATE = template0 ENCODING = 'UTF8'; --LC_COLLATE = 'English_United States.1252' LC_CTYPE = 'English_United States.1252';


ALTER DATABASE apersona OWNER TO postgres;

\connect apersona

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 6 (class 2615 OID 16395)
-- Name: apersona; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA apersona;


ALTER SCHEMA apersona OWNER TO postgres;

--
-- TOC entry 7 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 2341 (class 0 OID 0)
-- Dependencies: 7
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 210 (class 3079 OID 11855)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2343 (class 0 OID 0)
-- Dependencies: 210
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = apersona, pg_catalog;

--
-- TOC entry 224 (class 1255 OID 16396)
-- Name: a_d_alert_types_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_alert_types_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'alert_types'; 			pk_d = '<alert_type_id>'||OLD."alert_type_id"||'</alert_type_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_alert_types_f() OWNER TO postgres;

--
-- TOC entry 225 (class 1255 OID 16397)
-- Name: a_d_alerts_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_alerts_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'alerts'; 			pk_d = '<alert_id>'||OLD."alert_id"||'</alert_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_alerts_f() OWNER TO postgres;

--
-- TOC entry 226 (class 1255 OID 16398)
-- Name: a_d_device_geo_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_device_geo_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'device_geo'; 			pk_d = '<device_geo_id>'||OLD."device_geo_id"||'</device_geo_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_device_geo_f() OWNER TO postgres;

--
-- TOC entry 227 (class 1255 OID 16399)
-- Name: a_d_email_service_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_email_service_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'email_service'; 			pk_d = '<email_service_id>'||OLD."email_service_id"||'</email_service_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_email_service_f() OWNER TO postgres;

--
-- TOC entry 228 (class 1255 OID 16400)
-- Name: a_d_failed_logins_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_failed_logins_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'failed_logins'; 			pk_d = '<id>'||OLD."id"||'</id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_failed_logins_f() OWNER TO postgres;

--
-- TOC entry 229 (class 1255 OID 16401)
-- Name: a_d_installation_tracker_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_installation_tracker_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'installation_tracker'; 			pk_d = '<id>'||OLD."id"||'</id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_installation_tracker_f() OWNER TO postgres;

--
-- TOC entry 230 (class 1255 OID 16402)
-- Name: a_d_keyvault_license_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_keyvault_license_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'keyvault_license'; 			pk_d = '<kv_license_id>'||OLD."kv_license_id"||'</kv_license_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_keyvault_license_f() OWNER TO postgres;

--
-- TOC entry 231 (class 1255 OID 16403)
-- Name: a_d_provider_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_provider_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'provider'; 			pk_d = '<provider_id>'||OLD."provider_id"||'</provider_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_provider_f() OWNER TO postgres;

--
-- TOC entry 233 (class 1255 OID 16404)
-- Name: a_d_questions_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_questions_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'questions'; 			pk_d = '<question_id>'||OLD."question_id"||'</question_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_questions_f() OWNER TO postgres;

--
-- TOC entry 234 (class 1255 OID 16405)
-- Name: a_d_req_resp_log_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_req_resp_log_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'req_resp_log'; 			pk_d = '<id>'||OLD."id"||'</id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_req_resp_log_f() OWNER TO postgres;

--
-- TOC entry 235 (class 1255 OID 16406)
-- Name: a_d_roles_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_roles_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'roles'; 			pk_d = '<role_id>'||OLD."role_id"||'</role_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_roles_f() OWNER TO postgres;

--
-- TOC entry 236 (class 1255 OID 16407)
-- Name: a_d_server_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_server_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'server'; 			pk_d = '<server_id>'||OLD."server_id"||'</server_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_server_f() OWNER TO postgres;

--
-- TOC entry 237 (class 1255 OID 16408)
-- Name: a_d_server_group_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_server_group_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'server_group'; 			pk_d = '<server_group_id>'||OLD."server_group_id"||'</server_group_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_server_group_f() OWNER TO postgres;

--
-- TOC entry 238 (class 1255 OID 16409)
-- Name: a_d_server_group_mapping_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_server_group_mapping_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'server_group_mapping'; 			pk_d = '<server_group_mapping_id>'||OLD."server_group_mapping_id"||'</server_group_mapping_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_server_group_mapping_f() OWNER TO postgres;

--
-- TOC entry 239 (class 1255 OID 16410)
-- Name: a_d_user_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_user_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'user'; 			pk_d = '<user_id>'||OLD."user_id"||'</user_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_user_f() OWNER TO postgres;

--
-- TOC entry 240 (class 1255 OID 16411)
-- Name: a_d_user_login_counter_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_user_login_counter_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'user_login_counter'; 			pk_d = '<user_login_countrol_id>'||OLD."user_login_countrol_id"||'</user_login_countrol_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_user_login_counter_f() OWNER TO postgres;

--
-- TOC entry 242 (class 1255 OID 16412)
-- Name: a_d_user_questions_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_user_questions_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'user_questions'; 			pk_d = '<user_question_id>'||OLD."user_question_id"||'</user_question_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_user_questions_f() OWNER TO postgres;

--
-- TOC entry 243 (class 1255 OID 16413)
-- Name: a_d_user_roles_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_d_user_roles_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			rs = 0;				rec_state = 3; 			tbl_name = 'user_roles'; 			pk_d = '<user_role_id>'||OLD."user_role_id"||'</user_role_id>'; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 			IF ((rs ISNULL) OR (rs <> 1)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state) VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 			END IF; 			RETURN OLD; 		END; 		$$;


ALTER FUNCTION apersona.a_d_user_roles_f() OWNER TO postgres;

--
-- TOC entry 244 (class 1255 OID 16414)
-- Name: a_i_alert_types_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_alert_types_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'alert_types'; 							pk_d = '<alert_type_id>'||NEW."alert_type_id"||'</alert_type_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_alert_types_f() OWNER TO postgres;

--
-- TOC entry 245 (class 1255 OID 16415)
-- Name: a_i_alerts_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_alerts_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'alerts'; 							pk_d = '<alert_id>'||NEW."alert_id"||'</alert_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_alerts_f() OWNER TO postgres;

--
-- TOC entry 246 (class 1255 OID 16416)
-- Name: a_i_device_geo_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_device_geo_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'device_geo'; 							pk_d = '<device_geo_id>'||NEW."device_geo_id"||'</device_geo_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_device_geo_f() OWNER TO postgres;

--
-- TOC entry 247 (class 1255 OID 16417)
-- Name: a_i_email_service_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_email_service_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'email_service'; 							pk_d = '<email_service_id>'||NEW."email_service_id"||'</email_service_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_email_service_f() OWNER TO postgres;

--
-- TOC entry 248 (class 1255 OID 16418)
-- Name: a_i_failed_logins_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_failed_logins_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'failed_logins'; 							pk_d = '<id>'||NEW."id"||'</id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_failed_logins_f() OWNER TO postgres;

--
-- TOC entry 249 (class 1255 OID 16419)
-- Name: a_i_installation_tracker_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_installation_tracker_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'installation_tracker'; 							pk_d = '<id>'||NEW."id"||'</id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_installation_tracker_f() OWNER TO postgres;

--
-- TOC entry 250 (class 1255 OID 16420)
-- Name: a_i_keyvault_license_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_keyvault_license_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'keyvault_license'; 							pk_d = '<kv_license_id>'||NEW."kv_license_id"||'</kv_license_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_keyvault_license_f() OWNER TO postgres;

--
-- TOC entry 251 (class 1255 OID 16421)
-- Name: a_i_provider_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_provider_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'provider'; 							pk_d = '<provider_id>'||NEW."provider_id"||'</provider_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_provider_f() OWNER TO postgres;

--
-- TOC entry 232 (class 1255 OID 16422)
-- Name: a_i_questions_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_questions_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'questions'; 							pk_d = '<question_id>'||NEW."question_id"||'</question_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_questions_f() OWNER TO postgres;

--
-- TOC entry 241 (class 1255 OID 16423)
-- Name: a_i_req_resp_log_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_req_resp_log_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'req_resp_log'; 							pk_d = '<id>'||NEW."id"||'</id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_req_resp_log_f() OWNER TO postgres;

--
-- TOC entry 223 (class 1255 OID 16424)
-- Name: a_i_roles_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_roles_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'roles'; 							pk_d = '<role_id>'||NEW."role_id"||'</role_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_roles_f() OWNER TO postgres;

--
-- TOC entry 252 (class 1255 OID 16425)
-- Name: a_i_server_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_server_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'server'; 							pk_d = '<server_id>'||NEW."server_id"||'</server_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_server_f() OWNER TO postgres;

--
-- TOC entry 253 (class 1255 OID 16426)
-- Name: a_i_server_group_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_server_group_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'server_group'; 							pk_d = '<server_group_id>'||NEW."server_group_id"||'</server_group_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_server_group_f() OWNER TO postgres;

--
-- TOC entry 254 (class 1255 OID 16427)
-- Name: a_i_server_group_mapping_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_server_group_mapping_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'server_group_mapping'; 							pk_d = '<server_group_mapping_id>'||NEW."server_group_mapping_id"||'</server_group_mapping_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_server_group_mapping_f() OWNER TO postgres;

--
-- TOC entry 255 (class 1255 OID 16428)
-- Name: a_i_user_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_user_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'user'; 							pk_d = '<user_id>'||NEW."user_id"||'</user_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_user_f() OWNER TO postgres;

--
-- TOC entry 256 (class 1255 OID 16429)
-- Name: a_i_user_login_counter_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_user_login_counter_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'user_login_counter'; 							pk_d = '<user_login_countrol_id>'||NEW."user_login_countrol_id"||'</user_login_countrol_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_user_login_counter_f() OWNER TO postgres;

--
-- TOC entry 257 (class 1255 OID 16430)
-- Name: a_i_user_questions_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_user_questions_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'user_questions'; 							pk_d = '<user_question_id>'||NEW."user_question_id"||'</user_question_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_user_questions_f() OWNER TO postgres;

--
-- TOC entry 258 (class 1255 OID 16431)
-- Name: a_i_user_roles_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_i_user_roles_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 						DECLARE 							time_mark TIMESTAMP; 							rec_state INTEGER; 							pk_d VARCHAR(400); 							tbl_name VARCHAR(100); 						BEGIN 							time_mark = now()+'0 second'::interval; 							tbl_name = 'user_roles'; 							pk_d = '<user_role_id>'||NEW."user_role_id"||'</user_role_id>'; 							rec_state = 1;							DELETE FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d; 							INSERT INTO "apersona"."history_store"( timemark, table_name, pk_date_src, pk_date_dest, record_state ) 								VALUES (time_mark, tbl_name, pk_d, pk_d, rec_state ); 							RETURN NEW; 						END; 						$$;


ALTER FUNCTION apersona.a_i_user_roles_f() OWNER TO postgres;

--
-- TOC entry 259 (class 1255 OID 16432)
-- Name: a_u_alert_types_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_alert_types_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'alert_types'; 			pk_d_old = '<alert_type_id>'||OLD."alert_type_id"||'</alert_type_id>'; 			pk_d = '<alert_type_id>'||NEW."alert_type_id"||'</alert_type_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_alert_types_f() OWNER TO postgres;

--
-- TOC entry 260 (class 1255 OID 16433)
-- Name: a_u_alerts_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_alerts_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'alerts'; 			pk_d_old = '<alert_id>'||OLD."alert_id"||'</alert_id>'; 			pk_d = '<alert_id>'||NEW."alert_id"||'</alert_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_alerts_f() OWNER TO postgres;

--
-- TOC entry 261 (class 1255 OID 16434)
-- Name: a_u_device_geo_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_device_geo_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'device_geo'; 			pk_d_old = '<device_geo_id>'||OLD."device_geo_id"||'</device_geo_id>'; 			pk_d = '<device_geo_id>'||NEW."device_geo_id"||'</device_geo_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_device_geo_f() OWNER TO postgres;

--
-- TOC entry 262 (class 1255 OID 16435)
-- Name: a_u_email_service_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_email_service_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'email_service'; 			pk_d_old = '<email_service_id>'||OLD."email_service_id"||'</email_service_id>'; 			pk_d = '<email_service_id>'||NEW."email_service_id"||'</email_service_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_email_service_f() OWNER TO postgres;

--
-- TOC entry 263 (class 1255 OID 16436)
-- Name: a_u_failed_logins_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_failed_logins_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'failed_logins'; 			pk_d_old = '<id>'||OLD."id"||'</id>'; 			pk_d = '<id>'||NEW."id"||'</id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_failed_logins_f() OWNER TO postgres;

--
-- TOC entry 264 (class 1255 OID 16437)
-- Name: a_u_installation_tracker_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_installation_tracker_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'installation_tracker'; 			pk_d_old = '<id>'||OLD."id"||'</id>'; 			pk_d = '<id>'||NEW."id"||'</id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_installation_tracker_f() OWNER TO postgres;

--
-- TOC entry 265 (class 1255 OID 16438)
-- Name: a_u_keyvault_license_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_keyvault_license_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'keyvault_license'; 			pk_d_old = '<kv_license_id>'||OLD."kv_license_id"||'</kv_license_id>'; 			pk_d = '<kv_license_id>'||NEW."kv_license_id"||'</kv_license_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_keyvault_license_f() OWNER TO postgres;

--
-- TOC entry 266 (class 1255 OID 16439)
-- Name: a_u_provider_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_provider_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'provider'; 			pk_d_old = '<provider_id>'||OLD."provider_id"||'</provider_id>'; 			pk_d = '<provider_id>'||NEW."provider_id"||'</provider_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_provider_f() OWNER TO postgres;

--
-- TOC entry 267 (class 1255 OID 16440)
-- Name: a_u_questions_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_questions_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'questions'; 			pk_d_old = '<question_id>'||OLD."question_id"||'</question_id>'; 			pk_d = '<question_id>'||NEW."question_id"||'</question_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_questions_f() OWNER TO postgres;

--
-- TOC entry 268 (class 1255 OID 16441)
-- Name: a_u_req_resp_log_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_req_resp_log_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'req_resp_log'; 			pk_d_old = '<id>'||OLD."id"||'</id>'; 			pk_d = '<id>'||NEW."id"||'</id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_req_resp_log_f() OWNER TO postgres;

--
-- TOC entry 269 (class 1255 OID 16442)
-- Name: a_u_roles_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_roles_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'roles'; 			pk_d_old = '<role_id>'||OLD."role_id"||'</role_id>'; 			pk_d = '<role_id>'||NEW."role_id"||'</role_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_roles_f() OWNER TO postgres;

--
-- TOC entry 270 (class 1255 OID 16443)
-- Name: a_u_server_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_server_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'server'; 			pk_d_old = '<server_id>'||OLD."server_id"||'</server_id>'; 			pk_d = '<server_id>'||NEW."server_id"||'</server_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_server_f() OWNER TO postgres;

--
-- TOC entry 271 (class 1255 OID 16444)
-- Name: a_u_server_group_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_server_group_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'server_group'; 			pk_d_old = '<server_group_id>'||OLD."server_group_id"||'</server_group_id>'; 			pk_d = '<server_group_id>'||NEW."server_group_id"||'</server_group_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_server_group_f() OWNER TO postgres;

--
-- TOC entry 272 (class 1255 OID 16445)
-- Name: a_u_server_group_mapping_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_server_group_mapping_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'server_group_mapping'; 			pk_d_old = '<server_group_mapping_id>'||OLD."server_group_mapping_id"||'</server_group_mapping_id>'; 			pk_d = '<server_group_mapping_id>'||NEW."server_group_mapping_id"||'</server_group_mapping_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_server_group_mapping_f() OWNER TO postgres;

--
-- TOC entry 273 (class 1255 OID 16446)
-- Name: a_u_user_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_user_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'user'; 			pk_d_old = '<user_id>'||OLD."user_id"||'</user_id>'; 			pk_d = '<user_id>'||NEW."user_id"||'</user_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_user_f() OWNER TO postgres;

--
-- TOC entry 274 (class 1255 OID 16447)
-- Name: a_u_user_login_counter_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_user_login_counter_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'user_login_counter'; 			pk_d_old = '<user_login_countrol_id>'||OLD."user_login_countrol_id"||'</user_login_countrol_id>'; 			pk_d = '<user_login_countrol_id>'||NEW."user_login_countrol_id"||'</user_login_countrol_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_user_login_counter_f() OWNER TO postgres;

--
-- TOC entry 275 (class 1255 OID 16448)
-- Name: a_u_user_questions_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_user_questions_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'user_questions'; 			pk_d_old = '<user_question_id>'||OLD."user_question_id"||'</user_question_id>'; 			pk_d = '<user_question_id>'||NEW."user_question_id"||'</user_question_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_user_questions_f() OWNER TO postgres;

--
-- TOC entry 276 (class 1255 OID 16449)
-- Name: a_u_user_roles_f(); Type: FUNCTION; Schema: apersona; Owner: postgres
--

CREATE FUNCTION a_u_user_roles_f() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 		DECLARE 			time_mark TIMESTAMP; 			pk_d_old VARCHAR(400); 			pk_d VARCHAR(400); 			tbl_name VARCHAR(100); 			rec_state INTEGER; 			rs INTEGER; 		BEGIN 			time_mark = now()+'0 second'::interval; 			tbl_name = 'user_roles'; 			pk_d_old = '<user_role_id>'||OLD."user_role_id"||'</user_role_id>'; 			pk_d = '<user_role_id>'||NEW."user_role_id"||'</user_role_id>'; 			rec_state = 2; 			rs = 0; 			SELECT record_state INTO rs FROM "apersona"."history_store" WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			IF ((rs ISNULL) OR (rs = 0)) THEN 				INSERT INTO "apersona"."history_store"(timemark, table_name, pk_date_src, pk_date_dest, record_state)  					VALUES (time_mark, tbl_name, pk_d, pk_d_old, rec_state); 			ELSE 				UPDATE "apersona"."history_store" SET timemark = time_mark, pk_date_src = pk_d WHERE table_name = tbl_name AND pk_date_src = pk_d_old; 			END IF; 			RETURN NEW; 		END; 		$$;


ALTER FUNCTION apersona.a_u_user_roles_f() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 173 (class 1259 OID 16450)
-- Name: alert_types; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE TABLE alert_types (
    alert_type_id integer NOT NULL,
    alert_type character varying(50) NOT NULL
);


ALTER TABLE alert_types OWNER TO postgres;

--
-- TOC entry 174 (class 1259 OID 16453)
-- Name: alert_types_alert_type_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE alert_types_alert_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE alert_types_alert_type_id_seq OWNER TO postgres;

--
-- TOC entry 2344 (class 0 OID 0)
-- Dependencies: 174
-- Name: alert_types_alert_type_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE alert_types_alert_type_id_seq OWNED BY alert_types.alert_type_id;


--
-- TOC entry 175 (class 1259 OID 16455)
-- Name: alerts; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
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


ALTER TABLE alerts OWNER TO postgres;

--
-- TOC entry 176 (class 1259 OID 16460)
-- Name: alerts_alert_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE alerts_alert_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE alerts_alert_id_seq OWNER TO postgres;

--
-- TOC entry 2345 (class 0 OID 0)
-- Dependencies: 176
-- Name: alerts_alert_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE alerts_alert_id_seq OWNED BY alerts.alert_id;


--
-- TOC entry 177 (class 1259 OID 16462)
-- Name: device_geo; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
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


ALTER TABLE device_geo OWNER TO postgres;

--
-- TOC entry 178 (class 1259 OID 16468)
-- Name: device_geo_device_geo_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE device_geo_device_geo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE device_geo_device_geo_id_seq OWNER TO postgres;

--
-- TOC entry 2346 (class 0 OID 0)
-- Dependencies: 178
-- Name: device_geo_device_geo_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE device_geo_device_geo_id_seq OWNED BY device_geo.device_geo_id;


--
-- TOC entry 179 (class 1259 OID 16470)
-- Name: email_service; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
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


ALTER TABLE email_service OWNER TO postgres;

--
-- TOC entry 180 (class 1259 OID 16478)
-- Name: email_service_email_service_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE email_service_email_service_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE email_service_email_service_id_seq OWNER TO postgres;

--
-- TOC entry 2347 (class 0 OID 0)
-- Dependencies: 180
-- Name: email_service_email_service_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE email_service_email_service_id_seq OWNED BY email_service.email_service_id;


--
-- TOC entry 181 (class 1259 OID 16480)
-- Name: failed_logins; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE TABLE failed_logins (
    id integer NOT NULL,
    user_id integer,
    server_id integer,
    failed_on timestamp without time zone DEFAULT now(),
    reason character varying(255),
    email character varying(50)
);


ALTER TABLE failed_logins OWNER TO postgres;

--
-- TOC entry 182 (class 1259 OID 16484)
-- Name: failed_logins_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE failed_logins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE failed_logins_id_seq OWNER TO postgres;

--
-- TOC entry 2348 (class 0 OID 0)
-- Dependencies: 182
-- Name: failed_logins_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE failed_logins_id_seq OWNED BY failed_logins.id;


--
-- TOC entry 183 (class 1259 OID 16486)
-- Name: history_store; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE TABLE history_store (
    timemark timestamp without time zone NOT NULL,
    table_name character varying(50) NOT NULL,
    pk_date_src character varying(400) NOT NULL,
    pk_date_dest character varying(400) NOT NULL,
    record_state smallint NOT NULL
);


ALTER TABLE history_store OWNER TO postgres;

--
-- TOC entry 184 (class 1259 OID 16492)
-- Name: installation_tracker; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE TABLE installation_tracker (
    id integer NOT NULL,
    installation_key character varying(100),
    eff_from_dt timestamp without time zone,
    eff_until_dt timestamp without time zone,
    updated_by character varying(100),
    updated_dt timestamp without time zone
);


ALTER TABLE installation_tracker OWNER TO postgres;

--
-- TOC entry 185 (class 1259 OID 16495)
-- Name: installation_tracker_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE installation_tracker_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE installation_tracker_id_seq OWNER TO postgres;

--
-- TOC entry 2349 (class 0 OID 0)
-- Dependencies: 185
-- Name: installation_tracker_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE installation_tracker_id_seq OWNED BY installation_tracker.id;


--
-- TOC entry 186 (class 1259 OID 16497)
-- Name: keyvault_license; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
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


ALTER TABLE keyvault_license OWNER TO postgres;

--
-- TOC entry 187 (class 1259 OID 16505)
-- Name: keyvault_license_kv_license_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE keyvault_license_kv_license_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE keyvault_license_kv_license_id_seq OWNER TO postgres;

--
-- TOC entry 2350 (class 0 OID 0)
-- Dependencies: 187
-- Name: keyvault_license_kv_license_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE keyvault_license_kv_license_id_seq OWNED BY keyvault_license.kv_license_id;


--
-- TOC entry 188 (class 1259 OID 16507)
-- Name: provider; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
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


ALTER TABLE provider OWNER TO postgres;

--
-- TOC entry 189 (class 1259 OID 16513)
-- Name: provider_provider_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE provider_provider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE provider_provider_id_seq OWNER TO postgres;

--
-- TOC entry 2351 (class 0 OID 0)
-- Dependencies: 189
-- Name: provider_provider_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE provider_provider_id_seq OWNED BY provider.provider_id;


--
-- TOC entry 190 (class 1259 OID 16515)
-- Name: questions; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE TABLE questions (
    question_id integer NOT NULL,
    question character varying(255) NOT NULL,
    user_id integer,
    is_custom integer DEFAULT (1)::numeric NOT NULL
);


ALTER TABLE questions OWNER TO postgres;

--
-- TOC entry 191 (class 1259 OID 16519)
-- Name: questions_question_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE questions_question_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE questions_question_id_seq OWNER TO postgres;

--
-- TOC entry 2352 (class 0 OID 0)
-- Dependencies: 191
-- Name: questions_question_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE questions_question_id_seq OWNED BY questions.question_id;


--
-- TOC entry 192 (class 1259 OID 16521)
-- Name: req_resp_log; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
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


ALTER TABLE req_resp_log OWNER TO postgres;

--
-- TOC entry 193 (class 1259 OID 16527)
-- Name: req_resp_log_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE req_resp_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE req_resp_log_id_seq OWNER TO postgres;

--
-- TOC entry 2353 (class 0 OID 0)
-- Dependencies: 193
-- Name: req_resp_log_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE req_resp_log_id_seq OWNED BY req_resp_log.id;


--
-- TOC entry 194 (class 1259 OID 16529)
-- Name: roles; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE TABLE roles (
    role_id integer NOT NULL,
    role_name character varying(50) NOT NULL
);


ALTER TABLE roles OWNER TO postgres;

--
-- TOC entry 195 (class 1259 OID 16532)
-- Name: roles_role_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE roles_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE roles_role_id_seq OWNER TO postgres;

--
-- TOC entry 2354 (class 0 OID 0)
-- Dependencies: 195
-- Name: roles_role_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE roles_role_id_seq OWNED BY roles.role_id;


--
-- TOC entry 196 (class 1259 OID 16534)
-- Name: server; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
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


ALTER TABLE server OWNER TO postgres;

--
-- TOC entry 197 (class 1259 OID 16546)
-- Name: server_group; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE TABLE server_group (
    server_group_id integer NOT NULL,
    server_group_name character varying(55) NOT NULL
);


ALTER TABLE server_group OWNER TO postgres;

--
-- TOC entry 198 (class 1259 OID 16549)
-- Name: server_group_mapping; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE TABLE server_group_mapping (
    server_group_mapping_id integer NOT NULL,
    server_group_id integer NOT NULL,
    server_id integer NOT NULL,
    is_primary character varying(45) DEFAULT 'N'::character varying NOT NULL,
    notes character varying(200)
);


ALTER TABLE server_group_mapping OWNER TO postgres;

--
-- TOC entry 199 (class 1259 OID 16553)
-- Name: server_group_mapping_server_group_mapping_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE server_group_mapping_server_group_mapping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE server_group_mapping_server_group_mapping_id_seq OWNER TO postgres;

--
-- TOC entry 2355 (class 0 OID 0)
-- Dependencies: 199
-- Name: server_group_mapping_server_group_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE server_group_mapping_server_group_mapping_id_seq OWNED BY server_group_mapping.server_group_mapping_id;


--
-- TOC entry 200 (class 1259 OID 16555)
-- Name: server_group_server_group_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE server_group_server_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE server_group_server_group_id_seq OWNER TO postgres;

--
-- TOC entry 2356 (class 0 OID 0)
-- Dependencies: 200
-- Name: server_group_server_group_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE server_group_server_group_id_seq OWNED BY server_group.server_group_id;


--
-- TOC entry 201 (class 1259 OID 16557)
-- Name: server_server_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE server_server_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE server_server_id_seq OWNER TO postgres;

--
-- TOC entry 2357 (class 0 OID 0)
-- Dependencies: 201
-- Name: server_server_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE server_server_id_seq OWNED BY server.server_id;


--
-- TOC entry 202 (class 1259 OID 16559)
-- Name: user; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
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


ALTER TABLE "user" OWNER TO postgres;

--
-- TOC entry 203 (class 1259 OID 16573)
-- Name: user_login_counter; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE TABLE user_login_counter (
    user_login_countrol_id integer NOT NULL,
    user_id integer,
    server_id integer,
    counter integer,
    identifier character varying(100)
);


ALTER TABLE user_login_counter OWNER TO postgres;

--
-- TOC entry 204 (class 1259 OID 16576)
-- Name: user_login_counter_user_login_countrol_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE user_login_counter_user_login_countrol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE user_login_counter_user_login_countrol_id_seq OWNER TO postgres;

--
-- TOC entry 2358 (class 0 OID 0)
-- Dependencies: 204
-- Name: user_login_counter_user_login_countrol_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE user_login_counter_user_login_countrol_id_seq OWNED BY user_login_counter.user_login_countrol_id;


--
-- TOC entry 205 (class 1259 OID 16578)
-- Name: user_questions; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE TABLE user_questions (
    user_question_id integer NOT NULL,
    user_id integer NOT NULL,
    question_id integer NOT NULL,
    answer character varying(255) NOT NULL
);


ALTER TABLE user_questions OWNER TO postgres;

--
-- TOC entry 206 (class 1259 OID 16581)
-- Name: user_questions_user_question_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE user_questions_user_question_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE user_questions_user_question_id_seq OWNER TO postgres;

--
-- TOC entry 2359 (class 0 OID 0)
-- Dependencies: 206
-- Name: user_questions_user_question_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE user_questions_user_question_id_seq OWNED BY user_questions.user_question_id;


--
-- TOC entry 207 (class 1259 OID 16583)
-- Name: user_roles; Type: TABLE; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE TABLE user_roles (
    user_role_id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    is_accessed integer DEFAULT 0
);


ALTER TABLE user_roles OWNER TO postgres;

--
-- TOC entry 208 (class 1259 OID 16587)
-- Name: user_roles_user_role_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE user_roles_user_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE user_roles_user_role_id_seq OWNER TO postgres;

--
-- TOC entry 2360 (class 0 OID 0)
-- Dependencies: 208
-- Name: user_roles_user_role_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE user_roles_user_role_id_seq OWNED BY user_roles.user_role_id;


--
-- TOC entry 209 (class 1259 OID 16589)
-- Name: user_user_id_seq; Type: SEQUENCE; Schema: apersona; Owner: postgres
--

CREATE SEQUENCE user_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE user_user_id_seq OWNER TO postgres;

--
-- TOC entry 2361 (class 0 OID 0)
-- Dependencies: 209
-- Name: user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: apersona; Owner: postgres
--

ALTER SEQUENCE user_user_id_seq OWNED BY "user".user_id;


--
-- TOC entry 2050 (class 2604 OID 16591)
-- Name: alert_type_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY alert_types ALTER COLUMN alert_type_id SET DEFAULT nextval('alert_types_alert_type_id_seq'::regclass);


--
-- TOC entry 2053 (class 2604 OID 16592)
-- Name: alert_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY alerts ALTER COLUMN alert_id SET DEFAULT nextval('alerts_alert_id_seq'::regclass);


--
-- TOC entry 2054 (class 2604 OID 16593)
-- Name: device_geo_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY device_geo ALTER COLUMN device_geo_id SET DEFAULT nextval('device_geo_device_geo_id_seq'::regclass);


--
-- TOC entry 2057 (class 2604 OID 16594)
-- Name: email_service_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY email_service ALTER COLUMN email_service_id SET DEFAULT nextval('email_service_email_service_id_seq'::regclass);


--
-- TOC entry 2059 (class 2604 OID 16595)
-- Name: id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY failed_logins ALTER COLUMN id SET DEFAULT nextval('failed_logins_id_seq'::regclass);


--
-- TOC entry 2060 (class 2604 OID 16596)
-- Name: id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY installation_tracker ALTER COLUMN id SET DEFAULT nextval('installation_tracker_id_seq'::regclass);


--
-- TOC entry 2063 (class 2604 OID 16597)
-- Name: kv_license_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY keyvault_license ALTER COLUMN kv_license_id SET DEFAULT nextval('keyvault_license_kv_license_id_seq'::regclass);


--
-- TOC entry 2064 (class 2604 OID 16598)
-- Name: provider_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY provider ALTER COLUMN provider_id SET DEFAULT nextval('provider_provider_id_seq'::regclass);


--
-- TOC entry 2066 (class 2604 OID 16599)
-- Name: question_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY questions ALTER COLUMN question_id SET DEFAULT nextval('questions_question_id_seq'::regclass);


--
-- TOC entry 2067 (class 2604 OID 16600)
-- Name: id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY req_resp_log ALTER COLUMN id SET DEFAULT nextval('req_resp_log_id_seq'::regclass);


--
-- TOC entry 2068 (class 2604 OID 16601)
-- Name: role_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY roles ALTER COLUMN role_id SET DEFAULT nextval('roles_role_id_seq'::regclass);


--
-- TOC entry 2075 (class 2604 OID 16602)
-- Name: server_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY server ALTER COLUMN server_id SET DEFAULT nextval('server_server_id_seq'::regclass);


--
-- TOC entry 2076 (class 2604 OID 16603)
-- Name: server_group_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY server_group ALTER COLUMN server_group_id SET DEFAULT nextval('server_group_server_group_id_seq'::regclass);


--
-- TOC entry 2078 (class 2604 OID 16604)
-- Name: server_group_mapping_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY server_group_mapping ALTER COLUMN server_group_mapping_id SET DEFAULT nextval('server_group_mapping_server_group_mapping_id_seq'::regclass);


--
-- TOC entry 2087 (class 2604 OID 16605)
-- Name: user_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY "user" ALTER COLUMN user_id SET DEFAULT nextval('user_user_id_seq'::regclass);


--
-- TOC entry 2088 (class 2604 OID 16606)
-- Name: user_login_countrol_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY user_login_counter ALTER COLUMN user_login_countrol_id SET DEFAULT nextval('user_login_counter_user_login_countrol_id_seq'::regclass);


--
-- TOC entry 2089 (class 2604 OID 16607)
-- Name: user_question_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY user_questions ALTER COLUMN user_question_id SET DEFAULT nextval('user_questions_user_question_id_seq'::regclass);


--
-- TOC entry 2091 (class 2604 OID 16608)
-- Name: user_role_id; Type: DEFAULT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY user_roles ALTER COLUMN user_role_id SET DEFAULT nextval('user_roles_user_role_id_seq'::regclass);


--
-- TOC entry 2093 (class 2606 OID 16610)
-- Name: alert_types_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY alert_types
    ADD CONSTRAINT alert_types_pkey PRIMARY KEY (alert_type_id);


--
-- TOC entry 2096 (class 2606 OID 16612)
-- Name: alerts_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (alert_id);


--
-- TOC entry 2099 (class 2606 OID 16614)
-- Name: device_geo_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY device_geo
    ADD CONSTRAINT device_geo_pkey PRIMARY KEY (device_geo_id);


--
-- TOC entry 2104 (class 2606 OID 16616)
-- Name: email_service_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY email_service
    ADD CONSTRAINT email_service_pkey PRIMARY KEY (email_service_id);


--
-- TOC entry 2106 (class 2606 OID 16618)
-- Name: failed_logins_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY failed_logins
    ADD CONSTRAINT failed_logins_pkey PRIMARY KEY (id);


--
-- TOC entry 2110 (class 2606 OID 16620)
-- Name: history_store_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY history_store
    ADD CONSTRAINT history_store_pkey PRIMARY KEY (table_name, pk_date_dest);


--
-- TOC entry 2112 (class 2606 OID 16622)
-- Name: installation_tracker_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY installation_tracker
    ADD CONSTRAINT installation_tracker_pkey PRIMARY KEY (id);


--
-- TOC entry 2114 (class 2606 OID 16624)
-- Name: keyvault_license_keyvault_license_key_key; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY keyvault_license
    ADD CONSTRAINT keyvault_license_keyvault_license_key_key UNIQUE (keyvault_license_key);


--
-- TOC entry 2117 (class 2606 OID 16626)
-- Name: keyvault_license_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY keyvault_license
    ADD CONSTRAINT keyvault_license_pkey PRIMARY KEY (kv_license_id);


--
-- TOC entry 2119 (class 2606 OID 16628)
-- Name: provider_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY provider
    ADD CONSTRAINT provider_pkey PRIMARY KEY (provider_id);


--
-- TOC entry 2121 (class 2606 OID 16630)
-- Name: questions_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (question_id);


--
-- TOC entry 2124 (class 2606 OID 16632)
-- Name: req_resp_log_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY req_resp_log
    ADD CONSTRAINT req_resp_log_pkey PRIMARY KEY (id);


--
-- TOC entry 2126 (class 2606 OID 16634)
-- Name: roles_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (role_id);


--
-- TOC entry 2128 (class 2606 OID 16636)
-- Name: server_api_key_key; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY server
    ADD CONSTRAINT server_api_key_key UNIQUE (api_key);


--
-- TOC entry 2137 (class 2606 OID 16638)
-- Name: server_group_mapping_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY server_group_mapping
    ADD CONSTRAINT server_group_mapping_pkey PRIMARY KEY (server_group_mapping_id);


--
-- TOC entry 2139 (class 2606 OID 16640)
-- Name: server_group_mapping_server_id_key; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY server_group_mapping
    ADD CONSTRAINT server_group_mapping_server_id_key UNIQUE (server_id);


--
-- TOC entry 2133 (class 2606 OID 16642)
-- Name: server_group_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY server_group
    ADD CONSTRAINT server_group_pkey PRIMARY KEY (server_group_id);


--
-- TOC entry 2135 (class 2606 OID 16644)
-- Name: server_group_server_group_name_key; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY server_group
    ADD CONSTRAINT server_group_server_group_name_key UNIQUE (server_group_name);


--
-- TOC entry 2130 (class 2606 OID 16646)
-- Name: server_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY server
    ADD CONSTRAINT server_pkey PRIMARY KEY (server_id);


--
-- TOC entry 2147 (class 2606 OID 16648)
-- Name: user_login_counter_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_login_counter
    ADD CONSTRAINT user_login_counter_pkey PRIMARY KEY (user_login_countrol_id);


--
-- TOC entry 2143 (class 2606 OID 16650)
-- Name: user_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (user_id);


--
-- TOC entry 2145 (class 2606 OID 16652)
-- Name: user_provider_id_email_is_super_admin_user_login_id_key; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_provider_id_email_is_super_admin_user_login_id_key UNIQUE (provider_id, email, is_super_admin, user_login_id);


--
-- TOC entry 2150 (class 2606 OID 16654)
-- Name: user_questions_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_questions
    ADD CONSTRAINT user_questions_pkey PRIMARY KEY (user_question_id);


--
-- TOC entry 2154 (class 2606 OID 16656)
-- Name: user_roles_pkey; Type: CONSTRAINT; Schema: apersona; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_role_id);


--
-- TOC entry 2094 (class 1259 OID 16657)
-- Name: alerts_alert_type_id; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX alerts_alert_type_id ON alerts USING btree (alert_type_id);


--
-- TOC entry 2097 (class 1259 OID 16658)
-- Name: alerts_user_id; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX alerts_user_id ON alerts USING btree (user_id);


--
-- TOC entry 2100 (class 1259 OID 16659)
-- Name: device_geo_server_id_idx; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX device_geo_server_id_idx ON device_geo USING btree (server_id);


--
-- TOC entry 2101 (class 1259 OID 16660)
-- Name: device_geo_user_id; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX device_geo_user_id ON device_geo USING btree (user_id);


--
-- TOC entry 2102 (class 1259 OID 16661)
-- Name: email_service_emial_config_provider_fk_idx; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX email_service_emial_config_provider_fk_idx ON email_service USING btree (provider_id);


--
-- TOC entry 2107 (class 1259 OID 16662)
-- Name: failed_logins_server_id; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX failed_logins_server_id ON failed_logins USING btree (server_id);


--
-- TOC entry 2108 (class 1259 OID 16663)
-- Name: failed_logins_user_id; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX failed_logins_user_id ON failed_logins USING btree (user_id);


--
-- TOC entry 2115 (class 1259 OID 16664)
-- Name: keyvault_license_kv_lic_provider_fk_idx; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX keyvault_license_kv_lic_provider_fk_idx ON keyvault_license USING btree (provider_id);


--
-- TOC entry 2122 (class 1259 OID 16665)
-- Name: questions_user_id; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX questions_user_id ON questions USING btree (user_id);


--
-- TOC entry 2140 (class 1259 OID 16666)
-- Name: server_group_mapping_srv_mapping_grp_id_fk_idx; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX server_group_mapping_srv_mapping_grp_id_fk_idx ON server_group_mapping USING btree (server_group_id);


--
-- TOC entry 2131 (class 1259 OID 16667)
-- Name: server_provider_id; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX server_provider_id ON server USING btree (provider_id);


--
-- TOC entry 2141 (class 1259 OID 16668)
-- Name: user_fk_provider_idx; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX user_fk_provider_idx ON "user" USING btree (provider_id);


--
-- TOC entry 2148 (class 1259 OID 16669)
-- Name: user_login_counter_usr_login_server_id_idx; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX user_login_counter_usr_login_server_id_idx ON user_login_counter USING btree (server_id);


--
-- TOC entry 2151 (class 1259 OID 16670)
-- Name: user_questions_question_id; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX user_questions_question_id ON user_questions USING btree (question_id);


--
-- TOC entry 2152 (class 1259 OID 16671)
-- Name: user_questions_user_id; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX user_questions_user_id ON user_questions USING btree (user_id, question_id);


--
-- TOC entry 2155 (class 1259 OID 16672)
-- Name: user_roles_provider_id; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX user_roles_provider_id ON user_roles USING btree (user_id, role_id);


--
-- TOC entry 2156 (class 1259 OID 16673)
-- Name: user_roles_role_id; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX user_roles_role_id ON user_roles USING btree (role_id);


--
-- TOC entry 2157 (class 1259 OID 16674)
-- Name: user_roles_user_id; Type: INDEX; Schema: apersona; Owner: postgres; Tablespace: 
--

CREATE INDEX user_roles_user_id ON user_roles USING btree (user_id);


--
-- TOC entry 2173 (class 2620 OID 16675)
-- Name: a_d_alert_types; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_alert_types AFTER DELETE ON alert_types FOR EACH ROW EXECUTE PROCEDURE a_d_alert_types_f();


--
-- TOC entry 2176 (class 2620 OID 16676)
-- Name: a_d_alerts; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_alerts AFTER DELETE ON alerts FOR EACH ROW EXECUTE PROCEDURE a_d_alerts_f();


--
-- TOC entry 2179 (class 2620 OID 16677)
-- Name: a_d_device_geo; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_device_geo AFTER DELETE ON device_geo FOR EACH ROW EXECUTE PROCEDURE a_d_device_geo_f();


--
-- TOC entry 2182 (class 2620 OID 16678)
-- Name: a_d_email_service; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_email_service AFTER DELETE ON email_service FOR EACH ROW EXECUTE PROCEDURE a_d_email_service_f();


--
-- TOC entry 2185 (class 2620 OID 16679)
-- Name: a_d_failed_logins; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_failed_logins AFTER DELETE ON failed_logins FOR EACH ROW EXECUTE PROCEDURE a_d_failed_logins_f();


--
-- TOC entry 2188 (class 2620 OID 16680)
-- Name: a_d_installation_tracker; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_installation_tracker AFTER DELETE ON installation_tracker FOR EACH ROW EXECUTE PROCEDURE a_d_installation_tracker_f();


--
-- TOC entry 2191 (class 2620 OID 16681)
-- Name: a_d_keyvault_license; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_keyvault_license AFTER DELETE ON keyvault_license FOR EACH ROW EXECUTE PROCEDURE a_d_keyvault_license_f();


--
-- TOC entry 2194 (class 2620 OID 16682)
-- Name: a_d_provider; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_provider AFTER DELETE ON provider FOR EACH ROW EXECUTE PROCEDURE a_d_provider_f();


--
-- TOC entry 2197 (class 2620 OID 16683)
-- Name: a_d_questions; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_questions AFTER DELETE ON questions FOR EACH ROW EXECUTE PROCEDURE a_d_questions_f();


--
-- TOC entry 2200 (class 2620 OID 16684)
-- Name: a_d_req_resp_log; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_req_resp_log AFTER DELETE ON req_resp_log FOR EACH ROW EXECUTE PROCEDURE a_d_req_resp_log_f();


--
-- TOC entry 2203 (class 2620 OID 16685)
-- Name: a_d_roles; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_roles AFTER DELETE ON roles FOR EACH ROW EXECUTE PROCEDURE a_d_roles_f();


--
-- TOC entry 2206 (class 2620 OID 16686)
-- Name: a_d_server; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_server AFTER DELETE ON server FOR EACH ROW EXECUTE PROCEDURE a_d_server_f();


--
-- TOC entry 2209 (class 2620 OID 16687)
-- Name: a_d_server_group; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_server_group AFTER DELETE ON server_group FOR EACH ROW EXECUTE PROCEDURE a_d_server_group_f();


--
-- TOC entry 2212 (class 2620 OID 16688)
-- Name: a_d_server_group_mapping; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_server_group_mapping AFTER DELETE ON server_group_mapping FOR EACH ROW EXECUTE PROCEDURE a_d_server_group_mapping_f();


--
-- TOC entry 2215 (class 2620 OID 16689)
-- Name: a_d_user; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_user AFTER DELETE ON "user" FOR EACH ROW EXECUTE PROCEDURE a_d_user_f();


--
-- TOC entry 2218 (class 2620 OID 16690)
-- Name: a_d_user_login_counter; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_user_login_counter AFTER DELETE ON user_login_counter FOR EACH ROW EXECUTE PROCEDURE a_d_user_login_counter_f();


--
-- TOC entry 2221 (class 2620 OID 16691)
-- Name: a_d_user_questions; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_user_questions AFTER DELETE ON user_questions FOR EACH ROW EXECUTE PROCEDURE a_d_user_questions_f();


--
-- TOC entry 2224 (class 2620 OID 16692)
-- Name: a_d_user_roles; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_d_user_roles AFTER DELETE ON user_roles FOR EACH ROW EXECUTE PROCEDURE a_d_user_roles_f();


--
-- TOC entry 2174 (class 2620 OID 16693)
-- Name: a_i_alert_types; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_alert_types AFTER INSERT ON alert_types FOR EACH ROW EXECUTE PROCEDURE a_i_alert_types_f();


--
-- TOC entry 2177 (class 2620 OID 16694)
-- Name: a_i_alerts; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_alerts AFTER INSERT ON alerts FOR EACH ROW EXECUTE PROCEDURE a_i_alerts_f();


--
-- TOC entry 2180 (class 2620 OID 16695)
-- Name: a_i_device_geo; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_device_geo AFTER INSERT ON device_geo FOR EACH ROW EXECUTE PROCEDURE a_i_device_geo_f();


--
-- TOC entry 2183 (class 2620 OID 16696)
-- Name: a_i_email_service; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_email_service AFTER INSERT ON email_service FOR EACH ROW EXECUTE PROCEDURE a_i_email_service_f();


--
-- TOC entry 2186 (class 2620 OID 16697)
-- Name: a_i_failed_logins; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_failed_logins AFTER INSERT ON failed_logins FOR EACH ROW EXECUTE PROCEDURE a_i_failed_logins_f();


--
-- TOC entry 2189 (class 2620 OID 16698)
-- Name: a_i_installation_tracker; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_installation_tracker AFTER INSERT ON installation_tracker FOR EACH ROW EXECUTE PROCEDURE a_i_installation_tracker_f();


--
-- TOC entry 2192 (class 2620 OID 16699)
-- Name: a_i_keyvault_license; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_keyvault_license AFTER INSERT ON keyvault_license FOR EACH ROW EXECUTE PROCEDURE a_i_keyvault_license_f();


--
-- TOC entry 2195 (class 2620 OID 16700)
-- Name: a_i_provider; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_provider AFTER INSERT ON provider FOR EACH ROW EXECUTE PROCEDURE a_i_provider_f();


--
-- TOC entry 2198 (class 2620 OID 16701)
-- Name: a_i_questions; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_questions AFTER INSERT ON questions FOR EACH ROW EXECUTE PROCEDURE a_i_questions_f();


--
-- TOC entry 2201 (class 2620 OID 16702)
-- Name: a_i_req_resp_log; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_req_resp_log AFTER INSERT ON req_resp_log FOR EACH ROW EXECUTE PROCEDURE a_i_req_resp_log_f();


--
-- TOC entry 2204 (class 2620 OID 16703)
-- Name: a_i_roles; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_roles AFTER INSERT ON roles FOR EACH ROW EXECUTE PROCEDURE a_i_roles_f();


--
-- TOC entry 2207 (class 2620 OID 16704)
-- Name: a_i_server; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_server AFTER INSERT ON server FOR EACH ROW EXECUTE PROCEDURE a_i_server_f();


--
-- TOC entry 2210 (class 2620 OID 16705)
-- Name: a_i_server_group; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_server_group AFTER INSERT ON server_group FOR EACH ROW EXECUTE PROCEDURE a_i_server_group_f();


--
-- TOC entry 2213 (class 2620 OID 16706)
-- Name: a_i_server_group_mapping; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_server_group_mapping AFTER INSERT ON server_group_mapping FOR EACH ROW EXECUTE PROCEDURE a_i_server_group_mapping_f();


--
-- TOC entry 2216 (class 2620 OID 16707)
-- Name: a_i_user; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_user AFTER INSERT ON "user" FOR EACH ROW EXECUTE PROCEDURE a_i_user_f();


--
-- TOC entry 2219 (class 2620 OID 16708)
-- Name: a_i_user_login_counter; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_user_login_counter AFTER INSERT ON user_login_counter FOR EACH ROW EXECUTE PROCEDURE a_i_user_login_counter_f();


--
-- TOC entry 2222 (class 2620 OID 16709)
-- Name: a_i_user_questions; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_user_questions AFTER INSERT ON user_questions FOR EACH ROW EXECUTE PROCEDURE a_i_user_questions_f();


--
-- TOC entry 2225 (class 2620 OID 16710)
-- Name: a_i_user_roles; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_i_user_roles AFTER INSERT ON user_roles FOR EACH ROW EXECUTE PROCEDURE a_i_user_roles_f();


--
-- TOC entry 2175 (class 2620 OID 16711)
-- Name: a_u_alert_types; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_alert_types AFTER UPDATE ON alert_types FOR EACH ROW EXECUTE PROCEDURE a_u_alert_types_f();


--
-- TOC entry 2178 (class 2620 OID 16712)
-- Name: a_u_alerts; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_alerts AFTER UPDATE ON alerts FOR EACH ROW EXECUTE PROCEDURE a_u_alerts_f();


--
-- TOC entry 2181 (class 2620 OID 16713)
-- Name: a_u_device_geo; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_device_geo AFTER UPDATE ON device_geo FOR EACH ROW EXECUTE PROCEDURE a_u_device_geo_f();


--
-- TOC entry 2184 (class 2620 OID 16714)
-- Name: a_u_email_service; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_email_service AFTER UPDATE ON email_service FOR EACH ROW EXECUTE PROCEDURE a_u_email_service_f();


--
-- TOC entry 2187 (class 2620 OID 16715)
-- Name: a_u_failed_logins; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_failed_logins AFTER UPDATE ON failed_logins FOR EACH ROW EXECUTE PROCEDURE a_u_failed_logins_f();


--
-- TOC entry 2190 (class 2620 OID 16716)
-- Name: a_u_installation_tracker; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_installation_tracker AFTER UPDATE ON installation_tracker FOR EACH ROW EXECUTE PROCEDURE a_u_installation_tracker_f();


--
-- TOC entry 2193 (class 2620 OID 16717)
-- Name: a_u_keyvault_license; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_keyvault_license AFTER UPDATE ON keyvault_license FOR EACH ROW EXECUTE PROCEDURE a_u_keyvault_license_f();


--
-- TOC entry 2196 (class 2620 OID 16718)
-- Name: a_u_provider; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_provider AFTER UPDATE ON provider FOR EACH ROW EXECUTE PROCEDURE a_u_provider_f();


--
-- TOC entry 2199 (class 2620 OID 16719)
-- Name: a_u_questions; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_questions AFTER UPDATE ON questions FOR EACH ROW EXECUTE PROCEDURE a_u_questions_f();


--
-- TOC entry 2202 (class 2620 OID 16720)
-- Name: a_u_req_resp_log; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_req_resp_log AFTER UPDATE ON req_resp_log FOR EACH ROW EXECUTE PROCEDURE a_u_req_resp_log_f();


--
-- TOC entry 2205 (class 2620 OID 16721)
-- Name: a_u_roles; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_roles AFTER UPDATE ON roles FOR EACH ROW EXECUTE PROCEDURE a_u_roles_f();


--
-- TOC entry 2208 (class 2620 OID 16722)
-- Name: a_u_server; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_server AFTER UPDATE ON server FOR EACH ROW EXECUTE PROCEDURE a_u_server_f();


--
-- TOC entry 2211 (class 2620 OID 16723)
-- Name: a_u_server_group; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_server_group AFTER UPDATE ON server_group FOR EACH ROW EXECUTE PROCEDURE a_u_server_group_f();


--
-- TOC entry 2214 (class 2620 OID 16724)
-- Name: a_u_server_group_mapping; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_server_group_mapping AFTER UPDATE ON server_group_mapping FOR EACH ROW EXECUTE PROCEDURE a_u_server_group_mapping_f();


--
-- TOC entry 2217 (class 2620 OID 16725)
-- Name: a_u_user; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_user AFTER UPDATE ON "user" FOR EACH ROW EXECUTE PROCEDURE a_u_user_f();


--
-- TOC entry 2220 (class 2620 OID 16726)
-- Name: a_u_user_login_counter; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_user_login_counter AFTER UPDATE ON user_login_counter FOR EACH ROW EXECUTE PROCEDURE a_u_user_login_counter_f();


--
-- TOC entry 2223 (class 2620 OID 16727)
-- Name: a_u_user_questions; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_user_questions AFTER UPDATE ON user_questions FOR EACH ROW EXECUTE PROCEDURE a_u_user_questions_f();


--
-- TOC entry 2226 (class 2620 OID 16728)
-- Name: a_u_user_roles; Type: TRIGGER; Schema: apersona; Owner: postgres
--

CREATE TRIGGER a_u_user_roles AFTER UPDATE ON user_roles FOR EACH ROW EXECUTE PROCEDURE a_u_user_roles_f();


--
-- TOC entry 2158 (class 2606 OID 16729)
-- Name: alerts_ibfk_1; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY alerts
    ADD CONSTRAINT alerts_ibfk_1 FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 2159 (class 2606 OID 16734)
-- Name: alerts_ibfk_2; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY alerts
    ADD CONSTRAINT alerts_ibfk_2 FOREIGN KEY (alert_type_id) REFERENCES alert_types(alert_type_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 2160 (class 2606 OID 16739)
-- Name: device_geo_ibfk_1; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY device_geo
    ADD CONSTRAINT device_geo_ibfk_1 FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2162 (class 2606 OID 16744)
-- Name: emial_config_provider_fk; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY email_service
    ADD CONSTRAINT emial_config_provider_fk FOREIGN KEY (provider_id) REFERENCES provider(provider_id);


--
-- TOC entry 2168 (class 2606 OID 16749)
-- Name: fk_provider; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT fk_provider FOREIGN KEY (provider_id) REFERENCES provider(provider_id);


--
-- TOC entry 2163 (class 2606 OID 16754)
-- Name: kv_lic_provider_fk; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY keyvault_license
    ADD CONSTRAINT kv_lic_provider_fk FOREIGN KEY (provider_id) REFERENCES provider(provider_id);


--
-- TOC entry 2164 (class 2606 OID 16759)
-- Name: questions_ibfk_1; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY questions
    ADD CONSTRAINT questions_ibfk_1 FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 2165 (class 2606 OID 16764)
-- Name: server_ibfk_1; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY server
    ADD CONSTRAINT server_ibfk_1 FOREIGN KEY (provider_id) REFERENCES provider(provider_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 2161 (class 2606 OID 16769)
-- Name: server_id; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY device_geo
    ADD CONSTRAINT server_id FOREIGN KEY (server_id) REFERENCES server(server_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2166 (class 2606 OID 16774)
-- Name: srv_mapping_grp_id_fk; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY server_group_mapping
    ADD CONSTRAINT srv_mapping_grp_id_fk FOREIGN KEY (server_group_id) REFERENCES server_group(server_group_id);


--
-- TOC entry 2167 (class 2606 OID 16779)
-- Name: srv_mapping_server_id_fk; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY server_group_mapping
    ADD CONSTRAINT srv_mapping_server_id_fk FOREIGN KEY (server_id) REFERENCES server(server_id);


--
-- TOC entry 2169 (class 2606 OID 16784)
-- Name: user_questions_ibfk_1; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY user_questions
    ADD CONSTRAINT user_questions_ibfk_1 FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 2170 (class 2606 OID 16789)
-- Name: user_questions_ibfk_2; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY user_questions
    ADD CONSTRAINT user_questions_ibfk_2 FOREIGN KEY (question_id) REFERENCES questions(question_id) ON UPDATE RESTRICT ON DELETE CASCADE;


--
-- TOC entry 2171 (class 2606 OID 16794)
-- Name: user_role_roleId_fk; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY user_roles
    ADD CONSTRAINT "user_role_roleId_fk" FOREIGN KEY (role_id) REFERENCES roles(role_id);


--
-- TOC entry 2172 (class 2606 OID 16799)
-- Name: user_role_userId_fk; Type: FK CONSTRAINT; Schema: apersona; Owner: postgres
--

ALTER TABLE ONLY user_roles
    ADD CONSTRAINT "user_role_userId_fk" FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON DELETE CASCADE;


--
-- TOC entry 2342 (class 0 OID 0)
-- Dependencies: 7
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2015-11-09 15:11:03

--
-- PostgreSQL database dump complete
--

INSERT INTO apersona.provider (provider_id,provider_name,provider_url,key_timeout) VALUES (0,'Admin Provider','admin.com',200);

INSERT INTO apersona.roles(role_name) VALUES ('Admin'),('User');

INSERT INTO apersona.user(
            provider_id, email, email_hash, password, is_first_login, 
            is_pwd_reset, verification_code, created_on, is_verified, is_hint_set, 
            is_active, force_enhanced, verification_code_type, is_super_admin, 
            user_login_id, otp_sent_time)       
       VALUES (0,'superadmin@domain.com','-941740957','4c0bb193b5f00c2b9f9be81a490e903a',0,NULL,null,'2013-08-08 05:27:14',1,NULL,1,'N','',1,'superadmin@domain.com',null);

INSERT INTO apersona.user_roles(user_id, role_id, is_accessed) VALUES(1,1, null);

COMMIT;


