import argparse
import logging
from logging.handlers import RotatingFileHandler

import tqdm

from constants import LOG_DIR, LOG_FILE, PARSER_FILE, PARSER_PRETTY

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'


class TqdmLoggingHandler(logging.Handler):
    """Custom logging handler to avoid logging interfere with progress bars."""
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            message = self.format(record)
            tqdm.tqdm.write(message)
            self.flush()
        except Exception:
            self.handleError(record)


def configure_argument_parser(available_modes):
    """Конфигурирует работу парсера через аргументы командной строки."""
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(PARSER_PRETTY, PARSER_FILE),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    """Конфигурирует логгирование в парсере"""
    LOG_DIR.mkdir(exist_ok=True)
    rotating_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10 ** 6, backupCount=5
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(
            TqdmLoggingHandler(),
            rotating_handler,
        )
    )
