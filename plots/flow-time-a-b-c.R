library(tidyverse)

csvPath = '/Users/isadorapedrinipossebon/Documents/UFRGS/Mestrado/projeto/floodlight-api-look-ahead-rl/plots/data/iperf-reward-A-B-C-F.csv'

data <- read_csv(csvPath, col_types = cols(
  agent = col_character(),
  num_iperfs = col_integer(),
  port_number = col_integer(),
  original_size = col_character(),
  transfered = col_character(),
  retries = col_character(),
  flow_completion_time = col_double(),
  bandwidth = col_character(),
  iter = col_integer()
)) %>%
  mutate(original_size = as_factor(original_size)) %>%
  filter(!is.na(flow_completion_time)) %>%
  print


## Considera flow completion time de CADA fluxo.
## Devemos plotar a soma de todos os flow completion times. 
## Para saber o tempo que precisamos para transmitir X fluxos na rede
data1 <- data %>%
  # Selecionando apenas as colunas relevantes
  select(agent, num_iperfs, original_size, flow_completion_time, iter) %>%
  # Agrupamento considerando iterações
  group_by(agent, num_iperfs, original_size, iter) %>%
  # Total flow completion time = tempo para terminar todos os fluxos
  summarize(
    total_completion_time = sum(flow_completion_time)
  ) %>%
  # Agrupamento sem considerar iterações, para plot
  group_by(agent, num_iperfs, original_size) %>%
  # Média/desvio padrão dos grupos
  summarize(
    average_completion_time = mean(total_completion_time),
    sd_completion_time = sd(total_completion_time)
  ) %>%
  ungroup %>%
  print


facet_labels <- c(
  `2` = "4 flows",
  `4` = "8 flows",
  `8` = "16 flows"
)

data1 %>%
  ggplot(aes(x = original_size, y = average_completion_time, fill = agent)) +
  geom_col(position = position_dodge()) +
  geom_errorbar(
    aes(
      ymin = average_completion_time - sd_completion_time,
      ymax = average_completion_time + sd_completion_time
    ),
    width = .2,
    position = position_dodge(.9)
  ) +
  facet_wrap(~num_iperfs, scales = "free_y", labeller=as_labeller(facet_labels)) +
  theme_bw(base_size = 12) +
  scale_y_continuous(
    'Average total flow completion time (sec)',
    seq(0, 49000, 1000),
    labels = waiver(), 
    limits = c(0, NA)
  ) +
  scale_fill_discrete(name = 'Agent') +
  xlab('Flow size (Mbytes)')

