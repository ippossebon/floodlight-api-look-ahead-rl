import gym
from gym import spaces

# tutorial from: https://towardsdatascience.com/creating-a-custom-openai-gym-environment-for-stock-trading-be532be3910e


# reward = 1 / utilizacao_total_rede * (0.1 * num_steps)
MAX_REWARD = 1000

NUM_LINKS = 8# considerando rede de exemplo
NUM_FEATURES_PER_LINK = 3
NUM_FEATURES = 1 + (NUM_LINKS * NUM_FEATURES_PER_LINK)
NUM_DISCRETE_ACTIONS = 7
SNAPSHOTS_TO_CONSIDER = 5

INITIAL_NETWORK_USAGE = 0


class LoadBalanceEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, dataframe):
        super(LoadBalanceEnv, self).__init__()
        # pandas dataframe
        # serão os snapshots coeltados pela rede
        self.dataframe = dataframe

        # Cada (linha / snapshot) possui 31 features que nos interessam
        # numero de features = 1 (nro snapshot) + nro_links * 3
        # considerando rede de exemplo = 1 + (8*3) = 25
        self.observation_space = spaces.Box(
            low=0,
            high=1,
            shape=(SNAPSHOTS_TO_CONSIDER + 1, NUM_FEATURES), # snaphsots + atual
            dtype=np.float16
        )

        # Ações possíveis:
        # - manter
        # - dividir entre 2 menores caminhos
        # - dividir entre 3 menores caminhos
        # - usar menor caminho
        # - dividir entre 2 caminhos com menor utilização
        # - dividir entre 3 caminhos com menor utilização
        # - usar caminho com menor utilização
        self.action_space = spaces.Discrete(NUM_DISCRETE_ACTIONS) #interface inidical

        self.reward_range = (0, MAX_REWARD)

    def reset(self):
        """
         - Reset the state of the environment to an initial state
        It  will be called to periodically reset the environment to an initial
        state. This is followed by many steps through the environment, in which
        an action will be provided by the model and must be executed, and the next
        observation returned. This is also where rewards are calculated, more on this later.

        - Called any time a new environment is created or to reset an existing environment’s state.
        """
        # Reset the state of the environment to an initial state
        self.network_total_usage = INITIAL_NETWORK_USAGE
        self.net_worth = INITIAL_NETWORK_USAGE
        self.max_net_worth = INITIAL_NETWORK_USAGE

        self.shares_held = 0
        self.cost_basis = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0

        # Set the current step to a random point within the data frame
        # We set the current step to a random point within the data frame, because
        # it essentially gives our agent’s more unique experiences from the same data set.
        # The _next_observation method compiles the stock data for the last five time steps,
        # appends the agent’s account information, and scales all the values to between 0 and 1
        self.current_step = random.randint(0, len(self.df.loc[:, 'Open'].values) - 6)



    def step(self, action):
        # Execute one time step within the environment
        # It will take an action variable and will return a list of four things:
        # the next state, the reward for the current state, a boolean representing
        # whether the current episode of our model is done and some additional info on our problem.
        self._take_action(action)
        self.current_step += 1

        if self.current_step > len(self.df.loc[:, 'Open'].values) - 6:
            self.current_step = 0

        delay_modifier = (self.current_step / MAX_STEPS)

        reward = self.balance * delay_modifier
        done = self.net_worth <= 0
        obs = self._next_observation()

        return obs, reward, done, {}


    def _next_observation(self):
        # Get the data points for the last 5 days and scale to between 0-1
        frame = np.array([
            self.df.loc[self.current_step: self.current_step + 5, 'Open'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step: self.current_step + 5, 'High'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step: self.current_step + 5, 'Low'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step: self.current_step + 5, 'Close'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step: self.current_step + 5, 'Volume'].values / MAX_NUM_SHARES,
       ])

       # Append additional data and scale each value to between 0-1
       obs = np.append(frame, [[
            self.balance / MAX_ACCOUNT_BALANCE,
            self.max_net_worth / MAX_ACCOUNT_BALANCE,
            self.shares_held / MAX_NUM_SHARES,
            self.cost_basis / MAX_SHARE_PRICE,
            self.total_shares_sold / MAX_NUM_SHARES,
            self.total_sales_value / (MAX_NUM_SHARES * MAX_SHARE_PRICE),
        ]], axis=0)

        return obs


    def _take_action(self, action):
        # Set the current price to a random price within the time step
        current_price = random.uniform(
            self.df.loc[self.current_step, "Open"],
            self.df.loc[self.current_step, "Close"]
        )
        action_type = action[0]
        amount = action[1]

        if action_type < 1:
            # Buy amount % of balance in shares
            total_possible = self.balance / current_price
            shares_bought = total_possible * amount
            prev_cost = self.cost_basis * self.shares_held
            additional_cost = shares_bought * current_price
            self.balance -= additional_cost
            self.cost_basis = (prev_cost + additional_cost) / (self.shares_held + shares_bought)
            self.shares_held += shares_bought
        elif actionType < 2:
            # Sell amount % of shares held
            shares_sold = self.shares_held * amount .
            self.balance += shares_sold * current_price
            self.shares_held -= shares_sold
            self.total_shares_sold += shares_sold
            self.total_sales_value += shares_sold * current_price

        self.netWorth = self.balance + self.shares_held * current_price

        if self.net_worth > self.max_net_worth:
            self.max_net_worth = net_worth

        if self.shares_held == 0:
            self.cost_basis = 0



    def render(self, mode='human', close=False):
        """
        It may be called periodically to print a rendition of the environment. This could
        be as simple as a print statement, or as complicated as rendering a 3D
        environment using openGL. For this example, we will stick with print statements.
        """
        # Render the environment to the screen
        profit = self.net_worth - INITIAL_ACCOUNT_BALANCE

        print(f'Step: {self.current_step}')
        print(f'Balance: {self.balance}')
        print(f'Shares held: {self.shares_held} (Total sold: {self.total_shares_sold})')
        print(f'Avg cost for held shares: {self.cost_basis} (Total sales value: {self.total_sales_value})')
        print(f'Net worth: {self.net_worth} (Max net worth: {self.max_net_worth})')
        print(f'Profit: {profit}')
