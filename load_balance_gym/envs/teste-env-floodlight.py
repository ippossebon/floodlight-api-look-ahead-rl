from load_balance_with_floodlight import LoadBalanceEnv

env = LoadBalanceEnv(num_flows = 10, source_port = 1, source_switch = 0, target_port = 1, target_switch = 2)
env.getState()
print('Feito.')
