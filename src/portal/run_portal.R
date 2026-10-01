library(shiny)

# Set working dir to portal folder
setwd(dirname(rstudioapi::getSourceEditorContext()$path))

shiny::runApp("portal_app.R", port = 4040, launch.browser = TRUE)
