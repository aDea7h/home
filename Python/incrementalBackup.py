import sys
import os
import shutil
from time import localtime, strftime
import prod.tools

def incrementalBackup(filePath=sys.argv[0], backupFolder=None, verbose = False):
    '''
    maybe worth developping real versionning with comment
    '''
    ################################################################################
    appendName = ""
    generalBackupFolder = "_backups"
    ################################################################################
      
    if verbose == True:
        print ("Original file: %s" % (filePath))
    fileFolder = os.path.dirname(filePath)
    fileExtension = ((os.path.splitext(filePath)[-1:]))[0]
    if verbose ==True:
        print(fileExtension)
        print(os.path.basename(filePath))
    if fileExtension == "":
        fileName = os.path.basename(filePath)
    else:
        fileName = (os.path.basename(filePath).split(fileExtension[0]))[0]
    if verbose == True:
        print (fileName)
    
    if backupFolder != None:
        backupFolder = fileFolder+"/"+generalBackupFolder+"/"+backupFolder
    else:
        backupFolder = fileFolder+"/"+generalBackupFolder+"/"+fileName
    if verbose == True:
        print ("Backup Folder: %s" % (backupFolder))

    if os.path.isdir(backupFolder) == False:
        os.makedirs(backupFolder)
        if verbose == True:
            print ("folder created")

    #backup ac date incrementee
    localDate = strftime("%y%m%d", localtime())
    localTime = strftime("%H%M%S", localtime())

    #versionFile
    i = 1
    while i > 0:
        #versionFile = str(i).rjust(3, "0")
        backupedFileName = localDate+"-"+localTime+"_"+fileName+fileExtension+appendName
        if os.path.isfile("%s/%s" % (backupFolder, backupedFileName)) == True:
            i = i + 1
            print ("%s Already exists" % (backupedFileName))
        else:
            i = -1
    if verbose == True:
        print (("%s/%s" % (backupFolder, backupedFileName)))
    shutil.copy2(filePath, "%s/%s" % (backupFolder, backupedFileName))
    if verbose == True:
        print ("file written")

def backupFiles(files, path = None, verbose = False):

    def backupLaunch(files, backupFolder=None):
        for file in files:
            file = path+"/"+file
            if os.path.isfile(file) == True:
                if verbose == True:
                    print("Backuping : "+file)
                incrementalBackup(file, backupFolder, verbose)
            else:
                print("Wrong file name : "+file)

    if path == None:
        path = os.path.dirname(sys.argv[0])

    if os.path.isdir(path) == False:
        exit("Folder not found : "+path)

    if isinstance(files, list) == True:
        backupLaunch(files, None)
    else:#dict
        for backupFolder in files:
            backupLaunch(files[backupFolder], backupFolder)

def restoreFiles(pathBackup, file, version, fileProperties=True):
    print("restoring : "+pathBackup+"/"+version+"_"+file)
    origPath = pathBackup.split("_backups")
    if len(origPath) > 2:
        origPath = "_backups".join(origPath[:-1])
    else:
        origPath = origPath[0]
    restoring = pathBackup+"/"+version+"_"+file
    original = origPath+file
    print(restoring, original)
    if fileProperties == True:
        shutil.copy2(restoring, original)
    else:
        shutil.copy(restoring, original)

def restoreFilesPrompt(path=None, generalBackupFolder="_backups", fileProperties=True, verbose=0):

    def getBackupFolders(path):
        #Choose backup Folders
        backupedFiles = os.listdir(path)

        message = "Choose which Folder to restore : ..."
        chosenFolder = prod.tools.promptFormatting(backupedFiles, message)
        print(chosenFolder)

        if verbose >= 1:
            print("-->> Checking folder : "+str(chosenFolder[0][1]))
        path = path+"/"+str(chosenFolder[0][1])
        backupedFiles = sorted(os.listdir(path), reverse=True)
        return(path, backupedFiles)

    def getVersionList(backupedFiles):
        versionList = {}
        for file in backupedFiles:
            version = file.split("_")
            fileName = version[1:]
            fileName = "_".join(fileName)
            version = version[0]
            if fileName not in versionList.keys():
                versionList[fileName] = [version]
            else:
                versionList[fileName].append(version)
        return(versionList)

    #Test args
    if path == None:
        path = os.path.dirname(sys.argv[0])

    if os.path.isdir(path) == False:
        exit("Wrong path name : "+path)

    path = path+"/"+generalBackupFolder
    if os.path.isdir(path) == False:
        exit("No backup folder named : "+generalBackupFolder)

    print("---------------------->> Restoring from : "+path)
    path, backupedFiles = getBackupFolders(path)
    versionList = getVersionList(backupedFiles)

    if len(versionList) > 1:
        message = "Choose which File(s) to restore (multi files separated by '/''): ..."
        chosenFiles = prod.tools.promptFormatting(sorted(versionList.keys()), message)
    else:
        message = list(versionList)
        chosenFiles = [[0, message[0]]]

    idx = 0
    for i in chosenFiles:
        print("Restoring File : "+str(chosenFiles[idx][1]))
        idx +=1

    toRestore=[]
    for key in chosenFiles:
        key = key[1]
        message = "Choose '"+ key +"' Versionning : ..."
        chosenVersion = prod.tools.promptFormatting(versionList[key], message, processFor=["readableTimeFormat"])
        version = prod.tools.processStringName(chosenVersion[0][1], ["compactTimeFormat"])
        if os.path.isfile(path+"/"+version+"_"+key) == False:
            print("WARNING : Error, while processing backuped file name")
            user = input("Nothing done : ABORTING")
            exit(-1)
        else:
            toRestore.append([path, key, version])

    for i in toRestore:
        result = restoreFiles(i[0], i[1], i[2], fileProperties)







