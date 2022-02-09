--
-- PostgreSQL database cluster dump
--

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE anonymous;
CREATE ROLE api;
CREATE ROLE webuser;


--
-- Role memberships
--

GRANT anonymous TO authenticator;
GRANT api TO current_user;
GRANT webuser TO authenticator;


--
-- PostgreSQL database cluster dump complete
--


--
-- PostgreSQL database dump
--

-- Dumped from database version 11.2 (Debian 11.2-1.pgdg90+1)
-- Dumped by pg_dump version 12.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: api; Type: SCHEMA; Schema: -; Owner: superuser
--

CREATE SCHEMA api;



--
-- Name: data; Type: SCHEMA; Schema: -; Owner: superuser
--

CREATE SCHEMA data;



--
-- Name: pgjwt; Type: SCHEMA; Schema: -; Owner: superuser
--

CREATE SCHEMA pgjwt;



--
-- Name: rabbitmq; Type: SCHEMA; Schema: -; Owner: superuser
--

CREATE SCHEMA rabbitmq;



--
-- Name: request; Type: SCHEMA; Schema: -; Owner: superuser
--

CREATE SCHEMA request;



--
-- Name: settings; Type: SCHEMA; Schema: -; Owner: superuser
--

CREATE SCHEMA settings;



--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--



--
-- Name: user_role; Type: TYPE; Schema: data; Owner: superuser
--

CREATE TYPE data.user_role AS ENUM (
    'webuser'
);



--
-- Name: login(text, text); Type: FUNCTION; Schema: api; Owner: superuser
--

CREATE FUNCTION api.login(email text, password text) RETURNS json
    LANGUAGE plpgsql STABLE SECURITY DEFINER
    AS $_$
declare
    usr record;
begin

	select * from data."user" as u
    where u.email = $1 and u.password = public.crypt($2, u.password)
   	INTO usr;

    if usr is NULL then
        raise exception 'invalid email/password';
    else
        
        return json_build_object(
            'me', json_build_object(
                'id', usr.id,
                'name', usr.name,
                'email', usr.email,
                'role', 'customer'
            ),
            'token', pgjwt.sign(
                json_build_object(
                    'role', usr.role,
                    'user_id', usr.id,
                    'exp', extract(epoch from now())::integer + settings.get('jwt_lifetime')::int -- token expires in 1 hour
                ),
                settings.get('jwt_secret')
            )
        );
    end if;
end
$_$;



--
-- Name: me(); Type: FUNCTION; Schema: api; Owner: superuser
--

CREATE FUNCTION api.me() RETURNS json
    LANGUAGE plpgsql STABLE SECURITY DEFINER
    AS $$
declare
    usr record;
begin

    select * from data."user"
    where id = request.user_id()
    into usr;

    return json_build_object(
        'id', usr.id, 
        'name', usr.name,
        'email', usr.email, 
        'role', usr.role
    );
end
$$;



--
-- Name: refresh_token(); Type: FUNCTION; Schema: api; Owner: superuser
--

CREATE FUNCTION api.refresh_token() RETURNS text
    LANGUAGE plpgsql STABLE SECURITY DEFINER
    AS $$
declare
    usr record;
    token text;
begin

    select * from data."user" as u
    where id = request.user_id()
    into usr;

    if usr is null then
        raise exception 'user not found';
    else
        token := pgjwt.sign(
            json_build_object(
                'role', usr.role,
                'user_id', usr.id,
                'exp', extract(epoch from now())::integer + settings.get('jwt_lifetime')::int -- token expires in 1 hour
            ),
            settings.get('jwt_secret')
        );
        return token;
    end if;
end
$$;



--
-- Name: signup(text, text, text); Type: FUNCTION; Schema: api; Owner: superuser
--

CREATE FUNCTION api.signup(name text, email text, password text) RETURNS json
    LANGUAGE plpgsql SECURITY DEFINER
    AS $_$
declare
    usr record;
begin
    insert into data."user" as u
    (name, email, password) values ($1, $2, $3)
    returning *
   	into usr;

    return json_build_object(
        'me', json_build_object(
            'id', usr.id,
            'name', usr.name,
            'email', usr.email,
            'role', 'customer'
        ),
        'token', pgjwt.sign(
            json_build_object(
                'role', usr.role,
                'user_id', usr.id,
                'exp', extract(epoch from now())::integer + settings.get('jwt_lifetime')::int -- token expires in 1 hour
            ),
            settings.get('jwt_secret')
        )
    );
end
$_$;



--
-- Name: encrypt_pass(); Type: FUNCTION; Schema: data; Owner: superuser
--

CREATE FUNCTION data.encrypt_pass() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
  if new.password is not null then
  	new.password = public.crypt(new.password, public.gen_salt('bf'));
  end if;
  return new;
end
$$;



--
-- Name: algorithm_sign(text, text, text); Type: FUNCTION; Schema: pgjwt; Owner: superuser
--

CREATE FUNCTION pgjwt.algorithm_sign(signables text, secret text, algorithm text) RETURNS text
    LANGUAGE sql
    AS $$
WITH
  alg AS (
    SELECT CASE
      WHEN algorithm = 'HS256' THEN 'sha256'
      WHEN algorithm = 'HS384' THEN 'sha384'
      WHEN algorithm = 'HS512' THEN 'sha512'
      ELSE '' END)  -- hmac throws error
SELECT pgjwt.url_encode(public.hmac(signables, secret, (select * FROM alg)));
$$;



--
-- Name: sign(json, text, text); Type: FUNCTION; Schema: pgjwt; Owner: superuser
--

CREATE FUNCTION pgjwt.sign(payload json, secret text, algorithm text DEFAULT 'HS256'::text) RETURNS text
    LANGUAGE sql
    AS $$
WITH
  header AS (
    SELECT pgjwt.url_encode(convert_to('{"alg":"' || algorithm || '","typ":"JWT"}', 'utf8'))
    ),
  payload AS (
    SELECT pgjwt.url_encode(convert_to(payload::text, 'utf8'))
    ),
  signables AS (
    SELECT (SELECT * FROM header) || '.' || (SELECT * FROM payload)
    )
SELECT
    (SELECT * FROM signables)
    || '.' ||
    pgjwt.algorithm_sign((SELECT * FROM signables), secret, algorithm);
$$;



--
-- Name: url_decode(text); Type: FUNCTION; Schema: pgjwt; Owner: superuser
--

CREATE FUNCTION pgjwt.url_decode(data text) RETURNS bytea
    LANGUAGE sql
    AS $$
WITH t AS (SELECT translate(data, '-_', '+/')),
     rem AS (SELECT length((SELECT * FROM t)) % 4) -- compute padding size
    SELECT decode(
        (SELECT * FROM t) ||
        CASE WHEN (SELECT * FROM rem) > 0
           THEN repeat('=', (4 - (SELECT * FROM rem)))
           ELSE '' END,
    'base64');
$$;



--
-- Name: url_encode(bytea); Type: FUNCTION; Schema: pgjwt; Owner: superuser
--

CREATE FUNCTION pgjwt.url_encode(data bytea) RETURNS text
    LANGUAGE sql
    AS $$
    SELECT translate(encode(data, 'base64'), E'+/=\n', '-_');
$$;



--
-- Name: verify(text, text, text); Type: FUNCTION; Schema: pgjwt; Owner: superuser
--

CREATE FUNCTION pgjwt.verify(token text, secret text, algorithm text DEFAULT 'HS256'::text) RETURNS TABLE(header json, payload json, valid boolean)
    LANGUAGE sql
    AS $$
  SELECT
    convert_from(pgjwt.url_decode(r[1]), 'utf8')::json AS header,
    convert_from(pgjwt.url_decode(r[2]), 'utf8')::json AS payload,
    r[3] = pgjwt.algorithm_sign(r[1] || '.' || r[2], secret, algorithm) AS valid
  FROM regexp_split_to_array(token, '\.') r;
$$;



--
-- Name: on_row_change(); Type: FUNCTION; Schema: rabbitmq; Owner: superuser
--

CREATE FUNCTION rabbitmq.on_row_change() RETURNS trigger
    LANGUAGE plpgsql STABLE
    AS $$
  declare
    routing_key text;
    row jsonb;
    config jsonb;
    excluded_columns text[];
    col text;
  begin
    routing_key := 'row_change'
                   '.table-'::text || TG_TABLE_NAME::text || 
                   '.event-'::text || TG_OP::text;
    if (TG_OP = 'DELETE') then
        row := row_to_json(old)::jsonb;
    elsif (TG_OP = 'UPDATE') then
        row := row_to_json(new)::jsonb;
    elsif (TG_OP = 'INSERT') then
        row := row_to_json(new)::jsonb;
    end if;

    -- decide what row columns to send based on the config parameter
    -- there is a 8000 byte hard limit on the payload size so sending many big columns is not possible
    if ( TG_NARGS = 1 ) then
      config := TG_ARGV[0];
      if (config ? 'include') then
          --excluded_columns := ARRAY(SELECT unnest(jsonb_object_keys(row)::text[]) EXCEPT SELECT unnest( array(select jsonb_array_elements_text(config->'include')) ));
          -- this is a diff between two arrays
          excluded_columns := array(
            -- array of all row columns
            select unnest(
              array(select jsonb_object_keys(row))
            ) 
            except
            -- array of included columns
            select unnest(
              array(select jsonb_array_elements_text(config->'include'))
            )
          );
      end if;

      if (config ? 'exclude') then
        excluded_columns := array(select jsonb_array_elements_text(config->'exclude'));
      end if;

      if (current_setting('server_version_num')::int >= 100000) then
          row := row - excluded_columns;
      else
          FOREACH col IN ARRAY excluded_columns
          LOOP
            row := row - col;
          END LOOP;
      end if;
    end if;
    
    perform rabbitmq.send_message('events', routing_key, row::text);
    return null;
  end;
$$;



--
-- Name: send_message(text, text, text); Type: FUNCTION; Schema: rabbitmq; Owner: superuser
--

CREATE FUNCTION rabbitmq.send_message(channel text, routing_key text, message text) RETURNS void
    LANGUAGE sql STABLE
    AS $$
     
  select  pg_notify(
    channel,  
    routing_key || '|' || message
  );
$$;



--
-- Name: cookie(text); Type: FUNCTION; Schema: request; Owner: superuser
--

CREATE FUNCTION request.cookie(c text) RETURNS text
    LANGUAGE sql STABLE
    AS $$
    select request.env_var('request.cookie.' || c);
$$;



--
-- Name: env_var(text); Type: FUNCTION; Schema: request; Owner: superuser
--

CREATE FUNCTION request.env_var(v text) RETURNS text
    LANGUAGE sql STABLE
    AS $$
    select current_setting(v, true);
$$;



--
-- Name: header(text); Type: FUNCTION; Schema: request; Owner: superuser
--

CREATE FUNCTION request.header(h text) RETURNS text
    LANGUAGE sql STABLE
    AS $$
    select request.env_var('request.header.' || h);
$$;



--
-- Name: jwt_claim(text); Type: FUNCTION; Schema: request; Owner: superuser
--

CREATE FUNCTION request.jwt_claim(c text) RETURNS text
    LANGUAGE sql STABLE
    AS $$
    select request.env_var('request.jwt.claim.' || c);
$$;



--
-- Name: user_id(); Type: FUNCTION; Schema: request; Owner: superuser
--

CREATE FUNCTION request.user_id() RETURNS integer
    LANGUAGE sql STABLE
    AS $$
    select 
    case coalesce(request.jwt_claim('user_id'),'')
    when '' then 0
    else request.jwt_claim('user_id')::int
	end
$$;



--
-- Name: user_role(); Type: FUNCTION; Schema: request; Owner: superuser
--

CREATE FUNCTION request.user_role() RETURNS text
    LANGUAGE sql STABLE
    AS $$
    select request.jwt_claim('role')::text;
$$;



--
-- Name: get(text); Type: FUNCTION; Schema: settings; Owner: superuser
--

CREATE FUNCTION settings.get(text) RETURNS text
    LANGUAGE sql STABLE SECURITY DEFINER
    AS $_$
    select value from settings.secrets where key = $1
$_$;



--
-- Name: set(text, text); Type: FUNCTION; Schema: settings; Owner: superuser
--

CREATE FUNCTION settings.set(text, text) RETURNS void
    LANGUAGE sql SECURITY DEFINER
    AS $_$
	insert into settings.secrets (key, value)
	values ($1, $2)
	on conflict (key) do update
	set value = $2;
$_$;



SET default_tablespace = '';

--
-- Name: atlanta_metro_area_tract; Type: TABLE; Schema: data; Owner: superuser
--

CREATE TABLE data.atlanta_metro_area_tract (
    id integer,
    filedate text,
    tractid text,
    countyfp10 text,
    totalfilings integer,
    indexid text NOT NULL,
    totalansweredfilings integer
);



--
-- Name: atlanta_metro_area_tracts; Type: VIEW; Schema: api; Owner: api
--

CREATE VIEW api.atlanta_metro_area_tracts AS
 SELECT atlanta_metro_area_tract.id,
    atlanta_metro_area_tract.filedate,
    atlanta_metro_area_tract.tractid,
    atlanta_metro_area_tract.countyfp10,
    atlanta_metro_area_tract.totalfilings,
    atlanta_metro_area_tract.totalansweredfilings,
    atlanta_metro_area_tract.indexid
   FROM data.atlanta_metro_area_tract;


ALTER TABLE api.atlanta_metro_area_tracts OWNER TO api;

--
-- Name: todo; Type: TABLE; Schema: data; Owner: superuser
--

CREATE TABLE data.todo (
    id integer NOT NULL,
    todo text NOT NULL,
    private boolean DEFAULT true,
    owner_id integer DEFAULT request.user_id()
);



--
-- Name: todos; Type: VIEW; Schema: api; Owner: api
--

CREATE VIEW api.todos AS
 SELECT todo.id,
    todo.todo,
    todo.private,
    (todo.owner_id = request.user_id()) AS mine
   FROM data.todo;


ALTER TABLE api.todos OWNER TO api;

--
-- Name: todo_id_seq; Type: SEQUENCE; Schema: data; Owner: superuser
--

CREATE SEQUENCE data.todo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: todo_id_seq; Type: SEQUENCE OWNED BY; Schema: data; Owner: superuser
--

ALTER SEQUENCE data.todo_id_seq OWNED BY data.todo.id;


--
-- Name: user; Type: TABLE; Schema: data; Owner: superuser
--

CREATE TABLE data."user" (
    id integer NOT NULL,
    name text NOT NULL,
    email text NOT NULL,
    password text NOT NULL,
    role data.user_role DEFAULT 'webuser'::data.user_role NOT NULL,
    CONSTRAINT user_email_check CHECK ((email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'::text)),
    CONSTRAINT user_name_check CHECK ((length(name) > 2))
);



--
-- Name: user_id_seq; Type: SEQUENCE; Schema: data; Owner: superuser
--

CREATE SEQUENCE data.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: data; Owner: superuser
--

ALTER SEQUENCE data.user_id_seq OWNED BY data."user".id;


--
-- Name: secrets; Type: TABLE; Schema: settings; Owner: superuser
--

CREATE TABLE settings.secrets (
    key text NOT NULL,
    value text NOT NULL
);



--
-- Name: todo id; Type: DEFAULT; Schema: data; Owner: superuser
--

ALTER TABLE ONLY data.todo ALTER COLUMN id SET DEFAULT nextval('data.todo_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: data; Owner: superuser
--

ALTER TABLE ONLY data."user" ALTER COLUMN id SET DEFAULT nextval('data.user_id_seq'::regclass);


--
-- Name: atlanta_metro_area_tract atlanta_metro_area_tract_pkey; Type: CONSTRAINT; Schema: data; Owner: superuser
--

ALTER TABLE ONLY data.atlanta_metro_area_tract
    ADD CONSTRAINT atlanta_metro_area_tract_pkey PRIMARY KEY (indexid);


--
-- Name: todo todo_pkey; Type: CONSTRAINT; Schema: data; Owner: superuser
--

ALTER TABLE ONLY data.todo
    ADD CONSTRAINT todo_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: data; Owner: superuser
--

ALTER TABLE ONLY data."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: data; Owner: superuser
--

ALTER TABLE ONLY data."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: secrets secrets_pkey; Type: CONSTRAINT; Schema: settings; Owner: superuser
--

ALTER TABLE ONLY settings.secrets
    ADD CONSTRAINT secrets_pkey PRIMARY KEY (key);


--
-- Name: todo send_todo_change_event; Type: TRIGGER; Schema: data; Owner: superuser
--

CREATE TRIGGER send_todo_change_event AFTER INSERT OR DELETE OR UPDATE ON data.todo FOR EACH ROW EXECUTE PROCEDURE rabbitmq.on_row_change('{"include":["id","todo"]}');


--
-- Name: user send_user_change_event; Type: TRIGGER; Schema: data; Owner: superuser
--

CREATE TRIGGER send_user_change_event AFTER INSERT OR DELETE OR UPDATE ON data."user" FOR EACH ROW EXECUTE PROCEDURE rabbitmq.on_row_change('{"include":["id","name","email","role"]}');


--
-- Name: user user_encrypt_pass_trigger; Type: TRIGGER; Schema: data; Owner: superuser
--

CREATE TRIGGER user_encrypt_pass_trigger BEFORE INSERT OR UPDATE ON data."user" FOR EACH ROW EXECUTE PROCEDURE data.encrypt_pass();


--
-- Name: todo todo_owner_id_fkey; Type: FK CONSTRAINT; Schema: data; Owner: superuser
--

ALTER TABLE ONLY data.todo
    ADD CONSTRAINT todo_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES data."user"(id);


--
-- Name: SCHEMA api; Type: ACL; Schema: -; Owner: superuser
--

GRANT USAGE ON SCHEMA api TO anonymous;
GRANT USAGE ON SCHEMA api TO webuser;


--
-- Name: SCHEMA rabbitmq; Type: ACL; Schema: -; Owner: superuser
--

GRANT USAGE ON SCHEMA rabbitmq TO PUBLIC;


--
-- Name: SCHEMA request; Type: ACL; Schema: -; Owner: superuser
--

GRANT USAGE ON SCHEMA request TO PUBLIC;


--
-- Name: FUNCTION login(email text, password text); Type: ACL; Schema: api; Owner: superuser
--

REVOKE ALL ON FUNCTION api.login(email text, password text) FROM PUBLIC;
GRANT ALL ON FUNCTION api.login(email text, password text) TO anonymous;
GRANT ALL ON FUNCTION api.login(email text, password text) TO webuser;


--
-- Name: FUNCTION me(); Type: ACL; Schema: api; Owner: superuser
--

REVOKE ALL ON FUNCTION api.me() FROM PUBLIC;
GRANT ALL ON FUNCTION api.me() TO webuser;


--
-- Name: FUNCTION refresh_token(); Type: ACL; Schema: api; Owner: superuser
--

REVOKE ALL ON FUNCTION api.refresh_token() FROM PUBLIC;
GRANT ALL ON FUNCTION api.refresh_token() TO webuser;


--
-- Name: FUNCTION signup(name text, email text, password text); Type: ACL; Schema: api; Owner: superuser
--

REVOKE ALL ON FUNCTION api.signup(name text, email text, password text) FROM PUBLIC;
GRANT ALL ON FUNCTION api.signup(name text, email text, password text) TO anonymous;


--
-- Name: TABLE atlanta_metro_area_tract; Type: ACL; Schema: data; Owner: superuser
--

GRANT SELECT ON TABLE data.atlanta_metro_area_tract TO api;


--
-- Name: TABLE atlanta_metro_area_tracts; Type: ACL; Schema: api; Owner: api
--

GRANT SELECT ON TABLE api.atlanta_metro_area_tracts TO anonymous;


--
-- PostgreSQL database dump complete
--

