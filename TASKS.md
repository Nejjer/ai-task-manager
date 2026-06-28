# TASKS.md — Задачи для реализации

Выполняй строго по порядку. Отмечай задачи выполненными по мере завершения.

---

## Задача 1: Окружение ✅

- [x] Создать виртуальное окружение: `python -m venv venv`
- [x] Активировать: `source venv/bin/activate`
- [x] Создать `requirements.txt` согласно SPEC.md
- [x] Установить зависимости: `pip install -r requirements.txt`

**Проверка:** `pip list` показывает fastapi, uvicorn, openai-agents, python-dotenv

---

## Задача 2: Конфигурация ✅

- [x] Создать `.env.example` с пустыми переменными `ROUTER_AI_API_KEY` и `TODOIST_API_KEY`
- [x] Создать `.env` с реальными значениями (заполняет пользователь)
- [x] Создать `config.py` который загружает переменные из `.env` и бросает `ValueError` если они не заданы

**Проверка:** `python config.py` выполняется без ошибок если `.env` заполнен

---

## Задача 3: Агент ✅

- [x] Создать `agent.py`
- [x] Настроить `AsyncOpenAI` клиент с `base_url` провайдера
- [x] Подключить Todoist MCP сервер через `MCPServerStreamableHttp`
- [x] Создать `Agent` с моделью, MCP сервером и system prompt из SPEC.md
- [x] Реализовать `async def run_agent(message: str) -> str`

**Проверка:** `python -c "import asyncio; from agent import run_agent; print(asyncio.run(run_agent('Что у меня на сегодня?')))"` возвращает осмысленный ответ

---

## Задача 4: FastAPI приложение ✅

- [x] Создать `main.py`
- [x] Определить `ChatRequest` и `ChatResponse` модели
- [x] Реализовать `POST /chat` эндпоинт который вызывает `run_agent`
- [x] Обернуть вызов в try/except, при ошибке возвращать HTTP 500

**Проверка:** `uvicorn main:app --reload` запускается без ошибок, `http://localhost:8000/docs` открывается

---

## Задача 5: Финальная проверка ✅

- [x] Запустить сервер
- [x] Выполнить все три curl-запроса из раздела "Примеры запросов" в SPEC.md
- [x] Убедиться что задача действительно создаётся в Todoist
- [x] Убедиться что список задач возвращается корректно
