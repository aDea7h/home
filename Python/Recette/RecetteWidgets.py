# from email.contentmanager import maintype

from PySide6 import QtCore, QtGui, QtWidgets
from TextEditorWidget import TextEdit
from Recette import Units

class GenericWidget(QtWidgets.QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # ----->> Ui Elements

        # ----->> Init Ui Elements

        # ----->> Set Layout


class IngredientWidget(QtWidgets.QWidget):
    def __init__(self, ui, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        #----->> Ui Elements
        self.qtIngredientFilter = QtWidgets.QLineEdit()
        self.qtIngredientCheckAllButton = QtWidgets.QPushButton("All")
        self.qtIngredientCheckNoneButton = QtWidgets.QPushButton("None")
        self.qtIngredientCheckInvertButton = QtWidgets.QPushButton("Invert")
        self.qtIngredientSelAllButton = QtWidgets.QPushButton("All")
        self.qtIngredientSelNoneButton = QtWidgets.QPushButton("None")
        self.qtIngredientSelInvertButton = QtWidgets.QPushButton("Invert")

        self.qtMeatColumnTree = QtWidgets.QTreeWidget()
        self.qtVegetableColumnTree = QtWidgets.QTreeWidget()
        self.qtStarchColumnTree = QtWidgets.QTreeWidget()
        self.qtOtherColumnTree = QtWidgets.QTreeWidget()

        self.ingredientWidgetList = [('meat', self.qtMeatColumnTree), ('vegetable', self.qtVegetableColumnTree),
                                     ('starch', self.qtStarchColumnTree), ('other', self.qtOtherColumnTree)]

        #----->> Init Ui Elements
        self.qtIngredientFilter.setClearButtonEnabled(True)
        self.qtIngredientFilter.addAction(self.ui['icons']['search'],
                                          QtWidgets.QLineEdit.ActionPosition.LeadingPosition)
        self.qtIngredientFilter.setPlaceholderText("Filter Ingredients")

        meatqtitem = QtWidgets.QTreeWidgetItem(['Meat'])
        meatqtitem.setIcon(0, self.ui['icons']['meat'])
        self.qtMeatColumnTree.setHeaderItem(meatqtitem)
        self.qtMeatColumnTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtMeatColumnTree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode(3))
        vegetableqtitem = QtWidgets.QTreeWidgetItem(['Vegetable'])
        vegetableqtitem.setIcon(0, self.ui['icons']['vegetable'])
        self.qtVegetableColumnTree.setHeaderItem(vegetableqtitem)
        self.qtVegetableColumnTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtVegetableColumnTree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode(3))
        starchqtitem = QtWidgets.QTreeWidgetItem(['Starch'])
        starchqtitem.setIcon(0, self.ui['icons']['starch'])
        self.qtStarchColumnTree.setHeaderItem(starchqtitem)
        self.qtStarchColumnTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtStarchColumnTree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode(3))
        self.qtOtherColumnTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Other']))
        self.qtOtherColumnTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtOtherColumnTree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode(3))

        #----->> Set Layout
        self.qtLabelIngredient = QtWidgets.QLabel("Ingredients")
        self.layout.addWidget(self.qtLabelIngredient)
        self.qtIngredientColumn = QtWidgets.QWidget()
        self.qtIngredientColumnLayout = QtWidgets.QHBoxLayout()
        self.qtIngredientColumn.setLayout(self.qtIngredientColumnLayout)
        self.qtIngredientActionWidget = QtWidgets.QWidget()
        self.qtIngredientActionWidgetLayout = QtWidgets.QVBoxLayout()

        # left buttons
        self.layout.addWidget(self.qtIngredientFilter)
        self.qtIngredientActionWidget.setLayout(self.qtIngredientActionWidgetLayout)
        self.qtIngredientAllLabel = QtWidgets.QLabel("Check")
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientAllLabel)
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientCheckAllButton)
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientCheckNoneButton)
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientCheckInvertButton)
        self.qtIngredientSelLabel = QtWidgets.QLabel("Select")
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientSelLabel)
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientSelAllButton)
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientSelNoneButton)
        self.qtIngredientActionWidgetLayout.addWidget(self.qtIngredientSelInvertButton)

        # ingredients columns
        self.qtIngredientColumnLayout.addWidget(self.qtIngredientActionWidget)
        self.qtIngredientColumnLayout.addWidget(self.qtMeatColumnTree)
        self.qtIngredientColumnLayout.addWidget(self.qtVegetableColumnTree)
        self.qtIngredientColumnLayout.addWidget(self.qtStarchColumnTree)
        self.qtIngredientColumnLayout.addWidget(self.qtOtherColumnTree)
        self.layout.addWidget(self.qtIngredientColumn)


class RecipeWidget(QtWidgets.QWidget):
    def __init__(self, outer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outer = outer
        self.ui = self.outer.ui
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.generateUi()
        self.setConnections()

    def generateUi(self):
        # ----->> Ui Elements
        self.qtRecipeFilter = QtWidgets.QLineEdit()
        self.qtFilterByIngredientCheckBox = QtWidgets.QCheckBox("Filter Recipe by Ingredients")
        self.qtFilterByIngredientCombo = QtWidgets.QComboBox()
        self.qtIngredientFilter = QtWidgets.QLineEdit()

        self.qtTreeRecipe = QtWidgets.QTreeWidget()

        # ----->> Init Ui Elements
        self.qtRecipeFilter.setClearButtonEnabled(True)
        self.qtRecipeFilter.addAction(self.ui['icons']['search'], QtWidgets.QLineEdit.ActionPosition.LeadingPosition)
        self.qtRecipeFilter.setPlaceholderText("Filter Recipe")
        self.qtFilterByIngredientCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
        self.qtIngredientFilter.setClearButtonEnabled(True)
        self.qtIngredientFilter.addAction(self.ui['icons']['search'], QtWidgets.QLineEdit.ActionPosition.LeadingPosition)
        self.qtIngredientFilter.setPlaceholderText('Filter Ingredients')
        self.qtFilterByIngredientCombo.addItems(
            ['Selected Ingredients', 'Visible Ingredients', 'Checked Ingredients'])

        self.qtTreeRecipe.setColumnCount(6)
        # self.qtTreeRecipe.setHeaderHidden(True)
        qtItem = QtWidgets.QTreeWidgetItem(['Recipe Name', 'Badges', 'Ingredients', 'Preparation Time', 'Total Time', 'Extra Infos'])
        # qtItem.setIcon(0, self.ui['icons']['star_empty'])
        self.qtTreeRecipe.setHeaderItem(qtItem)
        self.qtTreeRecipe.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # ----->> Set Layout
        # Recipe Tabs
        self.qtRecipeGroupBox = QtWidgets.QTabWidget()
        self.qtAllGroupPage = QtWidgets.QWidget()
        self.qtStarterGroupPage = QtWidgets.QWidget()
        self.qtDishGroupPage = QtWidgets.QWidget()
        self.qtDessertGroupPage = QtWidgets.QWidget()
        self.qtSauceGroupPage = QtWidgets.QWidget()
        self.qtPicnicGroupPage = QtWidgets.QWidget()
        self.qtSoupGroupPage = QtWidgets.QWidget()
        self.qtRecipeGroupBox.addTab(self.qtAllGroupPage, "All")
        self.qtRecipeGroupBox.addTab(self.qtStarterGroupPage, "Starter")
        self.qtRecipeGroupBox.addTab(self.qtDishGroupPage, "Dish")
        self.qtRecipeGroupBox.addTab(self.qtDessertGroupPage, "Dessert")
        self.qtRecipeGroupBox.addTab(self.qtSauceGroupPage, "Sauce")
        self.qtRecipeGroupBox.addTab(self.qtPicnicGroupPage, "Picnic")
        self.qtRecipeGroupBox.addTab(self.qtSoupGroupPage, "Soup")

        self.qtAllGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtStarterGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtDishGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtDessertGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtSauceGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtPicnicGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtSoupGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtAllGroupPage.setLayout(self.qtAllGroupPageLayout)
        self.qtStarterGroupPage.setLayout(self.qtStarterGroupPageLayout)
        self.qtDishGroupPage.setLayout(self.qtDishGroupPageLayout)
        self.qtDessertGroupPage.setLayout(self.qtDessertGroupPageLayout)
        self.qtSauceGroupPage.setLayout(self.qtSauceGroupPageLayout)
        self.qtPicnicGroupPage.setLayout(self.qtPicnicGroupPageLayout)
        self.qtSoupGroupPage.setLayout(self.qtSoupGroupPageLayout)
        #layout
        self.qtLabelRecipes = QtWidgets.QLabel('Recipes')
        self.layout.addWidget(self.qtLabelRecipes)
        self.layout.addWidget(self.qtRecipeFilter)
        self.layout.addWidget(self.qtFilterByIngredientCheckBox)
        self.layout.addWidget(self.qtIngredientFilter)
        self.layout.addWidget(self.qtFilterByIngredientCombo)
        self.layout.addWidget(self.qtRecipeGroupBox)
        self.qtAllGroupPageLayout.addWidget(self.qtTreeRecipe)

    def setConnections(self):
        self.qtRecipeGroupBox.currentChanged.connect(self.switchTab)

    def switchTab(self):
        idx = self.qtRecipeGroupBox.currentIndex()
        widget = self.qtRecipeGroupBox.widget(idx)
        layout = widget.layout()
        layout.addWidget(self.qtTreeRecipe)
        self.outer.filterRecipe()


class StockWidget(QtWidgets.QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # ----->> Ui Elements
        self.qtStockedCookedTree = QtWidgets.QTreeWidget()

        # ----->> Init Ui Elements
        self.qtStockedCookedTree.setColumnCount(4)
        qtItem = QtWidgets.QTreeWidgetItem(['Stocks', 'Share Nbr', 'Nbr', 'Date'])
        self.qtStockedCookedTree.setHeaderItem(qtItem)
        self.qtStockedCookedTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # ----->> Set Layout
        self.layout.addWidget(self.qtStockedCookedTree)


class GoalsAndNotesWidget(QtWidgets.QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        # ----->> Ui Elements
        self.qtGoalsTreeWidget = QtWidgets.QTreeWidget()
        self.qtNotesTextEdit = QtWidgets.QTextEdit()
        self.qtSaveNotesButton = QtWidgets.QPushButton('Save Notes')

        # ----->> Init Ui Elements
        self.qtGoalsTreeWidget.setColumnCount(3)
        self.qtGoalsTreeWidget.setHeaderItem(QtWidgets.QTreeWidgetItem(["Nbr", "Objectif par semaine", "Note"]))
        self.qtNotesTextEdit.setPlaceholderText('Take notes here')
        self.qtNotesTextEdit.setAutoFormatting(QtWidgets.QTextEdit.AutoFormattingFlag.AutoAll)

        # ----->> Set Layout
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                                 QtWidgets.QSizePolicy.Policy.Maximum)
        self.layout.addWidget(self.qtGoalsTreeWidget, 0, 0, 2, 1)
        self.layout.addWidget(self.qtNotesTextEdit, 0, 1)
        self.layout.addWidget(self.qtSaveNotesButton, 1, 1)

        # self.qtGoalsAndNotesWidget = QtWidgets.QWidget()
        # self.qtGoalsAndNotesWidgetLayout = QtWidgets.QGridLayout()
        # self.qtGoalsAndNotesWidget.setLayout(self.qtGoalsAndNotesWidgetLayout)
        # self.leftPaneLayout.addWidget(self.qtGoalsAndNotesWidget)
        # self.qtGoalsAndNotesWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
        #                                          QtWidgets.QSizePolicy.Policy.Maximum)


class MenuWidget(QtWidgets.QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        # ----->> Ui Elements
        self.qtTreeMenu = QtWidgets.QTreeWidget()
        self.qtMenuButtonUp = QtWidgets.QPushButton('Up')
        self.qtMenuButtonDown = QtWidgets.QPushButton('Down')

        # ----->> Init Ui Elements
        self.qtTreeMenu.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.qtTreeMenu.setColumnCount(2)
        self.qtTreeMenu.setHeaderItem(QtWidgets.QTreeWidgetItem(["Day", "Menu"]))
        self.qtTreeMenu.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtTreeMenu.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        # ----->> Set Layout

        self.qtLabelMenu = QtWidgets.QLabel('Menus :')
        # self.qtMenuOperations = QtWidgets.QWidget()
        # self.qtMenuOperationsLayout = QtWidgets.QGridLayout()
        # self.qtMenuOperations.setLayout(self.qtMenuOperationsLayout)

        self.layout.addWidget(self.qtLabelMenu, 0, 0)
        self.layout.addWidget(self.qtTreeMenu, 1, 0, 1, 2)
        self.layout.addWidget(self.qtMenuButtonUp, 2, 0)
        self.layout.addWidget(self.qtMenuButtonDown, 2, 1)


        # self.leftPaneLayout.addWidget(self.qtLabelMenu)
        # self.leftPaneLayout.addWidget(self.qtTreeMenu)
        # self.leftPaneLayout.addWidget(self.qtMenuOperations)


class GroceriesWidget(QtWidgets.QWidget):
    def __init__(self, outer):
        super().__init__()
        self.outer = outer
        self.ui = self.outer.ui
        self.aislesDefault = {
            'Special': [],
            'Meat': [],
            'Vegetable': [],
            'Other': [],
            'Always Available - to check': [],
        }
        self.aisles = {}
        self.reinitAisles()

        self.aislesIcons = {
            'Special': self.ui['icons']['warning'],
            'Meat': self.ui['icons']['meat'],
            'Vegetable': self.ui['icons']['vegetable'],
            'Always Available - to check': self.ui['icons']['ok'],
        }
        self.groceriesExport = ''
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        # ----->> Ui Elements
        self.qtGroceriesTree = QtWidgets.QTreeWidget()
        self.qtGroceriesRefreshButton = QtWidgets.QPushButton('Refresh Groceries')
        self.qtGroceriesCopyButton = QtWidgets.QPushButton('Copy to Clipboard')

        # ----->> Init Ui Elements
        self.qtGroceriesTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Ingredients :']))
        self.qtGroceriesTree.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Expanding)

        # ----->> Set Layout
        self.qtLabelGroceriesList = QtWidgets.QLabel('Grocery List')
        self.layout.addWidget(self.qtLabelGroceriesList, 0, 0, 1, 2)
        self.layout.addWidget(self.qtGroceriesTree, 1, 0, 1, 2)
        self.layout.addWidget(self.qtGroceriesRefreshButton, 2, 0, 1, 1)
        self.layout.addWidget(self.qtGroceriesCopyButton, 2, 1, 1, 1)

        self.setConnexions()

    def reinitAisles(self):
        self.aisles = {}
        for key in self.aislesDefault:
            self.aisles[key] = []

    def setConnexions(self):
        self.qtGroceriesCopyButton.clicked.connect(lambda: self.outer.copyToClipboard(self.groceriesExport))
        self.qtGroceriesRefreshButton.clicked.connect(self.outer.setGroceriesFromMenu)

    # def copyToClipboard(self):
    #     clipboard = QtGui.QGuiApplication.clipboard()
    #     clipboard.setText(self.groceriesExport)

    def splitIngredientsToAisle(self, ingredientList):
        for ingredient in ingredientList:
            if ingredient.special is True:
                self.aisles['Special'].append(ingredient)
            elif ingredient.always_available is True:
                self.aisles['Always Available - to check'].append(ingredient)
            elif ingredient.aisle is not None:
                if ingredient.aisle in self.aisles.keys():
                    self.aisles[ingredient.aisle].append(ingredient)
                else:
                    self.aisles[ingredient.aisle] = [ingredient]
            elif 'meat' in ingredient.family:
                self.aisles['Meat'].append(ingredient)
            elif 'vegetable' in ingredient.family or 'starch' in ingredient.family:
                self.aisles['Vegetable'].append(ingredient)
            else:
                self.aisles['Other'].append(ingredient)
        print(self.aisles)

    def createAisleItem(self, aisle):
        qtAisleItem = QtWidgets.QTreeWidgetItem([aisle])
        if aisle in self.aislesIcons:
            qtAisleItem.setIcon(0, self.aislesIcons[aisle])
        return qtAisleItem

    def createIngredientItem(self, ingredient, qtAisleItem):
        ingredientLabel = f'{ingredient.name} : {ingredient.size}{ingredient.unit}'
        qtIngredientItem = QtWidgets.QTreeWidgetItem(qtAisleItem, [ingredientLabel])
        ingredientExport = f'  - {ingredientLabel}\n'
        return ingredientExport

    def exportAisle(self, aisle):
        return f'\n\n####################\n# {aisle}\n####################\n'

    def setGroceries(self, ingredientList):
        topLevel = []
        self.qtGroceriesTree.clear()
        self.groceriesExport = ''
        self.reinitAisles()

        self.splitIngredientsToAisle(ingredientList)
        for aisle in self.aisles:
            ingredientList = self.aisles[aisle]
            qtAisleItem = self.createAisleItem(aisle)
            topLevel.append(qtAisleItem)
            self.groceriesExport += self.exportAisle(aisle)
            for ingredient in ingredientList:
                self.groceriesExport += self.createIngredientItem(ingredient, qtAisleItem)
            qtAisleItem.sortChildren(0, QtCore.Qt.SortOrder.AscendingOrder)
            # qtAisleItem.setExpanded(True)

        self.qtGroceriesTree.addTopLevelItems(topLevel)
        self.qtGroceriesTree.expandAll()
        self.outer.copyToClipboard(self.groceriesExport)


class RecipeContentWidget(QtWidgets.QWidget): #QDialog

    def __init__(self, parent, ui):
        super().__init__()
        self.parent = parent
        self.ui = ui
        self.setWindowTitle("Recipe Content")
        if self.ui['icons'] is not None:
            self.setWindowIcon(self.ui['icons']['menu'])

        # ----->> Ui Elements
        # recipe identity
        self.qtNameLineEdit = QtWidgets.QLineEdit()
        self.qtMatchNameLineEdit = QtWidgets.QLineEdit()
        self.qtCategoryTree = QtWidgets.QTreeWidget()
        self.qtStarterTypeCheckBox = QtWidgets.QCheckBox('Starter')
        self.qtDishTypeCheckBox = QtWidgets.QCheckBox('Dish')
        self.qtDessertTypeCheckBox = QtWidgets.QCheckBox('Desert')
        self.qtSauceTypeCheckBox = QtWidgets.QCheckBox('Sauce')
        self.qtOriginTree = QtWidgets.QTreeWidget()
        self.qtTagsLineEdit = QtWidgets.QLineEdit()
        # recipe content
        self.qtIngredients = QtWidgets.QTreeWidget()
        self.qtBeforeRecipeText = TextEdit()
        self.qtRecipeText = QtWidgets.QTextEdit()
        self.qtSuggestionTree = QtWidgets.QTreeWidget()
        self.qtNoteText = QtWidgets.QTextEdit()
        self.qtFilesTree = QtWidgets.QTreeWidget()
        # recipe meta
        self.qtCookingTimeSpin = QtWidgets.QSpinBox()
        self.qtPreparationTimeSpin = QtWidgets.QSpinBox()
        self.qtCookingFullTimeLineEdit = QtWidgets.QLineEdit()
        self.qtIsBestReheatedCheckBox = QtWidgets.QCheckBox('Is best reheated')
        self.qtRatingRadio0 = QtWidgets.QRadioButton('Has not been tested')
        self.qtRatingRadio1 = QtWidgets.QRadioButton('1')
        self.qtRatingRadio2 = QtWidgets.QRadioButton('2')
        self.qtRatingRadio3 = QtWidgets.QRadioButton('3')
        self.qtRatingRadio4 = QtWidgets.QRadioButton('4')
        self.qtRatingRadio5 = QtWidgets.QRadioButton('5')
        self.qtFavoriteCheckBox = QtWidgets.QCheckBox('Favorite')
        self.qtRecipeIsWipCheckBox = QtWidgets.QCheckBox('Recipe is not fully completed')
        # Validation Accept / Reject Buttons
        self.qtButtonBox = QtWidgets.QDialogButtonBox()
        self.validationButton = QtWidgets.QPushButton("Save Recipe")
        self.qtButtonBox.addButton(self.validationButton, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.qtButtonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        self.qtEditButton = QtWidgets.QPushButton("Edit")
        self.qtCloseButton = QtWidgets.QPushButton("Close")

        # ----->> Init Ui Elements
        self.qtCookingTimeSpin.setRange(0, 999)
        self.qtPreparationTimeSpin.setRange(0, 999)
        self.qtRecipeText.setPlaceholderText("Type recipe here")
        self.qtBeforeRecipeText.setPlaceholderText("Preparation to be done the day before")
        self.qtNoteText.setPlaceholderText("Extr notes...")
        font = self.qtNameLineEdit.font()
        font.setPointSize(24)
        self.qtNameLineEdit.setFont(font)
        self.qtNameLineEdit.setPlaceholderText('Name')
        self.qtMatchNameLineEdit.setPlaceholderText('Additional matching names (separated by ",")')
        self.qtCategoryTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Nest recipe in category.ies']))
        self.qtCategoryTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtOriginTree.setHeaderItem(QtWidgets.QTreeWidgetItem(["Recipe's origin"]))
        self.qtOriginTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtTagsLineEdit.setPlaceholderText('tags (separated by ",")')
        self.qtIngredients.setColumnCount(2)
        self.qtIngredients.setHeaderItem(QtWidgets.QTreeWidgetItem(['Ingredients', 'Servings']))
        self.qtIngredients.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtSuggestionTree.setHeaderItem(QtWidgets.QTreeWidgetItem(["Side Dish Suggestion"]))
        self.qtCookingFullTimeLineEdit.setEnabled(False)
        self.qtFilesTree.setHeaderItem(QtWidgets.QTreeWidgetItem(["Photos / Files"]))

        # ----->> Setup Ui

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        scrollPane = QtWidgets.QScrollArea()
        scrollPane.setWidgetResizable(True)
        self.leftPane = QtWidgets.QWidget()
        self.leftPaneLayout = QtWidgets.QVBoxLayout()
        self.leftPane.setLayout(self.leftPaneLayout)
        # self.leftPane.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.layout.addWidget(scrollPane, 1, 0)
        # scrollPaneLayout.addWidget(self.leftPane)
        scrollPane.setWidget(self.leftPane)


        # Setup UI Layout
        self.layout.addWidget(self.qtNameLineEdit, 0, 0)
        typeGroupBox = QtWidgets.QGroupBox()
        typeGroupBox.setTitle('Recipe Type')
        typeGroupBoxLayout = QtWidgets.QHBoxLayout()
        typeGroupBox.setLayout(typeGroupBoxLayout)
        typeGroupBoxLayout.addWidget(self.qtStarterTypeCheckBox)
        typeGroupBoxLayout.addWidget(self.qtDishTypeCheckBox)
        typeGroupBoxLayout.addWidget(self.qtDessertTypeCheckBox)
        typeGroupBoxLayout.addWidget(self.qtSauceTypeCheckBox)

        timeGroupBox = QtWidgets.QGroupBox()
        timeGroupBox.setTitle('Time')
        timeGroupBoxLayout = QtWidgets.QGridLayout()
        timeGroupBox.setLayout(timeGroupBoxLayout)
        timeGroupBoxLayout.addWidget(QtWidgets.QLabel('Full Time Needed'), 0, 0)
        timeGroupBoxLayout.addWidget(self.qtCookingFullTimeLineEdit, 0, 1)
        timeGroupBoxLayout.addWidget(QtWidgets.QLabel('Preparation Time (min)'), 1, 0)
        timeGroupBoxLayout.addWidget(self.qtPreparationTimeSpin, 1, 1)
        timeGroupBoxLayout.addWidget(QtWidgets.QLabel('Cooking Time (min)'), 1, 2)
        timeGroupBoxLayout.addWidget(self.qtCookingTimeSpin, 1, 3)
        timeGroupBoxLayout.addWidget(self.qtIsBestReheatedCheckBox)

        ratingGroupBox = QtWidgets.QGroupBox()
        ratingGroupBox.setTitle('Rating')
        ratingGroupBoxLayout = QtWidgets.QGridLayout()
        ratingGroupBox.setLayout(ratingGroupBoxLayout)
        ratingGroupBoxLayout.addWidget(self.qtRatingRadio0, 0, 0)
        ratingGroupBoxLayout.addWidget(self.qtRatingRadio1, 0, 1)
        ratingGroupBoxLayout.addWidget(self.qtRatingRadio2, 0, 2)
        ratingGroupBoxLayout.addWidget(self.qtRatingRadio3, 0, 3)
        ratingGroupBoxLayout.addWidget(self.qtRatingRadio4, 0, 4)
        ratingGroupBoxLayout.addWidget(self.qtRatingRadio5, 0, 5)
        ratingGroupBoxLayout.addWidget(self.qtFavoriteCheckBox, 0, 6)

        #recipe identity
        identityGroupBox = QtWidgets.QGroupBox()
        identityGroupBox.setTitle('Recipe Identity')
        identityGroupBoxLayout = QtWidgets.QGridLayout()
        identityGroupBox.setLayout(identityGroupBoxLayout)
        identityGroupBoxLayout.addWidget(self.qtMatchNameLineEdit, 0, 0)
        identityGroupBoxLayout.addWidget(typeGroupBox, 1, 0)
        identityGroupBoxLayout.addWidget(self.qtCategoryTree, 2, 0)
        identityGroupBoxLayout.addWidget(self.qtOriginTree, 0, 1)
        identityGroupBoxLayout.addWidget(self.qtTagsLineEdit, 1, 1)

        self.qtDisplayButtonsWidget = QtWidgets.QWidget()
        self.qtDisplayButtonsWidgetLayout = QtWidgets.QHBoxLayout()
        self.qtDisplayButtonsWidget.setLayout(self.qtDisplayButtonsWidgetLayout)
        self.qtDisplayButtonsWidgetLayout.addWidget(self.qtEditButton)
        self.qtDisplayButtonsWidgetLayout.addWidget(self.qtCloseButton)


        #recipe content
        contentGroupBox = QtWidgets.QGroupBox()
        contentGroupBox.setTitle('Recipe Content')
        contentGroupBoxLayout = QtWidgets.QGridLayout()
        contentGroupBox.setLayout(contentGroupBoxLayout)
        contentGroupBoxLayout.addWidget(self.qtIngredients, 0, 0)
        contentGroupBoxLayout.addWidget(self.qtBeforeRecipeText, 1, 0)
        contentGroupBoxLayout.addWidget(self.qtRecipeText, 2, 0)
        contentGroupBoxLayout.addWidget(self.qtSuggestionTree, 3, 0)
        contentGroupBoxLayout.addWidget(self.qtNoteText, 0, 1)
        contentGroupBoxLayout.addWidget(self.qtFilesTree, 1, 1)

        # recipe meta
        metaGroupBox = QtWidgets.QGroupBox()
        metaGroupBox.setTitle('Recipe Meta')
        metaGroupBoxLayout = QtWidgets.QGridLayout()
        metaGroupBox.setLayout(metaGroupBoxLayout)
        metaGroupBoxLayout.addWidget(timeGroupBox, 0, 0)
        metaGroupBoxLayout.addWidget(ratingGroupBox, 1, 0)

        self.leftPaneLayout.addWidget(identityGroupBox)
        self.leftPaneLayout.addWidget(contentGroupBox)
        self.leftPaneLayout.addWidget(metaGroupBox)
        self.leftPaneLayout.addWidget(self.qtRecipeIsWipCheckBox)
        self.layout.addWidget(self.qtButtonBox, 2, 0)
        self.layout.addWidget(self.qtDisplayButtonsWidget, 3, 0)

    def clear(self):
        self.qtNameLineEdit.clear()
        self.qtMatchNameLineEdit.clear()
        # self.qtCategoryTree = QtWidgets.QTreeWidget()
        self.qtStarterTypeCheckBox.setChecked(False)
        self.qtDishTypeCheckBox.setChecked(False)
        self.qtDessertTypeCheckBox.setChecked(False)
        self.qtSauceTypeCheckBox.setChecked(False)
        # self.qtOriginTree = QtWidgets.QTreeWidget()
        self.qtTagsLineEdit.clear()
        # recipe content
        self.qtIngredients.clear()
        self.qtBeforeRecipeText.clear()
        self.qtRecipeText.clear()
        self.qtSuggestionTree.clear()
        self.qtNoteText.clear()
        self.qtFilesTree.clear()
        # recipe meta
        self.qtCookingTimeSpin.setValue(0)
        self.qtPreparationTimeSpin.setValue(0)
        # self.qtCookingFullTimeLineEdit = QtWidgets.QLineEdit()
        self.qtIsBestReheatedCheckBox.setChecked(False)
        self.qtRatingRadio0.setChecked(True)
        self.qtRatingRadio1.setChecked(False)
        self.qtRatingRadio2.setChecked(False)
        self.qtRatingRadio3.setChecked(False)
        self.qtRatingRadio4.setChecked(False)
        self.qtRatingRadio5.setChecked(False)
        self.qtFavoriteCheckBox.setChecked(False)
        self.qtRecipeIsWipCheckBox.setChecked(False)
        # Validation Accept / Reject Buttons
        # self.qtButtonBox = QtWidgets.QDialogButtonBox()

    def setUiEnabled(self, enabled):
        self.qtNameLineEdit.setEnabled(enabled)
        self.qtMatchNameLineEdit.setEnabled(enabled)
        self.qtCategoryTree.setEnabled(enabled)
        self.qtStarterTypeCheckBox.setEnabled(enabled)
        self.qtDishTypeCheckBox.setEnabled(enabled)
        self.qtDessertTypeCheckBox.setEnabled(enabled)
        self.qtSauceTypeCheckBox.setEnabled(enabled)
        self.qtOriginTree.setEnabled(enabled)
        self.qtTagsLineEdit.setEnabled(enabled)
        # recipe content
        self.qtIngredients.setEnabled(enabled)
        self.qtBeforeRecipeText.setEnabled(enabled)
        self.qtRecipeText.setEnabled(enabled)
        self.qtSuggestionTree.setEnabled(enabled)
        self.qtNoteText.setEnabled(enabled)
        self.qtFilesTree.setEnabled(enabled)
        # recipe meta
        self.qtCookingTimeSpin.setEnabled(enabled)
        self.qtPreparationTimeSpin.setEnabled(enabled)
        self.qtIsBestReheatedCheckBox.setEnabled(enabled)
        self.qtRatingRadio0.setEnabled(enabled)
        self.qtRatingRadio1.setEnabled(enabled)
        self.qtRatingRadio2.setEnabled(enabled)
        self.qtRatingRadio3.setEnabled(enabled)
        self.qtRatingRadio4.setEnabled(enabled)
        self.qtRatingRadio5.setEnabled(enabled)
        self.qtFavoriteCheckBox.setEnabled(enabled)
        self.qtRecipeIsWipCheckBox.setEnabled(enabled)
        # Validation Accept / Reject Buttons
        self.qtButtonBox.setEnabled(enabled)
        # self.qtDisplayButtonsWidget.setEnabled(enabled)


class MenuTreeWidgetContent(QtWidgets.QTreeWidgetItem):
    def __init__(self, outer, name, obj):
        super().__init__()
        self.outer = outer
        self.name = name
        self.obj = obj
        self.setData(1, QtCore.Qt.ItemDataRole.UserRole, obj)
        self.setData(0, QtCore.Qt.ItemDataRole.UserRole, 'RecipeItem')

        styleSheetShopping = """QCheckBox::indicator:unchecked {image: url(./icons/shoppingCart.png);height: 15px;width: 15px;}
        QCheckBox::indicator:checked {image: url(./icons/shoppingCartFade.png);height: 15px;width: 15px;}"""
        styleSheetPreCooked = """QCheckBox::indicator:unchecked {image: url(./icons/precooked.png);height: 15px;width: 15px;}
        QCheckBox::indicator:checked {image: url(./icons/precookedFade.png);height: 15px;width: 15px;}"""
        styleSheetLeftover = """QCheckBox::indicator:unchecked {image: url(./icons/leftover2.png);height: 15px;width: 15px;}
        QCheckBox::indicator:checked {image: url(./icons/leftover2Fade.png);height: 15px;width: 15px;}"""

        self.styles = {
            'is_bought': styleSheetShopping,
            'is_preCooked': styleSheetPreCooked,
            'is_leftover': styleSheetLeftover,
        }


        self.qtIngredientTreeWidgetItem = QtWidgets.QTreeWidgetItem(self, ['', ''])
        self.qtIngredientTreeWidgetItem.setData(0, QtCore.Qt.ItemDataRole.UserRole, 'IngredientItem')
        self.qtRecipeNameWidget = self.createRecipeNameWidget(name)
        self.qtIngredientWidget = QtWidgets.QWidget()
        self.ingredientLayout = QtWidgets.QVBoxLayout()
        self.ingredientLayout.setSpacing(0)
        self.ingredientLayout.setContentsMargins(33, 0, 11, 11)
        self.qtIngredientWidget.setLayout(self.ingredientLayout)
        self.refreshIngredientsList()
        self.applyObjData()
        self.setExpanded(True)
        self.qtIngredientTreeWidgetItem.setExpanded(True)


    def createRecipeNameWidget(self, name):
        widget = QtWidgets.QGroupBox()
        layout = QtWidgets.QVBoxLayout()
        # layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        subTitleWidget = QtWidgets.QWidget()
        subTitleWidgetLayout = QtWidgets.QHBoxLayout()
        subTitleWidgetLayout.setSpacing(5)
        subTitleWidgetLayout.setContentsMargins(11, 7, 11, 7)
        subTitleWidget.setLayout(subTitleWidgetLayout)
        layout.addWidget(subTitleWidget)

        self.qtBought = QtWidgets.QCheckBox()
        # self.qtBought.setIcon(self.outer.ui['icons']['shoppingCartFade'])
        # styleSheet = """QCheckBox::indicator:unchecked {image: url(./icons/shoppingCart.png);height: 15px;width: 15px;}
        # QCheckBox::indicator:checked {image: url(./icons/shoppingCartFade.png);height: 15px;width: 15px;}"""

        self.qtBought.setStyleSheet(self.styles['is_bought'])
        self.qtBought.setToolTip('is already bought')
        self.qtBought.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        subTitleWidgetLayout.addWidget(self.qtBought)

        nameWidget = QtWidgets.QLabel(name)
        nameWidget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        subTitleWidgetLayout.addWidget(nameWidget)

        self.qtLeftover = QtWidgets.QCheckBox()
        self.qtLeftover.setToolTip('is some left over')
        self.qtLeftover.setStyleSheet(self.styles['is_leftover'])
        self.qtLeftover.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        subTitleWidgetLayout.addWidget(self.qtLeftover)

        self.qtPreprepared = QtWidgets.QCheckBox()
        self.qtPreprepared.setToolTip('is pre-prepared')
        self.qtPreprepared.setStyleSheet(self.styles['is_preCooked'])
        self.qtPreprepared.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        subTitleWidgetLayout.addWidget(self.qtPreprepared)

        spacer = QtWidgets.QSpacerItem(2, 2, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        subTitleWidgetLayout.addItem(spacer)

        return widget

    def createSingleIngredient(self, ingredient):
        widget = QtWidgets.QWidget()
        widget.setProperty('obj', ingredient)
        layout = QtWidgets.QGridLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        bought = QtWidgets.QCheckBox()
        bought.setToolTip('is already bought')
        bought.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(bought, 0, 0)

        size = QtWidgets.QSpinBox()
        size.setRange(0, 999)
        size.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(size, 0, 1)

        unit = QtWidgets.QComboBox()
        unit.addItems(Units().nameList)
        unit.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(unit, 0, 2)

        name = QtWidgets.QLabel(f' of {ingredient.name}')
        name.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(name, 0, 3)

        spacer = QtWidgets.QSpacerItem(2, 2, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacer, 0, 4)

        return widget

    def refreshIngredientsList(self):
        if self.ingredientLayout.count() != 0:
            self.updateObjFromUi()
        for idx in reversed(range(self.ingredientLayout.count())):
            widget = self.ingredientLayout.itemAt(idx).widget()
            widget.deleteLater()

        if self.obj:
            if type(self.obj).__name__ == "Ingredient":
                ingredientList = [self.obj.name]
            else:
                ingredientList = self.obj.ingredients

            for ingredient in ingredientList:
                self.ingredientLayout.addWidget(self.createSingleIngredient(ingredient))

    def applyObjData(self):
        # if ingredient.size:
        #     size.setValue(ingredient.size)
        try:
            self.qtBought.setCheckState(QtCore.Qt.CheckState(self.obj.is_bought * 2))
            self.qtLeftover.setCheckState(QtCore.Qt.CheckState(self.obj.is_leftover * 2))
            self.qtPreprepared.setCheckState(QtCore.Qt.CheckState(self.obj.is_preprepared * 2))
        except AttributeError:
            pass

        for idx in range(self.ingredientLayout.count()):
            widget = self.ingredientLayout.itemAt(idx).widget()
            ingredientObj = widget.property('obj')
            try:
                sizeWidget = widget.layout().itemAtPosition(0, 1).widget()
                sizeWidget.setValue(ingredientObj.size)
                boughtWidget = widget.layout().itemAtPosition(0, 0).widget()
                boughtWidget.setCheckState(QtCore.Qt.CheckState(ingredientObj.bought *2))
                unitWidget = widget.layout().itemAtPosition(0, 2).widget()
                unitWidget.setCurrentText(ingredientObj.unit)
            except AttributeError:
                pass

    def updateObjFromUi(self):
        self.obj.is_bought = self.qtBought.checkState() == QtCore.Qt.CheckState.Checked
        self.obj.is_leftover = self.qtLeftover.checkState() == QtCore.Qt.CheckState.Checked
        self.obj.is_preprepared = self.qtPreprepared.checkState() == QtCore.Qt.CheckState.Checked
        print(f'-->update obj from ui for {self.obj.name}')
        print(f'bought : {self.obj.is_bought}, is leftover : {self.obj.is_leftover}, is preperaed : {self.obj.is_preprepared}')
        for idx in reversed(range(self.ingredientLayout.count())):
            widget = self.ingredientLayout.itemAt(idx).widget()
            ingredientObj = widget.property('obj')
            boughtWidget = widget.layout().itemAtPosition(0, 0).widget()
            ingredientObj.bought = boughtWidget.checkState() == QtCore.Qt.CheckState.Checked
            sizeWidget = widget.layout().itemAtPosition(0, 1).widget()
            ingredientObj.size = sizeWidget.value()
            unitWidget = widget.layout().itemAtPosition(0, 2).widget()
            ingredientObj.unit = unitWidget.currentText()

            print(f'{ingredientObj.name} : {ingredientObj.bought}, {ingredientObj.size}, {ingredientObj.unit}')

        return self.obj


