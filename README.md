# Проект парсинга pep
### Описание bs4_parser_pep:
Благодаря этому парсеру можно:
- получить информацию из статей о нововведениях в Python.
- получить ссылки на документацию различных версий Python и их статус.
- загрузить документацию к Python.
- анализировать статусы PEP: посчитать количество PEP в каждом статусе
     и общее количество PEP.

### УСТАНОВКА:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:ArtemBalandin81/bs4_parser_pep.git
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```
Запустить справку по проекту (из каталога src):

```
(venv) ...$ python main.py -h
```

## Используемые технологии:

- Python 3.7
- beautifulsoup4 

## Некоторые примеры запросов парсера

Очистить кэш:

```
(venv) ...$ python main.py whats-new -c
(venv) ...$ python main.py pep -c
```

Запуск парсера информации из статей о нововведениях в Python.

```
(venv) ...$ python main.py whats-new
```
Запуск парсера статусов версий Python.

```
(venv) ...$ python main.py latest-versions
```
Запуск парсера подсчета PEP Python.

```
(venv) ...$ python main.py pep
```
Запуск парсера, который скачивает архив документации Python.

```
(venv) ...$ python main.py download
```
Запуск парсера - сохранение результатов в файл.

```
(venv) ...$ python main.py whats-new --output file
(venv) ...$ python main.py latest-versions --output file
(venv) ...$ python main.py pep --output file
```
Запуск парсера - сохранение результатов в терминале в красивой таблице.

```
(venv) ...$ python main.py whats-new --output pretty
(venv) ...$ python main.py latest-versions --output pretty
(venv) ...$ python main.py pep --output pretty
```

### Автор
[Артем Баландин](https://github.com/ArtemBalandin81)
