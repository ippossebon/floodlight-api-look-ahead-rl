library(tidyverse)
library(dplyr)
library(ggplot2)
library(readr)


data <- read_csv('isadora.csv') %>%
  select(timeslot, switch_id, eth_src, eth_dst, everything())


data %>%
  ggplot(aes(x = timeslot, y = byte_count)) +
    geom_point(size = 1) +
    theme_bw(base_size = 14) +
    scale_y_continuous(breaks = seq(0, 340, 50)) +
    facet_wrap(~ switch_id, ncol = 1)

View(data)

