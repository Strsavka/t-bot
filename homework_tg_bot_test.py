import logging
import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler

# TOKEN for Telegram-bot is necessary
BOT_TOKEN = '7596957066:AAH5kPuJH1823dvaoIbaEYB7T79Y9oP-P78'

# Logging in
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# database connection
connection = sqlite3.connect("homework_database.sqlite")
cursor = con.cursor()


async def text_answer(updater, context):
    await updater.message.reply_text('Запрос не принят')


async def start(update, context):
    # Добавить в базу данных пользователей
    cursor.execute('''INSERT INTO users(name, telegram_id, username) VALUES(?, ?, ?)''', (...))
    user = update.effective_user
    await update.message.reply_html(rf"Привет {user.mention_html()}! Я телеграм-бот",)


def initialization():
    # Making an application of Telegram-bot
    application = Application.builder().token(BOT_TOKEN).build()

    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, text_answer)
    application.add_handler(text_handler)
    application.add_handler(CommandHandler("start", start))
    application.run_polling()


if __name__ == '__main__':
    initialization()