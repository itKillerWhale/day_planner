import sys
import json
import datetime

import qtmodern.styles
import qtmodern.windows

import qdarkstyle

from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt, QTime, QDate, QDateTime
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QGroupBox, QVBoxLayout, QCheckBox, QWidget, \
    QGridLayout, QDialog


class GroupBox(QGroupBox):
    clicked = QtCore.pyqtSignal(str, object)

    def __init__(self, title):
        super(GroupBox, self).__init__()
        self.title = title
        self.setTitle(self.title)

    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        if not child:
            child = self
        self.clicked.emit(self.title, child)


class CustomDialog(QDialog):
    def __init__(self, key, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/CustomDialog.ui', self)
        self.setWindowTitle("Задача")

        self.key = key

        self.btn_ok.clicked.connect(self.save)
        self.btn_cancel.clicked.connect(self.close_window)
        self.checkBox_do_prompts.stateChanged.connect(self.update_prompts_widget)
        self.comboBox_choice.activated.connect(self.update_prompts_widget)
        self.comboBox.activated.connect(self.important_function)

        if bool(self.key):
            with open('tasks.json') as file:
                data = json.load(file)
            task = data["tasks"][self.key]
            prompt = data["prompts"]

            self.lineEdit_header_text.setText(task[0])
            self.textEdit_text.setText(task[1])
            self.checkBox_completed.setChecked(task[2])

            time_1, time_2 = tuple(self.key.split(";"))
            time_1 = ":".join(time_1.split(":")[::-1])

            self.label_date.setText(" ".join([time_2, time_1]))

            self.checkBox_do_prompts.setChecked(prompt["date"][self.key][2] or prompt["every"][self.key][3])

            if prompt["date"][self.key][2]:
                date_list = list(map(int, prompt["date"][self.key][1].split(':')[::-1]))
                self.calendarWidget.setSelectedDate(QDate(date_list[0], date_list[1], date_list[2]))

                time_list = list(map(int, prompt["date"][self.key][0].split(":")))
                self.timeEdit.setTime(QTime(time_list[1], time_list[0]))

                self.tabWidget.setTabEnabled(0, True)

            if prompt["every"][self.key][3]:
                self.comboBox.setCurrentText(prompt["every"][self.key][2])
                self.important_function()

                self.spinBox.setValue(prompt["every"][self.key][1])

                time_list = list(map(int, prompt["every"][self.key][0].split(":")))
                self.timeEdit_2.setTime(QTime(time_list[1], time_list[0]))

                self.tabWidget.setTabEnabled(1, True)

            if self.tab.isEnabled() and self.tab_2.isEnabled():
                self.comboBox_choice.setCurrentIndex(2)

            elif self.tab.isEnabled():
                self.comboBox_choice.setCurrentIndex(1)

            elif self.tab_2.isEnabled():
                self.comboBox_choice.setCurrentIndex(0)







        else:
            self.label_date.setText("")
            self.timeEdit.setTime(QTime.currentTime().addSecs(600))

        self.update_prompts_widget()

    def save(self):
        with open('tasks.json') as file:
            dictionary = json.load(file)

        if bool(self.key):
            if bool(self.lineEdit_header_text.text()):
                dictionary["tasks"][self.key][0] = self.lineEdit_header_text.text()
                dictionary["tasks"][self.key][1] = self.textEdit_text.toPlainText()
                dictionary["tasks"][self.key][2] = self.checkBox_completed.isChecked()

        else:
            date, time = str(datetime.datetime.now()).split()
            time = ":".join(list(map(lambda x: str(round(float(x))).rjust(2, "0"), time.split(":")[::-1])))
            date = ":".join(date.split("-")[::-1])
            self.key = f"{time};{date}"

            dictionary["tasks"][self.key] = [self.lineEdit_header_text.text(), self.textEdit_text.toPlainText(),
                                             self.checkBox_completed.isChecked()]

        # if self.checkBox_do_prompts.isChecked():
        selected_date = self.calendarWidget.selectedDate()
        date_string = selected_date.toString("dd:MM:yyyy")

        time = self.timeEdit.time()
        time_string = time.toString("mm:hh")

        time_2 = self.timeEdit_2.time()
        time_string_2 = time_2.toString("mm:hh")

        dictionary["prompts"]["date"][self.key] = [time_string, date_string, self.tab.isEnabled()]
        dictionary["prompts"]["every"][self.key] = [time_string_2, self.spinBox.value(), self.comboBox.currentText(),
                                                    self.tab_2.isEnabled()]

        with open('tasks.json', 'w') as file:
            json.dump(dictionary, file)

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

    def important_function(self):
        if self.comboBox.currentIndex() < 2:
            self.label_6.setText("C")
        else:
            self.label_6.setText("В")

    def close_window(self):
        self.close()


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/MainWindow.ui', self)
        self.setWindowTitle("Планировщик задач на день")

        self.comboBox_sort.activated.connect(self.update_tasks)
        self.cb_reverse_sort.stateChanged.connect(self.update_tasks)
        self.cb_show_completed_task.stateChanged.connect(self.update_tasks)
        self.lineEdit_find.textChanged.connect(self.update_tasks)

        self.btn_clear_find.clicked.connect(self.clear_find_text)
        self.btn_do_all_completed_task.clicked.connect(self.do_all_tasks_complited)
        self.btn_new_task.clicked.connect(self.new_task)
        self.btn_del_all_completed_task.clicked.connect(self.delite_all_complited_tasks)

        self.vbox = QVBoxLayout()

        self.update_tasks()

    def update_tasks(self):
        with open('tasks.json') as file:
            data = json.load(file)
        tasks = data["tasks"]
        tasks_key_list = tasks.keys()

        # Филтр
        if not self.cb_show_completed_task.isChecked():
            tasks_key_list = list(filter(lambda x: not tasks[x][2], tasks_key_list))

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
            Group.setFixedHeight(100)
            Group.setFixedWidth(330)
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

    def onGroupClick(self, title, obj):
        group = self.scrollArea.findChild(QGroupBox, title)

        key = group.findChild(QLabel, "Item4").text()
        key_2, key_1 = key.split()
        key_1 = ":".join(key_1.split(":")[::-1])
        key = f"{key_1};{key_2}"

        dlg = CustomDialog(key, parent=self)
        mw = qtmodern.windows.ModernWindow(dlg)
        mw.move(200, 200)
        mw.show()

        dlg.exec()
        self.update_tasks()

    def clear_find_text(self):
        self.lineEdit_find.setText("")

    def change_completed(self):
        cb = self.sender()
        group = cb.parent()
        time = group.findChild(QLabel, "Item4").text()
        time_2, time_1 = time.split()
        time_1 = ":".join(time_1.split(":")[::-1])
        time = f"{time_1};{time_2}"

        with open('tasks.json') as file:
            dictionary = json.load(file)

        dictionary["tasks"][time][2] = cb.isChecked()

        with open('tasks.json', 'w') as file:
            json.dump(dictionary, file)

        if cb.isChecked():
            group.setStyleSheet(
                "QGroupBox{ background-color: #696969; border: 2px soild gray; border-radius: 3px; magrin-top: 10px}")

        else:
            group.setStyleSheet(
                "QGroupBox{border: 2px solid #A5A5A5; border-radius: 3px; magrin-top: 10px}")

    def do_all_tasks_complited(self):
        with open('tasks.json') as file:
            dictionary = json.load(file)

        for key in dictionary["tasks"].keys():
            dictionary["tasks"][key][2] = True

        with open('tasks.json', 'w') as file:
            json.dump(dictionary, file)

        self.update_tasks()

    def delite_all_complited_tasks(self):
        with open('tasks.json') as file:
            dictionary = json.load(file)

        tasks = dictionary["tasks"]
        tasks_copy = tasks.copy()
        for key in tasks_copy:
            if tasks[key][2]:
                del tasks[key]

        dictionary["tasks"] = tasks

        with open('tasks.json', 'w') as file:
            json.dump(dictionary, file)

        self.update_tasks()

    def new_task(self):
        dlg = CustomDialog("", parent=self)
        mw = qtmodern.windows.ModernWindow(dlg)
        mw.move(200, 200)
        mw.show()

        dlg.exec()
        self.update_tasks()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()

    qtmodern.styles.dark(app)
    mw = qtmodern.windows.ModernWindow(ex)
    mw.move(200, 200)

    mw.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
