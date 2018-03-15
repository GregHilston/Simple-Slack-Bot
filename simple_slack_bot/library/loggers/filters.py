"""Implements filters for logging."""

import logging


class LevelFilter(logging.Filter):
    """Limit the logging level between high and low for a logger.

    Attributes:
        _low (int): Lower bound for logging value.
        _high (int): Upper bound for logging value.

    """

    def __init__(self, low, high):
        """Set up the logging pass through levels.

        Args:
            low (int): Lower bound for logging value.
            high (int): Upper bound for logging value.

        """
        self._low = low
        self._high = high
        logging.Filter.__init__(self)

    def filter(self, record):
        """Determine if we want to filter out an record.

        Args:
            record (logging.LogRecord): A LogRecord from the logging module.

        """
        # If the level of the record is between low and high, then we don't want to filter it, else we will filter.
        if self._low <= record.levelno <= self._high:
            return True
        return False
