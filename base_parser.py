import csv
from typing import List

class BaseParser:
    def __init__(self, file_paths: List[str], skip_title=True):
        self.file_paths = sorted(file_paths)
        self.skip_title = skip_title

        self.index = 0
        self.reader = None

    def __len__(self):
        return len(self.file_paths)

    def __iter__(self):
        return self

    def __next__(self):
        if len(self) <= self.index:
            raise StopIteration

        if self.reader is None:
            self.reader = csv.reader(open(self.file_paths[self.index]), delimiter=',')
            
            if self.skip_title:
                next(self.reader)

        line = next(self.reader, None)

        if line is None:
            self.index += 1
            self.reader = None

            return next(self)
        
        return self.parse_csv_line(line)