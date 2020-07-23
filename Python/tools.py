from time import strptime, strftime
from pprint import pprint as pprint
import os
import shutil


def customPrint(msg, verboseLevel=0, title=None, onlyTitle=False, verbose=0):
    if verbose >= verboseLevel:
        if title is not None:
            if onlyTitle is True:
                title = '---------------------->>>>>> ' + str(title) + '<<<<<<----------------------'
            else:
                title = '---------------->>>>>> ' + str(title)
            print(title)
            if onlyTitle is True:
                return
        pprint(msg)


class CustomPrint:
    def __init__(self, class_verbose, dev):
        self.class_verbose = class_verbose
        self.dev = dev  # TODO How To manage ?

    def __call__(self, msg, verbose_level=0, title=None, only_title=False, title_level=6):
        self.cprint(msg, verbose_level, title, only_title, title_level)

    def cprint(self, msg, verbose_level=0, title=None, only_title=False, title_level=6):
        if self.dev is True and verbose_level > 0:
            return
        if self.class_verbose >= verbose_level:
            if title is not None:
                if only_title is True:
                    print('{0}{1} {2} {3}{0}'.format('-'*title_level*2, '>'*title_level, str(title), '<'*title_level))
                    return
                else:
                    print('---------------->>>>>> ' + str(title))
            pprint(msg)

    def title(self, title, verbose_level=0):
        self.cprint('', verbose_level, title, True)

    def title1(self, title, verbose_level=0,):
        self.cprint('', verbose_level, title, True, 6)

    def title2(self, title, verbose_level=0,):
        self.cprint('', verbose_level, title, True, 4)

    def title3(self, title, verbose_level=0,):
        self.cprint('', verbose_level, title, True, 2)


def processStringName(stringName, processFor, noError=True):
    if "readableTimeFormat" in processFor:
        try:
            stringName = strptime(stringName, '%y%m%d-%H%M%S')
            stringName = strftime("%Y/%m/%d - %Hh %Mmin %Ss", stringName)
        except:
            pass
    elif "compactTimeFormat" in processFor:
        try:
            stringName = strptime(stringName, "%Y/%m/%d - %Hh %Mmin %Ss")
            stringName = strftime('%y%m%d-%H%M%S', stringName)
        except:
            pass
    elif "toDotSpacedFullYear" in processFor:
        try:
            stringName = strptime(stringName, "%y%m%d")
            stringName = strftime('%Y.%m.%d', stringName)
        except:
            if noError == True:
                pass
            else:
                return(False)
    return(stringName)

def promptFormatting(inputChoices, message, errorMessage=None, processFor=[]):
    if errorMessage == None:
        errorMessage = "(type : 'break' to abort)"

    formattedChoices = []
    idx = 0
    for i in inputChoices:
        if processFor != []:
            i = processStringName(i, processFor)
        formattedChoices.append([idx, i])
        idx += 1

    while True:
        error = False
        idx = 0
        print()
        print("Index |  File Name")
        for i in formattedChoices:
            print(" "+str(i[0])+"    |  "+i[1])
        userInput = input("-->> "+message)

        if userInput in ["abort", "quit", "break"]:
            exit("User interupted")

        userInput = userInput.split("/")
        for i in list(userInput):
            try:
                i = int(i)
                userInput[idx] = i  
            except:
                print("wrong entry (only integers accepted) : " + i)
                userInput.pop(idx)
                error = True
                continue

            if i >= len(inputChoices):
                print("Index out of range, skipping index : "+str(i))
                userInput.pop(idx)
                error = True
                continue

            idx += 1
        if error == False:
            break
        else:
            userProceed = input("-->> errors occured, proceed anyway (only with accurate data) ? (y/n)")
            print(errorMessage)
            if userProceed in ["y", "yes"]:
                break
            if userProceed in ["abort", "quit", "break"]:
                exit("User interupted")

    idx = 0
    for item in list(formattedChoices):
        if item[0] not in userInput:
            formattedChoices.remove(item)
        idx += 1

    return(formattedChoices)

def savePref(configFile, prefs, verbose = 0):
    if verbose >= 1 :
        print("saving prefs")
        print(prefs)
    fileWriter = open(configFile, "w")
    pprint(prefs, fileWriter)
    fileWriter.close()
    if verbose >= 1:
        print("Saved to : "+configFile)
    return(True)

def getUserPref(configFile, scriptDirectory = None, verbose = 0):
    if scriptDirectory != None:
        userPrefFile = scriptDirectory+configFile
    else:
        userPrefFile = configFile
        
    if os.path.isfile(userPrefFile) == False:
        if os.path.isdir(os.path.dirname(userPrefFile)) == False:
            print("Config folder not found, creating it : "+os.path.dirname(userPrefFile))
            os.makedirs(os.path.dirname(userPrefFile))
        return(False, [])
    else:
        try:
            prefFile = open(userPrefFile, 'r')
        except: #if userPrefFile doesn't exists use tool to recreate one
            if verbose >=1:
                print("couldn't read user config file : "+userPrefFile)
            return(False, [])
        prefs = eval(prefFile.read())
        prefFile.close()
        return(True, prefs)

def getPref(defaultPrefs, configFile, scriptDirectory = None, verbose = 0):
    result, userPrefs = getUserPref(configFile, scriptDirectory, verbose)
    if scriptDirectory != None:
            userPrefFile = scriptDirectory+configFile
    else:
        userPrefFile = configFile
    if result != True:
        userPrefs = defaultPrefs
        savePref(userPrefFile, userPrefs, )
        print("no user pref file : using defaults")
        return(defaultPrefs)
    else:
        if userPrefs["configFile"] != defaultPrefs["configFile"]:
            userPrefs = getUserPref(userPrefs["configFile"], scriptDirectory, verbose)
            
        for key in defaultPrefs:
            if key not in userPrefs.keys():
                userPrefs = defaultPrefs
                print("wrong or obsolete config file : backuping old preferences, creating new defaults")
                shutil.copy2(userPrefFile, os.path.dirname(userPrefFile)+"/prefs.old")
                savePref(userPrefFile, userPrefs)
                return(defaultPrefs)
        if verbose >=1:
            print("returning user preferences")
        return(userPrefs)
    
def autoComplete(stringSearched, autoCompletionList, splitWords=",", splitChars=" ", exclChar="!", verbose = 0):
    import re
    #splitWords = pattern to split string, for multi search, return words
    #splitChars = pattern to split words to search parts in list, return a matched obect in list
    #exclChar = pattern to exclude string from words, return a matched obect in list
    matched = []
    #print(stringSearched, autoCompletionList, splitWords, splitChars)
    splitWords = stringSearched.split(splitWords)
    for word in splitWords:
        print("------>> word : "+word)
        word = word.strip()
        parts = word.split(splitChars)
        for objectTest in autoCompletionList:
            print("-- testing : "+objectTest)
            objectTest = str(objectTest)
            match = []
            for part in parts:
                print("-part : "+part)
                exclusion = False
                if len(part) >0 and part[0] == exclChar:
                    part = part[1:]
                    exclusion = True
                searchResult = re.search(part, objectTest, flags=re.IGNORECASE)
                if verbose >=1:
                    print(part, objectTest, searchResult)
                if searchResult:
                    if exclusion == True:
                        match = "skip"
                        break
                    else:
                        print("Match apend")
                        match.append(searchResult)
                else:
                    if exclusion == True:
                        continue
                    match.append(searchResult)
                    break
            print(match)
            if match  == "skip":
                if verbose >=1:
                    print(" - match skipped : "+objectTest)
                continue
            elif not None in match:
                if verbose >= 1:
                    print(" - match found : "+objectTest)
                matched.append(objectTest)
    matched = list(set(matched))
    if verbose >= 1:
        print("-- >> returning : "+str(matched))
    return(matched)


def matchItems(stringSearched, matchingPatternDic, splitChars="&&", exclChar="!=", verbose = 0):
    import re
    #splitChars = pattern to split words to search parts in list, return a matched obect in list
    #exclChar = pattern to exclude string from words, return a matched obect in list
    matched = []
    for key in matchingPatternDic:
        if verbose >= 1 :
            print("--------------- new key : "+ key)
        for pattern, weight in matchingPatternDic[key].items():
            if verbose >= 1 :
                print("------------- pattern : "+ pattern)
            splitStr = pattern.split(splitChars)
            partMatch = []
            for part in splitStr:
                if verbose >= 1 :
                    print("----testing part : "+ part)
                exclusion = False
                if part.startswith(exclChar):
                    exclusion = True
                    part = part [len(exclChar):]
                    if verbose >= 1:
                        print("-->> excluding : "+exclusion)
                searchResult = re.search(part, stringSearched, flags=re.IGNORECASE)

                if searchResult !=None:
                    if exclusion == True:
                        if verbose >=1:
                            print("-->> excluding : "+ part)
                        partMatch = None
                        break
                    else:
                        if verbose >= 1 :
                            print("-->> matched with : "+part)
                        partMatch.append(part)
                else:
                    if exclusion == True:
                        partMatch.append(exclChar+part)

            if partMatch != None:
                if len(partMatch) == len(splitStr):
                    matched.append([weight, pattern])
                    if verbose >= 1 :
                        print("Pattern matched : "+pattern)
                else:
                    if verbose >= 1:
                        print("Pattern rejected : "+ pattern)
            else:
                if verbose >= 1 :
                    print("Exclusion of some element, pattern rejected : "+ pattern)

    matched = sorted(matched, key=lambda weight : weight[0], reverse = True)
    tags = []
    for weight, match in matched:
        for tag in matchingPatternDic:
            for pattern in matchingPatternDic[tag]:
                if match == pattern and tag not in tags:
                    tags.append(tag)
    return(tags)
