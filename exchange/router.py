from exchange.events import *
from exchange.order_book import OrderBook
from exchange.matching_engine import MatchingEngine
from exchange.user_orders_contorller import UserOrdersController
from exchange.logging import Logger


class Router(Logger):
    def __init__(self):
        super().__init__()
        self.user_orders_contorller: UserOrdersController = None
        self.matching_engine: MatchingEngine = None
        self.order_book: OrderBook = None
        self.consumers = []

        self.reset()
    
    def reset(self):
        self.ts = Timestamp.min

    def set_user_orders_contorller(self, user_orders_contorller: UserOrdersController):
        self.user_orders_contorller = user_orders_contorller
    
    def set_matching_engine(self, matching_engine: MatchingEngine):
        self.matching_engine = matching_engine
    
    def set_order_book(self, order_book: OrderBook):
        self.order_book = order_book

    def add_consumer(self, consumer):
        self.consumers.append(consumer)

    @staticmethod
    def get_none_object():
        class NoneObject:
            def __getattr__(self, name):
                return lambda *args, **kwargs: None

        return NoneObject()
    
    def get_user_orders_contorller(self) -> UserOrdersController:
        if self.user_orders_contorller is None:
            return Router.get_none_object()

        return self.user_orders_contorller

    def get_matching_engine(self) -> MatchingEngine:
        if self.matching_engine is None:
            return Router.get_none_object()

        return self.matching_engine

    def get_order_book(self) -> OrderBook:
        if self.order_book is None:
            return Router.get_none_object()

        return self.order_book

    def on_historical_trade(self, event: HistoricalTradeEvent):
        self._log_event(event)
        self._update_ts(event)
        self.get_matching_engine().on_historical_trade(event)

    def on_historical_order_book_update(self, event: HistoricalOrderBookUpdate):
        self._log_event(event)
        self._update_ts(event)
        self.get_order_book().on_historical_order_book_update(event)
    
    def on_place_user_market_order(self, event: PlaceUserMarketOrderEvent):
        self._log_event(event)
        self._update_ts(event)
        self.get_user_orders_contorller().on_user_place_market_order(event)
    
    def on_user_market_order_placed(self, event: UserMarketOrderPlacedEvent):
        self._log_event(event)
        self._update_ts(event)
        self._for_all_consumers(event, 'on_user_market_order_placed')

    def on_user_fill(self, event: UserFillEvent):
        self._log_event(event)
        self._update_ts(event)
        self.get_user_orders_contorller().on_user_fill(event)
        self._for_all_consumers(event, 'on_user_fill')
    
    def on_order_book_update(self, event: OrderBookUpdateEvent):
        self._log_event(event)
        self._update_ts(event)
        self._for_all_consumers(event, 'on_order_book_update')

    def on_trade(self, event: TradeEvent):
        self._log_event(event)
        self._update_ts(event)
        self._for_all_consumers(event, 'on_trade')

    def _for_all_consumers(self, event, handler_name):
        for consumer in self.consumers:
            getattr(consumer, handler_name)(event)

    def _update_ts(self, event):
        # TODO: uncomment
        # assert self.ts <= event.ts

        self.ts = event.ts


# TODO: add tests
