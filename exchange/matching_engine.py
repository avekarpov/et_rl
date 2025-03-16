from primitives import *
from user_orders_contorller import UserOrdersController
from events import *
from router import Router


class MatchingEngine:
    def __init__(self, router: Router, user_orders_contorller: UserOrdersController):
        self.router = router
        self.router.set_matching_engine(self)

        self.user_orders_contorller = user_orders_contorller

    def on_historical_trade(self, event: HistoricalTradeEvent):
        if not self._user_market_order_quantity().is_zero() and event.trade.side == self._user_market_order_side():
            fill_quantity = min(event.trade.quantity, self._user_market_order_quantity())

            self.router.on_user_fill(UserFillEvent(UserFill(event.trade.side, event.trade.price, fill_quantity)))

            if fill_quantity < event.trade.quantity:
                self.router.on_trade(TradeEvent(Trade(event.trade.side, event.trade.price, event.trade.quantity - fill_quantity)))

        else:
            self.router.on_trade(TradeEvent(Trade(event.trade.side, event.trade.price, event.trade.quantity)))
    
    def _user_market_order_side(self):
        return self.user_orders_contorller.summary_market_order.side
    
    def _user_market_order_quantity(self):
        return self.user_orders_contorller.summary_market_order.quantity


# TODO: add tests
