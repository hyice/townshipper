#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import inspect


class IndentFormatter(logging.Formatter):
    def __init__(self, fmt=None, date_fmt=None):
        logging.Formatter.__init__(self, fmt, date_fmt)

        self.baseline = len(inspect.stack())

    def format(self, record):
        stack = inspect.stack()
        record.indent = '  ' * (len(stack) - self.baseline)
        record.function = stack[8][3]
        out = logging.Formatter.format(self, record)
        del record.indent; del record.function
        return out


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    formatter = IndentFormatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
