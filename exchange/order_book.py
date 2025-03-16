from primitives import *
from user_orders_contorller import UserOrdersController
from events import *
from router import Router


class OrderBook:
    def __init__(self, router: Router, user_orders_contorller: UserOrdersController):
        self.router = router
        self.router.set_order_book(self)

        self.user_orders_contorller = user_orders_contorller

    def on_historical_order_book_update(self, event: HistoricalOrderBookUpdate):
        self.router.on_order_book_update(OrderBookUpdateEvent(event.snapshot, event.ts))


# TODO: add tests