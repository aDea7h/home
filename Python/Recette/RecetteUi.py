from PySide6 import QtCore, QtGui, QtWidgets
import sys
import Recette
#import tools

# TODO
"""
sauvegarde / import / envoyer mail recap
direct edit menu by keyboard
ingredient list management (checkbox / remove on keyboard replace)
menu manual edit ingredient / recette and export / set ingredient-recipe as leftover
inverser right/left pane
menu item edit = txt insert in filter recipe and ingredient
case goal check
zone texte libre pour notes a cote des goals
ds vu ingredient proposer de congeler
zone a finir (farine sarasin  congel)
rappel conserves et congel
jour a contrainte de temps (sport/douche....)
idees de recette /ingredient a finir pour plus tard
menu icomplet / complet
filter de recette
ouverture rapide et progress bar
dark ui and colors and beautiful calendar
ajouter des repas
ajouter des ingredients / recettes et editer l'ods
liste des courses a split (speciaux / viande / legume / divers / toujours dispo)
ajout de menus generic sans ingredients a flagger : "gateau" = pas d'ingredient listable
recette avec variantes (utilisation de listes imbriquees [[liste pr variante 1], [liste var2]])
links d'accompagnement et menu tout fait
!! conform des ingredients de recette sur liste d ingredient a refaire  (on sait pas sur quoi ca match et peu precis)!!
gestion des poids d ingredients et repartition sur multi ingredients (poid des aliments total et pourcentage par classe)
"""

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, libPath='E:/Scripts/Python/Recette/recette liste.ods', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.libPath = libPath
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle("Recettes")
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralLayout = QtWidgets.QGridLayout()
        self.centralWidget.setLayout(self.centralLayout)
        #
        #HEADER
        #
        self.headerPaneWidget = QtWidgets.QWidget()
        self.headerPaneWidgetLayout = QtWidgets.QVBoxLayout()
        self.headerPaneWidget.setLayout(self.headerPaneWidgetLayout)
        self.qtCalendar = QtWidgets.QCalendarWidget()
        self.headerPaneWidgetLayout.addWidget(self.qtCalendar)
        # self.centralLayout.addWidget(self.headerPaneWidget, 0, 0, 1, 2)
        #
        #MAIN
        #
        self.leftPaneWidget = QtWidgets.QWidget()
        self.leftPaneLayout = QtWidgets.QVBoxLayout()
        self.leftPaneWidget.setLayout(self.leftPaneLayout)
        self.centralLayout.addWidget(self.leftPaneWidget, 1, 0)
        self.rightPaneWidget = QtWidgets.QWidget()
        self.rightPaneLayout = QtWidgets.QVBoxLayout()
        self.rightPaneWidget.setLayout(self.rightPaneLayout)
        self.centralLayout.addWidget(self.rightPaneWidget, 1, 1)
        #
        #LEFT PANE
        #
        #INGREDIENT
        #
        self.qtLabelIngredient = QtWidgets.QLabel("Ingredients")
        self.leftPaneLayout.addWidget(self.qtLabelIngredient)
        self.qtIngredientColumn = QtWidgets.QWidget()
        self.qtIngredientColumnLayout = QtWidgets.QHBoxLayout()
        self.qtIngredientColumn.setLayout(self.qtIngredientColumnLayout)
        self.qtIngredientActionWidget = QtWidgets.QWidget()
        self.qtIngredientActionWidgetLayout = QtWidgets.QVBoxLayout()
        # left buttons
        self.qtIngredientFilter = QtWidgets.QLineEdit()
        self.qtIngredientFilter.setPlaceholderText("Filter Ingredients")
        self.leftPaneLayout.addWidget(self.qtIngredientFilter)
        self.qtIngredientActionWidget.setLayout(self.qtIngredientActionWidgetLayout)
        self.qtIngredientAllLabel = QtWidgets.QLabel("Check")
        self.qtIngredientCheckAllButton = QtWidgets.QPushButton("All")
        self.qtIngredientCheckNoneButton = QtWidgets.QPushButton("None")
        self.qtIngredientCheckInvertButton = QtWidgets.QPushButton("Invert")
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientAllLabel)
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientCheckAllButton)
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientCheckNoneButton)
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientCheckInvertButton)
        self.qtIngredientSelLabel = QtWidgets.QLabel("Select")
        self.qtIngredientSelAllButton = QtWidgets.QPushButton("All")
        self.qtIngredientSelNoneButton = QtWidgets.QPushButton("None")
        self.qtIngredientSelInvertButton = QtWidgets.QPushButton("Invert")
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientSelLabel)
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientSelAllButton)
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientSelNoneButton)
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientSelInvertButton)
        # ingredients columns
        self.qtViandesColumnTree = QtWidgets.QTreeWidget()
        self.qtViandesColumnTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Viande']))
        self.qtViandesColumnTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtViandesColumnTree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode(3))
        self.qtLegumesColumnTree = QtWidgets.QTreeWidget()
        self.qtLegumesColumnTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Légumes']))
        self.qtLegumesColumnTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtLegumesColumnTree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode(3))
        self.qtFeculentsColumnTree = QtWidgets.QTreeWidget()
        self.qtFeculentsColumnTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Féculents']))
        self.qtFeculentsColumnTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtFeculentsColumnTree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode(3))
        self.qtDiversColumnTree = QtWidgets.QTreeWidget()
        self.qtDiversColumnTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Divers']))
        self.qtDiversColumnTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtDiversColumnTree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode(3))
        self.qtIngredientColumnLayout.addWidget(self.qtIngredientActionWidget)
        self.qtIngredientColumnLayout.addWidget(self.qtViandesColumnTree)
        self.qtIngredientColumnLayout.addWidget(self.qtLegumesColumnTree)
        self.qtIngredientColumnLayout.addWidget(self.qtFeculentsColumnTree)
        self.qtIngredientColumnLayout.addWidget(self.qtDiversColumnTree)
        self.leftPaneLayout.addWidget(self.qtIngredientColumn)
        self.ingredientWidgetList = [('viande', self.qtViandesColumnTree), ('légume', self.qtLegumesColumnTree),
                      ('féculent', self.qtFeculentsColumnTree), ('divers', self.qtDiversColumnTree)]
        #
        #RECIPE
        #
        self.qtLabelRecipes = QtWidgets.QLabel('Recettes')
        self.qtRecipeFilter = QtWidgets.QLineEdit()
        self.qtRecipeFilter.setPlaceholderText("Filter Recipe")
        self.qtFilterByIngredientCombo = QtWidgets.QComboBox()
        self.qtFilterByIngredientCombo.addItems(['Checked Ingredients', 'Ignore Ingredient Filter', 'Selected Ingredients', 'Visible Ingredients'])

        #Recipe Tabs
        self.qtgroupBox = QtWidgets.QTabWidget()
        self.qtToutesGroupPage = QtWidgets.QWidget()
        self.qtEntreeGroupPage = QtWidgets.QWidget()
        self.qtPlatGroupPage = QtWidgets.QWidget()
        self.qtDessertGroupPage = QtWidgets.QWidget()
        self.qtSauceGroupPage = QtWidgets.QWidget()
        self.qtgroupBox.addTab(self.qtToutesGroupPage, "Toutes")
        self.qtgroupBox.addTab(self.qtEntreeGroupPage, "Entrées")
        self.qtgroupBox.addTab(self.qtPlatGroupPage, "Plats")
        self.qtgroupBox.addTab(self.qtDessertGroupPage, "Desserts")
        self.qtgroupBox.addTab(self.qtSauceGroupPage, "Sauces")
        self.qtToutesGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtEntreeGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtPlatGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtDessertGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtSauceGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtToutesGroupPage.setLayout(self.qtToutesGroupPageLayout)
        self.qtEntreeGroupPage.setLayout(self.qtEntreeGroupPageLayout)
        self.qtPlatGroupPage.setLayout(self.qtPlatGroupPageLayout)
        self.qtDessertGroupPage.setLayout(self.qtDessertGroupPageLayout)
        self.qtSauceGroupPage.setLayout(self.qtSauceGroupPageLayout)
        #Recipe content
        self.qtTreeRecipe = QtWidgets.QTreeWidget()
        self.qtTreeRecipe.setColumnCount(1)
        self.qtTreeRecipe.setHeaderHidden(True)
        self.qtTreeRecipe.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.leftPaneLayout.addWidget(self.qtLabelRecipes)
        self.leftPaneLayout.addWidget(self.qtRecipeFilter)
        self.leftPaneLayout.addWidget(self.qtFilterByIngredientCombo)
        self.leftPaneLayout.addWidget(self.qtgroupBox)
        self.qtToutesGroupPageLayout.addWidget(self.qtTreeRecipe)
        #
        #RIGHT PANE
        #
        self.qtGoalsTreeWidget = QtWidgets.QTreeWidget()
        self.qtGoalsTreeWidget.setColumnCount(3)
        self.qtGoalsTreeWidget.setHeaderItem(QtWidgets.QTreeWidgetItem(["Nbr", "Objectif par semaine", "Note"]))
        self.qtGoalsTreeWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Maximum)
        self.rightPaneLayout.addWidget(self.qtGoalsTreeWidget)

        #Menus
        self.qtLabelMenu = QtWidgets.QLabel('Menus :')
        self.qtMenuOperations = QtWidgets.QWidget()
        self.qtMenuOperationsLayout = QtWidgets.QGridLayout()
        self.qtMenuOperations.setLayout(self.qtMenuOperationsLayout)
        self.qtMenuButtonUp = QtWidgets.QPushButton('Up')
        self.qtMenuButtonDown = QtWidgets.QPushButton('Down')
        self.qtMenuOperationsLayout.addWidget(self.qtMenuButtonUp, 0, 0)
        self.qtMenuOperationsLayout.addWidget(self.qtMenuButtonDown, 0, 1)
        self.qtTreeMenu = QtWidgets.QTreeWidget()
        self.qtTreeMenu.setColumnCount(3)
        self.qtTreeMenu.setHeaderItem(QtWidgets.QTreeWidgetItem(["Jour", "Menu", "Nbr"]))
        self.qtTreeMenu.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtTreeMenu.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.rightPaneLayout.addWidget(self.qtLabelMenu)
        self.rightPaneLayout.addWidget(self.qtTreeMenu)
        self.rightPaneLayout.addWidget(self.qtMenuOperations)


        #Groceries
        # self.qtGroceriesWidget = QtWidgets.QWidget()
        # self.qtGroceriesWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding) #"was Expanding / Prefered"
        # self.qtGroceriesWidgetLayout = QtWidgets.QGridLayout()
        # self.qtGroceriesWidget.setLayout(self.qtGroceriesWidgetLayout)
        self.qtLabelGroceriesList = QtWidgets.QLabel('Liste des Courses')
        self.qtGroceriesTree = QtWidgets.QTreeWidget()
        self.qtGroceriesTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Ingredients :']))
        topLevel = [QtWidgets.QTreeWidgetItem(['Non Commun']), QtWidgets.QTreeWidgetItem(['Viande']), QtWidgets.QTreeWidgetItem(['Légumes']), QtWidgets.QTreeWidgetItem(['Divers']), QtWidgets.QTreeWidgetItem(['Toujours Disponible'])]
        self.qtGroceriesTree.addTopLevelItems(topLevel)
        self.qtGroceriesTree.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.rightPaneLayout.addWidget(self.qtGroceriesTree)

        # self.qtGroceriesSpecialList = QtWidgets.QListWidget()
        # self.qtGroceriesAlwaysAvailableList = QtWidgets.QListWidget()
        # # self.qtGroceriesList = QtWidgets.QListWidget()
        # # self.qtGroceriesList.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        # self.qtGroceriesViandeList = QtWidgets.QListWidget()
        # self.qtGroceriesLegumeList = QtWidgets.QListWidget()
        # self.qtGroceriesDiversList = QtWidgets.QListWidget()
        #
        # self.qtGroceriesWidgetLayout.addWidget(self.qtGroceriesSpecialList, 0, 0, 1, 3)
        # self.qtGroceriesWidgetLayout.addWidget(self.qtGroceriesViandeList, 1, 0)
        # self.qtGroceriesWidgetLayout.addWidget(self.qtGroceriesLegumeList, 1, 1)
        # self.qtGroceriesWidgetLayout.addWidget(self.qtGroceriesDiversList, 1, 2)
        # self.qtGroceriesWidgetLayout.addWidget(self.qtGroceriesAlwaysAvailableList, 2, 0, 1, 3)
        # self.rightPaneLayout.addWidget(self.qtLabelGroceriesList)
        # self.rightPaneLayout.addWidget(self.qtGroceriesList)
        # self.rightPaneLayout.addWidget(self.qtGroceriesWidget)
        #
        #
        #SET CONNECTIONS AND ADD DATA TO UI
        #
        #
        self.setConnections()
        self.ingredientsDb = None
        self.setIngredients()
        self.recipeDb = None
        self.setRecipe()
        self.setGoals()
        self.initMenus()
        self.menuChanged() #init liste des courses

    def setIngredients(self):
        def createQtItem(ingredientObj, parent=None):
            qtItem = QtWidgets.QTreeWidgetItem(parent, [ingredientObj.name])
            qtItem.setCheckState(0, QtCore.Qt.CheckState.Checked)
            qtItem.setData(0, QtCore.Qt.ItemDataRole.UserRole, ingredientObj)
            ingredientObj.qtItem.append(qtItem)
            self.ingredientsDb.ingredientDic[ingredientObj.name] = ingredientObj
            return qtItem, ingredientObj

        self.ingredientsDb = Recette.IngredientList(self.libPath)

        self.qtIngredientDic = {
        'viande':{},
        'légume':{},
        'féculent':{},
        'divers':{}
        }

        topLevelItems = {
        'viande':[],
        'légume':[],
        'féculent':[],
        'divers':[]
        }
        self.categoryDict = {}
        for ingredientObj in self.ingredientsDb.ingredientList:
            categoryList = [None] if ingredientObj.category is None else ingredientObj.category
            for family in ingredientObj.family:
                # print('New Ingredient : ', ingredientObj.name, ingredientObj.family, categoryList)
                for category in categoryList:
                    if category is not None:
                        parent = self.qtIngredientDic[family][category][0]
                        qtItem, ingredientObj = createQtItem(ingredientObj, parent)
                    else:
                        qtItem, ingredientObj = createQtItem(ingredientObj, None)
                        topLevelItems[family].append(qtItem)
                    if ingredientObj.name in self.qtIngredientDic[family]:
                        self.qtIngredientDic[family][ingredientObj.name].append(qtItem)
                    else:
                        self.qtIngredientDic[family][ingredientObj.name] = [qtItem]

        for family, widget in self.ingredientWidgetList:
            widget.addTopLevelItems(topLevelItems[family])
            widget.expandAll()
            widget.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)

    def setRecipe(self):
        # TODO Check as True not False
        self.recipeDb = Recette.RecipeList(self.libPath, True, self.ingredientsDb.ingredientList)### TODO Check as TRUE not False
        qtRecipeList = []
        self.categoryDict = {}
        for recipeObj in self.recipeDb.recipeList:
            if recipeObj.category is None:
                nbrCategory = 1
            else:
                nbrCategory = max(1, len(recipeObj.category))
            recipeObj.qtitems = []
            for i in range(nbrCategory):
                qtitem = QtWidgets.QTreeWidgetItem([recipeObj.name])
                qtitem.setData(0, QtCore.Qt.ItemDataRole.UserRole, recipeObj)
                if recipeObj.category is not None:
                    ############
                    category = recipeObj.category[i]
                    if category in self.categoryDict:
                        parent = self.categoryDict[category]
                    else:
                        parent = QtWidgets.QTreeWidgetItem([category])
                        self.categoryDict[category] = parent
                        qtRecipeList.append(parent)
                    parent.addChild(qtitem)
                ############
                else:
                    qtRecipeList.append(qtitem)

                recipeObj.qtitems.append(qtitem)

        self.qtTreeRecipe.addTopLevelItems(qtRecipeList)
        self.qtTreeRecipe.expandAll()
        self.qtTreeRecipe.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)

    def setGoals(self):
        print('set goals')
        print(self.qtGoalsTreeWidget.size(), self.qtGoalsTreeWidget.sizeHint(), self.qtGoalsTreeWidget.sizePolicy())
        self.goalDb = Recette.GoalList(self.libPath)
        qtItemList = []
        for goalObj in self.goalDb.goalList:
            qtItem = QtWidgets.QTreeWidgetItem([str(goalObj.nbr), goalObj.name, goalObj.note])
            print(goalObj.name, goalObj.nbr, goalObj.note)
            goalObj.qtItem = qtItem
            qtItemList.append(qtItem)
        self.qtGoalsTreeWidget.addTopLevelItems(qtItemList)
        self.qtGoalsTreeWidget.expandAll()
        self.qtGoalsTreeWidget.sortItems(1, QtCore.Qt.SortOrder.AscendingOrder)

    def initMenus(self):
        def createQtItem(parent, label):
            qtItem = QtWidgets.QTreeWidgetItem(parent, label)
            qtItem.setData(1, QtCore.Qt.ItemDataRole.UserRole, [])
            qtItem.setFlags(qtItem.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
            return qtItem

        self.dayDb = Recette.DayList()
        qtDaysList = []
        for dayObj in self.dayDb.dayList:
            qtDay = QtWidgets.QTreeWidgetItem([dayObj.name, "", ""])
            qtDaysList.append(qtDay)

            qtItem = createQtItem(qtDay, ['Midi', '', ''])
            dayObj.qtItems.append(qtItem)
            qtItem = createQtItem(qtDay, ['Soir', '', ''])
            dayObj.qtItems.append(qtItem)
        self.qtTreeMenu.addTopLevelItems(qtDaysList)
        self.qtTreeMenu.expandAll()

    def setConnections(self):
        # self.qtAddToMenuButton.clicked.connect(self.addRecipeToMenu)
        self.qtIngredientFilter.textChanged.connect(self.filterIngredientList)
        self.qtIngredientCheckAllButton.clicked.connect(lambda: self.checkIngredient('All', 'All', True))
        self.qtIngredientCheckNoneButton.clicked.connect(lambda: self.checkIngredient('All', 'All', False))
        self.qtIngredientCheckInvertButton.clicked.connect(lambda: self.checkIngredient('All', 'All', -1))
        self.qtIngredientSelAllButton.clicked.connect(lambda: self.selIngredient('All', True))
        self.qtIngredientSelNoneButton.clicked.connect(lambda: self.selIngredient('All', False))
        self.qtIngredientSelInvertButton.clicked.connect(lambda: self.selIngredient('All', -1))
        self.qtgroupBox.currentChanged.connect(self.changeTab)
        self.qtRecipeFilter.textChanged.connect(self.filterRecipe)
        # self.qtButtonOther.clicked.connect(lambda: self.addSpecialToMenu(' - Autre'))
        # self.qtButtonRestes.clicked.connect(lambda: self.addSpecialToMenu(' - Restes'))
        # self.qtButtonRestaurant.clicked.connect(lambda: self.addSpecialToMenu(' - Restaurant'))
        self.qtMenuButtonUp.clicked.connect(lambda: self.moveItemMenu(True))
        self.qtMenuButtonDown.clicked.connect(lambda: self.moveItemMenu(False))

        self.qtViandesColumnTree.customContextMenuRequested.connect(self.viandeContextMenu)
        self.qtLegumesColumnTree.customContextMenuRequested.connect(self.legumeContextMenu)
        self.qtFeculentsColumnTree.customContextMenuRequested.connect(self.feculentContextMenu)
        self.qtDiversColumnTree.customContextMenuRequested.connect(self.diversContextMenu)
        self.qtTreeRecipe.customContextMenuRequested.connect(self.recipeContextMenu)
        self.qtTreeMenu.customContextMenuRequested.connect(self.menuContextMenu)
        self.qtTreeMenu.itemChanged.connect(self.menuChanged)

    def checkIngredient(self, widget, items, value):
        #TODO items on right click menu
        if value is True:
            state = QtCore.Qt.CheckState.Checked
        if value is False:
            state = QtCore.Qt.CheckState.Unchecked
        if widget == 'All':
            widget = [self.qtViandesColumnTree, self.qtLegumesColumnTree, self.qtFeculentsColumnTree, self.qtDiversColumnTree]
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
            widget = [self.qtViandesColumnTree, self.qtLegumesColumnTree, self.qtFeculentsColumnTree, self.qtDiversColumnTree]
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
        viandeList = []
        legumeList = []
        diversList = []
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
                        elif 'viande' in ingredientObj.family:
                            viandeList.append((ingredientObj, label))
                        elif 'légume' in ingredientObj.family or 'féculent' in ingredientObj.family:
                            legumeList.append((ingredientObj, label))
                        else: #divers
                            diversList.append((ingredientObj, label))
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
        topCount = self.qtGroceriesTree.topLevelItemCount()
        for i in range(topCount):
            item = self.qtGroceriesTree.topLevelItem(i)
            childrenCount = item.childCount()
            for childIdx in reversed(range(childrenCount)):
                item.removeChild(item.child(childIdx))

        def addItem(parent, obj, label):
            text = '{} : {}g ({})'.format(obj.name, obj.size, label)
            qtItem = QtWidgets.QTreeWidgetItem(parent, [text])

        # for obj in specialList:
        #     addItem(self.qtGroceriesTree.topLevelItem(0), obj[0], obj[1])
        #
        # for obj in viandeList:
        #     addItem(self.qtGroceriesTree.topLevelItem(1), obj[0], obj[1])
        #
        # for obj in legumeList:
        #     addItem(self.qtGroceriesTree.topLevelItem(2), obj[0], obj[1])
        #
        # for obj in diversList:
        #     addItem(self.qtGroceriesTree.topLevelItem(3), obj[0], obj[1])
        #
        # for obj in alwaysAvailableList:
        #     addItem(self.qtGroceriesTree.topLevelItem(4), obj[0], obj[1])

        for objList, widgetIdx in [(specialList, 0), (viandeList, 1), (legumeList, 2), (diversList, 3), (alwaysAvailableList, 4)]:
            parent = self.qtGroceriesTree.topLevelItem(widgetIdx)
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
        selection = self.qtTreeMenu.currentItem()
        txt = selection.text(1)
        data = selection.data(1, QtCore.Qt.ItemDataRole.UserRole)
        start = selection
        while True:
            if up is True:
                switch = self.qtTreeMenu.itemAbove(start)
            else:
                switch = self.qtTreeMenu.itemBelow(start)
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

        self.qtTreeMenu.setCurrentItem(switch)

    def viandeContextMenu(self, position):
        position = self.qtViandesColumnTree.viewport().mapToGlobal(position)
        self.GenericContextMenu(self.qtViandesColumnTree, position)

    def legumeContextMenu(self, position):
        position = self.qtLegumesColumnTree.viewport().mapToGlobal(position)
        self.GenericContextMenu(self.qtLegumesColumnTree, position)

    def feculentContextMenu(self, position):
        position = self.qtFeculentsColumnTree.viewport().mapToGlobal(position)
        self.GenericContextMenu(self.qtFeculentsColumnTree, position)

    def diversContextMenu(self, position):
        position = self.qtDiversColumnTree.viewport().mapToGlobal(position)
        self.GenericContextMenu(self.qtDiversColumnTree, position)

    def recipeContextMenu(self, position):
        position = self.qtTreeRecipe.viewport().mapToGlobal(position)
        self.GenericContextMenu(self.qtTreeRecipe, position)

    def GenericContextMenu(self, widget, position):
        item = widget.currentItem()
        self.qtRecipeContextMenu = QtWidgets.QMenu(self)
        addToMenuAction = QtGui.QAction('Add To Selected Menu')
        replaceMenuAction = QtGui.QAction('Replace Selected Menu')
        addToMenuAction.triggered.connect(lambda: self.addToMenu(item.text(0), False, item.data(0, QtCore.Qt.ItemDataRole.UserRole)))
        replaceMenuAction.triggered.connect(lambda: self.addToMenu(item.text(0), True, item.data(0, QtCore.Qt.ItemDataRole.UserRole)))
        self.qtRecipeContextMenu.addAction(addToMenuAction)
        self.qtRecipeContextMenu.addAction(replaceMenuAction)

        if widget != self.qtTreeRecipe:
            selectAllAction = QtGui.QAction('Select All Items')
            selectNoneAction = QtGui.QAction('Select None Items')
            selectInvertAction = QtGui.QAction("Select Invert Items")
            selectAllAction.triggered.connect(lambda: self.selIngredient(widget, True))
            selectNoneAction.triggered.connect(lambda: self.selIngredient(widget, False))
            selectInvertAction.triggered.connect(lambda: self.selIngredient(widget, -1))
            self.qtRecipeContextMenu.addSection("Selection")
            self.qtRecipeContextMenu.addAction(selectAllAction)
            self.qtRecipeContextMenu.addAction(selectNoneAction)
            self.qtRecipeContextMenu.addAction(selectInvertAction)

            checkSelAction = QtGui.QAction('Check Selected Items')
            uncheckSelAction = QtGui.QAction('Un-Check Selected Items')
            invertcheckSelAction = QtGui.QAction('Invert Check Selected Items')
            checkAllAction = QtGui.QAction('Check All Items')
            uncheckAllAction = QtGui.QAction('Un-Check All Items')
            invertcheckAllAction = QtGui.QAction('Invert Check All Items')
            checkSelAction.triggered.connect(lambda: self.checkIngredient(widget, 'Sel', True))
            uncheckSelAction.triggered.connect(lambda: self.checkIngredient(widget, 'Sel', False))
            invertcheckSelAction.triggered.connect(lambda: self.checkIngredient(widget, 'Sel', -1))
            checkAllAction.triggered.connect(lambda: self.checkIngredient(widget, 'All', True))
            uncheckAllAction.triggered.connect(lambda: self.checkIngredient(widget, 'All', False))
            invertcheckAllAction.triggered.connect(lambda: self.checkIngredient(widget, 'All', -1))
            self.qtRecipeContextMenu.addSection("Check Selection")
            self.qtRecipeContextMenu.addAction(checkSelAction)
            self.qtRecipeContextMenu.addAction(uncheckSelAction)
            self.qtRecipeContextMenu.addAction(invertcheckSelAction)
            self.qtRecipeContextMenu.addSection("Check All")
            self.qtRecipeContextMenu.addAction(checkAllAction)
            self.qtRecipeContextMenu.addAction(uncheckAllAction)
            self.qtRecipeContextMenu.addAction(invertcheckAllAction)

        self.qtRecipeContextMenu.exec(position)

    def menuContextMenu(self, position):
        position = self.qtTreeMenu.viewport().mapToGlobal(position)
        item = self.qtTreeMenu.currentItem()
        self.qtMenuContextMenu = QtWidgets.QMenu(self)
        autreReplaceMenuAction = QtGui.QAction('Autre')
        restesReplaceMenuAction = QtGui.QAction('Restes')
        restaurantReplaceMenuAction = QtGui.QAction('Restaurant')
        clearReplaceMenuAction = QtGui.QAction('Supprimer Menu')
        autreReplaceMenuAction.triggered.connect(lambda: self.addToMenu('Autre', True, None))
        restesReplaceMenuAction.triggered.connect(lambda: self.addToMenu('Restes', True, None))
        restaurantReplaceMenuAction.triggered.connect(lambda: self.addToMenu('Restaurant', True, None))
        clearReplaceMenuAction.triggered.connect(lambda: self.addToMenu('', True, None))
        self.qtMenuContextMenu.addAction(autreReplaceMenuAction)
        self.qtMenuContextMenu.addAction(restesReplaceMenuAction)
        self.qtMenuContextMenu.addAction(restaurantReplaceMenuAction)
        self.qtMenuContextMenu.addAction(clearReplaceMenuAction)
        self.qtMenuContextMenu.exec(position)

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

    def changeTab(self, idx):
        widget = self.qtgroupBox.widget(idx)
        layout = widget.layout()
        layout.addWidget(self.qtTreeRecipe)
        self.filterRecipe()

    def getMenuSelection(self):
        menu = self.qtTreeMenu.currentItem()
        if menu is None:
            return None
        if menu.childCount() > 0:
            return None
        return menu

    def addRecipeToMenu(self):
        menu = self.getMenuSelection()
        if menu is None:
            return
        sel = self.qtTreeRecipe.currentItem()
        menu.setText(1, sel.text(0))

    def addSpecialToMenu(self, text):
        menu = self.getMenuSelection()
        if menu is None:
            return
        menu.setText(1, text)

    def filterIngredientList(self):
        if self.qtIngredientFilter.text().strip() != '':
            filtered = self.ingredientsDb.filterIngredients(self.qtIngredientFilter.text())
        else:
            filtered = [(obj, True) for obj in self.ingredientsDb.ingredientList]
        for ingredientObj, match in filtered:
            for qtItem in ingredientObj.qtItem:
                qtItem.setHidden(not match)

        for family, widget in self.ingredientWidgetList:
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

    def filterRecipe(self):
        def retrieveIngredientList(choice): # TODO convert qtitem to ingredientobj
            ingredientList = []
            for name, widget in self.ingredientWidgetList:
                if choice == 'Selected Ingredients':
                    for item in widget.selectedItems():
                        ingredientList.append(item.data(0, QtCore.Qt.ItemDataRole.UserRole))
                else:
                    itemsCount = widget.topLevelItemCount()
                    for idx in range(itemsCount):
                        item = widget.topLevelItem(idx)
                        childrenCount = item.childCount()
                        if childrenCount == 0:
                            children = [item]
                        else:
                            children = [item.child(x) for x in range(childrenCount)]
                        print(item.text(0), children)
                        for child in children:
                            if choice == 'Checked Ingredients':
                                print(child.text(0), child.checkState(0), bool(child.checkState(0)))
                                if child.checkState(0) == QtCore.Qt.CheckState.Checked:
                                    print('add')
                                    ingredientList.append(child.data(0, QtCore.Qt.ItemDataRole.UserRole))
                            else: # visible ingredients
                                if child.isHidden() is False:
                                    ingredientList.append(child.data(0, QtCore.Qt.ItemDataRole.UserRole))
            print('ingredientList : ', ingredientList)
            return ingredientList

        def keepItemThatMatch(filtered):
            kept = []
            for obj, value in filtered:
                if value is True:
                    kept.append(obj)
            return kept

        # filter by tab
        print('tab filter')
        tabType = self.qtgroupBox.tabText(self.qtgroupBox.currentIndex())
        if tabType == "Toutes":
            filtered = [(obj, True) for obj in self.recipeDb.recipeList]
        else:
            tabType = tabType[:-1]
            filtered = self.recipeDb.filterRecipe(tabType, [], 'type')
        print('filtered tab :', filtered)

        #filter by ingredient filter
        kept = keepItemThatMatch(filtered)
        print('kept from tab:', kept)
        if self.qtFilterByIngredientCombo.currentText() == 'Ignore Ingredient Filter':
            print('ignore ingredient ok')
            pass
        else:
            ingredientList = retrieveIngredientList(self.qtFilterByIngredientCombo.currentText())
            filtered = self.recipeDb.filterRecipe(ingredientList, kept, 'ingredients')
            kept = keepItemThatMatch(filtered)
        print('filtered ingredient : ', filtered)
        print('kept ingredient : ', kept)

        #filter by recipe filter text TODO



        #apply results
        filtered = [(x, x in self.recipeDb.recipeList) for x in kept]
        # print((obj, val) for x in filtered)
        for recipeObj, match in filtered:
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


sys.argv += ['-platform', 'windows:darkmode=2']
app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')
libPath = 'E:/Scripts/Python/Recette/recette liste.ods'
# libPath = 'D:/Python/recette liste.ods'
window = MainWindow(libPath)
# window.show()
window.showMaximized()
app.exec()
#
# import pandas
# import odf
# import numpy
# import time
#
# p = "E:\Scripts\Python\Recette/recette liste.ods"
# data = pandas.read_excel(p, engine='odf', sheet_name="Recettes")
# print(data)
# now = time.time()
# daynow = time.strftime("%Y%m%d", time.gmtime(now))
# print(daynow)
# date = pandas.date_range(daynow, periods=7)
# print(date, date[0], isinstance(date[0], str))
# print(date[0])
# print(date[0].strftime("%A : %d %b"))
#
# print(list('tata yoyo'))
# table = pandas.DataFrame(numpy.random.randn(7, 4), index=date, columns=list('ABCD'))
# print(table)
#
# import Recette
# c = Recette.IngredientList()