from PyQt5 import QtGui, QtCore, QtWidgets
import sys

class UI(QtWidgets.QMainWindow):
    def __init___(self):
        super(UI, self).__init__()
        self.resize(300, 300)
        self.setWindowTitle('APP')
        self.centralWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.initUi()

    def initUi(self):
        return

def uiLaunch():
    app = QtWidgets.QApplication(sys.argv)
    ui = UI()
    ui.show()
    sys.exit(app.exec_())

uiLaunch()