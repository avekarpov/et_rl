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

        min_ts = min([self.bid_ask_tss[0], self.buy_trade_tss[0], self.sell_trade_tss[0]])
        max_ts = max([self.bid_ask_tss[-1], self.buy_trade_tss[-1], self.sell_trade_tss[-1]])

        min_ts = (min_ts // 86400000 + 0) * 86400000
        max_ts = (max_ts // 86400000 + 1) * 86400000

        plt.vlines([min_ts + i * 86400000 + 7  * 3600000 for i in range((max_ts - min_ts) // 86400000)], ymin=min(self.bids_prices), ymax=max(self.asks_prices))
        plt.vlines([min_ts + i * 86400000 + 21 * 3600000 for i in range((max_ts - min_ts) // 86400000)], ymin=min(self.bids_prices), ymax=max(self.asks_prices))

        plt.xticks([])
        
        plt.show()
