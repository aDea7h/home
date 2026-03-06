from copy import deepcopy

import Recette
import database

def reprocessLazyMatchName(ingredientObj):
    # print(ingredientObj, 'reprocessLazyMatchName', type(ingredientObj))
    lazyMatchName = []
    lazyMatchName.append(ingredientObj.name)
    match = Recette.completeMatchName(ingredientObj.name, True)
    if match:
        lazyMatchName.append(match)
    for item in ingredientObj.db_match_name:
        match = Recette.completeMatchName(item)
        if match and match not in lazyMatchName:
            lazyMatchName.append(match)

    return lazyMatchName






def reprocess_match_name(file):
    ingredientsdb = Recette.IngredientList(file)
    db = database.DB(file)
    for ingredient in ingredientsdb.ingredientList:
        # if ingredient.vegan != 2:
        #     continue

        print('-----------------------------------')
        #print(ingredient.name, ingredient.match_name)
        old = deepcopy(ingredient.match_name)
        if ingredient.name in ingredient.match_name:
            ingredient.match_name.remove(ingredient.name)

        uniname = Recette.completeMatchName(ingredient.name)
        if uniname in ingredient.match_name:
            ingredient.match_name.remove(uniname)

        for family in ingredient.family:
            ingredient.match_name.remove(family)
            uniname = Recette.completeMatchName(family)
            if uniname in ingredient.match_name:
                ingredient.match_name.remove(uniname)

        for match in ingredient.match_name:
            unimatch = Recette.completeMatchName(match)
            if unimatch in ingredient.match_name and match != unimatch:
                ingredient.match_name.remove(unimatch)


        print(ingredient.name, ingredient.match_name, old)
        ingredient.db_match_name = deepcopy(ingredient.match_name)
        ingredient.db_lazy_match_name = reprocessLazyMatchName(ingredient)

        # print(ingredient.id, ingredient.name, ingredient.match_name, ingredient.db_lazy_match_name, '\n')
        #
        # for key in ingredient.__dict__:
        #     print(key, type(ingredient.__dict__[key]), ingredient.__dict__[key])
        # break
        # db.editIngredient(ingredient)

def ingFamily(file):
    ingredientsdb = Recette.IngredientList(file)
    db = database.DB(file)
    dbFamilies = {
        'viande': 'meat',
        'légume': 'vegetable',
        'féculent': 'starch',
        'divers': 'other',
    }
    for ingredient in ingredientsdb.ingredientList:
        print('--->> ', ingredient.name, ingredient.family)
        idx = 0
        for family in ingredient.family:
            if family not in dbFamilies:
                return False
            ingredient.family[idx] = dbFamilies[family]
            # print('switched to :',  dbFamilies[family] )
            idx += 1
        print(ingredient.family)
        # db.editIngredient(ingredient)

def categoryFromMatchName(file):
    def findCategoryByName(ingredientsdb, name):
        for ingredient in ingredientsdb.ingredientList:
            if ingredient.name == name:
                return ingredient

    ingredientsdb = Recette.IngredientList(file)
    db = database.DB(file)
    for ingredient in ingredientsdb.ingredientList:
        edit = False
        # print('--->> ', ingredient.name, ingredient.db_match_name)
        for match in ingredient.db_match_name:
            if match == ingredient.name:
                continue
            # print(f'{ingredient.name} : try to match : {match}')
            result = findCategoryByName(ingredientsdb, match)
            if result is None:
                continue
            print(f'{ingredient.name} : new category : {result.name} - {result.id}')
            print(f'{result.id} in {ingredient.db_category_id} is {result.id in ingredient.db_category_id}')
            if result.id not in ingredient.db_category_id:
                ingredient.db_category_id.append(result.id)
                edit = True

        if edit is True:
            db.editIngredient(ingredient)

file = '/home/adeath/Scripts/Recette/recipe_database.db'
# reprocess_match_name(file)
# ingFamily(file)
categoryFromMatchName(file)