import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from exchange.events import *
from exchange.logging import Logger
from datetime import timedelta
from typing import List


# TODO: Use matplotlib.animation
class Plotter(Logger):
    def __init__(self, rounter, window_size = timedelta(hours=1), refresh_rate=500):
        super().__init__()

        self.router = rounter
        self.router.set_consumer(self)

        self.window_size = window_size

        self.refresh_rate = refresh_rate
        self.events_before_refresh = 0

        self.bbas: List[BbaEvent] = []
        self.trades: List[TradeEvent] = []

        # TODO: beauti
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Price')

    def on_user_market_order_placed(self, event):
        pass

    def on_user_fill(self, event):
        pass

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



        if self.window_size != 0:
            while self.bbas[0].ts + self.window_size < self.bbas[-1].ts:
                self.bbas.pop(0)

    def on_trade(self, event: TradeEvent):
        self.log_event(event)

        self.trades.append(event)

        if self.window_size != 0:
            while self.trades[0].ts + self.window_size < self.trades[-1].ts:
                self.trades.pop(0)

    def draw(self):
        if self.events_before_refresh != 0:
            self.events_before_refresh -= 1
            return

        self.events_before_refresh = self.refresh_rate

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

        plt.draw()
        plt.pause(0.0001) # TODO: remove
