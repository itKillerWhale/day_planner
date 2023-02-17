import sys
import json

from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
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

        self.vbox = QVBoxLayout()

        self.update_tasks()

    def update_tasks(self):
        with open('tasks.json') as file:
            data = json.load(file)
        tsaks = data["tasks"]

        # Сортировка


        scrollLayout = QVBoxLayout()

        scrollW = QWidget()
        self.scrollArea.setWidget(scrollW)

        scrollW.setLayout(scrollLayout)
        scrollLayout.setAlignment(QtCore.Qt.AlignTop)

        k = 0
        for key in tsaks.keys():
            k += 1
            Group = GroupBox(f'Задача {k}')

            Group.setObjectName(f'task {k}')
            Group.clicked.connect(self.onGroupClick)
            Group.setFixedHeight(100)
            Group.setFixedWidth(330)
            Layout = QGridLayout()
            Group.setLayout(Layout)

            Item1_text = tsaks[key][0] + "_" + " ".join(key.split(";"))
            Item1 = QLabel(Item1_text, objectName="Item1")
            Item1.setFixedHeight(21)
            Item1.setFont(QFont("MS Shell Dlg 2", 11, QFont.Bold))

            Item2 = QLabel(tsaks[key][1], objectName="Item2")
            Item2.setFixedHeight(21)
            Item2.setFont(QFont("MS Shell Dlg 2", 8))

            Item3 = QCheckBox("Завершено", objectName="Item3")
            Item3.setFixedHeight(21)
            Item3.setFont(QFont("MS Shell Dlg 2", 8))

            Item4 = QLabel("asd", objectName="Item4")
            Item4.setFixedHeight(21)
            Item4.setFont(QFont("MS Shell Dlg 2", 8))

            Layout.addWidget(Item1, 0, 0)
            Layout.addWidget(Item2, 1, 0)
            Layout.addWidget(Item3, 2, 0)
            Layout.addWidget(Item4, 2, 1)
            scrollLayout.addWidget(Group)

    def onGroupClick(self, title, obj):
        print(f"Group: {title}; objectName=`{obj.objectName()}`")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())

# 36
