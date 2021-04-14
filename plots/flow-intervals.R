library(tidyverse)

csvPath = '/Users/isadorapedrinipossebon/Documents/UFRGS/Mestrado/projeto/floodlight-api-look-ahead-rl/outputs-consolidated/data/look-ahead/iperfs-HET-v2.csv'

#agent, num_iperfs, port_number, original_size, transferred, retries, flow_completion_time, bandwidth, interval, workload, iter

data <- read_csv(csvPath, col_types = cols(
  agent = col_character(),
  num_iperfs = col_integer(),
  port_number = col_integer(),
  original_size = col_character(),
  transferred = col_character(),
  retries = col_character(),
  flow_completion_time = col_double(),
  bandwidth = col_character(),
  interval = col_integer(),
  workload = col_character(),
  iter = col_integer()
)) %>%
  mutate(original_size = as_factor(original_size)) %>%
  print



## Considera flow completion time de CADA fluxo.
## Devemos plotar a soma de todos os flow completion times. 
## Para saber o tempo que precisamos para transmitir X fluxos na rede
data1 <- data %>%
  # Selecionando apenas as colunas relevantes
  select(agent, num_iperfs, original_size, flow_completion_time, interval, workload, iter) %>%
  # Agrupamento considerando iterações - contabiliza tempo total do experimento
  group_by(agent, num_iperfs, original_size, interval, workload, iter) %>%
  # Total flow completion time = tempo para terminar todos os fluxos
  summarize(
    total_completion_time = sum(flow_completion_time)
  ) %>%
  ungroup %>%
  # Agrupamento sem considerar iterações, para plot
  group_by(agent, interval, workload) %>%
  # Média/desvio padrão dos grupos
  summarize(
    average_completion_time = mean(total_completion_time),
    sd_completion_time = sd(total_completion_time)
  ) %>%
  ungroup %>%
  print


facet_labels <- c(
  `75_25` = "25% Elephant Flows",
  `50_50` = "50% Elephant Flows",
  `25_75` = "75% Elephant Flows"
)

agent_labels <- c(
  "het-B_HET" = "Harmonic mean baseline (B)",
  "het-B_HET_LA" = "Harmonic mean + EFI (B-EFI)"
)

data1 %>%
  ggplot(aes(x=interval, y=average_completion_time)) +
  geom_line(aes(linetype=agent, color=agent), show.legend = F)+
  geom_point(aes(color=agent))+
  geom_text(aes(label = round(average_completion_time)), position = position_dodge(width=4.5), vjust=-.6) +
  facet_wrap(~workload, labeller=as_labeller(facet_labels), ncol=1) +
  xlab('Interval between connections (sec)') +
  ylab('Total flow completion time (sec)') +
  scale_x_discrete(limits=c(5,10,15)) +
  scale_y_continuous(limits = c(0, 14000)) +
  theme_bw() +
  scale_color_discrete(name = 'Reward function', label=as_labeller(agent_labels)) +
  theme(legend.position = "bottom")
