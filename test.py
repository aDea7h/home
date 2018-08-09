from tools import customPrint as customPrint
import sys
import os
import json
from pprint import pprint as pprint
'''
# store path as fullPath with constructor for custom drive / user / generated random folder...
backupDic = {"soft1":
{
    'name':'soft1',
    'doBackup':True,
    'folders':{'pathToFolder1':None, #backuping whole folder
               'pathToFolder2':['file1', 'file2'], #backuping selected files
               },
    'backupFolder':None, #None : backup in the same folder as specified in configDic, Else : override dest path
    'badObject':False, #set to True if object is not usable and needs to be omitted.
    'errors': [error1, error2] # lists all errors affecting object
}
}

configDic = {
    "createFolders": True,
    "sysRoot":'C:/',
    "user":'Doodoo',
    'windowsUserPath':'$ROOT/Users/$USER/Documents',
    "backupPath": None, #None : backup in the path of the file copied, Else : backup in specified folder
    "createBackupFolder":False, #if true create a "_backup" folder to store and stack backups
    "backupName":'$DATE.$TIME_$FILENAME_backup',
    "maxBackupNumber":None,
    "deleteOlderThan":None,
}

'''
# old functions
# ktop/configDic.cfg')
# class BackupedItem():
#     # needs cfg = {'user', 'sysRoot'}
#     def __init__(self, name, folders, cfg, doBackup=True, backupFolder=None, verbose=0):
#         self.verbose = verbose
#         self.folders = {}
#         self.badObject = False
#         self.errors = []
#
#         self.name = self.checkName(name)
#         self.doBackup = self.checkDoBackup(doBackup)
#         if self.badObject is True:
#             return
#         self.checkFolders(folders, cfg)
#         if self.badObject is True:
#             return
#         self.backupFolder = self.checkBackupFolder(backupFolder, cfg)
#
#     def customPrint(self, msg, verboseLevel, title=None, onlyTitle=False):
#         customPrint(msg, verboseLevel, title, onlyTitle, self.verbose)
#
#     def checkName(self, name):
#         if isinstance(name, str) is False:
#             self.errors.append('name parameter should be a string : ')
#             self.customPrint(None, 0, 'name parameter should be a string : ', True)
#             self.badObject = True
#             return
#         return name
#
#     def checkDoBackup(self, doBackup):
#         if isinstance(doBackup, bool) is False:
#             self.errors.append('doBackup parameter should be a bool : ')
#             self.customPrint(None, 0, 'doBackup parameter should be a bool : ', True)
#             self.badObject = True
#             return
#         return doBackup
#
#     def returnFolderFullPath(self, folder, user, sysRoot):
#         folder = folder.replace('$USER', user)
#         folder = folder.replace('$ROOT', sysRoot)
#         return folder
#
#     def checkFolders(self, folders, cfg):
#         if isinstance(folders, dict) is False:
#             self.errors.append('folders parameter should be a dict : ')
#             self.customPrint(None, 0, 'folders parameter should be a dict : ', True)
#             self.badObject = True
#             return
#         for folder in folders.keys():
#             folder = self.returnFolderFullPath(folder, cfg['user'], cfg['sysRoot'])
#             if os.path.isdir(folder) is False:
#                 self.errors.append('Folder not found : '+folder)
#                 self.customPrint(folder, 0, "Folder not found : ")
#                 continue
#             if folders[folder] is None:
#                 self.folders[folder] = None # #####TODO store each file and folders ?
#                 continue
#             else:
#                 self.folders[folder] = []
#                 if isinstance(folders[folder], str) is True:
#                     folders[folder] = [folders[folder]]
#                 for file in folders[folder]:
#                     if os.path.isfile(folder+'/'+file) is False:
#                         self.errors.append('File not found : '+folder+'/'+file)
#                         self.customPrint(folder+'/'+file, 0, 'File not found')
#                         continue
#                     self.folders[folder].append(file)
#                 if self.folders[folder] == []:
#                     self.errors.append('No File To Process Found : Skipping')
#                     self.customPrint(None, 0, 'No File To Process Found : Skipping', True)
#                     del self.folders[folder]
#         if self.folders == {}:
#             self.errors.append('Nothing To Process : Skipping')
#             self.customPrint(None, 0, 'Nothing To Process : Skipping', True)
#             self.doBackup = False
#
#     def checkBackupFolder(self, backupFolder, cfg):
#         if backupFolder is not None:
#             backupFolder = self.returnFolderFullPath(backupFolder, cfg['user'], cfg['sysRoot'])
#             if os.path.isdir(backupFolder) is False:
#                 self.errors.append('Backup folder not found : ' + backupFolder)
#                 self.customPrint(None, 0, 'Backup folder not found : '+backupFolder, True)
#                 self.badObject = True
#                 return
#         return backupFolder
#
#
# class Backup():
#     def __init__(self, softBank, configDic=None, verbose=0):
#         self.configDic = {
#             "createFolders": True,
#             "sysRoot": 'C:/',
#             "user": 'Doodoo',
#             'windowsUserPath': '$ROOT/Users/$USER/Documents',
#             "backupPath": None,  # None : backup in the path of the file copied, Else : backup in specified folder
#             "createBackupFolder": False,  # if true create a "_backup" folder to store and stack backups
#             "backupName": '$DATE.$TIME_$FILENAME_backup',
#             "maxBackupNumber": None,
#             "deleteOlderThan": None,
#             "checkSum":False, # is it Possible ? #### TODO
#         }
#         self.backupDic = {}
#         self.verbose = verbose
#         self.softBank = softBank
#
#         result = self.checkConfigDic(configDic)
#         if result == -1:
#             return
#         self.createBackupObjects()
#         self.customPrint(self.backupDic, 0, "Backup Dic")
#         for key in self.backupDic.keys():
#             self.customPrint(key, 1)
#             self.customPrint(self.backupDic[key].__dict__, 1)
#         # self.doBackup()
#
#     def customPrint(self, msg, verboseLevel, title=None, onlyTitle=False):
#         customPrint(msg, verboseLevel, title, onlyTitle, self.verbose)
#
#     def checkConfigDic(self, configDic):
#         # conform configDic
#         for key in configDic.keys():
#             if key not in self.configDic.keys():
#                 self.customPrint(None, 0, "Wrong arguments used in configDic : "+key, True)
#                 return (-1)
#         self.configDic.update(configDic)
#
#     def createBackupObjects(self):
#         for item in self.softBank.keys():
#             folders = self.softBank[item]['folders']
#             doBackup = self.softBank[item]['doBackup']
#             backupFolder = self.softBank[item]['backupFolder']
#             backupObj = BackupedItem(item, folders, self.configDic, doBackup, backupFolder, self.verbose)
#             if backupObj.badObject is True:
#                 self.customPrint(None, 0, "Omitting object : "+backupObj.name, True)
#                 continue
#             self.backupDic[backupObj.name] = backupObj
#
#     def doBackup(self):
#         print("backuping" + self.softBank)
#
#
# def launchBackupFromFile(backupParmFilePath, configDic=None, verbose=0):
#     if os.path.isfile(backupParmFilePath) is False:
#         customPrint(backupParmFilePath, 0, 'File not found', False, verbose)
#     fileObj = open(backupParmFilePath, 'r')
#     content = fileObj.read()
#     fileObj.close()
#     customPrint(content, 1, 'Software Backup Preferences')
#     softBank = eval(content)
#     result = Backup(softBank, configDic, verbose)
#
# def wholeBackupFromPref(softPath=None):
#     configDic = {}
#     if softPath is None:
#         softPath = sys.argv[0].replace('Backup.py', '/BackupPrefs.cfg')
#     launchBackupFromFile(softPath, configDic, 1)
#
# # def createDefaultConfig(path, ):
# #     softDic = {"soft1":
# #         {
# #             'name': 'test',
# #             'doBackup': True,
# #             'folders': {'D:/msdia80.dll',
# #                         },
# #             'backupFolder': 'D:/Desktop',
# #         }
# #     }
# #     fileObj = open(path, 'w')
# #     pprint(softDic, stream=fileObj)
# #     fileObj.close()
#
# if __name__ == "__main__":
#     wholeBackupFromPref('D:/Desktop/configDic.cfg')
#     # createDefaultConfig('D:/Des

from PySide import QtCore, QtGui, QtUiTools

class ActionObject():
    def __init__(self, cfgDic=None):
        self.name = None
        self.type = None
        self.description = None
        self.target = None
        self.isScript = False

        self.__dict__.update(cfgDic)

class BackupUi(QtGui.QMainWindow):
    def __init__(self, verbose=0):
        super(BackupUi, self).__init__()
        self.verbose = verbose
        self.data = Backup()

        self.init_ui()
        self.setup_ui()
        self.finishUi()

    def init_ui(self):
        self.setWindowTitle('Backup Tool')
        self.mainWidget = QtGui.QWidget()
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QtGui.QGridLayout()
        self.mainWidget.setLayout(self.mainLayout)

        self.setupMenuBar()
        self.setupToolBar()
        self.setupMainWidget()
        self.setupStatusBar()

    def setupMenuBar(self):
        pass

    def setupToolBar(self):
        pass

    def setupMainWidget(self):
        self.setupMainActionsPane()
        self.mainLayout.addWidget(self.mainActionPane, 0, 0)
        self.setupSubActionPane()
        self.mainLayout.addWidget(self.subActionPane, 0, 1)
        self.setupEditActionPane()
        self.mainLayout.addWidget(self.editActionPane, 0, 2)

    def setupMainActionsPane(self):
        self.mainActionPane = QtGui.QWidget()
        self.mainActionPane_layout = QtGui.QVBoxLayout()
        self.mainActionPane.setLayout(self.mainActionPane_layout)
        self.addMainAction = QtGui.QPushButton('Add Step')
        self.mainActionPane_layout.addWidget(self.addMainAction)
        self.applicationList_ListWidget = QtGui.QListWidget()
        self.mainActionPane_layout.addWidget(self.applicationList_ListWidget)
        self.runBackup = QtGui.QPushButton('Run Backup')
        self.mainActionPane_layout.addWidget(self.runBackup)

    def setupSubActionPane(self):
        self.subActionPane = QtGui.QWidget()
        self.subActionPane_layout = QtGui.QVBoxLayout()
        self.subActionPane.setLayout(self.subActionPane_layout)
        self.actions_TreeWidget = QtGui.QTreeWidget()
        self.actions_TreeWidget.setColumnCount(2)
        self.actions_TreeWidget.setHeaderItem(QtGui.QTreeWidgetItem(['Actions', 'Description']))
        self.subActionPane_layout.addWidget(self.actions_TreeWidget)
        self.runAction = QtGui.QPushButton('Run Action')
        self.subActionPane_layout.addWidget(self.runAction)

    def setupEditActionPane(self):
        self.editActionPane = QtGui.QWidget()
        self.editActionPane_Layout = QtGui.QVBoxLayout()
        self.editActionPane.setLayout(self.editActionPane_Layout)
        self.addAction_Button = QtGui.QPushButton('Add Action')
        self.editActionPane_Layout.addWidget(self.addAction_Button)
        self.apply_Button = QtGui.QPushButton('Apply')
        self.editActionPane_Layout.addWidget(self.apply_Button)
        self.removeAction_Button = QtGui.QPushButton('Remove Action')
        self.editActionPane_Layout.addWidget(self.removeAction_Button)

    def setupStatusBar(self):
        pass

    def setup_ui(self):
        for soft in self.data.config.keys():
            qtItem = QtGui.QListWidgetItem(soft)
            self.applicationList_ListWidget.addItem(qtItem)
            self.data.config[soft]['qtItem'] = qtItem

    def finishUi(self):
        self.data.config['Soft_2']['qtItem'].setSelected(True)
        current = self.applicationList_ListWidget.selectedItems()
        customPrint(current, 0)

class Backup:
    def __init__(self, verbose=0):
        self.verbose = verbose
        self.config = {
            'Soft_1':{
                'Action1 Label': ActionObject({'name':'action1', 'type':'file', 'description':'tata'}),
                'Action2 Label': ActionObject({'name': 'action2', 'type': 'file', 'description': 'tutu'})
            },
            'Soft_2': {
                'Action1 Label': ActionObject({'name': 'action3', 'type': 'folder', 'description': 'blabla'}),
                'Action2 Label': ActionObject({'name': 'action4', 'type': 'folder', 'description': 'bleble'})
            },
        }


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ui = BackupUi()
    ui.show()
    sys.exit(app.exec_())
