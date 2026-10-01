library(DBI)
library(RSQLite)

list_reminders <- function(borrower_id = NULL, status = NULL) {
    con <- get_con()
    on.exit(dbDisconnect(con))
    q <- "SELECT * FROM reminders WHERE 1=1"
    params <- list()
    if (!is.null(borrower_id) && borrower_id != "") {
        q <- paste(q, "AND borrower_id = ?")
        params <- c(params, list(borrower_id))
    }
    if (!is.null(status) && status != "All") {
        q <- paste(q, "AND status = ?")
        params <- c(params, list(status))
    }
    q <- paste(q, "ORDER BY due_date ASC")
    dbGetQuery(con, q, params = params)
}

create_reminder <- function(borrower_id, reminder_type, reference_id,
                            due_date, message, sent_to_email) {
    con <- get_con()
    on.exit(dbDisconnect(con))
    dbExecute(con, "
    INSERT INTO reminders
    (borrower_id, reminder_type, reference_id, reminder_date,
     due_date, message, status, sent_to_email)
    VALUES (?, ?, ?, ?, ?, ?, 'Pending', ?)
  ", params = list(
        borrower_id, reminder_type, reference_id,
        as.character(Sys.Date()), as.character(due_date),
        message, sent_to_email
    ))
}

mark_reminder_sent <- function(reminder_id) {
    con <- get_con()
    on.exit(dbDisconnect(con))
    dbExecute(con, "UPDATE reminders SET status = 'Sent' WHERE reminder_id = ?",
        params = list(reminder_id)
    )
}

generate_expiry_reminders <- function(days_ahead = 30) {
    expiring <- get_expiring_documents(days_ahead)
    if (nrow(expiring) == 0) {
        return(0)
    }

    con <- get_con()
    on.exit(dbDisconnect(con))

    count <- 0
    for (i in seq_len(nrow(expiring))) {
        d <- expiring[i, ]

        existing <- dbGetQuery(con, "
      SELECT reminder_id FROM reminders
      WHERE reference_id = ? AND reminder_type = 'DocExpiry'
        AND status IN ('Pending','Sent')
    ", params = list(d$doc_id))

        if (nrow(existing) > 0) next

        msg <- paste0(
            "Document '", d$doc_name, "' (", d$doc_type,
            ") for borrower ", d$borrower_id,
            " expires on ", d$expiry_date, "."
        )

        dbExecute(con, "
      INSERT INTO reminders
      (borrower_id, reminder_type, reference_id, reminder_date,
       due_date, message, status, sent_to_email)
      VALUES (?, 'DocExpiry', ?, ?, ?, ?, 'Pending', ?)
    ", params = list(
            d$borrower_id, d$doc_id,
            as.character(Sys.Date()),
            as.character(d$expiry_date),
            msg, "rm@idlc.com"
        ))
        count <- count + 1
    }
    count
}
