from order_book import OrderBook, Order, Side
from base_parser import BaseParser
from event import Event


class OrderBookParser(BaseParser):
    def parse_csv_line(self, line):
        def parse(side: Side, line_iterator):
            deep_size = 50

            order_book_side = []
            for i in range(deep_size):
                order = Order()
                (whole, fractional) = next(line_iterator).split(':')
                order.price = float(f'{whole}.{fractional}')
                order.amount = float(next(line_iterator))
                order.side = side

                order_book_side.append(order)
            
            return order_book_side

        line_iterator = iter(line)
        order_book = OrderBook()
        order_book.bids = parse(Side.Buy, line_iterator)
        order_book.asks = parse(Side.Sell, line_iterator)

        event = Event(next(line_iterator))
        event.value = ('order_book', order_book)

        return event
        

if __name__ == '__main__':
    parser = OrderBookParser(['/home/artem/Downloads/Market data/Market data/gazp/gazp_order_book_stream_20240422085001'])

    for event in parser:
        print(event)

        break