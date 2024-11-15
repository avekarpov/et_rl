from order_book import Order, Side
from event import Event, EventHandler
from wallet import Wallet

# Simple matching engine, fill only market orders
class MarketMatchingEngine(EventHandler):
    wallet = Wallet()

    market_order = Order()

    last_fill = None

    def process_event_order_book(self, event):
        return self.wallet.process_event_order_book(event)

    def process_event_trade(self, trade_event):
        trade = trade_event.value

        if trade.side == self.market_order.side:
            return []

        fill_amount = min(self.market_order.amount, trade.amount)
        if fill_amount != 0.0:
            self.market_order.amount -= fill_amount

            self.last_fill = Order()
            self.last_fill.side = self.market_order.side
            self.last_fill.amount = fill_amount
            self.last_fill.price = trade.price

            fill_event = Event(trade_event.ts)
            fill_event.value = ('fill', self.last_fill)

            return [fill_event] + self.wallet.process_event_fill(fill_event)
        
        return []

    def process_event_place_market(self, place_market):
        assert hasattr(place_market, 'place_market')
        assert place_market.value.price == 0.0

        order = place_market.value

        if self.market_order.amount == 0.0:
            self.market_order = order
        else:
            if self.market_order.side == order.side:
                self.market_order.amount += order.amount
            else:
                if self.market_order.amount > order.amount:
                    self.market_order.amount -= order.amount
                else:
                    order.amount -= self.market_order.amount
                    self.market_order = order

        return []

    def state(self):
        result = {'market_order': self.market_order, 'last_fill': self.last_fill}
        result.update(self.wallet.state())
        return result

    def reset(self):
        self.market_order = Order()
        self.wallet.reset()
