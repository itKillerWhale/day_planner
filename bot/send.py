import telebot
import json

from bot_key import bot_key
bot = telebot.TeleBot(bot_key)
def send(key):
    with open('../db/settings.json') as file:
        settings = json.load(file)

    with open('../db/tasks.json') as file:
        data = json.load(file)
    task = data["tasks"][key]

    time_1, time_2 = tuple(key.split(";"))
    time_2 = time_2.replace(":", ".")
    time_1 = ":".join(time_1.split(":")[:0:-1])
    time = " / ".join([time_1, time_2])

    text = f"<b>{task[0]}</b>\n\n{task[1]}\n\n{time}\n<em>{'Завершено' if task[2] else 'Не завершено'}</em>"

    bot.send_message(settings["telegram"]["id"], text, parse_mode="html")