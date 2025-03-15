from primitives import *
from user_orders_contorller import *
from events import *


class OrderBook:
    def __init__(self, router, user_orders_contorller: UserOrdersController):
        self.router = router
        self.user_orders_contorller = user_orders_contorller

    def on_order_book_update(self, event: OrderBookUpdate):
        self.router.on_order_book_update_full(OrderBookUpdateFull(event.snapshot, event.ts))
