from time import strptime, strftime
import pprint
import os
import shutil

def displayReadableByteSize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

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
        pprint.pprint(msg)


class CustomPrint:
    #TODO use logging module ?
    #TODO write log file
    #TODO Add colors
    def __init__(self, minimum_verbose_level=0):
        self.verbose = minimum_verbose_level
        self.title_level = 6
        self.infoLevel = 'Info' #Info / Warn / Error
        self.displayInfoLevel = True
        self.pprint = pprint.PrettyPrinter(indent=4)
        # self.dev = False  # TODO Why ? How To manage ?

    def __call__(self, msg, verbose_level=0, title=None, only_title=False, title_level=None, infoLevel=None):
        self.cprint(msg, verbose_level, title, only_title, title_level, infoLevel)

    def cprint(self, msg, verbose_level=0, title=None, only_title=False, title_level=None, infoLevel=None):
        if infoLevel is None:
            infoLevel = self.infoLevel
        if self.verbose >= verbose_level:
            if title is not None:
                if title_level is None:
                    title_level = self.title_level
                title = str(title) # TODO Manage Objects
                title = '{0}{1} {2} {3}{0}'.format('-' * title_level * 2, '>' * title_level, title, '<' * title_level)
                if self.displayInfoLevel is True:
                    title = '{}\t{}'.format(infoLevel, title)
                print(title)
                if only_title is True:
                    return

            if self.displayInfoLevel is True:
                lines = self.pprint.pformat(msg).split('\n')
                for line in lines:
                    print('{}\t{}'.format(infoLevel, line))
            else:
                self.pprint.pprint(msg)

    def warning(self, msg, verbose_level=0, title=None, only_title=False, title_level=None, infoLevel='Warn'):
        self.cprint(msg, verbose_level, title, only_title, title_level, infoLevel)

    def error(self, msg, verbose_level=0, title=None, only_title=False, title_level=None, infoLevel='Error'):
        self.cprint(msg, verbose_level, title, only_title, title_level, infoLevel)

    def title(self, title, verbose_level=0):
        self.cprint('', verbose_level, title, True)

    def title1(self, title, verbose_level=0,):
        self.cprint('', verbose_level, title, True, self.title_level)

    def title2(self, title, verbose_level=0,):
        self.cprint('', verbose_level, title, True, int(self.title_level/3*2))

    def title3(self, title, verbose_level=0,):
        self.cprint('', verbose_level, title, True, int(self.title_level/3))


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

import re
from unidecode import unidecode

# class Search:
#     def __init__(self, flag="unidecode", verbose=0):
#         self.flag = flag # ["unidecode", "ignoreCase", others = no flag]
#         if self.flag == "unidecode":
#             from unidecode import unidecode
#         self.partialMatch = True
#         self.partialExclude = False
#         self.lazyWildcard = ' '
#         self.exclusionChar = '!'
#         self.splitItems = ','
#         self.verbose = verbose
#
#     def searchText(self, searchTxt, matchTxt):
#         if self.flag in ["unidecode", "ignoreCase"]:
#             result = re.search(searchTxt, matchTxt, flags=re.IGNORECASE)
#         else:
#             result = re.search(searchTxt, matchTxt)
#         customPrint([searchTxt, matchTxt, result], 1)
#         if result:
#             if self.partialMatch is False:
#                 if result.end() - result.start() != len(searchTxt):
#                     return None
#             return True
#         return None
#
#     def searchTextInList(self, searchTxt, matchTxtList, exclusion=False):
#         #search text in list of text, a single exclusion match cancels everything
#         if self.flag == "unidecode":
#             searchTxt = unidecode(searchTxt)
#         match = None
#         for matchTxt in matchTxtList:
#             result = self.searchText(searchTxt, matchTxt)
#             if result is True:
#                 if exclusion is True:
#                     return False
#                 else:
#                     match = True
#         return match
#
#     def searchTextPartsInItemMatchList(self, searchTextParts, matchItem):
#         #search a whole item split in parts against item with multiple matching name (name list)
#         if isinstance(matchItem, str):
#             matchItem = [matchItem]
#         match = False
#         for textPart, exclusion in searchTextParts:
#             result = self.searchTextInList(textPart, matchItem)
#             if result is True:
#                 if exclusion is True:
#                     return False
#                 else:
#                     match = True
#         return match
#
#     def splitSearchItemToParts(self, searchItem):
#         itemParts = searchItem.split(self.lazyWildcard)
#         idx = 0
#         for item in itemParts:
#             item = item.strip()
#             exclusion = False
#             if item.startswith(self.exclusionChar):
#                 item = item[1:]
#                 exclusion = True
#             itemParts[idx] = (item, exclusion)
#             idx += 1
#         return itemParts
#
#     def splitWholeSearchToItemParts(self, wholeSearch):
#         if isinstance(wholeSearch, str):
#             searchedItems = [x.strip() for x in wholeSearch.split(self.splitItems)]
#         else:
#             searchedItems = wholeSearch
#         searchedItems = [self.splitSearchItemToParts(item) for item in searchedItems]
#         return searchedItems
#
#     def matchEachItemToWholeSearch(self, itemMatchList, wholeSearch, itemMatchIsObject=False, itemMatchAttribute='match_name'):
#         """
#         TODO
#         Refaire avec pour chaque objet 4 statut possible : gardé, non selectionné, exclus, inconnu
#         les 3 premiers statuts sont des resultats de recherche
#         le dernier est attribué lorsqu une autre recherche sur un autre attribut l'a deja gardé ou exclus
#         ne pas refaire la recherche, tant que ce n'est pas necessaire pour le statut inconnu
#         pour le statut final, il suffit d additioner les resultats de chaque recherche sur chaque objet
#
#         ie:
#         recherche 1: nom = 'tata'
#         {'tata' = True, 'toto'= 0, 'tutu'=0}
#         recherche 2: nom != 'tutu'
#         {'tata' = None, 'toto' = 0, 'tutu' = False}
#         resultat:
#         {'tata' = True, }
#         """
#         searchedItems = self.splitWholeSearchToItemParts(wholeSearch)
#         # print(searchedItems)
#         resultList = []
#         for itemMatch in itemMatchList:
#             match = False
#             for searchedItem in searchedItems:
#                 if itemMatchIsObject is False:
#                     result = self.searchTextPartsInItemMatchList(searchedItem, itemMatch)
#                 else:
#                     matchAttribute = getattr(itemMatch, itemMatchAttribute)
#                     # print('match is object:', matchAttribute)
#                     result = self.searchTextPartsInItemMatchList(searchedItem, matchAttribute)
#                 if result is True:
#                     match = True
#                     print("found", itemMatch.name)
#                     break
#             resultList.append((itemMatch, match))
#         print('resultlist:', resultList)
#         return resultList
def searchText(pattern, text, flag="unidecode", partialMatch=True):
    """ OK
    Process de recherche de string a string
    peut ignoreCase ou non et/ou necessiter un match Total Vs match partiel
    return True si match / None sinon
    utilisée par la class Search
    """
    if not isinstance(text, str):
        print(f'matchTxt is not a string {text}')
        text = str(text)
    if flag in ["unidecode", "ignoreCase"]:
        result = re.search(pattern, text, flags=re.IGNORECASE)
    else:
        result = re.search(pattern, text)
    customPrint([pattern, text, result], 1)
    if result:
        if partialMatch is False:
            if result.end() - result.start() != len(pattern):
                return None
        return True
    return None


class Search:
    def __init__(self, flag="unidecode", verbose=0):
        self.flag = flag # ["unidecode", "ignoreCase", others = no flag]
        if self.flag == "unidecode":
            from unidecode import unidecode
        self.partialMatch = True
        self.lazyWildcard = ' '
        self.exclusionChar = '!'
        self.splitItems = ','
        self.verbose = verbose
        self.searches = {}



    class SearchValueInObjList:
        def __init__(self, searchedString, objList, attr, exclusion=False, flag="unidecode", verbose=0):
            """
            Cette classe permet de faire une recherche d'un attribut dans une liste d'objets
            La recherche peut contenir des wildcard
            ie :
            Search(Recette.name, crepes au chocolat)
            recherche stockee pour chaque obj
            d autres pattern (autres instances de cette classe) serviront pour calculer le resultat de recherche final
            1 exclusion annule toute la recherche
            l'exclusion exclue que la part juxtaposee, et non tout !
            """
            self.searchedString = searchedString
            self.searchedPartsList = None #[(searchedValue, bool(exclusion)), ...]
            self.objList = objList
            self.attr = attr
            self.resultList = None
            self.flag = flag # ["unidecode", "ignoreCase", others = no flag]
            if self.flag == "unidecode":
                from unidecode import unidecode
            self.partialMatch = True
            self.lazyWildcard = ' '
            self.exclusionChar = '!'
            self.exclusion = exclusion
            self.splitItems = ','
            self.verbose = verbose

            if self.status == None:
                self.breakToSearchParts()
                self.searchElementInObjList()



        class ObjSearchPartResult:
            """
            Stocker les parametres et le resultat de la recherche
            Maj du result si omit a la creation possible
            """
            def __init__(self, searchedObj, searchedPart, exclusion, result):
                self.result = result  # [1 0 -1 None]
                self.searchedObj = searchedObj
                self.searchedPart = searchedPart
                self.exclusion = exclusion

            def update(self, force=False):
                if self.result is None or force is True:
                    result = searchText(self.searchedPart, self.searchedObj.__dict__[self.attr])
                    if result is True:
                        if self.exclusion is True:
                            self.result = -1
                        else:
                            self.result = 1
                    else:
                        self.result = 0

        class ObjSearchResult:
            """
            !!self.searchedPartList doit avoir les exclusions en debut de liste !!
            Stocker le resultat d'un element ou resultat final de la recherche pour un objet
            stocker les differents objsearchpartresult / objsearchresult ac les resultats
            recomplier si besoin les resultat a partir d objet mis a jour
            isElementSearch : if True one exclusion translates as whole object excluded
            if False each result only adds positive results, exclusions are not taken to account
            """
            # TODO
            def __init__(self, searchedObj, searchedPartList, resultList, isElementSearch):
                self.searchedObj = searchedObj
                self.searchedPartList = searchedPartList
                self.resultList = resultList
                self.isElementSearch = isElementSearch
                self.result = None #[1, 0, None]

            def update(self, force=False):
                """ OK
                Updates results
                """
                for result in self.resultList:
                    result.update(force)

            def addSearches(self, additionalSearchedPartList, additionalResultList):
                #TODO
                """
                do search, reorder / append to searchPartList
                append results
                y a t il besoin d update les anciennes recherches ? update si compile un element, pas dupdate interelement
                """
                #reorder searchedPartList !!!
                self.update(True)
                return

            def computeResults(self):
                notProcessed = []
                for resultItem in self.resultList:
                    if self.isElementSearch:
                        if resultItem.result == -1:
                            self.result = 0
                            break
                    if resultItem.result == 0:
                        notProcessed.append(resultItem)
                    if resultItem.result == 1:
                        self.result = 1
                        break
                if self.result not in [-1, 1] and len(notProcessed) != 0:
                    for resultItem in notProcessed:
                        resultItem.update()
                    self.computeResults()

                if self.result not in [-1, 1]:
                    self.result = 0




        def breakToSearchParts(self):
            """ OK
            Convertir la ElementSearch en parts et set des exclusions en premier
            ie:
            crepes sucre !oeuf -> [('oeuf', True), ('crepes', False), ('sucre', False)]
            """
            def doSplitToParts():
                """
                returns tupple list  [(searchedPart, exclusion), ...]
                """
                if isinstance(self.searchedString, str):
                    itemParts = self.searchedString.split(self.lazyWildcard)
                else:
                    itemParts = self.searchedString
                idx = 0
                for item in itemParts:
                    item = item.strip()
                    exclusion = False
                    if item.startswith(self.exclusionChar):
                        item = item[1:]
                        exclusion = True
                    itemParts[idx] = (item, exclusion)
                    idx += 1
                return itemParts

            def reorderSearchParts(searchParts):
                """
                reorder searchParts with exclusion parts first
                """
                reorderedList = []
                for part in list(searchParts):
                    if part[1] is True:
                        reorderedList.append(part)
                        searchParts.remove(part)
                reorderedList.extend(searchParts)
                return reorderedList

            if isinstance(self.searchedString, str):
                searchParts = doSplitToParts()
            if isinstance(self.searchedString, list):
                if len(self.searchedString[0]) and type(self.searchedString[0]).__name__ == 'str':
                    searchParts = doSplitToParts()

            searchParts = reorderSearchParts(searchParts)
            self.searchedPartsList = searchParts

        def searchElementInObjList(self):
            # search text in list of text, a single exclusion match cancels everything
            """
            effectuer une recherche pour chaque objet de la liste. stocker le resultat
            True : match positif
            0 : pas de match
            False : match exclusion
            None : recherche non effectuee
            sets self.resultList to:
            [ObjSearchPartResult(obj, part, result), ...]
            """
            elementResultList = []
            for searchedObj in self.objList:
                resultList = []
                resultState = None
                for searchedPart in self.searchedPartsList:
                    exclusion = searchedPart[1]
                    if resultState == -1 or resultState == 1:
                        resultObj = self.ObjSearchPartResult(searchedPart[0], searchedObj, exclusion, None)
                        resultList.append(resultObj)
                        continue
                    result = searchText(searchedPart[0], searchedObj.__dict__[self.attr])
                    if result is True:
                        resultState = 1
                        if exclusion is True: #exclusion de la part
                            resultState = -1
                    else:
                        resultState = 0
                    resultObj = self.ObjSearchPartResult(searchedPart[0], searchedObj, exclusion, resultState)
                    resultList.append(resultObj)

                objResult = self.ObjSearchResult(searchedObj, self.searchedPartsList, resultList)
                elementResultList.append(objResult)
            self.resultList = elementResultList


    ###############
    # Old Used in recette
    ###############

    def searchText(self, searchTxt, matchTxt):
        if self.flag in ["unidecode", "ignoreCase"]:
            result = re.search(searchTxt, matchTxt, flags=re.IGNORECASE)
        else:
            result = re.search(searchTxt, matchTxt)
        customPrint([searchTxt, matchTxt, result], 1)
        if result:
            if self.partialMatch is False:
                if result.end() - result.start() != len(searchTxt):
                    return None
            return True
        return None

    def searchTextInList(self, searchTxt, matchTxtList, exclusion=False):
        #search text in list of text, a single exclusion match cancels everything
        if self.flag == "unidecode":
            searchTxt = unidecode(searchTxt)
        match = None
        for matchTxt in matchTxtList:
            result = self.searchText(searchTxt, matchTxt)
            if result is True:
                if exclusion is True:
                    return False
                else:
                    match = True
        return match

    def searchTextPartsInItemMatchList(self, searchTextParts, matchItem):
        #search a whole item split in parts against item with multiple matching name (name list)
        if isinstance(matchItem, str):
            matchItem = [matchItem]
        match = False
        for textPart, exclusion in searchTextParts:
            result = self.searchTextInList(textPart, matchItem)
            if result is True:
                if exclusion is True:
                    return False
                else:
                    match = True
        return match

    def splitSearchItemToParts(self, searchItem):
        itemParts = searchItem.split(self.lazyWildcard)
        idx = 0
        for item in itemParts:
            item = item.strip()
            exclusion = False
            if item.startswith(self.exclusionChar):
                item = item[1:]
                exclusion = True
            itemParts[idx] = (item, exclusion)
            idx += 1
        return itemParts

    def splitWholeSearchToItemParts(self, wholeSearch):
        if isinstance(wholeSearch, str):
            searchedItems = [x.strip() for x in wholeSearch.split(self.splitItems)]
        else:
            searchedItems = wholeSearch
        searchedItems = [self.splitSearchItemToParts(item) for item in searchedItems]
        return searchedItems

    def matchEachItemToWholeSearch(self, itemMatchList, wholeSearch, itemMatchIsObject=False, itemMatchAttribute='match_name'):
        searchedItems = self.splitWholeSearchToItemParts(wholeSearch)
        # print(searchedItems)
        resultList = []
        for itemMatch in itemMatchList:
            match = False
            for searchedItem in searchedItems:
                if itemMatchIsObject is False:
                    result = self.searchTextPartsInItemMatchList(searchedItem, itemMatch)
                else:
                    matchAttribute = getattr(itemMatch, itemMatchAttribute)
                    # print('match is object:', matchAttribute)
                    result = self.searchTextPartsInItemMatchList(searchedItem, matchAttribute)
                if result is True:
                    match = True
                    print("found", itemMatch.name)
                    break
            resultList.append((itemMatch, match))
        print('resultlist:', resultList)
        return resultList
