from primitives import *


class UserOrdersController:
    def __init__(self):
        self.summary_market_order = MarketOrder()

    def add_market_order(self, order: MarketOrder):
        if self.summary_market_order.side == order.side:
            self.summary_market_order.quntity += order.quntity
        elif self.summary_market_order.quntity > order.quntity:
            self.summary_market_order.quntity -= order.quntity
        else:
            self.summary_market_order.quntity = order.quntity - self.summary_market_order.quntity
            self.summary_market_order.side = self.summary_market_order.side.another()
        
        assert self.summary_market_order.quntity >= Quntity('0')

    def __str__(self):
        return f'{{"summary_market_order":{self.summary_market_order}}}'


# Tests ################################################################################################################


class TestUserOrdersController:
    def test_to_str(constext):
        controller = UserOrdersController()
        assert str(controller) == '{"summary_market_order":{"side":"buy","quantity":0}}'

    def test_add_market_order(context):
        controller = UserOrdersController()

        controller.add_market_order(MarketOrder(Side.Buy, Quntity(10)))
        assert controller.summary_market_order.side == Side.Buy
        assert controller.summary_market_order.quntity == Quntity(10)

        controller.add_market_order(MarketOrder(Side.Buy, Quntity(32)))
        assert controller.summary_market_order.side == Side.Buy
        assert controller.summary_market_order.quntity == Quntity(42)

        controller.add_market_order(MarketOrder(Side.Sell, Quntity(12)))
        assert controller.summary_market_order.side == Side.Buy
        assert controller.summary_market_order.quntity == Quntity(30)

        controller.add_market_order(MarketOrder(Side.Sell, Quntity(50)))
        assert controller.summary_market_order.side == Side.Sell
        assert controller.summary_market_order.quntity == Quntity(20)


if __name__ == '__main__':
    import pytest
    pytest.main(["-v", __file__])


# Hide tests from import ###############################################################################################


__all__ = ['UserOrdersController']
