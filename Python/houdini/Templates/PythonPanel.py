from PySide2 import QtGui, QtCore, QtWidgets


class PyPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PyPanel, self).__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        button1 = QtWidgets.QPushButton('bla')
        self.layout.addWidget(button1)

        # self.show()


def main(parent=None):
    ui = PyPanel(parent)
    return ui
