# Run once to install all required R packages
pkgs <- c(
    "shiny", "shinydashboard", "shinyjs",
    "DBI", "RSQLite",
    "DT", "plotly", "ggplot2",
    "dplyr", "tidyr", "lubridate",
    "digest", "rstudioapi"
)

install_if_missing <- function(p) {
    if (!requireNamespace(p, quietly = TRUE)) {
        install.packages(p, repos = "https://cloud.r-project.org")
    }
}

invisible(lapply(pkgs, install_if_missing))
message("All R packages installed.")
