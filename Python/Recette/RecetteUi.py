from PySide6 import QtCore, QtGui, QtWidgets
import sys
import Recette
# import tools

# TODO
"""
recette in multicategory : pates pesto ds sauce et dans pates

"""

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, libPath='E:/Scripts/Python/Recette/recette liste.ods', *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.mainWidget = QtWidgets.QWidget()
        self.libPath = libPath
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle("Recettes")
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralLayout = QtWidgets.QGridLayout()
        self.centralWidget.setLayout(self.centralLayout)

        self.headerPaneWidget = QtWidgets.QWidget()
        self.headerPaneWidgetLayout = QtWidgets.QVBoxLayout()
        self.headerPaneWidget.setLayout(self.headerPaneWidgetLayout)
        # self.centralLayout.addWidget(self.headerPaneWidget, 0, 0, 1, 2)

        self.leftPaneWidget = QtWidgets.QWidget()
        self.leftPaneLayout = QtWidgets.QVBoxLayout()
        self.leftPaneWidget.setLayout(self.leftPaneLayout)
        self.centralLayout.addWidget(self.leftPaneWidget, 1, 0)
        self.rightPaneWidget = QtWidgets.QWidget()
        self.rightPaneLayout = QtWidgets.QVBoxLayout()
        self.rightPaneWidget.setLayout(self.rightPaneLayout)
        self.centralLayout.addWidget(self.rightPaneWidget, 1, 1)

        # Header Pane Widget
        self.qtCalendar = QtWidgets.QCalendarWidget()
        self.headerPaneWidgetLayout.addWidget(self.qtCalendar)

        # Left Pane Widget
        self.qtLabelFilter = QtWidgets.QLabel("Ingredients")
        # self.qtIngredientList = QtWidgets.QListWidget()
        self.leftPaneLayout.addWidget(self.qtLabelFilter)
        # self.leftPaneLayout.addWidget(self.qtIngredientList)

        self.qtIngredientColumn = QtWidgets.QWidget()
        self.qtIngredientColumnLayout = QtWidgets.QHBoxLayout()
        self.qtIngredientColumn.setLayout(self.qtIngredientColumnLayout)
        self.qtViandesColumnTree = QtWidgets.QTreeWidget()
        self.qtViandesColumnTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Viande']))
        self.qtViandesColumnTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtLegumesColumnTree = QtWidgets.QTreeWidget()
        self.qtLegumesColumnTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Legumes']))
        self.qtLegumesColumnTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtFeculentsColumnTree = QtWidgets.QTreeWidget()
        self.qtFeculentsColumnTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Feculents']))
        self.qtFeculentsColumnTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtDiversColumnTree = QtWidgets.QTreeWidget()
        self.qtDiversColumnTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Divers']))
        self.qtDiversColumnTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtIngredientColumnLayout.addWidget(self.qtViandesColumnTree)
        self.qtIngredientColumnLayout.addWidget(self.qtLegumesColumnTree)
        self.qtIngredientColumnLayout.addWidget(self.qtFeculentsColumnTree)
        self.qtIngredientColumnLayout.addWidget(self.qtDiversColumnTree)
        self.leftPaneLayout.addWidget(self.qtIngredientColumn)




        self.qtLabelRecipes = QtWidgets.QLabel('Recettes')
        self.qtSearch = QtWidgets.QLineEdit('Search Bar')




        #
        self.qtgroupBox = QtWidgets.QTabWidget()
        self.qtToutesGroupPage = QtWidgets.QWidget()
        self.qtEntreeGroupPage = QtWidgets.QWidget()
        self.qtPlatGroupPage = QtWidgets.QWidget()
        self.qtDessertGroupPage = QtWidgets.QWidget()
        self.qtSauceGroupPage = QtWidgets.QWidget()
        self.qtgroupBox.addTab(self.qtToutesGroupPage, "Toutes")
        self.qtgroupBox.addTab(self.qtEntreeGroupPage, "Entree")
        self.qtgroupBox.addTab(self.qtPlatGroupPage, "Plat")
        self.qtgroupBox.addTab(self.qtDessertGroupPage, "Dessert")
        self.qtgroupBox.addTab(self.qtSauceGroupPage, "Sauce")
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


        self.qtTreeRecipe = QtWidgets.QTreeWidget()
        self.qtTreeRecipe.setColumnCount(1)
        self.qtTreeRecipe.setHeaderHidden(True)
        self.qtTreeRecipe.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)





        self.leftPaneLayout.addWidget(self.qtLabelRecipes)

        self.leftPaneLayout.addWidget(self.qtSearch)
        self.leftPaneLayout.addWidget(self.qtgroupBox)
        self.qtToutesGroupPageLayout.addWidget(self.qtTreeRecipe)




        # Right Pane Widget
        self.qtLabelMenu = QtWidgets.QLabel('Menus :')

        self.qtButtonOther = QtWidgets.QPushButton('Autre')
        self.qtButtonRestes = QtWidgets.QPushButton('Restes')
        self.qtButtonRestaurant = QtWidgets.QPushButton('Restaurant')
        self.qtspecialMenu = QtWidgets.QWidget()
        self.qtspecialMenuLayout = QtWidgets.QGridLayout()
        self.qtspecialMenu.setLayout(self.qtspecialMenuLayout)
        self.qtspecialMenuLayout.addWidget(self.qtButtonOther, 0, 0)
        self.qtspecialMenuLayout.addWidget(self.qtButtonRestes, 0, 1)
        self.qtspecialMenuLayout.addWidget(self.qtButtonRestaurant, 0, 2)

        self.qtTreeMenu = QtWidgets.QTreeWidget()
        self.qtTreeMenu.setColumnCount(3)
        self.qtTreeMenu.setHeaderItem(QtWidgets.QTreeWidgetItem(["Jour", "Menu", "Nbr"]))
        self.qtTreeMenu.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.qtAddToMenuButton = QtWidgets.QPushButton("Ajouter la recette au menu selectionne")
        self.qtLabelGroceriesList = QtWidgets.QLabel('Liste des Courses')
        self.qtGroceriesList = QtWidgets.QListWidget()
        #
        self.rightPaneLayout.addWidget(self.qtLabelMenu)
        self.rightPaneLayout.addWidget(self.qtTreeMenu)
        self.rightPaneLayout.addWidget(self.qtspecialMenu)
        self.rightPaneLayout.addWidget(self.qtAddToMenuButton)
        self.rightPaneLayout.addWidget(self.qtLabelGroceriesList)
        self.rightPaneLayout.addWidget(self.qtGroceriesList)

        self.setConnections()

        self.ingredientsDb = None
        self.setIngredients()

        self.recipeDb = None
        self.setRecipe()
        self.initMenus()



    def setIngredients(self):
        self.ingredientsDb = Recette.IngredientList(self.libPath)

        qtIngredientDic = {
        'viande':[],
        'legume':[],
        'feculent':[],
        'divers':[]
        }
        categoryDict = {}
        for ingredientObj in self.ingredientsDb.ingredientList:
            if ingredientObj.visible is False:
                continue
            qtitem = QtWidgets.QTreeWidgetItem([ingredientObj.name])
            print(ingredientObj.name, ingredientObj.category, ingredientObj.family)
            if ingredientObj.category is None:
                qtIngredientDic[ingredientObj.family[0]].append(qtitem)
            else:
                cat = ingredientObj.category[0]
                if cat not in categoryDict:
                    qtcatitem = QtWidgets.QTreeWidgetItem([cat])
                    qtIngredientDic[ingredientObj.family[0]].append(qtcatitem)
                    categoryDict[cat] = qtcatitem
                else:
                    qtcatitem = categoryDict[cat]
                qtcatitem.addChild(qtitem)
        self.qtViandesColumnTree.addTopLevelItems(qtIngredientDic['viande'])
        self.qtLegumesColumnTree.addTopLevelItems(qtIngredientDic['legume'])
        self.qtFeculentsColumnTree.addTopLevelItems(qtIngredientDic['feculent'])
        self.qtDiversColumnTree.addTopLevelItems(qtIngredientDic['divers'])
        self.qtViandesColumnTree.expandAll()
        self.qtViandesColumnTree.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.qtLegumesColumnTree.expandAll()
        self.qtLegumesColumnTree.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.qtFeculentsColumnTree.expandAll()
        self.qtFeculentsColumnTree.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.qtDiversColumnTree.expandAll()
        self.qtDiversColumnTree.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)

    def setRecipe(self):
        self.recipeDb = Recette.RecipeList(self.libPath)
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

    def initMenus(self):
        self.dayDb = Recette.DayList()
        qtDaysList = []
        for dayObj in self.dayDb.dayList:
            # dayObj.lunchQtitem = QtWidgets.QListWidgetItem('{} midi'.format(dayObj.name))
            # dayObj.dinerQtitem = QtWidgets.QListWidgetItem('{} soir'.format(dayObj.name))
            # self.qtTreeMenu.addItem(dayObj.lunchQtitem)
            # self.qtTreeMenu.addItem(dayObj.dinerQtitem)
            qtDay = QtWidgets.QTreeWidgetItem([dayObj.name, "", ""])
            qtDaysList.append(qtDay)
            qtLunch = QtWidgets.QTreeWidgetItem(qtDay, ['Midi', '', ''])
            qtDinner = QtWidgets.QTreeWidgetItem(qtDay, ['Soir', '', ''])
        self.qtTreeMenu.addTopLevelItems(qtDaysList)
        self.qtTreeMenu.expandAll()

    def setConnections(self):
        self.qtAddToMenuButton.clicked.connect(self.addRecipeToMenu)
        self.qtgroupBox.currentChanged.connect(self.changeTab)
        self.qtButtonOther.clicked.connect(lambda: self.addSpecialToMenu(' - Autre'))
        self.qtButtonRestes.clicked.connect(lambda: self.addSpecialToMenu(' - Restes'))
        self.qtButtonRestaurant.clicked.connect(lambda: self.addSpecialToMenu(' - Restaurant'))

        self.qtViandesColumnTree.customContextMenuRequested.connect(self.viandeContextMenu)
        self.qtLegumesColumnTree.customContextMenuRequested.connect(self.legumeContextMenu)
        self.qtFeculentsColumnTree.customContextMenuRequested.connect(self.feculentContextMenu)
        self.qtDiversColumnTree.customContextMenuRequested.connect(self.diversContextMenu)
        self.qtTreeRecipe.customContextMenuRequested.connect(self.recipeContextMenu)
        self.qtTreeMenu.customContextMenuRequested.connect(self.menuContextMenu)


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
        addToMenuAction.triggered.connect(lambda: self.addToMenu(item.text(0), False))
        replaceMenuAction.triggered.connect(lambda: self.addToMenu(item.text(0), True))
        self.qtRecipeContextMenu.addAction(addToMenuAction)
        self.qtRecipeContextMenu.addAction(replaceMenuAction)
        self.qtRecipeContextMenu.exec(position)

    def menuContextMenu(self, position):
        print("menu context menu")
        position = self.qtTreeMenu.viewport().mapToGlobal(position)
        item = self.qtTreeMenu.currentItem()
        self.qtMenuContextMenu = QtWidgets.QMenu(self)
        autreReplaceMenuAction = QtGui.QAction('Autre')
        restesReplaceMenuAction = QtGui.QAction('Restes')
        restaurantReplaceMenuAction = QtGui.QAction('Restaurant')
        clearReplaceMenuAction = QtGui.QAction('Supprimer Menu')
        autreReplaceMenuAction.triggered.connect(lambda: self.addToMenu('Autre', True))
        restesReplaceMenuAction.triggered.connect(lambda: self.addToMenu('Restes', True))
        restaurantReplaceMenuAction.triggered.connect(lambda: self.addToMenu('Restaurant', True))
        clearReplaceMenuAction.triggered.connect(lambda: self.addToMenu('', True))
        self.qtMenuContextMenu.addAction(autreReplaceMenuAction)
        self.qtMenuContextMenu.addAction(restesReplaceMenuAction)
        self.qtMenuContextMenu.addAction(restaurantReplaceMenuAction)
        self.qtMenuContextMenu.addAction(clearReplaceMenuAction)
        self.qtMenuContextMenu.exec(position)

    def addToMenu(self, menuText, replace=True):
        menu = self.getMenuSelection()
        if menu is None:
            return
        if replace is False:
            text = menu.text(1)
            if text != "":
                text += ", "
            menu.setText(1, text+menuText)
        else:
            menu.setText(1, menuText)



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


    def filterRecipe(self):
        for recipeObj in self.recipeDb.recipeList:
            # filter recipe type
            type = recipeObj.type
            tabType = self.qtgroupBox.tabText(self.qtgroupBox.currentIndex())
            if tabType == "Toutes" or tabType.lower() == type.lower():
                hidden = False
            else:
                hidden = True
            recipeObj.qtitem.setHidden(hidden)

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