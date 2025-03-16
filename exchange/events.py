from primitives import *

class Event:
    def __init__(self, ts: Timestamp):
        self.ts = ts


class HistoricalTradeEvent(Event):
    def __init__(self, trade: Trade, ts: Timestamp):
        super().__init__(ts)
        self.trade = trade

    # TODO: implement __str__


class HistoricalOrderBookUpdate(Event):
    def __init__(self, snapshot: OrderBookSnaphot, ts: Timestamp):
        super().__init__(ts)
        self.snapshot = snapshot

    # TODO: implement __str__


class OrderBookUpdate(HistoricalOrderBookUpdate):
    pass

    # TODO: implement __str__


class TradeEvent(HistoricalTradeEvent):
    pass

    # TODO: implement __str__


class UserFillEvent(Event):
    def __init__(self, user_fill: UserFill, ts):
        super().__init__(ts)
        self.user_fill = user_fill

    # TODO: implement __str__


class PlaceUserMarketOrder(Event):
    def __init__(self, order: MarketOrder, ts: Timestamp):
        super().__init__(ts)
        self.order = order

    # TODO: implement __str__