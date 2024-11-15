from order_book import Order, Side
import gym
import numpy as np
from setuptools import setup

class ExchangeEnv(gym.Env):
    metadata = {"render_modes": [], "render_fps": 0}

    def __init__(self, exchange, depth_size):
        self.exchange = exchange
        self.depth_size = depth_size

    def step(self, action):
        if action.type == 'place':
            order = Order()

            if action.amount > 0:
                order.side = Side.Buy
                order.amount = action.amount
            else:
                order.side = Side.Sell
                order.amount = -action.amount

            self.exchange.place_market_order(order)

        is_end = next(self.exchange, None) == None
        state = self.exchange.state()

        observation = self.observation_from_state(state)
        pnl = state['last_pnl']

        return observation, pnl, is_end, False, None

    def reset(self, *args):
        self.exchange.reset()
        return self.observation_from_state(self.exchange.state())

    def render(self):
        return None

    def observation_from_state(self, state):
        order_book = state['last_order_book']
        position = state['market_position']

        observation = np.zeros(self.depth_size * 2 + 1)
        
        for i in range(self.depth_size):
            observation[i * 2] = order_book.bids[i].price
            observation[i * 2 + 1] = order_book.bids[i].amount

            observation[self.depth_size + i * 2] = order_book.asks[i].price
            observation[self.depth_size + i * 2 + 1] = order_book.asks[i].amount

        observation[-1] = position

        return observation
