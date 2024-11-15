from order_book import OrderBook, Order, Side
from base_parser import BaseParser
from event import Event


class OrderBookParser(BaseParser):
    fix_price_crossing=False

    def parse_csv_line(self, line):
        def parse(side: Side, line_iterator):
            depth_size = 50

            order_book_side = []
            for i in range(depth_size):
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

        if self.fix_price_crossing:
            while order_book.asks[0].price <= order_book.bids[0].price:
                if len(order_book) % 2 == 0:
                    self.logger.warning(
                        f'Fix price crossing by ask: '
                        f'ask price: {order_book.asks[0].price} <= bid price: {order_book.bids[0].price} '
                        f'new best ask price: {order_book.asks[1].price}'
                    )

                    order_book.asks[1].amount += order_book.asks[0].amount
                    order_book.asks.pop(0)
                else:
                    self.logger.warning(
                        f'Fix price crossing by bid: '
                        f'ask price: {order_book.asks[0].price} <= bid price: {order_book.bids[0].price} '
                        f'new best bid price: {order_book.bids[1].price}'
                    )

                    order_book.bids[1].amount += order_book.bids[0].amount
                    order_book.bids.pop(0)
                

        event = Event(int(next(line_iterator)))
        event.value = ('order_book', order_book)

        return event
