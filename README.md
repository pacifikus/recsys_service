# Сервис рекомендаций

[![Tests](https://github.com/pacifikus/recsys_service/actions/workflows/tests.yml/badge.svg)](https://github.com/pacifikus/recsys_service/actions/workflows/tests.yml)
[![Code review](https://github.com/pacifikus/recsys_service/actions/workflows/code-style.yml/badge.svg)](https://github.com/pacifikus/recsys_service/actions/workflows/code-style.yml)

## Описание

[FastAPI](https://fastapi.tiangolo.com/) сервис для получения рекомендаций из 10 объектов для каждого пользователя из тестовой выборки МТС Kion.

### Данные

Для реализации были использованы данные из приложения МТС Kion по взаимодействиям пользователей с контентом за период 6 месяцев, взятые из [RecSys Course Competition](https://ods.ai/competitions/competition-recsys-21).
Датасет содержит:

- факты просмотра контента пользователями
- описание контента
- описание пользователей

## Запуск приложения

### Инициализация окружения

Выполните команду
```
make setup
```

Будет создано новое виртуальное окружение в папке `.venv`.
В него будут установлены пакеты, перечисленные в файле `pyproject.toml`.

### Установка пакетов

Для установки новых пакетов используйте команду `poetry add`.

### Запуск сервиса

#### Способ 1: Python + Uvicorn

```
python main.py
```

Приложение запустится локально, в одном процессе. 
Хост и порт по умолчанию: `127.0.0.1` и `8080`.
Их можно изменить через переменные окружения `HOST` и `PORT`.

Управляет процессом легковесный [ASGI](https://asgi.readthedocs.io/en/latest/) server [uvicorn](https://www.uvicorn.org/).


#### Способ 2: Uvicorn

```
uvicorn main:app
```

Запуск напрямую через [uvicorn](https://www.uvicorn.org/).

#### Способ 3: Docker

Собрать и запустить Docker-образ можно командой

```
make run
```
