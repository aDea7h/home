import sys
import os
from PySide import QtCore, QtGui, QtUiTools

backup = 0
prod = False

class ExportFileUi(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(ExportFileUi, self).__init__(parent)


class ExportFile:
    def __init__(self, export_path):
        assert os.path.isdir(export_path)
        self.export_path = export_path
        print(self.export_path)
        self.ui = ExportFileUi()
        self.ui.show()



class AccountManager(QtGui.QMainWindow):
    def __init__(self, scriptDirectory, uiFileName, parent=None):
        super(AccountManager, self).__init__(parent)
        loader = QtUiTools.QUiLoader()

        # get Ui File and setup Ui:
        uifile = QtCore.QFile("/".join([scriptDirectory, uiFileName]))
        uifile.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(uifile, parent)
        uifile.close()

        #connect ui to events:
        self.connectUiEvents()

    def browseFiles(self):
        print("browsing files")
        return(True)

    def connectUiEvents(self):
        self.ui.Browse_Btn.clicked.connect(self.browseFiles)

if __name__ == "__main__":
    if prod == True:
        scriptDirectory = os.path.dirname(os.path.abspath(__file__))
    else:
        scriptDirectory = os.path.dirname(r"F:\tmp\eclipseTest\pipe\src/")
    print(scriptDirectory)
    uiFileName = "comptes.ui"
    print(sys.argv[0].split("\\")[-1])
    if sys.argv[0].split("\\")[-1] == "maya.exe":
        MainWindow = AccountManager(scriptDirectory, uiFileName)
        MainWindow.ui.show()
    else:
        app = QtGui.QApplication(sys.argv)
        MainWindow = AccountManager(scriptDirectory, uiFileName)
        MainWindow.ui.show()
        sys.exit(app.exec_())

