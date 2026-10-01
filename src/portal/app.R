library(shiny)
library(DBI)
library(RSQLite)
library(ggplot2)
library(DT)
library(plotly)
library(dplyr)

DB_PATH <- "../../data/sme_ews.db"

get_con <- function() {
    dbConnect(RSQLite::SQLite(), DB_PATH)
}

ui <- navbarPage(
    title = "SME Early Warning System",
    theme = NULL,

    # ---- Tab 1: Overview ----
    tabPanel(
        "Overview",
        fluidRow(
            column(3, valueBoxOutput("total_borrowers", width = 12)),
            column(3, valueBoxOutput("green_count", width = 12)),
            column(3, valueBoxOutput("amber_count", width = 12)),
            column(3, valueBoxOutput("red_count", width = 12))
        ),
        br(),
        fluidRow(
            column(6, plotlyOutput("zone_donut", height = "350px")),
            column(6, plotlyOutput("signal_bar", height = "350px"))
        ),
        br(),
        h4("Portfolio Zone Distribution Over Time"),
        plotlyOutput("zone_trend", height = "350px")
    ),

    # ---- Tab 2: Borrower Watchlist ----
    tabPanel(
        "Watchlist",
        fluidRow(
            column(
                3,
                selectInput("zone_filter", "Zone:",
                    choices = c("All", "Red", "Amber", "Green"), selected = "All"
                )
            ),
            column(
                3,
                selectInput("industry_filter", "Industry:",
                    choices = c("All"), selected = "All"
                )
            ),
            column(3, br(), downloadButton("download_watchlist", "Download CSV"))
        ),
        br(),
        DTOutput("watchlist_table")
    ),

    # ---- Tab 3: Borrower Deep Dive ----
    tabPanel(
        "Borrower Detail",
        fluidRow(
            column(
                4,
                selectInput("borrower_select", "Select Borrower:",
                    choices = NULL
                )
            )
        ),
        br(),
        fluidRow(
            column(6, h4("Active Signals"), DTOutput("signal_table")),
            column(6, h4("Recent Alerts"), DTOutput("alert_table"))
        ),
        br(),
        h4("Transaction Trend"),
        plotlyOutput("txn_trend", height = "350px")
    ),

    # ---- Tab 4: Signal Analytics ----
    tabPanel(
        "Signal Analytics",
        fluidRow(
            column(6, plotlyOutput("signal_type_freq", height = "400px")),
            column(6, plotlyOutput("signal_severity", height = "400px"))
        )
    )
)

# ---------------- Server ----------------
server <- function(input, output, session) {
    # ---- Reactive: borrowers list ----
    borrowers_df <- reactive({
        con <- get_con()
        df <- dbGetQuery(con, "SELECT borrower_id, borrower_name, industry FROM borrowers")
        dbDisconnect(con)
        df
    })

    observe({
        updateSelectInput(session, "borrower_select",
            choices = borrowers_df()$borrower_id
        )
        updateSelectInput(session, "industry_filter",
            choices = c("All", unique(borrowers_df()$industry))
        )
    })

    # ---- Reactive: latest zones ----
    latest_zones <- reactive({
        con <- get_con()
        df <- dbGetQuery(con, "
      SELECT z.*, b.borrower_name, b.industry, b.relationship_manager
      FROM borrower_zones z
      JOIN borrowers b ON z.borrower_id = b.borrower_id
      WHERE z.as_of_date = (SELECT MAX(as_of_date) FROM borrower_zones)
    ")
        dbDisconnect(con)
        df
    })

    # ---- Value boxes ----
    output$total_borrowers <- renderValueBox({
        valueBox(nrow(latest_zones()), "Total Borrowers", color = "blue", icon = icon("users"))
    })
    output$green_count <- renderValueBox({
        valueBox(sum(latest_zones()$zone == "Green"), "Green", color = "green", icon = icon("check"))
    })
    output$amber_count <- renderValueBox({
        valueBox(sum(latest_zones()$zone == "Amber"), "Amber", color = "yellow", icon = icon("exclamation"))
    })
    output$red_count <- renderValueBox({
        valueBox(sum(latest_zones()$zone == "Red"), "Red", color = "red", icon = icon("triangle-exclamation"))
    })

    # ---- Zone donut ----
    output$zone_donut <- renderPlotly({
        df <- latest_zones() %>% count(zone)
        plot_ly(df,
            labels = ~zone, values = ~n, type = "pie", hole = 0.5,
            marker = list(colors = c(
                "Green" = "#27AE60", "Amber" = "#F39C12", "Red" = "#E74C3C"
            ))
        ) %>%
            layout(title = "Current Zone Distribution")
    })

    # ---- Signal bar ----
    output$signal_bar <- renderPlotly({
        con <- get_con()
        df <- dbGetQuery(con, "
      SELECT signal_type, COUNT(*) as n FROM ews_signals
      GROUP BY signal_type ORDER BY n DESC
    ")
        dbDisconnect(con)
        plot_ly(df,
            x = ~signal_type, y = ~n, type = "bar",
            marker = list(color = "#2C3E50")
        ) %>%
            layout(
                title = "Signal Frequency", xaxis = list(title = ""),
                yaxis = list(title = "Count")
            )
    })

    # ---- Zone trend ----
    output$zone_trend <- renderPlotly({
        con <- get_con()
        df <- dbGetQuery(con, "
      SELECT as_of_date, zone, COUNT(*) as n
      FROM borrower_zones GROUP BY as_of_date, zone
    ")
        dbDisconnect(con)
        plot_ly(df,
            x = ~as_of_date, y = ~n, color = ~zone, type = "scatter",
            mode = "lines+markers",
            colors = c("Green" = "#27AE60", "Amber" = "#F39C12", "Red" = "#E74C3C")
        ) %>%
            layout(
                title = "Zone Trend Over Time", xaxis = list(title = ""),
                yaxis = list(title = "Borrowers")
            )
    })

    # ---- Watchlist ----
    watchlist_data <- reactive({
        df <- latest_zones()
        if (input$zone_filter != "All") df <- df[df$zone == input$zone_filter, ]
        if (input$industry_filter != "All") df <- df[df$industry == input$industry_filter, ]
        df[, c(
            "borrower_id", "borrower_name", "industry", "zone",
            "total_score", "active_signals", "previous_zone",
            "relationship_manager"
        )]
    })

    output$watchlist_table <- renderDT({
        datatable(watchlist_data(),
            options = list(pageLength = 15),
            rownames = FALSE
        ) %>%
            formatStyle("zone",
                backgroundColor = styleEqual(
                    c("Green", "Amber", "Red"),
                    c("#D5F5E3", "#FDEBD0", "#FADBD8")
                )
            )
    })

    output$download_watchlist <- downloadHandler(
        filename = function() paste0("watchlist_", Sys.Date(), ".csv"),
        content = function(file) write.csv(watchlist_data(), file, row.names = FALSE)
    )

    # ---- Borrower detail ----
    output$signal_table <- renderDT({
        req(input$borrower_select)
        con <- get_con()
        df <- dbGetQuery(con, "
      SELECT signal_date, signal_type, signal_value, severity
      FROM ews_signals WHERE borrower_id = ?
      ORDER BY signal_date DESC
    ", params = list(input$borrower_select))
        dbDisconnect(con)
        datatable(df, options = list(pageLength = 10, dom = "t"), rownames = FALSE)
    })

    output$alert_table <- renderDT({
        req(input$borrower_select)
        con <- get_con()
        df <- dbGetQuery(con, "
      SELECT alert_date, alert_type, severity, alert_message
      FROM alerts WHERE borrower_id = ?
      ORDER BY alert_date DESC LIMIT 10
    ", params = list(input$borrower_select))
        dbDisconnect(con)
        datatable(df, options = list(pageLength = 10, dom = "t"), rownames = FALSE)
    })

    output$txn_trend <- renderPlotly({
        req(input$borrower_select)
        con <- get_con()
        df <- dbGetQuery(con, "
      SELECT txn_date, amount, txn_type, balance_after
      FROM transactions WHERE borrower_id = ?
      ORDER BY txn_date
    ", params = list(input$borrower_select))
        dbDisconnect(con)
        if (nrow(df) == 0) {
            return(plotly_empty())
        }
        df$txn_date <- as.Date(df$txn_date)

        p1 <- plot_ly(df,
            x = ~txn_date, y = ~balance_after, type = "scatter",
            mode = "lines", name = "Balance"
        ) %>%
            layout(
                yaxis = list(title = "Balance (BDT)"),
                xaxis = list(title = ""),
                title = "Daily Balance Trend"
            )
        p1
    })

    # ---- Signal analytics ----
    output$signal_type_freq <- renderPlotly({
        con <- get_con()
        df <- dbGetQuery(con, "
      SELECT signal_type, COUNT(*) as n FROM ews_signals
      GROUP BY signal_type ORDER BY n DESC
    ")
        dbDisconnect(con)
        plot_ly(df,
            x = ~n, y = ~ reorder(signal_type, n), type = "bar",
            orientation = "h", marker = list(color = "#3498DB")
        ) %>%
            layout(
                title = "Signals by Type", xaxis = list(title = "Count"),
                yaxis = list(title = "")
            )
    })

    output$signal_severity <- renderPlotly({
        con <- get_con()
        df <- dbGetQuery(con, "
      SELECT severity, COUNT(*) as n FROM ews_signals GROUP BY severity
    ")
        dbDisconnect(con)
        plot_ly(df,
            labels = ~severity, values = ~n, type = "pie",
            marker = list(colors = c(
                "High" = "#E74C3C", "Medium" = "#F39C12", "Low" = "#27AE60"
            ))
        ) %>%
            layout(title = "Signals by Severity")
    })
}

shinyApp(ui, server)
