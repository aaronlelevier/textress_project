--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: account_acctcost; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE account_acctcost (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    hotel_id integer NOT NULL,
    init_amt integer NOT NULL,
    balance_min integer NOT NULL,
    recharge_amt integer NOT NULL,
    CONSTRAINT account_acctcost_balance_min_62b462f02aba6586_check CHECK ((balance_min >= 0)),
    CONSTRAINT account_acctcost_balance_min_check CHECK ((balance_min >= 0)),
    CONSTRAINT account_acctcost_init_amt_check CHECK ((init_amt >= 0)),
    CONSTRAINT account_acctcost_recharge_amt_check CHECK ((recharge_amt >= 0))
);


ALTER TABLE public.account_acctcost OWNER TO postgres;

--
-- Name: account_acctcost_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE account_acctcost_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.account_acctcost_id_seq OWNER TO postgres;

--
-- Name: account_acctcost_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE account_acctcost_id_seq OWNED BY account_acctcost.id;


--
-- Name: account_acctstmt; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE account_acctstmt (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    hotel_id integer NOT NULL,
    year integer NOT NULL,
    month integer NOT NULL,
    monthly_costs double precision NOT NULL,
    total_sms integer NOT NULL,
    balance double precision NOT NULL
);


ALTER TABLE public.account_acctstmt OWNER TO postgres;

--
-- Name: account_acctstmt_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE account_acctstmt_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.account_acctstmt_id_seq OWNER TO postgres;

--
-- Name: account_acctstmt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE account_acctstmt_id_seq OWNED BY account_acctstmt.id;


--
-- Name: account_accttrans; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE account_accttrans (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    hotel_id integer NOT NULL,
    trans_type_id integer NOT NULL,
    amount double precision,
    sms_used integer,
    insert_date date
);


ALTER TABLE public.account_accttrans OWNER TO postgres;

--
-- Name: account_accttrans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE account_accttrans_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.account_accttrans_id_seq OWNER TO postgres;

--
-- Name: account_accttrans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE account_accttrans_id_seq OWNED BY account_accttrans.id;


--
-- Name: account_pricing; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE account_pricing (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    tier integer NOT NULL,
    tier_name character varying(55) NOT NULL,
    "desc" character varying(255) NOT NULL,
    price numeric(5,4) NOT NULL,
    start integer NOT NULL,
    "end" integer NOT NULL,
    CONSTRAINT account_pricing_end_check CHECK (("end" >= 0)),
    CONSTRAINT account_pricing_start_check CHECK ((start >= 0)),
    CONSTRAINT account_pricing_tier_check CHECK ((tier >= 0))
);


ALTER TABLE public.account_pricing OWNER TO postgres;

--
-- Name: account_pricing_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE account_pricing_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.account_pricing_id_seq OWNER TO postgres;

--
-- Name: account_pricing_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE account_pricing_id_seq OWNED BY account_pricing.id;


--
-- Name: account_transtype; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE account_transtype (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    name character varying(50) NOT NULL,
    "desc" character varying(255) NOT NULL
);


ALTER TABLE public.account_transtype OWNER TO postgres;

--
-- Name: account_transtype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE account_transtype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.account_transtype_id_seq OWNER TO postgres;

--
-- Name: account_transtype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE account_transtype_id_seq OWNED BY account_transtype.id;


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone NOT NULL,
    is_superuser boolean NOT NULL,
    username character varying(30) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(75) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO postgres;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO postgres;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO postgres;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_user_groups_id_seq OWNED BY auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO postgres;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO postgres;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO postgres;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_user_user_permissions_id_seq OWNED BY auth_user_user_permissions.id;


--
-- Name: authtoken_token; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE authtoken_token (
    key character varying(40) NOT NULL,
    created timestamp with time zone NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.authtoken_token OWNER TO postgres;

--
-- Name: concierge_guest; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE concierge_guest (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    hidden boolean NOT NULL,
    hotel_id integer NOT NULL,
    name character varying(110) NOT NULL,
    room_number character varying(10) NOT NULL,
    phone_number character varying(12) NOT NULL,
    check_in date NOT NULL,
    check_out date NOT NULL,
    confirmed boolean NOT NULL,
    stop boolean NOT NULL
);


ALTER TABLE public.concierge_guest OWNER TO postgres;

--
-- Name: concierge_guest_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE concierge_guest_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.concierge_guest_id_seq OWNER TO postgres;

--
-- Name: concierge_guest_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE concierge_guest_id_seq OWNED BY concierge_guest.id;


--
-- Name: concierge_message; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE concierge_message (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    hidden boolean NOT NULL,
    guest_id integer NOT NULL,
    user_id integer,
    hotel_id integer,
    sid character varying(55),
    received boolean,
    status character varying(25),
    to_ph character varying(12) NOT NULL,
    from_ph character varying(12) NOT NULL,
    body text NOT NULL,
    reason character varying(100),
    cost double precision,
    insert_date date,
    read boolean NOT NULL
);


ALTER TABLE public.concierge_message OWNER TO postgres;

--
-- Name: concierge_message_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE concierge_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.concierge_message_id_seq OWNER TO postgres;

--
-- Name: concierge_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE concierge_message_id_seq OWNED BY concierge_message.id;


--
-- Name: concierge_reply; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE concierge_reply (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    hidden boolean NOT NULL,
    hotel_id integer NOT NULL,
    letter character varying(25) NOT NULL,
    message character varying(320) NOT NULL,
    func_call character varying(100) NOT NULL
);


ALTER TABLE public.concierge_reply OWNER TO postgres;

--
-- Name: concierge_reply_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE concierge_reply_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.concierge_reply_id_seq OWNER TO postgres;

--
-- Name: concierge_reply_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE concierge_reply_id_seq OWNED BY concierge_reply.id;


--
-- Name: contact_contact; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE contact_contact (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    subject character varying(255) NOT NULL,
    message text NOT NULL
);


ALTER TABLE public.contact_contact OWNER TO postgres;

--
-- Name: contact_contact_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE contact_contact_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contact_contact_id_seq OWNER TO postgres;

--
-- Name: contact_contact_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE contact_contact_id_seq OWNED BY contact_contact.id;


--
-- Name: contact_newsletter; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE contact_newsletter (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    email character varying(100) NOT NULL
);


ALTER TABLE public.contact_newsletter OWNER TO postgres;

--
-- Name: contact_newsletter_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE contact_newsletter_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contact_newsletter_id_seq OWNER TO postgres;

--
-- Name: contact_newsletter_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE contact_newsletter_id_seq OWNED BY contact_newsletter.id;


--
-- Name: contact_qa; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE contact_qa (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    topic_id integer NOT NULL,
    question character varying(255) NOT NULL,
    answer character varying(1000) NOT NULL,
    "order" integer NOT NULL
);


ALTER TABLE public.contact_qa OWNER TO postgres;

--
-- Name: contact_qa_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE contact_qa_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contact_qa_id_seq OWNER TO postgres;

--
-- Name: contact_qa_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE contact_qa_id_seq OWNED BY contact_qa.id;


--
-- Name: contact_topic; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE contact_topic (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    name character varying(100) NOT NULL,
    fa_icon character varying(50) NOT NULL,
    slug character varying(100) NOT NULL,
    "order" integer NOT NULL
);


ALTER TABLE public.contact_topic OWNER TO postgres;

--
-- Name: contact_topic_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE contact_topic_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contact_topic_id_seq OWNER TO postgres;

--
-- Name: contact_topic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE contact_topic_id_seq OWNED BY contact_topic.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_flatpage; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE django_flatpage (
    id integer NOT NULL,
    url character varying(100) NOT NULL,
    title character varying(200) NOT NULL,
    content text NOT NULL,
    enable_comments boolean NOT NULL,
    template_name character varying(70) NOT NULL,
    registration_required boolean NOT NULL
);


ALTER TABLE public.django_flatpage OWNER TO postgres;

--
-- Name: django_flatpage_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_flatpage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_flatpage_id_seq OWNER TO postgres;

--
-- Name: django_flatpage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_flatpage_id_seq OWNED BY django_flatpage.id;


--
-- Name: django_flatpage_sites; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE django_flatpage_sites (
    id integer NOT NULL,
    flatpage_id integer NOT NULL,
    site_id integer NOT NULL
);


ALTER TABLE public.django_flatpage_sites OWNER TO postgres;

--
-- Name: django_flatpage_sites_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_flatpage_sites_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_flatpage_sites_id_seq OWNER TO postgres;

--
-- Name: django_flatpage_sites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_flatpage_sites_id_seq OWNED BY django_flatpage_sites.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_migrations_id_seq OWNED BY django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO postgres;

--
-- Name: django_site; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.django_site OWNER TO postgres;

--
-- Name: django_site_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_site_id_seq OWNER TO postgres;

--
-- Name: django_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;


--
-- Name: main_hotel; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE main_hotel (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    hidden boolean NOT NULL,
    name character varying(100) NOT NULL,
    address_phone character varying(12) NOT NULL,
    address_line1 character varying(100) NOT NULL,
    address_city character varying(100) NOT NULL,
    address_state character varying(25) NOT NULL,
    address_zip integer NOT NULL,
    address_line2 character varying(100) NOT NULL,
    hotel_type character varying(100) NOT NULL,
    rooms integer,
    slug character varying(125) NOT NULL,
    active boolean NOT NULL,
    customer_id character varying(100),
    admin_id integer,
    twilio_sid character varying(100) NOT NULL,
    twilio_auth_token character varying(100) NOT NULL,
    twilio_phone_number character varying(12) NOT NULL,
    twilio_ph_sid character varying(100) NOT NULL
);


ALTER TABLE public.main_hotel OWNER TO postgres;

--
-- Name: main_hotel_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE main_hotel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.main_hotel_id_seq OWNER TO postgres;

--
-- Name: main_hotel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE main_hotel_id_seq OWNED BY main_hotel.id;


--
-- Name: main_subaccount; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE main_subaccount (
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    hidden boolean NOT NULL,
    hotel_id integer NOT NULL,
    sid character varying(100) NOT NULL,
    auth_token character varying(100) NOT NULL,
    active boolean NOT NULL
);


ALTER TABLE public.main_subaccount OWNER TO postgres;

--
-- Name: main_userprofile; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE main_userprofile (
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    hidden boolean NOT NULL,
    user_id integer NOT NULL,
    hotel_id integer,
    msg_sign character varying(25) NOT NULL
);


ALTER TABLE public.main_userprofile OWNER TO postgres;

--
-- Name: payment_card; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE payment_card (
    short_pk character varying(10) NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    customer_id character varying(100) NOT NULL,
    id character varying(100) NOT NULL,
    brand character varying(25) NOT NULL,
    last4 integer NOT NULL,
    exp_month integer NOT NULL,
    exp_year integer NOT NULL,
    "default" boolean NOT NULL,
    expires character varying(10) NOT NULL,
    CONSTRAINT payment_card_exp_month_check CHECK ((exp_month >= 0)),
    CONSTRAINT payment_card_exp_year_check CHECK ((exp_year >= 0)),
    CONSTRAINT payment_card_last4_check CHECK ((last4 >= 0))
);


ALTER TABLE public.payment_card OWNER TO postgres;

--
-- Name: payment_charge; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE payment_charge (
    short_pk character varying(10) NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    card_id character varying(100) NOT NULL,
    customer_id character varying(100) NOT NULL,
    id character varying(100) NOT NULL,
    amount integer NOT NULL,
    CONSTRAINT payment_charge_amount_check CHECK ((amount >= 0))
);


ALTER TABLE public.payment_charge OWNER TO postgres;

--
-- Name: payment_customer; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE payment_customer (
    short_pk character varying(10) NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    id character varying(100) NOT NULL,
    email character varying(75) NOT NULL
);


ALTER TABLE public.payment_customer OWNER TO postgres;

--
-- Name: payment_refund; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE payment_refund (
    short_pk character varying(10) NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    charge_id character varying(100) NOT NULL,
    id character varying(100) NOT NULL,
    amount integer NOT NULL,
    CONSTRAINT payment_refund_amount_check CHECK ((amount >= 0))
);


ALTER TABLE public.payment_refund OWNER TO postgres;

--
-- Name: sms_democounter; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE sms_democounter (
    day date NOT NULL,
    count integer NOT NULL
);


ALTER TABLE public.sms_democounter OWNER TO postgres;

--
-- Name: sms_phonenumber; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE sms_phonenumber (
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    hotel_id integer NOT NULL,
    sid character varying(50) NOT NULL,
    phone_number character varying(12) NOT NULL,
    friendly_name character varying(14) NOT NULL,
    is_primary boolean NOT NULL
);


ALTER TABLE public.sms_phonenumber OWNER TO postgres;

--
-- Name: sms_text; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE sms_text (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    "to" character varying(12) NOT NULL,
    frm character varying(12) NOT NULL,
    body character varying(160) NOT NULL,
    sent boolean NOT NULL
);


ALTER TABLE public.sms_text OWNER TO postgres;

--
-- Name: sms_text_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE sms_text_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sms_text_id_seq OWNER TO postgres;

--
-- Name: sms_text_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE sms_text_id_seq OWNED BY sms_text.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_acctcost ALTER COLUMN id SET DEFAULT nextval('account_acctcost_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_acctstmt ALTER COLUMN id SET DEFAULT nextval('account_acctstmt_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_accttrans ALTER COLUMN id SET DEFAULT nextval('account_accttrans_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_pricing ALTER COLUMN id SET DEFAULT nextval('account_pricing_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_transtype ALTER COLUMN id SET DEFAULT nextval('account_transtype_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_groups ALTER COLUMN id SET DEFAULT nextval('auth_user_groups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY concierge_guest ALTER COLUMN id SET DEFAULT nextval('concierge_guest_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY concierge_message ALTER COLUMN id SET DEFAULT nextval('concierge_message_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY concierge_reply ALTER COLUMN id SET DEFAULT nextval('concierge_reply_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY contact_contact ALTER COLUMN id SET DEFAULT nextval('contact_contact_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY contact_newsletter ALTER COLUMN id SET DEFAULT nextval('contact_newsletter_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY contact_qa ALTER COLUMN id SET DEFAULT nextval('contact_qa_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY contact_topic ALTER COLUMN id SET DEFAULT nextval('contact_topic_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_flatpage ALTER COLUMN id SET DEFAULT nextval('django_flatpage_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_flatpage_sites ALTER COLUMN id SET DEFAULT nextval('django_flatpage_sites_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_migrations ALTER COLUMN id SET DEFAULT nextval('django_migrations_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY main_hotel ALTER COLUMN id SET DEFAULT nextval('main_hotel_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY sms_text ALTER COLUMN id SET DEFAULT nextval('sms_text_id_seq'::regclass);


--
-- Data for Name: account_acctcost; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY account_acctcost (id, created, modified, hotel_id, init_amt, balance_min, recharge_amt) FROM stdin;
1	2015-05-02 13:47:23.12724-07	2015-05-02 13:47:23.144825-07	2	1000	100	1000
\.


--
-- Name: account_acctcost_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('account_acctcost_id_seq', 1, true);


--
-- Data for Name: account_acctstmt; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY account_acctstmt (id, created, modified, hotel_id, year, month, monthly_costs, total_sms, balance) FROM stdin;
\.


--
-- Name: account_acctstmt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('account_acctstmt_id_seq', 1, false);


--
-- Data for Name: account_accttrans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY account_accttrans (id, created, modified, hotel_id, trans_type_id, amount, sms_used, insert_date) FROM stdin;
1	2015-05-04 07:36:23.284312-07	2015-05-04 07:36:23.284347-07	2	1	1000	0	2015-05-04
\.


--
-- Name: account_accttrans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('account_accttrans_id_seq', 1, true);


--
-- Data for Name: account_pricing; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY account_pricing (id, created, modified, tier, tier_name, "desc", price, start, "end") FROM stdin;
3	2015-03-02 06:45:12.537-08	2015-03-03 06:29:34.498-08	0	Free	up to 200 SMS per month	0.0000	0	200
4	2015-03-02 06:48:20.743-08	2015-03-03 06:31:18.514-08	1	0.0550	Next   2k SMS per month	0.0550	201	2200
5	2015-03-02 06:51:10.931-08	2015-03-03 06:32:48.126-08	2	0.0525	Next   4k SMS per month	0.0525	2201	6200
6	2015-03-02 06:52:40.543-08	2015-03-03 06:33:36.054-08	3	0.0495	Next   6k SMS per month	0.0495	6201	12200
7	2015-03-02 06:53:30.321-08	2015-03-03 06:34:09.219-08	4	0.0475	remaining SMS	0.0475	12201	999999999
\.


--
-- Name: account_pricing_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('account_pricing_id_seq', 7, true);


--
-- Data for Name: account_transtype; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY account_transtype (id, created, modified, name, "desc") FROM stdin;
1	2014-12-27 05:47:57.473-08	2015-01-04 17:13:18.378-08	init_amt	initial account funding
2	2014-12-27 05:53:19.757-08	2015-01-04 17:13:52.203-08	recharge_amt	Recharge amount selected by the Hotel
3	2014-12-27 05:54:02.052-08	2014-12-27 05:54:02.052-08	sms_used	daily deduction for sms used for that day; cache - sms used during the day to save DB trips
4	2015-01-04 15:28:28.339-08	2015-01-04 15:28:28.339-08	bulk_discount	credit applied from previous months use based on bulk
\.


--
-- Name: account_transtype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('account_transtype_id_seq', 4, true);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_group (id, name) FROM stdin;
1	hotel_admin
2	hotel_manager
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_group_id_seq', 2, true);


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
1	1	96
2	2	97
\.


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 2, true);


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can add permission	2	add_permission
5	Can change permission	2	change_permission
6	Can delete permission	2	delete_permission
7	Can add group	3	add_group
8	Can change group	3	change_group
9	Can delete group	3	delete_group
10	Can add user	4	add_user
11	Can change user	4	change_user
12	Can delete user	4	delete_user
13	Can add content type	5	add_contenttype
14	Can change content type	5	change_contenttype
15	Can delete content type	5	delete_contenttype
16	Can add session	6	add_session
17	Can change session	6	change_session
18	Can delete session	6	delete_session
19	Can add newsletter	7	add_newsletter
20	Can change newsletter	7	change_newsletter
21	Can delete newsletter	7	delete_newsletter
22	Can add site	8	add_site
23	Can change site	8	change_site
24	Can delete site	8	delete_site
25	Can add flat page	9	add_flatpage
26	Can change flat page	9	change_flatpage
27	Can delete flat page	9	delete_flatpage
28	Can add token	10	add_token
29	Can change token	10	change_token
30	Can delete token	10	delete_token
31	Can add hotel	11	add_hotel
32	Can change hotel	11	change_hotel
33	Can delete hotel	11	delete_hotel
34	Can add user profile	12	add_userprofile
35	Can change user profile	12	change_userprofile
36	Can delete user profile	12	delete_userprofile
37	hotel_admin	12	hotel_admin
38	hotel_manager	12	hotel_manager
39	Can add subaccount	13	add_subaccount
40	Can change subaccount	13	change_subaccount
41	Can delete subaccount	13	delete_subaccount
42	Can add contact	14	add_contact
43	Can change contact	14	change_contact
44	Can delete contact	14	delete_contact
45	Can add topic	15	add_topic
46	Can change topic	15	change_topic
47	Can delete topic	15	delete_topic
48	Can add QA	16	add_qa
49	Can change QA	16	change_qa
50	Can delete QA	16	delete_qa
51	Can add text	17	add_text
52	Can change text	17	change_text
53	Can delete text	17	delete_text
54	Can add demo counter	18	add_democounter
55	Can change demo counter	18	change_democounter
56	Can delete demo counter	18	delete_democounter
57	Can add phone number	19	add_phonenumber
58	Can change phone number	19	change_phonenumber
59	Can delete phone number	19	delete_phonenumber
60	Can add guest	20	add_guest
61	Can change guest	20	change_guest
62	Can delete guest	20	delete_guest
63	Can add message	21	add_message
64	Can change message	21	change_message
65	Can delete message	21	delete_message
66	Can add reply	22	add_reply
67	Can change reply	22	change_reply
68	Can delete reply	22	delete_reply
69	Can add pricing	23	add_pricing
70	Can change pricing	23	change_pricing
71	Can delete pricing	23	delete_pricing
72	Can add Transaction Type	24	add_transtype
73	Can change Transaction Type	24	change_transtype
74	Can delete Transaction Type	24	delete_transtype
75	Can add Account Cost	25	add_acctcost
76	Can change Account Cost	25	change_acctcost
77	Can delete Account Cost	25	delete_acctcost
78	Can add Account Statement	26	add_acctstmt
79	Can change Account Statement	26	change_acctstmt
80	Can delete Account Statement	26	delete_acctstmt
81	Can add Account Transaction	27	add_accttrans
82	Can change Account Transaction	27	change_accttrans
83	Can delete Account Transaction	27	delete_accttrans
84	Can add customer	28	add_customer
85	Can change customer	28	change_customer
86	Can delete customer	28	delete_customer
87	Can add card	29	add_card
88	Can change card	29	change_card
89	Can delete card	29	delete_card
90	Can add charge	30	add_charge
91	Can change charge	30	change_charge
92	Can delete charge	30	delete_charge
93	Can add refund	31	add_refund
94	Can change refund	31	change_refund
95	Can delete refund	31	delete_refund
96	hotel_admin	12	is_hotel_admin
97	hotel_manager	12	is_hotel_manager
\.


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_permission_id_seq', 97, true);


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
2	pbkdf2_sha256$15000$HxWnL4k7nhYV$GiTQwyrjO/TePZLr8DDYaFMsOOk8jJMAC++wYQSioeA=	2015-05-01 06:34:48.30963-07	f	Dave			pyaaron@gmail.com	f	t	2015-05-01 05:31:44.887657-07
3	pbkdf2_sha256$15000$LTAwruTyEihs$AEfhRK+goMw8tRQtlOZ5d6uMHMDjEc35V3RewoikpcU=	2015-05-02 15:53:11.217406-07	f	bobby	Aaron	Lelevier	aaron@textress.com	f	t	2015-05-02 10:39:31.83362-07
1	pbkdf2_sha256$15000$0SalGU7jbiXK$m2/n8lBisfb0NAgx5p9lqlIl+85EIaWXRGaHKh8OvJQ=	2015-05-17 08:29:05.415883-07	t	aaron			aaron@textress.com	t	t	2015-04-01 06:47:42.203315-07
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_user_groups (id, user_id, group_id) FROM stdin;
1	3	1
\.


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_user_groups_id_seq', 1, true);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_user_id_seq', 3, true);


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_user_user_permissions_id_seq', 1, false);


--
-- Data for Name: authtoken_token; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY authtoken_token (key, created, user_id) FROM stdin;
265ee7a6d516e5c2ebdff4b12734339953f554f3	2015-05-02 10:39:32.001263-07	3
\.


--
-- Data for Name: concierge_guest; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY concierge_guest (id, created, modified, hidden, hotel_id, name, room_number, phone_number, check_in, check_out, confirmed, stop) FROM stdin;
\.


--
-- Name: concierge_guest_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('concierge_guest_id_seq', 1, false);


--
-- Data for Name: concierge_message; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY concierge_message (id, created, modified, hidden, guest_id, user_id, hotel_id, sid, received, status, to_ph, from_ph, body, reason, cost, insert_date, read) FROM stdin;
\.


--
-- Name: concierge_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('concierge_message_id_seq', 1, false);


--
-- Data for Name: concierge_reply; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY concierge_reply (id, created, modified, hidden, hotel_id, letter, message, func_call) FROM stdin;
\.


--
-- Name: concierge_reply_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('concierge_reply_id_seq', 1, false);


--
-- Data for Name: contact_contact; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY contact_contact (id, created, name, email, subject, message) FROM stdin;
1	2015-05-17 08:06:48.590232-07	Aaron	pyaaron@gmail.com	hi	test
2	2015-05-17 08:14:32.266521-07	Aaron	pyaaron@gmail.com		hey
\.


--
-- Name: contact_contact_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('contact_contact_id_seq', 2, true);


--
-- Data for Name: contact_newsletter; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY contact_newsletter (id, created, email) FROM stdin;
20	2015-04-17 16:16:23.292279-07	pyaaron@gmail.com
21	2015-04-17 16:17:20.128714-07	aaron.yy.lelevier@gmail.com
22	2015-04-17 16:17:29.669619-07	aaron@textress.com
\.


--
-- Name: contact_newsletter_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('contact_newsletter_id_seq', 22, true);


--
-- Data for Name: contact_qa; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY contact_qa (id, created, modified, topic_id, question, answer, "order") FROM stdin;
14	2015-03-21 10:56:59.134-07	2015-05-17 11:14:47.992015-07	3	Can we automate responses?	Yes, you can automate welcome responses and thank you for staying responses. When guests sign up or are done using the service.	2
6	2015-03-21 10:56:59.123-07	2015-05-17 11:01:47.51272-07	1	Our Mission	To provide simple SMS solutions to businesses to improve guest service.	0
5	2015-03-21 10:56:59.121-07	2015-05-17 11:03:02.978921-07	1	Why did we start building SMS solutions?	We saw some existing SMS services, but they were lacking, and we wanted to improve them.	1
13	2015-03-21 10:56:59.133-07	2015-05-17 11:16:00.495314-07	3	Can employees have SMS signatures	Yes. You can enable or disable SMS signatures. You can use a generic SMS signature for you business, or unique based on the employee that is replying to the guest.	3
4	2015-03-21 10:56:59.113-07	2015-05-17 11:03:55.759384-07	1	When were we founded?	We were founded in 2014.	2
11	2015-03-21 10:56:59.13-07	2015-05-17 11:06:37.556193-07	2	How do I sign up?	At this time our product is still under development.  Please contact us to let you know that you are interested, and we're going to be giving extra benefits to our early adopters.	0
16	2015-03-21 10:56:59.137-07	2015-05-17 11:09:54.682462-07	3	What are some of the benefits?	Improved guest service. You can help your customers without them having to wait on the phone.  Once they give you their phone number, you will know who they are, and can get strait to helping them with what they need.	0
15	2015-03-21 10:56:59.135-07	2015-05-17 11:12:51.175567-07	3	How many SMS phone numbers to we have?	All SMS go to a central SMS number for your business.  Then any employee responsible for responding to guest requests can help.  The SMS phone number is a local phone number based on your business' area code.	1
20	2015-03-21 10:56:59.145-07	2015-05-17 11:20:17.068371-07	4	Ho does billing and renewal work?	Billing is done on a pay-as-you-go basis.  You would sign up for an initial amount of funds to deposit.  Then this balance will recharge when you hit the refill amount that you set for your account. 	0
25	2015-03-21 10:56:59.152-07	2015-05-17 11:22:21.804147-07	5	How to I get help if I have questions?	At this time, since the product is still under development, please contact us via email or phone.	0
\.


--
-- Name: contact_qa_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('contact_qa_id_seq', 26, true);


--
-- Data for Name: contact_topic; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY contact_topic (id, created, modified, name, fa_icon, slug, "order") FROM stdin;
1	2015-03-21 10:51:30.225-07	2015-03-21 14:24:31.45-07	About Textress	fa-bolt	about-textress	0
2	2015-03-21 10:54:19.33-07	2015-03-21 14:25:51.25-07	Getting the SMS Service	fa-exchange	getting-the-sms-service	0
3	2015-03-21 10:54:28.396-07	2015-03-21 14:26:57.133-07	Benefits of the SMS Service	fa-star	benefits-of-the-sms-service	0
4	2015-03-21 10:55:01.123-07	2015-03-21 14:26:02.342-07	Billing and Renewal	fa-money	billing-and-renewal	0
5	2015-03-21 10:55:07.5-07	2015-03-21 14:27:09.567-07	Support and Resources	fa-phone	support-and-resources	0
\.


--
-- Name: contact_topic_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('contact_topic_id_seq', 5, true);


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2015-05-01 05:51:51.149083-07	1	textress.com	2	Changed domain and name.	8	1
2	2015-05-17 11:00:50.146921-07	6	Our Mission	2	Changed order, question and answer.	16	1
3	2015-05-17 11:01:47.514385-07	6	Our Mission	2	Changed order.	16	1
4	2015-05-17 11:03:02.980496-07	5	Why did we start building SMS solutions?	2	Changed order, question and answer.	16	1
5	2015-05-17 11:03:45.756687-07	4	When were we founded?	2	Changed question and answer.	16	1
6	2015-05-17 11:03:55.763352-07	4	When were we founded?	2	Changed order.	16	1
7	2015-05-17 11:04:29.01459-07	3	ipsum laboris velit irure proident,	3		16	1
8	2015-05-17 11:04:38.623247-07	2	anim aliqua. sint velit magna	3		16	1
9	2015-05-17 11:04:45.566269-07	1	ut anim culpa non sunt	3		16	1
10	2015-05-17 11:06:37.557903-07	11	How do I sign up?	2	Changed question and answer.	16	1
11	2015-05-17 11:06:49.559107-07	10	deserunt ut Duis reprehenderit in	3		16	1
12	2015-05-17 11:06:57.166974-07	9	proident, anim ut dolor ut	3		16	1
13	2015-05-17 11:07:01.499736-07	8	Ut tempor exercitation cupidatat ea	3		16	1
14	2015-05-17 11:07:07.754069-07	7	occaecat cupidatat reprehenderit incididunt ea	3		16	1
15	2015-05-17 11:09:54.684502-07	16	What are some of the benefits?	2	Changed question and answer.	16	1
16	2015-05-17 11:12:51.177231-07	15	How many SMS phone numbers to we have?	2	Changed order, question and answer.	16	1
17	2015-05-17 11:14:47.99376-07	14	Can we automate responses?	2	Changed order, question and answer.	16	1
18	2015-05-17 11:16:00.497526-07	13	Can employees have SMS signatures	2	Changed order, question and answer.	16	1
19	2015-05-17 11:16:06.994925-07	12	veniam, et occaecat aliquip pariatur.	3		16	1
20	2015-05-17 11:17:49.270185-07	21	anim Lorem in elit, enim	3		16	1
21	2015-05-17 11:17:53.787337-07	19	incididunt amet, enim non in	3		16	1
22	2015-05-17 11:17:59.251884-07	17	irure Ut occaecat in nisi	3		16	1
23	2015-05-17 11:18:04.403553-07	18	Excepteur reprehenderit magna incididunt labore	3		16	1
24	2015-05-17 11:20:17.070038-07	20	Ho does billing and renewal work?	2	Changed question and answer.	16	1
25	2015-05-17 11:21:04.061953-07	26	veniam, fugiat sed incididunt dolor	3		16	1
26	2015-05-17 11:21:08.928429-07	23	exercitation sint consectetur aliquip ut	3		16	1
27	2015-05-17 11:21:13.220748-07	22	laboris pariatur. sint elit, aute	3		16	1
28	2015-05-17 11:21:16.904807-07	24	sint veniam, cillum labore exercitation	3		16	1
29	2015-05-17 11:22:21.805816-07	25	How to I get help if I have questions?	2	Changed question and answer.	16	1
\.


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 29, true);


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_content_type (id, name, app_label, model) FROM stdin;
1	log entry	admin	logentry
2	permission	auth	permission
3	group	auth	group
4	user	auth	user
5	content type	contenttypes	contenttype
6	session	sessions	session
7	newsletter	contact	newsletter
8	site	sites	site
9	flat page	flatpages	flatpage
10	token	authtoken	token
11	hotel	main	hotel
12	user profile	main	userprofile
13	subaccount	main	subaccount
14	contact	contact	contact
15	topic	contact	topic
16	QA	contact	qa
17	text	sms	text
18	demo counter	sms	democounter
19	phone number	sms	phonenumber
20	guest	concierge	guest
21	message	concierge	message
22	reply	concierge	reply
23	pricing	account	pricing
24	Transaction Type	account	transtype
25	Account Cost	account	acctcost
26	Account Statement	account	acctstmt
27	Account Transaction	account	accttrans
28	customer	payment	customer
29	card	payment	card
30	charge	payment	charge
31	refund	payment	refund
\.


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_content_type_id_seq', 31, true);


--
-- Data for Name: django_flatpage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_flatpage (id, url, title, content, enable_comments, template_name, registration_required) FROM stdin;
\.


--
-- Name: django_flatpage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_flatpage_id_seq', 1, false);


--
-- Data for Name: django_flatpage_sites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_flatpage_sites (id, flatpage_id, site_id) FROM stdin;
\.


--
-- Name: django_flatpage_sites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_flatpage_sites_id_seq', 1, false);


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2015-04-01 06:46:38.184436-07
2	auth	0001_initial	2015-04-01 06:46:38.272419-07
3	admin	0001_initial	2015-04-01 06:46:38.311007-07
4	contact	0001_initial	2015-04-01 06:46:38.323132-07
5	sessions	0001_initial	2015-04-01 06:46:38.338138-07
6	contact	0002_auto_20150401_0657	2015-04-01 06:57:27.199301-07
7	authtoken	0001_initial	2015-04-29 05:22:04.608275-07
8	sites	0001_initial	2015-04-29 05:22:04.689129-07
9	flatpages	0001_initial	2015-04-29 05:22:04.782678-07
10	account	0001_initial	2015-05-02 13:39:27.251687-07
11	account	0002_auto_20150505_0611	2015-05-05 06:11:35.839263-07
12	account	0003_auto_20150507_0600	2015-05-07 06:00:29.508956-07
\.


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_migrations_id_seq', 12, true);


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_session (session_key, session_data, expire_date) FROM stdin;
48q379ydn6nthsg8ddrmgh0peosjqccl	MGFlZmE2OTVjYTc2YTE0ODE0YjE2MmE2Zjk0NGNkZDZlZGVmZmZiYTp7Il9hdXRoX3VzZXJfaGFzaCI6IjRjNTVmMDMyOTI3ODI1MzEwOTljYWUzNjkwZjgxYmJlNGMwYmMzOTciLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZCIsIl9hdXRoX3VzZXJfaWQiOjF9	2015-05-19 06:01:24.997052-07
jdmxvgx01d7cuxyq62v1u0v75geil7s9	YzU4NTQ5NTdkMmE4NzIzYTFiNDdmNzE3ZGYyZTNhYWE4MDUyZWMwYjp7fQ==	2015-05-27 05:23:08.779094-07
ktq0d5hdmlvzg02j6p7xrkvbqi481fnu	ZjQ0YzM1NWNkZDUzYWUyYjU3MGFiNDA3NjAzMTRhNjlhNmEwN2ZmZDp7Il9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiNGM1NWYwMzI5Mjc4MjUzMTA5OWNhZTM2OTBmODFiYmU0YzBiYzM5NyIsIl9hdXRoX3VzZXJfaWQiOjF9	2015-04-16 03:47:17.565724-07
a5l0smx47w7ksnasirhby23je7j6cj46	MGFlZmE2OTVjYTc2YTE0ODE0YjE2MmE2Zjk0NGNkZDZlZGVmZmZiYTp7Il9hdXRoX3VzZXJfaGFzaCI6IjRjNTVmMDMyOTI3ODI1MzEwOTljYWUzNjkwZjgxYmJlNGMwYmMzOTciLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZCIsIl9hdXRoX3VzZXJfaWQiOjF9	2015-05-31 08:29:05.41813-07
g6a4bl4y8epev7mdalzuwam8sfrlwesa	Mjc0MDE5OTdjNmQyNjMxOWNhM2U0YTVkNTUxYzI0NGZiMmY0MmM0OTp7Il9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjE3MjA0M2QwNWJkMGNjNDM4NzI3NTcxYjQxMDA4ZTcyYTg3YTRiMyIsIl9hdXRoX3VzZXJfaWQiOjIsIl9tZXNzYWdlcyI6IltbXCJfX2pzb25fbWVzc2FnZVwiLDAsMzAsXCJObyBIb3RlbCBhc3NvY2lhdGVkIHdpdGggdGhpcyBhY2NvdW50LlwiXSxbXCJfX2pzb25fbWVzc2FnZVwiLDAsMzAsXCJObyBIb3RlbCBhc3NvY2lhdGVkIHdpdGggdGhpcyBhY2NvdW50LlwiXSxbXCJfX2pzb25fbWVzc2FnZVwiLDAsMzAsXCJObyBIb3RlbCBhc3NvY2lhdGVkIHdpdGggdGhpcyBhY2NvdW50LlwiXSxbXCJfX2pzb25fbWVzc2FnZVwiLDAsMzAsXCJObyBIb3RlbCBhc3NvY2lhdGVkIHdpdGggdGhpcyBhY2NvdW50LlwiXSxbXCJfX2pzb25fbWVzc2FnZVwiLDAsMzAsXCJObyBIb3RlbCBhc3NvY2lhdGVkIHdpdGggdGhpcyBhY2NvdW50LlwiXSxbXCJfX2pzb25fbWVzc2FnZVwiLDAsMzAsXCJObyBIb3RlbCBhc3NvY2lhdGVkIHdpdGggdGhpcyBhY2NvdW50LlwiXV0ifQ==	2015-05-15 06:31:22.206879-07
1habpflewcx7rc4fnq52h8oqzyc1b595	Y2QxNWEzODAxOTJiZjY2ZGI2Y2Y5OThiM2YzZGE4MjkyNTRiYWM5Mjp7Il9hdXRoX3VzZXJfaWQiOjIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjE3MjA0M2QwNWJkMGNjNDM4NzI3NTcxYjQxMDA4ZTcyYTg3YTRiMyJ9	2015-05-15 06:34:48.312499-07
d2ej78qt2kgims2pcvnor7sedduesk83	YzU4NTQ5NTdkMmE4NzIzYTFiNDdmNzE3ZGYyZTNhYWE4MDUyZWMwYjp7fQ==	2015-05-16 10:12:27.25661-07
8aa6ftpfzk99ey3n6ahdfo7v29rtc2qt	YzU4NTQ5NTdkMmE4NzIzYTFiNDdmNzE3ZGYyZTNhYWE4MDUyZWMwYjp7fQ==	2015-05-16 14:53:22.746525-07
\.


--
-- Data for Name: django_site; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_site (id, domain, name) FROM stdin;
1	textress.com	textress.com
\.


--
-- Name: django_site_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_site_id_seq', 1, true);


--
-- Data for Name: main_hotel; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY main_hotel (id, created, modified, hidden, name, address_phone, address_line1, address_city, address_state, address_zip, address_line2, hotel_type, rooms, slug, active, customer_id, admin_id, twilio_sid, twilio_auth_token, twilio_phone_number, twilio_ph_sid) FROM stdin;
2	2015-05-02 11:49:52.035111-07	2015-05-04 07:36:19.719254-07	f	bobby hotel	+17754194000	6121 Arlington Ash St.	Las Vegas	Alabama	89148			\N	bobby-hotel	t	cus_6B6tROALrJ4hfk	3	AC2dd62548feea9bfe24fa4331bf1b9df5	c07a4042c9585920e71369016d74f470		
\.


--
-- Name: main_hotel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('main_hotel_id_seq', 2, true);


--
-- Data for Name: main_subaccount; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY main_subaccount (created, modified, hidden, hotel_id, sid, auth_token, active) FROM stdin;
2015-05-04 06:52:40.339949-07	2015-05-04 07:36:23.268214-07	f	2	AC2dd62548feea9bfe24fa4331bf1b9df5	c07a4042c9585920e71369016d74f470	t
\.


--
-- Data for Name: main_userprofile; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY main_userprofile (created, modified, hidden, user_id, hotel_id, msg_sign) FROM stdin;
2015-05-01 05:31:44.946865-07	2015-05-01 05:31:44.946906-07	f	2	\N	-Dave
2015-05-02 10:39:32.006543-07	2015-05-02 11:49:52.114489-07	f	3	2	-AL
\.


--
-- Data for Name: payment_card; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY payment_card (short_pk, created, modified, customer_id, id, brand, last4, exp_month, exp_year, "default", expires) FROM stdin;
kKrsOhQgzU	2015-05-04 07:26:22.102676-07	2015-05-04 07:36:20.230425-07	cus_6B6jI40d93AiUm	card_15ykWJ2DyompLxkKrsOhQgzU	Visa	4242	12	2018	f	12 / 2018
kKwxyfUjpO	2015-05-04 07:18:10.470186-07	2015-05-04 07:36:20.240621-07	cus_6B6bZ1aKs5wOXQ	card_15ykON2DyompLxkKwxyfUjpO	Visa	4242	12	2018	f	12 / 2018
kK6CoBm9en	2015-05-04 07:17:20.918367-07	2015-05-04 07:36:20.24316-07	cus_6B6akNZmnWpQ9C	card_15ykNZ2DyompLxkK6CoBm9en	Visa	4242	12	2019	f	12 / 2019
kKffhIhDJi	2015-05-04 07:07:04.144029-07	2015-05-04 07:36:20.245171-07	cus_6B6QFcBD3g3vL3	card_15ykDd2DyompLxkKffhIhDJi	Visa	4242	12	2019	f	12 / 2019
kKMYXRiZQw	2015-05-04 05:26:32.595761-07	2015-05-04 07:36:20.246807-07	cus_6B4oF6rZSPqR5S	card_15yieL2DyompLxkKMYXRiZQw	Visa	4242	12	2018	f	12 / 2018
kKeodDU1ox	2015-05-04 05:25:10.71467-07	2015-05-04 07:36:20.248415-07	cus_6B4meKpa4hhe00	card_15yid12DyompLxkKeodDU1ox	Visa	4242	12	2018	f	12 / 2018
kKyde55tqn	2015-05-04 05:20:00.99692-07	2015-05-04 07:36:20.250016-07	cus_6B4hw7WdUBBOXa	card_15yiY12DyompLxkKyde55tqn	Visa	4242	12	2018	f	12 / 2018
kKFKbUkoXU	2015-05-04 07:36:20.849216-07	2015-05-04 07:36:20.849258-07	cus_6B6tROALrJ4hfk	card_15ykfx2DyompLxkKFKbUkoXU	Visa	4242	12	2019	t	12 / 2019
\.


--
-- Data for Name: payment_charge; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY payment_charge (short_pk, created, modified, card_id, customer_id, id, amount) FROM stdin;
kKmmp784zo	2015-05-04 07:07:05.813242-07	2015-05-04 07:07:05.81329-07	card_15ykDd2DyompLxkKffhIhDJi	cus_6B6QFcBD3g3vL3	ch_15ykDh2DyompLxkKmmp784zo	1000
kKNVDKslTW	2015-05-04 07:17:22.972538-07	2015-05-04 07:17:22.972597-07	card_15ykNZ2DyompLxkK6CoBm9en	cus_6B6akNZmnWpQ9C	ch_15ykNe2DyompLxkKNVDKslTW	1000
kKihSPQCkD	2015-05-04 07:18:11.843921-07	2015-05-04 07:18:11.843963-07	card_15ykON2DyompLxkKwxyfUjpO	cus_6B6bZ1aKs5wOXQ	ch_15ykOR2DyompLxkKihSPQCkD	1000
kK6X6HI522	2015-05-04 07:26:23.631766-07	2015-05-04 07:26:23.631825-07	card_15ykWJ2DyompLxkKrsOhQgzU	cus_6B6jI40d93AiUm	ch_15ykWN2DyompLxkK6X6HI522	1000
kK7jume0pc	2015-05-04 07:36:23.279124-07	2015-05-04 07:36:23.279182-07	card_15ykfx2DyompLxkKFKbUkoXU	cus_6B6tROALrJ4hfk	ch_15ykg22DyompLxkK7jume0pc	1000
\.


--
-- Data for Name: payment_customer; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY payment_customer (short_pk, created, modified, id, email) FROM stdin;
w7WdUBBOXa	2015-05-04 05:19:59.94324-07	2015-05-04 05:19:59.943294-07	cus_6B4hw7WdUBBOXa	pyaaron@gmail.com
eKpa4hhe00	2015-05-04 05:25:09.642758-07	2015-05-04 05:25:09.64282-07	cus_6B4meKpa4hhe00	pyaaron@gmail.com
F6rZSPqR5S	2015-05-04 05:26:31.579098-07	2015-05-04 05:26:31.579198-07	cus_6B4oF6rZSPqR5S	pyaaron@gmail.com
FcBD3g3vL3	2015-05-04 07:07:03.080478-07	2015-05-04 07:07:03.080606-07	cus_6B6QFcBD3g3vL3	pyaaron@gmail.com
kNZmnWpQ9C	2015-05-04 07:17:19.893552-07	2015-05-04 07:17:19.893645-07	cus_6B6akNZmnWpQ9C	pyaaron@gmail.com
Z1aKs5wOXQ	2015-05-04 07:18:09.371605-07	2015-05-04 07:18:09.371656-07	cus_6B6bZ1aKs5wOXQ	pyaaron@gmail.com
I40d93AiUm	2015-05-04 07:26:21.098318-07	2015-05-04 07:26:21.098377-07	cus_6B6jI40d93AiUm	pyaaron@gmail.com
ROALrJ4hfk	2015-05-04 07:36:19.708684-07	2015-05-04 07:36:19.708743-07	cus_6B6tROALrJ4hfk	pyaaron@gmail.com
\.


--
-- Data for Name: payment_refund; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY payment_refund (short_pk, created, modified, charge_id, id, amount) FROM stdin;
\.


--
-- Data for Name: sms_democounter; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY sms_democounter (day, count) FROM stdin;
\.


--
-- Data for Name: sms_phonenumber; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY sms_phonenumber (created, modified, hotel_id, sid, phone_number, friendly_name, is_primary) FROM stdin;
\.


--
-- Data for Name: sms_text; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY sms_text (id, created, "to", frm, body, sent) FROM stdin;
\.


--
-- Name: sms_text_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('sms_text_id_seq', 1, false);


--
-- Name: account_acctcost_hotel_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY account_acctcost
    ADD CONSTRAINT account_acctcost_hotel_id_key UNIQUE (hotel_id);


--
-- Name: account_acctcost_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY account_acctcost
    ADD CONSTRAINT account_acctcost_pkey PRIMARY KEY (id);


--
-- Name: account_acctstmt_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY account_acctstmt
    ADD CONSTRAINT account_acctstmt_pkey PRIMARY KEY (id);


--
-- Name: account_accttrans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY account_accttrans
    ADD CONSTRAINT account_accttrans_pkey PRIMARY KEY (id);


--
-- Name: account_pricing_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY account_pricing
    ADD CONSTRAINT account_pricing_pkey PRIMARY KEY (id);


--
-- Name: account_transtype_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY account_transtype
    ADD CONSTRAINT account_transtype_name_key UNIQUE (name);


--
-- Name: account_transtype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY account_transtype
    ADD CONSTRAINT account_transtype_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions_group_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_key UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_content_type_id_codename_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_key UNIQUE (content_type_id, codename);


--
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_user_id_group_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_key UNIQUE (user_id, group_id);


--
-- Name: auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_user_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_key UNIQUE (user_id, permission_id);


--
-- Name: auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: authtoken_token_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY authtoken_token
    ADD CONSTRAINT authtoken_token_pkey PRIMARY KEY (key);


--
-- Name: authtoken_token_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_key UNIQUE (user_id);


--
-- Name: concierge_guest_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY concierge_guest
    ADD CONSTRAINT concierge_guest_pkey PRIMARY KEY (id);


--
-- Name: concierge_message_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY concierge_message
    ADD CONSTRAINT concierge_message_pkey PRIMARY KEY (id);


--
-- Name: concierge_message_sid_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY concierge_message
    ADD CONSTRAINT concierge_message_sid_key UNIQUE (sid);


--
-- Name: concierge_reply_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY concierge_reply
    ADD CONSTRAINT concierge_reply_pkey PRIMARY KEY (id);


--
-- Name: contact_contact_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY contact_contact
    ADD CONSTRAINT contact_contact_pkey PRIMARY KEY (id);


--
-- Name: contact_newsletter_email_15d92eefa8356660_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY contact_newsletter
    ADD CONSTRAINT contact_newsletter_email_15d92eefa8356660_uniq UNIQUE (email);


--
-- Name: contact_newsletter_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY contact_newsletter
    ADD CONSTRAINT contact_newsletter_pkey PRIMARY KEY (id);


--
-- Name: contact_qa_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY contact_qa
    ADD CONSTRAINT contact_qa_pkey PRIMARY KEY (id);


--
-- Name: contact_topic_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY contact_topic
    ADD CONSTRAINT contact_topic_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_app_label_6ac580331e719e89_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_6ac580331e719e89_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_flatpage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_flatpage
    ADD CONSTRAINT django_flatpage_pkey PRIMARY KEY (id);


--
-- Name: django_flatpage_sites_flatpage_id_site_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_flatpage_sites
    ADD CONSTRAINT django_flatpage_sites_flatpage_id_site_id_key UNIQUE (flatpage_id, site_id);


--
-- Name: django_flatpage_sites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_flatpage_sites
    ADD CONSTRAINT django_flatpage_sites_pkey PRIMARY KEY (id);


--
-- Name: django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: django_site_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);


--
-- Name: main_hotel_admin_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY main_hotel
    ADD CONSTRAINT main_hotel_admin_id_key UNIQUE (admin_id);


--
-- Name: main_hotel_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY main_hotel
    ADD CONSTRAINT main_hotel_name_key UNIQUE (name);


--
-- Name: main_hotel_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY main_hotel
    ADD CONSTRAINT main_hotel_pkey PRIMARY KEY (id);


--
-- Name: main_hotel_slug_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY main_hotel
    ADD CONSTRAINT main_hotel_slug_key UNIQUE (slug);


--
-- Name: main_subaccount_hotel_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY main_subaccount
    ADD CONSTRAINT main_subaccount_hotel_id_key UNIQUE (hotel_id);


--
-- Name: main_subaccount_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY main_subaccount
    ADD CONSTRAINT main_subaccount_pkey PRIMARY KEY (sid);


--
-- Name: main_userprofile_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY main_userprofile
    ADD CONSTRAINT main_userprofile_pkey PRIMARY KEY (user_id);


--
-- Name: payment_card_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY payment_card
    ADD CONSTRAINT payment_card_pkey PRIMARY KEY (id);


--
-- Name: payment_charge_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY payment_charge
    ADD CONSTRAINT payment_charge_pkey PRIMARY KEY (id);


--
-- Name: payment_customer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY payment_customer
    ADD CONSTRAINT payment_customer_pkey PRIMARY KEY (id);


--
-- Name: payment_refund_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY payment_refund
    ADD CONSTRAINT payment_refund_pkey PRIMARY KEY (id);


--
-- Name: sms_democounter_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY sms_democounter
    ADD CONSTRAINT sms_democounter_pkey PRIMARY KEY (day);


--
-- Name: sms_phonenumber_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY sms_phonenumber
    ADD CONSTRAINT sms_phonenumber_pkey PRIMARY KEY (sid);


--
-- Name: sms_text_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY sms_text
    ADD CONSTRAINT sms_text_pkey PRIMARY KEY (id);


--
-- Name: account_acctstmt_hotel_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX account_acctstmt_hotel_id ON account_acctstmt USING btree (hotel_id);


--
-- Name: account_accttrans_hotel_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX account_accttrans_hotel_id ON account_accttrans USING btree (hotel_id);


--
-- Name: account_accttrans_trans_type_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX account_accttrans_trans_type_id ON account_accttrans USING btree (trans_type_id);


--
-- Name: account_transtype_name_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX account_transtype_name_like ON account_transtype USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_name_728c674fbb4159e8_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX auth_group_name_728c674fbb4159e8_like ON auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_0e939a4f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX auth_group_permissions_0e939a4f ON auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_8373b171; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX auth_group_permissions_8373b171 ON auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_417f1b1c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX auth_permission_417f1b1c ON auth_permission USING btree (content_type_id);


--
-- Name: auth_user_groups_0e939a4f; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX auth_user_groups_0e939a4f ON auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX auth_user_groups_e8701ad4 ON auth_user_groups USING btree (user_id);


--
-- Name: auth_user_user_permissions_8373b171; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX auth_user_user_permissions_8373b171 ON auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX auth_user_user_permissions_e8701ad4 ON auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_username_64f7704e0381c9fb_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX auth_user_username_64f7704e0381c9fb_like ON auth_user USING btree (username varchar_pattern_ops);


--
-- Name: authtoken_token_key_55f64d4a837896c3_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX authtoken_token_key_55f64d4a837896c3_like ON authtoken_token USING btree (key varchar_pattern_ops);


--
-- Name: concierge_guest_hotel_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX concierge_guest_hotel_id ON concierge_guest USING btree (hotel_id);


--
-- Name: concierge_guest_phone_number; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX concierge_guest_phone_number ON concierge_guest USING btree (phone_number);


--
-- Name: concierge_guest_phone_number_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX concierge_guest_phone_number_like ON concierge_guest USING btree (phone_number varchar_pattern_ops);


--
-- Name: concierge_message_guest_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX concierge_message_guest_id ON concierge_message USING btree (guest_id);


--
-- Name: concierge_message_hotel_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX concierge_message_hotel_id ON concierge_message USING btree (hotel_id);


--
-- Name: concierge_message_sid_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX concierge_message_sid_like ON concierge_message USING btree (sid varchar_pattern_ops);


--
-- Name: concierge_message_user_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX concierge_message_user_id ON concierge_message USING btree (user_id);


--
-- Name: concierge_reply_hotel_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX concierge_reply_hotel_id ON concierge_reply USING btree (hotel_id);


--
-- Name: contact_qa_topic_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX contact_qa_topic_id ON contact_qa USING btree (topic_id);


--
-- Name: contact_topic_slug; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX contact_topic_slug ON contact_topic USING btree (slug);


--
-- Name: contact_topic_slug_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX contact_topic_slug_like ON contact_topic USING btree (slug varchar_pattern_ops);


--
-- Name: django_admin_log_417f1b1c; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX django_admin_log_417f1b1c ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_e8701ad4; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX django_admin_log_e8701ad4 ON django_admin_log USING btree (user_id);


--
-- Name: django_flatpage_572d4e42; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX django_flatpage_572d4e42 ON django_flatpage USING btree (url);


--
-- Name: django_flatpage_sites_9365d6e7; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX django_flatpage_sites_9365d6e7 ON django_flatpage_sites USING btree (site_id);


--
-- Name: django_flatpage_sites_c3368d3a; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX django_flatpage_sites_c3368d3a ON django_flatpage_sites USING btree (flatpage_id);


--
-- Name: django_flatpage_url_6be20101eda4d28_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX django_flatpage_url_6be20101eda4d28_like ON django_flatpage USING btree (url varchar_pattern_ops);


--
-- Name: django_session_de54fa62; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX django_session_de54fa62 ON django_session USING btree (expire_date);


--
-- Name: django_session_session_key_685562ed42a47934_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX django_session_session_key_685562ed42a47934_like ON django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: main_hotel_customer_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX main_hotel_customer_id ON main_hotel USING btree (customer_id);


--
-- Name: main_hotel_customer_id_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX main_hotel_customer_id_like ON main_hotel USING btree (customer_id varchar_pattern_ops);


--
-- Name: main_hotel_name_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX main_hotel_name_like ON main_hotel USING btree (name varchar_pattern_ops);


--
-- Name: main_hotel_slug_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX main_hotel_slug_like ON main_hotel USING btree (slug varchar_pattern_ops);


--
-- Name: main_subaccount_sid_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX main_subaccount_sid_like ON main_subaccount USING btree (sid varchar_pattern_ops);


--
-- Name: main_userprofile_hotel_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX main_userprofile_hotel_id ON main_userprofile USING btree (hotel_id);


--
-- Name: payment_card_customer_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX payment_card_customer_id ON payment_card USING btree (customer_id);


--
-- Name: payment_card_customer_id_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX payment_card_customer_id_like ON payment_card USING btree (customer_id varchar_pattern_ops);


--
-- Name: payment_card_id_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX payment_card_id_like ON payment_card USING btree (id varchar_pattern_ops);


--
-- Name: payment_charge_card_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX payment_charge_card_id ON payment_charge USING btree (card_id);


--
-- Name: payment_charge_card_id_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX payment_charge_card_id_like ON payment_charge USING btree (card_id varchar_pattern_ops);


--
-- Name: payment_charge_customer_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX payment_charge_customer_id ON payment_charge USING btree (customer_id);


--
-- Name: payment_charge_customer_id_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX payment_charge_customer_id_like ON payment_charge USING btree (customer_id varchar_pattern_ops);


--
-- Name: payment_charge_id_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX payment_charge_id_like ON payment_charge USING btree (id varchar_pattern_ops);


--
-- Name: payment_customer_id_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX payment_customer_id_like ON payment_customer USING btree (id varchar_pattern_ops);


--
-- Name: payment_refund_charge_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX payment_refund_charge_id ON payment_refund USING btree (charge_id);


--
-- Name: payment_refund_charge_id_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX payment_refund_charge_id_like ON payment_refund USING btree (charge_id varchar_pattern_ops);


--
-- Name: payment_refund_id_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX payment_refund_id_like ON payment_refund USING btree (id varchar_pattern_ops);


--
-- Name: sms_phonenumber_hotel_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX sms_phonenumber_hotel_id ON sms_phonenumber USING btree (hotel_id);


--
-- Name: sms_phonenumber_sid_like; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX sms_phonenumber_sid_like ON sms_phonenumber USING btree (sid varchar_pattern_ops);


--
-- Name: account_acctcost_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_acctcost
    ADD CONSTRAINT account_acctcost_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES main_hotel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: account_acctstmt_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_acctstmt
    ADD CONSTRAINT account_acctstmt_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES main_hotel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: account_accttrans_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_accttrans
    ADD CONSTRAINT account_accttrans_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES main_hotel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: account_accttrans_trans_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account_accttrans
    ADD CONSTRAINT account_accttrans_trans_type_id_fkey FOREIGN KEY (trans_type_id) REFERENCES account_transtype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_content_type_id_1400cbbfc9aac33e_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_content_type_id_1400cbbfc9aac33e_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissio_group_id_11b94e905d9face5_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_group_id_11b94e905d9face5_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permission_id_5beab1e238abd910_fk_auth_permission_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permission_id_5beab1e238abd910_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user__permission_id_53cb557dd936e23f_fk_auth_permission_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user__permission_id_53cb557dd936e23f_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups_group_id_775b13eeabeafacd_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_775b13eeabeafacd_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups_user_id_d3fa46065e75f05_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_d3fa46065e75f05_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permiss_user_id_63261446c91546f4_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permiss_user_id_63261446c91546f4_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: authtoken_token_user_id_4b5e436b6bc61ac0_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_4b5e436b6bc61ac0_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: concierge_guest_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY concierge_guest
    ADD CONSTRAINT concierge_guest_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES main_hotel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: concierge_message_guest_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY concierge_message
    ADD CONSTRAINT concierge_message_guest_id_fkey FOREIGN KEY (guest_id) REFERENCES concierge_guest(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: concierge_message_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY concierge_message
    ADD CONSTRAINT concierge_message_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES main_hotel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: concierge_message_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY concierge_message
    ADD CONSTRAINT concierge_message_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: concierge_reply_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY concierge_reply
    ADD CONSTRAINT concierge_reply_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES main_hotel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: contact_qa_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY contact_qa
    ADD CONSTRAINT contact_qa_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES contact_topic(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: customer_id_refs_id_6377e9e6; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY main_hotel
    ADD CONSTRAINT customer_id_refs_id_6377e9e6 FOREIGN KEY (customer_id) REFERENCES payment_customer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: djan_content_type_id_2e3d8b3baa24b1f4_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT djan_content_type_id_2e3d8b3baa24b1f4_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_user_id_17fd463ac8f2f6ac_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_17fd463ac8f2f6ac_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_flatp_flatpage_id_4833186f8c3d9c38_fk_django_flatpage_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_flatpage_sites
    ADD CONSTRAINT django_flatp_flatpage_id_4833186f8c3d9c38_fk_django_flatpage_id FOREIGN KEY (flatpage_id) REFERENCES django_flatpage(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_flatpage_site_site_id_6c6bc601de0f8784_fk_django_site_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_flatpage_sites
    ADD CONSTRAINT django_flatpage_site_site_id_6c6bc601de0f8784_fk_django_site_id FOREIGN KEY (site_id) REFERENCES django_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_subaccount_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY main_subaccount
    ADD CONSTRAINT main_subaccount_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES main_hotel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_userprofile_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY main_userprofile
    ADD CONSTRAINT main_userprofile_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES main_hotel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_userprofile_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY main_userprofile
    ADD CONSTRAINT main_userprofile_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: payment_card_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY payment_card
    ADD CONSTRAINT payment_card_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES payment_customer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: payment_charge_card_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY payment_charge
    ADD CONSTRAINT payment_charge_card_id_fkey FOREIGN KEY (card_id) REFERENCES payment_card(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: payment_charge_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY payment_charge
    ADD CONSTRAINT payment_charge_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES payment_customer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: payment_refund_charge_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY payment_refund
    ADD CONSTRAINT payment_refund_charge_id_fkey FOREIGN KEY (charge_id) REFERENCES payment_charge(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sms_phonenumber_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY sms_phonenumber
    ADD CONSTRAINT sms_phonenumber_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES main_hotel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

