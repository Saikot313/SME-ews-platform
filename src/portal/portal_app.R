# =====================================================
# SME Borrower Portal - Main Shiny App
# Role-based: Borrower / RM / Analyst / Admin
# =====================================================

library(shiny)
library(shinydashboard)
library(shinyjs)
library(DBI)
library(RSQLite)
library(DT)
library(plotly)
library(dplyr)

# ---- Source utility modules ----
source("utils/auth.R")
source("utils/vault.R")
source("utils/applications.R")
source("utils/reminders.R")
source("utils/comms.R")

# ---- Global state ----
current_user <- reactiveVal(NULL)

# =====================================================
# LOGIN UI
# =====================================================
login_ui <- function() {
    div(
        style = "max-width: 400px; margin: 100px auto; padding: 30px;
             border: 1px solid #ddd; border-radius: 10px;
             box-shadow: 0 4px 12px rgba(0,0,0,0.08);",
        h2("SME Portal Login", style = "text-align: center; color: #2C3E50;"),
        br(),
        textInput("login_user", "Username", placeholder = "e.g., borrower1"),
        passwordInput("login_pass", "Password", placeholder = "••••••••"),
        br(),
        actionButton("login_btn", "Login",
            class = "btn-primary btn-block",
            style = "width: 100%;"
        ),
        br(), br(),
        div(
            style = "font-size: 12px; color: #666;",
            tags$b("Demo credentials:"),
            tags$br(),
            "Borrower: borrower1 / borrower123",
            tags$br(),
            "RM: rm1 / rm123",
            tags$br(),
            "Analyst: analyst1 / analyst123",
            tags$br(),
            "Admin: admin / admin123"
        ),
        br(),
        uiOutput("login_error")
    )
}

# =====================================================
# BORROWER DASHBOARD
# =====================================================
borrower_ui <- function(user) {
    dashboardPage(
        dashboardHeader(title = paste("Welcome,", user$full_name)),
        dashboardSidebar(
            sidebarMenu(
                menuItem("Dashboard", tabName = "dash", icon = icon("home")),
                menuItem("My Documents", tabName = "docs", icon = icon("folder")),
                menuItem("Applications", tabName = "apps", icon = icon("file-signature")),
                menuItem("Reminders", tabName = "rem", icon = icon("bell")),
                menuItem("Messages", tabName = "msg", icon = icon("envelope")),
                br(),
                actionButton("logout_btn", "Logout",
                    class = "btn-danger",
                    style = "margin-left: 15px;"
                )
            )
        ),
        dashboardBody(
            tabItems(
                tabItem(
                    "dash",
                    h3("My Snapshot"),
                    fluidRow(
                        valueBoxOutput("b_doc_count", width = 4),
                        valueBoxOutput("b_app_count", width = 4),
                        valueBoxOutput("b_rem_count", width = 4)
                    ),
                    br(),
                    h4("Recent Activity"),
                    DTOutput("b_recent_activity")
                ),
                tabItem(
                    "docs",
                    h3("My Document Vault"),
                    fluidRow(
                        column(4, fileInput("b_upload_file", "Upload New Document")),
                        column(4, selectInput("b_doc_type", "Document Type",
                            choices = DOC_TYPES
                        )),
                        column(
                            4,
                            textInput("b_doc_name", "Document Label (optional)")
                        )
                    ),
                    fluidRow(
                        column(4, dateInput("b_expiry", "Expiry Date (if applicable)",
                            value = NULL
                        )),
                        column(4, br(), actionButton("b_upload_btn", "Upload",
                            class = "btn-primary"
                        )),
                        column(4, br(), actionButton("b_refresh", "Refresh",
                            icon = icon("sync")
                        ))
                    ),
                    hr(),
                    DTOutput("b_doc_table")
                ),
                tabItem(
                    "apps",
                    h3("My Applications"),
                    DTOutput("b_app_table"),
                    br(),
                    h4("Application Stage History"),
                    selectInput("b_app_select", "Select Application",
                        choices = NULL
                    ),
                    DTOutput("b_app_history")
                ),
                tabItem(
                    "rem",
                    h3("My Reminders"),
                    DTOutput("b_rem_table")
                ),
                tabItem(
                    "msg",
                    h3("Messages from RM"),
                    DTOutput("b_msg_table"),
                    br(),
                    h4("Send Message to RM"),
                    textInput("b_msg_subject", "Subject"),
                    textAreaInput("b_msg_body", "Message", rows = 4),
                    actionButton("b_msg_send", "Send", class = "btn-primary")
                )
            )
        )
    )
}

# =====================================================
# RM DASHBOARD
# =====================================================
rm_ui <- function(user) {
    dashboardPage(
        dashboardHeader(title = paste("RM Portal -", user$full_name)),
        dashboardSidebar(
            sidebarMenu(
                menuItem("Overview", tabName = "ov", icon = icon("chart-pie")),
                menuItem("Borrowers", tabName = "bor", icon = icon("users")),
                menuItem("Documents Expiring", tabName = "exp", icon = icon("calendar-times")),
                menuItem("Reminders", tabName = "rem", icon = icon("bell")),
                menuItem("Application Pipeline", tabName = "pipe", icon = icon("stream")),
                br(),
                actionButton("logout_btn", "Logout",
                    class = "btn-danger",
                    style = "margin-left: 15px;"
                )
            )
        ),
        dashboardBody(
            tabItems(
                tabItem(
                    "ov",
                    h3("Portfolio Overview"),
                    fluidRow(
                        valueBoxOutput("rm_total_borrowers", width = 3),
                        valueBoxOutput("rm_total_docs", width = 3),
                        valueBoxOutput("rm_expiring", width = 3),
                        valueBoxOutput("rm_pending_apps", width = 3)
                    ),
                    br(),
                    fluidRow(
                        column(6, plotlyOutput("rm_doc_status_pie")),
                        column(6, plotlyOutput("rm_app_stage_bar"))
                    )
                ),
                tabItem(
                    "bor",
                    h3("Borrower Portfolio"),
                    DTOutput("rm_borrowers")
                ),
                tabItem(
                    "exp",
                    h3("Documents Expiring Soon"),
                    DTOutput("rm_expiring_docs"),
                    br(),
                    actionButton("rm_gen_reminders", "Generate Expiry Reminders",
                        class = "btn-warning"
                    )
                ),
                tabItem(
                    "rem",
                    h3("Reminder Management"),
                    DTOutput("rm_reminders"),
                    br(),
                    selectInput("rm_rem_select", "Mark as Sent",
                        choices = NULL
                    ),
                    actionButton("rm_mark_sent", "Mark Sent",
                        class = "btn-success"
                    )
                ),
                tabItem(
                    "pipe",
                    h3("Application Pipeline"),
                    DTOutput("rm_pipeline"),
                    br(),
                    h4("Advance Stage"),
                    fluidRow(
                        column(4, selectInput("pipe_ref", "Application Ref",
                            choices = NULL
                        )),
                        column(4, selectInput("pipe_to_stage", "Move To",
                            choices = STAGES
                        )),
                        column(4, br(), actionButton("pipe_advance", "Advance",
                            class = "btn-primary"
                        ))
                    ),
                    br(),
                    textAreaInput("pipe_notes", "Stage Notes", rows = 2)
                )
            )
        )
    )
}

# =====================================================
# ANALYST DASHBOARD
# =====================================================
analyst_ui <- function(user) {
    dashboardPage(
        dashboardHeader(title = paste("Analyst Portal -", user$full_name)),
        dashboardSidebar(
            sidebarMenu(
                menuItem("Document Coverage", tabName = "cov", icon = icon("check-circle")),
                menuItem("All Applications", tabName = "apps", icon = icon("file")),
                menuItem("Borrower Docs", tabName = "bdocs", icon = icon("folder-open")),
                br(),
                actionButton("logout_btn", "Logout",
                    class = "btn-danger",
                    style = "margin-left: 15px;"
                )
            )
        ),
        dashboardBody(
            tabItems(
                tabItem(
                    "cov",
                    h3("Document Coverage by Borrower"),
                    DTOutput("an_coverage"),
                    br(),
                    plotlyOutput("an_doc_type_bar")
                ),
                tabItem(
                    "apps",
                    h3("All Applications"),
                    DTOutput("an_apps")
                ),
                tabItem(
                    "bdocs",
                    h3("Borrower Documents"),
                    selectInput("an_borrower", "Select Borrower", choices = NULL),
                    DTOutput("an_borrower_docs")
                )
            )
        )
    )
}

# =====================================================
# MAIN UI
# =====================================================
ui <- fluidPage(
    useShinyjs(),
    uiOutput("main_ui")
)

# =====================================================
# SERVER
# =====================================================
server <- function(input, output, session) {
    # ---------- Login ----------
    observeEvent(input$login_btn, {
        user <- authenticate(input$login_user, input$login_pass)
        if (is.null(user)) {
            output$login_error <- renderUI({
                div(
                    style = "color: red; text-align: center;",
                    "Invalid credentials. Try again."
                )
            })
        } else {
            current_user(user)
        }
    })

    observeEvent(input$logout_btn, {
        current_user(NULL)
        session$reload()
    })

    # ---------- Route UI by role ----------
    output$main_ui <- renderUI({
        user <- current_user()
        if (is.null(user)) {
            return(login_ui())
        }
        if (user$role == "Borrower") {
            return(borrower_ui(user))
        }
        if (user$role == "RM") {
            return(rm_ui(user))
        }
        if (user$role == "Analyst") {
            return(analyst_ui(user))
        }
        if (user$role == "Admin") {
            return(rm_ui(user))
        } # Admin sees RM view
        login_ui()
    })

    # =====================================================
    # BORROWER SERVER
    # =====================================================
    observe({
        req(current_user()$role == "Borrower")
        user <- current_user()

        # ---- Value boxes ----
        output$b_doc_count <- renderValueBox({
            docs <- list_documents(borrower_id = user$borrower_id)
            valueBox(nrow(docs), "Documents",
                icon = icon("folder"),
                color = "blue"
            )
        })

        output$b_app_count <- renderValueBox({
            apps <- list_applications(borrower_id = user$borrower_id)
            valueBox(nrow(apps), "Applications",
                icon = icon("file"),
                color = "green"
            )
        })

        output$b_rem_count <- renderValueBox({
            rem <- list_reminders(
                borrower_id = user$borrower_id,
                status = "Pending"
            )
            valueBox(nrow(rem), "Pending Reminders",
                icon = icon("bell"),
                color = "yellow"
            )
        })

        # ---- Recent activity ----
        output$b_recent_activity <- renderDT({
            msgs <- list_messages(user$borrower_id)
            if (nrow(msgs) == 0) {
                return(datatable(data.frame(Message = "No recent activity"),
                    rownames = FALSE
                ))
            }
            datatable(
                head(
                    msgs[, c("sent_at", "direction", "subject", "message")],
                    10
                ),
                options = list(pageLength = 5, dom = "t"), rownames = FALSE
            )
        })

        # ---- Document upload ----
        observeEvent(input$b_upload_btn, {
            req(input$b_upload_file)
            dest <- file.path(
                VAULT_DIR,
                paste0(
                    user$borrower_id, "_",
                    Sys.Date(), "_",
                    input$b_upload_file$name
                )
            )
            file.copy(input$b_upload_file$datapath, dest)

            doc_label <- if (nzchar(input$b_doc_name)) {
                input$b_doc_name
            } else {
                input$b_upload_file$name
            }

            upload_document(
                borrower_id = user$borrower_id,
                doc_type = input$b_doc_type,
                doc_name = doc_label,
                file_path = dest,
                expiry_date = if (is.null(input$b_expiry)) {
                    NA
                } else {
                    as.character(input$b_expiry)
                },
                uploaded_by = user$username
            )
            showNotification("Document uploaded successfully.",
                type = "message"
            )
        })

        observeEvent(input$b_refresh, {
            refresh_doc_status()
            showNotification("Document status refreshed.", type = "message")
        })

        # ---- Document table ----
        output$b_doc_table <- renderDT({
            input$b_refresh
            docs <- list_documents(borrower_id = user$borrower_id)
            datatable(
                docs[, c(
                    "doc_id", "doc_type", "doc_name", "expiry_date",
                    "upload_date", "status"
                )],
                options = list(pageLength = 10), rownames = FALSE
            ) %>%
                formatStyle("status",
                    backgroundColor = styleEqual(
                        c("Valid", "ExpiringSoon", "Expired"),
                        c("#D5F5E3", "#FDEBD0", "#FADBD8")
                    )
                )
        })

        # ---- Applications ----
        output$b_app_table <- renderDT({
            apps <- list_applications(borrower_id = user$borrower_id)
            datatable(
                apps[, c(
                    "application_ref", "facility_type",
                    "requested_amount", "current_stage",
                    "stage_entered_date", "status"
                )],
                rownames = FALSE
            )
        })

        observe({
            apps <- list_applications(borrower_id = user$borrower_id)
            updateSelectInput(session, "b_app_select",
                choices = apps$application_ref
            )
        })

        output$b_app_history <- renderDT({
            req(input$b_app_select)
            hist <- get_application_history(input$b_app_select)
            datatable(hist, rownames = FALSE)
        })

        # ---- Reminders ----
        output$b_rem_table <- renderDT({
            rem <- list_reminders(borrower_id = user$borrower_id)
            datatable(rem[, c("reminder_type", "due_date", "message", "status")],
                rownames = FALSE
            )
        })

        # ---- Messages ----
        output$b_msg_table <- renderDT({
            msgs <- list_messages(user$borrower_id)
            datatable(msgs[, c("sent_at", "direction", "subject", "message")],
                rownames = FALSE
            )
        })

        observeEvent(input$b_msg_send, {
            req(input$b_msg_subject, input$b_msg_body)
            send_message(
                borrower_id = user$borrower_id,
                channel = "Portal",
                direction = "Outbound",
                subject = input$b_msg_subject,
                message = input$b_msg_body,
                from_user = user$username,
                to_user = "RM"
            )
            showNotification("Message sent to RM.", type = "message")
        })
    })

    # =====================================================
    # RM SERVER
    # =====================================================
    observe({
        req(current_user()$role %in% c("RM", "Admin"))

        output$rm_total_borrowers <- renderValueBox({
            con <- get_con()
            on.exit(dbDisconnect(con))
            n <- dbGetQuery(con, "SELECT COUNT(*) n FROM borrowers")$n
            valueBox(n, "Total Borrowers", icon = icon("users"), color = "blue")
        })

        output$rm_total_docs <- renderValueBox({
            con <- get_con()
            on.exit(dbDisconnect(con))
            n <- dbGetQuery(con, "SELECT COUNT(*) n FROM document_vault")$n
            valueBox(n, "Total Documents", icon = icon("folder"), color = "green")
        })

        output$rm_expiring <- renderValueBox({
            n <- nrow(get_expiring_documents(30))
            valueBox(n, "Expiring (30d)",
                icon = icon("exclamation-triangle"),
                color = "yellow"
            )
        })

        output$rm_pending_apps <- renderValueBox({
            con <- get_con()
            on.exit(dbDisconnect(con))
            n <- dbGetQuery(
                con,
                "SELECT COUNT(*) n FROM application_status WHERE status = 'InProgress'"
            )$n
            valueBox(n, "Active Applications", icon = icon("stream"), color = "purple")
        })

        # ---- Doc status pie ----
        output$rm_doc_status_pie <- renderPlotly({
            con <- get_con()
            on.exit(dbDisconnect(con))
            df <- dbGetQuery(
                con,
                "SELECT status, COUNT(*) n FROM document_vault GROUP BY status"
            )
            plot_ly(df,
                labels = ~status, values = ~n, type = "pie", hole = 0.4,
                marker = list(colors = c(
                    "Valid" = "#27AE60", "ExpiringSoon" = "#F39C12",
                    "Expired" = "#E74C3C", "Pending" = "#95A5A6"
                ))
            ) %>%
                layout(title = "Document Status Distribution")
        })

        # ---- App stage bar ----
        output$rm_app_stage_bar <- renderPlotly({
            con <- get_con()
            on.exit(dbDisconnect(con))
            df <- dbGetQuery(
                con,
                "SELECT current_stage, COUNT(*) n FROM application_status
         GROUP BY current_stage"
            )
            plot_ly(df,
                x = ~current_stage, y = ~n, type = "bar",
                marker = list(color = "#2C3E50")
            ) %>%
                layout(
                    title = "Applications by Stage",
                    xaxis = list(title = ""), yaxis = list(title = "Count")
                )
        })

        # ---- Borrowers table ----
        output$rm_borrowers <- renderDT({
            con <- get_con()
            on.exit(dbDisconnect(con))
            df <- dbGetQuery(
                con,
                "SELECT borrower_id, borrower_name, industry,
                relationship_manager, onboarding_date
         FROM borrowers"
            )
            datatable(df, options = list(pageLength = 15), rownames = FALSE)
        })

        # ---- Expiring docs ----
        output$rm_expiring_docs <- renderDT({
            df <- get_expiring_documents(30)
            datatable(
                df[, c(
                    "borrower_id", "borrower_name", "doc_type",
                    "doc_name", "expiry_date", "status"
                )],
                rownames = FALSE
            ) %>%
                formatStyle("status",
                    backgroundColor = styleEqual(
                        c("ExpiringSoon", "Expired"), c("#FDEBD0", "#FADBD8")
                    )
                )
        })

        observeEvent(input$rm_gen_reminders, {
            n <- generate_expiry_reminders(30)
            showNotification(paste(n, "reminders generated."), type = "message")
        })

        # ---- Reminders ----
        output$rm_reminders <- renderDT({
            rem <- list_reminders()
            datatable(
                rem[, c(
                    "reminder_id", "borrower_id", "reminder_type",
                    "due_date", "status", "message"
                )],
                rownames = FALSE
            )
        })

        observe({
            rem <- list_reminders(status = "Pending")
            updateSelectInput(session, "rm_rem_select",
                choices = rem$reminder_id
            )
        })

        observeEvent(input$rm_mark_sent, {
            req(input$rm_rem_select)
            mark_reminder_sent(as.integer(input$rm_rem_select))
            showNotification("Reminder marked as sent.", type = "message")
        })

        # ---- Pipeline ----
        output$rm_pipeline <- renderDT({
            con <- get_con()
            on.exit(dbDisconnect(con))
            df <- dbGetQuery(con, "
        SELECT a.*, b.borrower_name
        FROM application_status a
        JOIN borrowers b ON a.borrower_id = b.borrower_id
        ORDER BY a.stage_entered_date ASC
      ")
            datatable(df, options = list(pageLength = 10), rownames = FALSE)
        })

        observe({
            apps <- list_applications()
            updateSelectInput(session, "pipe_ref",
                choices = apps$application_ref
            )
        })

        observeEvent(input$pipe_advance, {
            req(input$pipe_ref, input$pipe_to_stage)
            ok <- advance_stage(
                input$pipe_ref, input$pipe_to_stage,
                current_user()$username, input$pipe_notes
            )
            if (ok) {
                showNotification("Stage advanced.", type = "message")
            } else {
                showNotification("Failed to advance.", type = "error")
            }
        })
    })

    # =====================================================
    # ANALYST SERVER
    # =====================================================
    observe({
        req(current_user()$role == "Analyst")

        output$an_coverage <- renderDT({
            con <- get_con()
            on.exit(dbDisconnect(con))
            df <- dbGetQuery(con, "
        SELECT b.borrower_id, b.borrower_name, b.industry,
               COUNT(d.doc_id) AS doc_count,
               SUM(CASE WHEN d.status = 'Expired' THEN 1 ELSE 0 END) AS expired,
               SUM(CASE WHEN d.status = 'ExpiringSoon' THEN 1 ELSE 0 END) AS expiring
        FROM borrowers b
        LEFT JOIN document_vault d ON b.borrower_id = d.borrower_id
        GROUP BY b.borrower_id
      ")
            datatable(df, options = list(pageLength = 15), rownames = FALSE)
        })

        output$an_doc_type_bar <- renderPlotly({
            con <- get_con()
            on.exit(dbDisconnect(con))
            df <- dbGetQuery(
                con,
                "SELECT doc_type, COUNT(*) n FROM document_vault GROUP BY doc_type"
            )
            plot_ly(df,
                x = ~doc_type, y = ~n, type = "bar",
                marker = list(color = "#3498DB")
            ) %>%
                layout(
                    title = "Documents by Type",
                    xaxis = list(title = ""), yaxis = list(title = "Count")
                )
        })

        output$an_apps <- renderDT({
            apps <- list_applications()
            datatable(apps, options = list(pageLength = 15), rownames = FALSE)
        })

        observe({
            con <- get_con()
            on.exit(dbDisconnect(con))
            b <- dbGetQuery(con, "SELECT borrower_id FROM borrowers")
            updateSelectInput(session, "an_borrower", choices = b$borrower_id)
        })

        output$an_borrower_docs <- renderDT({
            req(input$an_borrower)
            docs <- list_documents(borrower_id = input$an_borrower)
            datatable(docs, rownames = FALSE)
        })
    })
}

shinyApp(ui, server)
