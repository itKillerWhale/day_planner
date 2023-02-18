import sys
import json

from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QGroupBox, QVBoxLayout, QCheckBox, QWidget, \
    QGridLayout


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


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/MainWindow.ui', self)

        self.comboBox_sort.activated.connect(self.update_tasks)
        self.cb_reverse_sort.stateChanged.connect(self.update_tasks)
        self.cb_show_completed_task.stateChanged.connect(self.update_tasks)
        self.lineEdit_find.textChanged.connect(self.update_tasks)

        self.btn_clear_find.clicked.connect(self.clear_find_text)

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
                    "QGroupBox{ background-color: #A5A5A5; border: 2px soild gray; border-radius: 3px; magrin-top: 10px}")
            else:
                Group.setStyleSheet(
                    "QGroupBox{border: 2px solid #A5A5A5; border-radius: 3px; magrin-top: 10px}")
            Group.setObjectName(f'task {k}')
            Group.clicked.connect(self.onGroupClick)
            Group.setFixedHeight(100)
            Group.setFixedWidth(330)
            Layout = QGridLayout()
            Group.setLayout(Layout)

            Item1_text = tasks[key][0]
            Item1 = QLabel(Item1_text, objectName="Item1")
            Item1.setFixedHeight(21)
            Item1.setFont(QFont("MS Shell Dlg 2", 11, QFont.Bold))

            Item2 = QLabel(tasks[key][1], objectName="Item2")
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
            Item4.setFont(QFont("MS Shell Dlg 2", 8))

            Layout.addWidget(Item1, 0, 0)
            Layout.addWidget(Item2, 1, 0)
            Layout.addWidget(Item3, 2, 0)
            Layout.addWidget(Item4, 2, 1)

            scrollLayout.addWidget(Group)

    def onGroupClick(self, title, obj):
        print(f"Group: {title}; objectName=`{obj.objectName()}`")

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

        # print(dictionary["tasks"][time][2])
        dictionary["tasks"][time][2] = cb.isChecked()
        # print(dictionary["tasks"][time][2])

        with open('tasks.json', 'w') as file:
            json.dump(dictionary, file)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())

# 36
