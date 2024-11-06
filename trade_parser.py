from order_book import Order, Side
from base_parser import BaseParser
from event import Event


class TradeParser(BaseParser):
    def parse_csv_line(self, line):
        line_iterator = iter(line)
        order = Order()
        order.side = Side.Buy if next(line_iterator) == 'b' else Side.Sell
        (whole, fractional) = next(line_iterator).split(':')
        order.price = float(f'{whole}.{fractional}')
        order.amount = float(next(line_iterator))

        event = Event(next(line_iterator))
        event.value = ('trade', order)

        return event
