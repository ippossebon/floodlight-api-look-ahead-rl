import gym
from gym import spaces

# tutorial from: https://towardsdatascience.com/creating-a-custom-openai-gym-environment-for-stock-trading-be532be3910e

MAX_REWARD = 100 # avaliar qual é o melhor valor

class LoadBalanceEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, dataframe):
        super(LoadBalanceEnv, self).__init__()
        """
        In the constructor, we first define the type and shape of our action_space,
        which will contain all of the actions possible for an agent to take in the environment.

        Similarly, we’ll define the observation_space, which contains all of the
        environment’s data to be observed by the agent.

        Define action and observation space
        They must be gym.spaces objects
        """
        # pandas dataframe
        self.dataframe = dataframe

        self.reward_range = (0, MAX_REWARD)

        # Example when using discrete actions:
        self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS) #interface inidical

        # Actions of the format Buy x%, Sell x%, Hold, etc. ## temos 3 ações disponiveis, por isso o [3, 1]
        # qual a diferença entre o Box e o Discrete ?
        self.action_space = spaces.Box(low=np.array([0, 0]), high=np.array([3, 1]), dtype=np.float16)


        # Example for using image as input:
        self.observation_space = spaces.Box(low=0, high=255, shape=(HEIGHT, WIDTH, N_CHANNELS), dtype=np.uint8) # interface inicial
        # Prices contains the OHCL values for the last five prices ## TODO: nao entendi
        self.observation_space = spaces.Box(low=0, high=1, shape=(6, 6), dtype=np.float16)


    def step(self, action):
        # Execute one time step within the environment
        self._take_action(action)
        self.current_step += 1

        if self.current_step > len(self.df.loc[:, 'Open'].values) - 6:
            self.current_step = 0

        delay_modifier = (self.current_step / MAX_STEPS)

        reward = self.balance * delay_modifier
        done = self.net_worth <= 0
        obs = self._next_observation()

        return obs, reward, done, {}


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
        self.balance = INITIAL_ACCOUNT_BALANCE
        self.net_worth = INITIAL_ACCOUNT_BALANCE
        self.max_net_worth = INITIAL_ACCOUNT_BALANCE
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

        return self._next_observation()


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
