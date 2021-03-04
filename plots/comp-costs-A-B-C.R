library(tidyverse)

csvPath = '/Users/isadorapedrinipossebon/Documents/UFRGS/Mestrado/projeto/floodlight-api-look-ahead-rl/outputs-consolidated/data/best-reward/comp-costs-A-B-C.csv'

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
    memory_usage = sum(memory)
  ) %>%
  ungroup %>%
  # Agrupamento sem considerar iterações, para plot
  group_by(agent, num_iperfs, flow_size) %>%
  # Média/desvio padrão dos grupos
  summarize(
    average_memory = mean(memory_usage),
    sd_memory = sd(memory_usage)
  ) %>%
  ungroup %>%
  print


facet_labels <- c(
  `2` = "2 flows",
  `4` = "4 flows",
  `8` = "8 flows"
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
  facet_wrap(~num_iperfs, labeller=as_labeller(facet_labels)) +
  theme_bw(base_size = 12) +
  scale_y_continuous(
    'Average memory usage (KB)',
    #seq(0, 40000, 1000),
    labels = waiver(), 
    limits = c(0, NA)
  ) +
  scale_fill_discrete(name = 'Agent') +
  xlab('Flow size (Mbytes)') +
  scale_fill_brewer(palette="Accent")

