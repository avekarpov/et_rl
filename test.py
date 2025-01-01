from exchange import Exchange
from order_book import Order, Side
from plotter import Plotter

import logging

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    exchange = Exchange(
        '/home/artem/Downloads/Market data/Market data/gazp'
    )
    exchange.order_book_parser.fix_price_crossing = False
    exchange.matching_engine.wallet.pnl_window_s = 30 * 60

    plotter = Plotter()

    position = 0

    for events in exchange:
        for event in events:
            if event.name == 'order_book':
                if event.value.bids[0].price <= 164.5:
                    order = Order()
                    order.side = Side.Buy
                    order.amount = 1

                    exchange.place_market_order(order)

                    position += 1

                elif event.value.asks[0].price > 164.5:
                    order = Order()
                    order.side = Side.Sell
                    order.amount = 1

                    exchange.place_market_order(order)

                    position -= 1

            plotter.process_event(event)

    plotter.show()
