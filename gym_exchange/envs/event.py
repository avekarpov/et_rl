from typing import Any


class Event:
    name = ''

    def __init__(self, ts):
        self.ts = ts

    @property
    def value(self):
        return getattr(self, self.name)

    @value.setter
    def value(self, name_value):
        (name, value) = name_value
        self.name = name
        setattr(self, name, value)

    def __str__(self):
        return f'{{"name": "{self.name}", "value": {self.value}, "ts": {self.ts}}}'
        
class EventHandler:
    def process_event(self, event):
        if event.name == 'order_book':
            return self.process_event_order_book(event)
        elif event.name == 'trade':
            return self.process_event_trade(event)
        elif event.name == 'place_market':
            return self.process_event_place_market(event)
        elif event.name == 'fill':
            return self.process_event_fill(event)
        elif event.name == 'trade_result':
            return self.process_event_pnl(event)
        else:
            assert False
        
    def process_event_order_book(self, event):
        return []

    def process_event_trade(self, event):
        return []

    def process_event_place_market(self, event):
        return []

    def process_event_fill(self, event):
        return []
    
    def process_event_pnl(self, event):
        return []