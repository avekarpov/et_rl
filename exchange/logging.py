import logging
from logging import ERROR, WARNING, INFO, DEBUG


class Logger:
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)

    def _log_event(self, event, level = DEBUG):
        self.logger.debug(f'Receive event: {event}')


def default_config(level = INFO):
    logging.basicConfig(
        level=level,
        # TODO: review
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    logging.getLogger("matplotlib").setLevel(logging.CRITICAL)
