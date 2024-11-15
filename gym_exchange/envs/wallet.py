from event import EventHandler, Event
from order_book import Side

class TradeResult:
    pnl = None
    position = None
    fiat = None

class Wallet(EventHandler):
    pnl_window_s = 30 * 60
    pnl_position_coef = 1

    postion = 0
    fiat = 0

    fill_events = []

    last_pnl = None

    def process_event_fill(self, fill_event):
        if self.pnl_window_s != 0:
            while len(self.fill_events) != 0 and self.fill_events[0].ts + self.pnl_window_s * 1000 < fill_event.ts:
                event = self.fill_events[0]
                if event.value.side == Side.Sell:
                    self.postion += event.value.amount
                    self.fiat -= event.value.amount * event.value.price
                else:
                    self.postion -= event.value.amount
                    self.fiat += event.value.amount * event.value.price
                self.fill_events.pop(0)
  
        if fill_event.value.side == Side.Buy:
            self.postion += fill_event.value.amount
            self.fiat -= fill_event.value.amount * fill_event.value.price
        else:
            self.postion -= fill_event.value.amount
            self.fiat += fill_event.value.amount * fill_event.value.price

        self.fill_events.append(fill_event)

        trade_result = TradeResult()
        trade_result.pnl = self.pnl(fill_event.value.price)
        trade_result.position = self.postion
        trade_result.fiat = self.fiat

        pnl = Event(fill_event.ts)
        pnl.value = ('trade_result', trade_result)

        return [pnl]
    
    def process_event_order_book(self, event):
        if self.postion >= 0:
            price = event.value.bids[0].price
        else:
            price = event.value.asks[0].price

        self.last_pnl = self.fiat / price + self.postion * self.pnl_position_coef

        trade_result = TradeResult()
        trade_result.pnl = self.last_pnl
        trade_result.position = self.postion
        trade_result.fiat = self.fiat

        pnl = Event(event.ts)
        pnl.value = ('trade_result', trade_result)

        return [pnl]

    def state(self):
        return {'last_pnl': self.last_pnl}

    def reset(self):
        self.postion = 0
        self.fiat = 0
        self.fill_events = []
