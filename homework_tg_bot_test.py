import logging
import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler

# TOKEN for Telegram-bot is necessary
BOT_TOKEN = '7596957066:AAH5kPuJH1823dvaoIbaEYB7T79Y9oP-P78'

# logging in
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# mark_ups making
keyboard_for_menu = [[KeyboardButton('Получить дз'), KeyboardButton('Отправить дз')],
                     [KeyboardButton('Инструктаж'), KeyboardButton('Сменить класс')]]
markup_menu = ReplyKeyboardMarkup(keyboard_for_menu)

stop_button = [['/stop']]
markup_stop = ReplyKeyboardMarkup(stop_button)

# database connection
connection = sqlite3.connect("homework_database.sqlite")
cursor = connection.cursor()


async def text_answer(updater, context):
    if updater.message.text == 'Сменить класс':
        await updater.message.reply_text('Чтобы сменить класс напиши цифру класса и букву класса без пробелов',
                                         reply_markup=markup_stop)
        return 1
    else:
        await updater.message.reply_text('Запрос не принят')


async def start(updater, context):
    # Adding new users to client's database
    try:
        chat_id = updater.message.chat.id
        first_name = updater.message.chat.first_name
        username = updater.message.chat.username
        if updater.message.chat.id not in list(map(lambda x: x[0], cursor.execute('''SELECT telegram_id FROM users''').fetchall())):
            cursor.execute('''INSERT INTO users(name, telegram_id, username) VALUES(?, ?, ?)''',
                           (first_name, chat_id, username))
            connection.commit()
            await updater.message.reply_text(f'Привет {first_name}! Я телеграм-бот, работающий на ГБОУ'
                                             f' УР Лицей №41, предназначен для помощи лицеистам получать домашнее задание')
            await updater.message.reply_text(f'Чтобы было проще сразу скажи в каком классе ты учишься, напиши цифру класса '
                                             f'и букву без пробелов', reply_markup=markup_stop)
            return 1
        else:
            await updater.message.reply_text(f'Привет {first_name}, похоже ты у нас уже был, если ты забыл как '
                                             f'работать со мной то просто вызови инструкцию', reply_markup=markup_menu)
    except Exception as e:
        await error(updater, context, e)


async def class_asking(updater, context):
    # Getting class of user and rewrite if needed
    try:
        user_class = updater.message.text
        if user_class[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'] and user_class[1] in 'абвм':
            cursor.execute('''UPDATE users SET (class, letter_of_class) = (?, ?) WHERE telegram_id = ?''',
                           (user_class[0], user_class[1].lower(), updater.message.chat.id))
            connection.commit()
            await updater.message.reply_text('Отлично', reply_markup=markup_menu)
            return ConversationHandler.END
        else:
            await updater.message.reply_text('Некорректный ввод, попробуйте ещё раз, цифру, букву, без пробелов, '
                                             'в русской раскладке')
            return 1
    except Exception as e:
        await error(updater, context, e)


async def stop(updater, context):
    await updater.message.reply_text('OK', reply_markup=markup_menu)
    return ConversationHandler.END


async def error(updater, context, mistake):
    await updater.message.reply_text('Извините, произошла ошибка')
    print(mistake)


async def thanking(updater, context):
    await updater.message.reply_text('Спасибо')
    return ConversationHandler.END


def initialization():
    # Making an application of Telegram-bot
    application = Application.builder().token(BOT_TOKEN).build()

    # A handler for asking user about his class
    entry_or_change_class_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(filters.TEXT & ~filters.COMMAND, text_answer)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, class_asking)]},
        fallbacks=[CommandHandler('stop', stop)]
    )

    # A handler for text messages out dialogs
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, text_answer)

    # Registration of handlers
    application.add_handler(entry_or_change_class_handler)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    initialization()
