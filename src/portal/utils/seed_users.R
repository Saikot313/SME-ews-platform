source("utils/auth.R")

seed_users <- function() {
    con <- get_con()
    on.exit(dbDisconnect(con))

    # Get first 5 borrowers for demo
    borrowers <- dbGetQuery(
        con,
        "SELECT borrower_id, borrower_name, relationship_manager
     FROM borrowers LIMIT 5"
    )

    # Admin
    tryCatch(
        create_user("admin", "admin123", "Admin",
            full_name = "System Admin",
            email = "admin@idlc.com"
        ),
        error = function(e) message("Admin exists")
    )

    # Analyst
    tryCatch(
        create_user("analyst1", "analyst123", "Analyst",
            full_name = "Credit Analyst",
            email = "analyst@idlc.com"
        ),
        error = function(e) message("Analyst exists")
    )

    # RM
    tryCatch(
        create_user("rm1", "rm123", "RM",
            full_name = "Relationship Manager",
            email = "rm@idlc.com"
        ),
        error = function(e) message("RM exists")
    )

    # Borrowers
    for (i in seq_len(nrow(borrowers))) {
        b <- borrowers[i, ]
        uname <- paste0("borrower", i)
        tryCatch(
            create_user(uname, "borrower123", "Borrower",
                borrower_id = b$borrower_id,
                full_name = b$borrower_name,
                email = paste0(uname, "@example.com")
            ),
            error = function(e) message(paste(uname, "exists"))
        )
    }

    message("Demo users seeded.")
    message("Admin: admin / admin123")
    message("Analyst: analyst1 / analyst123")
    message("RM: rm1 / rm123")
    message("Borrowers: borrower1..borrower5 / borrower123")
}

seed_users()
