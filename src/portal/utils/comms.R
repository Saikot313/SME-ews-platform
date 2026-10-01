# =====================================================
# Communication log: messages between borrower and RM
# =====================================================

library(DBI)
library(RSQLite)

list_messages <- function(borrower_id) {
    con <- get_con()
    on.exit(dbDisconnect(con))
    dbGetQuery(con, "
    SELECT * FROM communication_log
    WHERE borrower_id = ?
    ORDER BY sent_at DESC
  ", params = list(borrower_id))
}

send_message <- function(borrower_id, channel, direction, subject,
                         message, from_user, to_user) {
    con <- get_con()
    on.exit(dbDisconnect(con))
    dbExecute(con, "
    INSERT INTO communication_log
    (borrower_id, channel, direction, subject, message,
     from_user, to_user, sent_at, is_read)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
  ", params = list(
        borrower_id, channel, direction, subject,
        message, from_user, to_user,
        as.character(Sys.time())
    ))
}

mark_message_read <- function(comm_id) {
    con <- get_con()
    on.exit(dbDisconnect(con))
    dbExecute(con, "UPDATE communication_log SET is_read = 1 WHERE comm_id = ?",
        params = list(comm_id)
    )
}
