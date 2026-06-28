import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_BOT_TOKEN, PROXY_URL
from agent import run_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("bot")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогаю управлять задачами в Todoist.\n"
        "Просто напиши что нужно сделать, например:\n\n"
        "• Напомни завтра утром купить молоко\n"
        "• Что у меня на сегодня?\n"
        "• Покажи все задачи"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    user = update.effective_user.full_name
    logger.info("Сообщение от %s: %s", user, message)

    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        response = await run_agent(message)
        await update.message.reply_text(response)
    except Exception as e:
        logger.error("Ошибка агента: %s", e)
        await update.message.reply_text("Произошла ошибка. Попробуй ещё раз.")


def main():
    builder = Application.builder().token(TELEGRAM_BOT_TOKEN)
    if PROXY_URL:
        builder = builder.proxy(PROXY_URL).get_updates_proxy(PROXY_URL)
        logger.info("Прокси: %s", PROXY_URL)
    app = builder.build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
