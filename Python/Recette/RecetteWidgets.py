from PySide6 import QtCore, QtGui, QtWidgets


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
    def __init__(self, ui, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

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

        self.qtTreeRecipe.setColumnCount(1)
        self.qtTreeRecipe.setHeaderHidden(True)
        self.qtTreeRecipe.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # ----->> Set Layout
        # Recipe Tabs
        self.qtRecipeGroupBox = QtWidgets.QTabWidget()
        self.qtAllGroupPage = QtWidgets.QWidget()
        self.qtStarterGroupPage = QtWidgets.QWidget()
        self.qtDishGroupPage = QtWidgets.QWidget()
        self.qtDessertGroupPage = QtWidgets.QWidget()
        self.qtSauceGroupPage = QtWidgets.QWidget()
        self.qtRecipeGroupBox.addTab(self.qtAllGroupPage, "All")
        self.qtRecipeGroupBox.addTab(self.qtStarterGroupPage, "Starters")
        self.qtRecipeGroupBox.addTab(self.qtDishGroupPage, "Dishes")
        self.qtRecipeGroupBox.addTab(self.qtDessertGroupPage, "Desserts")
        self.qtRecipeGroupBox.addTab(self.qtSauceGroupPage, "Sauces")

        self.qtAllGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtStarterGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtDishGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtDessertGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtSauceGroupPageLayout = QtWidgets.QVBoxLayout()
        self.qtAllGroupPage.setLayout(self.qtAllGroupPageLayout)
        self.qtStarterGroupPage.setLayout(self.qtStarterGroupPageLayout)
        self.qtDishGroupPage.setLayout(self.qtDishGroupPageLayout)
        self.qtDessertGroupPage.setLayout(self.qtDessertGroupPageLayout)
        self.qtSauceGroupPage.setLayout(self.qtSauceGroupPageLayout)
        #layout
        self.qtLabelRecipes = QtWidgets.QLabel('Recipes')
        self.layout.addWidget(self.qtLabelRecipes)
        self.layout.addWidget(self.qtRecipeFilter)
        self.layout.addWidget(self.qtFilterByIngredientCheckBox)
        self.layout.addWidget(self.qtIngredientFilter)
        self.layout.addWidget(self.qtFilterByIngredientCombo)
        self.layout.addWidget(self.qtRecipeGroupBox)
        self.qtAllGroupPageLayout.addWidget(self.qtTreeRecipe)


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
        self.qtTreeMenu.setColumnCount(3)
        self.qtTreeMenu.setHeaderItem(QtWidgets.QTreeWidgetItem(["Day", "Menu", "Notes"]))
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
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # ----->> Ui Elements
        self.qtGroceriesTree = QtWidgets.QTreeWidget()
        qtSpecialItem = QtWidgets.QTreeWidgetItem(['Special'])
        qtMeatItem = QtWidgets.QTreeWidgetItem(['Meat'])
        qtLegumeItem = QtWidgets.QTreeWidgetItem(['Vegetable'])
        qtAlwaysAvailableItem = QtWidgets.QTreeWidgetItem(['Always available - to check'])

        # ----->> Init Ui Elements
        self.qtGroceriesTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Ingredients :']))
        qtSpecialItem.setIcon(0, self.ui['icons']['warning'])
        qtMeatItem.setIcon(0, self.ui['icons']['meat'])
        qtLegumeItem.setIcon(0, self.ui['icons']['vegetable'])
        qtAlwaysAvailableItem.setIcon(0, self.ui['icons']['ok'])
        topLevel = [qtSpecialItem, qtMeatItem, qtLegumeItem, QtWidgets.QTreeWidgetItem(['Other']),
                    qtAlwaysAvailableItem]
        self.qtGroceriesTree.addTopLevelItems(topLevel)
        self.qtGroceriesTree.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Expanding)

        # ----->> Set Layout
        self.qtLabelGroceriesList = QtWidgets.QLabel('Grocery List')
        self.layout.addWidget(self.qtLabelGroceriesList)
        self.layout.addWidget(self.qtGroceriesTree)


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
        self.qtBeforeRecipeText = QtWidgets.QTextEdit()
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
        self.qtIngredients.setHeaderItem(QtWidgets.QTreeWidgetItem(['Ingredients']))
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
        self.qtRatingRadio0.setChecked(False)
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

