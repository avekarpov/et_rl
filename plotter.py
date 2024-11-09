from event import EventHandler
from order_book import Side

import matplotlib.pyplot as plt


# TODO: fast solution, rewrite
class Plotter(EventHandler):
    def __init__(self):
        self.bids_prices = []
        self.asks_prices = []
        self.bid_ask_tss = []

        self.buy_trade_prices = []
        self.buy_trade_tss = []

        self.sell_trade_prices = []
        self.sell_trade_tss = []

    def process_event_order_book(self, event):
        self.bids_prices.append(event.value.bids[0].price)
        self.asks_prices.append(event.value.asks[0].price)
        self.bid_ask_tss.append(event.ts)

    def process_event_trade(self, event):
        if event.value.side == Side.Buy:
            self.buy_trade_prices.append(event.value.price)
            self.buy_trade_tss.append(event.ts)
        else:   
            self.sell_trade_prices.append(event.value.price)
            self.sell_trade_tss.append(event.ts)

    def show(self):
        plt.plot(self.bid_ask_tss, self.bids_prices, 'g')
        plt.plot(self.bid_ask_tss, self.asks_prices, 'r')
        plt.plot(self.buy_trade_tss, self.buy_trade_prices, 'ob')
        plt.plot(self.sell_trade_tss, self.sell_trade_prices, 'oy')
        plt.xticks([])
        plt.show()
