from exchange.primitives import *
from exchange.events import *
from exchange.logging import Logger


class UserOrdersController(Logger):
    def __init__(self, router):
        super().__init__()

        self.router = router
        self.router.set_user_orders_contorller(self)

        self.summary_market_order = MarketOrder()

    def on_user_place_market_order(self, event: PlaceUserMarketOrderEvent):
        self.log_event(event)

        self._add_market_order_quantity(event.order.side, event.order.quantity)
        self.router.on_user_market_order_placed(UserMarketOrderPlacedEvent(event.ts))

    def on_user_fill(self, event: UserFillEvent):
        self.log_event(event)

        assert event.user_fill.side == self.summary_market_order.side
        assert event.user_fill.quantity <= self.summary_market_order.quantity

        self._add_market_order_quantity(event.user_fill.side.another(), event.user_fill.quantity)

    def _add_market_order_quantity(self, side: Side, quantity: Quantity):
        if self.summary_market_order.side == side:
            self.summary_market_order.quantity += quantity
        elif quantity <= self.summary_market_order.quantity:
            self.summary_market_order.quantity -= quantity
        else:
            self.summary_market_order.quantity = quantity - self.summary_market_order.quantity
            self.summary_market_order.side = self.summary_market_order.side.another()
        
        assert self.summary_market_order.quantity >= Quantity('0')

    def __str__(self):
        return f'{{"summary_market_order":{self.summary_market_order}}}'


# Tests ################################################################################################################


class TestUserOrdersController:
    def test_to_str(constext):
        controller = UserOrdersController()
        assert str(controller) == '{"summary_market_order":{"side":"buy","quantity":0}}'

    def test_add_market_order_quantity(context):
        controller = UserOrdersController()

        controller._add_market_order_quantity(Side.Buy, Quantity(10))
        assert controller.summary_market_order.side == Side.Buy
        assert controller.summary_market_order.quantity == Quantity(10)

        controller._add_market_order_quantity(Side.Buy, Quantity(32))
        assert controller.summary_market_order.side == Side.Buy
        assert controller.summary_market_order.quantity == Quantity(42)

        controller._add_market_order_quantity(Side.Sell, Quantity(12))
        assert controller.summary_market_order.side == Side.Buy
        assert controller.summary_market_order.quantity == Quantity(30)

        controller._add_market_order_quantity(Side.Sell, Quantity(50))
        assert controller.summary_market_order.side == Side.Sell
        assert controller.summary_market_order.quantity == Quantity(20)


if __name__ == '__main__':
    import pytest
    pytest.main(["-v", __file__])


# Hide tests from import ###############################################################################################


__all__ = ['UserOrdersController']
