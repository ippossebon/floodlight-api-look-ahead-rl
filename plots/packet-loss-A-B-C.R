library(tidyverse)

csvPath = '/Users/isadorapedrinipossebon/Documents/UFRGS/Mestrado/projeto/floodlight-api-look-ahead-rl/plots/iperfs-A-B-C-E-F.csv'

data <- read_csv(csvPath, col_types = cols(
  agent = col_character(),
  num_iperfs = col_integer(),
  port_number = col_integer(),
  original_size = col_character(),
  transferred = col_double(),
  received = col_double(),
  retries = col_character(),
  flow_completion_time = col_double(),
  bandwidth = col_character(),
  iter = col_integer()
)) %>%
  #View %>%
  mutate(original_size = as_factor(original_size)) %>%
  filter(!is.na(flow_completion_time)) %>%
  filter(!is.na(received)) %>%
  print

data %>% 
  filter(agent == 'B1', original_size == '50M', num_iperfs == 2) %>%
  View
  

data1 <- data %>%
  # Selecionando apenas as colunas relevantes
  select(agent, port_number, num_iperfs, original_size, received) %>%
  # Transforma original_size em inteiro para manipular
  mutate(mbytes_size = as.integer(gsub('M', '', original_size))) %>%
  # Cada pacote tem 8KB
  mutate(total_packets = mbytes_size * 1024 / 8) %>%
  # Calcula quantidade de pacotes transferidos
  mutate(received_packets = as.integer(received * 1024 / 8)) %>%
  # Calcula quantidade de pacotes perdidos
  mutate(lost_packets = total_packets - received_packets) %>%
  # Ignora pacotes enviados em excesso
  mutate(lost_packets = ifelse(lost_packets < 0, 0, lost_packets)) %>%
  mutate(lost_packets = as.integer(lost_packets)) %>%
  # Calcula a proporção de pacotes perdidos
  mutate(loss_rate = lost_packets / total_packets * 100) %>%
  group_by(agent, num_iperfs, original_size) %>%
  summarize(
    avg_loss_rate = mean(loss_rate),
    sd_loss_rate = sd(loss_rate)
  ) %>%
  print


facet_labels <- c(
  `2` = "2 flows",
  `4` = "4 flows",
  `8` = "8 flows"
)

data1 %>%
  ggplot(aes(x = original_size, y = avg_loss_rate, fill = agent)) +
  geom_col(position = position_dodge()) +
  geom_errorbar(
    aes(
      ymin = avg_loss_rate - sd_loss_rate,
      ymax = avg_loss_rate + sd_loss_rate
    ),
    width = .2,
    position = position_dodge(.9)
  ) +
  facet_wrap(~num_iperfs, scales = "free_y", labeller=as_labeller(facet_labels)) +
  theme_bw(base_size = 12) +
  scale_y_continuous(
    'Average packet loss rate (%)',
    seq(0, 100, 1),
    labels = waiver(), 
    limits = c(0, NA)
  ) +
  scale_fill_discrete(name = 'Agent') +
  xlab('Flow size (Mbytes)')

