from matching_engine import MarketMatchingEngine
from order_book_parser import OrderBookParser
from trade_parser import TradeParser
from event import Event
import tools
import re
import logging


class Exchange:
    matching_engine = MarketMatchingEngine()

    def __init__(self, dir, skip_title=True, min_ts=None, max_ts=None):
        self.order_book_parser = OrderBookParser(
            tools.list_dir_regex(dir, re.compile('.*order_book.*')),
            skip_title
        )
        self.trade_parser = TradeParser(
            tools.list_dir_regex(dir, re.compile('.*trade.*')),
            skip_title
        )

        self.next_order_book_event = next(self.order_book_parser, None)
        self.next_trade_event = next(self.trade_parser, None)
        self.last_ts = None

        self.until_ts = max_ts

        if min_ts is not None:
            while self.next_trade_event.ts < min_ts or self.next_order_book_event.ts < min_ts:
                next(self)

        self.logger = logging.getLogger(type(self).__name__)

    def __len__(self):
        return max(len(self.order_book_parser), len(self.trade_parser))
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.until_ts is not None:
            if self.until_ts < self.next_trade_event.ts and self.until_ts < self.next_order_book_event.ts:
                raise StopIteration    

        if self.next_order_book_event is None:
            self.logger.info('There is no more order book events, stop')
            
            raise StopIteration
        
        if self.next_trade_event is None:
            self.logger.info('There is no more trade events, stop')

            raise StopIteration
        
        events = []

        if self.next_trade_event.ts < self.next_order_book_event.ts:
            self.last_ts = self.next_trade_event.ts

            events.append(self.next_trade_event)

            events += self.matching_engine.process_event_trade(
                self.next_trade_event
            )

            self.next_trade_event = next(self.trade_parser, None)

        else:
            self.last_ts = self.next_order_book_event.ts

            events.append(self.next_order_book_event)

            events += self.matching_engine.process_event_order_book(
                self.next_order_book_event
            )

            self.next_order_book_event = next(self.order_book_parser, None)

        return events

    def place_market_order(self, order):
        event = Event(self.last_ts)
        event.value = ('place_market', order)
        self.matching_engine.process_event_place_market(event)
