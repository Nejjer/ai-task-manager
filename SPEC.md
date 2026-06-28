# SPEC.md — Спецификация проекта

## Что строим

REST API с одним POST эндпоинтом. Пользователь отправляет текстовое сообщение на русском языке, AI агент интерпретирует его и управляет задачами в Todoist.

Пример:
- Вход: `{"message": "Напомни завтра утром купить пельмени"}`
- Выход: `{"response": "Задача 'Купить пельмени' создана на завтра в 9:00"}`

---

## Архитектура

```
POST /chat
    ↓
FastAPI (main.py)
    ↓
AI Agent (agent.py) — openai-agents SDK
    ↕ MCP Streamable HTTP
Todoist MCP Server (https://ai.todoist.net/mcp)
    ↕
Todoist API
```

---

## Стек

| Компонент | Решение |
|---|---|
| Web фреймворк | FastAPI + uvicorn |
| AI агент | openai-agents |
| LLM провайдер | https://routerai.ru/api/v1 |
| Модель | openai/gpt-4o-mini |
| Todoist MCP | https://ai.todoist.net/mcp (Streamable HTTP) |
| Env vars | python-dotenv |

---

## Структура файлов

```
todo-ai-manager-new/
├── .env                  # API ключи (не коммитить)
├── .env.example          # Шаблон для .env
├── requirements.txt      # Зависимости
├── config.py             # Загрузка настроек из .env
├── agent.py              # AI агент + MCP подключение
└── main.py               # FastAPI приложение
```

---

## Переменные окружения

```env
ROUTER_AI_API_KEY=       # API ключ провайдера routerai.ru
TODOIST_API_KEY=          # API токен Todoist
```

---

## requirements.txt

```
fastapi
uvicorn
openai-agents
python-dotenv
```

---

## config.py

Загружает переменные из `.env` и экспортирует как константы:
- `ROUTER_AI_API_KEY`
- `TODOIST_API_KEY`

Если переменная не задана — бросать `ValueError` с понятным сообщением.

---

## agent.py

### Настройка LLM клиента

Создать `AsyncOpenAI` клиент с:
- `base_url="https://routerai.ru/api/v1"`
- `api_key=ROUTER_AI_API_KEY`

Передать его как default клиент через `set_default_openai_client()`.

### Подключение к Todoist MCP

```python
from agents.mcp import MCPServerStreamableHttp

todoist_mcp = MCPServerStreamableHttp(
    url="https://ai.todoist.net/mcp",
    headers={"Authorization": f"Bearer {TODOIST_API_KEY}"}
)
```

### Агент

```python
from agents import Agent

agent = Agent(
    name="Todoist Manager",
    model="openai/gpt-4o-mini",
    mcp_servers=[todoist_mcp],
    instructions=SYSTEM_PROMPT
)
```

### System prompt

```
Ты помощник для управления задачами в Todoist. 
Пользователь пишет на русском языке.
У тебя есть инструменты для работы с Todoist — используй их чтобы выполнить запрос.
После выполнения действия кратко сообщи пользователю что сделано.
Текущая дата и время передаются в каждом запросе.
Если пользователь говорит "утром" — используй 09:00. 
Если пользователь говорит "вечером" — используй 19:00.
Если пользователь говорит "завтра" без времени — используй завтрашнюю дату без конкретного времени.
```

### Функция запуска агента

```python
async def run_agent(message: str) -> str
```

Принимает строку сообщения, возвращает строку ответа агента.
Передавать текущую дату/время как часть сообщения:
`f"[Сейчас: {datetime.now().strftime('%Y-%m-%d %H:%M')}]\n{message}"`

---

## main.py

### Модели запроса/ответа

```python
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
```

### Эндпоинт

```
POST /chat
Content-Type: application/json

Тело: {"message": "текст запроса"}
Ответ: {"response": "ответ агента"}
```

При ошибке возвращать HTTP 500 с `{"detail": "описание ошибки"}`.

### Запуск сервера

```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Примеры запросов для проверки

```bash
# Создать задачу
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Напомни завтра утром купить пельмени"}'

# Посмотреть задачи на сегодня
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Что у меня на сегодня?"}'

# Посмотреть все задачи
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Покажи все мои задачи"}'
```
