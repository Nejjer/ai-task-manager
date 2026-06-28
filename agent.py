import json
import logging
from datetime import datetime

from openai import AsyncOpenAI
from agents import Agent, AgentHooks, Runner, set_default_openai_client
from agents.mcp import MCPServerStreamableHttp
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from config import ROUTER_AI_API_KEY, TODOIST_API_KEY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("agent")

client = AsyncOpenAI(
    base_url="https://routerai.ru/api/v1",
    api_key=ROUTER_AI_API_KEY,
)
set_default_openai_client(client)

todoist_mcp = MCPServerStreamableHttp(
    params={
        "url": "https://ai.todoist.net/mcp",
        "headers": {"Authorization": f"Bearer {TODOIST_API_KEY}"},
    },
)

SYSTEM_PROMPT = """Ты помощник для управления задачами в Todoist.
Пользователь пишет на русском языке.
У тебя есть инструменты для работы с Todoist — используй их чтобы выполнить запрос.
После выполнения действия кратко сообщи пользователю что сделано.
Текущая дата и время передаются в каждом запросе.
Если пользователь говорит "утром" — используй 09:00.
Если пользователь говорит "вечером" — используй 19:00.
Если пользователь говорит "завтра" без времени — используй завтрашнюю дату без конкретного времени."""


class LoggingHooks(AgentHooks):
    async def on_llm_start(self, context, agent, system_prompt, input_items):
        logger.info(">>> LLM вызов (сообщений в контексте: %d)", len(input_items))

    async def on_llm_end(self, context, agent, response):
        usage = getattr(response, "usage", None)
        if usage:
            logger.info("<<< LLM ответ (токены: %s)", usage)
        else:
            logger.info("<<< LLM ответ получен")

    async def on_tool_start(self, context, agent, tool):
        args = getattr(context, "tool_arguments", None)
        name = getattr(tool, "name", str(tool))
        if args:
            try:
                pretty = json.dumps(json.loads(args), ensure_ascii=False, indent=2)
            except Exception:
                pretty = args
            logger.info("🔧 Инструмент: %s\n%s", name, pretty)
        else:
            logger.info("🔧 Инструмент: %s", name)

    async def on_tool_end(self, context, agent, tool, result):
        name = getattr(tool, "name", str(tool))
        preview = str(result)[:200] + ("..." if len(str(result)) > 200 else "")
        logger.info("✅ Результат [%s]: %s", name, preview)


agent = Agent(
    name="Todoist Manager",
    model=OpenAIChatCompletionsModel(model="openai/gpt-4o-mini", openai_client=client),
    mcp_servers=[todoist_mcp],
    instructions=SYSTEM_PROMPT,
    hooks=LoggingHooks(),
)


async def run_agent(message: str) -> str:
    stamped = f"[Сейчас: {datetime.now().strftime('%Y-%m-%d %H:%M')}]\n{message}"
    async with todoist_mcp:
        result = await Runner.run(agent, stamped)
    return result.final_output
