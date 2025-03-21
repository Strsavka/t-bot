import logging
import json
import sqlite3
import datetime as dt
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

data = []

markup_menu = ReplyKeyboardMarkup(keyboard_for_menu)

stop_button = [['/stop']]
markup_stop = ReplyKeyboardMarkup(stop_button)

# database connection
connection = sqlite3.connect("homework_database.sqlite")
cursor = connection.cursor()

# list_of_lessons
lessons = [[KeyboardButton('алгебра'), KeyboardButton('русский язык'), KeyboardButton('геометрия'),
           KeyboardButton('английский язык'), KeyboardButton('география'), KeyboardButton('биология'),
           KeyboardButton('литература'), KeyboardButton('физика'), KeyboardButton('химия'),
           KeyboardButton('вероятность и статистика'), KeyboardButton('история'), KeyboardButton('обществознание'),
           KeyboardButton('физическая культура'), KeyboardButton('труд'), KeyboardButton('информатика'),
           KeyboardButton('немецкий')]]

lessons_markup = ReplyKeyboardMarkup(lessons)


async def text_answer(updater, context):
    if updater.message.text == 'Сменить класс':
        await updater.message.reply_text('Чтобы сменить класс напиши цифру класса и букву класса без пробелов',
                                         reply_markup=markup_stop)
        return 1
    elif updater.message.text == 'Отправить дз':
        await updater.message.reply_text('Напишите на какое число вы бы хотели отправить дз', reply_markup=markup_stop)
        await updater.message.reply_text('Пишите через дату в формате ДД.ММ.ГГГГ')
        return 2
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
                                             f'и букву через пробел', reply_markup=markup_stop)
            return 1
        else:
            await updater.message.reply_text(f'Привет {first_name}, похоже ты у нас уже был, если ты забыл как '
                                             f'работать со мной то просто вызови инструкцию', reply_markup=markup_menu)
    except Exception as e:
        await error(updater, context, e)


async def class_asking(updater, context):
    # Getting class of user and rewrite if needed
    try:
        user_class = updater.message.text.split()
        if user_class[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'] and user_class[1] in 'абвм':
            cursor.execute('''UPDATE users SET (class, letter_of_class) = (?, ?) WHERE telegram_id = ?''',
                           (user_class[0], user_class[1].lower(), updater.message.chat.id))
            connection.commit()
            await updater.message.reply_text('Отлично', reply_markup=markup_menu)
            return ConversationHandler.END
        else:
            await updater.message.reply_text('Некорректный ввод, попробуйте ещё раз, цифру, букву, через пробел, '
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


async def asking_subject():
    try:
        pass
    except Exception as e:
        pass


async def getting_date(updater, context):
    try:
        string_date = updater.message.text.split('.')
        if len(string_date) != 3:
            raise Exception
        new_date = dt.date(string_date[2], string_date[1], string_date[0])
        await updater.message.reply_text('Отлично, теперь выберите урок на который запланировано дз', reply_markup=lessons_markup)
        await updater.message.reply_text('''СЮДА ВЫБОРКА УРОКОВ''')  # ДОДЕЛАТЬ!!!
        return 3
    except Exception as e:
        await updater.message.reply_text('Некорректная дата')
        await updater.message.reply_text('Попробуйте ещё раз')
        return 2


async def try_again():
    pass


def initialization():
    # opening json form
    global data
    with open('lessons.json') as lessons_file:
        data = json.load(lessons_file)

    # Making an application of Telegram-bot
    application = Application.builder().token(BOT_TOKEN).build()

    # A handler for asking user about his class
    entry_or_change_class_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(filters.TEXT & ~filters.COMMAND, text_answer)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, class_asking)]},
        fallbacks=[CommandHandler('stop', stop)]
    )

    aploading_hometask_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, text_answer)],
        states={2: [MessageHandler(filters.TEXT & ~filters.COMMAND, getting_date)],
                3: [MessageHandler(filters.TEXT & ~filters.COMMAND, asking_subject)]},
        fallbacks=[CommandHandler('stop', stop)]
    )

    # A handler for text messages out dialogs
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, text_answer)

    # Registration of handlers
    # ВНИМАНИЕ очень важен порядок: может съедать текстовый handler
    application.add_handler(entry_or_change_class_handler)
    application.add_handler(aploading_hometask_handler)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    initialization()
