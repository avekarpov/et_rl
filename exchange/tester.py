from order_book import OrderBook as Ob
from matching_engine import MatchingEngine as Me
from user_orders_contorller import UserOrdersController as Oc
from parsers import OrderBookUpdateParser as ObUpdateParer, TradeParser
from runner import Runner
from tools import list_dir_regex


class Tester:
    def __init__(self):
        self.runner = Runner()
        self.runner.set_order_book_update_parser(ObUpdateParer())
        self.runner.set_trade_parser(TradeParser())

        self.oc = Oc(self.runner.router)
        self.ob = Ob(self.runner.router, self.oc)
        self.me = Me(self.runner.router, self.oc)

    def set_dir(self, dir_path):
        #file name format TS_SYMBOL_TYPE
        self.runner.trade_parser.set_files(list_dir_regex(dir_path, r'.*trades'))
        self.runner.order_book_update_parser.set_files(list_dir_regex(dir_path, r'.*order_book_updates'))

    def set_consumer(self, consumer):
        self.runner.router.set_consumer(consumer)

    def run(self):
        while self.runner:
            pass