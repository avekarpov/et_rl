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

    def __repr__(self):
        return str(self)

    def another(self):
        if self.value == self.Buy.value:
            return self.Sell
        else:
            return self.Buy
        
    def is_deeper(self, lhs, rhs):
        if self.value == self.Buy.value:
            return lhs > rhs
        else:
            return lhs < rhs
        
    def sidded(self, value):
        if self.value == Side.Buy.value:
            return value
        else:
            return -value


# TODO: make as class Price(Decimal)
# TODO: only from str or int
Price = Decimal


# TODO: make as class Quantity(Decimal)
# TODO: only from str or int
Quantity = Decimal


class Timestamp(datetime):
    DEFAULT_FORMAT = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def from_str(str, format=DEFAULT_FORMAT) -> Timestamp:
        return Timestamp.strptime(str, format)

class MarketOrder:
    def __init__(self, side: Side = Side.Buy, quantity: Quantity = Quantity('0')):
        self.side = side
        self.quantity = quantity

    def __str__(self):
        return f'{{"side":{self.side},"quantity":{self.quantity}}}'

    def __repr__(self):
        return str(self)

    def __eq__(self, other: LimitOrder):
        assert self.side == other.side
        return self.quantity == other.quantity


class LimitOrder(MarketOrder):
    def __init__(self, side: Side, price: Price, quantity: Quantity):
        super().__init__(side, quantity)
        self.price = price

    def __str__(self):
        return f'{{"side":{self.side},"price":{self.price},"quantity":{self.quantity}}}'

    def __repr__(self):
        return str(self)

    def __eq__(self, other: LimitOrder):
        assert self.side == other.side
        return self.price == other.price and self.quantity == other.quantity

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
    
    def __repr__(self):
        return str(self)

    def append(self, level: OrderBookLevel):
        assert level.quantity != Quantity('0')
        assert self.side == level.side
        super().append(level)

    def insert(self, index, level: OrderBookLevel):
        assert level.quantity != Quantity('0')
        assert self.side == level.side
        super().insert(index, level)

    def __eq__(self, other: OrderBookSide):
        assert self.side == other.side
        return super().__eq__(other)

    def is_correct(self):
        for i in range(len(self) - 1):
            if self[i].quantity == Quantity('0'):
                return False

            if not self.side.is_deeper(self[i].price, self[i + 1].price):
                return False
        
        return self[-1].quantity != Quantity('0')


class OrderBookSnaphot:
    def __init__(self):
        self.bids = OrderBookSide(Side.Buy)
        self.asks = OrderBookSide(Side.Sell)

    def __str__(self):
        return f'{{"bids":{self.bids},"asks":{self.asks}}}'

    def __repr__(self):
        return str(self)

    def __getitem__(self, side: Side):
        if side == Side.Buy:
            return self.bids
        else:
            return self.asks

    def __eq__(self, other: OrderBookSnaphot):
        return self.bids == other.bids and self.asks == other.asks

    def is_correct(self):
        if len(self.bids) != 0 and len(self.asks) !=0:
            if (self.bids[0].price >= self.asks[0].price):
                return False

        return self.bids.is_correct() and self.asks.is_correct()


class Trade(LimitOrder):
    pass


class UserFill(LimitOrder):
    pass


# TODO: add tests
class Bba:
    def __init__(self, bid: OrderBookLevel, ask: OrderBookLevel):
        assert bid.side == Side.Buy
        assert ask.side == Side.Sell
        assert bid.price < ask.price

        self.bid = bid
        self.ask = ask

    def __str__(self):
        return f'{{"bid":{self.bid},"ask":{self.ask}}}'

    def __repr__(self):
        return str(self)


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
        order = MarketOrder(Side.Buy, Quantity("100"))

        assert str(order) == '{"side":"buy","quantity":100}'


class TestLimitOrder:
    def test_to_str(context):
        order = LimitOrder(Side.Buy, Price("1000"), Quantity("100"))

        assert str(order) == '{"side":"buy","price":1000,"quantity":100}'


class TestOrderBookLevel:
    def test_to_str(context):
        level = OrderBookLevel(Side.Buy, Price("1000"), Quantity("100"))

        assert str(level) == '{"side":"buy","price":1000,"quantity":100}'

class TestOrderBookSide:
    def test_to_str(context):
        side = OrderBookSide(Side.Buy)
        side.append(OrderBookLevel(Side.Buy, Price("90"), Quantity("42")))
        side.append(OrderBookLevel(Side.Buy, Price("80"), Quantity("42")))
        side.append(OrderBookLevel(Side.Buy, Price("70"), Quantity("42")))

        assert str(side) == \
            '[' \
                '{"side":"buy","price":90,"quantity":42},' \
                '{"side":"buy","price":80,"quantity":42},' \
                '{"side":"buy","price":70,"quantity":42}' \
            ']'


class TestOrderBookSnaphot:
    def test_to_str(context):
        order_book = OrderBookSnaphot()
        order_book.bids.append(OrderBookLevel(Side.Buy, Price("90"), Quantity("42")))
        order_book.asks.append(OrderBookLevel(Side.Sell, Price("95"), Quantity("42")))

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
    'Quantity',
    'Timestamp',
    'MarketOrder', 
    'LimitOrder', 
    'OrderBookLevel', 
    'OrderBookSide',
    'OrderBookSnaphot',
    'Trade',
    'UserFill',
    'Bba'
]
