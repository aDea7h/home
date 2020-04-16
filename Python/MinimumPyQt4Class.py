import sys
from PyQt4 import QtGui


class UI(QtGui.QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('TITLE')
        self.statusBar().showMessage('Ready')

        self.centralWidget = QtGui.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QtGui.QVBoxLayout()
        self.centralWidget.setLayout(self.layout)

        button1 = QtGui.QPushButton('test')
        self.layout.addWidget(button1)

        self.show()

def main():
    app = QtGui.QApplication(sys.argv)
    ui = UI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()