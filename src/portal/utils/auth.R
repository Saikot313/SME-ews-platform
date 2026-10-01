library(digest)
library(DBI)
library(RSQLite)

DB_PATH <- "../../data/sme_ews.db"

get_con <- function() {
    dbConnect(RSQLite::SQLite(), DB_PATH)
}

hash_password <- function(pwd) {
    digest(pwd, algo = "sha256", serialize = FALSE)
}

authenticate <- function(username, password) {
    con <- get_con()
    on.exit(dbDisconnect(con))
    pwd_hash <- hash_password(password)
    df <- dbGetQuery(con,
        "SELECT user_id, username, role, borrower_id, full_name, email
     FROM portal_users
     WHERE username = ? AND password_hash = ? AND is_active = 1",
        params = list(username, pwd_hash)
    )
    if (nrow(df) == 0) {
        return(NULL)
    }
    as.list(df[1, ])
}

create_user <- function(username, password, role, borrower_id = NA,
                        full_name = "", email = "") {
    con <- get_con()
    on.exit(dbDisconnect(con))
    dbExecute(con,
        "INSERT INTO portal_users
     (username, password_hash, role, borrower_id, full_name, email)
     VALUES (?, ?, ?, ?, ?, ?)",
        params = list(
            username, hash_password(password), role,
            borrower_id, full_name, email
        )
    )
}
