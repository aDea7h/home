import sys
if "E:/Scripts/Python/Phone Backup" not in sys.path:
    sys.path.append("E:/Scripts/Python/Phone Backup")

import phoneBackup


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

cfg = {'rootIn': '/sdcard',
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

c = phoneBackup.PhoneBackup(cfg=cfg, adblib=adblib)
c.fullAdbConnect()
c.setFileTree()
c.printTree()
c.fileTreeCopy(copy=True)