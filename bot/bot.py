import telebot
import json

from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from bot_key import bot_key
from send import send

bot = telebot.TeleBot(bot_key)

with open('../db/settings.json') as file:
    settings = json.load(file)
id = settings["telegram"]["id"]


@bot.message_handler(commands=['start', 'help'])
def start_help_message(message):
    if str(message.chat.id) == id:
        text = "<b>Этот бот предназдначен для получения напоминаний о ваших задачах.</b>\nТак же через него можно работать " \
               "с задачами.\n\nДоступные команды:\n\n/help - выводит подсказку о возможностях бота\n\n/tasks - выводит все" \
               " задачи которые у вас есть"
        bot.send_message(message.chat.id, text, parse_mode="html")
    else:
        bot.send_message(message.chat.id, "Под не подключен", parse_mode="html")


@bot.message_handler(commands=['tasks'])
def send_tasks(message):
    with open('../db/tasks.json') as file:
        tasks = json.load(file)["tasks"]
    keys_list = list(tasks.keys())

    if str(message.chat.id) == id:
        count = len(keys_list)
        page = 1
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                   InlineKeyboardButton(text=f'Вперёд --->',
                                        callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                            page + 1) + ",\"CountPage\":" + str(count) + "}"))

        key = keys_list[0]
        task = tasks[key]

        time_1, time_2 = tuple(key.split(";"))
        time_2 = time_2.replace(":", ".")
        time_1 = ":".join(time_1.split(":")[:0:-1])
        time = " / ".join([time_1, time_2])

        text = f"<b>{task[0]}</b>\n\n{task[1]}\n\n{time}\n<em>{'Завершено' if task[2] else 'Не завершено'}</em>"

        bot.send_message(message.chat.id, text, parse_mode="html", reply_markup=markup)

    else:
        bot.send_message(message.chat.id, "Под не подключен", parse_mode="html")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    req = call.data.split('_')

    if 'pagination' in req[0]:
        json_string = json.loads(req[0])
        count = json_string['CountPage']
        page = json_string['NumberPage']

        with open('../db/tasks.json') as file:
            tasks = json.load(file)["tasks"]
        keys_list = list(tasks.keys())

        key = keys_list[page - 1]
        task = tasks[key]

        markup = InlineKeyboardMarkup()
        if page == 1:
            markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       InlineKeyboardButton(text=f'Вперёд --->',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page + 1) + ",\"CountPage\":" + str(count) + "}"))

        elif page == count:
            markup.add(InlineKeyboardButton(text=f'<--- Назад',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page - 1) + ",\"CountPage\":" + str(count) + "}"),
                       InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))

        else:
            markup.add(InlineKeyboardButton(text=f'<--- Назад',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page - 1) + ",\"CountPage\":" + str(count) + "}"),
                       InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       InlineKeyboardButton(text=f'Вперёд --->',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page + 1) + ",\"CountPage\":" + str(count) + "}"))

        time_1, time_2 = tuple(key.split(";"))
        time_2 = time_2.replace(":", ".")
        time_1 = ":".join(time_1.split(":")[:0:-1])
        time = " / ".join([time_1, time_2])

        text = f"<b>{task[0]}</b>\n\n{task[1]}\n\n{time}\n<em>{'Завершено' if task[2] else 'Не завершено'}</em>"

        bot.edit_message_text(text, reply_markup=markup, chat_id=call.message.chat.id,
                              message_id=call.message.message_id, parse_mode="html")


bot.polling()
