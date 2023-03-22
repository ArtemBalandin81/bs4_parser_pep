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
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOAD_DIR, EXPECTED_STATUS,
                       INFO_ALL_VERSHIONS_NOT_FOUND, INFO_ARGS,
                       INFO_DIFFERENT_STATUS, INFO_DOWNLOAD, INFO_ERROR,
                       INFO_FINISH, INFO_START, INFO_URL_UNAVAILABLE,
                       MAIN_DOC_URL, PEPS_URL)
from exceptions import ParserFindTagException
from outputs import control_output
from utils import find_tag, get_soup


def whats_new(session):
    """Собирает ссылки на статьи об изменениях между основными версиями Python
     и достанете из них справочную информацию: имя автора (редактора) статьи"""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    sections_by_python = get_soup(session, whats_new_url).select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1 >a'
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    messages = []
    for section in tqdm(sections_by_python, desc='sections_by_python'):
        href = section['href']
        version_link = urljoin(whats_new_url, href)
        try:
            soup = get_soup(session, version_link)
        except ConnectionError as error:
            messages.append(INFO_URL_UNAVAILABLE.format(version_link, error))
            continue
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        results.append(
            (version_link, h1.text.encode("utf-8"), dl.text.encode("utf-8"))
        )
    for log in messages:
        logging.info(log)
    return results


def latest_versions(session):
    """Собирает ссылки на документацию различных версий Python и их статус."""
    ul_tags = get_soup(session, MAIN_DOC_URL).select(
        'div.sphinxsidebarwrapper ul'
    )
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException(INFO_ALL_VERSHIONS_NOT_FOUND)
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        if re.search(pattern, a_tag.text):
            version = re.search(pattern, a_tag.text).group(1)
            status = re.search(pattern, a_tag.text).group(2)
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


def download(session):
    """Загружает документацию к Python."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    archive_url = urljoin(
        downloads_url,
        soup.select_one('table.docutils a[href$="pdf-a4.zip"]')['href']
    )
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOAD_DIR
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(INFO_DOWNLOAD.format(archive_path))


def pep(session):
    """Парсит статусы PEP: считает количество PEP в каждом статусе
     и общее количество PEP."""
    pattern_status = r'Status:\n(\w+)'
    total_status = defaultdict(int)
    soup = get_soup(session, PEPS_URL)
    numerical_index = soup.find('section', attrs={'id': 'numerical-index'})
    pep_string = numerical_index.find_all('tr')
    messages = []
    for item in tqdm(pep_string[1:], desc='calculate total_status'):
        pep_table_status = item.find('abbr').text[1:]
        pep_reference = item.find(
            'a', attrs={'class': 'pep reference internal'}
        )['href']
        pep_link = urljoin(PEPS_URL, pep_reference)
        try:
            pep_soup = get_soup(session, pep_link)
        except ConnectionError as error:
            messages.append(INFO_URL_UNAVAILABLE.format(pep_link, error))
            continue
        field_list_simple = pep_soup.find(
            'dl', attrs={'class': 'rfc2822 field-list simple'}
        )
        pep_status = re.search(pattern_status, field_list_simple.text)[1]
        if pep_status not in EXPECTED_STATUS[pep_table_status]:
            messages.append(
                INFO_DIFFERENT_STATUS.format(
                    pep_link,
                    {pep_status},
                    {EXPECTED_STATUS[pep_table_status]}
                )
            )
        total_status[pep_status] += 1
    for log in messages:
        logging.info(log)
    return [
        ('Status', 'Quantities'),
        *total_status.items(),
        ('Total', sum(total_status.values()))
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    """Запускает парсер через аргументы командной строки"""
    configure_logging()
    logging.info(INFO_START)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(INFO_ARGS.format(args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        results = MODE_TO_FUNCTION[args.mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as error:
        logging.error(INFO_ERROR.format(error))
    logging.info(INFO_FINISH)


if __name__ == '__main__':
    main()
