"""
object recette temps / temsp repos /  difficulte.
Lib de recette avec base / variants et favoris / rqngement categories - tags
object ingredient: de saison / local / info culinaire / vege / viande / dispo tt le temps vs a acheter
planification semaine repas equilibré match de recette (proposer ingredients pour equilibre)
recherche
parser de fichier
suggestion fn d ingredients frigo / manque repas equi historique precedent
score climat
recettes a tester
proposer vieilles recettes de ts les jours
"""
import os.path
import sys

import pandas
import odf
import time
import numpy as np
from unidecode import unidecode
import tools
import database
from incrementalBackup import incrementalBackup
from collections import defaultdict
from bigtree import DAGNode, find, preorder_iter
import copy
global prefs


def removeNans(dict):
    def removeNan(val):
        if pandas.isna(val) is True:
            return None
        else:
            return val

    for key in dict:
        dict[key] = removeNan(dict[key])
    return dict

def splitValueToList(value):
    if value is None:
        return []
    if isinstance(value, int) is True:
        return [value]
    if isinstance(value, list)  is True:
        return value
    if value.startswith('[') and value.endswith(']'):
        return eval(value)
    return [x.strip() for x in value.split(',')]

def attrListToAttrDict(attrList, objType):
    if objType == 'Ingredient':
        if len(attrList) != 13:
            raise Exception("Db data doesn't match attributes created")
        attrs = {
            'id':  attrList[0],
            'name':  attrList[1],
            'category':  attrList[2],
            'family':  attrList[3],
            'match_name':  attrList[4],
            'vegan': attrList[5],
            'vegetarian': attrList[6],
            'meat_replacement': attrList[7],
            'protein': attrList[8],
            'always_available': attrList[9],
            'special': attrList[10],
            'season': attrList[11],
            'local': attrList[12],
        }
    elif objType == 'Recipe':
        if len(attrList) != 18:
            print(len(attrList), attrList)
            raise Exception("Db data doesn't match attributes created")
        attrs = {
            'id': attrList[0],
            'name':  attrList[1],
            'match_name':  attrList[2],
            'category_id':  attrList[3],
            'type': attrList[4],
            'origin': attrList[5],
            'tags': attrList[6],
            'ingredients': attrList[7],
            'before_recipe': attrList[8],
            'recipe': attrList[9],
            'suggestion': attrList[10],
            'notes': attrList[11],
            'files': attrList[12],
            'cooking_time': attrList[13],
            'preparation_time': attrList[14],
            'is_best_reheated': attrList[15],
            'rating': attrList[16],
            'is_wip': attrList[17],
        }
    elif objType == 'Stock':
        if len(attrList) > 9:
            raise Exception("Db data doesn't match attributes created")
        attrs = {
            'id': attrList[0],
            'name': attrList[1],
            'category': attrList[2],
            'servingsQuantity': attrList[3],
            'servingsUnit': attrList[4],
            'nbr': attrList[5],
            'dateName': attrList[6],
            'dateIsExpirationDate': bool(attrList[7]),
            'ingredients': attrList[8],
        }
    else:
        raise Exception("Unknown Attribute list type")
    return attrs

def convertIngredientIdToObj(path, ingredients): #TODO
    ingredientList = []
    print(ingredients)
    ingredients = eval(ingredients) ### Ingredients were stored in str([ing, ing])
    for ingredient in ingredients:
        className, id = ingredient.split('.')
        id = int(id)
        #TODO retrieve content from id
        attrs = {}
        if className == 'Ingredient':
            data = database.getIngredientFromId(path, id)
            attrs = attrListToAttrDict(data, className)
            obj = Ingredient(attrs)
        elif className == 'Recipe':
            data = database.getRecipeFromId(path, id)
            attrs = attrListToAttrDict(data, className)
            obj = Recipe(attrs)
        else:
            raise Exception("Unknown ingredient stored {}.{}".format(ingredient, ingredient.name))
        print('recreated ingredient:')
        print(obj.__dict__())
        ingredientList.append(obj)
    return ingredientList

def checkFilePath(path):
    if os.path.exists(path) is False:
        raise Exception('File Does not exists : {}'.format(path))
    return True

def importExportDb(data, libPath):
    """"{'filePath': self.qtFilePath.text(),
             'db': self.qtDataCombo.currentText(),
             'mode': self.mode,
             'backup': self.qtMakeBackupChekbox.checkState()}"""
    print('importing from lib : {}'.format(libPath))
    if data['db'] == 'Ingredients':
        db = IngredientList(libPath)
    elif data['db'] == 'Recipe':
        db = RecipeList(libPath)
    else:
        db = StockList(libPath)
    if data['mode'] == 'import':
        exists = checkFilePath(data['filePath'])
        print(exists)
        print(bool(data['backup']), data['backup'])
        if bool(data['backup']) is True:
            incrementalBackup(libPath)
        db.importDataFromFile(data['filePath'])
    else:
        db.exportDataToFile(data['filePath'])

def isVegan(obj):
    if type(obj.ingredients) in [type(None)] or len(obj.ingredients) == 0:
        return None
    vegan = True
    for ingredient in obj.ingredients:
        if isinstance(ingredient, str): # not an Ingredient class type returns None
            vegan = None
            break
        if ingredient.vegan is False:
            vegan = False
            break
    # print('is vegan : '+str(vegan))
    return vegan

def copyIngredientObj(ingredientObjTmp, ingredientObj):
    for attr in ingredientObjTmp.__dict__.keys():
        if attr in ['size', 'qtItem']:
            continue
        ingredientObjTmp.__dict__[attr] = ingredientObj.__dict__[attr]
    # print('copy out : ', ingredientObjTmp.__dict__)
    return ingredientObjTmp

def copyRecipeObj(recipeObj):
    print('copy in ref : ', recipeObj.__dict__)
    recipeObjTmp = Recipe({'name': recipeObj.name}, False)
    print('copy in init : ', recipeObjTmp.__dict__)
    for attr in recipeObjTmp.__dict__.keys():
        if attr in ['qtItem', 'ingredients']:
            continue
        recipeObjTmp.__dict__[attr] = recipeObj.__dict__[attr]
    ingredientList = []
    for ingredient in recipeObj.ingredients:
        ingredientObjTmp = Ingredient({'name': ingredient.name}, False)
        ingredientList.append(copyIngredientObj(ingredientObjTmp, ingredient))
    recipeObjTmp.ingredients = ingredientList
    print('copy out : ', recipeObjTmp.__dict__)
    return recipeObjTmp


class Units:
    def __init__(self):
        self.name = 'g'
        self.nameList = ['g', 'kg', 'L', 'cL', 'u']

class Preferences:
    def __init__(self, libPath):
        global prefs
        prefs = self
        pathExists = os.path.exists(libPath)
        db = database.DB(libPath)
        if pathExists is False:
            db.create_db()

        dbPrefs = db.get_preferences()
        prefDict, self.idDict = self.conformFromDb(dbPrefs)
        self.__dict__.update(prefDict)

    def conformFromDb(self, dbPrefs):
        prefDict = {}
        prefId = {}
        for pref in dbPrefs:
            id = int(pref[0])
            prefName = pref[1]
            prefValue = pref[2]
            if pref[1] in ['recipe_origin', 'menu_meal_choices', 'menu_meal_composition']:
                prefValue = splitValueToList(prefValue)
            elif pref[1] in ['menu_generate_x_days', 'menu_nbr_vegetarian_meal', 'recipe_is_fast_time_max', 'recipe_slow_preparation_time_min', 'recipe_slow_cooking_time_min']:
                prefValue = int(prefValue)
            prefDict[prefName] = prefValue
            prefId[prefName] = id
        return prefDict, prefId


class Ingredient:
    def __init__(self, attrs, fullCreation=True):
        self.id = -1
        self.name = None
        self.category = None
        self.categoryId = None
        self.family = None
        self.match_name = []
        self.season = None
        self.local = False
        # self.nutritional_value = None  # lipids / glucids / vitamins / iron...
        # self.vegetarian = None
        self.vegan = None
        self.vegetarian = None
        self.meat_replacement = None
        self.protein = None
        self.always_available = None
        self.special = None
        self.is_bought = False
        self.aisle = None
        self.fullCreation = fullCreation

        attrs = self.conformAttrs(attrs)

        self.visible = True  # not stored in Db usefull ?
        self.size = 0  # not stored in Db (used by recipe for ingredient quantity)
        self.unit = Units()
        self.qtItem = []  #not stored in Db
        self.__dict__.update(attrs)

        if self.fullCreation:
            self.detectMatchNames(self.fullCreation)

    def detectMatchNames(self, processCategory=True):
        """clean"""
        mn = []
        for item in self.match_name:
            item = item.strip()
            if item == '' or len(item) == 1:
                continue
            mn.append(item)
        self.match_name = mn

        """add"""
        if self.category is not None and processCategory is True:
            cat = [x for x in self.category]
        else:
            cat = []
        if self.family is not None:
            fam = [x for x in self.family]
        else:
            fam = []
        if self.match_name is not None:
            match = [x for x in self.match_name]
        else:
            match = []
        for item in [self.name] + cat + fam + match:
            item = item.strip()
            if item == '':
                continue
            if item not in self.match_name:
                self.match_name.append(item)
            if unidecode(item).strip() not in self.match_name:
                self.match_name.append(unidecode(item).strip())

    def conformAttrs(self, attrs):
        attrs = removeNans(attrs)
        for key in attrs:
            if key in ['id']:
                attrs[key] = int(attrs[key])
            elif key in ['family', 'category', 'match_name']:
                attrs[key] = splitValueToList(attrs[key])
            elif key in ['visible', 'local', 'vegan', 'vegetarian', 'meat_replacement', 'always_available', 'special']:
                attrs[key] = bool(attrs[key])
        return attrs

    def __repr__(self):
        return(f'Ingredient({self.name})')

    def __str__(self):
        return f'I:{self.name}'

class IngredientList:
    def __init__(self, path='E:/Scripts/Python/Recette/recette liste.ods'):
        self.path = path
        self.ingredientList = []
        # self.ingredientDic = {}
        self.db = None
        self.ingredientTree = {}
        self.Search = tools.Search(flag='unidecode')
        if path[-4:] == '.ods':
            self.setupFromOds()
        else:
            self.setupFromDb()

    def setupFromOds(self):
        self.ingredientList = self.readOds(self.path)
        self.conformCategories()
        self.buildIngredientTree()

    def setupFromDb(self):
        self.ingredientList = self.readDb(self.path)
        self.conformCategories()
        self.buildIngredientTree()

    def readOds(self, path=None):
        if path is None:
            path = self.path
        if os.path.exists(path) is False:
            raise Exception('File not found')
        data = pandas.read_excel(path, engine='odf', sheet_name="Ingredients")

        ingredientList = []
        # ingredientDic = {}
        for i in range(data.index.stop):
            attrs = {}
            for col in data.columns:
                attrs[col] = data.at[i, col]
            ingredientObj = Ingredient(attrs, False)
            ingredientObj.categoryId = ingredientObj.category
            ingredientList.append(ingredientObj)
            # ingredientDic[ingredientObj.name] = ingredientObj
        return ingredientList

    def readDb(self, path):
        if path is None:
            path = self.path
        pathExists = os.path.exists(path)
        self.db = database.DB(path)
        if pathExists is False:
            self.db.create_db()
        ingredients = self.db.get_ingredients()

        ingredientList = []
        # ingredientDic = {}
        for ingredient in ingredients:
            attrs = attrListToAttrDict(ingredient, 'Ingredient')
            #TODO Conform data
            # if attrs['ingredients'] is not None:
            #     attrs['ingredients'] = convertIngredientIdToObj(path, attrs['ingredients'])
            ingredientObj = Ingredient(attrs, False)
            ingredientObj.categoryId = ingredientObj.category
            ingredientList.append(ingredientObj)
            # ingredientDic[ingredientObj.name] = ingredientObj

        return ingredientList

    def conformCategories(self):
        for ingredientObj in self.ingredientList:
            ingredientObj.categoryId = ingredientObj.category
            #returns list of names from object id
            ingredientObj.category = [x.name for x in self.ingredientList if x.id in ingredientObj.categoryId]
            # print(ingredientObj.name, ingredientObj.categoryId, ingredientObj.category)

            # TODO add category to ingredients matchname
            ingredientObj.detectMatchNames()

    def buildIngredientTree(self):

        # class Tree(defaultdict):
        #     def __init__(self, value=None):
        #         super(Tree, self).__init__(Tree)
        #         self.value = value
        #
        # def recursiveTreeBuild(ingredientName, path):
        #     ingredientObj = self.ingredientDic[ingredientName]
        #     path.append(ingredientObj.name)
        #     print(ingredientObj.category)
        #     if ingredientObj.category == []:
        #         self.ingredientTree[ingredientName] = {'ingredientObj': ingredientObj}
        #         ingredientObj.ParentDicKeys = None
        #     else:
        #         for category in ingredientObj.category:
        #             print(category)

        # self.ingredientTree = Tree()
        # print(self.ingredientDic)
        # path = []
        #ingredientTree = {'viande':{'mouton': {'mergez': {}}}
        #path = ['viande', 'mouton', 'mergez']

        rootNode = DAGNode('root', id=-1, obj=None)
        meatNode = DAGNode('meat', parents=[rootNode], id=-2, obj=Ingredient({'name': 'meat'}, False))
        vegetableNode = DAGNode('vegetable', parents=[rootNode], id=-3, obj=Ingredient({'name': 'vegetable'}, False))
        starchNode = DAGNode('starch', parents=[rootNode], id=-4, obj=Ingredient({'name': 'starch'}, False))
        otherNode = DAGNode('other', parents=[rootNode], id=-5, obj=Ingredient({'name': 'other'}, False))
        self.ingredientTree = rootNode
        # print('---->> ingredientObj creation')
        for ingredientObj in self.ingredientList:
            # recursiveTreeBuild(ingredientName, path)
            # ingredientObj = self.ingredientDic[ingredientName]
            ingredientObj.treeNode = DAGNode(ingredientObj.name, id=ingredientObj.id, obj=ingredientObj)
            # print(ingredientObj.name, ingredientObj.treeNode, ingredientObj)

        # print('---->> ingredientObj parent')
        for ingredientObj in self.ingredientList:
            if ingredientObj.category != []:
                parent = [x.treeNode for x in self.ingredientList if x.id in ingredientObj.categoryId]
            else:
                nodes = [meatNode, vegetableNode, starchNode, otherNode]
                titles = ['viande', 'légume', 'féculent', 'divers']
                parent = [nodes[titles.index(x)] for x in ingredientObj.family]
            ingredientObj.treeNode.parents = parent

    def returnParentCategoryObj(self, ingredientObj, category):
        categoryId = ingredientObj.categoryId[ingredientObj.category.index(category)]
        found = find(self.ingredientTree, lambda node: node.id == categoryId)
        print(found, found.obj)
        return found.obj

    def returnTreeAsList(self):
        return [node for node in preorder_iter(self.ingredientTree)]

    def returnCategories(self):
        pass

    def filterIngredients(self, filterText):
        filterText = filterText.strip()
        method = 1
        if method == 0:
            matchList = self.Search.matchEachItemToWholeSearch(self.ingredientList, filterText, True, 'match_name')
        elif method == 1:
            matchList = []
            search = {'match_name': [filterText, False, True]}
            print(f'-->> Ingredient Search Launch : {search}')
            # searches = {'attr': ['searchedStr', exclusionOverride, result], }
            for ingredientObj in self.ingredientList:
                if 'searches' not in ingredientObj.__dict__.keys():
                    if search == {}:
                        ingredientObj.searches = self.Search.newSearchInObj(ingredientObj, {})
                        ingredientObj.searches.result = 1
                    else:
                        ingredientObj.searches = self.Search.newSearchInObj(ingredientObj, search)
                else:
                    if search == {}:
                        ingredientObj.searches.result = 1
                    else:
                        ingredientObj.searches.search(search, True)
                result = ingredientObj.searches.result == 1
                # ie : searches = {'attr': ['searchedStr', bool exclusionOverride, split, ('objAttrName')], ...}
                print(f'------>> recipe result: {ingredientObj.searches} : {ingredientObj.searches.result} // {ingredientObj.searches.allSearches}')
                matchList.append([ingredientObj, result])

        return matchList

    def importDataFromFile(self, odsPath):
        ingredientList = self.readOds(odsPath)
        db = database.DB(self.path, {'backupDB':False})
        print("==> importing ingredient to db")
        print(self.path, odsPath)
        for ingredientObj in ingredientList:
            print(ingredientObj.name)
            #check existence
            # if ingredientObj.name in self.ingredientDic.keys():
            if ingredientObj.name in [x.name for x in self.ingredientList]:
                #update # TODO confirmation and display delta
                db.editIngredient(ingredientObj)
            else: #add
                db.addToIngredient(ingredientObj)

        db.backupDB = True

    def exportDataToFile(self, odsPath): #TODO
        return

    def exportDatasToDb(self, datas):
        # print(f'\n\n-->> export inputs: {datas}')
        ingredientObj = Ingredient(datas, True)
        ingredientObjTmp = Ingredient({'name':ingredientObj.name})
        ingredientObjTmp = copyIngredientObj(ingredientObjTmp, ingredientObj)
        if self.db is None:
            self.db = database.DB(self.path)
        if ingredientObj.id in [None, -1]:
            print('adding ingredient')
            self.db.addToIngredient(ingredientObjTmp)
        else:
            print('editing ingredient')
            self.db.editIngredient(ingredientObj)

    def reprocessMatchNames(self):
        self.db.backup()
        self.db.backupDB = False
        for ingredientObj in self.ingredientList:
            # print(f'old matchname for {ingredientObj.name} : {ingredientObj.match_name}')
            # l = copy.deepcopy(ingredientObj.match_name)
            # d = []
            ingredientObj.detectMatchNames()
            # print(f'new matchname for {ingredientObj.name} : {ingredientObj.match_name}')
            # for x in ingredientObj.match_name:
            #     if x not in l:
            #         d.append(x)
            # print(d)
            try:
                self.exportDatasToDb(ingredientObj.__dict__)
            except:
                raise Exception('error while exporting object')
        self.db.backupDB = True


class Recipe:
    def __init__(self, attrs={}, checkInit=True, ingredientList=[]):
        #recipe identity
        self.id = -1
        self.name = None
        self.match_name = []  # is a list
        self.category_id = None  # is a list
        self.type = None  # is a list
        self.origin = None  # is a list
        self.tags = None  # is a list
        #content
        self.ingredients = []  # is a list
        self.before_recipe = None
        self.recipe = None
        self.suggestion = None # is list of recipe and ingredients id and string mixed
        self.notes = None
        self.files = None  # is a list
        #meta
        self.cooking_time = None
        self.preparation_time = None
        self.is_best_reheated = None
        self.rating = -1
        self.is_wip = True
        self.is_bought = False
        self.is_leftover = False
        self.is_preprepared = False

        #calculated attribs
        self.category = None  # parent item label (is a list)
        self.special_ingredient = None # a single ingredient is a special one
        self.needs_before_prep = None # before_recipe is not empty
        self.total_time = None # preparation_time + cooking_time
        self.ui_speed = None # total_time is < as fast settings
        self.is_tested = None # rating = -1
        self.is_favorite = None # rating = 10
        self.error = None # not all ingredients are recognized (aka string); other ?
        self.thumbnail = None #if path to img
        self.is_favorite_icon = None

        # print("---->> raw ingredients : {}".format(attrs['ingredients']))
        # if 'ingredients' in attrs.keys():
        #     if isinstance(attrs['ingredients'], str) is True:
        #         print('-->Ingredients are Strings', attrs['ingredients'])
        #         attrs['ingredients'] = attrs['ingredients'].split(',')
        # print("kept ingredients : {}".format(attrs['ingredients']))
        attrs = removeNans(attrs)
        # attrs = splitList(attrs)
        print('raw_attrs', attrs)
        attrs = self.splitListAttrs(attrs)
        print('split attrs', attrs)
        self.__dict__.update(attrs)
        if self.type is None:
            self.type = ["Dish"]
        if self.match_name is None:
            self.match_name = []
        if checkInit is True:
            self.conformRecipeIngredients(ingredientList)
            self.computeAttrs()
        self.detectMatchNames()
        print("check ingredients for vegan: {}".format(self.ingredients))
        print(self.ingredients)
        # self.is_vegan = is_vegan(self)
        # self.computeRating()



    def computeRating(self):
        self.is_tested = True
        if(self.rating == -1):
            self.is_tested = False
            self.is_favorite = False
        elif(self.rating == 10):
            self.is_favorite = True
            self.rating = 5

    def needSpecialIngredient(self):
        for ingredient in self.ingredients:
            if isinstance(ingredient, Ingredient) is False:
                if ingredient in [[], None, '']:
                    continue
                return True
            if ingredient.special is True:
                return True
        return False

    def computeAttrs(self):
        self.is_vegan = isVegan(self)
        self.computeRating()
        self.special_ingredient = self.needSpecialIngredient()
        if self.cooking_time and self.preparation_time:
            self.total_time = self.cooking_time + self.preparation_time
        speed = None
        if self.total_time not in [0, None]:
            if self.preparation_time <= prefs.recipe_is_fast_time_max:
                speed = 'fast'
            elif self.preparation_time >= prefs.recipe_slow_preparation_time_min:
                speed = 'slow'
            elif self.cooking_time >= prefs.recipe_slow_cooking_time_min:
                speed = 'slow'
        self.ui_speed = speed

    def printObj(self):
        print('-->> {}'.format(self.name))
        print(self.__dict__)

    def splitListAttrs(self, attrs):
        for key in attrs:
            if key in ['match_name', 'category_id', 'type', 'origin', 'tags', 'ingredients', 'suggestion', 'files']:
                if isinstance(attrs[key], list) is False:
                    attrs[key] = splitValueToList(attrs[key])
        return attrs

    def conformRecipeIngredients(self, ingredientList): #TODO Bad replace ingredient
        def getIngredientObject(recipeIngredient):
            id = -1
            name = ''
            size = 0
            if isinstance(recipeIngredient, tuple):
                try:
                    id = int(recipeIngredient[0])
                    print('recipe ingredient is id  {} and size {}'.format(recipeIngredient[0], recipeIngredient[1]))
                except ValueError:
                    name = recipeIngredient[0]
                    print('recipe ingredient is name  {} and size {}'.format(recipeIngredient[0], recipeIngredient[1]))
                size = recipeIngredient[1]
            elif isinstance(recipeIngredient, Ingredient):
                print('recipe ingredient is object : ', recipeIngredient, recipeIngredient.name, recipeIngredient.size)
                return recipeIngredient
            else:
                print('recipe ingredient is string')
                name = unidecode(recipeIngredient).strip()
            attrs = {'id': id,
                    'name': name,
                    'size': size, }
            ingredientObjTmp = Ingredient(attrs, False)
            return ingredientObjTmp

        # def copyIngredientObj(ingredientObjTmp, ingredientObj):
        #     for attr in ingredientObjTmp.__dict__.keys():
        #         if attr in ['size', 'qtItem']:
        #             continue
        #         ingredientObjTmp.__dict__[attr] = ingredientObj.__dict__[attr]
        #     print('copy out : ', ingredientObjTmp.__dict__)
        #     return ingredientObjTmp

        def matchIngredientsById(ingredientObjTmp, ingredientList):
            for ingredientObj in ingredientList:
                if ingredientObjTmp.id == ingredientObj.id:
                    # newIngredientObj = copy.deepcopy(ingredientObj)
                    newIngredientObj = copyIngredientObj(ingredientObjTmp, ingredientObj)
                    # newIngredientObj.size = ingredientObjTmp.size
                    return True, newIngredientObj
            return False, ingredientObjTmp

        def matchIngredientsByString(ingredientObjTmp, ingredientList): #TODO what if multimatch (soja / mergez)
            for ingredientObj in ingredientList:
                if ingredientObjTmp.name in ingredientObj.match_name:
                    # newIngredientObj = copy.deepcopy(ingredientObj)
                    newIngredientObj = copyIngredientObj(ingredientObjTmp, ingredientObj)
                    # if ingredientObjTmp.size != 0:
                    #     newIngredientObj.size = ingredientObjTmp.size
                    return True, newIngredientObj
            return False, ingredientObjTmp


        idx = 0
        print('conforming Ingredients')
        print(self.ingredients, type(self.ingredients))
        print(ingredientList)
        if self.ingredients in [None, []]:
            print("No ingredients found for : {}".format(self.name))
            self.ingredients = []
            self.error = True
            return
        for recipeIngredient in self.ingredients:
            ingredientObjTmp = getIngredientObject(recipeIngredient)
            if ingredientObjTmp.id != -1:
                found, ingredientObj = matchIngredientsById(ingredientObjTmp, ingredientList)
            else:
                found, ingredientObj = matchIngredientsByString(ingredientObjTmp, ingredientList)
            if found is False:
                print('--> Ingredient not Found : ' + ingredientObj.name, ingredientObj)
                ingredientObj.special = True
                self.error = True
            self.ingredients[idx] = ingredientObj
            print('--> ingredient added:', ingredientObj.name, ingredientObj.size)
            idx += 1

    def detectMatchNames(self):
        """clean"""
        mn = []
        for item in self.match_name:
            item = item.strip()
            if item == '' or len(item) == 1:
                continue
            mn.append(item)
        self.match_name = mn

        """add"""
        if self.category is not None:
            cat = [x for x in self.category]
        else:
            cat = []
        if self.type is not None:
            type = [x for x in self.type]
        else:
            type = []
        if self.match_name is not None:
            match = [x for x in self.match_name]
        else:
            match = []
        for item in [self.name] + cat + type + match:
            item = item.strip()
            if item not in self.match_name:
                self.match_name.append(item)
            if unidecode(item).strip() not in self.match_name:
                self.match_name.append(unidecode(item).strip())
        # print(self.match_name)

    def __repr__(self):
        return f"Recipe({self.name})"

    def __str__(self):
        return f"R:{self.name}"

class RecipeList:
    def __init__(self, path='E:/Scripts/Python/Recette/recette liste.ods', checkIngredient=True, ingredientList=[]):
        self.path = path
        self.recipeList = []
        self.db = None
        self.recipeTree = {}
        self.checkIngredient = checkIngredient
        self.ingredientList = ingredientList
        self.Search = tools.Search(flag='unidecode')
        self.recipeTypes = ['All', 'Starter', 'Dish', 'Dessert', 'Sauce', 'Picnic', 'Soup']
        if self.checkIngredient is True and self.ingredientList is []:
            self.ingredientList = IngredientList().ingredientList
        if path in ['', None]:
            return
        if path[-4:] == ".ods":
            self.setupFromOds()
        else:
            self.setupFromDb()

    def setupFromDb(self):  # TODO
        self.recipeList = self.readDb(self.path)
        # self.conformCategories()
        # self.buildIngredientTree()

    def setupFromOds(self):  # TODO
        self.recipeList = self.readOds()
        # self.conformCategories()
        # self.buildIngredientTree()

    # def readCsv(self):
    #     fileObj = open(self.path, 'r')
    #     lines = fileObj.readlines()
    #     fileObj.close()
    #
    #     csvColumns = ['Titre', 'Ingrédients Spéciaux', 'Rapide', 'Ingrédients', 'Chemin Recette']
    #     for line in lines:
    #         name, needsIngrSpe, isFast, ingredients, recipePath = line.strip().split(';')
    #         dict = {'name': name, 'needsIngrSpe': bool(needsIngrSpe), 'isFast': bool(isFast), 'ingredients': ingredients, 'recipePath': recipePath}
    #         recipeObj = Recipe(dict)
    #         self.recipeList.append(recipeObj)

    def readDb(self, path): # TODO a checker
        if path is None:
            path = self.path
        pathExists = os.path.exists(path)
        self.db = database.DB(path)
        if pathExists is False:
            self.db.create_db()
        recipes = self.db.get_recipes()
        print('Recipes from db : {}'.format(recipes))
        recipeList = []

        for recipe in recipes:
            attrs = attrListToAttrDict(recipe, 'Recipe')
            attrs = self.conformFromDb(attrs)
            recipeObj = Recipe(attrs, self.checkIngredient, self.ingredientList)
            recipeObj.categoryId = recipeObj.category
            recipeList.append(recipeObj)

        return recipeList

    def readOds(self, path=None, check=None):
        if path is None:
            path = self.path
        if os.path.exists(path) is False:
            raise Exception('File not found')
        data = pandas.read_excel(path, engine='odf', sheet_name="Recettes")
        recipeList = []
        if check is None:
            check = self.checkIngredient
        for i in range(data.index.stop):
            attrs = {}
            for col in data.columns:
                attrs[col] = data.at[i, col]

            recipeObj = Recipe(attrs, check, self.ingredientList)
            recipeList.append(recipeObj)

        return recipeList

    def conformCategories(self): #TODO
        for recipeObj in self.recipeList:
            recipeObj.categoryId = recipeObj.category
            #returns list of names from object id
            recipeObj.category = [x.name for x in self.recipeList if x.id in recipeObj.categoryId]
            # print(ingredientObj.name, ingredientObj.categoryId, ingredientObj.category)

            # TODO add category to ingredients matchname
            recipeObj.detectMatchNames()

    def conformFromDb(self, attrs):
        empty = ['', [], ['']]
        attrList = ['name', 'origin', 'notes']
        for attr in attrList:
            if attrs[attr] in empty:
               attrs[attr] = None

        attrList = ['match_name', 'category_id', 'tags', 'ingredients', 'suggestion', 'files']
        for attr in attrList:
            if attrs[attr] in empty:
               attrs[attr] = []

        return attrs

    def importDataFromFile(self, odsPath): # TODO
        recipeList = self.readOds(odsPath)
        db = database.DB(self.path, {'backupDB': False})
        print("==> importing recipe to db")
        print(self.path, odsPath)
        for recipeObj in recipeList:
            print(f'--->> importing recipe : {recipeObj.name} : {recipeObj.__dict__}')
            exportedRecipeObj = copy.deepcopy(recipeObj)
            print(exportedRecipeObj)
            # check existence
            # if ingredientObj.name in self.ingredientDic.keys():
            if exportedRecipeObj.name in [x.name for x in self.recipeList]:
                # update # TODO confirmation and display delta
                print("edit recipe")
                db.editRecipe(exportedRecipeObj)
            else:  # add
                print('add recipe')
                db.addToRecipe(exportedRecipeObj)

        db.backupDB = True

    def exportDatasToDb(self, datas):
        recipeObj = Recipe(datas, True, self.ingredientList)
        recipeObjTmp = copyRecipeObj(recipeObj)
        if self.db is None:
            self.db = database.DB(self.path)
        if recipeObj.id in [None, -1]:
            print('adding recipe')
            self.db.addToRecipe(recipeObjTmp)

        else:
            print('editing recipe')
            self.db.editRecipe(recipeObjTmp)
        print("done")
        return recipeObj

    def filterRecipe(self, filterText, items=[], attr='match_name'):
        if items == []:
            items = self.recipeList
        if isinstance(filterText, str):
            filterText = filterText.strip()
        matchList = self.Search.matchEachItemToWholeSearch(items, filterText, True, attr)
        # print([(obj.name, match) for obj, match in matchList])
        return matchList

    def filterRecipeIngredients(self, ingredientList, recipeList):
        filterList = []
        for recipeObj in recipeList:
            recipeIngredientList = [x.name for x in recipeObj.ingredients]
            matchList = self.Search.matchEachItemToWholeSearch(ingredientList, recipeIngredientList, True, 'match_name')
            recipeMatch = False
            for ingredient, match in matchList:
                if match is True:
                    recipeMatch = True
                    print('found recipe', recipeObj.name, ingredient.name, recipeIngredientList, ingredient.match_name)
                    break
            filterList.append((recipeObj, recipeMatch))
        print([(obj.name, recipeMatch) for obj, recipeMatch in filterList])
        return filterList

    def filterRecipe2(self, filters):
        """
        filters['recipeType']
        filters['recipeMatchName']
        filters['doFilterIngredients']
        filters['ingredients']
        """
        search = {}
        if self.recipeTypes[filters['recipeType']] is not 'All':
            search['type'] = [self.recipeTypes[filters['recipeType']], False, False]
        else:
            # search['type'] = [self.recipeTypes[1:], False, False]
            pass
        if filters['recipeMatchName'] != '':
            search['match_name'] = [filters['recipeMatchName'], False, True]
        else:
            pass
        # print(filters['doFilterIngredients'], filters['ingredients'])
        # if filters['doFilterIngredients'] and filters['ingredients'] != []:
        #     search['ingredients'] = [filters['ingredients'], False, True]
        # else:
        #     pass

        print(f'-->> Recipe Search Launch : {search}')
        #searches = {'attr': ['searchedStr', exclusionOverride, result], }
        for recipeObj in self.recipeList:
            if 'searches' not in recipeObj.__dict__.keys():
                if search == {}:
                    recipeObj.searches = self.Search.newSearchInObj(recipeObj, {})
                    recipeObj.searches.result = 1
                else:
                    recipeObj.searches = self.Search.newSearchInObj(recipeObj, search)
            else:
                if search == {}:
                    recipeObj.searches.result = 1
                else:
                    recipeObj.searches.search(search, True)
            result = recipeObj.searches.result == 1
            #ie : searches = {'attr': ['searchedStr', bool exclusionOverride, split, ('objAttrName')], ...}
            print(f'recipe result: {recipeObj.searches} : {recipeObj.searches.result} // {recipeObj.searches.allSearches}')

    def reprocessMatchNames(self):
        self.db.backup()
        self.db.backupDB = False
        for recipeObj in self.recipeList:
            print(f'old matchname for {recipeObj.name} : {recipeObj.match_name}')
            l = copy.deepcopy(recipeObj.match_name)
            d = []
            recipeObj.detectMatchNames()
            print(f'new matchname for {recipeObj.name} : {recipeObj.match_name}')
            for x in recipeObj.match_name:
                if x not in l:
                    d.append(x)
            print(d)
            try:
                self.exportDatasToDb(recipeObj.__dict__)
                pass
            except:
                raise Exception('error while exporting object')
        self.db.backupDB = True



class Goal:
    def __init__(self, attrs={}):
        self.name = None
        self.nbr = None
        self.note = None
        attrs = removeNans(attrs)
        self.__dict__.update(attrs)

        if self.nbr:
            self.nbr = float(self.nbr)
        else:
            self.nbr = ""

class GoalList:
    def __init__(self, path='E:/Scripts/Python/Recette/recette liste.ods'):
        self.path = path
        self.goalList = []
        if path[-4:] != ".ods":
            self.readCsv()
        else:
            self.readOds()

    def readCsv(self):
        print("TODO")

    def readOds(self):
        data = pandas.read_excel(self.path, engine='odf', sheet_name="Goals")
        for i in range(data.index.stop):
            attrs = {}
            for col in data.columns:
                attrs[col] = data.at[i, col]

            goalObj = Goal(attrs)
            self.goalList.append(goalObj)

class Notes:
    def __init__(self, path='E:/Scripts/Python/Recette/notes.txt'):
        self.path = path

    def read(self):
        if os.path.exists(self.path) is False:
            print("TODO file not found") #TODO
            return ''

        fileObj = open(self.path, 'r')
        content = fileObj.read()
        fileObj.close()
        return content

    def save(self, content):
        if os.path.exists(self.path) is False:
            if os.path.exists(os.path.split(self.path)[0]) is False:
                print("Folder not found, unable to save notes") #TODO
                return

        fileObj = open(self.path, 'w')
        fileObj.write(content)
        fileObj.close()

class Stock:
    def __init__(self, attrs={}):
        self.id = None
        self.name = None
        self.category = None
        self.servingsQuantity = None
        self.servingsUnit = None
        self.nbr = None
        self.dateName = None
        self.dateIsExpirationDate = None
        self.ingredients = None
        self.__dict__.update(attrs)

class StockList:
    def __init__(self, path='E:/Scripts/Python/Recette/recipe_database.db'):
        self.path = path
        self.db = database.DB(self.path)
        if os.path.exists(self.path) is False:
            # database.create_stock_db(self.path)
            self.db.create_db()
        # stocks = database.get_stocks(self.path)
        stocks = self.db.get_stocks()

        self.stockList = []
        for stock in stocks:
            # id, name, category, servingsQuantity, servingsUnit, nbr, dateName, dateIsExpirationDate, ingredients = stock
            # ingredients = convertIngredientIdToObj(path, ingredients)
            #
            # attrs = {
            #     'id': id,
            #     'name': name,
            #     'category': category,
            #     'servingsQuantity': servingsQuantity,
            #     'servingsUnit': servingsUnit,
            #     'nbr': nbr,
            #     'dateName': dateName,
            #     'dateIsExpirationDate': bool(dateIsExpirationDate),
            #     'ingredients': ingredients,
            # }
            attrs = attrListToAttrDict(stock, 'Stock')
            if attrs['ingredients'] is not None:
                attrs['ingredients'] = convertIngredientIdToObj(path, attrs['ingredients'])
            stockObj = Stock(attrs)
            self.stockList.append(stockObj)


        self.categories = ['A Finir', 'Surgelés', 'Conserves']

    def addStock(self, attrs):
        stockObj = Stock(attrs)
        database.addToStock(self.path, stockObj)

    def editStock(self, attrs):
        stockObj = Stock(attrs)
        database.editStock(self.path, stockObj)

    def removeStock(self, id):
        database.removeStock(self.path, id)

class Day:
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.lunch = None
        self.dinner = None
        self.qtItems = []

class DayList:
    def __init__(self, start=None, length=17):
        if start is None:
            start = time.time()

        self.startDay = time.strftime("%Y%m%d", time.gmtime(start))
        dayRange = pandas.date_range(self.startDay, periods=length)

        self.dayList = []
        idx = 0
        for day in dayRange:
            # if idx == 0:
            #     idx += 1
            #     continue
            dayName = day.strftime("%A : %d %b")
            dayNum = day.strftime("%Y.%m.%d")
            dayObj = Day(dayName, dayNum)
            self.dayList.append(dayObj)
            idx += 1


class Datas:
    def __init__(self, dbPath):
        self.dbPath = self.checkDbPath(dbPath)
        self.prefs = Preferences(self.dbPath)
        self.ingredients = IngredientList(self.dbPath)
        self.recipes = RecipeList(self.dbPath, True, self.ingredients.ingredientList)

    def checkDbPath(self, dbPath):
        if os.path.isfile(dbPath):
            return dbPath
        else:
            tmpPath = os.path.join(sys.argv[0], dbPath)
            if os.path.isfile(tmpPath):
                return dbPath
            else:
                db = database.DB(dbPath)
                db.create_db()
                if os.path.isfile(dbPath):
                    return dbPath
                raise FileNotFoundError(dbPath)



if __name__ == "__main__":
    RecipeList()