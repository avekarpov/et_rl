from __future__ import annotations
from enum import Enum
from decimal import Decimal
from typing import List
from datetime import datetime


class Side(Enum):
    Buy = 1
    Sell = -1

    def __str__(self):
        return '"buy"' if self.value == Side.Buy.value else '"sell"'

    def another(self):
        if self.value == self.Buy.value:
            return self.Sell
        else:
            return self.Buy


# TODO: make as class Price(Decimal)
# TODO: only from str or int
Price = Decimal


# TODO: make as class Quntity(Decimal)
# TODO: only from str or int
Quntity = Decimal


# TODO: make as class Quntity(Decimal)
Timestamp = datetime


class MarketOrder:
    def __init__(self, side: Side = Side.Buy, quntity: Quntity = Quntity('0')):
        self.side = side
        self.quntity = quntity

    def __str__(self):
        return f'{{"side":{self.side},"quantity":{self.quntity}}}'


class LimitOrder(MarketOrder):
    def __init__(self, side: Side, price: Price, quntity: Quntity):
        super().__init__(side, quntity)
        self.price = price

    def __str__(self):
        return f'{{"side":{self.side},"price":{self.price},"quantity":{self.quntity}}}'


class OrderBookLevel(LimitOrder):
    pass


# TODO: append must check ordering
# TODO: append must check side
# TODO: must store side (as const value)
class OrderBookSide(List[OrderBookLevel]):
    def __init__(self, side: Side):
        self.side = side

    def __str__(self):
        return f'[{",".join(str(level) for level in self)}]'
    

class OrderBook:
    def __init__(self):
        self.bids = OrderBookSide(Side.Buy)
        self.asks = OrderBookSide(Side.Sell)

    def __str__(self):
        return f'{{"bids":{self.bids},"asks":{self.asks}}}'


class Trade(LimitOrder):
    pass
    
# Tests ################################################################################################################


class TestSide:
    def test_to_str(context):
        assert str(Side.Buy) == '"buy"'
        assert str(Side.Sell) == '"sell"'

    def test_antoter(context):
        assert Side.Buy.another() == Side.Sell
        assert Side.Sell.another() == Side.Buy


class TestMarketOrder:
    def test_to_str(context):
        order = MarketOrder(Side.Buy, Quntity("100"))

        assert str(order) == '{"side":"buy","quantity":100}'


class TestLimitOrder:
    def test_to_str(context):
        order = LimitOrder(Side.Buy, Price("1000"), Quntity("100"))

        assert str(order) == '{"side":"buy","price":1000,"quantity":100}'


class TestOrderBookLevel:
    def test_to_str(context):
        level = OrderBookLevel(Side.Buy, Price("1000"), Quntity("100"))

        assert str(level) == '{"side":"buy","price":1000,"quantity":100}'

class TestOrderBookSide:
    def test_to_str(context):
        side = OrderBookSide(Side.Buy)
        side.append(OrderBookLevel(Side.Buy, Price("90"), Quntity("42")))
        side.append(OrderBookLevel(Side.Buy, Price("80"), Quntity("42")))
        side.append(OrderBookLevel(Side.Buy, Price("70"), Quntity("42")))

        assert str(side) == \
            '[' \
                '{"side":"buy","price":90,"quantity":42},' \
                '{"side":"buy","price":80,"quantity":42},' \
                '{"side":"buy","price":70,"quantity":42}' \
            ']'


class TestOrderBook:
    def test_to_str(context):
        order_book = OrderBook()
        order_book.bids.append(OrderBookLevel(Side.Buy, Price("90"), Quntity("42")))
        order_book.asks.append(OrderBookLevel(Side.Sell, Price("95"), Quntity("42")))

        assert str(order_book) == \
            '{' \
                '"bids":[{"side":"buy","price":90,"quantity":42}],' \
                '"asks":[{"side":"sell","price":95,"quantity":42}]' \
            '}'


if __name__ == '__main__':
    import pytest
    pytest.main(["-v", __file__])


# Hide tests from import ###############################################################################################


__all__ = [
    'Side', 
    'Price', 
    'Quntity',
    'Timestamp',
    'MarketOrder', 
    'LimitOrder', 
    'OrderBookLevel', 
    'OrderBookSide',
    'OrderBook',
    'Trade'
]
