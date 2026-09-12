# Отчет о тестировании и статическом анализе кода

## Сводная информация

* Тестирование: 10 тестов успешно пройдены (100% success rate).
* Общее покрытие кода (Coverage): 90%.
* Форматирование кода (Black): Соответствует стандарту.
* Сортировка импортов (Isort): Соответствует стандарту.
* Статический анализ (Ruff): Пройдено без замечаний.
* Линтер (Flake8 / Wemake-python-styleguide): 0 ошибок (WPS).

---

## Результаты тестирования и покрытия (Pytest Coverage)

```text
❯ pytest --cov=backend backend/tests/                   
============================================================================= test session starts ==============================================================================
platform darwin -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/akldrix/PycharmProjects/python_advanced_diploma/backend
configfile: pyproject.toml
plugins: cov-7.1.0, asyncio-1.4.0, anyio-4.15.1
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 10 items                                                                                                                                                             

backend/tests/test_api.py ..........                                                                                                                                     [100%]

================================================================================ tests coverage ================================================================================
_______________________________________________________________ coverage: platform darwin, python 3.14.0-final-0 _______________________________________________________________

Name                              Stmts   Miss  Cover
-----------------------------------------------------
backend/app/__init__.py              34     11    68%
backend/app/database.py              14      2    86%
backend/app/models/__init__.py        4      0   100%
backend/app/models/tweets.py         28      0   100%
backend/app/models/users.py          13      0   100%
backend/app/routes/__init__.py        0      0   100%
backend/app/routes/medias.py         28      0   100%
backend/app/routes/tweets.py         63      9    86%
backend/app/routes/users.py          54     14    74%
backend/app/schemas/__init__.py       0      0   100%
backend/app/schemas/tweets.py        28      2    93%
backend/app/schemas/users.py          8      0   100%
backend/run.py                        4      4     0%
backend/tests/__init__.py             0      0   100%
backend/tests/conftest.py            66      0   100%
backend/tests/test_api.py            77      0   100%
-----------------------------------------------------
TOTAL                               421     42    90%
============================================================================== 10 passed in 0.15s ==============================================================================
```

---

## Результаты статического анализа и форматирования

### Проверка форматирования (Black)
```text
❯ black --check --diff .
All done!
19 files would be left unchanged.
```

### Проверка сортировки импортов (Isort)
```text
❯ isort --check-only --profile black .
```
*Вывод пуст*

### Проверка линтера (Ruff)
```text
❯ ruff check
All checks passed!
```

### Проверка стиля и сложности кода (Flake8 / Wemake-python-styleguide)
```text
❯ flake8 . --select=WPS
0
```

