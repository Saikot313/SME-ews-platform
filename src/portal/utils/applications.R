STAGES <- c(
    "Submitted", "InitialReview", "CreditAssessment",
    "Approval", "Disbursement", "Disbursed", "Rejected"
)

list_applications <- function(borrower_id = NULL) {
    con <- get_con()
    on.exit(dbDisconnect(con))
    q <- "SELECT * FROM application_status WHERE 1=1"
    params <- list()
    if (!is.null(borrower_id) && borrower_id != "") {
        q <- paste(q, "AND borrower_id = ?")
        params <- c(params, list(borrower_id))
    }
    q <- paste(q, "ORDER BY created_at DESC")
    dbGetQuery(con, q, params = params)
}

get_application_history <- function(application_ref) {
    con <- get_con()
    on.exit(dbDisconnect(con))
    dbGetQuery(con, "
    SELECT * FROM application_stage_history
    WHERE application_ref = ?
    ORDER BY changed_date ASC
  ", params = list(application_ref))
}

advance_stage <- function(application_ref, to_stage, changed_by, notes = "") {
    con <- get_con()
    on.exit(dbDisconnect(con))

    current <- dbGetQuery(con,
        "SELECT * FROM application_status WHERE application_ref = ?",
        params = list(application_ref)
    )

    if (nrow(current) == 0) {
        return(FALSE)
    }

    from_stage <- current$current_stage[1]
    stage_entered <- as.Date(current$stage_entered_date[1])
    days_in_stage <- as.numeric(Sys.Date() - stage_entered)

    dbExecute(con, "
    INSERT INTO application_stage_history
    (application_ref, from_stage, to_stage, changed_date,
     changed_by, days_in_stage, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  ", params = list(
        application_ref, from_stage, to_stage,
        as.character(Sys.time()), changed_by,
        days_in_stage, notes
    ))

    dbExecute(con, "
    UPDATE application_status
    SET current_stage = ?,
        stage_entered_date = ?,
        stage_notes = ?,
        status = CASE WHEN ? IN ('Disbursed','Rejected')
                      THEN 'Completed' ELSE 'InProgress' END
    WHERE application_ref = ?
  ", params = list(
        to_stage, as.character(Sys.Date()),
        notes, to_stage, application_ref
    ))
    TRUE
}
