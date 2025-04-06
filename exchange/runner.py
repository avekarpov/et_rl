from exchange.router import Router
from exchange.events import HistoricalTradeEvent, HistoricalOrderBookUpdate
from exchange.logging import Logger
from exchange.primitives import Timestamp


class Runner(Logger):
    def __init__(self):
        super().__init__()

        self.router = Router()
        self.trade_parser = None
        self.order_book_update_parser = None
        
        self.until_ts = None

        self.reset()

    def reset(self):
        self.next_historical_trade = None
        self.next_historical_order_book_update = None

        self.last_ts = Timestamp.min

    def init_order_book(self):
        while self._get_next_historical_trade().ts < self._get_next_historical_order_book_update().ts:
            next(self)

        next(self)

    def set_trade_parser(self, parser):
        self.logger.info('Set trade parser')

        self.trade_parser = parser

    def set_order_book_update_parser(self, parser):
        self.logger.info('Set order book parser')

        self.order_book_update_parser = parser

    def set_until_ts(self, until_ts: Timestamp):
        self.until_ts = until_ts

    def __iter__(self):
        return self

    def __next__(self):
        self.logger.debug('Step')

        next_trade = self._get_next_historical_trade()
        next_ob_update = self._get_next_historical_order_book_update()

        self.logger.debug(f'Next trade event: {next_trade}')
        self.logger.debug(f'Next order book update event: {next_ob_update}')

        assert next_trade is None or self.last_ts <= next_trade.ts
        assert next_ob_update is None or self.last_ts <= next_ob_update.ts

        if self.until_ts is not None:
            if self.until_ts < min(next_trade.ts, next_ob_update.ts):
                self.logger.info("Ended by until ts")

                raise StopIteration

        if next_trade is not None and next_ob_update is not None:
            if next_trade.ts < next_ob_update.ts:
                self.logger.debug(
                    f'Trade event is ealry: {next_trade.ts.strftime("%Y-%m-%d %H:%M:%S")} < {next_ob_update.ts.strftime("%Y-%m-%d %H:%M:%S")}',                    
                )

                self.router.on_historical_trade(next_trade)
                self._update_last_ts(next_trade.ts)

                self._use_historical_trade()

            else: 
                self.logger.debug(
                    f'Order book updata event is ealry: {next_trade.ts.strftime("%Y-%m-%d %H:%M:%S")} > {next_ob_update.ts.strftime("%Y-%m-%d %H:%M:%S")}',
                )

                self.router.on_historical_order_book_update(next_ob_update)
                self._update_last_ts(next_ob_update.ts)

                self._use_next_historical_order_book_update()
        
        elif next_trade is not None:
            self.logger.debug("Has only trade event")

            self.router.on_historical_trade(next_trade)
            self._update_last_ts(next_trade.ts)

            self._use_historical_trade()
        
        elif next_ob_update is not None:
            self.logger.debug("Has only order book update event")

            self.router.on_historical_order_book_update(next_ob_update)
            self._update_last_ts(next_ob_update.ts)

            self._use_next_historical_order_book_update()

        else:
            self.logger.info("Ended")

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

    def _use_historical_trade(self):
        self.next_historical_trade = None

    def _use_next_historical_order_book_update(self):
        self.next_historical_order_book_update = None

    def _update_last_ts(self, ts):
        assert self.last_ts <= ts

        if self.last_ts == Timestamp.min or int(self.last_ts.timestamp() / 60) < int(ts.timestamp() / 60):
            self.logger.info(f'Ts: {ts}')
        
        self.last_ts = ts


# TODO: add tests
