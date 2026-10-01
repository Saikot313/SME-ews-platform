CREATE TABLE IF NOT EXISTS portal_users (
    user_id             SERIAL PRIMARY KEY,
    username            VARCHAR(100) UNIQUE NOT NULL,
    password_hash       VARCHAR(255) NOT NULL,
    role                VARCHAR(20) NOT NULL,   
    borrower_id         VARCHAR(20),            
    full_name           VARCHAR(200),
    email               VARCHAR(200),
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_vault (
    doc_id              SERIAL PRIMARY KEY,
    borrower_id         VARCHAR(20) NOT NULL,
    doc_type            VARCHAR(50) NOT NULL,   
    doc_name            VARCHAR(200),
    file_path           VARCHAR(500),
    file_size_kb        INT,
    mime_type           VARCHAR(100),
    version             INT DEFAULT 1,
    expiry_date         DATE,
    upload_date         DATE,
    uploaded_by         VARCHAR(100),
    status              VARCHAR(20),            
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS application_status (
    app_id              SERIAL PRIMARY KEY,
    borrower_id         VARCHAR(20) NOT NULL,
    application_ref     VARCHAR(50) UNIQUE,
    facility_type       VARCHAR(50),
    requested_amount    NUMERIC(18,2),
    current_stage       VARCHAR(50),           
    stage_entered_date  DATE,
    stage_notes         TEXT,
    assigned_to         VARCHAR(100),
    status              VARCHAR(20),          
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS application_stage_history (
    history_id          SERIAL PRIMARY KEY,
    application_ref     VARCHAR(50),
    from_stage          VARCHAR(50),
    to_stage            VARCHAR(50),
    changed_date        TIMESTAMP,
    changed_by          VARCHAR(100),
    days_in_stage       INT,
    notes               TEXT
);

CREATE TABLE IF NOT EXISTS reminders (
    reminder_id         SERIAL PRIMARY KEY,
    borrower_id         VARCHAR(20),
    reminder_type       VARCHAR(50),          
    reference_id        INT,                  
    reminder_date       DATE,
    due_date            DATE,
    message             TEXT,
    status              VARCHAR(20),            
    sent_to_email       VARCHAR(200),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS communication_log (
    comm_id             SERIAL PRIMARY KEY,
    borrower_id         VARCHAR(20),
    channel             VARCHAR(20),            
    direction           VARCHAR(10),           
    subject             VARCHAR(300),
    message             TEXT,
    from_user           VARCHAR(100),
    to_user             VARCHAR(100),
    sent_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read             BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_doc_borrower ON document_vault(borrower_id, doc_type);
CREATE INDEX IF NOT EXISTS idx_doc_expiry ON document_vault(expiry_date, status);
CREATE INDEX IF NOT EXISTS idx_app_borrower ON application_status(borrower_id);
CREATE INDEX IF NOT EXISTS idx_reminder_borrower ON reminders(borrower_id, status);
CREATE INDEX IF NOT EXISTS idx_comm_borrower ON communication_log(borrower_id, sent_at);