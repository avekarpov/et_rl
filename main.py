from gym_exchange.envs.exchange import Exchange
import gym

exchange = Exchange('/home/artem/Downloads/Market data/Market data/gazp', init=False)
env = gym.make('ExchangeEnv', exchange=exchange)

for i in range(1):
    state = env.reset()
    

