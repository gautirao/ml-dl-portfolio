-- Schema for LedgerMind Local

-- 1. Track uploaded files to prevent redundant processing and aid auditing
CREATE TABLE IF NOT EXISTS uploaded_files (
    id UUID PRIMARY KEY,
    filename VARCHAR NOT NULL,
    file_hash VARCHAR NOT NULL UNIQUE, -- SHA256 of file content
    bank_type VARCHAR NOT NULL,        -- 'MONZO', 'HSBC', etc.
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    row_count INTEGER
);

-- 2. Canonical Transaction Table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY,
    source_bank VARCHAR NOT NULL,
    source_file_id UUID REFERENCES uploaded_files(id),
    account_name VARCHAR,
    transaction_date DATE NOT NULL,
    posted_date DATE,
    description VARCHAR NOT NULL,
    merchant VARCHAR,
    amount DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP',
    direction VARCHAR CHECK (direction IN ('inflow', 'outflow')),
    category VARCHAR,
    subcategory VARCHAR,
    balance DECIMAL(18, 2),
    reference VARCHAR,
    transaction_fingerprint VARCHAR UNIQUE, -- Hash of (date, amount, description, bank, account)
    raw_row_json JSON,                      -- Keep the original row data for explainability
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Merchant Rules for future normalization (Mapping raw strings to clean merchants)
CREATE TABLE IF NOT EXISTS merchant_rules (
    id UUID PRIMARY KEY,
    pattern VARCHAR NOT NULL,      -- Regex or ILIKE pattern
    merchant_name VARCHAR NOT NULL,
    category VARCHAR,
    subcategory VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Audit Events for governance and explainability
CREATE TABLE IF NOT EXISTS audit_events (
    id UUID PRIMARY KEY,
    event_type VARCHAR NOT NULL,   -- 'FILE_UPLOAD', 'QUERY_EXECUTED', 'DB_INIT'
    description VARCHAR,
    metadata JSON,                 -- Structured data about the event
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_trans_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_trans_merchant ON transactions(merchant);
CREATE INDEX IF NOT EXISTS idx_trans_category ON transactions(category);

-- 5. Category Suggestions for Human-in-the-loop review
CREATE TABLE IF NOT EXISTS category_suggestions (
    id UUID PRIMARY KEY,
    transaction_id UUID,             -- Optional: can suggest for a specific transaction
    merchant_text VARCHAR,           -- The raw merchant/description text
    suggested_merchant VARCHAR,
    suggested_category VARCHAR,
    suggested_subcategory VARCHAR,
    confidence DECIMAL(5, 4),        -- 0.0 to 1.0
    evidence_json JSON,              -- Details on why this was suggested
    status VARCHAR DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'edited'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);
