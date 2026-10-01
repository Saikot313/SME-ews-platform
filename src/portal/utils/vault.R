library(DBI)
library(RSQLite)

VAULT_DIR <- "../../data/portal_uploads"
if (!dir.exists(VAULT_DIR)) dir.create(VAULT_DIR, recursive = TRUE)

DOC_TYPES <- c(
    "TradeLicense", "TIN", "VAT", "BankStatement",
    "FinancialStatement", "KYC", "Other"
)

list_documents <- function(borrower_id = NULL, doc_type = NULL) {
    con <- get_con()
    on.exit(dbDisconnect(con))
    q <- "SELECT * FROM document_vault WHERE 1=1"
    params <- list()
    if (!is.null(borrower_id) && borrower_id != "") {
        q <- paste(q, "AND borrower_id = ?")
        params <- c(params, list(borrower_id))
    }
    if (!is.null(doc_type) && doc_type != "All") {
        q <- paste(q, "AND doc_type = ?")
        params <- c(params, list(doc_type))
    }
    q <- paste(q, "ORDER BY upload_date DESC")
    dbGetQuery(con, q, params = params)
}

upload_document <- function(borrower_id, doc_type, doc_name,
                            file_path, expiry_date, uploaded_by,
                            notes = "") {
    con <- get_con()
    on.exit(dbDisconnect(con))

    # Get file size
    size_kb <- round(file.info(file_path)$size / 1024)

    # Determine status
    status <- "Valid"
    if (!is.na(expiry_date) && expiry_date != "") {
        days_to_exp <- as.numeric(as.Date(expiry_date) - Sys.Date())
        if (days_to_exp < 0) {
            status <- "Expired"
        } else if (days_to_exp <= 30) status <- "ExpiringSoon"
    } else {
        expiry_date <- NA
    }

    dbExecute(con,
        "INSERT INTO document_vault
     (borrower_id, doc_type, doc_name, file_path, file_size_kb,
      expiry_date, upload_date, uploaded_by, status, notes)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        params = list(
            borrower_id, doc_type, doc_name, file_path,
            size_kb, as.character(expiry_date),
            as.character(Sys.Date()), uploaded_by, status, notes
        )
    )
}

delete_document <- function(doc_id) {
    con <- get_con()
    on.exit(dbDisconnect(con))
    dbExecute(con, "DELETE FROM document_vault WHERE doc_id = ?",
        params = list(doc_id)
    )
}

refresh_doc_status <- function() {
    con <- get_con()
    on.exit(dbDisconnect(con))
    today <- Sys.Date()
    dbExecute(con, "
    UPDATE document_vault SET status =
      CASE
        WHEN expiry_date IS NULL OR expiry_date = '' THEN 'Valid'
        WHEN date(expiry_date) < date(?) THEN 'Expired'
        WHEN julianday(expiry_date) - julianday(?) <= 30 THEN 'ExpiringSoon'
        ELSE 'Valid'
      END
  ", params = list(as.character(today), as.character(today)))
}

get_expiring_documents <- function(days = 30) {
    con <- get_con()
    on.exit(dbDisconnect(con))
    dbGetQuery(con, "
    SELECT d.*, b.borrower_name, b.relationship_manager
    FROM document_vault d
    JOIN borrowers b ON d.borrower_id = b.borrower_id
    WHERE d.expiry_date IS NOT NULL
      AND d.expiry_date != ''
      AND julianday(d.expiry_date) - julianday('now') BETWEEN 0 AND ?
    ORDER BY d.expiry_date ASC
  ", params = list(days))
}
