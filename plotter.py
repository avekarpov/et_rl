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

        self.buy_fill_prices = []
        self.buy_fill_tss = []

        self.sell_fill_prices = []
        self.sell_fill_tss = []

        self.pnl = []
        self.position = []
        self.fiat = []
        self.trade_resutl_tss = []

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

    def process_event_fill(self, event):
        if event.value.side == Side.Buy:
            self.buy_fill_prices.append(event.value.price)
            self.buy_fill_tss.append(event.ts)
        else:
            self.sell_fill_prices.append(event.value.price)
            self.sell_fill_tss.append(event.ts)

    def process_event_pnl(self, event):
        self.pnl.append(event.value.pnl)
        self.position.append(event.value.position)
        self.fiat.append(event.value.fiat)
        self.trade_resutl_tss.append(event.ts)

    def show(self):
        min_ts = min([self.bid_ask_tss[0], self.buy_trade_tss[0], self.sell_trade_tss[0]])
        max_ts = max([self.bid_ask_tss[-1], self.buy_trade_tss[-1], self.sell_trade_tss[-1]])
        min_ts = (min_ts // 86400000 + 0) * 86400000
        max_ts = (max_ts // 86400000 + 1) * 86400000

        _, ax = plt.subplots(2)

        md_plot = ax[0]

        md_plot.plot(self.bid_ask_tss, self.bids_prices, 'g')
        md_plot.plot(self.bid_ask_tss, self.asks_prices, 'r')

        # md_plot.plot(self.buy_trade_tss, self.buy_trade_prices, 'ob')
        # md_plot.plot(self.sell_trade_tss, self.sell_trade_prices, 'oy')

        md_plot.plot(self.buy_fill_tss, self.buy_fill_prices, 'og')
        md_plot.plot(self.sell_fill_tss, self.sell_fill_prices, 'or')

        md_plot.vlines([min_ts + i * 86400000 + 7  * 3600000 for i in range((max_ts - min_ts) // 86400000)], ymin=min(self.bids_prices), ymax=max(self.asks_prices))
        md_plot.vlines([min_ts + i * 86400000 + 21 * 3600000 for i in range((max_ts - min_ts) // 86400000)], ymin=min(self.bids_prices), ymax=max(self.asks_prices))

        pnl_plot = ax[1]

        pnl_plot.plot(self.trade_resutl_tss, self.pnl, 'm')

        pnl_plot.vlines([min_ts + i * 86400000 + 7  * 3600000 for i in range((max_ts - min_ts) // 86400000)], ymin=min(self.pnl), ymax=max(self.pnl))
        pnl_plot.vlines([min_ts + i * 86400000 + 21 * 3600000 for i in range((max_ts - min_ts) // 86400000)], ymin=min(self.pnl), ymax=max(self.pnl))

        plt.xticks([])
        
        plt.show()
