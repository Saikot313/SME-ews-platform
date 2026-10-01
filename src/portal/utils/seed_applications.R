# =====================================================
# Seed sample loan applications for testing
# =====================================================

source("utils/auth.R")

seed_applications <- function() {
    con <- get_con()
    on.exit(dbDisconnect(con))

    borrowers <- dbGetQuery(
        con,
        "SELECT borrower_id FROM borrowers LIMIT 20"
    )

    stages <- c(
        "Submitted", "InitialReview", "CreditAssessment",
        "Approval", "Disbursement", "Disbursed", "Rejected"
    )

    for (i in seq_len(nrow(borrowers))) {
        bid <- borrowers$borrower_id[i]
        ref <- paste0("APP", format(Sys.Date(), "%Y"), 1000 + i)
        stage <- sample(stages, 1)
        status <- if (stage %in% c("Disbursed", "Rejected")) {
            "Completed"
        } else {
            "InProgress"
        }

        existing <- dbGetQuery(con,
            "SELECT app_id FROM application_status WHERE application_ref = ?",
            params = list(ref)
        )
        if (nrow(existing) > 0) next

        dbExecute(con, "
      INSERT INTO application_status
      (borrower_id, application_ref, facility_type, requested_amount,
       current_stage, stage_entered_date, status, assigned_to)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ", params = list(
            bid, ref,
            sample(c("Term Loan", "Working Capital", "LC", "OD"), 1),
            round(runif(1, 5e6, 5e7), 2),
            stage,
            as.character(Sys.Date() - sample(1:60, 1)),
            status,
            "RM"
        ))
    }
    message("Seeded applications.")
}

seed_applications()
