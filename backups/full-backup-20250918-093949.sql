
\restrict KWMctvCTM0iPaOObLsot2Ygqn7vQ06l2Lj9ixbJAtE1NdpSb59TRvzI8pde4c2t


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


CREATE EXTENSION IF NOT EXISTS "pg_net" WITH SCHEMA "extensions";






COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";






CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";






CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";





SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."accounts" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "entity_id" "uuid" NOT NULL,
    "institution_id" "uuid" NOT NULL,
    "account_number" "text" NOT NULL,
    "account_number_display" "text",
    "account_name" "text",
    "account_type" "text" NOT NULL,
    "account_subtype" "text",
    "tax_reporting_name" "text",
    "custodian_name" "text",
    "account_opening_date" "date",
    "account_status" "text" DEFAULT 'active'::"text",
    "is_tax_deferred" boolean DEFAULT false,
    "is_tax_free" boolean DEFAULT false,
    "requires_rmd" boolean DEFAULT false,
    "beneficiary_info" "jsonb",
    "notes" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "accounts_account_status_check" CHECK (("account_status" = ANY (ARRAY['active'::"text", 'inactive'::"text", 'closed'::"text", 'transferred'::"text"]))),
    CONSTRAINT "accounts_account_type_check" CHECK (("account_type" = ANY (ARRAY['checking'::"text", 'savings'::"text", 'brokerage'::"text", 'ira'::"text", '401k'::"text", 'roth_ira'::"text", 'trust'::"text", 'business'::"text", 'money_market'::"text", 'cd'::"text"]))),
    CONSTRAINT "chk_tax_attributes_exclusive" CHECK ((NOT (("is_tax_deferred" = true) AND ("is_tax_free" = true))))
);


ALTER TABLE "public"."accounts" OWNER TO "postgres";


COMMENT ON TABLE "public"."accounts" IS 'Individual financial accounts within institutions - links entities to specific account numbers';



CREATE TABLE IF NOT EXISTS "public"."asset_notes" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "entity_id" "uuid" NOT NULL,
    "account_id" "uuid",
    "symbol" "text" NOT NULL,
    "cusip" "text",
    "security_name" "text",
    "security_type" "text",
    "buy_below" numeric(12,4),
    "sell_above" numeric(12,4),
    "stop_loss" numeric(12,4),
    "current_price" numeric(12,4),
    "price_updated_at" timestamp with time zone,
    "cost_basis" numeric(15,2),
    "current_shares" numeric(15,6),
    "unrealized_gain_loss" numeric(15,2),
    "last_transaction_date" "date",
    "alert_enabled" boolean DEFAULT false,
    "alert_conditions" "jsonb",
    "dividend_yield" numeric(5,4),
    "next_dividend_date" "date",
    "research_notes" "text",
    "review_frequency" "text",
    "next_review_date" "date",
    "status" "text" DEFAULT 'active'::"text",
    "notes" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "asset_notes_buy_below_check" CHECK (("buy_below" > (0)::numeric)),
    CONSTRAINT "asset_notes_current_price_check" CHECK (("current_price" > (0)::numeric)),
    CONSTRAINT "asset_notes_current_shares_check" CHECK (("current_shares" >= (0)::numeric)),
    CONSTRAINT "asset_notes_dividend_yield_check" CHECK (("dividend_yield" >= (0)::numeric)),
    CONSTRAINT "asset_notes_review_frequency_check" CHECK (("review_frequency" = ANY (ARRAY['weekly'::"text", 'monthly'::"text", 'quarterly'::"text", 'annually'::"text"]))),
    CONSTRAINT "asset_notes_security_type_check" CHECK (("security_type" = ANY (ARRAY['stock'::"text", 'etf'::"text", 'mutual_fund'::"text", 'bond'::"text", 'option'::"text", 'other'::"text"]))),
    CONSTRAINT "asset_notes_sell_above_check" CHECK (("sell_above" > (0)::numeric)),
    CONSTRAINT "asset_notes_status_check" CHECK (("status" = ANY (ARRAY['active'::"text", 'watch_list'::"text", 'sold'::"text", 'deprecated'::"text"]))),
    CONSTRAINT "asset_notes_stop_loss_check" CHECK (("stop_loss" > (0)::numeric))
);


ALTER TABLE "public"."asset_notes" OWNER TO "postgres";


COMMENT ON TABLE "public"."asset_notes" IS 'Investment strategy notes and price targets for securities performance tracking';



CREATE TABLE IF NOT EXISTS "public"."document_accounts" (
    "document_id" "uuid" NOT NULL,
    "account_id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."document_accounts" OWNER TO "postgres";


COMMENT ON TABLE "public"."document_accounts" IS 'Many-to-many association between documents and accounts - handles consolidated statements';



CREATE TABLE IF NOT EXISTS "public"."documents" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "institution_id" "uuid" NOT NULL,
    "tax_year" integer NOT NULL,
    "document_type" "text" NOT NULL,
    "period_start" "date",
    "period_end" "date",
    "file_path" "text" NOT NULL,
    "file_name" "text" NOT NULL,
    "file_size" integer,
    "file_hash" "text" NOT NULL,
    "mime_type" "text" DEFAULT 'application/pdf'::"text",
    "is_amended" boolean DEFAULT false,
    "amends_document_id" "uuid",
    "version_number" integer DEFAULT 1,
    "processed_at" timestamp with time zone,
    "processed_by" "text" DEFAULT 'claude'::"text",
    "extraction_method" "text" DEFAULT 'claude_ai'::"text",
    "extraction_confidence" "text" DEFAULT 'needs_review'::"text" NOT NULL,
    "extraction_notes" "text",
    "needs_human_review" boolean DEFAULT false,
    "human_reviewed_at" timestamp with time zone,
    "raw_extraction" "jsonb",
    "structured_data" "jsonb",
    "summary_data" "jsonb",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "imported_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "chk_amendment_not_self" CHECK (("id" <> "amends_document_id")),
    CONSTRAINT "chk_period_dates" CHECK ((("period_start" IS NULL) OR ("period_end" IS NULL) OR ("period_start" <= "period_end"))),
    CONSTRAINT "documents_document_type_check" CHECK (("document_type" = ANY (ARRAY['statement'::"text", '1099'::"text", 'quickbooks_export'::"text", 'bank_statement'::"text", 'tax_return'::"text", 'k1'::"text", 'receipt'::"text", 'invoice'::"text", 'other'::"text"]))),
    CONSTRAINT "documents_extraction_confidence_check" CHECK (("extraction_confidence" = ANY (ARRAY['high'::"text", 'medium'::"text", 'low'::"text", 'needs_review'::"text", 'failed'::"text"]))),
    CONSTRAINT "documents_extraction_method_check" CHECK (("extraction_method" = ANY (ARRAY['claude_ai'::"text", 'ocr'::"text", 'manual'::"text", 'api_import'::"text"]))),
    CONSTRAINT "documents_tax_year_check" CHECK ((("tax_year" >= 2020) AND ("tax_year" <= 2035)))
);


ALTER TABLE "public"."documents" OWNER TO "postgres";


COMMENT ON TABLE "public"."documents" IS 'Source documents with extraction metadata - supports multi-account documents via junction table';



COMMENT ON COLUMN "public"."documents"."raw_extraction" IS 'Complete unprocessed extraction data from Claude for debugging and reprocessing';



COMMENT ON COLUMN "public"."documents"."summary_data" IS 'High-level summary data: 1099 totals, statement summaries for quick reference';



CREATE TABLE IF NOT EXISTS "public"."entities" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "entity_name" "text" NOT NULL,
    "entity_type" "text" NOT NULL,
    "tax_id" "text" NOT NULL,
    "tax_id_display" "text",
    "primary_taxpayer" "text",
    "tax_year_end" "text" DEFAULT '12-31'::"text",
    "georgia_resident" boolean DEFAULT true,
    "entity_status" "text" DEFAULT 'active'::"text",
    "formation_date" "date",
    "notes" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "chk_tax_year_end_format" CHECK (("tax_year_end" ~ '^\d{2}-\d{2}$'::"text")),
    CONSTRAINT "entities_entity_status_check" CHECK (("entity_status" = ANY (ARRAY['active'::"text", 'inactive'::"text", 'dissolved'::"text"]))),
    CONSTRAINT "entities_entity_type_check" CHECK (("entity_type" = ANY (ARRAY['individual'::"text", 's_corp'::"text", 'llc'::"text", 'partnership'::"text", 'c_corp'::"text", 'trust'::"text"])))
);


ALTER TABLE "public"."entities" OWNER TO "postgres";


COMMENT ON TABLE "public"."entities" IS 'Master table for all business entities and individual taxpayers - central hub for organizational structure';



CREATE TABLE IF NOT EXISTS "public"."institutions" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "entity_id" "uuid" NOT NULL,
    "institution_name" "text" NOT NULL,
    "institution_type" "text",
    "routing_number" "text",
    "swift_code" "text",
    "institution_address" "text",
    "primary_contact" "jsonb",
    "login_credentials" "jsonb",
    "document_delivery" "jsonb",
    "status" "text" DEFAULT 'active'::"text",
    "notes" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "institutions_institution_type_check" CHECK (("institution_type" = ANY (ARRAY['brokerage'::"text", 'bank'::"text", 'credit_union'::"text", 'insurance'::"text", 'retirement_plan'::"text", 'other'::"text"]))),
    CONSTRAINT "institutions_status_check" CHECK (("status" = ANY (ARRAY['active'::"text", 'inactive'::"text", 'closed'::"text"])))
);


ALTER TABLE "public"."institutions" OWNER TO "postgres";


COMMENT ON TABLE "public"."institutions" IS 'Financial institutions that hold accounts for entities - supports multiple institutions per entity';



CREATE TABLE IF NOT EXISTS "public"."liabilities" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "entity_id" "uuid" NOT NULL,
    "real_asset_id" "uuid",
    "liability_type" "text" NOT NULL,
    "lender_name" "text" NOT NULL,
    "account_number" "text",
    "original_amount" numeric(15,2) NOT NULL,
    "current_balance" numeric(15,2) NOT NULL,
    "interest_rate" numeric(5,3) NOT NULL,
    "loan_start_date" "date" NOT NULL,
    "maturity_date" "date",
    "monthly_payment" numeric(15,2) NOT NULL,
    "next_payment_date" "date",
    "escrow_amount" numeric(15,2),
    "status" "text" DEFAULT 'active'::"text",
    "notes" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "liabilities_liability_type_check" CHECK (("liability_type" = ANY (ARRAY['mortgage'::"text", 'home_equity'::"text", 'auto_loan'::"text", 'business_loan'::"text", 'personal_loan'::"text", 'other'::"text"]))),
    CONSTRAINT "liabilities_status_check" CHECK (("status" = ANY (ARRAY['active'::"text", 'paid_off'::"text", 'refinanced'::"text", 'transferred'::"text"])))
);


ALTER TABLE "public"."liabilities" OWNER TO "postgres";


COMMENT ON TABLE "public"."liabilities" IS 'Mortgages and long-term debt for net worth tracking - excludes inter-entity loans and credit cards';



CREATE TABLE IF NOT EXISTS "public"."real_assets" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "entity_id" "uuid" NOT NULL,
    "asset_type" "text" NOT NULL,
    "description" "text" NOT NULL,
    "address" "text",
    "purchase_date" "date",
    "purchase_price" numeric(15,2),
    "current_value" numeric(15,2) NOT NULL,
    "valuation_date" "date" NOT NULL,
    "valuation_source" "text",
    "monthly_income" numeric(15,2),
    "monthly_expense" numeric(15,2),
    "status" "text" DEFAULT 'active'::"text",
    "notes" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "real_assets_asset_type_check" CHECK (("asset_type" = ANY (ARRAY['primary_residence'::"text", 'rental_property'::"text", 'commercial_property'::"text", 'land'::"text", 'vacation_home'::"text", 'vehicle'::"text", 'other'::"text"]))),
    CONSTRAINT "real_assets_status_check" CHECK (("status" = ANY (ARRAY['active'::"text", 'pending_sale'::"text", 'sold'::"text", 'transferred'::"text"])))
);


ALTER TABLE "public"."real_assets" OWNER TO "postgres";


COMMENT ON TABLE "public"."real_assets" IS 'Physical properties and non-financial assets for complete net worth calculation';



CREATE TABLE IF NOT EXISTS "public"."tax_payments" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "entity_id" "uuid" NOT NULL,
    "account_id" "uuid",
    "tax_year" integer NOT NULL,
    "payment_type" "text" NOT NULL,
    "tax_authority" "text" NOT NULL,
    "payment_date" "date" NOT NULL,
    "due_date" "date",
    "amount" numeric(15,2) NOT NULL,
    "calculation_basis" "jsonb",
    "estimated_income" numeric(15,2),
    "estimated_tax_liability" numeric(15,2),
    "notes" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "tax_payments_amount_check" CHECK (("amount" > (0)::numeric)),
    CONSTRAINT "tax_payments_payment_type_check" CHECK (("payment_type" = ANY (ARRAY['est_q1'::"text", 'est_q2'::"text", 'estimated_q3'::"text", 'estimated_q4'::"text", 'extension'::"text", 'balance_due'::"text", 'amended_return'::"text", 'penalty'::"text", 'interest'::"text"]))),
    CONSTRAINT "tax_payments_tax_authority_check" CHECK (("tax_authority" = ANY (ARRAY['federal'::"text", 'georgia'::"text", 'other_state'::"text"]))),
    CONSTRAINT "tax_payments_tax_year_check" CHECK ((("tax_year" >= 2020) AND ("tax_year" <= 2030)))
);


ALTER TABLE "public"."tax_payments" OWNER TO "postgres";


COMMENT ON TABLE "public"."tax_payments" IS 'Quarterly estimated tax payments and annual tax liabilities for compliance tracking';



CREATE TABLE IF NOT EXISTS "public"."transactions" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "entity_id" "uuid" NOT NULL,
    "document_id" "uuid" NOT NULL,
    "account_id" "uuid" NOT NULL,
    "transaction_date" "date" NOT NULL,
    "settlement_date" "date",
    "transaction_type" "text" NOT NULL,
    "transaction_subtype" "text",
    "description" "text" NOT NULL,
    "amount" numeric(15,2) NOT NULL,
    "source" "text" NOT NULL,
    "security_info" "jsonb",
    "security_type" "text",
    "tax_category" "text" NOT NULL,
    "federal_taxable" boolean NOT NULL,
    "state_taxable" boolean NOT NULL,
    "tax_details" "jsonb",
    "source_transaction_id" "text",
    "source_reference" "text",
    "is_duplicate_of" "uuid",
    "duplicate_reason" "text",
    "needs_review" boolean DEFAULT false,
    "review_notes" "text",
    "confidence_score" numeric(3,2),
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "processed_by" "text" DEFAULT 'claude'::"text",
    CONSTRAINT "chk_duplicate_not_self" CHECK (("id" <> "is_duplicate_of")),
    CONSTRAINT "transactions_amount_check" CHECK (("amount" <> (0)::numeric)),
    CONSTRAINT "transactions_confidence_score_check" CHECK ((("confidence_score" >= (0)::numeric) AND ("confidence_score" <= (1)::numeric))),
    CONSTRAINT "transactions_security_type_check" CHECK (("security_type" = ANY (ARRAY['stock'::"text", 'bond'::"text", 'mutual_fund'::"text", 'etf'::"text", 'money_market'::"text", 'cd'::"text", 'option'::"text", 'other'::"text"]))),
    CONSTRAINT "transactions_source_check" CHECK (("source" = ANY (ARRAY['statement'::"text", 'qb_export'::"text", 'ledger'::"text"]))),
    CONSTRAINT "transactions_tax_category_check" CHECK (("tax_category" = ANY (ARRAY['ordinary_dividend'::"text", 'qualified_dividend'::"text", 'municipal_interest'::"text", 'corporate_interest'::"text", 'capital_gain_short'::"text", 'capital_gain_long'::"text", 'return_of_capital'::"text", 'tax_exempt'::"text", 'fee_expense'::"text", 'other'::"text"]))),
    CONSTRAINT "transactions_transaction_type_check" CHECK (("transaction_type" = ANY (ARRAY['dividend'::"text", 'interest'::"text", 'buy'::"text", 'sell'::"text", 'transfer_in'::"text", 'transfer_out'::"text", 'fee'::"text", 'return_of_capital'::"text", 'assignment'::"text", 'other'::"text"])))
);


ALTER TABLE "public"."transactions" OWNER TO "postgres";


COMMENT ON TABLE "public"."transactions" IS 'Individual financial transactions with comprehensive tax categorization and source tracking';



COMMENT ON COLUMN "public"."transactions"."amount" IS 'CRITICAL: Uses NUMERIC(15,2) to prevent floating-point errors in financial calculations';



COMMENT ON COLUMN "public"."transactions"."security_info" IS 'Flexible JSONB storage: {cusip, symbol, name, quantity, price, security_type}';



COMMENT ON COLUMN "public"."transactions"."tax_details" IS 'Complex tax scenarios: {issuer_state, taxpayer_state, amt_preference, section_199a}';



CREATE TABLE IF NOT EXISTS "public"."transfers" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "source_entity_id" "uuid" NOT NULL,
    "source_account_id" "uuid",
    "destination_entity_id" "uuid" NOT NULL,
    "destination_account_id" "uuid",
    "transfer_date" "date" NOT NULL,
    "amount" numeric(15,2) NOT NULL,
    "transfer_type" "text" NOT NULL,
    "purpose" "text" NOT NULL,
    "notes" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "chk_no_self_transfer" CHECK (("source_entity_id" <> "destination_entity_id")),
    CONSTRAINT "transfers_amount_check" CHECK (("amount" > (0)::numeric)),
    CONSTRAINT "transfers_transfer_type_check" CHECK (("transfer_type" = ANY (ARRAY['loan'::"text", 'distribution'::"text", 'capital_contribution'::"text", 'reimbursement'::"text", 'gift'::"text", 'repayment'::"text", 'other'::"text"])))
);


ALTER TABLE "public"."transfers" OWNER TO "postgres";


COMMENT ON TABLE "public"."transfers" IS 'Inter-entity money movements and loans for multi-entity financial management';



ALTER TABLE ONLY "public"."accounts"
    ADD CONSTRAINT "accounts_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."asset_notes"
    ADD CONSTRAINT "asset_notes_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."documents"
    ADD CONSTRAINT "documents_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."entities"
    ADD CONSTRAINT "entities_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."entities"
    ADD CONSTRAINT "entities_tax_id_key" UNIQUE ("tax_id");



ALTER TABLE ONLY "public"."institutions"
    ADD CONSTRAINT "institutions_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."liabilities"
    ADD CONSTRAINT "liabilities_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."real_assets"
    ADD CONSTRAINT "real_assets_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."tax_payments"
    ADD CONSTRAINT "tax_payments_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."transactions"
    ADD CONSTRAINT "transactions_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."transfers"
    ADD CONSTRAINT "transfers_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."document_accounts"
    ADD CONSTRAINT "uq_document_accounts" UNIQUE ("document_id", "account_id");



CREATE INDEX "idx_accounts_composite" ON "public"."accounts" USING "btree" ("entity_id", "institution_id", "account_status");



CREATE INDEX "idx_accounts_entity" ON "public"."accounts" USING "btree" ("entity_id");



CREATE INDEX "idx_accounts_institution" ON "public"."accounts" USING "btree" ("institution_id");



CREATE INDEX "idx_accounts_tax_attributes" ON "public"."accounts" USING "btree" ("is_tax_deferred", "is_tax_free", "requires_rmd") WHERE ("account_status" = 'active'::"text");



CREATE INDEX "idx_accounts_type" ON "public"."accounts" USING "btree" ("account_type");



CREATE INDEX "idx_asset_notes_account" ON "public"."asset_notes" USING "btree" ("account_id") WHERE ("account_id" IS NOT NULL);



CREATE INDEX "idx_asset_notes_alert_conditions" ON "public"."asset_notes" USING "gin" ("alert_conditions");



CREATE INDEX "idx_asset_notes_alerts" ON "public"."asset_notes" USING "btree" ("alert_enabled") WHERE ("alert_enabled" = true);



CREATE INDEX "idx_asset_notes_entity" ON "public"."asset_notes" USING "btree" ("entity_id");



CREATE INDEX "idx_asset_notes_review_date" ON "public"."asset_notes" USING "btree" ("next_review_date") WHERE ("next_review_date" IS NOT NULL);



CREATE INDEX "idx_asset_notes_status" ON "public"."asset_notes" USING "btree" ("status");



CREATE INDEX "idx_asset_notes_symbol" ON "public"."asset_notes" USING "btree" ("symbol");



CREATE INDEX "idx_document_accounts_acct" ON "public"."document_accounts" USING "btree" ("account_id");



CREATE INDEX "idx_document_accounts_doc" ON "public"."document_accounts" USING "btree" ("document_id");



CREATE INDEX "idx_documents_amendments" ON "public"."documents" USING "btree" ("amends_document_id") WHERE ("amends_document_id" IS NOT NULL);



CREATE INDEX "idx_documents_institution" ON "public"."documents" USING "btree" ("institution_id");



CREATE INDEX "idx_documents_processing" ON "public"."documents" USING "btree" ("extraction_confidence", "needs_human_review");



CREATE INDEX "idx_documents_raw_extraction" ON "public"."documents" USING "gin" ("raw_extraction");



CREATE INDEX "idx_documents_structured_data" ON "public"."documents" USING "gin" ("structured_data");



CREATE INDEX "idx_documents_summary_data" ON "public"."documents" USING "gin" ("summary_data");



CREATE INDEX "idx_documents_tax_year" ON "public"."documents" USING "btree" ("tax_year");



CREATE INDEX "idx_documents_type_period" ON "public"."documents" USING "btree" ("document_type", "period_start", "period_end");



CREATE INDEX "idx_entities_tax_id" ON "public"."entities" USING "btree" ("tax_id");



CREATE INDEX "idx_entities_type_status" ON "public"."entities" USING "btree" ("entity_type", "entity_status");



CREATE INDEX "idx_institutions_entity" ON "public"."institutions" USING "btree" ("entity_id");



CREATE INDEX "idx_institutions_name_status" ON "public"."institutions" USING "btree" ("institution_name", "status");



CREATE INDEX "idx_liabilities_asset" ON "public"."liabilities" USING "btree" ("real_asset_id") WHERE ("real_asset_id" IS NOT NULL);



CREATE INDEX "idx_liabilities_entity" ON "public"."liabilities" USING "btree" ("entity_id");



CREATE INDEX "idx_liabilities_maturity" ON "public"."liabilities" USING "btree" ("maturity_date") WHERE ("status" = 'active'::"text");



CREATE INDEX "idx_liabilities_status" ON "public"."liabilities" USING "btree" ("status");



CREATE INDEX "idx_liabilities_type" ON "public"."liabilities" USING "btree" ("liability_type");



CREATE INDEX "idx_real_assets_entity" ON "public"."real_assets" USING "btree" ("entity_id");



CREATE INDEX "idx_real_assets_status" ON "public"."real_assets" USING "btree" ("status");



CREATE INDEX "idx_real_assets_type" ON "public"."real_assets" USING "btree" ("asset_type");



CREATE INDEX "idx_tax_payments_authority" ON "public"."tax_payments" USING "btree" ("tax_authority");



CREATE INDEX "idx_tax_payments_calculation_basis" ON "public"."tax_payments" USING "gin" ("calculation_basis");



CREATE INDEX "idx_tax_payments_date" ON "public"."tax_payments" USING "btree" ("payment_date");



CREATE INDEX "idx_tax_payments_due_date" ON "public"."tax_payments" USING "btree" ("due_date") WHERE ("due_date" IS NOT NULL);



CREATE INDEX "idx_tax_payments_entity" ON "public"."tax_payments" USING "btree" ("entity_id");



CREATE INDEX "idx_tax_payments_entity_year" ON "public"."tax_payments" USING "btree" ("entity_id", "tax_year", "payment_type");



CREATE INDEX "idx_tax_payments_type" ON "public"."tax_payments" USING "btree" ("payment_type");



CREATE INDEX "idx_tax_payments_year" ON "public"."tax_payments" USING "btree" ("tax_year");



CREATE INDEX "idx_transactions_account" ON "public"."transactions" USING "btree" ("account_id");



CREATE INDEX "idx_transactions_amount" ON "public"."transactions" USING "btree" ("amount") WHERE ("abs"("amount") > (100)::numeric);



CREATE INDEX "idx_transactions_date" ON "public"."transactions" USING "btree" ("transaction_date");



CREATE INDEX "idx_transactions_date_entity" ON "public"."transactions" USING "btree" ("entity_id", "transaction_date");



CREATE INDEX "idx_transactions_document" ON "public"."transactions" USING "btree" ("document_id");



CREATE INDEX "idx_transactions_duplicates" ON "public"."transactions" USING "btree" ("is_duplicate_of") WHERE ("is_duplicate_of" IS NOT NULL);



CREATE INDEX "idx_transactions_entity" ON "public"."transactions" USING "btree" ("entity_id");



CREATE INDEX "idx_transactions_review" ON "public"."transactions" USING "btree" ("needs_review") WHERE ("needs_review" = true);



CREATE INDEX "idx_transactions_security_info" ON "public"."transactions" USING "gin" ("security_info");



CREATE INDEX "idx_transactions_security_type" ON "public"."transactions" USING "btree" ("security_type") WHERE ("security_type" IS NOT NULL);



CREATE INDEX "idx_transactions_source" ON "public"."transactions" USING "btree" ("source_transaction_id") WHERE ("source_transaction_id" IS NOT NULL);



CREATE INDEX "idx_transactions_tax_category" ON "public"."transactions" USING "btree" ("tax_category");



CREATE INDEX "idx_transactions_tax_details" ON "public"."transactions" USING "gin" ("tax_details");



CREATE INDEX "idx_transactions_tax_federal" ON "public"."transactions" USING "btree" ("federal_taxable", "transaction_date") WHERE ("federal_taxable" = true);



CREATE INDEX "idx_transactions_tax_state" ON "public"."transactions" USING "btree" ("state_taxable", "transaction_date") WHERE ("state_taxable" = true);



CREATE INDEX "idx_transactions_taxable" ON "public"."transactions" USING "btree" ("federal_taxable", "state_taxable");



CREATE INDEX "idx_transfers_date" ON "public"."transfers" USING "btree" ("transfer_date");



CREATE INDEX "idx_transfers_dest_entity" ON "public"."transfers" USING "btree" ("destination_entity_id");



CREATE INDEX "idx_transfers_entities" ON "public"."transfers" USING "btree" ("source_entity_id", "destination_entity_id", "transfer_date");



CREATE INDEX "idx_transfers_source_entity" ON "public"."transfers" USING "btree" ("source_entity_id");



CREATE INDEX "idx_transfers_type" ON "public"."transfers" USING "btree" ("transfer_type");



CREATE UNIQUE INDEX "uq_documents_file_hash" ON "public"."documents" USING "btree" ("file_hash");



ALTER TABLE ONLY "public"."accounts"
    ADD CONSTRAINT "accounts_entity_id_fkey" FOREIGN KEY ("entity_id") REFERENCES "public"."entities"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."accounts"
    ADD CONSTRAINT "accounts_institution_id_fkey" FOREIGN KEY ("institution_id") REFERENCES "public"."institutions"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."asset_notes"
    ADD CONSTRAINT "asset_notes_account_id_fkey" FOREIGN KEY ("account_id") REFERENCES "public"."accounts"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."asset_notes"
    ADD CONSTRAINT "asset_notes_entity_id_fkey" FOREIGN KEY ("entity_id") REFERENCES "public"."entities"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."document_accounts"
    ADD CONSTRAINT "document_accounts_account_id_fkey" FOREIGN KEY ("account_id") REFERENCES "public"."accounts"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."document_accounts"
    ADD CONSTRAINT "document_accounts_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "public"."documents"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."documents"
    ADD CONSTRAINT "documents_amends_document_id_fkey" FOREIGN KEY ("amends_document_id") REFERENCES "public"."documents"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."documents"
    ADD CONSTRAINT "documents_institution_id_fkey" FOREIGN KEY ("institution_id") REFERENCES "public"."institutions"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."institutions"
    ADD CONSTRAINT "institutions_entity_id_fkey" FOREIGN KEY ("entity_id") REFERENCES "public"."entities"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."liabilities"
    ADD CONSTRAINT "liabilities_entity_id_fkey" FOREIGN KEY ("entity_id") REFERENCES "public"."entities"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."liabilities"
    ADD CONSTRAINT "liabilities_real_asset_id_fkey" FOREIGN KEY ("real_asset_id") REFERENCES "public"."real_assets"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."real_assets"
    ADD CONSTRAINT "real_assets_entity_id_fkey" FOREIGN KEY ("entity_id") REFERENCES "public"."entities"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."tax_payments"
    ADD CONSTRAINT "tax_payments_account_id_fkey" FOREIGN KEY ("account_id") REFERENCES "public"."accounts"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."tax_payments"
    ADD CONSTRAINT "tax_payments_entity_id_fkey" FOREIGN KEY ("entity_id") REFERENCES "public"."entities"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."transactions"
    ADD CONSTRAINT "transactions_account_id_fkey" FOREIGN KEY ("account_id") REFERENCES "public"."accounts"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."transactions"
    ADD CONSTRAINT "transactions_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "public"."documents"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."transactions"
    ADD CONSTRAINT "transactions_entity_id_fkey" FOREIGN KEY ("entity_id") REFERENCES "public"."entities"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."transactions"
    ADD CONSTRAINT "transactions_is_duplicate_of_fkey" FOREIGN KEY ("is_duplicate_of") REFERENCES "public"."transactions"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."transfers"
    ADD CONSTRAINT "transfers_destination_account_id_fkey" FOREIGN KEY ("destination_account_id") REFERENCES "public"."accounts"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."transfers"
    ADD CONSTRAINT "transfers_destination_entity_id_fkey" FOREIGN KEY ("destination_entity_id") REFERENCES "public"."entities"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."transfers"
    ADD CONSTRAINT "transfers_source_account_id_fkey" FOREIGN KEY ("source_account_id") REFERENCES "public"."accounts"("id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."transfers"
    ADD CONSTRAINT "transfers_source_entity_id_fkey" FOREIGN KEY ("source_entity_id") REFERENCES "public"."entities"("id") ON DELETE RESTRICT;





ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";





GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";














































































































































































GRANT ALL ON TABLE "public"."accounts" TO "anon";
GRANT ALL ON TABLE "public"."accounts" TO "authenticated";
GRANT ALL ON TABLE "public"."accounts" TO "service_role";



GRANT ALL ON TABLE "public"."asset_notes" TO "anon";
GRANT ALL ON TABLE "public"."asset_notes" TO "authenticated";
GRANT ALL ON TABLE "public"."asset_notes" TO "service_role";



GRANT ALL ON TABLE "public"."document_accounts" TO "anon";
GRANT ALL ON TABLE "public"."document_accounts" TO "authenticated";
GRANT ALL ON TABLE "public"."document_accounts" TO "service_role";



GRANT ALL ON TABLE "public"."documents" TO "anon";
GRANT ALL ON TABLE "public"."documents" TO "authenticated";
GRANT ALL ON TABLE "public"."documents" TO "service_role";



GRANT ALL ON TABLE "public"."entities" TO "anon";
GRANT ALL ON TABLE "public"."entities" TO "authenticated";
GRANT ALL ON TABLE "public"."entities" TO "service_role";



GRANT ALL ON TABLE "public"."institutions" TO "anon";
GRANT ALL ON TABLE "public"."institutions" TO "authenticated";
GRANT ALL ON TABLE "public"."institutions" TO "service_role";



GRANT ALL ON TABLE "public"."liabilities" TO "anon";
GRANT ALL ON TABLE "public"."liabilities" TO "authenticated";
GRANT ALL ON TABLE "public"."liabilities" TO "service_role";



GRANT ALL ON TABLE "public"."real_assets" TO "anon";
GRANT ALL ON TABLE "public"."real_assets" TO "authenticated";
GRANT ALL ON TABLE "public"."real_assets" TO "service_role";



GRANT ALL ON TABLE "public"."tax_payments" TO "anon";
GRANT ALL ON TABLE "public"."tax_payments" TO "authenticated";
GRANT ALL ON TABLE "public"."tax_payments" TO "service_role";



GRANT ALL ON TABLE "public"."transactions" TO "anon";
GRANT ALL ON TABLE "public"."transactions" TO "authenticated";
GRANT ALL ON TABLE "public"."transactions" TO "service_role";



GRANT ALL ON TABLE "public"."transfers" TO "anon";
GRANT ALL ON TABLE "public"."transfers" TO "authenticated";
GRANT ALL ON TABLE "public"."transfers" TO "service_role";









ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "service_role";






























\unrestrict KWMctvCTM0iPaOObLsot2Ygqn7vQ06l2Lj9ixbJAtE1NdpSb59TRvzI8pde4c2t

RESET ALL;
