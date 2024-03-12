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
import pandas
import odf
import time
import numpy as np
from unidecode import unidecode
import tools

def removeNans(dict):
    def removeNan(val):
        if pandas.isna(val) is True:
            return None
        else:
            return val

    for key in dict:
        dict[key] = removeNan(dict[key])
    return dict

def splitList(dict):
    for key in dict.keys():
        if key == 'name' or isinstance(dict[key], str) is False:
            continue
        dict[key] = [x.strip() for x in dict[key].split(',')]
    return dict

class Ingredient:
    def __init__(self, attrs={}):
        self.name = None
        self.category = None
        self.family = None
        self.match_name = []
        self.visible = True
        self.season = None
        self.local = False
        # self.nutritional_value = None  # lipids / glucids / vitamins / iron...
        # self.vegetarian = None
        self.vegan = None
        self.always_available = None
        self.special = None
        self.size = 0
        attrs = removeNans(attrs)
        attrs = splitList(attrs)
        self.__dict__.update(attrs)
        self.visible = bool(self.visible)
        self.local = bool(self.local)
        self.special = bool(self.special)
        self.always_available = bool(self.always_available)
        self.qtItem = []
        if self.match_name is None:
            self.match_name = []

        self.detectMatchNames()

    def detectMatchNames(self):
        if self.category is not None:
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
            if item not in self.match_name:
                self.match_name.append(item)
            if unidecode(item).strip() not in self.match_name:
                self.match_name.append(unidecode(item).strip())
        # print(self.match_name)

class IngredientList:
    def __init__(self, path='E:/Scripts/Python/Recette/recette liste.ods'):
        self.path = path
        self.ingredientList = []
        self.ingredientDic = {}
        self.Search = tools.Search(flag='unidecode')
        if path[-4:] != ".ods":
            self.readCsv()
        else:
            self.readOds()

    def readCsv(self):
        fileObj = open(self.path, 'r')
        lines = fileObj.readlines()
        fileObj.close()
        for line in lines:
            print(line)
            name, family, altNames, visible, season, local = line.strip().split(';')
            dict = {'name': name, 'family': family, 'altNames': altNames, 'visible':visible, 'season': season, 'local': local}
            ingredientObj = Ingredient(dict)
            # print(recipeObj.printObj())
            self.ingredientList.append(ingredientObj)

    def readOds(self):
        data = pandas.read_excel(self.path, engine='odf', sheet_name="Ingredients")
        for i in range(data.index.stop):
            attrs = {}
            for col in data.columns:
                attrs[col] = data.at[i, col]
            ingredientObj = Ingredient(attrs)
            self.ingredientList.append(ingredientObj)
            self.ingredientDic[ingredientObj.name] = ingredientObj

    def filterIngredients(self, filterText):
        filterText = filterText.strip()
        matchList = self.Search.matchEachItemToWholeSearch(self.ingredientList, filterText, True, 'match_name')
        print([(obj.name, match) for obj, match in matchList])
        return matchList



class Recipe:
    def __init__(self, attrs={}, checkIngredient=False, ingredientList=[]):
        self.name = None
        self.category = None
        self.type = None
        self.match_name = []
        self.ingredients = []
        self.needsSpeIngredient = False
        self.isFast = False
        self.tried = False
        self.wip = False
        self.customizable = False
        self.recipePath = None
        self.error = False
        if 'ingredients' in attrs.keys():
            if isinstance(attrs['ingredients'], str) is True:
                attrs['ingredients'] = attrs['ingredients'].split(',')
        attrs = removeNans(attrs)
        attrs = splitList(attrs)
        self.__dict__.update(attrs)
        if self.type is None:
            self.type = ["plat"]
        if self.match_name is None:
            self.match_name = []
        if checkIngredient is True:
            self.conformRecipeIngredients(ingredientList)
        self.detectMatchNames()

    def printObj(self):
        print('-->> {}'.format(self.name))
        print(self.__dict__)

    def conformRecipeIngredients(self, ingredientList): #TODO Bad replace ingredient
        idx = 0
        if self.ingredients in [None, []]:
            print("No ingredients found for : {}".format(self.name))
            return
        for recipeIngredient in self.ingredients:
            name = unidecode(recipeIngredient).strip()
            found = False
            for ingredientObj in ingredientList:
                # print(name, ingredientObj.match_name, name in ingredientObj.match_name, isinstance(name, str), isinstance(ingredientObj.match_name, list))
                if name in ingredientObj.match_name:
                    # recipeIngredient = ingredientObj.name
                    recipeIngredient = ingredientObj
                    found = True
                    break
            if found is True:
                self.ingredients[idx] = recipeIngredient
            else:
                print('--> Ingredient not Found : '+recipeIngredient)
                self.error = True
            idx += 1

    def detectMatchNames(self):
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
            if item not in self.match_name:
                self.match_name.append(item)
            if unidecode(item).strip() not in self.match_name:
                self.match_name.append(unidecode(item).strip())
        # print(self.match_name)

class RecipeList:
    def __init__(self, path='E:/Scripts/Python/Recette/recette liste.ods', checkIngredient=False, ingredientList=[]):
        self.path = path
        self.recipeList = []
        self.checkIngredient = checkIngredient
        self.ingredientList = ingredientList
        self.Search = tools.Search(flag='unidecode')
        if self.checkIngredient is True and self.ingredientList is []:
            self.ingredientList = IngredientList().ingredientList
        if path[-4:] != ".ods":
            self.readCsv()
        else:
            self.readOds()


    def readCsv(self):
        fileObj = open(self.path, 'r')
        lines = fileObj.readlines()
        fileObj.close()

        csvColumns = ['Titre', 'Ingrédients Spéciaux', 'Rapide', 'Ingrédients', 'Chemin Recette']
        for line in lines:
            name, needsIngrSpe, isFast, ingredients, recipePath = line.strip().split(';')
            dict = {'name': name, 'needsIngrSpe': bool(needsIngrSpe), 'isFast': bool(isFast), 'ingredients': ingredients, 'recipePath': recipePath}
            recipeObj = Recipe(dict)
            self.recipeList.append(recipeObj)

    def readOds(self):
        data = pandas.read_excel(self.path, engine='odf', sheet_name="Recettes")
        for i in range(data.index.stop):
            attrs = {}
            for col in data.columns:
                attrs[col] = data.at[i, col]

            recipeObj = Recipe(attrs, self.checkIngredient, self.ingredientList)
            self.recipeList.append(recipeObj)

    def filterRecipe(self, filterText, items=[], attr='match_name'):
        if items == []:
            items = self.recipeList
        if isinstance(filterText, str):
            filterText = filterText.strip()
        matchList = self.Search.matchEachItemToWholeSearch(items, filterText, True, attr)
        print([(obj.name, match) for obj, match in matchList])
        return matchList



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



class Day:
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.lunch = None
        self.dinner = None
        self.qtItems = []

class DayList:
    def __init__(self, start=None, length=9):
        if start is None:
            start = time.time()

        self.startDay = time.strftime("%Y%m%d", time.gmtime(start))
        dayRange = pandas.date_range(self.startDay, periods=length)

        self.dayList = []
        for day in dayRange:
            dayName = day.strftime("%A : %d %b")
            dayNum = day.strftime("%Y.%m.%d")
            dayObj = Day(dayName, dayNum)
            self.dayList.append(dayObj)


if __name__ == "__main__":
    RecipeList()