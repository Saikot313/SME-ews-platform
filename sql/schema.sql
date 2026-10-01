

CREATE TABLE IF NOT EXISTS borrowers (
    borrower_id         VARCHAR(20) PRIMARY KEY,
    borrower_name       VARCHAR(200) NOT NULL,
    industry            VARCHAR(100),
    sub_industry        VARCHAR(100),
    incorporation_date  DATE,
    legal_structure     VARCHAR(50),     
    district            VARCHAR(100),
    relationship_manager VARCHAR(100),
    onboarding_date     DATE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS financial_statements (
    statement_id        SERIAL PRIMARY KEY,
    borrower_id         VARCHAR(20) REFERENCES borrowers(borrower_id),
    fiscal_year         INT NOT NULL,
    statement_type      VARCHAR(20),      
    source_file_path    VARCHAR(500),
    upload_date         DATE,
    extraction_status   VARCHAR(20),      
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS spread_line_items (
    spread_id           SERIAL PRIMARY KEY,
    statement_id        INT REFERENCES financial_statements(statement_id),
    borrower_id         VARCHAR(20),
    fiscal_year         INT,
    statement_category  VARCHAR(50),      
    standard_line_item  VARCHAR(100),     
    raw_line_item       VARCHAR(200),     
    amount              NUMERIC(18,2),
    confidence_score    NUMERIC(5,2),    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS financial_ratios (
    ratio_id            SERIAL PRIMARY KEY,
    borrower_id         VARCHAR(20),
    fiscal_year         INT,
    ratio_name          VARCHAR(50),
    ratio_value         NUMERIC(18,4),
    benchmark_value     NUMERIC(18,4),
    deviation_pct       NUMERIC(10,2),
    flag                VARCHAR(20),      
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loan_facilities (
    facility_id         VARCHAR(20) PRIMARY KEY,
    borrower_id         VARCHAR(20) REFERENCES borrowers(borrower_id),
    facility_type       VARCHAR(50),      
    sanctioned_amount   NUMERIC(18,2),
    disbursed_amount    NUMERIC(18,2),
    outstanding_amount  NUMERIC(18,2),
    interest_rate       NUMERIC(6,2),
    sanction_date       DATE,
    maturity_date       DATE,
    status              VARCHAR(20)       
);

CREATE TABLE IF NOT EXISTS transactions (
    txn_id              SERIAL PRIMARY KEY,
    borrower_id         VARCHAR(20),
    txn_date            DATE,
    txn_type            VARCHAR(20),      
    amount              NUMERIC(18,2),
    balance_after       NUMERIC(18,2),
    narration           VARCHAR(500),
    category            VARCHAR(50),      
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payment_history (
    payment_id          SERIAL PRIMARY KEY,
    facility_id         VARCHAR(20) REFERENCES loan_facilities(facility_id),
    borrower_id         VARCHAR(20),
    due_date            DATE,
    paid_date           DATE,
    due_amount          NUMERIC(18,2),
    paid_amount         NUMERIC(18,2),
    days_past_due       INT,
    status              VARCHAR(20)       
);

CREATE TABLE IF NOT EXISTS cib_queries (
    query_id            SERIAL PRIMARY KEY,
    borrower_id         VARCHAR(20),
    query_date          DATE,
    query_purpose       VARCHAR(100),
    institution_count   INT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ews_signals (
    signal_id           SERIAL PRIMARY KEY,
    borrower_id         VARCHAR(20),
    signal_date         DATE,
    signal_type         VARCHAR(100),    
    signal_value        NUMERIC(18,4),
    severity            VARCHAR(20),      
    rule_id             VARCHAR(50),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borrower_zones (
    zone_id             SERIAL PRIMARY KEY,
    borrower_id         VARCHAR(20),
    as_of_date          DATE,
    zone                VARCHAR(20),      
    total_score         NUMERIC(10,2),
    active_signals      INT,
    previous_zone       VARCHAR(20),
    zone_changed_date   DATE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id            SERIAL PRIMARY KEY,
    borrower_id         VARCHAR(20),
    alert_date          TIMESTAMP,
    alert_type          VARCHAR(50),
    alert_message       TEXT,
    severity            VARCHAR(20),
    notified_to         VARCHAR(200),     
    notification_status VARCHAR(20),      
    acknowledged        BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS industry_benchmark (
    benchmark_id        SERIAL PRIMARY KEY,
    industry            VARCHAR(100),
    ratio_name          VARCHAR(50),
    p25_value           NUMERIC(18,4),
    p50_value           NUMERIC(18,4),
    p75_value           NUMERIC(18,4),
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_vault (
    doc_id              SERIAL PRIMARY KEY,
    borrower_id         VARCHAR(20),
    doc_type            VARCHAR(50),      
    doc_name            VARCHAR(200),
    file_path           VARCHAR(500),
    expiry_date         DATE,
    upload_date         DATE,
    uploaded_by         VARCHAR(100),
    status              VARCHAR(20),     
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_spread_borrower ON spread_line_items(borrower_id, fiscal_year);
CREATE INDEX idx_ratio_borrower ON financial_ratios(borrower_id, fiscal_year);
CREATE INDEX idx_txn_borrower_date ON transactions(borrower_id, txn_date);
CREATE INDEX idx_ews_borrower_date ON ews_signals(borrower_id, signal_date);
CREATE INDEX idx_zone_borrower_date ON borrower_zones(borrower_id, as_of_date);
CREATE INDEX idx_alerts_borrower ON alerts(borrower_id, alert_date);