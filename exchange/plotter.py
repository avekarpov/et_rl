import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from exchange.events import *
from exchange.logging import Logger
from datetime import timedelta
from typing import List
from copy import deepcopy as copy


# TODO: Use matplotlib.animation
class Plotter(Logger):
    def __init__(self, router):
        super().__init__()

        self.router = router
        self.router.add_consumer(self)

        self.window_size = timedelta(hours=1)

        # TODO: change to time interval
        self.refresh_rate = 500

        plt.ion()
        self.init_axs()

        self.reset()

    def reset(self):
        self.bbas: List[BbaEvent] = []
        self.trades: List[TradeEvent] = []
        self.user_fills: List[UserFillEvent] =[]

        self.events_before_refresh = 0

    def set_window_size(self, window_size):
        self.window_size = window_size

    def set_refresh_rate(self, refresh_rate):
        self.refresh_rate = refresh_rate

    def init_axs(self):
        _, self.ax = plt.subplots()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Price')

    def on_user_market_order_placed(self, event):
        pass

    def on_user_fill(self, event: UserFillEvent):
        self._log_event(event)

        self.user_fills.append(event)

        self._clear(self.user_fills)

    def on_order_book_update(self, event: OrderBookUpdateEvent):
        self._log_event(event)

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
        self._log_event(event)

        self.trades.append(event)

        self._clear(self.trades)

    def _clear(self, events, mult=1):
        if self.window_size != timedelta():
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


class ExtendedPlotter(Plotter):
    def __init__(self, router):
        super().__init__(router)
    
        self.builders = []

    def add_builder(self, builder):
        self.builders.append(builder)
        builder.init_axs()

    def build(self):
        super().build()
    
        for builder in self.builders:
            builder.build()
