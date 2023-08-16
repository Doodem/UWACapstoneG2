library(dplyr)
library(stringdist)
library(qgraph)
library(readxl)
rm(list = ls())
setwd("C:/Users/Mitch/OneDrive/Documents/MASTER OF DATA SCIENCE/SEM 2 2023/CITS5553 Data Science Capstone Project/EDA")

# import
Tenders <- read_excel("C:/Users/Mitch/git/UWACapstoneG2/data/Tenders.xlsx")

# extract unique tender titles
TenderTitles <- Tenders %>% 
  filter(!is.na(`Tender Number`)) %>%
  select(`Contract Title`) %>% 
  distinct() %>% 
  na.omit()

# parameters
n <- 50

# calculate similarity matrix between tender titles
dist_m <- stringdistmatrix(TenderTitles$`Contract Title`[1:n], method = "jaccard")
dist_mi <- 1/dist_m

# create jpg to save graph
jpeg('tender_title_similarities_graph.jpg', width=2000, height=2000, unit='px', res = 300)

# generate graph, nodes as titles, thickness as strength of similarity
qgraph(dist_mi, layout='spring', vsize=3)

# add title and legend to connect titles to nodes
legend_labels <- paste(1:n, ": ", TenderTitles$`Contract Title`[1:n])
legend("bottomright", legend = legend_labels, col = "black", pch = 1, cex = 0.22)

# turn off to save
dev.off()
