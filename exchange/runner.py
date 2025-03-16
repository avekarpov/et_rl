from router import Router
from events import HistoricalTradeEvent, HistoricalOrderBookUpdate

class Runner:
    def __init__(self):
        self.router = Router()
        self.trade_parser = None
        self.order_book_update_parser = None

        self.next_historical_trade = None
        self.next_historical_order_book_update = None

    def set_trade_parser(self, parser):
        self.trade_parser = parser

    def set_order_book_update_parser(self, parser):
        self.order_book_update_parser = parser

    def __iter__(self):
        return self

    def __next__(self):
        next_trade = self._get_next_historical_trade()
        next_ob_update = self._get_next_historical_order_book_update()

        if next_trade is not None and next_ob_update is not None:
            if next_trade.ts < next_ob_update.ts:
                self.router.on_historical_trade(next_trade)
                self.next_historical_trade = None

            else: 
                self.router.on_historical_order_book_update(next_ob_update)
                self.next_historical_order_book_update = None
        
        if next_trade is not None:
            self.router.on_historical_trade(next_trade)
            self.next_historical_trade = None
        
        if next_ob_update is not None:
            self.router.on_historical_order_book_update(next_ob_update)
            self.next_historical_order_book_update = None

        raise StopIteration

    def _get_next_historical_trade(self) -> HistoricalTradeEvent|None:
        if self.next_historical_trade is not None:
            return self.next_historical_trade

        if self.trade_parser is not None:
            self.next_historical_trade = next(self.trade_parser, None)
        
        return self.next_historical_trade

    def _get_next_historical_order_book_update(self) -> HistoricalOrderBookUpdate|None:
        if self.next_historical_order_book_update is not None:
            return self.next_historical_order_book_update

        if self.order_book_update_parser is not None:
            self.next_historical_order_book_update = next(self.order_book_update_parser, None)
        
        return self.next_historical_order_book_update

# TODO: add tests
