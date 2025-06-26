from exchange.tester import Tester
from exchange.plotter import ExtendedPlotter
from exchange.adaptor import Adaptor
from exchange.primitives import Quantity, Side, MarketOrder
from gym import Env, spaces
from datetime import timedelta
import numpy as np


class ExchangeEnv(Env):
    a = 10
    k = 0.5
    slippage_fine = -100
    N = 5
    T = timedelta(minutes=5)
    Fee = Quantity('0.01')
    
    def __init__(self):
        super().__init__()

        self.depth = ExchangeEnv.N

        self.tester = Tester()
        self.adaptor = Adaptor(self.tester.router)
        self.plotter = ExtendedPlotter(self.tester.router)
        self.plotter.add_builder(self.adaptor)
        self.plotter.add_builder(self.tester.me)

        self.adaptor.set_window_size(ExchangeEnv.T)
        self.adaptor.set_fee_percent(ExchangeEnv.Fee)

        self.action_space = spaces.Box(low=0, high=1.0, shape=(3,), dtype=np.float32)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(self.depth * 4 + 5,), dtype=np.float32)

    def set_dir(self, dir_path):
        self.tester.set_dir(dir_path)

        self.tester.runner.init_order_book()

    def step(self, action):
        force_reward = None

        if abs(action[0]) >= 0.8:
            side = Side.Buy if action[1] <= 0.5 else Side.Sell
            quantity = Quantity(str(action[2]))

            summary_market_order = self.tester.uoc.summary_market_order
            new_quantity = summary_market_order.side.sidded(summary_market_order.quantity) + side.sidded(quantity)

            (new_side, new_quantity) = Side.unsidded(new_quantity)

            if self.adaptor.order_book[new_side][0].quantity < new_quantity:
                force_reward = ExchangeEnv.slippage_fine
            else:
                self.adaptor.place_market_order(MarketOrder(side, quantity))

        is_done = not self.tester.step()

        self.plotter.draw()

        obs = []
        for ask in self.adaptor.order_book.asks[0:self.depth]:
            obs.append(np.float32(ask.price))
            obs.append(np.float32(ask.quantity))
        for bid in self.adaptor.order_book.bids[0:self.depth]:
            obs.append(np.float32(bid.price))
            obs.append(np.float32(bid.quantity))

        assert len(obs) == self.depth * 4

        state = self.adaptor.wallet_state

        if state is None:
            obs.append(0)
            obs.append(0)    
            reward = 0
        else:
            obs.append(np.float32(state.position))
            obs.append(np.float32(state.finalized_balance))
            reward = ExchangeEnv.scaled_sigmoid(np.float32(state.pnl))

        if force_reward is not None:
            reward = force_reward

        obs.append(action[0])
        obs.append(action[1])
        obs.append(action[2])

        return obs, reward, is_done, False, {}

    def reset(self, *, seed = None, options = None):
        self.tester.reset()
        self.adaptor.reset()
        self.plotter.reset()

        self.tester.runner.init_order_book()

        obs = []
        for ask in self.adaptor.order_book.asks[0:self.depth]:
            obs.append(np.float32(ask.price))
            obs.append(np.float32(ask.quantity))
        for bid in self.adaptor.order_book.bids[0:self.depth]:
            obs.append(np.float32(bid.price))
            obs.append(np.float32(bid.quantity))
        
        obs.append(0)
        obs.append(0)
        obs.append(0)
        obs.append(0)
        obs.append(0)

        return obs, {}
    
    @staticmethod
    def scaled_sigmoid(x):
        a = ExchangeEnv.a
        k = ExchangeEnv.k

        if abs(x) > a:
            if x < 0:
                return -a
            else:
                return a

        x = np.clip(x, -a * 2, a * 2)
        exp = np.exp(-k * x)
        exp = np.clip(exp, 1e-10, 1e10)
        return a * (2 / (1 + exp) - 1)
