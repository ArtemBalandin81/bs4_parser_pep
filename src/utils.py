from http import HTTPStatus

from requests import RequestException

from constants import INFO_TAG_ERROR, INFO_URL_UNAVAILABLE
from exceptions import ParserFindTagException


def get_response(session, url, charset='utf-8'):
    """Реализует перехват ошибки RequestException и записывает ее в логи."""
    response = session.get(url)
    response.encoding = charset
    if response.status_code != HTTPStatus.OK:
        raise ConnectionError(
            INFO_URL_UNAVAILABLE.format(url),
        )
    return response


def find_tag(soup, tag, attrs=None):
    """Перехват ошибки поиска тегов."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(INFO_TAG_ERROR.format(tag, attrs))
    return searched_tag
