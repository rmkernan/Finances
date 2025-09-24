--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: tenants; Type: TABLE DATA; Schema: _realtime; Owner: supabase_admin
--

COPY _realtime.tenants (id, name, external_id, jwt_secret, max_concurrent_users, inserted_at, updated_at, max_events_per_second, postgres_cdc_default, max_bytes_per_second, max_channels_per_client, max_joins_per_second, suspend, jwt_jwks, notify_private_alpha, private_only, migrations_ran, broadcast_adapter, max_presence_events_per_second, max_payload_size_in_kb) FROM stdin;
fe0dcb5e-2d08-4cc5-b6b5-c3fd5de67a69	realtime-dev	realtime-dev	iNjicxc4+llvc9wovDvqymwfnj9teWMlyOIbJ8Fh6j2WNU8CIJ2ZgjR6MUIKqSmeDmvpsKLsZ9jgXJmQPpwL8w==	200	2025-09-23 00:33:37	2025-09-23 00:33:37	100	postgres_cdc_rls	100000	100	100	f	{"keys": [{"k": "c3VwZXItc2VjcmV0LWp3dC10b2tlbi13aXRoLWF0LWxlYXN0LTMyLWNoYXJhY3RlcnMtbG9uZw", "kty": "oct"}]}	f	f	63	gen_rpc	10000	3000
\.


--
-- Data for Name: extensions; Type: TABLE DATA; Schema: _realtime; Owner: supabase_admin
--

COPY _realtime.extensions (id, type, settings, tenant_external_id, inserted_at, updated_at) FROM stdin;
4160a57a-721c-48c6-b155-dda03bdb4dc8	postgres_cdc_rls	{"region": "us-east-1", "db_host": "ws1+KUnBysGEOPHISNWuK5dSFDPuG/xnyi3fsvUmKo4=", "db_name": "sWBpZNdjggEPTQVlI52Zfw==", "db_port": "+enMDFi1J/3IrrquHHwUmA==", "db_user": "uxbEq/zz8DXVD53TOI1zmw==", "slot_name": "supabase_realtime_replication_slot", "db_password": "sWBpZNdjggEPTQVlI52Zfw==", "publication": "supabase_realtime", "ssl_enforced": false, "poll_interval_ms": 100, "poll_max_changes": 100, "poll_max_record_bytes": 1048576}	realtime-dev	2025-09-23 00:33:37	2025-09-23 00:33:37
\.


--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: _realtime; Owner: supabase_admin
--

COPY _realtime.schema_migrations (version, inserted_at) FROM stdin;
20210706140551	2025-09-23 00:33:33
20220329161857	2025-09-23 00:33:33
20220410212326	2025-09-23 00:33:33
20220506102948	2025-09-23 00:33:33
20220527210857	2025-09-23 00:33:33
20220815211129	2025-09-23 00:33:33
20220815215024	2025-09-23 00:33:33
20220818141501	2025-09-23 00:33:33
20221018173709	2025-09-23 00:33:33
20221102172703	2025-09-23 00:33:33
20221223010058	2025-09-23 00:33:33
20230110180046	2025-09-23 00:33:33
20230810220907	2025-09-23 00:33:33
20230810220924	2025-09-23 00:33:33
20231024094642	2025-09-23 00:33:33
20240306114423	2025-09-23 00:33:33
20240418082835	2025-09-23 00:33:33
20240625211759	2025-09-23 00:33:33
20240704172020	2025-09-23 00:33:33
20240902173232	2025-09-23 00:33:33
20241106103258	2025-09-23 00:33:33
20250424203323	2025-09-23 00:33:33
20250613072131	2025-09-23 00:33:33
20250711044927	2025-09-23 00:33:33
20250811121559	2025-09-23 00:33:33
\.


--
-- Data for Name: audit_log_entries; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.audit_log_entries (instance_id, id, payload, created_at, ip_address) FROM stdin;
\.


--
-- Data for Name: flow_state; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.flow_state (id, user_id, auth_code, code_challenge_method, code_challenge, provider_type, provider_access_token, provider_refresh_token, created_at, updated_at, authentication_method, auth_code_issued_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.users (instance_id, id, aud, role, email, encrypted_password, email_confirmed_at, invited_at, confirmation_token, confirmation_sent_at, recovery_token, recovery_sent_at, email_change_token_new, email_change, email_change_sent_at, last_sign_in_at, raw_app_meta_data, raw_user_meta_data, is_super_admin, created_at, updated_at, phone, phone_confirmed_at, phone_change, phone_change_token, phone_change_sent_at, email_change_token_current, email_change_confirm_status, banned_until, reauthentication_token, reauthentication_sent_at, is_sso_user, deleted_at, is_anonymous) FROM stdin;
\.


--
-- Data for Name: identities; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.identities (provider_id, user_id, identity_data, provider, last_sign_in_at, created_at, updated_at, id) FROM stdin;
\.


--
-- Data for Name: instances; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.instances (id, uuid, raw_base_config, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.sessions (id, user_id, created_at, updated_at, factor_id, aal, not_after, refreshed_at, user_agent, ip, tag) FROM stdin;
\.


--
-- Data for Name: mfa_amr_claims; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.mfa_amr_claims (session_id, created_at, updated_at, authentication_method, id) FROM stdin;
\.


--
-- Data for Name: mfa_factors; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.mfa_factors (id, user_id, friendly_name, factor_type, status, created_at, updated_at, secret, phone, last_challenged_at, web_authn_credential, web_authn_aaguid) FROM stdin;
\.


--
-- Data for Name: mfa_challenges; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.mfa_challenges (id, factor_id, created_at, verified_at, ip_address, otp_code, web_authn_session_data) FROM stdin;
\.


--
-- Data for Name: one_time_tokens; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.one_time_tokens (id, user_id, token_type, token_hash, relates_to, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.refresh_tokens (instance_id, id, token, user_id, revoked, created_at, updated_at, parent, session_id) FROM stdin;
\.


--
-- Data for Name: sso_providers; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.sso_providers (id, resource_id, created_at, updated_at, disabled) FROM stdin;
\.


--
-- Data for Name: saml_providers; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.saml_providers (id, sso_provider_id, entity_id, metadata_xml, metadata_url, attribute_mapping, created_at, updated_at, name_id_format) FROM stdin;
\.


--
-- Data for Name: saml_relay_states; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.saml_relay_states (id, sso_provider_id, request_id, for_email, redirect_to, created_at, updated_at, flow_state_id) FROM stdin;
\.


--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.schema_migrations (version) FROM stdin;
20171026211738
20171026211808
20171026211834
20180103212743
20180108183307
20180119214651
20180125194653
00
20210710035447
20210722035447
20210730183235
20210909172000
20210927181326
20211122151130
20211124214934
20211202183645
20220114185221
20220114185340
20220224000811
20220323170000
20220429102000
20220531120530
20220614074223
20220811173540
20221003041349
20221003041400
20221011041400
20221020193600
20221021073300
20221021082433
20221027105023
20221114143122
20221114143410
20221125140132
20221208132122
20221215195500
20221215195800
20221215195900
20230116124310
20230116124412
20230131181311
20230322519590
20230402418590
20230411005111
20230508135423
20230523124323
20230818113222
20230914180801
20231027141322
20231114161723
20231117164230
20240115144230
20240214120130
20240306115329
20240314092811
20240427152123
20240612123726
20240729123726
20240802193726
20240806073726
20241009103726
20250717082212
\.


--
-- Data for Name: sso_domains; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

COPY auth.sso_domains (id, sso_provider_id, domain, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: entities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.entities (id, entity_name, entity_type, tax_id, tax_id_display, primary_taxpayer, tax_year_end, georgia_resident, entity_status, formation_date, notes, created_at, updated_at) FROM stdin;
11111111-1111-1111-1111-111111111111	Kernan Family	individual	2222	\N	Richard Michael Kernan	12-31	t	active	\N	\N	2025-09-23 20:33:56.339077+00	2025-09-23 20:33:56.339077+00
22222222-2222-2222-2222-222222222222	Milton Preschool Inc	s_corp	PLACEHOLDER_EIN_MILTON	\N	Milton Preschool Inc	12-31	t	active	\N	\N	2025-09-23 20:33:56.339077+00	2025-09-23 20:33:56.339077+00
\.


--
-- Data for Name: institutions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.institutions (id, institution_name, institution_type, status, notes, created_at, updated_at) FROM stdin;
33333333-3333-3333-3333-333333333333	Fidelity	brokerage	active	\N	2025-09-23 20:37:58.288132+00	2025-09-23 20:37:58.288132+00
\.


--
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts (id, entity_id, institution_id, account_number, account_number_display, account_holder_name, account_name, account_type, account_subtype, account_opening_date, account_status, is_tax_deferred, is_tax_free, requires_rmd, notes, created_at, updated_at, institution_name) FROM stdin;
44444444-4444-4444-4444-444444444444	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	Z24-527872	\N	RICHARD M KERNAN AND PEGGY E KERNAN	Joint Brokerage	brokerage	joint_taxable	\N	active	f	f	f	\N	2025-09-23 20:38:06.474942+00	2025-09-23 20:43:14.390034+00	Fidelity
55555555-5555-5555-5555-555555555555	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	Z27-375656	\N	RICHARD M KERNAN AND PEGGY E KERNAN	Cash Management Account	cash_management	joint_cash	\N	active	f	f	f	\N	2025-09-23 20:38:06.474942+00	2025-09-23 20:43:14.390034+00	Fidelity
66666666-6666-6666-6666-666666666666	22222222-2222-2222-2222-222222222222	33333333-3333-3333-3333-333333333333	Z40-394067	\N	MILTON PRESCHOOL INC	Brokerage Account	brokerage	corporate	\N	active	f	f	f	\N	2025-09-23 20:38:06.474942+00	2025-09-23 20:43:14.390034+00	Fidelity
\.


--
-- Data for Name: data_mappings_backup; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_mappings_backup (id, mapping_type, source_value, target_type, target_subtype, notes, created_at, updated_at) FROM stdin;
d6fb6611-ce6c-45cd-b7f6-38fda580ece3	transaction_descriptions	Dividend Received	dividend	received	Standard dividend payment	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
7bbe5b1a-5618-40bb-9997-22d6c59641fa	transaction_descriptions	Reinvestment	dividend	reinvestment	Dividend automatically reinvested into more shares	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
8497e081-d124-46b5-a882-b1130bb1f1b2	transaction_descriptions	Interest Earned	interest	deposit	Interest from FDIC insured bank deposits	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
ad86a51b-ed57-4ab7-a02a-0ce222ae10a8	transaction_descriptions	Muni Exempt Int	interest	muni_exempt	Tax-exempt municipal bond interest	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
9570e427-9e34-44e3-80a3-649b4d63be48	security_types	PUT	option	put	Put option contract	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
e729783a-1e3c-40e3-8dd1-6d4ea2ac3e80	security_types	CALL	option	call	Call option contract	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
fa69aa62-4799-43b6-8101-348b81632574	security_patterns	CLOSING TRANSACTION	override_subtype	closing_transaction	Options closing transaction - override subtype regardless of other mappings	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
fd6e1ead-d643-441b-9d78-ad5a02571d8f	security_patterns	OPENING TRANSACTION	override_subtype	opening_transaction	Options opening transaction - override subtype regardless of other mappings	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
d0af5d0f-07e9-4384-b576-b3e7e0aa8b97	security_patterns	ASSIGNED PUTS	override_subtype	assignment	Put option assignment - override subtype	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
dade9403-aa1b-4d0d-a3fa-8a4d856ea867	security_patterns	ASSIGNED CALLS	override_subtype	assignment	Call option assignment - override subtype	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
c0813cf5-e455-422c-88f9-10d0ccd7bc62	security_classification	CALL (	sec_class	call	Call options - security name starts with CALL (	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
c7ceee44-ac3c-4239-a63f-d6a0870e036e	security_classification	PUT (	sec_class	put	Put options - security name starts with PUT (	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
42321ec4-05e3-4570-a30d-e7defed87b5a	security_classification	ASSIGNED PUTS	sec_class	put	Assigned put options	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
01f3bfbc-afb4-4075-be0d-a5c149d8a522	security_classification	ASSIGNED CALLS	sec_class	call	Assigned call options	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
cf13767a-6a54-4299-bdf7-78bdc226f079	activity_sections	securities_bought_sold	trade	security	Stock, bond, and option trading transactions	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
e317f8e7-24c8-4d59-a39d-b7d48a744967	activity_sections	dividends_interest_income	income	investment	Dividend and interest income - requires description lookup	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
935c5407-aeb2-4529-a021-7ff6b783a341	activity_sections	deposits	transfer	deposit	Cash deposits into account	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
e578aa26-c6a2-4d33-ba04-df0277775add	activity_sections	withdrawals	transfer	withdrawal	Cash withdrawals from account	2025-09-23 23:14:40.472976+00	2025-09-23 23:14:40.472976+00
\.


--
-- Data for Name: documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.documents (id, institution_id, tax_year, document_type, period_start, period_end, file_path, file_name, file_size, doc_md5_hash, mime_type, is_amended, amends_document_id, version_number, portfolio_value, portfolio_value_with_ai, portfolio_change_period, portfolio_change_ytd, processed_at, processed_by, extraction_notes, is_archived, created_at, updated_at, imported_at, activities_loaded, activities_json_md5_hash, positions_loaded, positions_json_md5_hash) FROM stdin;
4297643c-91b0-4000-8252-97034c4d9898	33333333-3333-3333-3333-333333333333	2025	statement	2025-08-01	2025-08-31	/Users/richkernan/Projects/Finances/documents/5loaded/Fid_Stmnt_2025-08_KernBrok+KernCMA_activities_2025.09.24_11.35ET.json	Fid_Stmnt_2025-08_KernBrok+KernCMA.pdf	\N	32967b1d3e40b2c544cc42e0c6f378e5	application/pdf	f	\N	1	\N	\N	\N	\N	2025-09-24 16:17:23.36666+00	claude	{"extraction_type": "activities", "extraction_timestamp": "2024-09-24T11:35:00Z", "extractor_version": "1.0", "pages_processed": 36, "extraction_notes": [], "json_output_md5_hash": "557242c2c76b71cda1712c9140e56a7f"}	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:17:23.362174+00	2025-09-24 20:17:23.362174+00	2025-09-24 16:17:23.36666+00	df049a0efd7a790902c63c57996d7fdf	\N	\N
\.


--
-- Data for Name: doc_level_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.doc_level_data (id, document_id, account_id, account_number, doc_section, as_of_date, net_acct_value, beg_value, end_value, taxable_total_period, taxable_total_ytd, divs_taxable_period, divs_taxable_ytd, stcg_taxable_period, stcg_taxable_ytd, int_taxable_period, int_taxable_ytd, ltcg_taxable_period, ltcg_taxable_ytd, tax_exempt_total_period, tax_exempt_total_ytd, divs_tax_exempt_period, divs_tax_exempt_ytd, int_tax_exempt_period, int_tax_exempt_ytd, roc_period, roc_ytd, grand_total_period, grand_total_ytd, st_gain_period, st_loss_period, lt_gain_ytd, lt_loss_ytd, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: document_accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.document_accounts (document_id, account_id, created_at) FROM stdin;
4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-09-24 20:17:23.362174+00
4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-09-24 20:17:23.362174+00
\.


--
-- Data for Name: map_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.map_rules (id, rule_name, application_order, rule_category, problem_solved, created_at, updated_at) FROM stdin;
f06eb085-b30a-4ca2-83ce-fd10e9cab31e	Deposits Section	1	Section Fallbacks	Fallback classification when specific transaction patterns don't match	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
d2108add-ba75-44e4-bc2c-f3519bc46fc7	Securities Trading Section	1	Section Fallbacks	Fallback classification when specific transaction patterns don't match	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
cdf3e690-d283-429d-89fb-7f75d27d2511	Withdrawals Section	1	Section Fallbacks	Fallback classification when specific transaction patterns don't match	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
f5fc930c-91ec-44c8-928c-b7644594b6fa	Core Fund Activity Section	1	Section Fallbacks	Core fund transactions were unclassified causing loader failures	2025-09-24 20:06:43.196508+00	2025-09-24 20:06:43.196508+00
2c894c9e-e2b0-44d7-89b9-7a9fd8135465	Exchanges In Section	1	Section Fallbacks	Exchange/transfer transactions were unclassified causing loader failures	2025-09-24 20:06:57.378449+00	2025-09-24 20:06:57.378449+00
5beb05ea-3a11-42a1-984b-5ad5dc3589b2	Fees Charges Section	1	Section Fallbacks	Fee and charge transactions were unclassified causing loader failures	2025-09-24 20:07:10.484449+00	2025-09-24 20:07:10.484449+00
939f3887-e908-4942-80d4-1fbf84c50fda	Dividend Interest Income Section	1	Section Fallbacks	Fallback rule for dividends_interest_income section transactions	2025-09-24 20:15:05.253721+00	2025-09-24 20:15:05.253721+00
7a85354c-6028-4e70-9dc0-4017ded57464	Billpay Section	1	Section Fallbacks	Bill payment transactions fallback classification	2025-09-24 20:17:18.346473+00	2025-09-24 20:17:18.346473+00
c644d20f-843b-4e51-ab3b-68b16cb01ab5	Dividend Interest Section	20	Transaction Types	Fallback classification when specific transaction patterns don't match	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
5d0af098-bb6d-4de7-a731-19cb9b69432c	Dividend Received	20	Transaction Types	Generic income transactions needed precise categorization for tax forms	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
239a522a-7805-4096-9195-3c15579a9a86	Dividend Reinvestment	20	Transaction Types	Reinvested dividends weren't properly classified for cost basis tracking	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
5f992775-935f-46a8-9245-3337f721ce1c	Interest Earned	20	Transaction Types	Interest income was mixed with dividend income, causing tax reporting errors	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
66f6a087-9c2a-465d-bdac-737ff5d76ad6	Muni Bond Interest	20	Transaction Types	Municipal bonds in dividend section were taxed as dividends instead of tax-free interest	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
118ff942-d3fb-4dbd-93a7-8d659c00619b	Return of Capital	20	Transaction Types	Properly categorizes return of capital Transaction type	2025-09-24 19:10:35.183876+00	2025-09-24 19:10:35.183876+00
ccfb5158-af58-41b3-9e22-16f53023e9bd	Closing Call Transaction	30	Options Lifecycle	Options trades were classified as generic trades, preventing P&L matching	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
019ff693-ba2b-409e-9420-fc3cc0c54637	Closing Put Transaction	30	Options Lifecycle	Options trades were classified as generic trades, preventing P&L matching	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
9853db3f-5dba-401d-86e4-269276f934ae	Opening Call Transaction	30	Options Lifecycle	Options trades were classified as generic trades, preventing P&L matching	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
64875588-f37d-4a69-a202-71e9be8e7e02	Opening Put Transaction	30	Options Lifecycle	Options trades were classified as generic trades, preventing P&L matching	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
6a5e614b-f8f7-4780-9b8d-941bbe60bc80	Options Assignment - Calls	30	Options Lifecycle	Assigned options weren't distinguished from regular trades for tax reporting	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
4e7c3cc7-0259-4476-b1d0-566866410789	Options Assignment - Puts	30	Options Lifecycle	Assigned options weren't distinguished from regular trades for tax reporting	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
f8d10bea-4bde-4477-9c30-95f1e49f7003	Call Option Identifier	40	Security Identification	Options transactions couldn't be matched to opening/closing pairs for P&L analysis	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
af57b7e8-c8f0-44d1-98bf-b7c16c0bb635	Call Security Type	40	Security Identification	Basic security type classification for options	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
f57be46f-b7c2-499d-ae56-d79c2bda17fb	Put Option Identifier	40	Security Identification	Options transactions couldn't be matched to opening/closing pairs for P&L analysis	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
605ce171-7eed-4540-b083-852209324ea9	Put Security Type	40	Security Identification	Basic security type classification for options	2025-09-24 14:06:09.087336+00	2025-09-24 14:06:09.087336+00
\.


--
-- Data for Name: map_actions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.map_actions (id, rule_id, set_field, set_value) FROM stdin;
276304ea-b2b4-4723-93b0-686887c09790	f5fc930c-91ec-44c8-928c-b7644594b6fa	activities.transactiontype	fund_activity
c9e317c9-f200-4a6e-b571-d8b1514f1e7b	f5fc930c-91ec-44c8-928c-b7644594b6fa	activities.transactionsubtype	core_fund
53320e4a-f115-44a0-a72f-a57d074c99fc	5beb05ea-3a11-42a1-984b-5ad5dc3589b2	activities.transactiontype	fee
e2c3f01e-a18b-4a7c-8a30-76f9c6061be2	5beb05ea-3a11-42a1-984b-5ad5dc3589b2	activities.transactionsubtype	charge
3e57989a-554a-47da-bee1-b519f71a099b	7a85354c-6028-4e70-9dc0-4017ded57464	activities.transactiontype	payment
00178a55-939c-429c-9e4b-4a2be4789a6c	7a85354c-6028-4e70-9dc0-4017ded57464	activities.transactionsubtype	bill_payment
21d22c21-0abf-48c2-9a44-d951c224217c	ccfb5158-af58-41b3-9e22-16f53023e9bd	activities.sec_class	call
94980b8a-dc2e-4362-8a2e-7df782acde1c	019ff693-ba2b-409e-9420-fc3cc0c54637	activities.sec_class	put
a27b7e6b-fcb8-455d-9ab1-ff443e251f1a	9853db3f-5dba-401d-86e4-269276f934ae	activities.sec_class	call
6a49862b-8742-4e94-a8a0-b37a83c53bbf	64875588-f37d-4a69-a202-71e9be8e7e02	activities.sec_class	put
f7009796-2556-452b-833a-b0048672fec0	6a5e614b-f8f7-4780-9b8d-941bbe60bc80	activities.sec_class	call
503bdc93-3378-4d43-baaa-2347d5e470b8	4e7c3cc7-0259-4476-b1d0-566866410789	activities.sec_class	put
22636e98-e519-4298-bc14-2f18a1e5dbaa	f8d10bea-4bde-4477-9c30-95f1e49f7003	activities.sec_class	call
83686f35-dcae-446d-8b58-4e61daa9810a	f57be46f-b7c2-499d-ae56-d79c2bda17fb	activities.sec_class	put
4ec42f8f-3257-4651-88ce-8c5682df8b1e	118ff942-d3fb-4dbd-93a7-8d659c00619b	activities.transactiontype	return of capital
5395d3b7-8687-452e-a51c-4bf922ea01d7	c644d20f-843b-4e51-ab3b-68b16cb01ab5	activities.transactiontype	income
ecc378ba-c5f8-487d-87cf-377cb08f9527	5d0af098-bb6d-4de7-a731-19cb9b69432c	activities.transactiontype	dividend
2f035268-82b9-470e-98aa-ca40d0a618b0	239a522a-7805-4096-9195-3c15579a9a86	activities.transactiontype	dividend
2c7abbc1-e97f-4f77-bf0d-2a2f94794a48	5f992775-935f-46a8-9245-3337f721ce1c	activities.transactiontype	interest
da7ecf49-87c0-4d3a-928d-f3d48ada27ff	66f6a087-9c2a-465d-bdac-737ff5d76ad6	activities.transactiontype	interest
c025c2d0-e9fe-4347-a8b7-5f8d7630c203	af57b7e8-c8f0-44d1-98bf-b7c16c0bb635	activities.transactiontype	option
538b66f1-f828-43c3-98ef-9f2a078b1d32	605ce171-7eed-4540-b083-852209324ea9	activities.transactiontype	option
a4299a29-4ad3-47fc-9a45-174e8739cc96	f06eb085-b30a-4ca2-83ce-fd10e9cab31e	activities.transactiontype	transfer
2d200814-cd4f-458b-a583-1dcf829718d5	d2108add-ba75-44e4-bc2c-f3519bc46fc7	activities.transactiontype	trade
2cee03cf-ad65-4ff1-a49e-7afe1c521dae	cdf3e690-d283-429d-89fb-7f75d27d2511	activities.transactiontype	transfer
8cc488e3-00ec-40cf-adb0-51a58572edb9	ccfb5158-af58-41b3-9e22-16f53023e9bd	activities.transactionsubtype	closing_transaction
0f45e557-c1ba-4d89-887b-5f58e25d1cae	019ff693-ba2b-409e-9420-fc3cc0c54637	activities.transactionsubtype	closing_transaction
5ad70ba2-c847-42ef-ab87-bd638de33ddb	9853db3f-5dba-401d-86e4-269276f934ae	activities.transactionsubtype	opening_transaction
341f67f6-f780-4c1f-8042-46d07fbef153	64875588-f37d-4a69-a202-71e9be8e7e02	activities.transactionsubtype	opening_transaction
46806d59-5d72-428c-af68-5db6fbcc0200	6a5e614b-f8f7-4780-9b8d-941bbe60bc80	activities.transactionsubtype	assignment
18ebbab3-dc74-4a3f-a40a-e611e6b1b78e	4e7c3cc7-0259-4476-b1d0-566866410789	activities.transactionsubtype	assignment
d0d34729-5214-4286-a7ff-9344f0b6228f	c644d20f-843b-4e51-ab3b-68b16cb01ab5	activities.transactionsubtype	investment
18beb929-3fee-43b8-870f-6fe596953fd1	5d0af098-bb6d-4de7-a731-19cb9b69432c	activities.transactionsubtype	received
bae7cf0e-25ea-49e5-9641-b13d09eb7620	239a522a-7805-4096-9195-3c15579a9a86	activities.transactionsubtype	reinvestment
d7c740b6-7c54-4a53-8b1a-1a0aeb03703b	5f992775-935f-46a8-9245-3337f721ce1c	activities.transactionsubtype	deposit
237b7f37-1752-4ff7-a118-f66397989446	66f6a087-9c2a-465d-bdac-737ff5d76ad6	activities.transactionsubtype	muni_exempt
e87a47a0-9ca9-49f1-85f0-0c61ec198c87	af57b7e8-c8f0-44d1-98bf-b7c16c0bb635	activities.transactionsubtype	call
2fc98d2a-cb8b-4100-bddb-af52758f5b62	605ce171-7eed-4540-b083-852209324ea9	activities.transactionsubtype	put
941280d0-1d9e-43e8-884b-c555f185155e	f06eb085-b30a-4ca2-83ce-fd10e9cab31e	activities.transactionsubtype	deposit
688ac89e-1f85-4b92-a95f-734e21d2d6c4	d2108add-ba75-44e4-bc2c-f3519bc46fc7	activities.transactionsubtype	security
98a5a858-fbd6-4876-8660-649a36052797	cdf3e690-d283-429d-89fb-7f75d27d2511	activities.transactionsubtype	withdrawal
80bb9d02-7cd7-447b-852d-1603edcac869	2c894c9e-e2b0-44d7-89b9-7a9fd8135465	activities.transactiontype	transfer
8bb4509a-d46c-47ab-b2b6-36534a0f9537	2c894c9e-e2b0-44d7-89b9-7a9fd8135465	activities.transactionsubtype	exchange_in
f0ab8a26-acba-4e98-839a-79a8704aff8b	939f3887-e908-4942-80d4-1fbf84c50fda	activities.transactiontype	income
a2a89442-f234-4597-99e4-00c7858b9380	939f3887-e908-4942-80d4-1fbf84c50fda	activities.transactionsubtype	investment
\.


--
-- Data for Name: map_conditions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.map_conditions (id, rule_id, check_field, match_operator, match_value, logic_connector) FROM stdin;
ab77eb4b-4e56-409f-960b-b4c698455a78	ccfb5158-af58-41b3-9e22-16f53023e9bd	activities.description	contains	CLOSING TRANSACTION	AND
0c2a8e62-e142-409a-bc5d-55040a38ffda	ccfb5158-af58-41b3-9e22-16f53023e9bd	activities.description	contains	CALL	AND
6dd21c37-ae29-4b7a-bb51-9d4295d1a416	019ff693-ba2b-409e-9420-fc3cc0c54637	activities.description	contains	CLOSING TRANSACTION	AND
8055c040-584d-431a-b7c2-526892bf3797	019ff693-ba2b-409e-9420-fc3cc0c54637	activities.description	contains	PUT	AND
04feef31-7e18-4eb5-a7bc-3430cc8fadd6	9853db3f-5dba-401d-86e4-269276f934ae	activities.description	contains	OPENING TRANSACTION	AND
5a387f37-c5f7-444e-9005-1ede8ff22872	9853db3f-5dba-401d-86e4-269276f934ae	activities.description	contains	CALL	AND
5ded412e-e9ae-4c6b-b0c3-953a55c721e0	64875588-f37d-4a69-a202-71e9be8e7e02	activities.description	contains	OPENING TRANSACTION	AND
89afdaf2-5b59-4cb9-9e3d-96a2938b5d9a	64875588-f37d-4a69-a202-71e9be8e7e02	activities.description	contains	PUT	AND
3cac5b98-9f00-44e5-a3fa-9d100f745421	6a5e614b-f8f7-4780-9b8d-941bbe60bc80	activities.description	contains	ASSIGNED CALLS	AND
a3f7f7eb-2f31-4252-bea6-437da11ca249	4e7c3cc7-0259-4476-b1d0-566866410789	activities.description	contains	ASSIGNED PUTS	AND
8d5fa018-293d-4608-b9b4-ba2f0c9d99c5	c644d20f-843b-4e51-ab3b-68b16cb01ab5	activities.section	equals	dividends_interest_income	AND
0164595c-a83c-4fc7-99d7-7d69e890ec01	5d0af098-bb6d-4de7-a731-19cb9b69432c	activities.description	contains	Dividend Received	AND
1e21531a-21aa-4dd7-870a-562991d763ad	239a522a-7805-4096-9195-3c15579a9a86	activities.description	contains	Reinvestment	AND
ec6da154-c743-4dd1-bdc7-e16c35e94cf7	5f992775-935f-46a8-9245-3337f721ce1c	activities.description	contains	Interest Earned	AND
ba10180c-41e4-427f-ac16-a76eb7c52e0b	66f6a087-9c2a-465d-bdac-737ff5d76ad6	activities.description	contains	Muni Exempt Int	AND
e2065779-c27e-4e38-97ce-1a06257c3f82	66f6a087-9c2a-465d-bdac-737ff5d76ad6	activities.section	equals	dividends_interest_income	AND
2cd7c2de-9b6c-4777-9cfb-63181777848c	f8d10bea-4bde-4477-9c30-95f1e49f7003	activities.description	contains	CALL (	AND
a287d984-e3f1-4fc3-92ee-83cca28eee05	f8d10bea-4bde-4477-9c30-95f1e49f7003	activities.security	contains	CALL (	OR
1bdb211b-12e7-4db2-9fba-298390ee0953	af57b7e8-c8f0-44d1-98bf-b7c16c0bb635	activities.security	contains	CALL	AND
b4dac44d-1e45-477b-a169-78111aae088c	f57be46f-b7c2-499d-ae56-d79c2bda17fb	activities.description	contains	PUT (	AND
73bf3d87-7065-4cad-87d1-39ff3ea28419	f57be46f-b7c2-499d-ae56-d79c2bda17fb	activities.security	contains	PUT (	OR
16cd5dc7-12dc-441c-a524-b2016dfd848d	605ce171-7eed-4540-b083-852209324ea9	activities.security	contains	PUT	AND
3228883d-eba6-41b2-ac1c-27145e80ca0f	f06eb085-b30a-4ca2-83ce-fd10e9cab31e	activities.section	equals	deposits	AND
4dbde6d0-f26d-42b3-906a-34fcf23890ce	d2108add-ba75-44e4-bc2c-f3519bc46fc7	activities.section	equals	securities_bought_sold	AND
dd8e7456-bd13-46f4-86f9-d82655d97344	cdf3e690-d283-429d-89fb-7f75d27d2511	activities.section	equals	withdrawals	AND
acc011a6-1a8d-40a0-8eae-47f393b509f3	118ff942-d3fb-4dbd-93a7-8d659c00619b	activities.source	equals	other_activity_in	AND
e802a8b6-a5bb-4f31-b6f7-d443c3dfd970	118ff942-d3fb-4dbd-93a7-8d659c00619b	activities.description	contains	Return Of Capital	AND
13765c5f-f29f-4ce6-bc92-6a076bf1fd46	f5fc930c-91ec-44c8-928c-b7644594b6fa	activities.section	equals	core_fund_activity	AND
ad00bd4f-f17f-4aa8-a259-1af58c7d7da8	2c894c9e-e2b0-44d7-89b9-7a9fd8135465	activities.section	equals	exchanges_in	AND
10730437-8e01-45bf-abd0-48d792f30a2e	5beb05ea-3a11-42a1-984b-5ad5dc3589b2	activities.section	equals	fees_charges	AND
8fe50433-8fe4-4e7e-9d72-058be75665bc	939f3887-e908-4942-80d4-1fbf84c50fda	activities.section	equals	dividends_interest_income	AND
d5d24348-b96f-4e22-a8b8-4718c050891a	7a85354c-6028-4e70-9dc0-4017ded57464	activities.section	equals	billpay	AND
\.


--
-- Data for Name: positions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.positions (id, document_id, account_id, entity_id, position_date, account_number, sec_ticker, cusip, sec_name, sec_type, sec_subtype, beg_market_value, quantity, price, end_market_value, cost_basis, unrealized_gain_loss, estimated_ann_inc, est_yield, underlying_symbol, strike_price, exp_date, option_type, maturity_date, coupon_rate, accrued_int, agency_ratings, next_call_date, call_price, payment_freq, bond_features, is_margin, is_short, created_at, updated_at, source, source_file, json_output_md5_hash) FROM stdin;
\.


--
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.transactions (id, entity_id, document_id, account_id, transaction_date, settlement_date, transaction_type, transaction_subtype, description, amount, security_name, security_identifier, sec_cusip, quantity, price_per_unit, cost_basis, fees, security_type, option_type, strike_price, expiration_date, underlying_symbol, option_details, bond_state, dividend_qualified, bond_details, source, reference_number, payee, payee_account, ytd_amount, balance, account_type, tax_category, federal_taxable, state_taxable, tax_details, source_transaction_id, source_reference, related_transaction_id, is_duplicate_of, duplicate_reason, is_archived, created_at, updated_at, processed_by, sec_class, source_file, json_output_md5_hash) FROM stdin;
1e6310aa-96c9-4aa2-a2fd-032a22f44205	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-01	2025-08-01	dividend	received	Dividend Received	110.25	PIMCO DYNAMIC INCOME FD COM USD0.00001	PDI	72201Y101	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
1977104c-7798-4006-af2a-6fe5a736d543	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-01	2025-08-01	dividend	received	Dividend Received	660.78	AT&T INC COM USD1	T	00206R102	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
d564ce7f-76c3-4394-a1dc-44f6a2450bb8	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-01	2025-08-01	interest	muni_exempt	Muni Exempt Int	1250.00	GLYNN-BRUNSWICK MEM HOSP AUTH GA REV REV 05.00000% 08/01/2026 ANTIC CTFS SOUTHEAST GEORGIA HEALTH SYSTEM INC SOUTHEAST	\N	380037FU0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
8bcc6202-e8cb-4a8b-bb4f-2c10124ec295	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-01	2025-08-01	dividend	received	Dividend Received	54.00	NUVEEN CR STRATEGIES INCOME FD COM SHS	JQC	67073D102	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
62bc5e25-c2b2-4345-9ed5-6815006deb95	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-01	2025-08-01	dividend	received	Dividend Received	182.62	NUVEEN MUNICIPAL CREDIT INC FD COM SH BEN INT	NZF	67070X101	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
6cf56f90-a06c-4c6b-af4c-54d11d669198	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-01	2025-08-01	dividend	received	Dividend Received	0.23	NUVEEN MUNICIPAL CREDIT INC FD COM SH BEN INT SUBSTITUTE PAYMENT	NZF	67070X101	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
90cbd3d4-cf86-4924-9d6d-156ecd21f455	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-06	2025-08-06	dividend	received	Dividend Received	239.22	BRITISH AMERICAN TOBACCO LVL II ADR EACH REP 1 ORD GBP0.25 BNY	BTI	110448107	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
d6930150-e3d8-4220-ada8-acc2329c7947	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-08	2025-08-08	dividend	received	Dividend Received	113.29	TIDAL TR II YIELDMAX TSLA OP	TSLY	88636J444	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
f37920e9-272c-4b3b-8c9e-df5cefe3e064	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-08	2025-08-08	option	call	Muni Exempt Int	115.28	WISCONSIN ST HEALTH & EDL FACS AUTH REV 05.00000% 11/15/2027 FULL CALL PAYOUT #REOR R6006628610000	\N	97712DHL3	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
f5de23cb-69d3-4012-9210-c30a1cfb2301	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	interest	muni_exempt	Muni Exempt Int	1250.00	CLIFTON TEX HIGHER ED FIN CORP ED REV 05.00000% 08/15/2025 REV BDS IDEA PUB SCH SER. 2016 B	\N	187145GB7	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
2834b0b1-bb72-45b2-9082-900089c95045	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	interest	muni_exempt	Muni Exempt Int	500.00	DALTON WHITFIELD CNTY GA JT DEV AUTH 05.00000% 08/15/2031 REV BDS HAMILTON HEALTH CARE SYS INC HAMILTON HELATH CARE	\N	235641AC1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
0e9e4ed6-9674-4805-a3a9-10a9b02ac8b6	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	interest	muni_exempt	Muni Exempt Int	1500.00	GAINESVILLE & HALL CNTY GA HOSP AUTH 05.00000% 02/15/2037 REV ANTIC CTFS REV ANTIC CTFS NORTHEAST GEORGIA HLTH SYS INC	\N	362762LR5	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
b9600586-04de-4a3b-b1c1-b386e6f633c5	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	interest	muni_exempt	Muni Exempt Int	250.00	GAINESVILLE & HALL CNTY GA HOSP AUTH 05.00000% 02/15/2027 REV ANTIC CTFS CTFS NORTHEAST GEORGIA HLTH SYS INC SER.	\N	362762PX8	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
5fbbb55d-7fa4-46a9-a7aa-50053e276cb3	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	interest	muni_exempt	Muni Exempt Int	1000.00	LAGO VISTA TEX GO REF BDS SER. 2015 04.00000% 02/15/2027	\N	507071JC3	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
4d115d77-a134-43cb-a07b-6961be2b6c47	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	interest	muni_exempt	Muni Exempt Int	375.00	OKLAHOMA DEV FIN AUTH HEALTH SYS REV 05.00000% 08/15/2029 REF BDS INTEGRIS BAPTIST MED CTR INC SER. 2015A	\N	67884XBQ9	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
f0aa90e0-3381-465e-8997-ae993d7a3553	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-20	2025-08-20	dividend	received	Dividend Received	4.50	PROSPECT CAP CORP COM	PSEC	74348T102	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
5a2572b8-4240-4dee-8001-0e2bb52ed2ac	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	dividend	received	Dividend Received	82.30	BLACKROCK CR ALLOCATION INCOME COM SUBSTITUTE PAYMENT	BTZ	092508100	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
dbb2350e-88dc-47e8-bc49-6a657e066e2f	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	dividend	received	Dividend Received	1.60	BLACKROCK CR ALLOCATION INCOME COM	BTZ	092508100	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
7bfbf6b4-e77c-486f-a612-cd5400bead40	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	dividend	received	Dividend Received	548.94	FIDELITY GOVERNMENT MONEY MARKET	SPAXX	31617H102	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
b37f8293-8b73-4c2b-ae86-c61714c624db	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	dividend	reinvestment	Reinvestment	-2815.60	FIDELITY TAX-FREE BOND	FTABX	316128503	262.404000	10.7300	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
a63c894e-58cb-4fd8-9faf-df4928bbc632	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	dividend	received	Dividend Received	2815.60	FIDELITY TAX-FREE BOND	FTABX	316128503	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
ff13c5e7-e76c-4ca7-8f2e-fcbaeed2e5e5	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	dividend	reinvestment	Reinvestment	-5619.83	FIMM TAX EXEMPT PORTFOLIO: CLASS I	FTCXX	316176106	5619.830000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
abe814f2-bb73-4ed3-995b-0f282fd683f1	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	dividend	received	Dividend Received	5619.83	FIMM TAX EXEMPT PORTFOLIO: CLASS I	FTCXX	316176106	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
f478c953-d179-4e6b-8814-bfd477bc9f1d	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	dividend	received	Dividend Received	24.00	MFS MUN INCOME TR SH BEN INT	MFM	552738106	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
3c04d244-1849-4971-a0c0-6e2105c557d8	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	dividend	received	Dividend Received	90.00	TORTOISE SUSTAINABLE AND SOCIAL IMPACT TERM FUND	TEAF	27901F109	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
4fa982dc-8981-4a18-aaa8-9849276b7998	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-21	2025-08-21	transfer	deposit	Deposit Received	8000.00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	deposits	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
683ef16e-7766-4ccd-9cc4-143c47b2126b	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-01	2025-08-01	transfer	withdrawal	Wire Tfr To Bank WD83188739 COINBASE INC CROSS RIVER BANK ******7024	-100000.00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	withdrawals	WD83188739	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
a98869c5-61f1-4fb0-9787-845a03a3cadd	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-13	2025-08-13	transfer	withdrawal	Wire Tfr To Bank WD83488553 COINBASE INC CROSS RIVER BANK ******7024	-250000.00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	withdrawals	WD83488553	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
3196e196-813f-4344-903d-0f81702f3937	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	transfer	withdrawal	Wire Tfr To Bank WD83546207 COINBASE INC CROSS RIVER BANK ******7024	-250000.00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	withdrawals	WD83546207	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
1d5f0506-dc9c-4912-b123-ce1a5984a186	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-01	2025-08-01	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	2767.46	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	SPAXX	\N	2767.460000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
2ba0118e-69a2-442f-9e2b-cf292b2badc6	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-04	2025-08-04	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET @ 1	-152500.00	FIDELITY GOVERNMENT MONEY MARKET @ 1	SPAXX	\N	-152500.000000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
b375c01e-72be-4fcd-b10e-71020a63d193	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-06	2025-08-06	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET @ 1	236.22	FIDELITY GOVERNMENT MONEY MARKET @ 1	SPAXX	\N	236.220000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
998b9d02-9a7a-4927-b987-5c4e14de8ca5	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-06	2025-08-06	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	23731.41	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	SPAXX	\N	23731.410000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
36f646e7-67bd-4ace-beef-d1b7f4ed0586	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-08	2025-08-08	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	11952.51	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	SPAXX	\N	11952.510000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
3304b719-1f78-46f1-b5ff-9c8c57b754e6	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-12	2025-08-12	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	-15485.46	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	SPAXX	\N	-15485.460000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
55e14aff-7d0e-47cf-a460-012482c34898	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-13	2025-08-13	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET @ 1	-199416.88	FIDELITY GOVERNMENT MONEY MARKET @ 1	SPAXX	\N	-199416.880000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
052f1e84-c8b6-4530-bbfb-0b3bae15d8a6	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-14	2025-08-14	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET @ 1	406000.00	FIDELITY GOVERNMENT MONEY MARKET @ 1	SPAXX	\N	406000.000000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
74bdecbb-fd96-4682-96d0-300fa395c469	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET @ 1	-250000.00	FIDELITY GOVERNMENT MONEY MARKET @ 1	SPAXX	\N	-250000.000000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
53b3d8e5-f461-4e95-be54-bafccea3ce7b	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	102401.76	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	SPAXX	\N	102401.760000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
5b3e235b-a2ec-44d5-9597-7133b07c5f8f	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-18	2025-08-18	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET @ 1	-258391.52	FIDELITY GOVERNMENT MONEY MARKET @ 1	SPAXX	\N	-258391.520000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
6b46bb1e-ea04-498a-8a8c-3d325b86a7c5	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-18	2025-08-18	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	-10.24	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	SPAXX	\N	-10.240000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
8adcecc4-eda1-4011-8de6-103356598805	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-19	2025-08-19	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	2090.92	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	SPAXX	\N	2090.920000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
33f8bf20-e993-4d5f-a72b-aff4ebbce2e3	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-20	2025-08-20	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	4.50	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	SPAXX	\N	4.500000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
3fd73c7b-71db-4bcc-b5a4-6d4c3b7d7459	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-21	2025-08-21	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET @ 1	8000.00	FIDELITY GOVERNMENT MONEY MARKET @ 1	SPAXX	\N	8000.000000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
96e6df3e-1c12-4df5-9298-b34b55be513e	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-22	2025-08-22	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	394.00	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	SPAXX	\N	394.000000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
e3e21600-8ad4-4410-9cbb-76a420e6e408	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-25	2025-08-25	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET @ 1	-10489.42	FIDELITY GOVERNMENT MONEY MARKET @ 1	SPAXX	\N	-10489.420000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
32170bb2-eba2-4a76-ad4f-8930ef29441e	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-27	2025-08-27	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	7616.52	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	SPAXX	\N	7616.520000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
47acce7c-72a8-43a3-8622-7b6aa3ce3e02	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-28	2025-08-28	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	3826.52	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	SPAXX	\N	3826.520000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
7f533358-c344-4079-a075-82181a2d99f5	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET @ 1	-11540.33	FIDELITY GOVERNMENT MONEY MARKET @ 1	SPAXX	\N	-11540.330000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
8cff1d73-39e6-4ed9-8834-7f5583cc2f98	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	-451.65	FIDELITY GOVERNMENT MONEY MARKET MORNING TRADE @ 1	SPAXX	\N	-451.650000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
b65ba9db-064e-4192-b2c3-b25e017353ab	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	fund_activity	core_fund	FIDELITY GOVERNMENT MONEY MARKET REINVEST @ $1.000	548.94	FIDELITY GOVERNMENT MONEY MARKET REINVEST @ $1.000	SPAXX	\N	548.940000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
9a48cb99-7347-4069-8f20-e2d32cdacdc5	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-04	2025-08-04	option	put	You Bought	-152500.00	TESLA INC COM ASSIGNED PUTS	TSLA	88160R101	500.000000	305.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
694af096-642d-4ef9-9c5a-c4e9850efd70	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-06	2025-08-06	option	put	You Sold	10693.26	PUT (COIN) COINBASE GLOBAL INC AUG 15 25 $300 (100 SHS) OPENING TRANSACTION	COIN	7378399EA	-10.000000	10.7000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
9625fc76-a4ea-4d94-bf93-56d3e222c5eb	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-06	2025-08-06	option	put	You Sold	3801.63	PUT (CRWV) COREWEAVE INC COM CL AUG 15 25 $100 (100 SHS) OPENING TRANSACTION	CRWV	7894949PJ	-5.000000	7.6100	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
d71624c4-bea4-478b-9773-90189156be76	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-06	2025-08-06	option	put	You Sold	3236.63	PUT (META) META PLATFORMS INC AUG 15 25 $750 (100 SHS) OPENING TRANSACTION	META	7285639EE	-5.000000	6.4800	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
de34b98b-fcc2-47e0-a853-8df2c39b891c	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-06	2025-08-06	option	put	You Sold	2893.26	PUT (NVDA) NVIDIA CORPORATION AUG 29 25 $160 (100 SHS) OPENING TRANSACTION	NVDA	7999339BX	-10.000000	2.9000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
b8404b5a-113a-4855-b25b-2a0b0528aae4	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-06	2025-08-06	option	put	You Sold	3106.63	PUT (TSLA) TESLA INC COM AUG 15 25 $300 (100 SHS) OPENING TRANSACTION	TSLA	7347879NJ	-5.000000	6.2200	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
a8907e12-7984-4199-bc72-1485e8b7e37d	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-08	2025-08-08	option	call	You Bought	-845.35	CALL (ETN) EATON CORPORATION SEP 19 25 $380 (100 SHS) OPENING TRANSACTION	ETN	7408299DD	2.000000	4.2200	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
a4fefb94-22a4-4867-a576-38427f7d137c	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-08	2025-08-08	option	call	You Bought	-1271.02	CALL (ETN) EATON CORPORATION SEP 19 25 $380 (100 SHS) OPENING TRANSACTION	ETN	7408299DD	3.000000	4.2300	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
452c2c36-98cc-4932-b649-ab996e749ab1	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-08	2025-08-08	option	put	You Sold	843.26	PUT (AR) ANTERO RESOURCES AUG 22 25 $33 (100 SHS) OPENING TRANSACTION	AR	7986819AS	-10.000000	0.8500	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
9fa9ee65-225e-47a8-bc09-d41e9a751aec	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-08	2025-08-08	option	put	You Sold	795.98	PUT (ETN) EATON CORPORATION SEP 19 25 $320 (100 SHS) OPENING TRANSACTION	ETN	7408289VR	-3.000000	2.6600	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
56b39ad5-8d5a-4c5f-a653-b4a11c4ae7dd	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-08	2025-08-08	option	put	You Sold	532.65	PUT (ETN) EATON CORPORATION SEP 19 25 $320 (100 SHS) OPENING TRANSACTION	ETN	7408289VR	-2.000000	2.6700	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
82dc2254-edf3-4a1c-9b37-ad133f864b6c	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-08	2025-08-08	option	put	You Sold	1393.26	PUT (RRC) RANGE RESOURCES CORP SEP 19 25 $35 (100 SHS) OPENING TRANSACTION	RRC	7669819SQ	-10.000000	1.4000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
f7b32888-9c0e-4f0e-8db2-8805623f43a1	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-08	2025-08-08	option	call	Redeemed	10000.00	WISCONSIN ST HEALTH & EDL FACS AUTH REV 05.00000% 11/15/2027 FULL CALL PAYOUT #REOR R6006628610000	\N	97712DHL3	-10000.000000	\N	10000.00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
39576563-3ef6-4584-a754-e8f64f33038c	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-12	2025-08-12	option	call	You Bought	-1053.49	CALL (INTC) INTEL CORP COM OCT 17 25 $25 (100 SHS) OPENING TRANSACTION	INTC	7729649UU	20.000000	0.5200	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
42d0d20a-ba18-44c2-838e-ed1e901ce570	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-12	2025-08-12	trade	security	You Bought	-20905.00	INTEL CORP COM USD0.001	INTC	458140100	1000.000000	20.9050	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
3eb18aee-bb62-4995-8464-efb287d25501	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-12	2025-08-12	option	put	You Sold	2593.26	PUT (GOOG) ALPHABET INC CAP STK AUG 15 25 $200 (100 SHS) OPENING TRANSACTION	GOOG	7766399TT	-10.000000	2.6000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
7aa3f911-89d8-43c9-8b36-8fe3dff74ff1	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-12	2025-08-12	option	put	You Sold	806.51	PUT (INTC) INTEL CORP COM OCT 17 25 $18 (100 SHS) OPENING TRANSACTION	INTC	7729639FZ	-20.000000	0.4100	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
071bebe2-c60e-4a69-bba7-9b961bdb192b	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-12	2025-08-12	option	put	You Sold	3073.26	PUT (TSLA) TESLA INC COM AUG 22 25 $320 (100 SHS) OPENING TRANSACTION	TSLA	7990219SO	-10.000000	3.0800	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
98f75abd-7391-49a0-94d0-f09f55142233	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-13	2025-08-13	trade	security	You Sold	50583.12	FIMM TAX EXEMPT PORTFOLIO: CLASS I REDEEMED TO COVER A SETTLED OBLIGATION @ 1	FTCXX	316176106	-50583.120000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
d2478e33-c0f5-4f0a-ba1d-421b1bba09f8	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	trade	security	Redeemed	50000.00	CLIFTON TEX HIGHER ED FIN CORP ED REV 05.00000% 08/15/2025 REDEMPTION PAYOUT #REOR R6006569090000	\N	187145GB7	-50000.000000	\N	50000.00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
9b3279a5-1d66-41a7-9981-722527963246	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	option	put	You Sold	11486.51	PUT (AMD) ADVANCED MICRO AUG 29 25 $180 (100 SHS) OPENING TRANSACTION	AMD	8001059DZ	-20.000000	5.7500	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
df8707f5-bd77-4c27-b973-56fbaede05f9	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	option	put	You Sold	35243.26	PUT (COIN) COINBASE GLOBAL INC JAN 16 26 $300 (100 SHS) OPENING TRANSACTION	COIN	6922869EC	-10.000000	35.2500	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
1cb470b4-b48b-473b-ab8c-d9a4347cab83	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	option	put	You Sold	2981.63	PUT (MSTR) MICROSTRATEGY COM AUG 15 25 $370 (100 SHS) OPENING TRANSACTION	MSTR	7881139QQ	-5.000000	5.9700	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
1482a76f-8c21-450a-9b37-2d3e8d9128a3	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-18	2025-08-18	option	put	You Bought	-67500.00	COREWEAVE INC COM CL A ASSIGNED PUTS	CRWV	21873S108	500.000000	135.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
e76866ae-594c-4def-9d84-7debdb783d3b	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-18	2025-08-18	option	put	You Bought	-77500.00	COREWEAVE INC COM CL A ASSIGNED PUTS	CRWV	21873S108	500.000000	155.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
acab9a27-9a3f-4037-a9bc-c9a02bcfe639	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-18	2025-08-18	trade	security	You Sold	71608.48	FIMM TAX EXEMPT PORTFOLIO: CLASS I REDEEMED TO COVER A SETTLED OBLIGATION @ 1	FTCXX	316176106	-71608.480000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
129fe146-f46f-4ae3-bff5-9f199e91aa03	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-18	2025-08-18	option	put	You Bought - Short-term gain: $10,683.02	-10.24	PUT (COIN) COINBASE GLOBAL INC AUG 15 25 $300 (100 SHS) CLOSING TRANSACTION	COIN	7378399EA	10.000000	0.0100	-10693.26	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
305e57f1-ad39-4c53-abc8-82748a799f50	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-18	2025-08-18	option	put	You Bought	-185000.00	STRATEGY INC COMMON STOCK CLASS A ASSIGNED PUTS	MSTR	594972408	500.000000	370.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
0d6e01f2-2def-4ed3-85d0-a880477a27dc	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-19	2025-08-19	option	call	You Bought	-1451.35	CALL (CRWV) COREWEAVE INC COM CL SEP 05 25 $105 (100 SHS) OPENING TRANSACTION	CRWV	8041349XV	2.000000	7.2500	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
0f630e23-a9f6-4068-b445-8f820b63afaa	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-19	2025-08-19	option	call	You Bought	-5717.39	CALL (CRWV) COREWEAVE INC COM CL SEP 05 25 $105 (100 SHS) OPENING TRANSACTION	CRWV	8041349XV	8.000000	7.1400	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
573c665f-4a7d-42c4-9d10-3dcef189c159	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-19	2025-08-19	option	call	You Bought	-274.67	CALL (GOOG) ALPHABET INC CAP STK SEP 12 25 $215 (100 SHS) OPENING TRANSACTION	GOOG	8051819VP	1.000000	2.7400	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
7bd8fe5b-fdd9-44cc-82c7-99039c69c7ab	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-19	2025-08-19	option	call	You Bought	-5218.81	CALL (GOOG) ALPHABET INC CAP STK SEP 12 25 $215 (100 SHS) OPENING TRANSACTION	GOOG	8051819VP	19.000000	2.7400	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
d6150092-95eb-4b38-9425-a78a3e9523e2	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-19	2025-08-19	option	put	You Sold	6993.26	PUT (CRWV) COREWEAVE INC COM CL AUG 29 25 $100 (100 SHS) OPENING TRANSACTION	CRWV	7997579KG	-10.000000	7.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
ac514bdf-785f-44d7-8fd6-620529ed4b47	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-19	2025-08-19	option	put	You Sold	6006.63	PUT (MSTR) MICROSTRATEGY COM AUG 29 25 $360 (100 SHS) OPENING TRANSACTION	MSTR	7998979GG	-5.000000	12.0200	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
db0be350-de93-4d28-bd61-d80827efda0a	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-19	2025-08-19	option	put	You Sold	853.95	PUT (TSLA) TESLA INC COM AUG 29 25 $300 (100 SHS) OPENING TRANSACTION	TSLA	8000269GE	-6.000000	1.4300	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
fec32f17-a0b6-4597-b6b4-a43e12e83eb3	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-19	2025-08-19	option	put	You Sold	569.30	PUT (TSLA) TESLA INC COM AUG 29 25 $300 (100 SHS) OPENING TRANSACTION	TSLA	8000269GE	-4.000000	1.4300	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
57c3cf06-8bdc-431c-8b31-1d4d25e24c25	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-25	2025-08-25	option	put	You Bought	-33000.00	ANTERO RESOURCES CORP COM ASSIGNED PUTS	AR	03674X106	1000.000000	33.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
dd2d2c0d-c4b8-46ff-87f2-63df223ae1a3	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-25	2025-08-25	trade	security	You Sold	22510.58	FIMM TAX EXEMPT PORTFOLIO: CLASS I REDEEMED TO COVER A SETTLED OBLIGATION @ 1	FTCXX	316176106	-22510.580000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
59d9988e-8922-4596-9946-f08cdf04d3bb	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-27	2025-08-27	option	put	You Sold	5543.26	PUT (AVGO) BROADCOM INC COM SEP 05 25 $280 (100 SHS) OPENING TRANSACTION	AVGO	8040849CU	-10.000000	5.5500	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
1b39924f-008f-4b79-ac3c-57c8401076f4	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-27	2025-08-27	option	put	You Sold	2073.26	PUT (ORCL) ORACLE CORP AUG 29 25 $230 (100 SHS) OPENING TRANSACTION	ORCL	7999409MI	-10.000000	2.0800	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
cf1e9356-2b21-4289-a58a-8b6cbadda4cb	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-28	2025-08-28	option	put	You Sold	2943.26	PUT (NVDA) NVIDIA CORPORATION AUG 29 25 $175 (100 SHS) OPENING TRANSACTION	NVDA	7999339QK	-10.000000	2.9500	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
98d867ec-d9b4-4d03-88cb-43f4034489f8	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-28	2025-08-28	option	put	You Sold	883.26	PUT (SERV) SERVE ROBOTICS INC SEP 12 25 $11.5 (100 SHS) OPENING TRANSACTION	SERV	8053339OK	-10.000000	0.8900	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
0c6a210f-76fc-4ad1-a6e7-8b5804831d35	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	option	put	You Bought	-360000.00	ADVANCED MICRO DEVICES INC ASSIGNED PUTS	AMD	007903107	2000.000000	180.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
963fe452-4818-4030-a46e-5c91ca265957	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-08-29	trade	security	You Sold	348459.67	FIMM TAX EXEMPT PORTFOLIO: CLASS I REDEEMED TO COVER A SETTLED OBLIGATION @ 1	FTCXX	316176106	-348459.670000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
5eceecf7-e4d8-4318-a0e0-52da06e9a5e8	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-01	2025-08-01	option	put	Expired	0.00	PUT (META) META PLATFORMS INC AUG 01 25 $712.5 (100 SHS)	META	8004479AY	5.000000	\N	-12496.62	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
3eec3456-215a-4a12-ae9f-5f7af417c7ff	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-01	2025-08-01	option	put	Expired	0.00	PUT (MSFT) MICROSOFT CORP AUG 01 25 $490 (100 SHS)	MSFT	7946929CY	5.000000	\N	-2061.62	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
4dc05eed-8e36-45bc-b639-367cdd97eeda	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	return of capital	\N	Return Of Capital	136.35	MPLX LP COM UNIT REP LTD	MPLX	55336V100	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
0b8aadf0-eab8-436f-85e7-79e2f1a29152	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	option	put	Expired	0.00	PUT (CRWV) COREWEAVE INC COM CL AUG 15 25 $100 (100 SHS)	CRWV	7894949PJ	5.000000	\N	-3801.63	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
814c3da7-48bb-4635-a68b-1d2182f16140	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	option	put	Expired	0.00	PUT (GOOG) ALPHABET INC CAP STK AUG 15 25 $170 (100 SHS)	GOOG	7766399LJ	10.000000	\N	-10173.21	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
6b0361eb-cd3a-449b-8c5e-18d40cc95d3d	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	option	put	Expired	0.00	PUT (GOOG) ALPHABET INC CAP STK AUG 15 25 $200 (100 SHS)	GOOG	7766399TT	10.000000	\N	-2593.26	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
f107c6d3-650c-4c83-971d-cd257fc4b4a9	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	option	put	Expired	0.00	PUT (META) META PLATFORMS INC AUG 15 25 $750 (100 SHS)	META	7285639EE	5.000000	\N	-3236.63	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
7869195e-441d-4575-bda8-93f9bd89c9be	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	option	put	Expired	0.00	PUT (TSLA) TESLA INC COM AUG 15 25 $300 (100 SHS)	TSLA	7347879NJ	10.000000	\N	-15308.25	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
a01c57f4-a092-4e23-91bc-a0cfda9f8451	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-19	2025-08-19	return of capital	\N	Return Of Capital	330.00	ENERGY TRANSFER L P COM UT LTD PTN	ET	29273V100	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
79af606a-fd46-4626-a759-6aa1991f41a6	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-22	2025-08-22	option	put	Expired	0.00	PUT (TSLA) TESLA INC COM AUG 22 25 $320 (100 SHS)	TSLA	7990219SO	10.000000	\N	-3073.26	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
a590bbca-ea00-4e83-8e79-760350ea4566	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-01	2025-08-01	option	put	Assigned	0.00	PUT (TSLA) TESLA INC COM AUG 01 25 $305 (100 SHS)	TSLA	7948139BB	5.000000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_out	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
12373da2-d7a9-46ac-8d57-6f2d17cfe4c4	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	option	put	Assigned	0.00	PUT (CRWV) COREWEAVE INC COM CL AUG 15 25 $135 (100 SHS)	CRWV	7914329NL	5.000000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_out	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
d1a4984e-e19b-46f5-95a1-c8004f408fbf	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	option	put	Assigned	0.00	PUT (CRWV) COREWEAVE INC COM CL AUG 15 25 $155 (100 SHS)	CRWV	7915829GG	5.000000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_out	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
e2332735-e8a7-46bc-8870-b20aae4d8d57	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-15	2025-08-15	option	put	Assigned	0.00	PUT (MSTR) MICROSTRATEGY COM AUG 15 25 $370 (100 SHS)	MSTR	7881139QQ	5.000000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_out	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
4b668dd7-332f-4a62-8637-09db12296075	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-22	2025-08-22	option	put	Assigned	0.00	PUT (AR) ANTERO RESOURCES AUG 22 25 $33 (100 SHS)	AR	7986819AS	10.000000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_out	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
3600b3bf-885e-47a7-a66b-b861869aee1c	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-28	2025-08-28	option	put	Assigned	0.00	PUT (AMD) ADVANCED MICRO AUG 29 25 $180 (100 SHS)	AMD	8001059DZ	20.000000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	other_activity_out	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
d7e6fa1d-f6e1-4838-ac28-d1a0d0c7f967	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-01	2025-08-01	transfer	exchange_in	Transferred From	100000.00	Z40-394071-1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	exchanges_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
a39d3945-e62b-4017-b9af-0537d1d5f833	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-14	2025-08-14	transfer	exchange_in	Transferred From	250000.00	Z40-394067-1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	exchanges_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
1294bca1-5afa-4619-a703-4ecf3b06383c	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-14	2025-08-14	transfer	exchange_in	Transferred From	156000.00	Z40-397011-1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	exchanges_in	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
8e9d8b60-cbc0-4cde-8cd2-1721e7cab9fb	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-06	2025-08-06	fee	charge	British American Tobacco Lvl Ii Adr	-3.00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	fees_charges	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
b2087186-9060-4b45-8dac-64ba733348f0	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-09-02	option	put	Bought - Short-term gain: $698.31	-1.02	PUT (CRWV) COREWEAVE INC COM CL AUG 29 25 $100 (100 SHS) CLOSING TRANSACTION	CRWV	\N	1.000000	0.0100	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	trades_pending_settlement	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
7e38afbd-d643-4f7a-9b68-61ce3d2e68c1	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-09-02	option	put	Bought - Short-term gain: $6,284.71	-9.22	PUT (CRWV) COREWEAVE INC COM CL AUG 29 25 $100 (100 SHS) CLOSING TRANSACTION	CRWV	\N	9.000000	0.0100	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	trades_pending_settlement	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
3d8f41cc-1035-43a2-8fec-11a59c3d88ad	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-09-02	option	put	Bought - Short-term gain: $1,756.52	-1186.74	PUT (NVDA) NVIDIA CORPORATION AUG 29 25 $175 (100 SHS) CLOSING TRANSACTION	NVDA	\N	10.000000	1.1800	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	trades_pending_settlement	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
117af672-33eb-4e0a-bb7b-95d237e3c5b4	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-09-02	option	put	Sold	4793.26	PUT (COIN) COINBASE GLOBAL INC SEP 05 25 $300 (100 SHS) OPENING TRANSACTION	COIN	\N	-10.000000	4.8000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	trades_pending_settlement	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
917f6d6e-a44c-48de-9a9e-2a5bd94c3905	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-09-02	option	put	Sold	4493.26	PUT (TSM) TAIWAN SEMICONDUCTOR SEP 12 25 $230 (100 SHS) OPENING TRANSACTION	TSM	\N	-10.000000	4.5000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	trades_pending_settlement	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
0e607db0-b4b0-48a1-9af3-28ab314536a2	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-09-02	option	call	Sold	1093.26	CALL (MP) MP MATERIALS CORP SEP 05 25 $77 (100 SHS) OPENING TRANSACTION	MP	\N	-10.000000	1.1000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	trades_pending_settlement	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
b1146bde-883d-4a0f-aed9-d9c479410bed	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	44444444-4444-4444-4444-444444444444	2025-08-29	2025-09-02	option	put	Sold	2423.26	PUT (CRWV) COREWEAVE INC COM CL SEP 05 25 $101 (100 SHS) OPENING TRANSACTION	CRWV	\N	-10.000000	2.4300	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	trades_pending_settlement	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	put	\N	\N
bc4d4810-aea6-450b-82f5-9dc2303069e6	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-29	2025-08-29	interest	deposit	Interest Earned	22.52	FDIC INSURED DEPOSIT	\N	FDIC99375	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
40e2ecc7-5c1b-469a-8804-1b579d3d0cb7	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-29	2025-08-29	dividend	reinvestment	Reinvestment	-163.23	FIMM MONEY MARKET PORTFOLIO: CL I	FMPXX	316175207	163.230000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
8459094d-0c1e-4fd0-8585-caaa6aaca9e2	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-29	2025-08-29	dividend	received	Dividend Received	163.23	FIMM MONEY MARKET PORTFOLIO: CL I	FMPXX	316175207	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	dividends_interest_income	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
783ab491-0b29-43a5-8147-687744c8c5d5	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-14	2025-08-14	transfer	deposit	Deposit Crabapple Pr Payroll	470.11	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	deposits	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
7645d240-9526-4745-ad87-44ea81947a2b	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-28	2025-08-28	transfer	deposit	Deposit Crabapple Pr Payroll	470.11	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	deposits	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
56704aef-24a1-42e5-854e-4a741b74fb4e	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-29	2025-08-29	transfer	deposit	Deposit Cws Inv Cash Disb	4458.89	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	deposits	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
2b103259-d08d-4997-ae29-d8e21e8e76af	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-01	2025-08-01	transfer	withdrawal	DEBIT ROUNDPOINT MTG PAYMENTS	-2339.78	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	withdrawals	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
a9bc1b56-9322-4e80-bee4-b0540e1528f6	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-18	2025-08-18	transfer	withdrawal	Money Line Paid EFT FUNDS PAID ED84401349 /WEB JPMORGAN CHASE BANK, NA ******1981	-10000.00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	withdrawals	ED84401349	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
66bca3fb-8870-4948-b139-78567592378b	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-20	2025-08-20	transfer	withdrawal	DEBIT AUBURN UNIVERS AUBURN UNI	-13584.73	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	withdrawals	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
f3a64fc0-8e15-40f2-8424-3180851cd3bc	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-01	2025-08-01	fund_activity	core_fund	FDIC INSURED DEPOSIT AT CITIBANK NOT COVERED BY SIPC @ 1	-2339.78	FDIC INSURED DEPOSIT AT CITIBANK NOT COVERED BY SIPC @ 1	\N	\N	-2339.780000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
ea322822-b029-4de2-94e4-f976f3b9e9b1	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-14	2025-08-14	fund_activity	core_fund	FDIC INSURED DEPOSIT AT CITIBANK NOT COVERED BY SIPC @ 1	470.11	FDIC INSURED DEPOSIT AT CITIBANK NOT COVERED BY SIPC @ 1	\N	\N	470.110000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
7fddbb2c-aefb-405c-9589-2388b6ce89fe	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-18	2025-08-18	fund_activity	core_fund	FDIC INSURED DEPOSIT AT CITIBANK NOT COVERED BY SIPC @ 1	-10000.00	FDIC INSURED DEPOSIT AT CITIBANK NOT COVERED BY SIPC @ 1	\N	\N	-10000.000000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
38cc1b4b-e26f-415a-b382-da4dbceefe48	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-20	2025-08-20	fund_activity	core_fund	FDIC INSURED DEPOSIT AT CITIBANK NOT COVERED BY SIPC @ 1	-9677.67	FDIC INSURED DEPOSIT AT CITIBANK NOT COVERED BY SIPC @ 1	\N	\N	-9677.670000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
41c12bec-d6d1-4c0c-b051-cec54de0348f	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-28	2025-08-28	fund_activity	core_fund	FDIC INSURED DEPOSIT AT CITIBANK NOT COVERED BY SIPC @ 1	470.11	FDIC INSURED DEPOSIT AT CITIBANK NOT COVERED BY SIPC @ 1	\N	\N	470.110000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
81b8788a-7e3d-4ee3-8bc4-61a3e144c3ed	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-29	2025-08-29	fund_activity	core_fund	FDIC INSURED DEPOSIT AT CITIBANK NOT COVERED BY SIPC @ 1	-470.11	FDIC INSURED DEPOSIT AT CITIBANK NOT COVERED BY SIPC @ 1	\N	\N	-470.110000	1.0000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	core_fund_activity	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
580b540a-4679-4280-864d-4c7a683e6e45	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-20	2025-08-20	trade	security	You Sold	3907.06	FIMM MONEY MARKET PORTFOLIO: CL I REDEEMED TO COVER A SETTLED OBLIGATION @ 1	FMPXX	316175207	-3907.060000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
a8f1d720-bbc1-41e4-8329-e5f4f960b8fb	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-29	2025-08-29	trade	security	You Sold	13180.48	FIMM MONEY MARKET PORTFOLIO: CL I REDEEMED TO COVER A SETTLED OBLIGATION @ 1	FMPXX	316175207	-13180.480000	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	securities_bought_sold	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
2dfd79ec-c007-4f83-9329-f8d7f634fe7f	11111111-1111-1111-1111-111111111111	4297643c-91b0-4000-8252-97034c4d9898	55555555-5555-5555-5555-555555555555	2025-08-29	2025-08-29	payment	bill_payment	Unknown	-18132.00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	billpay	\N	CHASE CARD SERVICES	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	2025-09-24 20:17:23.362174+00	2025-09-24 20:20:26.980511+00	claude	\N	\N	\N
\.


--
-- Data for Name: messages_2025_09_22; Type: TABLE DATA; Schema: realtime; Owner: supabase_admin
--

COPY realtime.messages_2025_09_22 (topic, extension, payload, event, private, updated_at, inserted_at, id) FROM stdin;
\.


--
-- Data for Name: messages_2025_09_23; Type: TABLE DATA; Schema: realtime; Owner: supabase_admin
--

COPY realtime.messages_2025_09_23 (topic, extension, payload, event, private, updated_at, inserted_at, id) FROM stdin;
\.


--
-- Data for Name: messages_2025_09_24; Type: TABLE DATA; Schema: realtime; Owner: supabase_admin
--

COPY realtime.messages_2025_09_24 (topic, extension, payload, event, private, updated_at, inserted_at, id) FROM stdin;
\.


--
-- Data for Name: messages_2025_09_25; Type: TABLE DATA; Schema: realtime; Owner: supabase_admin
--

COPY realtime.messages_2025_09_25 (topic, extension, payload, event, private, updated_at, inserted_at, id) FROM stdin;
\.


--
-- Data for Name: messages_2025_09_26; Type: TABLE DATA; Schema: realtime; Owner: supabase_admin
--

COPY realtime.messages_2025_09_26 (topic, extension, payload, event, private, updated_at, inserted_at, id) FROM stdin;
\.


--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: realtime; Owner: supabase_admin
--

COPY realtime.schema_migrations (version, inserted_at) FROM stdin;
20211116024918	2025-09-23 00:33:33
20211116045059	2025-09-23 00:33:33
20211116050929	2025-09-23 00:33:33
20211116051442	2025-09-23 00:33:33
20211116212300	2025-09-23 00:33:33
20211116213355	2025-09-23 00:33:33
20211116213934	2025-09-23 00:33:33
20211116214523	2025-09-23 00:33:33
20211122062447	2025-09-23 00:33:33
20211124070109	2025-09-23 00:33:33
20211202204204	2025-09-23 00:33:33
20211202204605	2025-09-23 00:33:33
20211210212804	2025-09-23 00:33:33
20211228014915	2025-09-23 00:33:33
20220107221237	2025-09-23 00:33:33
20220228202821	2025-09-23 00:33:33
20220312004840	2025-09-23 00:33:33
20220603231003	2025-09-23 00:33:33
20220603232444	2025-09-23 00:33:33
20220615214548	2025-09-23 00:33:33
20220712093339	2025-09-23 00:33:33
20220908172859	2025-09-23 00:33:33
20220916233421	2025-09-23 00:33:33
20230119133233	2025-09-23 00:33:33
20230128025114	2025-09-23 00:33:33
20230128025212	2025-09-23 00:33:33
20230227211149	2025-09-23 00:33:33
20230228184745	2025-09-23 00:33:33
20230308225145	2025-09-23 00:33:33
20230328144023	2025-09-23 00:33:33
20231018144023	2025-09-23 00:33:33
20231204144023	2025-09-23 00:33:33
20231204144024	2025-09-23 00:33:33
20231204144025	2025-09-23 00:33:33
20240108234812	2025-09-23 00:33:33
20240109165339	2025-09-23 00:33:33
20240227174441	2025-09-23 00:33:33
20240311171622	2025-09-23 00:33:33
20240321100241	2025-09-23 00:33:33
20240401105812	2025-09-23 00:33:33
20240418121054	2025-09-23 00:33:33
20240523004032	2025-09-23 00:33:33
20240618124746	2025-09-23 00:33:33
20240801235015	2025-09-23 00:33:33
20240805133720	2025-09-23 00:33:33
20240827160934	2025-09-23 00:33:33
20240919163303	2025-09-23 00:33:33
20240919163305	2025-09-23 00:33:33
20241019105805	2025-09-23 00:33:33
20241030150047	2025-09-23 00:33:33
20241108114728	2025-09-23 00:33:33
20241121104152	2025-09-23 00:33:33
20241130184212	2025-09-23 00:33:33
20241220035512	2025-09-23 00:33:33
20241220123912	2025-09-23 00:33:33
20241224161212	2025-09-23 00:33:33
20250107150512	2025-09-23 00:33:33
20250110162412	2025-09-23 00:33:33
20250123174212	2025-09-23 00:33:33
20250128220012	2025-09-23 00:33:33
20250506224012	2025-09-23 00:33:33
20250523164012	2025-09-23 00:33:33
20250714121412	2025-09-23 00:33:33
\.


--
-- Data for Name: subscription; Type: TABLE DATA; Schema: realtime; Owner: supabase_admin
--

COPY realtime.subscription (id, subscription_id, entity, filters, claims, created_at) FROM stdin;
\.


--
-- Data for Name: buckets; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--

COPY storage.buckets (id, name, owner, created_at, updated_at, public, avif_autodetection, file_size_limit, allowed_mime_types, owner_id, type) FROM stdin;
\.


--
-- Data for Name: buckets_analytics; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--

COPY storage.buckets_analytics (id, type, format, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: iceberg_namespaces; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--

COPY storage.iceberg_namespaces (id, bucket_id, name, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: iceberg_tables; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--

COPY storage.iceberg_tables (id, namespace_id, bucket_id, name, location, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: migrations; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--

COPY storage.migrations (id, name, hash, executed_at) FROM stdin;
0	create-migrations-table	e18db593bcde2aca2a408c4d1100f6abba2195df	2025-09-23 00:33:34.761427
1	initialmigration	6ab16121fbaa08bbd11b712d05f358f9b555d777	2025-09-23 00:33:34.762472
2	storage-schema	5c7968fd083fcea04050c1b7f6253c9771b99011	2025-09-23 00:33:34.762868
3	pathtoken-column	2cb1b0004b817b29d5b0a971af16bafeede4b70d	2025-09-23 00:33:34.76563
4	add-migrations-rls	427c5b63fe1c5937495d9c635c263ee7a5905058	2025-09-23 00:33:34.767129
5	add-size-functions	79e081a1455b63666c1294a440f8ad4b1e6a7f84	2025-09-23 00:33:34.767825
6	change-column-name-in-get-size	f93f62afdf6613ee5e7e815b30d02dc990201044	2025-09-23 00:33:34.768377
7	add-rls-to-buckets	e7e7f86adbc51049f341dfe8d30256c1abca17aa	2025-09-23 00:33:34.768848
8	add-public-to-buckets	fd670db39ed65f9d08b01db09d6202503ca2bab3	2025-09-23 00:33:34.769141
9	fix-search-function	3a0af29f42e35a4d101c259ed955b67e1bee6825	2025-09-23 00:33:34.769616
10	search-files-search-function	68dc14822daad0ffac3746a502234f486182ef6e	2025-09-23 00:33:34.770087
11	add-trigger-to-auto-update-updated_at-column	7425bdb14366d1739fa8a18c83100636d74dcaa2	2025-09-23 00:33:34.770704
12	add-automatic-avif-detection-flag	8e92e1266eb29518b6a4c5313ab8f29dd0d08df9	2025-09-23 00:33:34.771406
13	add-bucket-custom-limits	cce962054138135cd9a8c4bcd531598684b25e7d	2025-09-23 00:33:34.771767
14	use-bytes-for-max-size	941c41b346f9802b411f06f30e972ad4744dad27	2025-09-23 00:33:34.772206
15	add-can-insert-object-function	934146bc38ead475f4ef4b555c524ee5d66799e5	2025-09-23 00:33:34.775584
16	add-version	76debf38d3fd07dcfc747ca49096457d95b1221b	2025-09-23 00:33:34.776086
17	drop-owner-foreign-key	f1cbb288f1b7a4c1eb8c38504b80ae2a0153d101	2025-09-23 00:33:34.776407
18	add_owner_id_column_deprecate_owner	e7a511b379110b08e2f214be852c35414749fe66	2025-09-23 00:33:34.77697
19	alter-default-value-objects-id	02e5e22a78626187e00d173dc45f58fa66a4f043	2025-09-23 00:33:34.77768
20	list-objects-with-delimiter	cd694ae708e51ba82bf012bba00caf4f3b6393b7	2025-09-23 00:33:34.778002
21	s3-multipart-uploads	8c804d4a566c40cd1e4cc5b3725a664a9303657f	2025-09-23 00:33:34.778642
22	s3-multipart-uploads-big-ints	9737dc258d2397953c9953d9b86920b8be0cdb73	2025-09-23 00:33:34.780618
23	optimize-search-function	9d7e604cddc4b56a5422dc68c9313f4a1b6f132c	2025-09-23 00:33:34.781961
24	operation-function	8312e37c2bf9e76bbe841aa5fda889206d2bf8aa	2025-09-23 00:33:34.782493
25	custom-metadata	d974c6057c3db1c1f847afa0e291e6165693b990	2025-09-23 00:33:34.783025
26	objects-prefixes	ef3f7871121cdc47a65308e6702519e853422ae2	2025-09-23 00:33:34.78341
27	search-v2	33b8f2a7ae53105f028e13e9fcda9dc4f356b4a2	2025-09-23 00:33:34.785981
28	object-bucket-name-sorting	ba85ec41b62c6a30a3f136788227ee47f311c436	2025-09-23 00:33:34.786963
29	create-prefixes	a7b1a22c0dc3ab630e3055bfec7ce7d2045c5b7b	2025-09-23 00:33:34.787616
30	update-object-levels	6c6f6cc9430d570f26284a24cf7b210599032db7	2025-09-23 00:33:34.788152
31	objects-level-index	33f1fef7ec7fea08bb892222f4f0f5d79bab5eb8	2025-09-23 00:33:34.788966
32	backward-compatible-index-on-objects	2d51eeb437a96868b36fcdfb1ddefdf13bef1647	2025-09-23 00:33:34.789603
33	backward-compatible-index-on-prefixes	fe473390e1b8c407434c0e470655945b110507bf	2025-09-23 00:33:34.790344
34	optimize-search-function-v1	82b0e469a00e8ebce495e29bfa70a0797f7ebd2c	2025-09-23 00:33:34.790477
35	add-insert-trigger-prefixes	63bb9fd05deb3dc5e9fa66c83e82b152f0caf589	2025-09-23 00:33:34.791387
36	optimise-existing-functions	81cf92eb0c36612865a18016a38496c530443899	2025-09-23 00:33:34.791689
37	add-bucket-name-length-trigger	3944135b4e3e8b22d6d4cbb568fe3b0b51df15c1	2025-09-23 00:33:34.792982
38	iceberg-catalog-flag-on-buckets	19a8bd89d5dfa69af7f222a46c726b7c41e462c5	2025-09-23 00:33:34.793608
\.


--
-- Data for Name: objects; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--

COPY storage.objects (id, bucket_id, name, owner, created_at, updated_at, last_accessed_at, metadata, version, owner_id, user_metadata, level) FROM stdin;
\.


--
-- Data for Name: prefixes; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--

COPY storage.prefixes (bucket_id, name, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: s3_multipart_uploads; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--

COPY storage.s3_multipart_uploads (id, in_progress_size, upload_signature, bucket_id, key, version, owner_id, created_at, user_metadata) FROM stdin;
\.


--
-- Data for Name: s3_multipart_uploads_parts; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--

COPY storage.s3_multipart_uploads_parts (id, upload_id, size, part_number, bucket_id, key, etag, owner_id, version, created_at) FROM stdin;
\.


--
-- Data for Name: hooks; Type: TABLE DATA; Schema: supabase_functions; Owner: supabase_functions_admin
--

COPY supabase_functions.hooks (id, hook_table_id, hook_name, created_at, request_id) FROM stdin;
\.


--
-- Data for Name: migrations; Type: TABLE DATA; Schema: supabase_functions; Owner: supabase_functions_admin
--

COPY supabase_functions.migrations (version, inserted_at) FROM stdin;
initial	2025-09-23 00:33:23.331285+00
20210809183423_update_grants	2025-09-23 00:33:23.331285+00
\.


--
-- Data for Name: secrets; Type: TABLE DATA; Schema: vault; Owner: supabase_admin
--

COPY vault.secrets (id, name, description, secret, key_id, nonce, created_at, updated_at) FROM stdin;
\.


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: auth; Owner: supabase_auth_admin
--

SELECT pg_catalog.setval('auth.refresh_tokens_id_seq', 1, false);


--
-- Name: subscription_id_seq; Type: SEQUENCE SET; Schema: realtime; Owner: supabase_admin
--

SELECT pg_catalog.setval('realtime.subscription_id_seq', 1, false);


--
-- Name: hooks_id_seq; Type: SEQUENCE SET; Schema: supabase_functions; Owner: supabase_functions_admin
--

SELECT pg_catalog.setval('supabase_functions.hooks_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

