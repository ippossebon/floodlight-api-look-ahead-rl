library(ggplot2)
library(readr)


data <- read.csv("~/Documents/UFRGS/Mestrado/projeto/floodlight-api-look-ahead-rl/plots/data/iperf-consolidated-A1-and-F.csv") %>%
  select(agent, num_iperfs, original_size, flow_completion_time, everything())


# data %>%
#   ggplot(aes(x = Original.Size..MBytes, y = Flow.completion.time..sec)) +
#   geom_point(size = 1) +
#   theme_bw(base_size = 14)

ggplot(data, aes(original_size, flow_completion_time, fill = agent)) +
  geom_bar(stat="identity", position = "dodge") + 
  scale_fill_brewer(palette = "Set1")

View(data)


