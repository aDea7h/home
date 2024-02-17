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
        attrs = removeNans(attrs)
        attrs = splitList(attrs)
        self.__dict__.update(attrs)
        self.visible = bool(self.visible)
        self.local = bool(self.local)

class IngredientList:
    def __init__(self, path='E:/Scripts/Python/Recette/recette liste.ods'):
        self.path = path
        self.ingredientList = []
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



class Recipe:
    def __init__(self, attrs={}):
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
        if 'ingredients' in attrs.keys():
            if isinstance(attrs['ingredients'], str) is True:
                attrs['ingredients'] = attrs['ingredients'].split(',')
        attrs = removeNans(attrs)
        attrs = splitList(attrs)
        self.__dict__.update(attrs)
        if self.type is None:
            self.type = "plat"

    def printObj(self):
        print('-->> {}'.format(self.name))
        print(self.__dict__)

class RecipeList:
    def __init__(self, path='E:/Scripts/Python/Recette/recette liste.ods'):
        self.path = path
        self.recipeList = []
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
            recipeObj = Recipe(attrs)
            self.recipeList.append(recipeObj)

class Day:
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.lunch = None
        self.dinner = None


class DayList:
    def __init__(self, start=None, length=7):
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