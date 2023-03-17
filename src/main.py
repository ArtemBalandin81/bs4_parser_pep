"""
# Справка по парсеру
(venv) ...$ python main.py -h

# Запуск парсера информации из статей о нововведениях в Python.
(venv) ...$ python main.py whats-new

# Запуск парсера статусов версий Python.
(venv) ...$ python main.py latest-versions

# Запуск парсера подсчета PEP Python.
(venv) ...$ python main.py pep

# Запуск парсера, который скачивает архив документации Python.
(venv) ...$ python main.py download

# Запуск парсера - сохранение результатов в файл.
(venv) ...$ python main.py whats-new --output file
(venv) ...$ python main.py latest-versions --output file
(venv) ...$ python main.py pep --output file

# Запуск парсера - сохранение результатов в терминале в красивой таблице.
(venv) ...$ python main.py whats-new --output pretty
(venv) ...$ python main.py latest-versions --output pretty
(venv) ...$ python main.py pep --output pretty

# Очистка кэша.
(venv) ...$ python main.py whats-new -c
(venv) ...$ python main.py pep -c
"""
import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PATTERN_STATUS, PEPS_URL
)
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    """Собирает ссылки на статьи об изменениях между основными версиями Python
     и достанете из них справочную информацию: имя автора (редактора) статьи"""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python, desc='sections_by_python'):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        results.append(
            (version_link, h1.text.encode("utf-8"), dl.text.encode("utf-8"))
        )
    return results


def latest_versions(session):
    """Собирает ссылки на документацию различных версий Python и их статус."""
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        if re.search(pattern, a_tag.text):
            version = re.search(pattern, a_tag.text).group(1)
            status = re.search(pattern, a_tag.text).group(2)
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    """Загружает документацию к Python."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    """Парсит статусы PEP: считает количество PEP в каждом статусе
     и общее количество PEP."""
    total_status = {
        'Active': 0,
        'Accepted': 0,
        'Deferred': 0,
        'Final': 0,
        'Provisional': 0,
        'Rejected': 0,
        'Superseded': 0,
        'Withdrawn': 0,
        'Draft': 0,
        'April': 0,
    }
    results = [('Status', 'Quantity')]
    response = get_response(session, PEPS_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    numerical_index = soup.find('section', attrs={'id': 'numerical-index'})
    pep_string = numerical_index.find_all('tr')
    for item in tqdm(pep_string[1:], desc='calculate total_status'):
        pep_table_status = item.find('abbr').text[1:]
        pep_reference = item.find(
            'a', attrs={'class': 'pep reference internal'}
        )['href']
        pep_link = urljoin(PEPS_URL, pep_reference)
        pep_response = session.get(pep_link)
        pep_soup = BeautifulSoup(pep_response.text, features='lxml')
        field_list_simple = pep_soup.find(
            'dl', attrs={'class': 'rfc2822 field-list simple'}
        )
        pep_status = re.search(PATTERN_STATUS, field_list_simple.text)
        if pep_status.group(1) not in EXPECTED_STATUS[pep_table_status]:
            logging.info('Несовпадающие статусы:')
            logging.info(f'{pep_link}')
            logging.info(f'Статус в карточке: {pep_status.group(1)}')
            logging.info(
                f'Ожидаемые статусы: {EXPECTED_STATUS[pep_table_status]}')
        count_status = total_status.get(pep_status.group(1))
        count_status += 1
        total_status[pep_status.group(1)] = count_status
    for status, quantity in total_status.items():
        results.append((status, quantity))
    results.append(('Total', sum(total_status.values())))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    """Запускает парсер через аргументы командной строки"""
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
