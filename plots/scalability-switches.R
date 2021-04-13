library(tidyverse)

csvPath = '/Users/isadorapedrinipossebon/Documents/UFRGS/Mestrado/projeto/floodlight-api-look-ahead-rl/outputs-consolidated/data/best-reward/comp-costs-A-B-C-As2-Bs2.csv'

# agent, num_iperfs, flow_size, time, memory, iter

data <- read_csv(csvPath, col_types = cols(
  agent = col_character(),
  num_iperfs = col_integer(),
  flow_size = col_character(),
  time = col_double(),
  memory = col_double(),
  iter = col_integer()
)) %>%
  mutate(flow_size = as_factor(flow_size)) %>%
  print
View


## Considera flow completion time de CADA fluxo.
## Devemos plotar a soma de todos os flow completion times. 
## Para saber o tempo que precisamos para transmitir X fluxos na rede
data1 <- data %>%
  # Selecionando apenas as colunas relevantes
  select(agent, num_iperfs, flow_size, time, memory, iter) %>%
  # Agrupamento considerando iterações - contabiliza tempo total do experimento
  group_by(agent, num_iperfs, flow_size, iter) %>%
  # Total flow completion time = tempo para terminar todos os fluxos
  summarize(
    memory_usage_mb = sum(memory)/1024
  ) %>%
  ungroup %>%
  # Agrupamento sem considerar iterações, para plot
  group_by(agent, num_iperfs, flow_size) %>%
  # Média/desvio padrão dos grupos
  summarize(
    average_memory = mean(memory_usage_mb),
    sd_memory = sd(memory_usage_mb)
  ) %>%
  ungroup %>%
  print


facet_labels <- c(
  `2` = "4 flows",
  `4` = "8 flows",
  `8` = "16 flows"
)

agent_labels <- c(
  "A" = "Usage heuristics",
  "B" = "Harmonic mean", 
  "C" = "Standard deviation",
  "F" = "Baseline",
  "A2" = "Usage heuristic - S2",
  "B2" = "Harmonic mean - S2",
  "F2" = "Baseline - S2"
)

data1 %>%
  ggplot(aes(x = flow_size, y = average_memory, fill = agent)) +
  geom_col(position = position_dodge()) +
  geom_errorbar(
    aes(
      ymin = average_memory - sd_memory,
      ymax = average_memory + sd_memory
    ),
    width = .2,
    position = position_dodge(.9)
  ) +
  #geom_text(aes(label = round(average_memory,2)), position = position_dodge(width=4.5), vjust=-1) +
  facet_wrap(~num_iperfs, labeller=as_labeller(facet_labels)) +
  theme_bw(base_size = 10) +
  scale_y_continuous(
    'Average memory usage (KBytes)',
    #seq(0, 40000, 1000),
    labels = waiver(), 
    limits = c(0, NA)
  ) +
  #scale_fill_brewer() +
  scale_fill_brewer(name = 'Reward function', label=as_labeller(agent_labels), palette="Pastel1") +
  xlab('Flow size (MBytes)') +
  theme(legend.position = c(0.86, 0.2))


