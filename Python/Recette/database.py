import sqlite3
from incrementalBackup import incrementalBackup

# Sql Datatypes:
    # NULL > exists or not
    # INTEGER
    # REAL > float
    # TEXT
    # BLOB > images / mp3 ... = data

# def convertIngredientObjToId(obj):
#     #ingredientsId = [ingredient.id for ingredient in obj.ingredients]
#     ingredientList = []
#     print('conforming ingredients')
#     print(obj.ingredients)
#     if obj.ingredients in [None, '']:
#         return ''
#     for ingredient in obj.ingredients:
#         print(ingredient)
#         print(ingredient.id)
#         if ingredient.id == -1:
#             ingredientList.append(ingredient.name)
#         else:
#             ingredientList.append(str(ingredient.id))
#             # ingredientList.append('{}.{}'.format(type(ingredient).__name__, ingredient.id))
#             # print('converting ingredient {}, {} to {}.{}'.format(ingredient, ingredientName, type(ingredient).__name__, ingredient.id))
#     return ', '.join(ingredientList)

def conformIngredientObjInRecipe(obj):
    if obj.ingredients in [None, '']:
        obj.dbIngredients = ''
        return obj
    ingredientList = []
    for ingredientObj in obj.ingredients:
        if ingredientObj.id < 0:
            ingredientList.append((ingredientObj.name, ingredientObj.size))
        else:
            ingredientList.append((ingredientObj.id, ingredientObj.size))
    obj.dbIngredients = str(ingredientList)
    return obj

def conformObjToDBDatas(obj):
    for attr in obj.__dict__:
        attrType = type(obj.__dict__[attr]).__name__
        print(attr, attrType, obj.__dict__[attr])
        if attrType == 'list':
            print("converting LIST attr {} to STR : {}".format(attr, obj.__dict__[attr]))
            obj.__dict__[attr] = str(obj.__dict__[attr])
        elif attrType == 'bool':
            print("converting BOOL attr {} to INT : {}".format(attr, obj.__dict__[attr]))
            obj.__dict__[attr] = int(obj.__dict__[attr])
    return obj

def conformRating(obj):
    if(obj.is_tested == False):
        obj.rating = -1
    if(obj.is_favorite == True):
        obj.rating = 10
    return obj




# ###############
# #DB creations
# ###############

# def create_recipe_db(path):
#     #create file if not existant and a cursor
#     cxion = sqlite3.connect(path)
#     c = cxion.cursor()

#     c.execute("""CREATE TABLE ingredients(
#         name text,
#         category text,
#         family text,
#         match_name text,
#         vegan integer,
#         vegetarian integer,
#         meat_replacement integer,
#         protein real,
#         always_available integer,
#         special integer,
#         season text,
#         local integer
#         )""")
    

#     #commit our command
#     cxion.commit()

#     #close connection
#     cxion.close()


# def create_stock_db(path):
#     # create file if not existant and a cursor
#     cxion = sqlite3.connect(path)
#     cxion.commit()
#     cxion.close()
#     cxion = sqlite3.connect(path)
#     c = cxion.cursor()

#     c.execute("""CREATE TABLE stocks(
#         name text,
#         category text,
#         servingsQuantity real,
#         servingsUnit text,
#         nbr integer,
#         dateName text,
#         dateIsExpirationDate integer,
#         ingredients text
#         )""")
#     # commit our command
#     # cxion.commit()

#     c.execute("""CREATE TABLE goals(
#             name text,
#             nbr text,
#             note text
#             )""")
#     # commit our command
#     # cxion.commit()

#     c.execute("""CREATE TABLE notes(
#                 name text
#                 )""")
#     # commit our command
#     cxion.commit()

#     # close connection
#     cxion.close()


# ###############
# #STOCKS
# ###############

# def get_stocks(path):
#     #setup connection
#     cxion = sqlite3.connect(path)
#     c = cxion.cursor()

#     c.execute("""SELECT rowid, * FROM stocks""")
#     items = c.fetchall()

#     cxion.commit()
#     cxion.close()
#     return items

# def addToStock(path, stockObj):
#     incrementalBackup(path)
#     cxion = sqlite3.connect(path)
#     c = cxion.cursor()

#     stockObj.ingredients = convertIngredientObjToId(stockObj)

#     c.execute("INSERT INTO stocks VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (stockObj.name, stockObj.category, stockObj.servingsQuantity, stockObj.servingsUnit, stockObj.nbr, stockObj.dateName, stockObj.dateIsExpirationDate, stockObj.ingredients))
              
#     cxion.commit()
#     cxion.close()

# def editStock(path, stockObj):
#     incrementalBackup(path)
#     cxion = sqlite3.connect(path)
#     c = cxion.cursor()

#     stockObj.ingredients = convertIngredientObjToId(stockObj)

#     sqlQuery = """UPDATE stocks set name = ?, category = ?, servingsQuantity = ?, servingsUnit = ?, nbr = ?, dateName = ?, dateIsExpirationDate = ?, ingredients = ? WHERE rowid = ?"""
#     data = (stockObj.name, stockObj.category, stockObj.servingsQuantity, stockObj.servingsUnit, stockObj.nbr, stockObj.dateName, stockObj.dateIsExpirationDate, stockObj.id, stockObj.ingredients)
#     c.execute(sqlQuery, data)
              
#     cxion.commit()
#     cxion.close()

# def removeStock(path, id):
#     incrementalBackup(path)
#     cxion = sqlite3.connect(path)
#     c = cxion.cursor()

#     sqlQuery = """DELETE from stocks WHERE rowid = {}""".format(id)
#     c.execute(sqlQuery)
              
#     cxion.commit()
#     cxion.close()



# ###############
# #INGREDIENTS
# ###############

# def getIngredientFromId(path, id):
#     cxion = sqlite3.connect(path)
#     c = cxion.cursor()

#     sqlQuery = """SELECT rowid * from ingredients WHERE rowid = {}""".format(id)
#     c.execute(sqlQuery)
              
#     cxion.commit()
#     cxion.close()



# ###############
# #RECIPES
# ###############

# def getRecipeFromId(path, id):
#     cxion = sqlite3.connect(path)
#     c = cxion.cursor()

#     sqlQuery = """SELECT rowid * from recipes WHERE rowid = {}""".format(id)
#     c.execute(sqlQuery)
              
#     cxion.commit()
#     cxion.close()


class DB:
    def __init__(self, pathToRecipeDb, attrs={}):
        self.pathToRecipeDb = pathToRecipeDb
        self.backupDB = True
        self.connexion = None
        self.__dict__.update(attrs)

    ###############
    # DB General Actions
    ###############

    def setConnexion(self):
        print('--> DB : Setting connection')
        self.connexion = sqlite3.connect(self.pathToRecipeDb)
        self.cursor = self.connexion.cursor()

    def commit(self, close=True):
        self.connexion.commit()
        if close is True:
            self.connexion.close()
            self.connection = None
            self.cursor = None
        print('--> DB : Commit Done')

    def executeQuery(self, sqlQuery, commit=True):
        def doExecute(sqlQuery):
            print('--> DB : pathToRecipeDb : {}'.format(self.pathToRecipeDb))
            print('--> DB : Executing : {}'.format(sqlQuery))
            print('--> DB : cursor : {}'.format(self.cursor))
            if isinstance(sqlQuery, str) is False:
                self.cursor.execute(sqlQuery[0], sqlQuery[1])
            else:
                self.cursor.execute(sqlQuery)


        if self.connexion is None or self.cursor is None:
            self.setConnexion()
        if isinstance(sqlQuery, list) is True:
            for singleSqlquery in sqlQuery:
                doExecute(singleSqlquery)
        else:
            doExecute(sqlQuery)
        if commit is True:
            self.commit()

    ###############
    # Others
    ###############


    # def convertIngredientObjToId(self, obj):
    #     #ingredientsId = [ingredient.id for ingredient in obj.ingredients]
    #     ingredientList = []
    #     for ingredient in obj.ingredients:
    #         ingredientList.append('{}.{}'.format(type(ingredient).__name__, ingredient.id))
    #         print('converting ingredient {}, {} to {}.{}'.format(ingredient, ingredientName, type(ingredient).__name__, ingredient.id))
    #     return str(ingredientsId)


    ###############
    # DB creations
    ###############

    def create_db(self):
        self.setConnexion()
        self.commit(close=False)
        sqlQuery = """CREATE TABLE ingredients(
            name text,
            category text,
            family text,
            match_name text,
            vegan integer,
            vegetarian integer,
            meat_replacement integer,
            protein real,
            always_available integer,
            special integer,
            season text,
            local integer
            )"""
        sqlQuery2 = """CREATE TABLE stocks(
            name text,
            category text,
            servingsQuantity real,
            servingsUnit text,
            nbr integer,
            dateName text,
            dateIsExpirationDate integer,
            ingredients text
            )"""
        sqlQuery3 = """CREATE TABLE goals(
                name text,
                nbr text,
                note text
                )"""
        sqlQuery4 = """CREATE TABLE notes(
                    name text
                    )"""
        self.executeQuery([sqlQuery, sqlQuery2, sqlQuery3, sqlQuery4], False)
        # self.executeQuery(sqlQuery, False)
        self.commit(close=False)


    ###############
    # INGREDIENTS Table
    ###############

    def getIngredientFromId(self, id):
        sqlQuery = """SELECT rowid * from ingredients WHERE rowid = {}""".format(id)
        self.executeQuery(sqlQuery, True)

    def get_ingredients(self):
        sqlQuery = """SELECT rowid, * FROM ingredients"""
        self.executeQuery(sqlQuery, False)
        items = self.cursor.fetchall()
        self.commit()
        return items

    def addToIngredient(self, ingredientObj):
        if self.backupDB is True:
            incrementalBackup(self.pathToRecipeDb)
        # sqlQuery = "INSERT INTO ingredients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (ingredientObj.name, ingredientObj.category, ingredientObj.family, ingredientObj.match_name, ingredientObj.vegan, ingredientObj.vegetarian, ingredientObj.meat_replacement, ingredientObj.protein, ingredientObj.always_available, ingredientObj.special, ingredientObj.season, ingredientObj.local) 
        ingredientObj = conformObjToDBDatas(ingredientObj)
        sqlQuery = "INSERT INTO ingredients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        data = (ingredientObj.name, ingredientObj.category, ingredientObj.family, ingredientObj.match_name, ingredientObj.vegan, ingredientObj.vegetarian, ingredientObj.meat_replacement, ingredientObj.protein, ingredientObj.always_available, ingredientObj.special, ingredientObj.season, ingredientObj.local)
        self.executeQuery((sqlQuery, data), True)

    def editIngredient(self, ingredientObj):
        if self.backupDB is True:
            incrementalBackup(self.pathToRecipeDb)
        ingredientObj = conformObjToDBDatas(ingredientObj)
        sqlQuery = """UPDATE ingredients set name = ?, category = ?, family = ?, match_name = ?, vegan = ?, vegetarian = ?, meat_replacement = ?, protein = ?, always_available = ?, special = ?, season = ?, local = ? WHERE rowid = ?"""
        data = (ingredientObj.name, ingredientObj.category, ingredientObj.family, ingredientObj.match_name, ingredientObj.vegan, ingredientObj.vegetarian, ingredientObj.meat_replacement, ingredientObj.protein, ingredientObj.always_available, ingredientObj.special, ingredientObj.season, ingredientObj.local, ingredientObj.id)
        self.executeQuery((sqlQuery, data), True)

    def removeIngredient(self, id):
        if self.backupDB is True:
            incrementalBackup(self.pathToRecipeDb)
        sqlQuery = """DELETE from ingredients WHERE rowid = {}""".format(id)
        self.executeQuery(sqlQuery, True)


    ###############
    # RECIPES Table
    ###############

    def getRecipeFromId(self, id):
        sqlQuery = """SELECT rowid * from recipes WHERE rowid = {}""".format(id)
        self.executeQuery(sqlQuery, True)

    def get_recipes(self):
        sqlQuery = """SELECT rowid, * FROM recipes"""
        self.executeQuery(sqlQuery, False)
        items = self.cursor.fetchall()
        self.commit()
        return items

    def addToRecipe(self, recipeObj):
        if self.backupDB is True:
            incrementalBackup(self.pathToRecipeDb)
        recipeObj = conformIngredientObjInRecipe(recipeObj)
        recipeObj = conformObjToDBDatas(recipeObj)
        recipeObj = conformRating(recipeObj)
        sqlQuery = "INSERT INTO recipes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        data = (recipeObj.name, recipeObj.match_name, recipeObj.category_id, recipeObj.type, recipeObj.origin, recipeObj.tags, recipeObj.dbIngredients, recipeObj.before_recipe, recipeObj.recipe, recipeObj.suggestion, recipeObj.notes, recipeObj.files, recipeObj.cooking_time, recipeObj.preparation_time, recipeObj.is_best_reheated, recipeObj.rating, recipeObj.is_wip)
        self.executeQuery((sqlQuery, data), True)

    def editRecipe(self, recipeObj):
        if self.backupDB is True:
            incrementalBackup(self.pathToRecipeDb)
        recipeObj = conformIngredientObjInRecipe(recipeObj)
        recipeObj = conformObjToDBDatas(recipeObj)
        recipeObj = conformRating(recipeObj)
        sqlQuery = """UPDATE recipes set name = ?, match_name = ?, category_id = ?, type = ?, origin = ?, tags = ?, ingredients = ?, before_recipe = ?, recipe = ?, suggestion = ?, notes = ?, files = ?, cooking_time = ?, preparation_time = ?, is_best_reheated = ?, rating = ?, is_wip = ? WHERE rowid = ?"""
        data = (recipeObj.name, recipeObj.match_name, recipeObj.category_id, recipeObj.type, recipeObj.origin, recipeObj.tags, recipeObj.dbIngredients, recipeObj.before_recipe, recipeObj.recipe, recipeObj.suggestion, recipeObj.notes, recipeObj.files, recipeObj.cooking_time, recipeObj.preparation_time, recipeObj.is_best_reheated, recipeObj.rating, recipeObj.is_wip, recipeObj.id)
        self.executeQuery((sqlQuery, data), True)

    def removeRecipe(self, id):
        if self.backupDB is True:
            incrementalBackup(self.pathToRecipeDb)
        sqlQuery = """DELETE from recipes WHERE rowid = {}""".format(id)
        self.executeQuery(sqlQuery, True)


    ###############
    # STOCKS Table
    ###############

    def get_stocks(self):
        sqlQuery = """SELECT rowid, * FROM stocks"""
        self.executeQuery(sqlQuery, False)
        items = self.cursor.fetchall()
        self.commit()
        return items

    def addToStock(self, stockObj):
        if self.backupDB is True:
            incrementalBackup(self.pathToCustom)
        stockObj = conformIngredientObjInRecipe(stockObj)
        sqlQuery = "INSERT INTO stocks VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (stockObj.name, stockObj.category, stockObj.servingsQuantity, stockObj.servingsUnit, stockObj.nbr, stockObj.dateName, stockObj.dateIsExpirationDate, stockObj.dbIngredients)
        self.executeQuery(sqlQuery, True)

    def editStock(self, stockObj):
        if self.backupDB is True:
            incrementalBackup(self.pathToCustom)
        stockObj = conformIngredientObjInRecipe(stockObj)
        sqlQuery = """UPDATE stocks set name = ?, category = ?, servingsQuantity = ?, servingsUnit = ?, nbr = ?, dateName = ?, dateIsExpirationDate = ?, ingredients = ? WHERE rowid = ?"""
        data = (stockObj.name, stockObj.category, stockObj.servingsQuantity, stockObj.servingsUnit, stockObj.nbr, stockObj.dateName, stockObj.dateIsExpirationDate, stockObj.dbIngredients, stockObj.id)
        self.executeQuery((sqlQuery, data), True)

    def removeStock(self, id):
        if self.backupDB is True:
            incrementalBackup(self.pathToCustom)
        sqlQuery = """DELETE from stocks WHERE rowid = {}""".format(id)
        self.executeQuery(sqlQuery, True)


    ###############
    # Config Table
    ###############

    def get_preferences(self):
        sqlQuery = """SELECT rowid, * FROM config"""
        self.executeQuery(sqlQuery, False)
        items = self.cursor.fetchall()
        self.commit()
        return items

    def edit_preferences(self, prefs):
        if self.backupDB is True:
            incrementalBackup(self.pathToCustom)
        sqlQuery = """UPDATE config set Key = ?, Value = ? WHERE rowid = ?"""
        data = (prefs['key'], prefs['value'], prefs['id'])
        self.executeQuery((sqlQuery, data), True)