from primitives import *

class Event:
    def __init__(self, ts: Timestamp):
        self.ts = ts


class TradeEvent(Event):
    def __init__(self, trade: Trade, ts: Timestamp):
        super().__init__(ts)
        self.trade = trade

    # TODO: implement __str__


class OrderBookUpdate(Event):
    def __init__(self, order_book: OrderBook, ts: Timestamp):
        super().__init__(ts)
        self.order_book = order_book

    # TODO: implement __str__

