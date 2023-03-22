from bs4 import BeautifulSoup
from requests import RequestException

from constants import INFO_TAG_ERROR, INFO_URL_UNAVAILABLE
from exceptions import ParserFindTagException


def get_response(session, url, charset='utf-8'):
    """Реализует перехват ошибки соединения и записывает ее в логи."""
    try:
        response = session.get(url)
        response.encoding = charset
        return response
    except RequestException:
        raise ConnectionError(INFO_URL_UNAVAILABLE.format(url))


def find_tag(soup, tag, attrs=None):
    """Перехват ошибки поиска тегов."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(INFO_TAG_ERROR.format(tag, attrs))
    return searched_tag


def get_soup(session, url, parse_settings='lxml'):
    """Готовит суп"""
    return BeautifulSoup(get_response(session, url).text, parse_settings)
