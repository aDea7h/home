from time import strptime, strftime
import pprint
import os
import shutil
import warnings
import inspect
import re
from unidecode import unidecode

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
def searchText(pattern, text, flag=["unidecode", "ignoreCase"]):
    """ OK
    Process de recherche de string a string
    peut ignoreCase et unidecode ou non. pas de partialMatch possible ici
    return True si match / None sinon
    utilisée par la class Search
    """
    if not isinstance(text, str):
        text = str(text)
        warnings.warn('searchText() text should be a string (converted automatically)')
    if 'unidecode' in flag:
        text = unidecode(text)
        pattern = unidecode(pattern)
    if "ignoreCase" in flag:
        result = re.search(pattern, text, flags=re.IGNORECASE)
    else:
        result = re.search(pattern, text)
    customPrint([pattern, text, result], 1)
    if result:
        return True
    return None


class SearchPart:
    def __init__(self, searchedPart, textStack, exclusion=False):
        """
        OK
        cette classe recherche dans une seul part si il y a un match dans le textStack
        ne gere pas les pattern avec lazy wildcard (ie: 'par ial')
        Stocker les parametres et le resultat de la recherche
        Maj du result si omit a la creation possible ou si maj forcee
        1 : resultat positif
        0 : resultat negatif
        -1: resultat exclus
        None: pas de resultat
        """
        self.result = None  # [1 0 -1 None]
        self.searchedPart = searchedPart
        self.textStack = textStack
        self.exclusion = exclusion
        self.update()

    def update(self, force=False):
        if self.result is None or force is True:
            # print(f'-- textStack : {self.textStack}')
            result = searchText(self.searchedPart, self.textStack)
            # print(result, self.searchedPart, self.textStack)
            if result is True:
                if self.exclusion is True:
                    self.result = -1
                else:
                    self.result = 1
            else:
                self.result = 0
        return result


class Search:
    def __init__(self, flag="unidecode", verbose=0):
        """
        memoriser le texte recherche dans cette classe, car s il change ca invalide tout l historique de recherche

        """
        self.flag = flag  # ["unidecode", "ignoreCase", others = no flag]
        self.partialMatch = True
        self.lazyWildcard = ' '
        self.exclusionChar = '!'
        self.splitItems = ',' #TODO remove
        self.splitGroups = ','
        self.verbose = verbose
        self.searches = {}

    def newSearchPattern(self, searchedPattern, stack):
        newSearchPattern = self.SearchGroupParts(searchedPattern, stack, self)
        #store ??
        return newSearchPattern

    def newSearchInObj(self, obj, searches, mode='linearExclusion'):
        newSearchInObj = self.SearchInObj(obj, searches, self, mode)
        #store ??
        return newSearchInObj

    # def newSearchPattern(self, pattern, stack, mode='linearExclusion'):
    #     newSearchPattern = self.SearchInObj()


    class SearchGroupParts:
        def __init__(self, searchedPattern, stack, outer, split=True):
            """
            cette classe effectue une recherche de group de parts (pattern splitte) (potentiellement composee de wildcard)
            le group sera divise en plusieurs part pour les wildcards
            plusieurs SearchPart class sont necessaire pour aggreger le resultat
            effectuer toutes les exclusions en premier, 1 exclusion annule toute la recherche
            le text cherche peut etre une str, list ou une classe avec un attribut specifie(sinon __name__)
            si la recherche est une list elle est traitee dans son ensemble, une exclusion rejette la totalite de la liste
            """
            # TODO
            # Test ConformStackToSearch
            # recuperer une stack deja conformee d avant
            # ordre de match des part doit etre conservee >> 're po' patch pas avec poivre (retourner l index de matche, le suivant doit etre superieur)

            self.outer = outer
            self.lazyWildcard = self.outer.lazyWildcard
            self.exclusionChar = self.outer.exclusionChar
            self.searchedPattern = searchedPattern
            self.stack = stack
            self.split = split
            self.searchedStackList = None
            self.searchParts = None
            self.result = None

            self.conformStackToSearch()
            print(f'conformedStackSearched : {self.searchedStackList}')
            self.splitPatternToParts()
            print(f'pattern split : {self.searchParts}')
            self.search()


        def conformStackToSearch(self):
            """
            NOT TESTED
            Permet de convertir le stack d input en une liste de string utilisable pour la recherche
            inputs:
            (obj: obj, str: attribute) obj attribute containing a String or searchable content
            'str', ['str', ]
            """
            print(f'conformStackSearched input : {self.stack}')
            searchedStackList = []
            if type(self.stack).__name__ not in ['tuple', 'list']:
                self.stack = [self.stack]

            for stackItem in self.stack:
                if isinstance(stackItem, str):
                    searchedStackList.append(stackItem)
                else:
                    try:
                        if len(stackItem) == 2: # is an object stored as (obj: obj, str: attribute)
                            try:
                                attribute = stackItem[0].__dict__[stackItem[1]]
                                if not isinstance(attribute, str):
                                    warnings.warn("SearchPattern: searching inside an object attribute should be a string: implicit conversion")
                                    attribute = str(attribute)
                                searchedStackList.append(attribute)
                            except:
                                warnings.warn(f'SearchPattern: unable to search into {stackItem}')
                        else:
                            warnings.warn(
                                f'SearchPattern: searched stack should be a string or an (object, attribute) pair')
                    except:
                        warnings.warn(f'SearchPattern: searched stack should be a string or an (object, attribute) pair')

            print(f'out self.searchedStackList : {searchedStackList}')
            self.searchedStackList = searchedStackList

        def splitPatternToParts(self):
            """
            Non teste
            Convertir le searchedPattern en parts et set des exclusions en premier et en ordre alphabetique
            accepte aussi les searchpattern deja splittes [('search', exclusion)]
            ie:
            po !ron -> [('ron', True), ('po', False)] => match poireau mais pas poivron
            """
            def partProcess(part):
                part = part.strip()
                exclusion = False
                if part.startswith(self.exclusionChar):
                    part = part[1:]
                    exclusion = True
                return (part, exclusion)

            def partListProcess(partList):
                idx = 0
                for item in partList:
                    partList[idx] = partProcess(item)
                    idx += 1
                return partList

            def doSplitToParts():
                """
                returns tupple list  [(searchedPart, exclusion), ...]
                """
                if self.split is True:
                    itemParts = self.searchedPattern.split(self.lazyWildcard)
                else:
                    itemParts = [self.searchedPattern]
                return partListProcess(itemParts)

            def reorderSearchParts(searchParts):
                """
                reorder searchParts with exclusion parts first
                """
                reorderedList = []
                # for part in sorted(searchParts, key=lambda x: x[0]):
                #     if part[1] is True:
                #         reorderedList.append(part)
                #         searchParts.remove(part)
                # reorderedList.extend(searchParts)
                idx = 0
                for part in list(searchParts):
                    if part[1] is True:
                        reorderedList.append(searchParts.pop(idx))
                    idx += 1
                reorderedList.extend(searchParts)
                return reorderedList

            if isinstance(self.searchedPattern, str):  # crepes sucre !oeuf
                searchParts = doSplitToParts()
            else:
                if isinstance(self.searchedPattern, list):  # soit [oeuf, crepes...] soit [('oeuf', True), ('crepes', False), ('sucre', False)]
                    if len(self.searchedPattern[0]) == 2 and isinstance(self.searchedPattern[0][0], str) and isinstance(self.searchedPattern[0][1], bool):
                        searchParts = self.searchedPattern
                    else: # [oeuf crepes]
                        searchParts = partListProcess(self.searchedPattern)
                else:
                    warnings.warn(f"Wrong searchedPattern found : '{self.searchedPattern}'")
                    return []
            self.searchParts = reorderSearchParts(searchParts)

        def search(self):
            """
            # effectuer la recherche pour chaque part sur la liste searchedStackList
            # annuler la recherche part suivante si exclusion match
            # un match positif valide le resultat vu que les exclusions ont deja ete faites (sort de la liste)
            """
            finalResult = None
            for part in self.searchParts:
                if finalResult is not None:
                    break
                print(f'-->> search launch with {part[0]} and {part[1]}')
                for text in self.searchedStackList:
                    print(f'-> search text: {text}' )
                    searchPartObj = SearchPart(part[0], text, part[1])
                    print(f'result : {searchPartObj.result}')
                    if searchPartObj.result in [-1, 1]:
                        finalResult = searchPartObj.result
                        print(f'break search in stack {finalResult}')
                        break
            if finalResult is None:
                finalResult = 0
            self.result = finalResult


    class SearchInObj:
        def __init__(self, obj, searches, outer, mode='linearExclusion'):
            """
            Cette classe permet de faire une recherche complete dans un ou plusieurs attribut d'un seul objet
            le resultat de chaque attribut recherche est stocke avec ses parametres dans un SearchPattern class
            ###
            definir des modes de calcul de resultat final (linear exclusion, add, strict exclusion)
                - linear exclusion : le resultat de la premiere recherche done la source de la suivante
                - add : chaque recherche est effectuee, tous les resultats positifs sont aggreges
                - strict exclusion : add mais chaque exclusion interdit l ajout par une recherche
            ###
            La recherche peut contenir des wildcard et un override d exclusion (inverse le resultat de la recherche)
            ie : searches = {'attr': ['searchedStr', bool exclusionOverride, split, ('objAttrName')], ...}
            ie : searches = {'attr': [['searchedStr', 'searchStr2', ...], exclusionOverride, split], ...}

            Resultats aggrege:
                1 : resultat positif
                0 : resultat negatif
                -1: resultat exclus
                None: pas de resultat
            """
            """
            #TODO
            Comment updater
            Comment store les resultats
            si stack is updated > reinit tout
            """

            self.allSearches = {}
            self.obj = obj
            self.outer = outer
            self.mode = mode
            self.result = None

            self.search(searches)

        def splitSearchPatternToGroups(self, searchPattern):
            print('split', searchPattern)
            if isinstance(searchPattern, list) is True:
                if isinstance(searchPattern[0], str) is True:
                    searchGroups = [group.strip() for group in searchPattern]
                else:
                    searchGroups = searchPattern
            else: #string
                searchGroups = searchPattern.split(self.outer.splitGroups)
                searchGroups = [group.strip() for group in searchGroups]
            print('splitted:', searchGroups)
            return searchGroups

        def searchLinearExclusion(self, searches):
            """
            ajouter / maj des recherches deja effectuees
            update des resultats stockes dans allsearches
            Ne pas updater l ordre de recherche > affecte le resultat (linear parent search > child search > subchild, add or multiply)
            stocker les resultats
            #TODO
            conform stack dans search in obj
            """
            def computePatternResult(groupList):
                """Pattern result of multiple groups is the maximum, if a group excludes and another adds it, it should be kept"""
                return max(groupList)

            result = None
            for attrSearch in searches:
                # search = {'attr': ['searchedStr', exclusionOverride], } part list must be alphabeticaly sorted

                # TODO
                # split attrSearch to item list if needed
                # ie: match_name : 'poi on, roti' sera split en ['poi on', 'roti'] le lazywildcard viendra ensuite

                searchPattern, exclusion, split = searches[attrSearch]
                print(f'searchPattern, exclusion, split {searchPattern}, {exclusion}, {split}')
                if split is True:
                    searchGroups = self.splitSearchPatternToGroups(searchPattern)
                else:
                    searchGroups = [searchPattern]
                groupResults = []
                for group in searchGroups:
                    groupSearchName = f'{attrSearch}.{int(exclusion)}.{int(split)}.{group}'
                    if groupSearchName in self.allSearches:
                        if [group, exclusion, split] == self.allSearches[groupSearchName][:3]:
                            # Si recherche deja existante > la recuperer
                            resultObj = self.allSearches[groupSearchName][3]
                            print(f'found existing search: {group} : {groupSearchName}')
                        else:
                            # update needed
                            resultObj = self.outer.SearchGroupParts(group, self.obj.__dict__[attrSearch], self.outer, split)
                            self.allSearches[groupSearchName] = [group, exclusion, split, resultObj]
                    else:
                        print(f'new search: {group} : obj.{attrSearch} = {self.obj.__dict__[attrSearch]}')
                        resultObj = self.outer.SearchGroupParts(group, self.obj.__dict__[attrSearch], self.outer, split)
                        # resultObj = self.outer.SearchGroupParts(self.obj.__dict__[attrSearch], group, self.outer, split)
                        self.allSearches[groupSearchName] = [group, exclusion, split, resultObj]
                    groupResults.append(resultObj.result)
                result = computePatternResult(groupResults)
                print(f'search results: {group} : {result}')
                if result == -1:
                    """first exclusion on item, cancels all other researches"""
                    break
                if result == 1 and exclusion is True:
                    result = -1
                    break

            self.result = result
            return result

        def search(self, searches, update=False):
            """switch search algo based on mode
            TODO other modes
            TODO UPDATES
            """
            if self.mode == 'linearExclusion':
                self.searchLinearExclusion(searches)
            else:
                raise Exception('Unknown search mode')











    class SearchValueInObjList:
        def __init__(self, searches, obj, flag="unidecode", verbose=0):
            """
            Cette classe permet de faire une recherche dans un ou plusieurs attribut dans un seul objet
            le resultat de chaque bout de recherche est stocke avec ses parametres
            La recherche peut contenir des wildcard et un override d exclusion
            ie : searches = {'attr': ['searchedStr', bool exclusionOverride], }
            ie : searches = {'attr': [['searchedStr', 'searchStr2'], exclusionOverride], }
            d autres pattern (autres instances de cette classe) serviront pour calculer le resultat de recherche final
            1 exclusion annule toute la recherche
            l'exclusion exclue que la part juxtaposee, et non tout !
            """
            self.searches = searches
            self.searchedPartsList = None #[(searchedValue, bool(exclusion)), ...]
            self.obj = obj
            self.attr = attr
            self.result = None
            self.flag = flag  # ["unidecode", "ignoreCase", others = no flag]
            # if self.flag == "unidecode":
            #     from unidecode import unidecode
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
            Maj du result si omit a la creation possible ou si maj forcee
            1 : resultat positif
            0 : resultat negatif
            -1: resultat exclus
            None: pas de resultat
            """
            def __init__(self, attrNameValue, searchedPart, exclusion, result):
                self.result = result  # [1 0 -1 None]
                self.attrNameValue = attrNameValue
                self.searchedPart = searchedPart
                self.exclusion = exclusion

            def update(self, force=False):
                if self.result is None or force is True:
                    # result = searchText(self.searchedPart, self.searchedObj.__dict__[self.attr])
                    result = searchText(self.searchedPart, self.attrNameValue)
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
                    if part[1] is False:
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
            effectuer une recherche sur l'objet. stocker le resultat
            True : match positif
            0 : pas de match
            False : match exclusion
            None : recherche non effectuee
            sets self.resultList to:
            [ObjSearchPartResult(obj, part, result), ...]
            """
            resultList = []
            resultState = None
            for searchedPart in self.searchedPartsList:
                exclusion = searchedPart[1]
                if resultState == -1 or resultState == 1:
                    resultObj = self.ObjSearchPartResult(searchedPart[0], self.obj, exclusion, None)
                    resultList.append(resultObj)
                    continue
                result = searchText(searchedPart[0], self.obj.__dict__[self.attr])
                if result is True:
                    resultState = 1
                    if exclusion is True: #exclusion de la part
                        resultState = -1
                else:
                    resultState = 0
                resultObj = self.ObjSearchPartResult(searchedPart[0], self.obj, exclusion, resultState)
                resultList.append(resultObj)

            self.result = self.ObjSearchResult(self.obj, self.searchedPartsList, resultList)

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
