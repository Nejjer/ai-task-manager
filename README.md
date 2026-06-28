# Todo AI Manager

REST API для управления задачами в Todoist через естественный язык. Отправляете текст на русском — AI агент интерпретирует его и выполняет нужное действие в Todoist.

## Как это работает

```
POST /chat
    ↓
FastAPI
    ↓
AI Agent (openai-agents) — openai/gpt-4o-mini через routerai.ru
    ↕ MCP Streamable HTTP
Todoist MCP Server (ai.todoist.net)
    ↕
Todoist API
```

## Установка

```bash
git clone <repo>
cd todo-ai-manager-new

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Скопируйте `.env.example` в `.env` и заполните ключи:

```bash
cp .env.example .env
```

```env
ROUTER_AI_API_KEY=ваш_ключ_от_routerai.ru
TODOIST_API_KEY=ваш_токен_todoist
```

## Запуск

```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

## Использование

```bash
# Создать задачу
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Напомни завтра утром купить пельмени"}'

# Задачи на сегодня
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Что у меня на сегодня?"}'

# Все задачи
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Покажи все мои задачи"}'
```

Формат ответа:

```json
{"response": "Задача 'Купить пельмени' создана на завтра в 9:00"}
```

## Соглашения о времени

| Фраза | Время |
|---|---|
| "утром" | 09:00 |
| "вечером" | 19:00 |
| "завтра" (без времени) | завтрашняя дата без времени |

## Структура проекта

```
├── .env                  # API ключи (не коммитить)
├── .env.example          # Шаблон для .env
├── requirements.txt
├── config.py             # Загрузка переменных окружения
├── agent.py              # AI агент + подключение к Todoist MCP
└── main.py               # FastAPI приложение
```

## Получение ключей

- **ROUTER_AI_API_KEY** — регистрация на [routerai.ru](https://routerai.ru)
- **TODOIST_API_KEY** — Settings → Integrations → Developer token на [todoist.com](https://todoist.com)
