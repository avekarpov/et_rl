from enum import Enum


class Side(Enum):
    Buy = 1
    Sell = 2

    def __str__(self):
        if self.value == Side.Buy:
            return 'buy'
        else:
            return 'sell'

class Order:
    side: Side = None
    price = 0.0
    amount = 0.0

    def __str__(self):
        return f'{{"side": {self.side}, "price": {self.price}, "amount": {self.amount}}}'
        
    def __repr__(self):
        return str(self)

class OrderBook:
    bids = []
    asks = []

    def __len__(self):
        return len(self.bids) + len(self.asks)

    def __str__(self):
        return f'{{"bids": {self.bids}, "asks": {self.asks}}}'
