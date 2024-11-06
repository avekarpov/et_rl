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
        
