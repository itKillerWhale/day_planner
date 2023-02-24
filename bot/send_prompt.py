import time
import datetime
import telebot
import json

from send import send

while True:
    with open('../db/settings.json') as file:
        settings = json.load(file)

    if settings["telegram"]["send"]:

        with open('../db/tasks.json') as file:
            tasks = json.load(file)

        date = tasks["prompts"]["date"]
        every = tasks["prompts"]["every"]

        for key in date.keys():
            if date[key][2]:
                prompt_time, prompt_date = date[key][0], date[key][1]

                now = datetime.datetime.now()
                now_date, now_time = now.strftime("%d:%m:%Y"), now.strftime("%M:%H")

                if now_date == prompt_date and now_time == prompt_time:
                    send(key)

            if every[key][3]:
                if every[key][2] == "Минут":
                    now = datetime.datetime.now()
                    prompt_time = every[key][0]
                    prompt_time_list = prompt_time.split(":")[::-1]
                    prompt_minute, prompt_hour = int(prompt_time_list[1]), int(prompt_time_list[0])

                    delta = (now.minute + now.hour * 60) - (prompt_minute + prompt_hour * 60)

                    if delta >= 0:
                        if delta % every[key][1] == 0:
                            send(key)


                elif every[key][2] == "Часов":
                    now = datetime.datetime.now()
                    prompt_time = every[key][0]
                    prompt_time_list = prompt_time.split(":")[::-1]
                    prompt_minute, prompt_hour = int(prompt_time_list[1]), int(prompt_time_list[0])

                    delta = (now.minute + now.hour * 60) - (prompt_minute + prompt_hour * 60)
                    if delta >= 0:
                        if delta % every[key][1] * 60 == 0 and prompt_minute == now.minute:
                            send(key)

                elif every[key][2] == "Дней":
                    now = datetime.datetime.now()
                    delta = int(now.strftime("%d")) - int(key.split(";")[1].split(":")[0]) % every[key][1]
                    if now.strftime("%M:%H") == every[key][0] and delta % every[key][1] == 0:
                        send(key)

                elif every[key][2] == "Недель":
                    now = datetime.datetime.now()
                    print(now.strftime("%M:%H") == every[key][0])
                    print(str(now.strftime("%w")), every[key][5])
                    if now.strftime("%M:%H") == every[key][0] and str(now.strftime("%w")) in list(
                            map(str, every[key][5])):
                        send(key)

                elif every[key][2] == "Месяцев":
                    now = datetime.datetime.now()
                    delta = int(now.strftime("%d")) - int(key.split(";")[1].split(":")[0])
                    delta_2 = int(now.strftime("%m")) - int(key.split(";")[1].split(":")[1]) % every[key][1]
                    if delta == 0 and now.strftime("%M:%H") == every[key][0] and delta_2 % every[key][1] == 0:
                        send(key)

                elif every[key][2] == "Лет":
                    now = datetime.datetime.now()
                    day_m = f"{key.split(';')[1].split(':')[0]}:{key.split(';')[1].split(':')[1]}"
                    delta = int(now.strftime("%Y")) - int(key.split(";")[1].split(":")[2]) % every[key][1]
                    if now.strftime("%M:%H") == every[key][0] and day_m == now.strftime("%d:%m") and now.strftime(
                            "%M:%H") == every[key][0] and delta % every[key][1] == 0:
                        send(key)

                elif every[key][2] == "Десятилетий":
                    now = datetime.datetime.now()
                    day_m = f"{key.split(';')[1].split(':')[0]}:{key.split(';')[1].split(':')[1]}"
                    delta = int(now.strftime("%Y")) - int(key.split(";")[1].split(":")[2]) % (every[key][1] * 10)
                    if now.strftime("%M:%H") == every[key][0] and day_m == now.strftime("%d:%m") and now.strftime(
                            "%M:%H") == every[key][0] and delta % (every[key][1] * 10) == 0:
                        send(key)

                elif every[key][2] == "Столетий":
                    now = datetime.datetime.now()
                    day_m = f"{key.split(';')[1].split(':')[0]}:{key.split(';')[1].split(':')[1]}"
                    delta = int(now.strftime("%Y")) - int(key.split(";")[1].split(":")[2]) % (every[key][1] * 100)
                    if now.strftime("%M:%H") == every[key][0] and day_m == now.strftime("%d:%m") and now.strftime(
                            "%M:%H") == every[key][0] and delta % (every[key][1] * 100) == 0:
                        send(key)

                elif every[key][2] == "Тысячелетий":
                    now = datetime.datetime.now()
                    day_m = f"{key.split(';')[1].split(':')[0]}:{key.split(';')[1].split(':')[1]}"
                    delta = int(now.strftime("%Y")) - int(key.split(";")[1].split(":")[2]) % (every[key][1] * 1000)
                    if now.strftime("%M:%H") == every[key][0] and day_m == now.strftime("%d:%m") and now.strftime(
                            "%M:%H") == every[key][0] and delta % (every[key][1] * 1000) == 0:
                        send(key)
    time.sleep(60)
