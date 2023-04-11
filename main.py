import sys
import json
import datetime
import random

import qtmodern.styles
import qtmodern.windows

from bot.bot_key import bot_key

from PyQt5 import uic, QtCore
from PyQt5.QtCore import QTime, QDate, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGroupBox, QVBoxLayout, QCheckBox, QWidget, \
    QGridLayout, QDialog, QInputDialog, QSizeGrip


class GroupBox(QGroupBox):
    clicked = QtCore.pyqtSignal(str, object)

    def __init__(self, title):
        super(GroupBox, self).__init__()
        self.title = title

    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        if not child:
            child = self
        self.clicked.emit(self.title, child)


class Connect(QDialog):
    key = ""

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/Connect_bot.ui', self)
        self.setWindowTitle("Соеденение")

        self.exit_ifo = ""

        self.btn_ok.clicked.connect(self.close_window)
        self.btn_cancel.clicked.connect(self.close_window)

        with open('db/settings.json') as file:
            data = json.load(file)

        if bool(data["telegram"]["id"]):
            self.label.setText("Подключено")

        self.list_for_choice = ["QW", "fS", "CXC", "ITU", "SAD", "gTS", "TUi", "BMr", "RLee"]

        self.generate_key()

    def generate_key(self):
        Connect.key = f"I{random.randint(0, 100)}{random.choice(self.list_for_choice)}{random.randint(0, 100)}GO"
        self.lineEdit_key.setText(Connect.key)

    def close_window(self):
        self.exit_ifo = self.sender().text()
        self.close()


class Settings(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/Settings.ui', self)
        self.setWindowTitle("Настройки")

        self.btn_ok.clicked.connect(self.save)
        self.btn_cancel.clicked.connect(self.close_window)
        self.btn_connect_bot.clicked.connect(self.connect_bot)

        with open('db/settings.json') as file:
            data = json.load(file)

        self.comboBox_theme.setCurrentText(data["theme"])
        self.checkBox_send.setChecked(data["telegram"]["send"])
        self.label_send_2.setText(
            "Бот подключён" if bool(data["telegram"]["id"]) else "(Для получения напоминаний подключите бота)")


    def save(self):
        with open('db/settings.json') as file:
            data = json.load(file)

        data["theme"] = self.comboBox_theme.currentText()
        data["telegram"]["send"] = self.checkBox_send.isChecked()

        with open('db/settings.json', 'w') as file:
            json.dump(data, file)

        theme = data["theme"] == "dark"

        if theme:
            qtmodern.styles.dark(app)

        else:
            qtmodern.styles.light(app)

        self.close_window()

    def close_window(self):
        self.close()

    def connect_bot(self):
        con = Connect(parent=self)
        mw = qtmodern.windows.ModernWindow(con)
        mw.move(200, 200)
        mw.show()

        con.exec()

        if con.exit_ifo == "Готово":
            bot.polling()


class Task(QDialog):
    def __init__(self, key, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/Task.ui', self)
        self.setWindowTitle("Задача")

        self.key = key

        self.btn_ok.clicked.connect(self.save)
        self.btn_cancel.clicked.connect(self.close_window)
        self.btn_del.clicked.connect(self.delite_task)

        self.checkBox_do_prompts.stateChanged.connect(self.update_prompts_widget)
        self.comboBox_choice.activated.connect(self.update_prompts_widget)
        self.comboBox.activated.connect(self.important_function)
        self.comboBox.activated.connect(self.update_groupbox)

        if bool(self.key):
            with open('db/tasks.json') as file:
                data = json.load(file)
            task = data["tasks"][self.key]
            prompt = data["prompts"]

            self.lineEdit_header_text.setText(task[0])
            self.textEdit_text.setText(task[1])
            self.checkBox_completed.setChecked(task[2])

            time_1, time_2 = tuple(self.key.split(";"))
            time_2 = time_2.replace(":", ".")
            time_1 = ":".join(time_1.split(":")[::-1])

            self.label_date.setText(" ".join([time_2, time_1]))

            self.checkBox_do_prompts.setChecked(prompt["date"][self.key][2] or prompt["every"][self.key][3])

            # Первый tab
            date_list = list(map(int, prompt["date"][self.key][1].split(':')[::-1]))
            self.calendarWidget.setSelectedDate(QDate(date_list[0], date_list[1], date_list[2]))

            time_list = list(map(int, prompt["date"][self.key][0].split(":")))
            self.timeEdit.setTime(QTime(time_list[1], time_list[0]))

            self.tabWidget.setTabEnabled(0, True)

            # Второй tab
            self.comboBox.setCurrentText(prompt["every"][self.key][2])
            self.important_function()

            self.spinBox.setValue(prompt["every"][self.key][1])

            time_list = list(map(int, prompt["every"][self.key][0].split(":")))
            self.timeEdit_2.setTime(QTime(time_list[1], time_list[0]))

            self.tabWidget.setTabEnabled(1, True)

            checked_list = prompt["every"][self.key][5]
            self.checkBox.setChecked(True if checked_list[0] == 0 else False)
            self.checkBox_2.setChecked(bool(checked_list[1]))
            self.checkBox_3.setChecked(bool(checked_list[2]))
            self.checkBox_4.setChecked(bool(checked_list[3]))
            self.checkBox_5.setChecked(bool(checked_list[4]))
            self.checkBox_6.setChecked(bool(checked_list[5]))
            self.checkBox_7.setChecked(bool(checked_list[6]))

            if prompt["date"][self.key][2] and prompt["every"][self.key][3]:
                self.comboBox_choice.setCurrentIndex(2)

            elif prompt["date"][self.key][2]:
                self.comboBox_choice.setCurrentIndex(1)

            elif prompt["every"][self.key][3]:
                self.comboBox_choice.setCurrentIndex(0)

        else:
            self.label_date.setText("")
            self.timeEdit.setTime(QTime.currentTime().addSecs(600))
            self.btn_del.hide()

        self.update_groupbox()
        self.update_prompts_widget()

    def save(self):
        with open('db/tasks.json') as file:
            data = json.load(file)

        if bool(self.key):
            if bool(self.lineEdit_header_text.text()):
                data["tasks"][self.key][0] = self.lineEdit_header_text.text()
                data["tasks"][self.key][1] = self.textEdit_text.toPlainText()
                data["tasks"][self.key][2] = self.checkBox_completed.isChecked()

        else:
            date, time = str(datetime.datetime.now()).split()
            time = ":".join(list(map(lambda x: str(round(float(x))).rjust(2, "0"), time.split(":")[::-1])))
            date = ":".join(date.split("-")[::-1])
            self.key = f"{time};{date}"

            data["tasks"][self.key] = [self.lineEdit_header_text.text(), self.textEdit_text.toPlainText(),
                                       self.checkBox_completed.isChecked()]

        # if self.checkBox_do_prompts.isChecked():
        selected_date = self.calendarWidget.selectedDate()
        date_string = selected_date.toString("dd:MM:yyyy")

        time = self.timeEdit.time()
        time_string = time.toString("mm:hh")

        time_2 = self.timeEdit_2.time()
        time_string_2 = time_2.toString("mm:hh")

        data["prompts"]["date"][self.key] = [time_string, date_string, self.tab.isEnabled()]
        data["prompts"]["every"][self.key] = [time_string_2, self.spinBox.value(), self.comboBox.currentText(),
                                              self.tab_2.isEnabled(), 1]

        data["prompts"]["every"][self.key].append([0 if self.checkBox.isChecked() else None,
                                                   1 if self.checkBox_2.isChecked() else None,
                                                   2 if self.checkBox_3.isChecked() else None,
                                                   3 if self.checkBox_4.isChecked() else None,
                                                   4 if self.checkBox_5.isChecked() else None,
                                                   5 if self.checkBox_6.isChecked() else None,
                                                   6 if self.checkBox_7.isChecked() else None])

        with open('db/tasks.json', 'w') as file:
            json.dump(data, file)

        self.close_window()

    def update_prompts_widget(self):
        self.tabWidget.setTabEnabled(0, True)
        self.tabWidget.setTabEnabled(1, True)

        if self.checkBox_do_prompts.isChecked():
            self.tabWidget.setEnabled(True)
            self.comboBox_choice.show()

            self.tabWidget.setTabEnabled(self.comboBox_choice.currentIndex(), False)

        else:
            self.tabWidget.setEnabled(False)

            self.tabWidget.setTabEnabled(0, False)
            self.tabWidget.setTabEnabled(1, False)

            self.comboBox_choice.hide()

    def delite_task(self):
        n = random.randint(1000, 9999)
        input_dialog = QInputDialog()
        name, ok_pressed = input_dialog.getText(self, "Подтверждение",
                                                f"Вы точно хотите удалить эту задачу?\nДля подтверждения введите {n}")
        if ok_pressed and name == str(n):
            with open('db/tasks.json') as file:
                data = json.load(file)

            del data["tasks"][self.key]
            del data["prompts"]["date"][self.key]
            del data["prompts"]["every"][self.key]

            with open('db/tasks.json', 'w') as file:
                json.dump(data, file)

            self.close_window()

    def update_groupbox(self):
        if self.comboBox.currentText() == "Недель":
            self.groupBox.setEnabled(True)
        else:
            self.groupBox.setEnabled(False)

    def important_function(self):
        if self.comboBox.currentIndex() < 2:
            self.label_6.setText("C")
        else:
            self.label_6.setText("В")

    def close_window(self):
        self.close()


class MainWindow(QMainWindow):
    old_data = {}

    def __init__(self):
        super().__init__()
        uic.loadUi('ui/MainWindow.ui', self)
        self.setWindowTitle("Планировщик задач на день")
        QSizeGrip(self.size_grip)

        self.comboBox_sort.activated.connect(self.update_tasks)
        self.cb_reverse_sort.stateChanged.connect(self.update_tasks)
        # self.cb_show_completed_task.stateChanged.connect(self.update_tasks)
        self.lineEdit_find.textChanged.connect(self.update_tasks)

        self.btn_new_task.clicked.connect(self.new_task)
        self.btn_del_all_completed_task.clicked.connect(self.delite_all_complited_tasks)
        self.btn_settings.clicked.connect(self.open_settings)

        self.menu_animation = QPropertyAnimation(self.right_menu, b'maximumWidth')
        self.menu_animation.setDuration(350)
        self.menu_animation.setEasingCurve(QEasingCurve.InOutCubic)

        self.menu_btn.clicked.connect(self.slide_menu)
        self.menu_visible = False
        self.delete_borders()

        self.vbox = QVBoxLayout()

        self.update_tasks()

    def update_tasks(self):
        with open('db/tasks.json') as file:
            data = json.load(file)
        tasks = data["tasks"]
        tasks_key_list = tasks.keys()

        # Филтр
        # if not self.cb_show_completed_task.isChecked():
        #     tasks_key_list = list(filter(lambda x: not tasks[x][2], tasks_key_list))

        # Поиск
        search_text = self.lineEdit_find.text().lower()
        if bool(search_text):
            tasks_key_list = list(
                filter(lambda x: search_text in tasks[x][0].lower() or search_text in tasks[x][1].lower(),
                       tasks_key_list))

        # Сортировка
        comboBox_text = self.comboBox_sort.currentText()
        do_revers = self.cb_reverse_sort.isChecked()

        if comboBox_text == "Дате создания":
            tasks_key_list = sorted(tasks_key_list, key=lambda x: x[::-1], reverse=not do_revers)

        elif comboBox_text == "Дате напоминания":
            pass

        elif comboBox_text == "Заголовку":
            tasks_key_list = sorted(tasks_key_list, key=lambda x: tasks[x][0].lower(), reverse=do_revers)

        else:
            tasks_key_list = sorted(tasks_key_list, key=lambda x: tasks[x][1].lower(), reverse=do_revers)

        # Добавление задач в ScrollArea
        scrollLayout = QVBoxLayout()

        scrollW = QWidget()
        self.scrollArea.setWidget(scrollW)

        scrollW.setLayout(scrollLayout)
        scrollLayout.setAlignment(QtCore.Qt.AlignTop)

        k = 0
        for key in tasks_key_list:
            k += 1
            Group = GroupBox(f'Задача {k}')

            if tasks[key][2]:
                Group.setStyleSheet(
                    "QGroupBox{ background-color: #696969; border: 2px soild gray; border-radius: 3px; magrin-top: 10px}")
            else:
                Group.setStyleSheet(
                    "QGroupBox{border: 2px solid #A5A5A5; border-radius: 3px; magrin-top: 10px}")
            Group.setObjectName(f'Задача {k}')
            Group.clicked.connect(self.onGroupClick)
            Group.setFixedHeight(120)
            Layout = QGridLayout()
            Group.setLayout(Layout)

            Item1_text = tasks[key][0].replace("\n", " ")
            if len(Item1_text) > 18:
                Item1_text = Item1_text[:18] + "..."
            Item1 = QLabel(Item1_text, objectName="Item1")
            Item1.setFixedHeight(21)
            Item1.setFont(QFont("MS Shell Dlg 2", 11, QFont.Bold))

            Item2_text = tasks[key][1].replace("\n", " ")
            if len(Item2_text) > 28:
                Item2_text = Item2_text[:28] + "..."
            Item2 = QLabel(Item2_text, objectName="Item2")
            Item2.setFixedHeight(21)
            Item2.setFont(QFont("MS Shell Dlg 2", 8))

            Item3 = QCheckBox("Завершено", objectName="Item3")
            Item3.setFixedHeight(21)
            Item3.setFont(QFont("MS Shell Dlg 2", 8))
            Item3.setChecked(tasks[key][2])
            Item3.stateChanged.connect(self.change_completed)

            time_1, time_2 = tuple(key.split(";"))
            time_1 = ":".join(time_1.split(":")[::-1])
            Item4 = QLabel(" ".join([time_2, time_1]), objectName="Item4")
            Item4.setFixedHeight(21)
            Item4.setFixedWidth(110)
            Item4.setFont(QFont("MS Shell Dlg 2", 8))

            Layout.addWidget(Item1, 0, 0)
            Layout.addWidget(Item2, 1, 0)
            Layout.addWidget(Item3, 2, 0)
            Layout.addWidget(Item4, 2, 1)

            scrollLayout.addWidget(Group)

    def delete_borders(self):
        self.size_grip.setStyleSheet('border: none;')
        self.frame_3.setStyleSheet('QFrame{border: none;}')

    def onGroupClick(self, title, obj):
        group = self.scrollArea.findChild(QGroupBox, title)

        key = group.findChild(QLabel, "Item4").text()
        key_2, key_1 = key.split()
        key_1 = ":".join(key_1.split(":")[::-1])
        key = f"{key_1};{key_2}"

        dlg = Task(key, parent=self)
        mw = qtmodern.windows.ModernWindow(dlg)
        mw.move(200, 200)
        mw.show()

        dlg.exec()
        self.update_tasks()

    def change_completed(self):
        cb = self.sender()
        group = cb.parent()
        time = group.findChild(QLabel, "Item4").text()
        time_2, time_1 = time.split()
        time_1 = ":".join(time_1.split(":")[::-1])
        time = f"{time_1};{time_2}"

        with open('db/tasks.json') as file:
            data = json.load(file)

        data["tasks"][time][2] = cb.isChecked()

        with open('db/tasks.json', 'w') as file:
            json.dump(data, file)

        if cb.isChecked():
            group.setStyleSheet(
                "QGroupBox{ background-color: #696969; border: 2px soild gray; border-radius: 3px; magrin-top: 10px}")

        else:
            group.setStyleSheet(
                "QGroupBox{border: 2px solid #A5A5A5; border-radius: 3px; magrin-top: 10px}")

    def slide_menu(self):
        if self.menu_visible:
            self.menu_animation.setStartValue(250)
            self.menu_animation.setEndValue(40)
            self.menu_animation.start()
            self.menu_visible = False
        else:
            self.menu_animation.setStartValue(40)
            self.menu_animation.setEndValue(250)
            self.menu_animation.start()
            self.menu_visible = True

    def delite_all_complited_tasks(self):
        n = random.randint(1000, 9999)
        input_dialog = QInputDialog()
        name, ok_pressed = input_dialog.getText(self, "Подтверждение",
                                                f"Вы точно хотите удалить все завершённe задачи?\nДля подтверждения введите {n}")
        if ok_pressed and name == str(n):

            with open('db/tasks.json') as file:
                data = json.load(file)

            prompts = data["prompts"]
            tasks = data["tasks"]
            tasks_copy = tasks.copy()
            for key in tasks_copy:
                if tasks[key][2]:
                    del tasks[key]
                    del prompts["date"][key]
                    del prompts["every"][key]

            data["tasks"] = tasks
            data["prompts"] = prompts

            with open('db/tasks.json', 'w') as file:
                json.dump(data, file)

            self.update_tasks()

    def new_task(self):
        dlg = Task("", parent=self)
        mw = qtmodern.windows.ModernWindow(dlg)
        mw.move(200, 200)
        mw.show()

        dlg.exec()
        self.update_tasks()

    def open_settings(self):

        sett = Settings(parent=self)
        mw = qtmodern.windows.ModernWindow(sett)
        mw.move(200, 200)
        mw.show()

        sett.exec()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    with open('db/settings.json') as file:
        data = json.load(file)

    # bot = telebot.TeleBot(bot_key)
    #
    #
    # @bot.message_handler(content_types=["text"])
    # def get_message(message):
    #     if message.text == Connect.key:
    #         with open('db/settings.json') as file:
    #             data = json.load(file)
    #
    #         data["telegram"]["id"] = f"{message.chat.id}"
    #
    #         with open('db/settings.json', 'w') as file:
    #             json.dump(data, file)
    #
    #     try:
    #         bot.stop_polling()
    #     except Exception:
    #         pass


    app = QApplication(sys.argv)
    ex = MainWindow()

    theme = data["theme"] == "dark"

    if theme:
        qtmodern.styles.dark(app)

    else:
        qtmodern.styles.light(app)

    mw = qtmodern.windows.ModernWindow(ex)
    mw.move(200, 200)

    mw.show()
    sys.excepthook = except_hook
    app.exec_()
