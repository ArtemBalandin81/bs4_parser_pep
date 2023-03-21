import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (BASE_DIR, DATETIME_FORMAT, INFO_SAVE, PARSER_FILE,
                       PARSER_PRETTY, RESULTS_DIR)


def control_output(results, cli_args):
    """
    Отвечает за контроль выходных данных парсера:
    results — список с результатами results из функции main() файла main.py
    cli_args — объект с аргументами командной строки
    """
    output_dictionary = {
        PARSER_PRETTY: pretty_output,
        PARSER_FILE: file_output,
        None: default_output
    }
    output_dictionary[cli_args.output](results, cli_args)


def default_output(results, cli_args):
    """Вывод данных по умолчанию (построчно)."""
    for row in results:
        print(*row)


def pretty_output(results, cli_args):
    """Вывод данных в формате таблицы"""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """Создает директорию и записывает данные в файл."""
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    #RESULTS_DIR.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    #file_path = RESULTS_DIR / file_name
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        writer.writerows(results)
    logging.info(INFO_SAVE.format(file_path))
