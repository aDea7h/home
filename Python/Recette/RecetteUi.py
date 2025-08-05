import unidecode
from PySide6 import QtCore, QtGui, QtWidgets
import sys
import Recette
from RecetteWidgets import *
import os
import ctypes
import time
#import tools

# TODO
"""
USES Python 3.9 PySide 6.6.1
WIP : Recipe from Db

Qt to Android Tuto
https://www.qt.io/blog/taking-qt-for-python-to-android

db: switch all to db and DB class!
db: addingredient a finir (manage categories)
db: check data before import

ui: crockpot mode : quick recette
ui: quick add stock ui
ui: display recipe

stock : attach ingredient data to it
stock : add from recipe / ingredient / crockpot only
stock : quick add stock ui from menu

bug: multi parent are parented to first one
bug : bobun sort dans ingredient canelle
bug : filter de recette et trop lent ac ingredients
bug: !! conform des ingredients de recette sur liste d ingredient a refaire  (on sait pas sur quoi ca match et peu precis)!!

menu: separer entree / plat / dessert
menu: affichage en child les ingredients
menu: supprimer un repas (ou mettre repas auto : rien)
menu: manual edit ingredient / recette and export / set ingredient-recipe as leftover (no shopping needed) or bought pre made
menu: case reste a cocher: et add to stock

ingredient: remove ingredient checkbox ?
ingredient: remove from db only if no recipe / stock is in use
ingredient: temps de cuisson

recipe: special kids : jambon pates with kid rating
recipe: add servings data
recipe: regen ui on edit
recipe : rich text editor
recipe: ajout de menus generic sans ingredients a flagger : "gateau" = pas d'ingredient listable
recipe: concept de base et toppings (pate a pizza / cake / crepes) completees par variantes (reine / chorizo ....)
recipe: concept de variantes de recette (variantes completes (recette porc au sucre )ou partielles (humous))
recipe: gestion des poids d ingredients et repartition sur multi ingredients (poid des aliments total et pourcentage par classe)
recipe: recherche recette sans ingredient !piment !blé
recipe: avertissement pour trempage ingredients.... prepa la veille
recipe: tab a tester
recipe: ajout notion repos pour recette

groceries: ingredient list management for recipe (checkbox / remove on keyboard replace)
groceries: selection ingredient selectionne le/les repas du menu (et inversement)


general: custompprint for logging
general: sauvegarde / import / envoyer mail recap / hitorique
general: links d'accompagnement (legumes / viande) et menu tout fait (curry indien royal)
general: ds vu liste des courses/menus proposer de congeler (avoir jour des courses)
general: jour a contrainte de temps (sport/douche....)
general: ouverture rapide et progress bar
general: colors and beautiful calendar

goals: restriction des aliments : entre 0 et 1 fois pour le boeuf : 1-3 poisson 1-2 oeufs

    menu item edit = txt insert in filter recipe and ingredient
    case goal check
    zone texte libre pour notes a cote des goals
    idees de recette /ingredient a finir pour plus tard
    liste des courses a split (speciaux / viande / legume / divers / toujours dispo)
    dark ui
    menu icomplet / complet
    ajouter des repas dans les menus
"""
def getIconFiles(libPath):
    path = '{}/{}'.format(os.path.split(libPath)[0], 'icons')
    imageList = []
    for image in os.listdir(path):
        if os.path.splitext(image)[1] == '.png':
            imageList.append(image)
    return path, imageList

def getIcons(libPath):
    path, images = getIconFiles(libPath)
    imageDic = {}
    for image in images:
        qimage = QtGui.QIcon(os.path.join(path, image))
        imageDic[os.path.splitext(image)[0]] = qimage
    return imageDic

def getImages(libPath):
    path, images = getIconFiles(libPath)
    imageDic = {}
    for image in images:
        qpixmap = QtGui.QPixmap(os.path.join(path, image))
        qpixmap = qpixmap.scaled(24, 24, QtCore.Qt.KeepAspectRatio)
        # qimage = QtWidgets.QLabel()
        # qimage.setPixmap(qpixmap)
        imageDic[os.path.splitext(image)[0]] = qpixmap
    return imageDic

def getTheme():
    uiTheme = {
        'menuIsOk_bg': (0.1, 0.3, 0.1, 1),
        'error_bg': (0.3, 0.1, 0.1, 1),
        'meat_bg': (0.35, 0.16, 0.16, 1),
        'vegetable_bg': (0.18, 0.35, 0.16, 1),
        'starch_bg': (0.5, 0.45, 0.21, 1),
        'other_bg': (0.16, 0.24, 0.35, 1),
    }
    for key in uiTheme:
        r, g, b, a = uiTheme[key]
        uiTheme[key] = QtGui.QColor.fromRgbF(r, g, b, a)
    return uiTheme


class EditIngredientWindow(QtWidgets.QDialog): #TODO WIP
    def __init__(self, parent, ui, topItemsDic):
        super().__init__()
        self.parent = parent
        if ui['icons'] is None:
            ui['icons'] = getIcons(libPath)
        if ui['uiTheme'] is None:
            ui['uiTheme'] = getTheme()
        self.ui = ui
        if topItemsDic is None:
            topItemDic = self.getTopItems()
        self.topItemDic = topItemsDic
        self.setWindowTitle("Add Ingredient")
        if self.ui['icons']:
            self.setWindowIcon(self.ui['icons']['menu'])
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        #UI Elements
        self.qtNameLineEdit = QtWidgets.QLineEdit()
        font = self.qtNameLineEdit.font()
        font.setPointSize(24)
        self.qtNameLineEdit.setFont(font)
        self.qtNameLineEdit.setPlaceholderText('Name')
        self.qtCategoryTree = QtWidgets.QTreeWidget()
        self.qtCategoryTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Nest Ingredient in Food Category.ies']))
        self.qtCategoryTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtMatchNameLineEdit = QtWidgets.QLineEdit()
        self.qtMatchNameLineEdit.setPlaceholderText('Additional matching names')
        self.qtIsVeganCombo = QtWidgets.QComboBox()
        self.qtIsVeganCombo.addItems(['Not Vegetarian', 'Vegetarian', 'Vegan'])
        self.qtIsMeatReplacementChk = QtWidgets.QCheckBox("Contribute to replace meat")
        self.qtProteinContribution = QtWidgets.QSpinBox()
        self.qtIngredientAvailability = QtWidgets.QComboBox()
        self.qtIngredientAvailability.addItems(['Always Available, no shopping needed', 'shopping needed', 'hard to find'])

        #UI Accept / Reject Buttons
        self.qtButtonBox = QtWidgets.QDialogButtonBox()
        self.qtButtonBox.addButton("Add Ingredient", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.qtButtonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        self.qtButtonBox.accepted.connect(self.accept)
        self.qtButtonBox.rejected.connect(self.reject)
        if self.parent:
            self.accepted.connect(self.parent.addIngredientProcess)

        #Setup UI
        self.layout.addWidget(self.qtNameLineEdit)
        self.layout.addWidget(self.qtMatchNameLineEdit)
        self.layout.addWidget(self.qtCategoryTree)

        self.qtAttributesGroupBox = QtWidgets.QGroupBox()
        self.qtAttributesGroupBox.setTitle("Ingredient's Attributes")
        self.qtAttributesGroupBoxLayout = QtWidgets.QGridLayout()
        self.qtAttributesGroupBox.setLayout(self.qtAttributesGroupBoxLayout)
        self.qtAttributesGroupBoxLayout.addWidget(self.qtIsVeganCombo, 0, 0, 1, 2)
        self.qtAttributesGroupBoxLayout.addWidget(self.qtIsMeatReplacementChk, 1, 0, 1, 2)
        self.qtAttributesGroupBoxLayout.addWidget(QtWidgets.QLabel("Protein supply (g/100g)"), 2, 0, 1, 1)
        self.qtAttributesGroupBoxLayout.addWidget(self.qtProteinContribution, 2, 1, 1, 1)
        self.qtAttributesGroupBoxLayout.addWidget(self.qtIngredientAvailability, 3, 0, 1,2)

        self.layout.addWidget(self.qtAttributesGroupBox)
        self.layout.addWidget(self.qtButtonBox)

        if self.topItemDic:
            self.addCategoryItems()
        self.qtCategoryTree.customContextMenuRequested.connect(self.contextMenu)

    def addCategoryItems(self):
        topItems = []
        for Family in self.topItemDic:
            qtFamilyItem = QtWidgets.QTreeWidgetItem([Family])
            qtFamilyItem.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
            if Family == 'Viande':
                qtFamilyItem.setIcon(0, self.ui['icons']['viande'])
                color = self.ui['uiTheme']['meat_bg']
            elif Family == 'Légumes':
                qtFamilyItem.setIcon(0, self.ui['icons']['legume'])
                color = self.ui['uiTheme']['vegetable_bg']
            elif Family == 'Féculents':
                qtFamilyItem.setIcon(0, self.ui['icons']['feculent'])
                color = self.ui['uiTheme']['starch_bg']
            else:
                color = self.ui['uiTheme']['other_bg']
            qtFamilyItem.setBackground(0, color)

            topItems.append(qtFamilyItem)
            for category in self.topItemDic[Family]:
                qtCategoryItem = QtWidgets.QTreeWidgetItem(qtFamilyItem, [category])
                qtCategoryItem.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
                qtCategoryItem.setBackground(0, color)

        self.qtCategoryTree.addTopLevelItems(topItems)

    def contextMenu(self, position):
        position = self.qtCategoryTree.viewport().mapToGlobal(position)
        self.qtCategoryMenu = QtWidgets.QMenu(self)
        qtManageCategories = QtGui.QAction(self.ui['icons']['edit'], 'Editer les categories')
        qtManageCategories.triggered.connect(self.manageCategories)
        self.qtCategoryMenu.addAction(qtManageCategories)
        self.qtCategoryMenu.exec(position)

    def manageCategories(self): #TODO
        print('managing categories')
        raise Exception("TODO")

    def getTopItems(self):
        ingredientDb = Recette.IngredientList()
        categories = ingredientDb.returnCategories() #TODO


class RecipeWindowContent(RecipeContentWidget): # TODO
    """
    Display calculated attributes
    Add Ingredient
    recompute attributes from db and before saving
    """
    def __init__(self, parent, ui):
        super().__init__(parent, ui)
        self.parent = parent
        self.setConnections()
        self.editMode = False
        self.recipeObj = None
        self.clear()

    def setConnections(self):
        self.qtIngredients.customContextMenuRequested.connect(self.ingredientContextMenu)
        self.qtPreparationTimeSpin.valueChanged.connect(self.setFullTime)
        self.qtCookingTimeSpin.valueChanged.connect(self.setFullTime)
        self.qtButtonBox.accepted.connect(self.checkAndAccept)
        self.qtButtonBox.rejected.connect(self.reject)
        self.qtEditButton.clicked.connect(lambda: self.parent.recipeContent("Edit"))
        self.qtCloseButton.clicked.connect(self.reject)

    def ingredientContextMenu(self, position):
        position = self.qtIngredients.viewport().mapToGlobal(position)
        item = self.qtIngredients.currentItem()
        menu = QtWidgets.QMenu(self)
        editIngredients = QtGui.QAction(self.ui['icons']['edit'], 'Edit Ingredients')
        # replaceMenuAction = QtGui.QAction(self.ui['icons']['replace'], 'Replace Selected Menu')
        editIngredients.triggered.connect(self.editIngredients)
        # editIngredients.triggered.connect(
        #     lambda: self.editIngredients(item.text(0), False, item.data(0, QtCore.Qt.ItemDataRole.UserRole)))
        menu.addAction(editIngredients)
        menu.exec(position)

    def editIngredients(self):
        #switch to ingredients tab and lock
        #each item is not selected not checked
        #additional column with weight / nbr available
        #validation / cancel button
        print("edit ingredient mode")
        self.parent.editRecipeIngredientMode()

    def setFullTime(self):
        preparationTime = self.qtPreparationTimeSpin.value()
        cookingTime = self.qtCookingTimeSpin.value()
        fullTime = (preparationTime + cookingTime) * 60
        fullTime = time.strftime("%H h : %M min", time.gmtime(fullTime))
        self.qtCookingFullTimeLineEdit.setText(fullTime)

    def setEditMode(self, recipeObj, editMode='Display'):
        self.validationButton.setText('Save Recipe')
        self.clear()
        if editMode == 'Add':
            self.setUiEnabled(True)
            self.qtButtonBox.show()
            self.qtDisplayButtonsWidget.hide()
            self.editMode = False
            self.recipeObj = None
        else:
            self.setDatas(recipeObj)
            self.recipeObj = recipeObj
            self.editMode = editMode
            if editMode == "Edit":
                self.setUiEnabled(True)
                self.qtButtonBox.show()
                self.qtDisplayButtonsWidget.hide()
            else: # editMode == 'Display'
                self.setUiEnabled(False)
                self.qtButtonBox.hide()
                self.qtDisplayButtonsWidget.show()

    def setDatas(self, recipeObj): # TODO
        self.qtNameLineEdit.setText(recipeObj.name)
        self.qtMatchNameLineEdit.setText(str(recipeObj.match_name))
        # self.qtCategoryTree = QtWidgets.QTreeWidget()
        for type in [self.qtStarterTypeCheckBox, self.qtDishTypeCheckBox, self.qtDessertTypeCheckBox, self.qtSauceTypeCheckBox]:
            if type.text() in recipeObj.type:
                type.setChecked(True)
        item = QtWidgets.QTreeWidgetItem([recipeObj.origin])
        self.qtOriginTree.addTopLevelItem(item)
        self.qtTagsLineEdit.setText(', '.join(recipeObj.tags))

        # recipe content
        # TODO is empty string from db if no ingredient saved
        # ingredientList = []
        print(recipeObj.ingredients, 'recipeObj ingredients')
        print('--> recipeObj ingredients', [(x.name, x.size) for x in recipeObj.ingredients])
        for ingredient in recipeObj.ingredients:
            attrs = {'id': ingredient.id,
                     'size': ingredient.size,
                     }
            ingredientTmp = Recette.Ingredient(attrs, False)
            ingredientTmp = Recette.copyIngredientObj(ingredientTmp, ingredient)
            item = QtWidgets.QTreeWidgetItem([ingredientTmp.name, str(ingredientTmp.size)])
            item.setData(0, QtCore.Qt.ItemDataRole.UserRole, ingredientTmp)
            self.qtIngredients.addTopLevelItem(item)
        #     ingredientList.append(ingredient)
        # print(ingredientList)

        self.qtBeforeRecipeText.setHtml(recipeObj.before_recipe)
        self.qtRecipeText.setHtml(recipeObj.recipe)
        suggestionList = []
        for suggestion in recipeObj.suggestion:
            item = QtWidgets.QTreeWidgetItem([suggestion])
            suggestionList.append(suggestion)
        self.qtSuggestionTree.addTopLevelItems(suggestionList)
        self.qtNoteText.setText(recipeObj.notes)
        fileList = []
        for fileName in recipeObj.files:
            item = QtWidgets.QTreeWidgetItem([fileName])
            fileList.append(fileName)
        self.qtFilesTree.addTopLevelItems(fileList)

        # # recipe meta
        self.qtCookingTimeSpin.setValue(recipeObj.cooking_time)
        self.qtPreparationTimeSpin.setValue(recipeObj.preparation_time)
        # # self.qtCookingFullTimeLineEdit = QtWidgets.QLineEdit()
        self.qtIsBestReheatedCheckBox.setChecked(recipeObj.is_best_reheated)
        if(recipeObj.is_tested == False):
            self.qtRatingRadio0.setChecked(True)
        elif(recipeObj.is_favorite == True):
            self.qtRatingRadio5.setChecked(True)
            self.qtFavoriteCheckBox.setChecked(True)
        else:
            idx = [None, self.qtRatingRadio1, self.qtRatingRadio2, self.qtRatingRadio3, self.qtRatingRadio4, self.qtRatingRadio5]
            idx = idx[recipeObj.rating]
            idx.setChecked(True)
        self.qtRecipeIsWipCheckBox.setChecked(recipeObj.is_wip)



    def extractDatasFromUi(self):  #TODO
        #TODO
        # conform datas to recipeObj
        # conform match_name => signal on modification end with popup
        # conform tags => signal on modification end with popup
        # finish data recup
        # ingredients should be tupple (100g * ingredient)

        def getTreeTopItems(tree, type=None):
            result = []
            topItems = tree.topLevelItemCount()
            for topItem in range(topItems):
                topItem = tree.topLevelItem(topItem)
                if type == 'ingredient':
                    obj = topItem.data(0, QtCore.Qt.ItemDataRole.UserRole)
                    obj.size = str(topItem.text(1))
                    result.append(obj)
                else:
                    result.append(topItem.text(0))
            return result

        datas = {}
        if(self.recipeObj):
            datas['id'] = self.recipeObj.id
        datas['name'] = self.qtNameLineEdit.text().strip()
        datas['match_name'] = self.qtMatchNameLineEdit.text().strip()
        datas['category_id'] = [self.qtCategoryTree.item(idx) for idx in range(self.qtCategoryTree.topLevelItemCount())]
        types = []
        if self.qtStarterTypeCheckBox.isChecked() == True:
            types.append('Starter')
        if self.qtDishTypeCheckBox.isChecked() == True:
            types.append('Dish')
        if self.qtDessertTypeCheckBox.isChecked() == True:
            types.append('Dessert')
        if self.qtSauceTypeCheckBox.isChecked() == True:
            types.append('Sauce')
        datas['type'] = types
        datas['origin'] = getTreeTopItems(self.qtOriginTree)
        datas['tags'] = self.qtTagsLineEdit.text().strip()
        datas['ingredients'] = getTreeTopItems(self.qtIngredients, 'ingredient')
        datas['before_recipe'] = self.qtBeforeRecipeText.toHtml().strip()
        datas['recipe'] = self.qtRecipeText.toHtml().strip()
        datas['suggestion'] = getTreeTopItems(self.qtSuggestionTree)
        datas['notes'] = self.qtNoteText.toHtml().strip()
        datas['files'] = getTreeTopItems(self.qtFilesTree)
        datas['cooking_time'] = self.qtCookingTimeSpin.value()
        datas['preparation_time'] = self.qtPreparationTimeSpin.value()
        datas['is_best_reheated'] = int(self.qtIsBestReheatedCheckBox.isChecked())

        idx = 1
        for i in [self.qtRatingRadio1, self.qtRatingRadio2, self.qtRatingRadio3, self.qtRatingRadio4,
               self.qtRatingRadio5]:
            if(i.isChecked()):
                datas['rating'] = idx
                break
            idx += 1
        datas['rating'] = idx
        if(self.qtRatingRadio0.isChecked()):
            datas['rating'] = -1
        if(self.qtFavoriteCheckBox.isChecked()):
            datas['rating'] = 10


        datas['is_wip'] = int(self.qtRecipeIsWipCheckBox.isChecked())
        print(datas)
        return datas

    def checkAndAccept(self):#TODO
        datas = self.extractDatasFromUi()
        if(datas['name'] != '' and datas['type'] != []):
            self.parent.addRecipeProcess(datas)
        else:
            self.validationButton.setText("Invalid Recipe")

    def reject(self): #TODO
        print("rejecting right now")
        self.parent.exitRecipeContent()


class ImportExportWindow(QtWidgets.QDialog):
    def __init__(self, parentFunctionCall, ui):
        super().__init__()
        self.parentFunctionCall = parentFunctionCall
        self.ui = ui
        self.mode = 'import'
        self.setWindowTitle("Import / Export to Database")
        if self.ui['icons'] is not None:
            self.setWindowIcon(self.ui['icons']['menu'])
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.resize(750, 200)

        # UI Elements
        self.qtImportTab = QtWidgets.QWidget()
        self.qtExportTab = QtWidgets.QWidget()
        self.fileLabel = QtWidgets.QLabel("Importing from file :")
        self.comboLabel = QtWidgets.QLabel("Setting data to :")
        self.qtFilePath = QtWidgets.QLineEdit()
        self.qtFilePath.setPlaceholderText('File path')
        self.qtBrowseFilePath = QtWidgets.QPushButton("Browse")
        self.qtDataCombo = QtWidgets.QComboBox()
        self.qtDataCombo.addItems(['Ingredients', 'Recipe', 'Stocks'])
        self.qtMakeBackupChekbox = QtWidgets.QCheckBox('Make backup before modifications')

        # UI Accept / Reject Buttons
        self.qtButtonBox = QtWidgets.QDialogButtonBox()
        self.qtButtonBox.addButton("Process", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.qtButtonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        self.qtButtonBox.accepted.connect(self.accept)
        self.qtButtonBox.rejected.connect(self.reject)
        if self.parentFunctionCall:
            # data = self.getDatas()
            # self.accepted.connect(lambda : self.parentFunctionCall(data))
            self.accepted.connect(self.returnDatas)

        #setup UI
        self.qtIOTab = QtWidgets.QTabWidget()
        self.qtIOTab.addTab(self.qtImportTab, "Import Data")
        self.qtImportTabLayout = QtWidgets.QVBoxLayout()
        self.qtImportTab.setLayout(self.qtImportTabLayout)
        self.qtIOTab.addTab(self.qtExportTab, "Export Data")
        self.qtExportTabLayout = QtWidgets.QVBoxLayout()
        self.qtExportTab.setLayout(self.qtExportTabLayout)

        self.layout.addWidget(self.qtIOTab)
        self.layout.addWidget(self.qtButtonBox)
        self.switchMode()
        self.setConnections()


    def setConnections(self):
        self.qtBrowseFilePath.clicked.connect(self.browseFile)
        self.qtIOTab.currentChanged.connect(self.switchMode)

    def switchMode(self):
        self.qtFilePath.setText('')
        if self.qtIOTab.currentIndex() == 0:
            self.mode = 'import'
            self.fileLabel.setText("Importing from file :")
            self.comboLabel.setText("Setting data to :")
            self.qtImportTabLayout.addWidget(self.fileLabel)
            self.qtImportTabLayout.addWidget(self.qtFilePath)
            self.qtImportTabLayout.addWidget(self.qtBrowseFilePath)
            self.qtImportTabLayout.addWidget(self.comboLabel)
            self.qtImportTabLayout.addWidget(self.qtDataCombo)
            self.qtImportTabLayout.addWidget(self.qtMakeBackupChekbox)
        else:
            self.mode = 'export'
            self.fileLabel.setText("Saving to file :")
            self.comboLabel.setText("Exporting data from :")
            self.qtExportTabLayout.addWidget(self.comboLabel)
            self.qtExportTabLayout.addWidget(self.qtDataCombo)
            self.qtExportTabLayout.addWidget(self.fileLabel)
            self.qtExportTabLayout.addWidget(self.qtFilePath)
            self.qtExportTabLayout.addWidget(self.qtBrowseFilePath)

    def browseFile(self):
        if self.mode == 'import':
            fileName, fileType = QtWidgets.QFileDialog.getOpenFileName()
        else:
            fileName, fileType = QtWidgets.QFileDialog.getSaveFileName()
        if fileName == '':
            return
        if fileName.endswith('.ods') is False:
            raise Exception('Wrong File Type, only .ods file are supported')
        self.qtFilePath.setText(fileName)

    def returnDatas(self):
        data = {'filePath': self.qtFilePath.text(),
                'db': self.qtDataCombo.currentText(),
                'mode': self.mode,
                'backup': bool(self.qtMakeBackupChekbox.checkState().value)}
        self.parentFunctionCall(data)


class EditStockedFoodWindow(QtWidgets.QDialog):
    # def __init__(self, parent, icons, uiTheme, parentItems, defaultParent, edit):
    def __init__(self, parent, defaultParent, edit, stockObj):
        super().__init__()
        self.parent = parent
        self.ui = parent.ui
        self.parentItems = parent.stockedFoodCategories
        self.edit = edit
        self.stockObj = stockObj
        self.units = ['pers', 'x', 'kg', 'g', 'L']

        self.setWindowTitle("Add Stocked Food")
        self.setWindowIcon(self.ui['icons']['menu'])
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        #UI Elements
        self.qtNameLineEdit = QtWidgets.QLineEdit()
        self.qtNameLineEdit.setPlaceholderText('Nom')
        if self.stockObj:
            self.qtNameLineEdit.setText(self.stockObj.name)
        self.qtParentItemCombo = QtWidgets.QComboBox()
        items = [x.text(0) for x in self.parentItems]
        self.qtParentItemCombo.addItems(items)
        self.qtIngredientsTree = QtWidgets.QTreeWidget()
        self.qtIngredientsTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Ingredients']))
        self.qtDateIsCreationRadio = QtWidgets.QRadioButton("Date de création / achat")
        self.qtDateIsLimitRadio = QtWidgets.QRadioButton("Date Limite")
        self.qtDateIsCreationRadio.setChecked(True)
        self.qtDateCalendar = QtWidgets.QCalendarWidget()
        self.qtServingUnitCombo = QtWidgets.QComboBox()

        self.qtServingUnitCombo.addItems(self.units)
        self.qtServingsQuantitySpinBox = QtWidgets.QSpinBox()
        self.qtServingsQuantitySpinBox.setSuffix(' ' + self.qtServingUnitCombo.currentText())
        self.qtServingsQuantitySpinBox.setValue(3)
        self.qtNumberSpinbox = QtWidgets.QSpinBox()
        self.qtNumberSpinbox.setValue(1)

        #UI Accept / Reject Buttons
        self.qtButtonBox = QtWidgets.QDialogButtonBox()
        confirmLabel = "Add Stocked Food"
        if self.edit is True:
            confirmLabel = "Edit Stocked Food"
        self.qtButtonBox.addButton(confirmLabel, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.qtButtonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        self.qtButtonBox.accepted.connect(self.accept)
        self.qtButtonBox.rejected.connect(self.reject)
        self.accepted.connect(lambda: self.parent.stockedFoodProcess(self))

        #Setup UI
        self.layout.addWidget(self.qtNameLineEdit)
        self.layout.addWidget(self.qtParentItemCombo)
        self.layout.addWidget(self.qtIngredientsTree)
        self.layout.addWidget(self.qtDateIsCreationRadio)
        self.layout.addWidget(self.qtDateIsLimitRadio)
        self.layout.addWidget(self.qtDateCalendar)
        self.unitsLayout = QtWidgets.QGridLayout()
        self.layout.addLayout(self.unitsLayout)
        self.unitsLayout.addWidget(QtWidgets.QLabel("Servings :"), 0, 0)
        self.unitsLayout.addWidget(self.qtServingsQuantitySpinBox, 0, 1)
        self.unitsLayout.addWidget(self.qtServingUnitCombo, 0, 2)
        self.unitsLayout.addWidget(QtWidgets.QLabel("Number:"), 1, 0)
        self.unitsLayout.addWidget(self.qtNumberSpinbox, 1, 1)
        self.layout.addWidget(self.qtButtonBox)

        # Connections
        self.qtServingUnitCombo.currentIndexChanged.connect(self.setServingUnit)
        self.setIngredients()

        if self.edit is True:
            self.setEditValue()

    def setServingUnit(self):
        self.qtServingsQuantitySpinBox.setSuffix(' ' + self.qtServingUnitCombo.currentText())

    def setEditValue(self):
        self.qtNameLineEdit.setText(self.stockObj.name)
        if self.stockObj.dateIsExpirationDate is True:
            self.qtDateIsLimitRadio.setChecked(True)
        else:
            self.qtDateIsCreationRadio.setChecked(True)

        #set date
        y, m, d = self.stockObj.dateName.split('.')
        self.qtDateCalendar.setSelectedDate(QtCore.QDate(int(y), int(m), int(d)))
        self.qtServingsQuantitySpinBox.setValue(self.stockObj.servingsQuantity)
        idx = self.units.index(self.stockObj.servingsUnit)
        self.qtServingUnitCombo.setCurrentIndex(idx)
        self.qtNumberSpinbox.setValue(self.stockObj.nbr)

    def setIngredients(self):
        print(self.stockObj.__dict__)
        if isinstance(self.stockObj, Recette.Ingredient) is True:
            ingredientList = [self.stockObj]
        else:
            ingredientList = self.stockObj.ingredients
        items = []
        for ingredient in ingredientList:
            qtItem = QtWidgets.QTreeWidgetItem([ingredient.name])
            items.append(qtItem)
        self.qtIngredientsTree.addTopLevelItems(items)


class AddMealToMenu(QtWidgets.QDialog):
    def __init__(self, parent, ui, dayName, meal):
        super().__init__()
        self.parent = parent
        self.ui = ui
        self.setWindowTitle("Ajouter un repas à {}".format(dayName))
        self.setWindowIcon(self.ui['icons']['menu'])
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        #UI Elements
        label = QtWidgets.QLabel(dayName)
        lineEdit = QtWidgets.QLineEdit()
        lineEdit.setPlaceholderText('nom du repas à ajouter')
        combo = QtWidgets.QComboBox()
        combo.addItems(['Avant', 'Après'])
        meallabel = QtWidgets.QLabel('le {}'.format(meal))

        # UI Accept / Reject Buttons
        self.qtButtonBox = QtWidgets.QDialogButtonBox()
        self.qtButtonBox.addButton("Ok", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.qtButtonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        self.qtButtonBox.accepted.connect(self.accept)
        self.qtButtonBox.rejected.connect(self.reject)

        #Setup Ui
        layout.addWidget(label)
        layout.addWidget(lineEdit)
        layout.addWidget(combo)
        layout.addWidget(meallabel)
        layout.addWidget(self.qtButtonBox)

        #Connections
        self.accepted.connect(lambda: self.parent.AddMealToMenuProcess(lineEdit.text(), combo.currentIndex()))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, libPath='E:/Scripts/Python/Recette/recette liste.ods', *args, **kwargs):
        super().__init__(*args, **kwargs)

        # init datas
        self.datas = Recette.Datas(libPath)
        self.libPath = self.datas.dbPath
        self.ingredientsDb = self.datas.ingredients
        self.recipeDb = self.datas.recipes

        #init ui parms
        self.ui = {
            'icons': getIcons(self.libPath),
            'images': getImages(self.libPath),
            'uiTheme': getTheme()
        }
        self.mode = "editMenu"

        self.qtGoalAndNotesWidget = GoalsAndNotesWidget(self.ui)
        self.qtMenuWidget = MenuWidget(self.ui)
        self.qtGroceriesWidget = GroceriesWidget(self.ui)
        self.qtIngredientWidget = IngredientWidget(self.ui)
        self.qtRecipeWidget = RecipeWidget(self.ui)
        self.qtStockWidget = StockWidget(self.ui)

        def setupUi():
            self.setWindowIcon(self.ui['icons']['menu'])
            self.setWindowTitle("Recipes")

            # ----->>User Splitter and Main Widgets
            self.qtMainSplitter = QtWidgets.QSplitter()
            self.setCentralWidget(self.qtMainSplitter)
            self.qtPrimaryWidget = QtWidgets.QWidget()
            self.qtSecondaryWidget = QtWidgets.QWidget()
            self.qtMainSplitter.addWidget(self.qtPrimaryWidget)
            self.qtMainSplitter.addWidget(self.qtSecondaryWidget)
            self.qtPrimaryWidgetLayout = QtWidgets.QGridLayout()
            self.qtSecondaryWidgetLayout = QtWidgets.QGridLayout()
            self.qtPrimaryWidget.setLayout(self.qtPrimaryWidgetLayout)
            self.qtSecondaryWidget.setLayout(self.qtSecondaryWidgetLayout)

            # ----->>ToolBar
            self.qtToolbar = QtWidgets.QToolBar('tools')
            self.addToolBar(self.qtToolbar)
            self.qtAddIngredient = QtGui.QAction("Add Ingredient")
            self.qtEditIngredients = QtGui.QAction("Edit Ingredients")
            self.qtAddRecipe = QtGui.QAction("Add Recipe")
            self.qtEditRecipes = QtGui.QAction("Edit Recipes")
            self.qtImportExportData = QtGui.QAction('Import - Export Data to Ods')
            self.qtSetLibPath = QtGui.QAction('Set Database Path')
            self.qtToolbar.addAction(self.qtAddIngredient)
            self.qtToolbar.addAction(self.qtEditIngredients)
            self.qtToolbar.addAction(self.qtAddRecipe)
            self.qtToolbar.addAction(self.qtEditRecipes)
            self.qtToolbar.addAction(self.qtImportExportData)
            self.qtToolbar.addAction(self.qtSetLibPath)
            """
            # ----->>HEADER
            self.headerPaneWidget = QtWidgets.QWidget()
            self.headerPaneWidgetLayout = QtWidgets.QVBoxLayout()
            self.headerPaneWidget.setLayout(self.headerPaneWidgetLayout)
            self.qtCalendar = QtWidgets.QCalendarWidget()
            self.headerPaneWidgetLayout.addWidget(self.qtCalendar)
            # self.centralLayout.addWidget(self.headerPaneWidget, 0, 0, 1, 2)
            """

            # ----->>Primary Pane
            self.qtMainMenuWidget = QtWidgets.QWidget()
            self.qtMainMenuWidgetLayout = QtWidgets.QVBoxLayout()
            self.qtMainMenuWidget.setLayout(self.qtMainMenuWidgetLayout)
            self.qtEditRecipeWidget = RecipeWindowContent(self, self.ui)


            self.qtLeftPaneTabWidget = QtWidgets.QTabWidget()
            self.qtLeftPaneTabWidget.setTabBarAutoHide(True)
            self.qtLeftPaneTabWidget.addTab(self.qtMainMenuWidget, "Menus")
            self.qtLeftPaneTabWidget.addTab(self.qtEditRecipeWidget, "Edit Recipe")
            self.qtLeftPaneTabWidget.setTabVisible(1, False)
            self.qtPrimaryWidgetLayout.addWidget(self.qtLeftPaneTabWidget)

            self.qtMainMenuWidgetLayout.addWidget(self.qtGoalAndNotesWidget)
            self.qtMainMenuWidgetLayout.addWidget(self.qtMenuWidget)
            self.qtMainMenuWidgetLayout.addWidget(self.qtGroceriesWidget)

            # ----->> Secondary
            self.qtRightPaneTabWidget = QtWidgets.QTabWidget()
            self.qtRightPaneTabWidget.addTab(self.qtIngredientWidget, 'Ingredients')
            self.qtRightPaneTabWidget.addTab(self.qtRecipeWidget, 'Recipe')
            self.qtRightPaneTabWidget.addTab(self.qtStockWidget, 'Stocks')
            self.qtSecondaryWidgetLayout.addWidget(self.qtRightPaneTabWidget)

        setupUi()
        self.initDataAndPopulate()
        self.setConnections()

    #####
    # Initialisation
    #####
    def initDataAndPopulate(self): #TODO
        # TODO Clear Ui before
        #
        self.blockSignals(True)
        self.setIngredients()
        self.recipeDb = None
        print('')
        print('')
        print('----------------->> INGREDIENTS DONE')
        print('')
        print('')
        self.setRecipe()

        ################
        #recipe bug !! Invalid ingredients
        ################

        # self.setStockedFood()
        # self.setGoals()
        # self.readNotes()
        self.initMenus()
        self.menuChanged()  # init liste des courses
        self.blockSignals(False)


    def setIngredients(self):
        def createQtItem(ingredientObj, parents, color=None):
            parents = parents[0].obj.qtItem
            print('parentList: {}, obj: {}'.format(parents, ingredientObj.name))
            qtItems = []
            for parent in parents:
                qtItem = QtWidgets.QTreeWidgetItem(parent, [ingredientObj.name])
                qtItem.setCheckState(0, QtCore.Qt.CheckState.Checked)
                qtItem.setData(0, QtCore.Qt.ItemDataRole.UserRole, ingredientObj)
                qtItem.setFlags(qtItem.flags() | QtCore.Qt.ItemFlag.ItemIsAutoTristate)
                ingredientObj.qtItem.append(qtItem)
                # self.ingredientsDb.ingredientDic[ingredientObj.name] = ingredientObj
                if color:
                    qtItem.setBackground(0, color)
                qtItems.append(qtItem)
            return qtItems, ingredientObj

        if self.ingredientsDb is None:
            self.ingredientsDb = Recette.IngredientList(self.libPath)

        # self.qtIngredientDic = {
        # 'viande':{},
        # 'légume':{},
        # 'féculent':{},
        # 'divers':{}
        # }

        # topLevelItems = {
        # 'viande':[],
        # 'légume':[],
        # 'féculent':[],
        # 'divers':[]
        # }
        # self.categoryDict = {}
        print(self.ingredientsDb.ingredientTree)
        # for ingredientObj in self.ingredientsDb.ingredientList:
        #     categoryList = [None] if ingredientObj.category is None else ingredientObj.category
        #     for family in ingredientObj.family:
        #         print('New Ingredient : ', ingredientObj.name, ingredientObj.family, categoryList)
        #         color = self.ui['uiTheme']['{}_bg'.format(family)]
        #         for category in categoryList:
        #             # if category is not None:
        #             #     # parent = self.qtIngredientDic[family][category][0]
        #             #     # categoryId = ingredientObj.categoryId[ingredientObj.category.index(category)]
        #             #     parent = self.ingredientsDb.returnParentCategoryObj(ingredientObj, category)
        #             #     print(parent)
        #             #     parentQtItem = parent.qtItem
        #             #     print(parentQtItem, ingredientObj.name, parent, parent.name)
        #             #     # qtItem, ingredientObj = createQtItem(ingredientObj, parentQtItem, color)
        #             #     qtItem, ingredientObj = createQtItem(ingredientObj, None, color)
        #             # else:
        #             qtItem, ingredientObj = createQtItem(ingredientObj, None, color)
        #             topLevelItems[family].append(qtItem)
        #             # if ingredientObj.name in self.qtIngredientDic[family]:
        #             #     self.qtIngredientDic[family][ingredientObj.name].append(qtItem)
        #             # else:
        #             #     self.qtIngredientDic[family][ingredientObj.name] = [qtItem]
        # # parenting qtitem
        # for ingredientObj in self.ingredientsDb.ingredientList:
        #     categoryList = [None] if ingredientObj.category is None else ingredientObj.category
        #     for family in ingredientObj.family:
        #         for category in categoryList:
        #             if category is not None:
        #                 parent = self.ingredientsDb.returnParentCategoryObj(ingredientObj, category)
        #                 parentQtItem = parent.qtItem
        #                 # TODO
        #             else:
        #                 pass #TODO

        treeAsList = self.ingredientsDb.returnTreeAsList()
        currentFamily = None
        topLevelItems = {}
        for node in treeAsList:
            if node.id < 0:
                if node.id == -1: #root
                    continue
                elif node.id == -2: #meat
                    currentFamily = 'meat'
                elif node.id == -3: #vegetable
                    currentFamily = 'vegetable'
                elif node.id == -4: #starch
                    currentFamily = 'starch'
                elif node.id == -5: #other
                    currentFamily = 'other'
                color = self.ui['uiTheme']['{}_bg'.format(currentFamily)]
                qtItem = QtWidgets.QTreeWidgetItem(None, [node.obj.name])
                qtItem.setBackground(0, color)
                node.obj.qtItem = [qtItem]
                topLevelItems[currentFamily] = qtItem
            else:
                parents = node.parents
                qtItems, ingredientObj = createQtItem(node.obj, parents, color)

        for family, widget in self.qtIngredientWidget.ingredientWidgetList:
            topList = topLevelItems[family].takeChildren()
            root = widget.invisibleRootItem()
            root.addChildren(topList)
            widget.expandAll()
            widget.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)

    def setRecipe(self):
        def getBadges(recipeObj):
            def getBadge(name):
                badge = QtWidgets.QLabel('')
                badge.setPixmap(self.ui['images'][name])
                return badge

            def getAttributeBadge(attributeVal, value, name, addNull=True):
                if attributeVal == value:
                    return getBadge(name)
                else:
                    if addNull is True:
                        return getBadge('null')

            badges = []
            extraInfos = []
            badges.append(getAttributeBadge(recipeObj.is_favorite, True, 'star'))
            if recipeObj.rating > 0:
                rating = f'rating{recipeObj.rating}'
                badges.append(getAttributeBadge(recipeObj.rating, recipeObj.rating, rating))
            else:
                badges.append(getAttributeBadge(recipeObj.rating, -1, 'null'))
            if recipeObj.ui_speed == 'fast':
                badges.append(getAttributeBadge(recipeObj.ui_speed, 'fast', 'fast', False))
            elif recipeObj.ui_speed == 'slow':
                badges.append(getAttributeBadge(recipeObj.ui_speed, 'slow', 'slow', False))
            else:
                badges.append(getAttributeBadge(recipeObj.ui_speed, 'slow', 'slow', True))
            badges.append(getAttributeBadge(recipeObj.is_vegan, True, 'vegan'))

            extraInfos.append(getAttributeBadge(recipeObj.special_ingredient, True, 'warning', False))
            extraInfos.append(getAttributeBadge(recipeObj.needs_before_prep, True, 'dayBefore', False))
            extraInfos.append(getAttributeBadge(recipeObj.is_best_reheated, True, 'dayBefore', False))
            extraInfos.append(getAttributeBadge(recipeObj.is_wip, True, 'edit', False))
            extraInfos.append(getAttributeBadge(recipeObj.is_tested, True, 'ok', False))
            extraInfos.append(getAttributeBadge(recipeObj.error, True, 'clear', False))
            print(badges, extraInfos)
            return badges, extraInfos

        self.qtRecipeWidget.blockSignals(True)
        print('-------->>> set Recipe')
        print(self.qtRecipeWidget, type(self.qtRecipeWidget))
        self.qtRecipeWidget.qtTreeRecipe.clear()
        if self.recipeDb is None:
            self.recipeDb = Recette.RecipeList(self.libPath, True, self.ingredientsDb.ingredientList)
        qtRecipeList = []
        qtRecipeSubWidgetList = []
        qtRecipeInfosSubWidgetList = []
        self.categoryDict = {}
        for recipeObj in self.recipeDb.recipeList:
            if recipeObj.is_favorite:
                recipeObj.is_favorite_icon = self.ui['icons']['star']
            else:
                recipeObj.is_favorite_icon = self.ui['icons']['null']
            if recipeObj.category is None:
                nbrCategory = 1
            else:
                nbrCategory = max(1, len(recipeObj.category))
            recipeObj.qtitems = []
            for i in range(nbrCategory):
                labelList = [recipeObj.name, '', ', '.join([ing.name for ing in recipeObj.ingredients]), str(recipeObj.preparation_time), str(recipeObj.total_time), '']
                print('-> new qt item : ',
                      labelList)
                qtitem = QtWidgets.QTreeWidgetItem(labelList)
                qtitem.setData(0, QtCore.Qt.ItemDataRole.UserRole, recipeObj)

                qtitemSubWidget = QtWidgets.QWidget()
                qtitemSubWidgetLayout = QtWidgets.QHBoxLayout()
                qtitemSubWidget.setLayout(qtitemSubWidgetLayout)
                qtitemInfosSubWidget = QtWidgets.QWidget()
                qtitemInfosSubWidgetLayout = QtWidgets.QHBoxLayout()
                qtitemInfosSubWidget.setLayout(qtitemInfosSubWidgetLayout)

                badges, extraInfos = getBadges(recipeObj)
                for badge in badges:
                    qtitemSubWidgetLayout.addWidget(badge)
                print('>>>>>>>>>>>>  extra infos', extraInfos)
                for extraInfo in extraInfos:
                    print(extraInfo)
                    if extraInfo:
                        qtitemInfosSubWidgetLayout.addWidget(extraInfo)

                if recipeObj.category is not None:
                    ############
                    category = recipeObj.category[i]
                    if category in self.categoryDict:
                        parent = self.categoryDict[category]
                    else:
                        parent = QtWidgets.QTreeWidgetItem([category, '', '', '', '', ''])
                        self.categoryDict[category] = parent
                        qtRecipeList.append(parent)
                        qtRecipeSubWidgetList.append(qtitemSubWidget)
                        qtRecipeInfosSubWidgetList.append(qtitemInfosSubWidget)
                    parent.addChild(qtitem)
                ############
                else:
                    qtRecipeList.append(qtitem)
                    qtRecipeSubWidgetList.append(qtitemSubWidget)
                    qtRecipeInfosSubWidgetList.append(qtitemInfosSubWidget)

                recipeObj.qtitems.append(qtitem)

        self.qtRecipeWidget.qtTreeRecipe.addTopLevelItems(qtRecipeList)

        idx = 0
        for qtitem in qtRecipeList:
            self.qtRecipeWidget.qtTreeRecipe.setItemWidget(qtitem, 1, qtRecipeSubWidgetList[idx])
            self.qtRecipeWidget.qtTreeRecipe.setItemWidget(qtitem, 5, qtRecipeInfosSubWidgetList[idx])
            idx += 1

        self.qtRecipeWidget.qtTreeRecipe.expandAll()
        self.qtRecipeWidget.qtTreeRecipe.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.qtRecipeWidget.blockSignals(False)

    def setStockedFood(self): #TODO WIP
        self.stocksDb = Recette.StockList()
        self.stockedFoodCategories = [QtWidgets.QTreeWidgetItem([x, '', '', '']) for x in self.stocksDb.categories]
        for stockObj in self.stocksDb.stockList:
            idx = self.stocksDb.categories.index(stockObj.category)
            parent = self.stockedFoodCategories[idx]
            date = stockObj.dateName
            if bool(stockObj.dateIsExpirationDate) is True:
                date = 'max: '+date
            qtItem = QtWidgets.QTreeWidgetItem(parent, [stockObj.name, '{} {}'.format(stockObj.servingsQuantity, stockObj.servingsUnit), str(stockObj.nbr), date])
            qtItem.setData(0, QtCore.Qt.ItemDataRole.UserRole, stockObj)
            stockObj.qtItem = qtItem

        self.qtStockWidget.qtStockedCookedTree.addTopLevelItems(self.stockedFoodCategories)
        self.qtStockWidget.qtStockedCookedTree.expandAll()
        self.qtStockWidget.qtStockedCookedTree.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)
        print('columns')
        self.qtStockWidget.qtStockedCookedTree.resizeColumnToContents(True)
        # self.qtTreeRecipe.header().setMinimumSectionSize(10)
        # self.qtTreeRecipe.header().resizeSection(2, 10)
        # self.qtTreeRecipe.header().resizeSection(3, 40)
        # self.qtTreeRecipe.header().resizeSection(4, 100)
        # self.qtTreeRecipe.header().setStretchLastSection(False)
        # self.qtTreeRecipe.setSizePolicy()

    def setGoals(self):
        print('set goals')
        self.goalDb = Recette.GoalList(self.libPath)
        qtItemList = []
        for goalObj in self.goalDb.goalList:
            qtItem = QtWidgets.QTreeWidgetItem([str(goalObj.nbr), goalObj.name, goalObj.note])
            qtItem.setCheckState(1, QtCore.Qt.CheckState.Unchecked)
            print(goalObj.name, goalObj.nbr, goalObj.note)
            goalObj.qtItem = qtItem
            qtItemList.append(qtItem)
        self.qtGoalAndNotesWidget.qtGoalsTreeWidget.addTopLevelItems(qtItemList)
        self.qtGoalAndNotesWidget.qtGoalsTreeWidget.expandAll()
        self.qtGoalAndNotesWidget.qtGoalsTreeWidget.sortItems(1, QtCore.Qt.SortOrder.AscendingOrder)

    def readNotes(self):
        # print('reading notes')
        notes = Recette.Notes(os.path.split(self.libPath)[0] + '/notes.html')
        content = notes.read()
        self.qtGoalAndNotesWidget.qtNotesTextEdit.setHtml(content)

    def createMenuQtItem(self, parent, label):
        qtItem = QtWidgets.QTreeWidgetItem(parent, label)
        qtItem.setData(1, QtCore.Qt.ItemDataRole.UserRole, [])
        qtItem.setFlags(qtItem.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
        qtItem.setCheckState(2, QtCore.Qt.CheckState.Unchecked)
        return qtItem

    def initMenus(self):
        self.dayDb = Recette.DayList()
        qtDaysList = []
        for dayObj in self.dayDb.dayList:
            qtDay = QtWidgets.QTreeWidgetItem([dayObj.name, "", ""])
            qtDaysList.append(qtDay)

            qtItem = self.createMenuQtItem(qtDay, ['Midi', '', ''])
            dayObj.qtItems.append(qtItem)
            qtItem = self.createMenuQtItem(qtDay, ['Soir', '', ''])
            dayObj.qtItems.append(qtItem)
        self.qtMenuWidget.qtTreeMenu.addTopLevelItems(qtDaysList)
        self.qtMenuWidget.qtTreeMenu.expandAll()

    def setConnections(self):
        #Toolbar
        self.qtAddIngredient.triggered.connect(self.addIngredientDialog)
        self.qtAddRecipe.triggered.connect(lambda:self.recipeContent('Add'))
        self.qtImportExportData.triggered.connect(self.importExportToDbDialog)
        self.qtSetLibPath.triggered.connect(self.setLibPathDialog)

        #Primary Pane
        self.qtGoalAndNotesWidget.qtSaveNotesButton.clicked.connect(self.saveNotes)

        self.qtMenuWidget.qtTreeMenu.itemChanged.connect(self.menuTextChanged)
        self.qtMenuWidget.qtTreeMenu.itemEntered.connect(self.menuTextChanged)
        self.qtMenuWidget.qtTreeMenu.selectionModel().selectionChanged.connect(self.selectIngredientFromMenu)

        # deport to class ?? # TODO
        # self.qtMenuButtonUp.clicked.connect(lambda: self.moveItemMenu(True))
        # self.qtMenuButtonDown.clicked.connect(lambda: self.moveItemMenu(False))

        #Secondary Pane
        self.qtIngredientWidget.qtIngredientFilter.textChanged.connect(self.filterIngredientList)
        # deport to class ?? # TODO
        # self.qtIngredientWidget.qtIngredientCheckAllButton.clicked.connect(lambda: self.checkIngredient('All', 'All', True))
        # self.qtIngredientWidget.qtIngredientCheckNoneButton.clicked.connect(lambda: self.checkIngredient('All', 'All', False))
        # self.qtIngredientWidget.qtIngredientCheckInvertButton.clicked.connect(lambda: self.checkIngredient('All', 'All', -1))
        # self.qtIngredientWidget.qtIngredientSelAllButton.clicked.connect(lambda: self.selIngredient('All', True))
        # self.qtIngredientWidget.qtIngredientSelNoneButton.clicked.connect(lambda: self.selIngredient('All', False))
        # self.qtIngredientWidget.qtIngredientSelInvertButton.clicked.connect(lambda: self.selIngredient('All', -1))

        self.qtIngredientWidget.qtMeatColumnTree.selectionModel().selectionChanged.connect(self.ingredientTreeSelectionChanged)
        self.qtIngredientWidget.qtMeatColumnTree.itemChanged.connect(self.ingredientTreeCheckChanged)
        self.qtIngredientWidget.qtVegetableColumnTree.selectionModel().selectionChanged.connect(self.ingredientTreeSelectionChanged)
        self.qtIngredientWidget.qtVegetableColumnTree.itemChanged.connect(self.ingredientTreeCheckChanged)
        self.qtIngredientWidget.qtStarchColumnTree.selectionModel().selectionChanged.connect(self.ingredientTreeSelectionChanged)
        self.qtIngredientWidget.qtStarchColumnTree.itemChanged.connect(self.ingredientTreeCheckChanged)
        self.qtIngredientWidget.qtOtherColumnTree.selectionModel().selectionChanged.connect(self.ingredientTreeSelectionChanged)
        self.qtIngredientWidget.qtOtherColumnTree.itemChanged.connect(self.ingredientTreeCheckChanged)

        self.qtRecipeWidget.qtFilterByIngredientCheckBox.stateChanged.connect(self.filterRecipe)
        self.qtRecipeWidget.qtFilterByIngredientCombo.currentIndexChanged.connect(self.filterRecipe)
        # deport to class ?? # TODO
        # self.qtRecipeWidget.qtRecipeGroupBox.currentChanged.connect(self.changeTab)
        self.qtRecipeWidget.qtRecipeFilter.textChanged.connect(self.filterRecipe)
        self.qtRecipeWidget.qtTreeRecipe.clicked.connect(self.exitRecipeContent)

        self.qtRecipeWidget.qtTreeRecipe.doubleClicked.connect(lambda: self.recipeContent("Display"))

        #Context Menus
        self.qtIngredientWidget.qtMeatColumnTree.customContextMenuRequested.connect(self.meatContextMenu)
        self.qtIngredientWidget.qtVegetableColumnTree.customContextMenuRequested.connect(self.vegetableContextMenu)
        self.qtIngredientWidget.qtStarchColumnTree.customContextMenuRequested.connect(self.starchContextMenu)
        self.qtIngredientWidget.qtOtherColumnTree.customContextMenuRequested.connect(self.otherContextMenu)
        self.qtRecipeWidget.qtTreeRecipe.customContextMenuRequested.connect(self.recipeContextMenu)
        self.qtMenuWidget.qtTreeMenu.customContextMenuRequested.connect(self.menuContextMenu)
        self.qtMenuWidget.qtTreeMenu.itemChanged.connect(self.menuChanged)
        self.qtStockWidget.qtStockedCookedTree.customContextMenuRequested.connect(self.stockedCookedContextMenu)

    #####
    # DB Actions
    #####
    def addIngredientDialog(self): #TODO a refaire ac vrai categories
        def extractTopItemToList(widget):
            topItems = []
            topCount = widget.topLevelItemCount()
            for i in range(topCount):
                item = widget.topLevelItem(i)
                if item.childCount() > 0:
                    topItems.append(item.text(0))
            return topItems

        for family, widget in self.qtIngredientWidget.ingredientWidgetList:
            print(family)
            if family == 'meat':
                meatTopItem = extractTopItemToList(widget)
            if family == 'vegetable':
                vegetableTopItem = extractTopItemToList(widget)
            if family == 'starch':
                starchTopItem = extractTopItemToList(widget)
            if family == 'other':
                otherTopItem = extractTopItemToList(widget)

        topItemsDic = {
            'meat': meatTopItem,
            'vegetable': vegetableTopItem,
            'starch': starchTopItem,
            'other': otherTopItem,
        }
        self.AddIngredientWindow = EditIngredientWindow(self, self.ui, topItemsDic)
        self.AddIngredientWindow.exec()

    def addIngredientProcess(self):
        print("adding ingredient processing ing")

    def addRecipeProcess(self, datas):
        #TODO update recipeObj
        # copy recipe obj
        newRecipeObj = self.recipeDb.exportDatasToDb(datas)
        print("exit recipe content mode")
        print(self.recipeDb.recipeList)
        if newRecipeObj.id < 0: #TODO Gestion id negatives multiples ?
            #TODO add Id from db
            #rebuild tree ??
            self.recipeDb.recipeList.append(newRecipeObj)
            self.setRecipe()
        else: #edit with id
            for recipeObj in self.recipeDb.recipeList:
                print(recipeObj.id, newRecipeObj.id) #Crash on rename ??
                if recipeObj.id == newRecipeObj.id:
                    idx = self.recipeDb.recipeList.index(recipeObj.name)
                    qtItemList = []
                    for qtItem in recipeObj.qtItems:
                        qtItem.setText([newRecipeObj.name])
                        qtItem.setData(0, QtCore.Qt.ItemDataRole.UserRole, newRecipeObj)
                        qtItemList.append(qtItem)
                    newRecipeObj.qtItems = qtItemList
                    self.recipeDb.recipeList[idx] = newRecipeObj

        print(newRecipeObj.__dict__)
        self.exitRecipeContent()

    def recipeContent(self, editMode='Display'): #TODO
        print("editing recipe in mode {}".format(editMode))
        recipeObj = None
        if editMode in ["Display", "Edit"]:
            recipeObj = self.qtRecipeWidget.qtTreeRecipe.selectedItems()[0]
            print(recipeObj)
            recipeObj = recipeObj.data(0, QtCore.Qt.ItemDataRole.UserRole)
            print(recipeObj)

        if editMode in ["Edit", "Add"]:
            """lock pane tabs"""
            self.mode = "editRecipe"
            self.qtLeftPaneTabWidget.setTabVisible(0, False)
            self.qtRightPaneTabWidget.setTabVisible(1, False)
            self.qtRightPaneTabWidget.setTabVisible(2, False)
        else: #Display
            """auto closes"""
        self.qtLeftPaneTabWidget.setTabVisible(1, True)
        self.qtLeftPaneTabWidget.setCurrentIndex(1)
        self.qtEditRecipeWidget.setEditMode(recipeObj, editMode)

    def exitRecipeContent(self): #TODO
        # To finish
        # Apply result if needed
        self.qtLeftPaneTabWidget.setTabVisible(0, True)
        self.qtLeftPaneTabWidget.setTabVisible(1, False)
        self.qtLeftPaneTabWidget.setTabVisible(0, True)
        self.qtRightPaneTabWidget.setTabVisible(1, True)
        self.qtRightPaneTabWidget.setTabVisible(2, True)
        self.qtLeftPaneTabWidget.setCurrentIndex(0)
        self.qtRightPaneTabWidget.setCurrentIndex(1)

        self.mode = "editMenu"



    def importExportToDbDialog(self):
        self.ImportExportWindow = ImportExportWindow(self.importExportToDbProcess, self.ui)
        self.ImportExportWindow.exec()

    def importExportToDbProcess(self, data):
        # if data['db'] == 'Ingredients':
        #     db = self.ingredientsDb
        # elif data['db'] == 'Recipe':
        #     db = self.recipeDb
        # else:
        #     db = self.stocksDb
        Recette.importExportDb(data, self.libPath)
        self.initDataAndPopulate()

    def editRecipeIngredientMode(self): #TODO
        # switch to ingredients tab and lock
        # each item is not selected not checked
        # additional column with weight / nbr available
        # validation / cancel button
        print("mode on")

    def setLibPathDialog(self):
        fileName, fileType = QtWidgets.QFileDialog.getOpenFileName()
        print(fileName, fileType)
        if fileName.endswith('.db') is False:
            raise Exception('Wrong File Type, only .db file are supported')
        print('libPath set to : {}'.format(fileName))
        self.libPath = fileName
        #Repopulate window #TODO
        # self.initDataAndPopulate()

    def stockedFood(self, item, edit):
        stockObj = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if stockObj:
            print('Stocked data : ', stockObj.name)
        defaultParent = item.parent()
        if defaultParent is None:
            if edit is True:
                return
            defaultParent = item
        self.AddStockedFoodWindow = EditStockedFoodWindow(self, defaultParent.text(0), edit, stockObj)
        self.AddStockedFoodWindow.exec()

    def stockedFoodProcess(self, ui):
        print('stock food wip edit is ', ui.edit)
        """
        ui.qtNameLineEdit
        ui.qtParentItemCombo
        ui.qtDateIsCreationRadio
        ui.qtDateIsLimitRadio
        ui.qtDateCalendar
        ui.qtServingUnitCombo
        ui.qtServingsQuantitySpinBox
        ui.qtNumberSpinbox
        ui.edit
        """
        # print(ui.qtDateCalendar.selectedDate().toString('yy.MM.dd'))
        name = ui.qtNameLineEdit.text()
        if name == '':
            raise Exception("Invalid Name")
        attrs = {
            'name': name,
            'category': ui.qtParentItemCombo.currentText(),
            'servingsQuantity': ui.qtServingsQuantitySpinBox.value(),
            'servingsUnit': ui.qtServingUnitCombo.currentText(),
            'nbr': ui.qtNumberSpinbox.value(),
            'dateName': ui.qtDateCalendar.selectedDate().toString('yy.MM.dd'),
            'dateIsExpirationDate': ui.qtDateIsLimitRadio.isChecked(),
            'ingredients': ui.stockObj.ingredients
        }
        print(attrs)
        if ui.edit is True:
            attrs['id'] = ui.stockObj.id
            print('id is ', ui.stockObj.id)
            self.stocksDb.editStock(attrs)
        else:
            self.stocksDb.addStock(attrs)
        self.qtStockWidget.qtStockedCookedTree.clear()
        self.setStockedFood()

    def stockFoodMinusOne(self, item): #TODO
        print("TODO")

    def removeStockedFood(self, item):
        msgbx = QtWidgets.QMessageBox(self)
        msgbx.setWindowTitle("Delete Stock ?")
        msgbx.setText("Confirm, deletion of {} ?, no undo possible".format(item.text(0)))
        msgbx.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        msgbx.setIcon(QtWidgets.QMessageBox.Warning)
        confirm = msgbx.exec()
        if confirm == QtWidgets.QMessageBox.Yes:
            stockObj = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
            self.stocksDb.removeStock(stockObj.id)
            self.qtStocktWidget.qtStockedCookedTree.clear()
            self.setStockedFood()

    def saveNotes(self):
        # print('todo save notes')
        content = self.qtGoalAndNotesWidget.qtNotesTextEdit.toHtml()
        notes = Recette.Notes(os.path.split(self.libPath)[0]+'/notes.html')
        notes.save(content)

    #####
    #Others
    #####
    def menuTextChanged(self): #TODO
        print('typing')

    def selectIngredientFromMenu(self): #TODO
        print('new item selected')

    def checkIngredient(self, widget, items, value):
        #TODO items on right click menu
        if value is True:
            state = QtCore.Qt.CheckState.Checked
        if value is False:
            state = QtCore.Qt.CheckState.Unchecked
        if widget == 'All':
            widget = [self.qtIngredientWidget.qtMeatColumnTree, self.qtIngredientWidget.qtVegetableColumnTree, self.qtIngredientWidget.qtStarchColumnTree, self.qtIngredientWidget.qtOtherColumnTree]
        else:
            widget = [widget]
        for qtTree in widget:
            if items == "All":
                item = qtTree.topLevelItem(0)
                while True:
                    if value == -1:
                        if item.checkState(0) == QtCore.Qt.CheckState.Checked:
                            state = QtCore.Qt.CheckState.Unchecked
                        else:
                            state = QtCore.Qt.CheckState.Checked
                    item.setCheckState(0, state)
                    item = qtTree.itemBelow(item)
                    if item is None:
                        break
            else:
                selItems = qtTree.selectedItems()
                for item in selItems:
                    if value == -1:
                        if item.checkState(0) == QtCore.Qt.CheckState.Checked:
                            state = QtCore.Qt.CheckState.Unchecked
                        else:
                            state = QtCore.Qt.CheckState.Checked
                    item.setCheckState(0, state)

    def selIngredient(self, widget, value):
        if widget == 'All':
            widget = [self.qtIngredientWidget.qtMeatColumnTree, self.qtIngredientWidget.qtVegetableColumnTree, self.qtIngredientWidget.qtStarchColumnTree, self.qtIngredientWidget.qtOtherColumnTree]
        else:
            widget = [widget]
        state = value
        for qtTree in widget:
            item = qtTree.topLevelItem(0)
            while True:
                if value == -1:
                    if item.isSelected() is True:
                        state = False
                    else:
                        state = True
                item.setSelected(state)
                item = qtTree.itemBelow(item)
                if item is None:
                    break

    def menuChanged(self):
        print("menu changed")
        ingredientList = []
        specialList = []
        meatList = []
        vegetableList = []
        otherList = []
        alwaysAvailableList = []
        for dayObj in self.dayDb.dayList:
            for qtItem in dayObj.qtItems:
                print(qtItem.text(1), qtItem.data(1, QtCore.Qt.ItemDataRole.UserRole))
                for link in qtItem.data(1, QtCore.Qt.ItemDataRole.UserRole):
                    if isinstance(link, Recette.Ingredient):
                        # print(link.name, 'Ingredient', link)
                        # ingredientList.append((link, '{} {}'.format(dayObj.name, qtItem.text(0))))
                        label = '{} {}'.format(dayObj.name, qtItem.text(0))
                        ingredients = [link]
                    else:
                        print(link.name, 'Recipe', link)
                        label = link.name
                        ingredients = link.ingredients
                        # for ingredientObj in link.ingredients:
                        #     ingredientList.append((ingredientObj, link.name))
                    for ingredientObj in ingredients:
                        ingredientList.append((ingredientObj, label))
                        print(ingredientObj.name, ingredientObj.special, ingredientObj.always_available)
                        if ingredientObj.special is True:
                            specialList.append((ingredientObj, label))
                        elif ingredientObj.always_available is True:
                            alwaysAvailableList.append((ingredientObj, label))
                        elif 'meat' in ingredientObj.family:
                            meatList.append((ingredientObj, label))
                        elif 'vegetable' in ingredientObj.family or 'starch' in ingredientObj.family:
                            vegetableList.append((ingredientObj, label))
                        else: #divers
                            otherList.append((ingredientObj, label))

                #Check Menu State
                if qtItem.checkState(2) == QtCore.Qt.CheckState.Checked:
                    color = self.ui['uiTheme']['menuIsOk_bg']
                else:
                    color = QtGui.QBrush()
                for i in range(3):
                    qtItem.setBackground(i, color)

        # qtItemList = []
        # print(ingredientList)
        # self.qtGroceriesList.clear()
        # for ingredient in ingredientList:
        #     qtItem = QtWidgets.QListWidgetItem('{}:{}g ({})'.format(ingredient[0].name, ingredient[0].size, ingredient[1]))
        #     qtItemList.append(qtItem)
        #     self.qtGroceriesList.addItem(qtItem)
        # self.qtGroceriesList.sortItems(QtCore.Qt.SortOrder.AscendingOrder)
        print("special", specialList)
        print("always available", alwaysAvailableList)
        topCount = self.qtGroceriesWidget.qtGroceriesTree.topLevelItemCount()
        for i in range(topCount):
            item = self.qtGroceriesWidget.qtGroceriesTree.topLevelItem(i)
            childrenCount = item.childCount()
            for childIdx in reversed(range(childrenCount)):
                item.removeChild(item.child(childIdx))

        def addItem(parent, obj, label):
            text = '{} : {}g ({})'.format(obj.name, obj.size, label)
            qtItem = QtWidgets.QTreeWidgetItem(parent, [text])

        for objList, widgetIdx in [(specialList, 0), (meatList, 1), (vegetableList, 2), (otherList, 3), (alwaysAvailableList, 4)]:
            parent = self.qtGroceriesWidget.qtGroceriesTree.topLevelItem(widgetIdx)
            if len(objList) == 0:
                parent.setHidden(1)
            else:
                parent.setHidden(0)
                for obj, label in objList:
                    # addItem(self.qtGroceriesTree.topLevelItem(widgetIdx), obj[0], obj[1])
                    text = '{} : {}g ({})'.format(obj.name, obj.size, label)
                    qtItem = QtWidgets.QTreeWidgetItem(parent, [text])
                parent.sortChildren(0, QtCore.Qt.SortOrder.AscendingOrder)
                parent.setExpanded(True)

    def moveItemMenu(self, up=True):
        selection = self.qtMenuWidget.qtTreeMenu.currentItem()
        txt = selection.text(1)
        data = selection.data(1, QtCore.Qt.ItemDataRole.UserRole)
        start = selection
        while True:
            if up is True:
                switch = self.qtMenuWidget.qtTreeMenu.itemAbove(start)
            else:
                switch = self.qtMenuWidget.qtTreeMenu.itemBelow(start)
            if switch.childCount() == 0:
                break
            else:
                start = switch
        txtSwitch = switch.text(1)
        dataSwitch = switch.data(1, QtCore.Qt.ItemDataRole.UserRole)
        selection.setText(1, txtSwitch)
        selection.setData(1, QtCore.Qt.ItemDataRole.UserRole, dataSwitch)
        switch.setText(1, txt)
        switch.setData(1, QtCore.Qt.ItemDataRole.UserRole, data)

        self.qtMenuWidget.qtTreeMenu.setCurrentItem(switch)



    def meatContextMenu(self, position):
        position = self.qtIngredientWidget.qtMeatColumnTree.viewport().mapToGlobal(position)
        self.GenericContextMenu(self.qtIngredientWidget.qtMeatColumnTree, position)

    def vegetableContextMenu(self, position):
        position = self.qtIngredientWidget.qtVegetableColumnTree.viewport().mapToGlobal(position)
        self.GenericContextMenu(self.qtIngredientWidget.qtVegetableColumnTree, position)

    def starchContextMenu(self, position):
        position = self.qtIngredientWidget.qtStarchColumnTree.viewport().mapToGlobal(position)
        self.GenericContextMenu(self.qtIngredientWidget.qtStarchColumnTree, position)

    def otherContextMenu(self, position):
        position = self.qtIngredientWidget.qtOtherColumnTree.viewport().mapToGlobal(position)
        self.GenericContextMenu(self.qtIngredientWidget.qtOtherColumnTree, position)

    def recipeContextMenu(self, position):
        position = self.qtRecipeWidget.qtTreeRecipe.viewport().mapToGlobal(position)
        self.GenericContextMenu(self.qtRecipeWidget.qtTreeRecipe, position)

    def stockedCookedContextMenu(self, position):
        position = self.qtStockWidget.qtStockedCookedTree.viewport().mapToGlobal(position)
        self.GenericContextMenu(self.qtStockWidget.qtStockedCookedTree, position)

    def createToMenuActions(self, item):
        addToMenuAction = QtGui.QAction(self.ui['icons']['add'], 'Add To Selected Menu')
        replaceMenuAction = QtGui.QAction(self.ui['icons']['replace'], 'Replace Selected Menu')
        addToMenuAction.triggered.connect(
            lambda: self.addToMenu(item.text(0), False, item.data(0, QtCore.Qt.ItemDataRole.UserRole)))
        replaceMenuAction.triggered.connect(
            lambda: self.addToMenu(item.text(0), True, item.data(0, QtCore.Qt.ItemDataRole.UserRole)))
        return [addToMenuAction, replaceMenuAction]

    def createStockedFoodActions(self, item):
        addStockAction = QtGui.QAction(self.ui['icons']['addStock'], 'Tmp : Add Stocked Food')
        minusOneStockAction = QtGui.QAction('Decrease Share Available by 1')
        editStockAction = QtGui.QAction(self.ui['icons']['edit'], 'Edit Stocked Food')
        removeStockAction = QtGui.QAction(self.ui['icons']['removeStock'], 'Remove Stocked Food')
        addStockAction.triggered.connect(lambda: self.stockedFood(item, False))
        minusOneStockAction.triggered.connect(lambda: self.stockFoodMinusOne(item))
        editStockAction.triggered.connect(lambda: self.stockedFood(item, True))
        removeStockAction.triggered.connect(lambda: self.removeStockedFood(item))
        return ['Manage Stocks', addStockAction, minusOneStockAction, editStockAction, removeStockAction]

    def createSelectionHandlerActions(self, widget):
        selectAllAction = QtGui.QAction('Select All Items')
        selectNoneAction = QtGui.QAction('Select None Items')
        selectInvertAction = QtGui.QAction("Select Invert Items")
        checkSelAction = QtGui.QAction('Check Selected Items')
        uncheckSelAction = QtGui.QAction('Un-Check Selected Items')
        invertcheckSelAction = QtGui.QAction('Invert Check Selected Items')
        checkAllAction = QtGui.QAction('Check All Items')
        uncheckAllAction = QtGui.QAction('Un-Check All Items')
        invertcheckAllAction = QtGui.QAction('Invert Check All Items')
        selectAllAction.triggered.connect(lambda: self.selIngredient(widget, True))
        selectNoneAction.triggered.connect(lambda: self.selIngredient(widget, False))
        selectInvertAction.triggered.connect(lambda: self.selIngredient(widget, -1))
        checkSelAction.triggered.connect(lambda: self.checkIngredient(widget, 'Sel', True))
        uncheckSelAction.triggered.connect(lambda: self.checkIngredient(widget, 'Sel', False))
        invertcheckSelAction.triggered.connect(lambda: self.checkIngredient(widget, 'Sel', -1))
        checkAllAction.triggered.connect(lambda: self.checkIngredient(widget, 'All', True))
        uncheckAllAction.triggered.connect(lambda: self.checkIngredient(widget, 'All', False))
        invertcheckAllAction.triggered.connect(lambda: self.checkIngredient(widget, 'All', -1))
        return ['Selection', selectAllAction, selectNoneAction, selectInvertAction, 'Check Selection', checkSelAction, uncheckSelAction, invertcheckSelAction, 'Check All', checkAllAction, uncheckAllAction, invertcheckAllAction]

    def createAddToStockedFoodActions(self, item):
        addStockAction = QtGui.QAction(self.ui['icons']['addStock'], 'Add To Stocked Food')
        addStockAction.triggered.connect(lambda: self.stockedFood(item, False))
        # self.qtRecipeContextMenu.addAction(addStockAction)
        return [addStockAction]

    def createAddIngredientToRecipeAction(self, widget):
        addIngredient = QtGui.QAction(self.ui['icons']['add'], 'Add Selected Ingredient To Recipe')
        items = widget.selectedItems()
        addIngredient.triggered.connect(lambda: self.addIngredientsToRecipe(items))
        return [addIngredient]

    def GenericContextMenu(self, widget, position):
        actions = []
        item = widget.currentItem()
        self.qtRecipeContextMenu = QtWidgets.QMenu(self)

        if self.mode == "editMenu":
            actions.extend(self.createToMenuActions(item))
            if widget == self.qtStockWidget.qtStockedCookedTree:
                actions.extend(self.createStockedFoodActions(item))
            else:
                # addStockAction = QtGui.QAction(self.ui['icons']['addStock'], 'Add To Stocked Food')
                # addStockAction.triggered.connect(lambda: self.stockedFood(item, False))
                # self.qtRecipeContextMenu.addAction(addStockAction)
                actions.extend(self.createAddToStockedFoodActions(item))
                if widget != self.qtRecipeWidget.qtTreeRecipe:
                    actions.extend(self.createSelectionHandlerActions(widget))

        elif self.mode == "editRecipe":
            actions.extend(self.createAddIngredientToRecipeAction(widget))
            actions.extend(self.createSelectionHandlerActions(widget))

        # add actions to menu
        for action in actions:
            if isinstance(action, str):
                self.qtRecipeContextMenu.addSection(action)
            else:
                self.qtRecipeContextMenu.addAction(action)
        self.qtRecipeContextMenu.exec(position)

    def menuContextMenu(self, position):
        position = self.qtMenuWidget.qtTreeMenu.viewport().mapToGlobal(position)
        # item = self.qtTreeMenu.currentItem()
        self.qtMenuContextMenu = QtWidgets.QMenu(self)
        qtManualEditAction = QtGui.QAction(self.ui['icons']['edit'], 'Editer à la main')
        qtsearchMenuAction = QtWidgets.QWidgetAction(self.qtMenuContextMenu)
        qtLineEdit = QtWidgets.QLineEdit()
        qtLineEdit.setClearButtonEnabled(True)
        qtLineEdit.addAction(self.ui['icons']['search'], QtWidgets.QLineEdit.ActionPosition.LeadingPosition)
        qtLineEdit.setPlaceholderText('search ingredients and recipes')
        qtsearchMenuAction.setDefaultWidget(qtLineEdit)


        # self.qtIngredientPosition = position + QtCore.QPoint(150, 0)
        # self.qtMenuPosition = position
        # self.menuFilter('')
        qtLineEdit.textChanged.connect(lambda: self.menuFilter(qtLineEdit.text()))

        autreReplaceMenuAction = QtGui.QAction(self.ui['icons']['menu'], 'Autre')
        restesReplaceMenuAction = QtGui.QAction(self.ui['icons']['menu'], 'Restes')
        restaurantReplaceMenuAction = QtGui.QAction(self.ui['icons']['menu'], 'Restaurant')
        clearReplaceMenuAction = QtGui.QAction(self.ui['icons']['clear'], 'Supprimer Menu')
        addMealMenuAction = QtGui.QAction(self.ui['icons']['add'], 'Ajouter un repas')

        qtManualEditAction.triggered.connect(self.manualMenuEdit)
        autreReplaceMenuAction.triggered.connect(lambda: self.addToMenu('Autre', True, None))
        restesReplaceMenuAction.triggered.connect(lambda: self.addToMenu('Restes', True, None))
        restaurantReplaceMenuAction.triggered.connect(lambda: self.addToMenu('Restaurant', True, None))
        clearReplaceMenuAction.triggered.connect(lambda: self.addToMenu('', True, None))
        addMealMenuAction.triggered.connect(self.addMealToMenu)

        self.qtMenuContextMenu.addAction(qtManualEditAction)
        self.qtMenuContextMenu.addAction(qtsearchMenuAction)
        self.qtMenuContextMenu.addAction(autreReplaceMenuAction)
        self.qtMenuContextMenu.addAction(restesReplaceMenuAction)
        self.qtMenuContextMenu.addAction(restaurantReplaceMenuAction)
        self.qtMenuContextMenu.addAction(clearReplaceMenuAction)
        self.qtMenuContextMenu.addAction(addMealMenuAction)
        self.qtMenuContextMenu.exec(position)




    def manualMenuEdit(self): #TODO
        print('edit a la main')

    def menuFilter(self, filterText): #TODO Open search result in context menu
        # self.qtIngredientMenu = QtWidgets.QMenu(self)
        # print("filterText at ", self.qtIngredientPosition)
        # if filterText.strip() != '':
        #     filtered = self.ingredientsDb.filterIngredients(filterText.strip())
        # else:
        #     filtered = []
        # qtlist = []
        # for obj, match in filtered:
        #     if match:
        #         qtObjAction = QtGui.QAction(obj.name)
        #         qtlist.append(qtObjAction)
        # self.qtIngredientMenu.addActions(qtlist)
        # self.qtIngredientMenu.popup(self.qtIngredientPosition)
        # self.qtMenuContextMenu.insertMenu(self.qtsearchMenuAction, self.qtIngredientMenu)
        # self.qtMenuContextMenu.update()
        if filterText != '':
            self.qtIngredientWidget.qtIngredientFilter.setText(filterText)
            self.qtRecipeWidget.qtRecipeFilter.setText(filterText)

    def addMealToMenu(self):
        item = self.qtMenuWidget.qtTreeMenu.currentItem()
        currentParent = item.parent()
        if currentParent:
            self.AddMealToMenuWindow = AddMealToMenu(self, self.ui, currentParent.text(0), item.text(0))
            self.AddMealToMenuWindow.exec()

    def AddMealToMenuProcess(self, name, index):
        item = self.qtMenuWidget.qtTreeMenu.currentItem()
        itemindex = self.qtMenuWidget.qtTreeMenu.indexFromItem(item, 0)
        parent = item.parent()
        if name.strip() == '':
            return
        for dayObj in self.dayDb.dayList:
            if parent.text(0) == dayObj.name:
                dayObj.__setattr__(name, None)
                break

        qtItem = self.createMenuQtItem(None, [name, '', ''])
        parent.insertChild(itemindex.row() + index, qtItem)
        dayObj.qtItems.append(qtItem)

    def addToMenu(self, menuText, replace=True, obj=None):
        menu = self.getMenuSelection()
        if menu is None:
            return
        # print("addToMenu:", menu.data(1, QtCore.Qt.ItemDataRole.UserRole))
        if replace is False:
            text = menu.text(1)
            if text != "":
                text += ", "
            menu.setText(1, text+menuText)
            if obj:
                dataobj = menu.data(1, QtCore.Qt.ItemDataRole.UserRole)
                dataobj.append(obj)
                menu.setData(1, QtCore.Qt.ItemDataRole.UserRole, dataobj)
        else:
            menu.setText(1, menuText)
            if obj:
                menu.setData(1, QtCore.Qt.ItemDataRole.UserRole, [obj])
            else:
                menu.setData(1, QtCore.Qt.ItemDataRole.UserRole, [])

    def addIngredientsToRecipe(self, items):
        for item in items:
            qtItem = QtWidgets.QTreeWidgetItem([item.text(0), str(0)])
            ingredientObj = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
            qtItem.setData(0, QtCore.Qt.ItemDataRole.UserRole, ingredientObj)
            # qtItem.setFlags(qtItem.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
            self.qtEditRecipeWidget.qtIngredients.addTopLevelItem(qtItem)
            # print(qtItem, qtItem.data(0, QtCore.Qt.ItemDataRole.UserRole))




    def changeTab(self, idx):
        widget = self.qtRecipeWidget.qtRecipeGroupBox.widget(idx)
        layout = widget.layout()
        layout.addWidget(self.qtRecipeWidget.qtTreeRecipe)
        self.filterRecipe()

    def getMenuSelection(self):
        menu = self.qtMenuWidget.qtTreeMenu.currentItem()
        if menu is None:
            return None
        if menu.childCount() > 0:
            return None
        return menu

    def addRecipeToMenu(self):
        menu = self.getMenuSelection()
        if menu is None:
            return
        sel = self.qtRecipeWidget.qtTreeRecipe.currentItem()
        menu.setText(1, sel.text(0))

    def addSpecialToMenu(self, text):
        menu = self.getMenuSelection()
        if menu is None:
            return
        menu.setText(1, text)

    def filterIngredientList(self):
        if self.qtIngredientWidget.qtIngredientFilter.text().strip() != '':
            filtered = self.ingredientsDb.filterIngredients(self.qtIngredientWidget.qtIngredientFilter.text())
        else:
            filtered = [(obj, True) for obj in self.ingredientsDb.ingredientList]
        for ingredientObj, match in filtered:
            for qtItem in ingredientObj.qtItem:
                qtItem.setHidden(not match)

        for family, widget in self.qtIngredientWidget.ingredientWidgetList:
            itemsCount = widget.topLevelItemCount()
            for idx in range(itemsCount):
                item = widget.topLevelItem(idx)
                childrenCount = item.childCount()
                if childrenCount == 0:
                    continue
                vis = False
                for idx in range(childrenCount):
                    child = item.child(idx)
                    if child.isHidden() is False:
                        vis = True
                        break
                item.setHidden(not vis)
        if self.qtRecipeWidget.qtFilterByIngredientCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
            self.filterRecipe()

    def ingredientTreeSelectionChanged(self):
        if self.qtRecipeWidget.qtFilterByIngredientCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
            if self.qtRecipeWidget.qtFilterByIngredientCombo.currentText() in ['Selected Ingredients', 'Visible Ingredients']:
                self.filterRecipe()

    def ingredientTreeCheckChanged(self):
        if self.qtRecipeWidget.qtFilterByIngredientCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
            if self.qtRecipeWidget.qtFilterByIngredientCombo.currentText() in 'Checked Ingredients':
                self.filterRecipe()



    def filterRecipe(self):
        def retrieveIngredientList(choice):
            ingredientList = []
            for name, widget in self.qtIngredientWidget.ingredientWidgetList:
                if choice == 'Selected Ingredients':
                    for item in widget.selectedItems():
                        ingredientList.append(item.data(0, QtCore.Qt.ItemDataRole.UserRole))
                    if len(ingredientList) == 0:
                        choice = 'Visible Ingredients'
                if choice != 'Selected Ingredients':
                    itemsCount = widget.topLevelItemCount()
                    for idx in range(itemsCount):
                        item = widget.topLevelItem(idx)
                        childrenCount = item.childCount()
                        if childrenCount == 0:
                            children = [item]
                        else:
                            children = [item.child(x) for x in range(childrenCount)]
                        for child in children:
                            if choice == 'Checked Ingredients':
                                # print(child.text(0), child.checkState(0), bool(child.checkState(0)))
                                if child.checkState(0) == QtCore.Qt.CheckState.Checked:
                                    ingredientList.append(child.data(0, QtCore.Qt.ItemDataRole.UserRole))
                            else: # visible ingredients
                                if child.isHidden() is False:
                                    ingredientList.append(child.data(0, QtCore.Qt.ItemDataRole.UserRole))
            # print('ingredientList : ', ingredientList)
            return ingredientList

        def keepItemThatMatch(filtered):
            kept = []
            for obj, value in filtered:
                if value is True:
                    kept.append(obj)
            return kept

        # filter by tab
        tabType = self.qtRecipeWidget.qtRecipeGroupBox.tabText(self.qtRecipeWidget.qtRecipeGroupBox.currentIndex())
        if tabType == "Toutes":
            filtered = [(obj, True) for obj in self.recipeDb.recipeList]
        else:
            tabType = tabType[:-1]
            filtered = self.recipeDb.filterRecipe(tabType, [], 'type')
        # print('filtered tab :', filtered)

        #filter by recipe name
        kept = keepItemThatMatch(filtered)
        filtered = self.recipeDb.filterRecipe(self.qtRecipeWidget.qtRecipeFilter.text(), kept, 'match_name')
        kept = keepItemThatMatch(filtered)
        print('kept from recipe name:', kept)

        #filter by ingredient filter
        print('------------>> new ingredient search')
        if self.qtRecipeWidget.qtFilterByIngredientCheckBox.checkState() == QtCore.Qt.CheckState.Checked:
            ingredientList = retrieveIngredientList(self.qtRecipeWidget.qtFilterByIngredientCombo.currentText())
            filtered = self.recipeDb.filterRecipeIngredients(ingredientList, kept)
            kept = keepItemThatMatch(filtered)
            print('kept ingredient : ', kept)

        #filter by recipe filter text TODO



        #apply results
        filtered = [(x, x in kept) for x in self.recipeDb.recipeList]
        for recipeObj, match in filtered:
            # print('set vis', recipeObj.name, match, recipeObj.qtitems)
            for qtItem in recipeObj.qtitems:
                qtItem.setHidden(not match)

        # display categories
        for category in self.categoryDict:
            qtcategory = self.categoryDict[category]
            childrenNbr  = qtcategory.childCount()
            vis = False
            vislist = []
            for childIdx in range(childrenNbr):
                child = qtcategory.child(childIdx)
                vislist.append([child.text(0), child.isHidden()])
                if child.isHidden() is False:
                    vis = True
                    break
            qtcategory.setHidden(not vis)

test = False
window = True
AppWindowsId = 'Recette'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(AppWindowsId)
sys.argv += ['-platform', 'windows:darkmode=2']
app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')
libPath = 'E:/Scripts/Python/Recette/recette liste.ods'
# libPath = 'D:/Python/recette liste.ods'
libPath = 'E:/Scripts/Python/Recette/recipe_database.db'
# libPath = ''
if test is True:
    # print(sys.argv)
    window = RecipeWindowContent(None, None, None)
    window = EditIngredientWindow(None, None, None, None)

    window = MainWindow(None)

    # db = Recette.IngredientList(libPath)
else:
    window = MainWindow(libPath)
if window:
    # window.show()
    window.showMaximized()
    app.exec()