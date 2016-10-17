## === Set Up ===
setwd("~/Engineering/Third Year/silverscreen/scripts/twitter_api")

## Libraries
library(ndjson)
library(ggplot2)

## Choose the sample file to look at
sample_file = "martian.json"

## Parse json to dataframe
tweets <- stream_in(sample_file)

