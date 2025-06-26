from exchange.primitives import *

class EventBase:
    id = 0

    def __init__(self, ts: Timestamp):
        self.ts = ts

        EventBase.id += 1
        self.id = EventBase.id

    def __str__(self):
        return f'{{"name":"{type(self).__name__}","id":{self.id},"ts":"{self.ts}}}'


class HistoricalTradeEvent(EventBase):
    def __init__(self, trade: Trade, ts: Timestamp):
        super().__init__(ts)
        self.trade = trade

    # TODO: implement __str__


# TODO: rename HistoricalOrderBookUpdateEvent
class HistoricalOrderBookUpdate(EventBase):
    def __init__(self, snapshot: OrderBookSnaphot, ts: Timestamp):
        super().__init__(ts)
        self.snapshot = snapshot

    # TODO: implement __str__


class OrderBookUpdateEvent(HistoricalOrderBookUpdate):
    pass

    # TODO: implement __str__


class TradeEvent(HistoricalTradeEvent):
    pass

    # TODO: implement __str__


class UserFillEvent(EventBase):
    def __init__(self, user_fill: UserFill, ts):
        super().__init__(ts)
        self.user_fill = user_fill

    # TODO: implement __str__


class PlaceUserMarketOrderEvent(EventBase):
    def __init__(self, order: MarketOrder, ts: Timestamp):
        super().__init__(ts)
        self.order = order

    # TODO: implement __str__


class UserMarketOrderPlacedEvent(EventBase):
    pass


class BbaEvent(EventBase):
    def __init__(self, bba: Bba, ts):
        super().__init__(ts)
        self.bba = bba

    # TODO: implement __str__
