import sys
import json

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QGroupBox, QVBoxLayout


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

        with open('tasks.json') as file:
            data = json.load(file)
        tsaks = data["tasks"]

        k = 0
        for key in tsaks.keys():
            k += 1
            Group = GroupBox(f'Задача {k}')
            Group.setObjectName(f'task {k}')
            Group.clicked.connect(self.onGroupClick)
            Group.setFixedHeight(65)
            Layout = QVBoxLayout()
            Group.setLayout(Layout)

            Item1 = QLabel(tsaks[key][0], objectName="Item1")
            Item1.setFixedHeight(21)

            Item2 = QLabel(tsaks[key][1], objectName="Item2")
            Item2.setFixedHeight(21)

            Item3 = QLabel(tsaks[key][2], objectName="Item3")
            Item3.setFixedHeight(21)

            Layout.addWidget(Item1)
            Layout.addWidget(Item2)
            Layout.addWidget(Item3)
            self.vbox.addWidget(Group)

        self.scrollArea.setLayout(self.vbox)

    def onGroupClick(self, title, obj):
        print(f"Group: {title}; objectName=`{obj.objectName()}`")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
