import sys
from PySide2 import QtGui, QtCore, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('TITLE')
        self.statusBar().showMessage('Ready')

        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QtWidgets.QVBoxLayout()
        self.centralWidget.setLayout(self.layout)

        button1 = QtWidgets.QPushButton('test')
        self.layout.addWidget(button1)

        self.show()


def main(parent=None):
    # print(sys.argv[0])
    # app = QtWidgets.QApplication(sys.argv[0])
    ui = MainWindow(parent)
    return ui
    # ui.show()
    # sys.exit(app.exec_())


if __name__ == '__main__':
    main()
