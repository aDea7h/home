import File
import os
import io
import tools
import shutil

def readPlaylist(playListPath, driveLetter="D"):
    if os.path.isfile(playListPath) is False:
        raise Exception("Wrong Path")

    file = io.open(playListPath, 'r', encoding='utf8')
    content = file.readlines()
    file.close()

    files = []
    filesWeight = 0
    driveLetter = driveLetter+':'
    for line in content:
        line = line.strip()
        if line.startswith("#"):
            continue
        filepath = '{}{}'.format(driveLetter, line.replace('\\', '/'))
        fileObj = File.FileObj(filepath)
        if fileObj.exists is False:
            print("--->> file not found : {}/{}".format(fileObj.path, fileObj.name))
            continue
        files.append(fileObj)
        filesWeight += fileObj.size
        print("added {}".format(fileObj.name))

    print("added {} files : Total weight : {}".format(len(files), tools.displayReadableByteSize(filesWeight)))
    return files

def copyPlaylist(playlistPath="D:/Musique/_Playlist/playlist.txt", destinationPath="I:/Music/Base"):
    playlist = readPlaylist(playlistPath)
    copy = True
    if copy is True:
        for fileObj in playlist:
            fileObj.newpath = fileObj.path.replace("D:/Musique", destinationPath)
            # root = os.path.split(fileObj.newpath)[0]
            # print(root, fileObj.newpath)
            if os.path.isdir(fileObj.newpath) is False:
                print("makefolder")
                os.makedirs(fileObj.newpath)
            fullpath = os.path.join(fileObj.path, fileObj.name)
            fullnewpath = os.path.join(fileObj.newpath, fileObj.name)
            shutil.copy2(fullpath, fullnewpath)
            print("copied {}".format(fullnewpath))

class MusicCopy:
    def __init__(self, dbPath='', destPath='', cfg={}):
        defaultCfg = {}
        defaultCfg['dbPath'] = 'D:/Musique'
        defaultCfg['destPath'] = 'I:/Music'
        defaultCfg['playlistRelPath'] = '_Playlist/playlist.txt'

        if dbPath not in ['', None]:
            defaultCfg['dbPath'] = dbPath
        if destPath not in ['', None]:
            defaultCfg['destPath'] = destPath
        if os.path.exists(defaultCfg['dbPath']) is False:
            raise Exception("DB Path not found : "+defaultCfg['dbPath'])
        if os.path.exists(defaultCfg['destPath']) is False:
            raise Exception("Destination Path not found : "+defaultCfg['destPath'])

        defaultCfg['baseDestPath'] = os.path.join(defaultCfg["destPath"], 'Base')

        defaultCfg.update(cfg)
        self.__dict__.update(defaultCfg)

    def readPlaylist(self):
        playlistPath = os.path.join(self.dbPath, self.playlistRelPath)
        if os.path.isfile(playlistPath) is False:
            raise Exception("Wrong Path : {}".format(playlistPath))

        file = io.open(playlistPath, 'r', encoding='utf8')
        content = file.readlines()
        file.close()

        files = []
        filesWeight = 0
        driveLetter = playlistPath[:2]
        for line in content:
            line = line.strip()
            if line.startswith("#"):
                continue
            filepath = '{}{}'.format(driveLetter, line.replace('\\', '/'))
            fileObj = File.FileObj(filepath)
            if fileObj.exists is False:
                print("--->> file not found : {}/{}".format(fileObj.path, fileObj.name))
                continue
            files.append(fileObj)
            filesWeight += fileObj.size
            print("added {}".format(fileObj.name))

        print("added {} files : Total weight : {}".format(len(files), tools.displayReadableByteSize(filesWeight)))
        return files, filesWeight

    def buildBaseList(self):
        if os.path.exists(self.baseDestPath) is False:
            print('--->> Base folder not found : '+self.baseDestPath)
            return []

        baseTreeObj = File.RecursiveWalk(self.baseDestPath)
        baseTree = baseTreeObj.return_tree()
        baseTreeObj.print_tree()
        print(baseTree)

    def removeExistInBase(self, objList):
        baseObjList = self.buildBaseList()
        print(objList)
        # for obj in objList:



    def copyFiles(self, source, dest, objList, copy=True):
        for fileObj in objList:
            fileObj.newpath = fileObj.path.replace("D:/Musique", dest)
            if os.path.isdir(fileObj.newpath) is False:
                print("make path to folder : "+fileObj.newpath)
                if copy is True:
                    os.makedirs(fileObj.newpath)
            fullpath = os.path.join(fileObj.path, fileObj.name)
            fullnewpath = os.path.join(fileObj.newpath, fileObj.name)
            if copy is True:
                shutil.copy2(fullpath, fullnewpath)
                print("copied {}".format(fullnewpath))
            else:
                print('copy from {} to {}'.format(fullpath, fullnewpath))

    def playlistToBase(self, copy=True):
        objList, weight = self.readPlaylist()
        self.copyFiles(self.dbPath, self.baseDestPath, objList, copy)

    def playlistToDest(self, copy=True):
        objList, weight = self.readPlaylist()
        self.removeExistInBase(objList)
        self.copyFiles(self.dbPath, self.destPath, objList, copy)


if __name__ == "__main__":
    mc = MusicCopy(destPath="G:/")
    # mc.playlistToBase(False)
    mc.playlistToDest(True)

# Todo
# remove duplicate from base / dest
# check if exists before copy
# remove unwanted before copy