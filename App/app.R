# loading packages
library(shiny)
library(shinythemes)
library(plotly)
library(DT)
library(dplyr)

# reading github data
DataRaw <- read.csv("https://raw.githubusercontent.com/xmusphlkg/CNID/master/Data/AllData/WeeklyReport/latest.csv")
DataRaw$Date <- as.Date(DataRaw$Date)
DataRaw <- DataRaw[, c("Date", "Diseases", "DiseasesCN", "Cases", "Deaths", "Source")]

# Create Date range
DateRange <- seq.Date(min(DataRaw$Date), max(DataRaw$Date), by = "month")
# Find missing dates
MissingDates <- DateRange[!DateRange %in% unique(DataRaw$Date)]
DataRaw <- DataRaw |>
  rbind(
    data.frame(
      Date = MissingDates,
      Diseases = "Total",
      DiseasesCN = "总计",
      Cases = NA,
      Deaths = NA,
      Source = "missing"
    )
  )
# reorder the data
DataRaw <- DataRaw |>
  arrange(desc(Date))
diseases <- unique(DataRaw$Diseases)

ui <- navbarPage(
  theme = shinytheme("flatly"),
  title = "Chinese Notifiable Infectious Diseases (CNIDs) Dashboard",
  windowTitle = "CNIDs",
  tags$div(
    style = "position: absolute; top: 10px; right: 10px; z-index:10000; color: #18bc9c;",
    selectInput(
      inputId = "disease",
      label = NULL,
      choices = diseases,
      width = "200px",
      selected = "Total"
    )
  ),
  tabPanel(
    "Overview",
    column(
      width = 8,
      offset = 2,
      tags$h2("Reported Cases"),
      plotlyOutput("plot1", height = "300px"),
      tags$h2("Reported Deaths"),
      plotlyOutput("plot2", height = "300px"),
      tags$h2("Ratio of Reported Deaths to Cases"),
      plotlyOutput("plot3", height = "300px"),
    )
  ),
  tabPanel(
    "Data",
    column(
      width = 8,
      offset = 2,
      tags$h1("Data Table"),
      DT::dataTableOutput("table")
    )
  ),
  tabPanel(
    "About",
    column(
      width = 8,
      offset = 2,
      tags$h2("About"),
      tags$p("This is a dashboard for Chinese Notifiable Infectious Diseases (CNIDs) data."),
      tags$p("The data is from the website of China CDC Weekly."),
      tags$p("The dashboard is developed by Kangguo Li."),
      tags$p("The source code is available on Github:"),
      tags$a("Github", href = "https://github.com/xmusphlkg/CNID/"),
      tags$h2("Documents and Data"),
      tags$a("Get Report of NID", href = "https://github.com/xmusphlkg/CNID/tree/master/Report", target = "_blank"),
      tags$br(),
      tags$a("Get All Data", href = "https://github.com/xmusphlkg/CNID/tree/master/AllData/WeeklyReport", target = "_blank"),
      tags$br(),
      tags$a("Get Province Level Data", href = "https://github.com/xmusphlkg/CNID/tree/master/AllData/DatacenterReport", target = "_blank"),
      tags$h2("Cite:"),
      tags$p("CNIDs: Chinese Notifiable Infectious Diseases Sensing Project. https://github.com/xmusphlkg/CNID")
    )
  )
)

server <- function(input, output) {
  values <- reactiveValues(
    datasub = NULL
  )
  observeEvent(input$disease, {
    datasub <- DataRaw[DataRaw$Diseases == input$disease, ]
    datasub <- datasub |> arrange(desc(Date))
    values$datasub <- datasub
  })
  output$table <- renderDT(
    {
      datatable(
        {
          values$datasub
        },
        extensions = "Buttons",
        rownames = F,
        selection = "none",
        options =
          list(
            leftColumns = 6,
            # scrollX = TRUE,
            dom = "Bfrtip",
            bSort = FALSE,
            buttons = list(
              "pageLength",
              "copy",
              list(extend = "csv", filename = paste("CNIDS", sep = "-")),
              list(extend = "excel", filename = paste("CNIDS", sep = "-")),
              "print"
            ),
            initComplete = JS(
              "function(settings, json) {",
              "$(this.api().table().header()).css({'background-color': '#F39B7FFF', 'color': '#fff'});",
              "}"
            )
          )
      )
    },
    server = FALSE
  )
  output$plot1 <- renderPlotly({
    plot_ly(
      values$datasub,
      x = ~Date,
      y = ~Cases,
      type = "scatter",
      mode = "lines+markers",
      line = list(color = "#4DBBD5FF"),
      marker = list(color = "#4DBBD5FF"),
      name = "Cases"
    )
  })
  output$plot2 <- renderPlotly({
    plot_ly(
      values$datasub,
      x = ~Date,
      y = ~Deaths,
      type = "scatter",
      mode = "lines+markers",
      line = list(color = "#E64B35FF"),
      marker = list(color = "#E64B35FF"),
      name = "Deaths"
    )
  })
  output$plot3 <- renderPlotly({
    plot_ly(
      values$datasub,
      x = ~Date,
      y = ~ Deaths / Cases,
      type = "scatter",
      mode = "lines+markers",
      line = list(color = "#00A087FF"),
      marker = list(color = "#00A087FF"),
      name = "Ratio"
    )
  })
}

# Run the application
shinyApp(ui = ui, server = server)
