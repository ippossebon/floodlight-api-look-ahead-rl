library(tidyverse)
library(magrittr) # needs to be run every time you start R and want to use %>%
library(dplyr)


data <- read_csv('./h1-as-server/snapshot-h2-client-h1-server.csv') %>%
  select(timeslot, switch_id, eth_src, eth_dst, everything())


data %>%
  mutate(gbyte_count = byte_count/1024/1024/1024) %>%
  filter(timeslot > 59) %>%
  filter(eth_src == '00:00:00:00:00:01') %>%
  filter(eth_dst == '00:00:00:00:00:04') %>%
  ggplot(aes(x = timeslot, y = gbyte_count)) +
    geom_point(size = 1) +
    theme_bw(base_size = 14) +
    scale_y_continuous(breaks = seq(0, 340, 50)) +
    facet_wrap(~ switch_id, ncol = 1)

View(
  data %>%
    filter(timeslot > 59) %>%
    filter(eth_src == '00:00:00:00:00:01') %>%
    filter(eth_dst == '00:00:00:00:00:04')
)
