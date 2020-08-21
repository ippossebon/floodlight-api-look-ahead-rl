from load_balance_with_floodlight import LoadBalanceEnv

print('Vai instanciar env')
env = LoadBalanceEnv(num_flows = 10, source_port = 1, source_switch = 0, target_port = 1, target_switch = 2)
print('Feito.')
