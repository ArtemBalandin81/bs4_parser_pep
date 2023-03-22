from pathlib import Path

BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
PARSER_FILE = 'file'
PARSER_PRETTY = 'pretty'
RESULTS_DIR = 'results'

INFO_ALL_VERSHIONS_NOT_FOUND = '"All versions" не найдены.'
INFO_ARGS = 'Аргументы командной строки {}'
INFO_DIFFERENT_STATUS = (
    '\nНесовпадающие статусы:\n{}'
    '\nСтатус в карточке: {}\n'
    'Ожидаемые статусы: {}'
)
INFO_DOWNLOAD = 'Архив был загружен и сохранён {}'
INFO_FINISH = 'Парсер завершил работу.'
INFO_URL_UNAVAILABLE = 'Страница {} не доступна'
INFO_SAVE = 'Файл с результатами был сохранён {}'
INFO_START = 'Парсер запущен.'
INFO_TAG_ERROR = 'Не найден тег {} {}'
INFO_ERROR = 'Ошибка {}'

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEPS_URL = 'https://peps.python.org/'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
