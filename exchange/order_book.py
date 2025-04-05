from exchange.primitives import *
from exchange.user_orders_contorller import UserOrdersController
from exchange.events import *
from exchange.logging import Logger


class OrderBook(Logger):
    def __init__(self, router, user_orders_contorller: UserOrdersController):
        super().__init__()

        self.router = router
        self.router.set_order_book(self)

        self.user_orders_contorller = user_orders_contorller

    def on_historical_order_book_update(self, event: HistoricalOrderBookUpdate):
        self.log_event(event)
        self.router.on_order_book_update(OrderBookUpdateEvent(event.snapshot, event.ts))


# TODO: add tests