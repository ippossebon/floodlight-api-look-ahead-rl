library(tidyverse)

csvPath = '/Users/isadorapedrinipossebon/Documents/UFRGS/Mestrado/projeto/floodlight-api-look-ahead-rl/outputs-consolidated/data/look-ahead/comp-costs-HET.csv'

# agent, num_iperfs, interval, workload, time, memory, iter
data <- read_csv(csvPath, col_types = cols(
  agent = col_character(),
  num_iperfs = col_character(),
  interval = col_integer(),
  workload = col_character(),
  time = col_double(),
  memory = col_double(),
  iter = col_integer()
)) %>%
  mutate(num_iperfs = as_factor(num_iperfs)) %>%
  mutate(workload = as_factor(workload)) %>%
  mutate(memory_mb = memory/1024) %>%
  print
View

facet_labels <- c(
  `25_75` = "75% Elephant Flows",
  `50_50` = "50% Elephant Flows",
  `75_25` = "25% Elephant Flows"
)

agent_labels <- c(
  "het-B_HET" = "Harmonic mean baseline (B)",
  "het-B_HET_LA" = "Harmonic mean + EF (B-EF)"
)


data %>%
  ggplot(aes(x = interval, y = memory_mb, fill = agent)) +
  geom_col(position = position_dodge()) +
  geom_text(aes(label = round(memory_mb,2)), position = position_dodge(width=4.5), vjust=-1) +
  facet_wrap(~workload, scales = "free_y", labeller=as_labeller(facet_labels)) +
  scale_fill_brewer(name = 'Reward function', label=as_labeller(agent_labels), palette="Pastel1") +
  ylab('Average memory usage (MBytes)') +
  theme_bw() +
  xlab('Interval between connections (sec)') +
  theme(legend.position = c(0.86, 0.2))

