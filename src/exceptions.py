class ParserFindTagException(Exception):
    """Класс исключений. Вызывается, когда парсер не может найти тег."""
    pass


class ParserFindKeyWordException(Exception):
    """Вызывается, когда парсер не может найти ключевое слово."""
    pass