from __future__ import annotations
from exchange.primitives import *
from exchange.user_orders_contorller import UserOrdersController
from exchange.events import *
from exchange.logging import Logger
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List
from datetime import timedelta


class MatchingEngine(Logger):
    class StatSlot:
        def __init__(self, ts: Timestamp):
            self.ts = ts
            self.trade_volume = Quantity('0')
            self.user_fill_volume = Quantity('0')

        @property
        def percent(self):
            if self.trade_volume.is_zero():
                assert self.user_fill_volume.is_zero()
                return
            
            return self.user_fill_volume / self.trade_volume

    def __init__(self, router, user_orders_contorller: UserOrdersController):
        super().__init__()

        self.router = router
        self.router.set_matching_engine(self)

        self.user_orders_contorller = user_orders_contorller

        self.window_size = timedelta(hours=1)

        self.reset()

    def reset(self):
        self.stat: List[MatchingEngine.StatSlot] = []

    def set_window_size(self, window_size):
        self.window_size = window_size

    def on_historical_trade(self, event: HistoricalTradeEvent):
        self._log_event(event)
        if not self._user_market_order_quantity().is_zero() and event.trade.side == self._user_market_order_side():
            fill_quantity = min(event.trade.quantity, self._user_market_order_quantity())

            user_fill = UserFillEvent(UserFill(event.trade.side, event.trade.price, fill_quantity), event.ts)
            self.router.on_user_fill(user_fill)
            self._stat_user_fill(user_fill)

            trade = TradeEvent(Trade(event.trade.side, event.trade.price, fill_quantity), event.ts)
            self.router.on_trade(trade)
            self._stat_trade(trade)

            if fill_quantity < event.trade.quantity:
                trade = TradeEvent(Trade(event.trade.side, event.trade.price, event.trade.quantity - fill_quantity), event.ts)
                self.router.on_trade(trade)
                self._stat_trade(trade)

        else:
            trade = TradeEvent(Trade(event.trade.side, event.trade.price, event.trade.quantity), event.ts)
            self.router.on_trade(trade)
            self._stat_trade(trade)
    
    def _user_market_order_side(self):
        return self.user_orders_contorller.summary_market_order.side
    
    def _user_market_order_quantity(self):
        return self.user_orders_contorller.summary_market_order.quantity

    def _stat_user_fill(self, event: UserFillEvent):
        self._get_stat_slot(event.ts).user_fill_volume += event.user_fill.quantity
        self._clear()

    def _stat_trade(self, event: TradeEvent):
        self._get_stat_slot(event.ts).trade_volume += event.trade.quantity
        self._clear()

    def _get_stat_slot(self, ts) -> MatchingEngine.StatSlot:
        ts.replace(second=0, microsecond=0)

        if len(self.stat) == 0:
            self.stat.append(MatchingEngine.StatSlot(ts))

        elif self.stat[-1].ts != ts:
            assert self.stat[-1].ts < ts
            self.stat.append(MatchingEngine.StatSlot(ts))

        return self.stat[-1]

    def _clear(self):
        if self.window_size != timedelta():
            while self.stat[0].ts + self.window_size < self.stat[-1].ts:
                self.stat.pop(0)

    def init_axs(self):
        _, ax = plt.subplots(1, 1)
        
        self.ax = ax
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Price')

    def build(self):
        self.ax.clear()
        self.ax.plot(
            [slot.ts for slot in self.stat],
            [slot.percent for slot in self.stat]
        )

# TODO: add tests
