from typing import List
import csv
import logging

class BaseParser:
    def __init__(self, file_paths: List[str], skip_title=True):
        self.file_paths = sorted(file_paths)
        self.skip_title = skip_title

        self.index = 0
        self.reader = None

        self.logger = logging.getLogger(type(self).__name__)

    def __len__(self):
        return len(self.file_paths)

    def __iter__(self):
        return self

    def __next__(self):
        def open_next_file():
            if len(self) <= self.index:
                raise StopIteration

            self.reader = csv.reader(open(self.file_paths[self.index]), delimiter=',')
            if self.skip_title:
                next(self.reader)

        if self.reader is None:
            open_next_file()

        while True:
            line = next(self.reader, None)
            while line is None:
                self.index += 1
                self.reader = None
                open_next_file()

                line = next(self.reader, None)

            try:
                return self.parse_csv_line(line)
            except Exception as error:
                self.logger.warning(f'Failed to parse line "{self.file_paths[self.index]}:{line}": {error}')
