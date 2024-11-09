from order_book import Order
from event import Event, EventHandler

# Simple matching engine, fill only market orders
class MarketMatchingEngine(EventHandler):
    market_order = Order()

    def process_event_order_book(self, event):
        return []

    def process_event_trade(self, trade_event):


        trade = trade_event.value

        if trade.side == self.market_order.side:
            return []

        fill_amount = min(self.market_order.amount, trade.amount)
        if fill_amount != 0.0:
            self.market_order.amount -= fill_amount

            fill = Order()
            fill.amount = fill_amount
            fill.price = trade.price

            fill_event = Event(trade_event.ts)
            fill_event.value = ('fill', fill)

            return [fill_event]
        
        return []

    def prorcess_event_place_market(self, place_market):
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
