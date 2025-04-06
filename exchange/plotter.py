from __future__ import annotations 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from exchange.events import *
from exchange.logging import Logger
from datetime import timedelta
from typing import List
from copy import deepcopy as copy


# TODO: Use matplotlib.animation
class Plotter(Logger):
    def __init__(self, router, window_size = timedelta(hours=1), refresh_rate=500):
        super().__init__()

        self.router = router
        self.router.add_consumer(self)

        self.window_size = window_size

        self.refresh_rate = refresh_rate
        self.events_before_refresh = 0

        plt.ion()
        self.init_axs()

        self.bbas: List[BbaEvent] = []
        self.trades: List[TradeEvent] = []
        self.user_fills: List[UserFillEvent] =[]

    def init_axs(self):
        _, self.ax = plt.subplots()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Price')

    def on_user_market_order_placed(self, event):
        pass

    def on_user_fill(self, event: UserFillEvent):
        self.log_event(event)

        self.user_fills.append(event)

        self._clear(self.user_fills)

    def on_order_book_update(self, event: OrderBookUpdateEvent):
        self.log_event(event)

        bba = BbaEvent(
            Bba(
                OrderBookLevel(Side.Buy, event.snapshot.bids[0].price, event.snapshot.bids[0].quantity),
                OrderBookLevel(Side.Sell, event.snapshot.asks[0].price, event.snapshot.asks[0].quantity)
            ),
            event.ts
        )

        self.bbas.append(bba)

        self._clear(self.bbas)

    def on_trade(self, event: TradeEvent):
        self.log_event(event)

        self.trades.append(event)

        self._clear(self.trades)

    def _clear(self, events, mult=1):
        if self.window_size != 0:
            while events[0].ts + self.window_size * mult < events[-1].ts:
                events.pop(0)

    def build(self):
        ax = self.ax
        ax.clear()
        ax.plot(
            [event.ts for event in self.bbas],
            [event.bba.bid.price for event in self.bbas],
            linestyle='-', color='green'
        )
        ax.plot(
            [event.ts for event in self.bbas],
            [event.bba.ask.price for event in self.bbas],
            linestyle='-', color='red'
        )
        ax.scatter(
            [event.ts for event in self.trades],
            [event.trade.price for event in self.trades],
            marker = 'o', color='black', alpha=0.7
        )
        ax.scatter(
            [event.ts for event in self.user_fills],
            [event.user_fill.price for event in self.user_fills],
            marker = 'o', color='blue'
        )

    def draw(self):
        if self.events_before_refresh != 0:
            self.events_before_refresh -= 1
            return

        self.events_before_refresh = self.refresh_rate

        self.build()

        plt.draw()
        plt.pause(0.0001) # TODO: remove

    def show(self):
        self.build()
        plt.show(block=True)


class PlotterWithPnl(Plotter):
    class PnlState:
        def __init__(self, ts):
            self.balance = Quantity('0')
            self.position = Quantity('0')
            self.pnl = 0
            self.ts = ts

        def with_fill(self, event: UserFillEvent) -> PlotterWithPnl.PnlState:
            fill = event.user_fill

            pnl = copy(self)
            pnl.balance -= fill.side.sidded(fill.quantity * fill.price)
            pnl.position += fill.side.sidded(fill.quantity)
            pnl.pnl = pnl.balance + pnl.position * fill.price
            pnl.ts = event.ts

            return pnl
        
        def with_trade(self, event: TradeEvent) -> PlotterWithPnl.PnlState:
            pnl = copy(self)

            pnl.pnl = pnl.balance + pnl.position * event.trade.price
            pnl.ts = event.ts

            return pnl

    def __init__(self, router, window_size=timedelta(hours=1), refresh_rate=500):
        super().__init__(router, window_size, refresh_rate)

        self.pnl_states: List[PlotterWithPnl.PnlState] = []

    def init_axs(self):
        super().init_axs()

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

    def on_trade(self, event: TradeEvent):
        super().on_trade(event)

        if len(self.pnl_states) != 0:
            self.pnl_states.append(self.pnl_states[-1].with_trade(event))
        
            self._clear(self.pnl_states)

    def on_user_fill(self, event: UserFillEvent):
        super().on_user_fill(event)

        fill = event.user_fill

        if len(self.pnl_states) == 0:
            pnl = PlotterWithPnl.PnlState(event.ts)
            pnl.balance -= fill.side.sidded(fill.quantity * fill.price)
            pnl.position += fill.side.sidded(fill.quantity)

            self.pnl_states.append(pnl)
        else:
            self.pnl_states.append(self.pnl_states[-1].with_fill(event))
        
        self._clear(self.pnl_states, mult=10)

    def build(self):
        super().build()

        ax_pnl = self.ax_pnl
        ax_pnl.clear()
        ax_pnl.plot(
            [pnl.ts for pnl in self.pnl_states],
            [pnl.pnl for pnl in self.pnl_states],
            linestyle='-', color='purple'
        )

        ax_postion = self.ax_postion
        ax_postion.clear()
        ax_postion.plot(
            [pnl.ts for pnl in self.pnl_states],
            [pnl.position for pnl in self.pnl_states],
            linestyle='-', color='red'
        )
        ax_balance = self.ax_balance
        ax_balance.clear()
        ax_balance.plot(
            [pnl.ts for pnl in self.pnl_states],
            [pnl.balance for pnl in self.pnl_states],
            linestyle='-', color='blue'
        )

    def log_last_pnl(self):
        pnl: PlotterWithPnl.PnlState = self.pnl_states[-1]
        self.logger.info(f'Balance: {pnl.balance}, "postion: {pnl.position}, pnl: {pnl.pnl}')
