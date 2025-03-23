from primitives import *
from events import HistoricalOrderBookUpdate, HistoricalTradeEvent
from typing import List
import json


class ParserBase:
    class FilesStream:
        def __init__(self):
            self.file_paths = iter([])
            self.current_file = None

        def set_files(self, file_paths: List[str]):
            self.file_paths = iter(sorted(file_paths))
            self.current_file = None

        def __iter__(self):
            return self

        def __next__(self):
            while True:
                if self.current_file is None:
                    file_path = next(self.file_paths, None)
                    
                    if file_path is None:
                        raise StopIteration

                    self.current_file = open(file_path)

                line = next(self.current_file, None)

                if line is None:
                    continue

                return line


    def __init__(self, file_paths: List[str]):
        self.stream = ParserBase.FilesStream(file_paths)
    
    def __iter__(self):
        return self


class OrderBookUpdateParser(ParserBase):
    '''
    Snashot:
    {
        "timestamp": "2025-03-17 17:04:30.942243347",
        "commands": [
            [
                "Snapshot",
                "BUY",
                [
                    [
                        "127.11",
                        "7027.28"
                    ],
                    [
                        "127.1",
                        "7027.21"
                    ]
                ]
            ],
            [
                "Snapshot",
                "SELL",
                [
                    [
                        "127.12",
                        "414.54"
                    ],
                    [
                        "127.13",
                        "414.55"
                    ]
                ]
            ]
        ]
    }
    '''

    def __init__(self):
        super().__init__()
        self.event = HistoricalOrderBookUpdate(OrderBookSnaphot(), None)

    def __next__(self):
        while True:
            line = next(self.stream, None)

            if line is None:
                raise StopIteration
            
            if not self._parse_and_apply_line(line):
                continue

            return self.event

    def _parse_and_apply_line(self, line) -> bool:
        OrderBookUpdateParser._parse_line(self.event, line)
        return len(self.event.snapshot.bids) != 0 and len(self.event.snapshot.asks) != 0

    @staticmethod 
    def _parse_line(event, line):
        data = json.loads(line)

        commands = data['commands']

        for command in commands:
            OrderBookUpdateParser._parse_commands(event.snapshot, command)

        event.ts = Timestamp.strptime(data['timestamp'][:26], "%Y-%m-%d %H:%M:%S.%f")

    @staticmethod
    def _parse_commands(snapshot: OrderBookSnaphot, commands):
        update_type = commands[0]

        side = Side.Buy if commands[1 if update_type == 'Snapshot' else 2] == 'BUY' else Side.Sell

        snapshot_side: OrderBookSide = snapshot[side]

        if len(snapshot_side) == 0 and update_type != 'Snapshot':
            return
        
        if update_type == 'Snapshot':
            snapshot_side.clear()
            for level in commands[2]:
                snapshot_side.append(OrderBookLevel(side, Price(level[0]), Quantity(level[1])))

        elif update_type == 'Increment':
            def try_insert():
                for i in range(len(snapshot_side)):
                    if snapshot_side[i].price == price:
                        if not quantity.is_zero():
                            snapshot_side[i].quantity = quantity
                        else:
                            snapshot_side.pop(i)

                        return True

                    elif (side == Side.Buy and price > snapshot_side[i].price) or (side == Side.Sell and price < snapshot_side[i].price):
                        if not quantity.is_zero():
                            snapshot_side.insert(i, OrderBookLevel(side, price, quantity))

                        return True

                return False

            for level in commands[3]:
                price = Price(level[0])
                quantity = Quantity(level[1])
                if not try_insert():
                    snapshot_side.append(OrderBookLevel(side, price, quantity))


class TradeParser(ParserBase):
    '''
    {
        "timestamp": "2025-03-21 12:00:00.000000000",
        "trades": [
            {
                "side": "BUY",
                "price": "84000",
                "qty": "0.00088"
            }
        ]
    }
    '''

    def __init__(self):
        super().__init__()
        self.next_events: List[HistoricalTradeEvent] = []

    def __next__(self):
        while True:
            if len(self.next_events) != 0:
                event = self.next_events[0]
                self.next_events.pop(0)
                return event

            line = next(self.stream, None)

            if line is None:
                raise StopIteration
            
            self._parse_and_apply_line(line)

    def _parse_and_apply_line(self, line):
        TradeParser._parse_line(self.next_events, line)

    @staticmethod
    def _parse_line(next_events, line):
        data = json.loads(line)

        ts = Timestamp.strptime(data['timestamp'][:26], "%Y-%m-%d %H:%M:%S.%f")

        for trade in data['trades']:
            side = Side.Buy if trade['side'] == 'BUY' else Side.Sell
            price = Price(trade['price'])
            quantity = Quantity(trade['qty'])
            event = HistoricalTradeEvent(Trade(side, price, quantity), ts)
            next_events.append(event)


# Tests ################################################################################################################


class TestOrderBookUpdateParser:
    # TODO: split test cases
    def test_parse_line(context):
        event = HistoricalOrderBookUpdate(OrderBookSnaphot(), None)

        # Initial snapshot
        line = '{"timestamp":"2025-03-17 17:04:30.942243347","commands":[["Snapshot","BUY",[["127.11","7027.28"],["127.1","7027.21"]]],["Snapshot","SELL",[["127.12","414.54"],["127.13","414.55"]]]]}'

        OrderBookUpdateParser._parse_line(event, line)
        snapshot = OrderBookSnaphot()
        snapshot.bids.append(OrderBookLevel(Side.Buy, Price("127.11"), Quantity("7027.28")))
        snapshot.bids.append(OrderBookLevel(Side.Buy, Price("127.1"), Quantity("7027.21")))
        snapshot.asks.append(OrderBookLevel(Side.Sell, Price("127.12"), Quantity("414.54")))
        snapshot.asks.append(OrderBookLevel(Side.Sell, Price("127.13"), Quantity("414.55")))
        assert event.snapshot == snapshot

        # Add middle price level
        line = '{"timestamp":"2025-03-17 17:04:31.530788493","commands":[["Increment","Reason: Depth","BUY",[["127.105","703.21"]]],["Increment","Reason: Depth","SELL",[["127.125","412.33"]]]]}'

        OrderBookUpdateParser._parse_line(event, line)
        snapshot = OrderBookSnaphot()
        snapshot.bids.append(OrderBookLevel(Side.Buy, Price("127.11"), Quantity("7027.28")))
        snapshot.bids.append(OrderBookLevel(Side.Buy, Price("127.105"), Quantity("703.21")))
        snapshot.bids.append(OrderBookLevel(Side.Buy, Price("127.1"), Quantity("7027.21")))
        snapshot.asks.append(OrderBookLevel(Side.Sell, Price("127.12"), Quantity("414.54")))
        snapshot.asks.append(OrderBookLevel(Side.Sell, Price("127.125"), Quantity("412.33")))
        snapshot.asks.append(OrderBookLevel(Side.Sell, Price("127.13"), Quantity("414.55")))
        assert event.snapshot == snapshot

        # Remove middle price level
        line = '{"timestamp":"2025-03-17 17:04:31.530788493","commands":[["Increment","Reason: Depth","BUY",[["127.105","0"]]],["Increment","Reason: Depth","SELL",[["127.125","0"]]]]}'

        OrderBookUpdateParser._parse_line(event, line)
        snapshot = OrderBookSnaphot()
        snapshot.bids.append(OrderBookLevel(Side.Buy, Price("127.11"), Quantity("7027.28")))
        snapshot.bids.append(OrderBookLevel(Side.Buy, Price("127.1"), Quantity("7027.21")))
        snapshot.asks.append(OrderBookLevel(Side.Sell, Price("127.12"), Quantity("414.54")))
        snapshot.asks.append(OrderBookLevel(Side.Sell, Price("127.13"), Quantity("414.55")))
        assert event.snapshot == snapshot

        # Add new bests
        line = '{"timestamp":"2025-03-17 17:04:31.530788493","commands":[["Increment","Reason: Depth","BUY",[["127.115","50"]]],["Increment","Reason: Depth","SELL",[["127.116","42"]]]]}'

        OrderBookUpdateParser._parse_line(event, line)
        snapshot = OrderBookSnaphot()
        snapshot.bids.append(OrderBookLevel(Side.Buy, Price("127.115"), Quantity("50")))
        snapshot.bids.append(OrderBookLevel(Side.Buy, Price("127.11"), Quantity("7027.28")))
        snapshot.bids.append(OrderBookLevel(Side.Buy, Price("127.1"), Quantity("7027.21")))
        snapshot.asks.append(OrderBookLevel(Side.Sell, Price("127.116"), Quantity("42")))
        snapshot.asks.append(OrderBookLevel(Side.Sell, Price("127.12"), Quantity("414.54")))
        snapshot.asks.append(OrderBookLevel(Side.Sell, Price("127.13"), Quantity("414.55")))
        assert event.snapshot == snapshot


class TestTradeParser:
    def test_parse_line(context):
        next_events = []

        line = '{"timestamp":"2025-03-21 12:00:12.995441514","trades":[{"side":"SELL","price":"83998","qty":"0.00015"},{"side":"BUY","price":"83997","qty":"0.00016"}]}'

        TradeParser._parse_line(next_events, line)
        trade = Trade(Side.Sell, Price("83998"), Quantity("0.00015"))
        assert next_events[0].trade == trade
        trade = Trade(Side.Buy, Price("83997"), Quantity("0.00016"))
        assert next_events[1].trade == trade

if __name__ == '__main__':
    import pytest
    pytest.main(["-v", __file__])


# Hide tests from import ###############################################################################################


__all__ = ['OrderBookUpdateParser', 'TradeParser']
