DataRaw <- read.csv("https://ai.shinyweb.top/proxy/raw.githubusercontent.com/xmusphlkg/CNID/master/AllData/WeeklyReport/latest.csv")
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
