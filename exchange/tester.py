from exchange.order_book import OrderBook as Ob
from exchange.matching_engine import MatchingEngine as Me
from exchange.user_orders_contorller import UserOrdersController as Uoc
from exchange.parsers import OrderBookUpdateParser as ObUpdateParer, TradeParser
from exchange.runner import Runner
from exchange.tools import list_dir_regex
from exchange.logging import Logger
import re


class Tester(Logger):
    def __init__(self):
        super().__init__()

        self.runner = Runner()
        self.runner.set_order_book_update_parser(ObUpdateParer())
        self.runner.set_trade_parser(TradeParser())

        self.uoc = Uoc(self.runner.router)
        self.ob = Ob(self.runner.router, self.uoc)
        self.me = Me(self.runner.router, self.uoc)

    def set_dir(self, dir_path):
        self.logger.info(f'Use dir: {dir_path}')

        self.runner.trade_parser.set_files(list_dir_regex(dir_path, re.compile(r'.*trades')))
        self.runner.order_book_update_parser.set_files(list_dir_regex(dir_path, re.compile(r'.*order_book_updates')))

    def add_consumer(self, consumer):
        self.runner.router.add_consumer(consumer)

    def run(self, after_step=None):
        self.logger.info("Start runner")

        for _ in self.runner:
            if after_step is not None:
                after_step()
