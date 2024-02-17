"""TODO
# v1.0 : 24.01.20
# v1.1 :
# v1.2 : 24.02.14
photos actualisees sur oneplus
# TODO :
aGarder : supprimer en local fichiers suppr sur telephone (re copie pour l instant)
signal video envoie vers autres video
checksum files on file collision  doublons: identique =suppression distant ou rien faire / different duplication
copie memoire interne => acceder a whatsapp => besoin du root
clear WhatsApp' sent folder ??
tester autres modes
"""
import sys
import os
import shutil
import subprocess
if "C:/Marik/Documents/Installs/Python" not in sys.path:
    sys.path.append("C:/Marik/Documents/Installs/Python")
import File
import hashlib
import time

adblib = "ppadb"
print("--> Utilisation de la lib ADB : "+adblib)
if adblib == "adb_shell":
    # official google adb_shell lib
    from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
    from adb_shell.auth.sign_pythonrsa import PythonRSASigner
elif adblib == "ppadb":
    from ppadb.client import Client as AdbClient
else:
    raise Exception("Choisir une lib ADB valide")




class PhoneBackup():
    def __init__(self, cfg={}, adblib='ppadb'):
        self.cfg = {'rootIn': '/sdcard',
                 'rootOut': 'D:/Desktop/Telephone',
                 'log': '/sdcard/Documents/{}-file-list.tmp',
                 'logFile': '{}/_historiques',
                 'copiedFileCheck' : "checksum",  # weight, None, checksum
                 'nameCollision': 'copyAsDuplicate',  # copyAsDuplicate, doNothing, removeDistant, overwrite
                 'separateVideos': True,
                 'videoExtensionList': [".webm", ".mkv", ".avi", ".mov", ".wmv", ".mp4", ".mpg", ".mpeg", ".m4v"],
                 'backups': {
                     'Photos': ['{}/DCIM/Camera', '{}/Photos', True],
                     'WhatsApp Video': ['{}/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Video',
                                        '{}/WhatsApp Videos', True],
                     'WhatsApp Photo': ['{}/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images',
                                        '{}/WhatsApp Photos', True],
                     'Autres': ['{}/Pictures', '{}/Autres Photos', True],
                     'AutresVideos': ['{}/Movies', '{}/Autres Videos', True],
                     'aGarder': ['{}/_aGarder', '{}/DCIM/_aGarder', False],
                 },
                    'pathReplace': {
                     'Signal': '{}/Signal Photos',
                 },
                    'adb': {
                     'adbServerPath': "D:/Desktop/copie photos maman/adb_platform-tools_r34.0.5-windows/platform-tools",
                     'method': 'usb',  # wifi / usb
                     'ip': '192.168.1.13',
                     'port': '1234',
                     'adbKeyPath': 'D:/Desktop/copie photos maman/adbkey'},
                    }
        self.cfg.update(cfg)
        self.cfg['adb']['adblib'] = adblib
        self.phone = None
        self.fileTree = {}
        self.errors = []
        self.starttime = time.time()
        start = time.strftime("%H h : %M min : %S s", time.gmtime(self.starttime))
        if os.path.exists(self.cfg['logFile'].format(self.cfg['rootOut'])) is False :
            os.makedirs(self.cfg['logFile'].format(self.cfg['rootOut']))
        self.logPath = self.cfg['logFile'].format(self.cfg['rootOut'])+time.strftime("/%Y.%m.%d_%Hh%Mm%Ss_backup.log", time.gmtime(self.starttime))
        print('Historique des actions : {}'.format(self.logPath))
        self.logObj = open(self.logPath, 'a')
        self.doublePrint("Debut a {}".format(start))

    def doublePrint(self, msg):
        print(msg)
        print(msg, file=self.logObj)

    def adbLauncher(self,):
        adbExe = [self.cfg['adb']['adbServerPath'] + "/adb.exe", "devices"]
        process = subprocess.Popen(adbExe, stdout=subprocess.PIPE)
        process.wait()
        return process.returncode

    def adbConnect(self,):
        def adb_shell_connect():
            # Load the public and private keys
            with open(self.cfg['adb']['adbKeyPath']) as f:
                priv = f.read()
            with open(self.cfg['adb']['adbKeyPath'] + '.pub') as f:
                pub = f.read()
            signer = PythonRSASigner(pub, priv)

            # Connect
            if self.cfg['adb']['method'] == 'wifi':
                device = AdbDeviceTcp('192.168.0.222', 5555, default_transport_timeout_s=9.)
                device.connect(rsa_keys=[signer], auth_timeout_s=0.1)
            else:
                # Connect via USB (package must be installed via `pip install adb-shell[usb])`
                device = AdbDeviceUsb()
                device.connect(rsa_keys=[signer], auth_timeout_s=0.1)

            # Send a shell command
            response1 = device.shell('echo TEST1')
            print(response1)
            return device

        def ppadb_connect():
            if self.cfg['adb']['method'] == 'usb':
                client = AdbClient(host="127.0.0.1", port=5037)
                # print(client)
                devices = client.devices()
                # print(devices)
            else:
                # TODO
                raise Exception("Connection Wifi non supportée avec la lib PPADB")
            if len(devices) == 0:
                raise Exception("Aucun telephone n'est détecté")
            return devices[0]

        if self.cfg['adb']['adblib'] == "adb_shell":
            self.phone = adb_shell_connect()
        elif self.cfg['adb']['adblib'] == "ppadb":
            self.phone = ppadb_connect()
        # print(self.phone)
        return

    def loopAdbConnect(self,):
        loop = 0
        while True:
            if loop > 0:
                userInput = input("Rééssayer la connexion au téléphone ('oui/o/y/yes/1') ou abandonner ('non/n/no/0') ? ")
                if userInput.lower() not in ['oui', 'o', 'y', 'yes', '1', '']:
                    raise Exception("Connection au téléphone à été abandonnée")
                    break
            try:
                self.adbConnect()
                self.phone.shell("ls /sdcard/")
                break
            except:
                self.doublePrint("La connexion a échouée\n\n")
            loop += 1
        return

    def detectVideo(self, fileObj):
        basename, ext = os.path.splitext(fileObj.name)
        if ext in self.cfg['videoExtensionList']:
            return True
        else:
            return False

    def listPhonePath(self, currentBackup):
        src = self.cfg['backups'][currentBackup][0]
        fileName = self.cfg['log'].format(src.split('/')[-1])
        self.phone.shell("ls -lR {0} > {1}".format(src, fileName))
        outFileName = os.path.join(self.cfg['rootOut'], os.path.basename(fileName))
        self.cfg['backups'][currentBackup].append(outFileName)
        self.phone.pull(fileName, outFileName)
        return

    def printTree(self, tree=None, indent=0):
        def iterTree(tree, indent):
            for key in tree:
                if isinstance(tree[key], dict) is True:
                    self.doublePrint('   ' * (indent) + '-folder : ' + key)
                    iterTree(tree[key], indent + 1)
                else:
                    self.doublePrint('   ' * indent + ' - file : ' + tree[key].backupName + ' ' + tree[key].name)
        if tree is None:
            tree = self.fileTree
        self.doublePrint("\n=====> Fichiers a copier")
        iterTree(tree, indent)

    def fullAdbConnect(self):
        adbServerReturnCode = self.adbLauncher()
        if adbServerReturnCode != 0:
            raise Exception("ADB ne s'est pas lancé correctement. Rien a été fait")
        else:
            self.doublePrint("=====> ADB lancé correctement")

        # adb phone connection
        self.loopAdbConnect()
        self.doublePrint("=====> Connection au Téléphone active")

    def createFileObj(self, name, path, clear):
        fileObjCfg = {
            'check_existence': False,
            'get_file_info': True,
            'check_validity': False,
        }
        fileObjAttr = {
            'exists': True,
            'backupName': 'aGarder',
            'copy': None,
            'clear': clear,
            'destName': name,
        }
        fileObj = File.FileObj(path, name, cfg=fileObjCfg, attrs=fileObjAttr)
        return fileObj

    def lslinesplitter(self, line):
        line = line.split(' ')
        split = []
        for item in line:
            if item != '':
                split.append(item)
        return split

    def createFileObjFromLs(self, line, path, backupName, clear):
        fileName = self.lslinesplitter(line)
        fileSize = int(fileName[4])
        fileName = ' '.join(fileName[7:])
        fullsrc = path + '/' + fileName

        fileObjCfg = {
            'check_existence': False,
            'get_file_info': False,
            'check_validity': False,
        }
        fileObjAttr = {
            'size': fileSize,
            'backupName': backupName,
            'copy': None,
            'clear': clear,
            'destName': fileName,
        }
        fileObj = File.FileObj(path, fileName, cfg=fileObjCfg, attrs=fileObjAttr)
        return fullsrc, fileObj

    def buildFileTree(self, currentBackup):
        outFileName = self.cfg['backups'][currentBackup][3]
        clear = self.cfg['backups'][currentBackup][2]
        with open(outFileName, 'r') as logfile:
            lines = logfile.readlines()

        newPath = True
        headerLine = 0
        for line in lines:
            line = line.strip()
            if line == "":
                newPath = True
                headerLine = 0
                continue
            elif newPath is True:
                if headerLine == 0:
                    path = line[:-1]
                    if not path in self.fileTree.keys():
                        self.fileTree[path] = {}
                    headerLine += 1
                    continue
                else:
                    newPath = False
                    continue

            if line.startswith('d'): #is a directory
                continue

            fullsrc, fileObj = self.createFileObjFromLs(line, path, currentBackup, clear)
            self.fileTree[path][fullsrc] = fileObj

    def buildKeptFileTree(self):
        path = self.cfg['backups']['aGarder'][0]
        self.fileTree[path] = {}
        if os.path.exists(path) is False:
            self.doublePrint("=====> Chemin introuvable : {}".format(path))
            self.errors.append("=====> Chemin introuvable : {}".format(path))
            return
        fileList = os.listdir(path)
        clear = self.cfg['backups']['aGarder'][2]
        for fileName in fileList:
            fullsrc = self.cfg['backups']['aGarder'][0] + '/' + fileName
            if os.path.isdir(fullsrc) is True:
                self.errors.append("{} dossier ignoré, transfert de fichier uniquement".format(fullsrc))
                self.doublePrint("{} dossier ignoré, transfert de fichier uniquement".format(fullsrc))
                continue
            fileObj = self.createFileObj(fileName, self.cfg['backups']['aGarder'][0], clear)
            self.fileTree[path][fullsrc] = fileObj

    def setFileTree(self):
        self.doublePrint("\n=====> Liste des fichiers trouves")
        for path in self.cfg['backups']:
            if path == 'aGarder':
                continue
            currentBackup = path
            self.cfg['backups'][path][0] = self.cfg['backups'][path][0].format(self.cfg['rootIn'])
            self.cfg['backups'][path][1] = self.cfg['backups'][path][1].format(self.cfg['rootOut'])
            self.listPhonePath(currentBackup)
            self.buildFileTree(currentBackup)

        self.cfg['backups']['aGarder'][0] = self.cfg['backups']['aGarder'][0].format(self.cfg['rootOut'])
        self.cfg['backups']['aGarder'][1] = self.cfg['backups']['aGarder'][1].format(self.cfg['rootIn'])
        self.buildKeptFileTree()

    def collisionResolve(self, fileObj):
        if fileObj.path.startswith(self.cfg['rootIn']) is True:
            fileColision = os.path.exists('{}/{}'.format(fileObj.destPath, fileObj.destName))
        else:
            fileLs = self.phone.shell("ls '{}/{}'".format(fileObj.destPath, fileObj.destName))
            if fileLs.strip() == '{}/{}'.format(fileObj.destPath, fileObj.destName):
                fileColision = True
            else:
                fileColision = False

        if fileColision is True:
            # copyAsDuplicate, doNothing, removeDistant, overwrite
            if fileObj.backupName == 'aGarder':
                fileObj.copy = False
                self.doublePrint("  Copie Annulee car fichier deja existant")
            elif self.cfg["nameCollision"] == "copyAsDuplicate":
                fileObj.destName = 'dup_{}'.format(fileObj.destName)
                fileObj.copy = True
                self.doublePrint("  Copie Doublon car fichier deja existant")
            elif self.cfg["nameCollision"] == "doNothing":
                fileObj.copy = False
                self.doublePrint("  Copie Annulee car fichier deja existant")
            elif self.cfg["nameCollision"] == "removeDistant":
                fileObj.copy = False
                fileObj.clear = True
                self.doublePrint("  Suppression du telephone car fichier deja existant")
            else:  # overwrite
                self.doublePrint("  Ecraser le fichier deja existant")
                fileObj.copy = True
        else:
            fileObj.copy = True
        return fileObj

    def setOutPath(self, fileObj):
        outPath = self.cfg['backups'][fileObj.backupName][1]
        if fileObj.backupName != 'aGarder':
            if fileObj.path.endswith('Pictures') is True and fileObj.name.startswith('signal-') is True:
                outPath = self.cfg['pathReplace']['Signal'].format(self.cfg['rootOut'])
            else:
                midpath = os.path.commonpath([self.cfg['backups'][fileObj.backupName][0].format(self.cfg['rootIn']), fileObj.path])
                midpath = fileObj.path[len(midpath):]
                outPath = self.cfg['backups'][fileObj.backupName][1] + midpath

            if self.cfg['separateVideos'] is True:
                isVideo = self.detectVideo(fileObj)
                if isVideo is True:
                    outPath = outPath.replace('Photo', 'Video')

        fileObj.destPath = outPath
        fileObj = self.collisionResolve(fileObj)
        self.doublePrint('  - Fichier Source: {}/{}'.format(fileObj.path, fileObj.name))
        self.doublePrint('  - Fichier Destination: {}/{}'.format(fileObj.destPath, fileObj.destName))

    def getHash(self, path):
        return hashlib.md5(open(path, 'rb').read()).hexdigest()

    def getAndroidHash(self, path):
        hash = self.phone.shell("md5sum '{}'".format(path))
        hash = hash.split(' ')[0].strip()
        return hash

    def copyCheck(self, fileObj, fullsrc, fulldst):
        # 'copiedFileCheck': "weight",  # weight, None, checksum
        check = self.cfg['copiedFileCheck']
        if check is None:
            return True
        elif check == 'weight':
            if fileObj.path.startswith(self.cfg['rootIn']) is True:
                destsize = os.path.getsize(fulldst)
            else:
                ls = self.phone.shell("ls -l '{}'".format(fulldst))
                destsize = int(self.lslinesplitter(ls)[4])
            self.doublePrint('  --> verif poid fichier: {} - {}'.format(fileObj.size, destsize))
            if destsize == fileObj.size:
                return True
            else:
                return False
        else:  # checksum
            if fileObj.path.startswith(self.cfg['rootIn']) is True:
                hashSrc = self.getAndroidHash(fullsrc)
                hashDst = self.getHash(fulldst)
            else:
                hashSrc = self.getHash(fullsrc)
                hashDst = self.getAndroidHash(fulldst)
            self.doublePrint('  --> verif hash fichier: {} - {} / {}'.format(hashSrc == hashDst, hashSrc, hashDst))
            if hashSrc == hashDst:
                return True
            else:
                return False

    def copyFile(self, fileObj, copy):
        def removeFile(path, phone):
            if phone is True:
                self.phone.shell("rm '{}'".format(path))
            else:
                os.remove('{}'.format(path))

        fullsrc = '{}/{}'.format(fileObj.path, fileObj.name)
        fulldst = '{}/{}'.format(fileObj.destPath, fileObj.destName)
        copyCheckOk = True
        phone = fileObj.path.startswith(self.cfg['rootIn'])
        if fileObj.copy is True:
            if phone is True:
                if os.path.exists(fileObj.destPath) is False:
                    os.makedirs(fileObj.destPath)
                    self.doublePrint('  Dossier cree {}'.format(fileObj.destPath))
                if copy is True:
                    self.phone.pull(fullsrc, fulldst)
            else:
                ls = self.phone.shell("ls '{}'".format(fileObj.destPath))
                if ls == 'ls: {}: No such file or directory'.format(fileObj.destPath):
                    self.phone.shell("mkdir -p {}".format(fileObj.destPath))
                    self.doublePrint('  Dossier cree {}'.format(fileObj.destPath))
                if copy is True:
                    self.phone.push('{}'.format(fullsrc), '{}'.format(fulldst))
            if copy is True:
                copyCheckOk = self.copyCheck(fileObj, fullsrc, fulldst)
                if copyCheckOk is True:
                    self.doublePrint('--> OK: Copie')
                else:
                    self.errors.append('=====> Erreur lors de la copie de: {}'.format(fullsrc))
                    self.doublePrint('=====> Erreur lors de la copie de: {}'.format(fullsrc))
                    removeFile(fulldst, phone)
                    self.doublePrint('--> Fichier errone destination supprime')

        if copy is True:
            if fileObj.clear is True and copyCheckOk is True:
                removeFile(fullsrc, phone)
                self.doublePrint('--> OK: Fichier source supprime')

    def fileTreeCopy(self, copy=True):
        for folder in self.fileTree.keys():
            for path in self.fileTree[folder]:
                self.doublePrint('\n')
                fileObj = self.fileTree[folder][path]
                self.doublePrint('--> Copie de {}'.format(fileObj.name))
                self.setOutPath(fileObj)
                self.copyFile(fileObj, copy)

        self.rescan()
        self.clean()

    def rescan(self):
        # adb shell am broadcast - a android.intent.action.MEDIA_MOUNTED - d file: // / sdcard
        # https://stackoverflow.com/questions/17928576/refresh-android-mediastore-using-adb
        # https://stackoverflow.com/questions/66929450/images-not-shown-in-photos-using-adb-push-pictures-to-android-11-emulator
        # path = "{}".format(self.cfg['backups']['aGarder'][1].format(self.cfg['rootIn']))
        # print("rescan ", path)

        #print("test old scan")
        #print("am broadcast -a android.intent.action.MEDIA_MOUNTED - d file :{}".format(path))
        # print(self.phone.shell("ls "+path))
        #self.phone.shell("am broadcast -a android.intent.action.MEDIA_MOUNTED - d file :{}".format(path))
        # print('test new scan 1')
        # print("find /mnt" + path[2:] + " -exec am broadcast \ -a android.intent.action.MEDIA_SCANNER_FILE \ -d file://{} \\\\;")
        #self.phone.shell("find /mnt" + path + " -exec am broadcast \ -a android.intent.action.MEDIA_SCANNER_FILE \ -d file://{} \\\\;")
        # self.phone.shell("find /mnt" + path + " -exec am broadcast -a android.intent.action.MEDIA_SCANNER_FILE -d file://{} \\\\;")
        # print('method 3')
        #adb shell "find /mnt" + path + " | while read f; do am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d \"file://${f}\"; done"
        # self.phone.shell("find /mnt" + path + " | while read f; do am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d \"file://${f}\"; done")

        # print()
        #adb shell content call --method scan_volume --uri content://media --arg external_primary
        self.phone.shell("content call --method scan_volume --uri content://media --arg external_primary")
        # adb logcat -s MediaProvider
        # self.phone.logcat()

    def clean(self):
        def cleanTmpFiles():
            for path in self.cfg['backups']:
                if path == 'aGarder':
                    continue
                logfile = self.cfg['backups'][path][3]
                os.remove(logfile)
            ls = self.phone.shell("ls {}".format(self.cfg['log'].format('*')))
            for log in ls.split():
                self.phone.shell("rm "+log.strip())
            self.doublePrint("\n=====> Nettoyage des fichiers temporaire Ok")

        cleanTmpFiles()
        if len(self.errors) > 0:
            self.doublePrint("\n##################### Erreurs lors de la copie : #####################")
            for line in self.errors:
                # print('# {}'.format(line))
                self.doublePrint(line)
            self.doublePrint("##############################################################")
            self.doublePrint('\n')
            self.doublePrint("##############################################################")
            self.doublePrint("==> ATTENTION : Il y a eu {} erreurs lors de la copie <==".format(len(self.errors)))
            self.doublePrint("##############################################################")
        else:
            self.doublePrint('')
        timelength = time.time()-self.starttime
        timelength = time.strftime('%H h: %M min: %S s', time.gmtime(timelength))
        self.doublePrint("==> {} plus tard c'est enfin fini :)".format(timelength))
        self.doublePrint("==> Historique de l'execution ici:")
        self.doublePrint('')
        self.doublePrint(self.logPath)
        self.doublePrint('')
        self.logObj.close()
        subprocess.Popen(["C:/Windows/system32/notepad.exe", self.logPath])


# cfg = {'rootIn': '/sdcard/Documents/Tests',
#          'rootOut': 'D:/Desktop/copie photos maman/Telephone',
#          'copiedFileCheck': "checksum",  # weight, None, checksum
#          'nameCollision': 'overwrite',  # copyAsDuplicate, doNothing, removeDistant, overwrite
#          'backups': {
#              'Autres': ['{}/Pictures', '{}/Autres Photos', True],
#              'aGarder': ['{}/_aGarder', '{}/DCIM/_aGarder', False],
#          },
#          }

# cfg = {'backups': {
#                      'Photos': ['{}/DCIM/Camera', '{}/Photos', False],
#                      'WhatsApp Video': ['{}/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Video',
#                                         '{}/WhatsApp Videos', False],
#                      'WhatsApp Photo': ['{}/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images',
#                                         '{}/WhatsApp Photos', False],
#                      'Autres': ['{}/Pictures', '{}/Autres Photos', False],
#                      'AutresVideos': ['{}/Movies', '{}/Autres Videos', False],
#                      'aGarder': ['{}/_aGarder', '{}/DCIM/_aGarder', False],
#                  },
# }
#
# cfg = {'nameCollision': 'doNothing',  # copyAsDuplicate, doNothing, removeDistant, overwrite
#         'backups': {
#                      'WhatsApp Video': ['{}/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Video', '{}/WhatsApp Videos', False],
#                      'WhatsApp Photo': ['{}/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images', '{}/WhatsApp Photos', False],
#                      'Autres': ['{}/Pictures', '{}/Autres Photos', False],
#                      'AutresVideos': ['{}/Movies', '{}/Autres Videos', False],
#                      'aGarder': ['{}/_aGarder', '{}/DCIM/_aGarder', False],
#                  },
# }
if __name__ == "__main__":
    c = PhoneBackup(adblib=adblib)
    c.fullAdbConnect()
    c.setFileTree()
    c.printTree()
    c.fileTreeCopy(copy=True)

# l = c.phone.shell("ls /sdcard/Documents/*-file-list.tmp")
# l = c.phone.shell("ls /")
# c.rescan()
# print(l)
# print(c.phone.shell("ls /data/data"))
# for i in l.split():
#     print(i)
#     c.phone.shell("rm "+i.strip())
