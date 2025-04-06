from __future__ import annotations 
from exchange.events import *
from exchange.primitives import *
from exchange.logging import Logger
from datetime import timedelta
from typing import List
from copy import deepcopy as copy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Adaptor(Logger):
    class WalletState:
        def __init__(self, side: Side, price: Price, quantity: Quantity, ts: Timestamp):
            self.balance = -side.sidded(quantity * price)
            self.position = side.sidded(quantity)
            
            self.side = side
            self.price = price
            
            self.ts = ts

        def with_fill(self, event: UserFillEvent) -> Adaptor.WalletState:
            fill = event.user_fill

            state = copy(self)
            state.balance -= fill.side.sidded(fill.quantity * fill.price)
            state.position += fill.side.sidded(fill.quantity)
            state.price = fill.price
            state.ts = event.ts

            return state
        
        def with_trade(self, event: TradeEvent) -> Adaptor.WalletState:
            state = copy(self)
            state.price = event.trade.price
            state.ts = event.ts

            return state

        @property
        def pnl(self):
            return self.balance + self.position * self.price


    def __init__(self, router, window_size=timedelta(minutes=5)):
        super().__init__()

        self.router = router
        self.router.add_consumer(self)

        self.window_size = window_size
        self.wallet_states: List[Adaptor.WalletState] = []
        
        self.last_snapshot = None

        self.strategy = None

    def set_strategy(self, strategy):
        self.strategy = strategy

    def on_user_market_order_placed(self, event):
        pass

    def on_user_fill(self, event: UserFillEvent):
        self._log_event(event)

        fill = event.user_fill

        if len(self.wallet_states) == 0:
            self.wallet_states.append(Adaptor.WalletState(fill.side, fill.price, fill.quantity, event.ts))
        else:
            self.wallet_states.append(self.wallet_states[-1].with_fill(event))
            self._clear()

        self._push_state()

    def on_order_book_update(self, event: OrderBookUpdateEvent):
        self._log_event(event)

        self.last_snapshot = event.snapshot

        self._push_state()

    def on_trade(self, event: TradeEvent):
        self._log_event(event)

        if len(self.wallet_states) != 0:
            self.wallet_states.append(self.wallet_states[-1].with_trade(event))
            self._clear()
        
        self._push_state()

    def place_market_order(self, order: MarketOrder):
        self.router.on_place_user_market_order(PlaceUserMarketOrderEvent(order, self.router.ts))

    def _clear(self):
        if self.window_size != timedelta():
            if self.wallet_states[0].ts + self.window_size <= self.wallet_states[-1].ts:
                last_state = self.wallet_states.pop(0)

                while self.wallet_states[0].ts + self.window_size < self.wallet_states[-1].ts:
                    last_state = self.wallet_states.pop(0)

                for state in self.wallet_states:
                    state.balance -= last_state.balance
                    state.position -= last_state.position

    def _push_state(self):
        if self.strategy is not None:
            # TODO: implement
            self.strategy.on_state(None)


    def init_axs(self):
        _, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 6))

        self.ax_pnl = ax1
        self.ax_pnl.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax_pnl.set_xlabel('Time')
        self.ax_pnl.set_ylabel('Price')

        self.ax_postion = ax2
        self.ax_postion.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax_postion.set_xlabel('Time')
        self.ax_postion.set_ylabel('Price')
        self.ax_balance = self.ax_postion.twinx()

    def build(self):
        ax_pnl = self.ax_pnl
        ax_pnl.clear()
        ax_pnl.plot(
            [state.ts for state in self.wallet_states],
            [state.pnl for state in self.wallet_states],
            linestyle='-', color='purple'
        )

        ax_postion = self.ax_postion
        ax_postion.clear()
        ax_postion.plot(
            [state.ts for state in self.wallet_states],
            [state.position for state in self.wallet_states],
            linestyle='-', color='red'
        )
        ax_balance = self.ax_balance
        ax_balance.clear()
        ax_balance.plot(
            [state.ts for state in self.wallet_states],
            [state.balance for state in self.wallet_states],
            linestyle='-', color='blue'
        )


# Tests ################################################################################################################


class TestAdaptor:
    def test_state(context):
        class RouterMock:
            def add_consumer(self, consumer):
                pass

        adaptor = Adaptor(RouterMock(), window_size=timedelta(minutes=1))

        fill_1 = UserFillEvent(
            UserFill(Side.Buy, Price("100"), Quantity("10")),
            Timestamp.from_str("2025-03-21 12:30:00")
        )
        adaptor.on_user_fill(fill_1)

        state = adaptor.wallet_states[0]
        assert state.balance == -Quantity("1000")
        assert state.position == Quantity("10")
        assert state.pnl == Quantity("0")

        fill_2 = UserFillEvent(
            UserFill(Side.Sell, Price("110"), Quantity("20")),
            Timestamp.from_str("2025-03-21 12:30:30")
        )
        adaptor.on_user_fill(fill_2)

        state = adaptor.wallet_states[1]
        assert state.balance == Quantity("1200")
        assert state.position == -Quantity("10")
        assert state.pnl == Quantity("100")

        fill_3 = UserFillEvent(
            UserFill(Side.Buy, Price("100"), Quantity("10")),
            Timestamp.from_str("2025-03-21 12:31:00")
        )
        adaptor.on_user_fill(fill_3)

        state = adaptor.wallet_states[0]
        assert state.balance == Quantity("2200")
        assert state.position == -Quantity("20")
        assert state.pnl == Quantity("0")
        state = adaptor.wallet_states[1]
        assert state.balance == Quantity("1200")
        assert state.position == -Quantity("10")
        assert state.pnl == Quantity("200")

if __name__ == '__main__':
    import pytest
    pytest.main(["-v", __file__])


# Hide tests from import ###############################################################################################


__all__ = ['Adaptor']
