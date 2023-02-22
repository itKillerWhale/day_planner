import time
import json
import datetime
from datetime import timedelta

import telebot
import json

from bot.bot_key import bot_key

bot = telebot.TeleBot(bot_key)

def send(key):
    with open('db/settings.json') as file:
        settings = json.load(file)

    with open('db/tasks.json') as file:
        data = json.load(file)
    task = data["tasks"][key]

    time_1, time_2 = tuple(key.split(";"))
    time_2 = time_2.replace(":", ".")
    time_1 = ":".join(time_1.split(":")[:0:-1])
    time = " / ".join([time_1, time_2])

    text = f"<b>{task[0]}</b>\n\n{task[1]}\n\n{time}\n<em>{'Завершено' if task[2] else 'Не завершено'}</em>"

    bot.send_message(settings["telegram"]["id"], text, parse_mode="html")


while True:
    with open('db/settings.json') as file:
        settings = json.load(file)

    print(settings["telegram"]["send"])
    if settings["telegram"]["send"]:

        with open('db/tasks.json') as file:
            tasks = json.load(file)

        date = tasks["prompts"]["date"]
        every = tasks["prompts"]["every"]

        for key in date.keys():

            print(every[key][3], key)
            if date[key][2]:
                prompt_time, prompt_date = date[key][0], date[key][1]

                now = datetime.datetime.now()
                now_date, now_time = now.strftime("%d:%m:%Y"), now.strftime("%M:%H")

                if now_date == prompt_date and now_time == prompt_time:
                    send(key)

            if every[key][3]:
                if every[key][2] == "Минут":
                    now = datetime.datetime.now()
                    now_date, now_time = now.strftime("%d:%m:%Y"), now.strftime("%M:%H")

                    time_list = list(map(int, now_time.split(":")))
                    datetime_time = datetime.datetime(hour=time_list[1], minute=time_list[0], day=1, year=1, month=1)
                    hours_and_minuts = every[key][0].split(":")
                    hour, minut = hours_and_minuts[1], hours_and_minuts[0]
                    datetime_time = datetime_time + timedelta(minutes=int(every[key][1]) * int(every[key][4])) + timedelta(
                        minutes=int(minut), hours=int(hour))

                    print(now_time, datetime_time.strftime("%M:%H"))

                    if now_time == datetime_time.strftime("%M:%H"):
                        send(key)

    print("-----------------------------------------------------------------------------------------------------------")

    time.sleep(30)
