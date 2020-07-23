from PySide2 import QtGui, QtCore, QtWidgets
import hou
import os
from time import strptime

import File
import FileVersionning
import tools
reload(FileVersionning)
reload(File)
reload(tools)

# TODO hou.putenv doesnt set $JOB on console yes but not this tool WTF ??
# TODO Set proj on untitled.hip ?
# Todo on load projman doesn't actualize with current file !!



# class ProjectManagerUi(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         super(ProjectManagerUi, self).__init__()


class ProjectManager(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ProjectManager, self).__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.proj_name = None
        self.proj_path = None
        self.site_path = None
        self.proj_list = None

        self.style = {
            'bg_valid': (50, 200, 50),
            'bg_warning': (200, 50, 50),
            'bg_item_folder': (50, 75, 50),
            'bg_item_version': (73, 73, 73),
        }

        self.cprint = tools.CustomPrint(0, 0)

        font_title = QtGui.QFont()
        font_title.setPointSize(250)
        font_title.setBold(True)
        self.ui_proj_name = QtWidgets.QComboBox()
        self.layout.addWidget(self.ui_proj_name)
        # self.proj_name.setScaledContents(True)
        self.ui_proj_name.setMinimumHeight(50)
        self.ui_proj_name.setFont(font_title)

        self.set_proj_button = QtWidgets.QPushButton('Set Project')
        self.layout.addWidget(self.set_proj_button)

        self.ui_proj_path = QtWidgets.QLabel('')
        self.layout.addWidget(self.ui_proj_path)

        self.main_tabs = QtWidgets.QTabWidget()
        self.layout.addWidget(self.main_tabs)

        # Load Tab
        self.load_widget = QtWidgets.QWidget()
        self.load_tab = self.main_tabs.addTab(self.load_widget, 'Load')
        self.loadtab_layout = QtWidgets.QGridLayout()
        self.load_widget.setLayout(self.loadtab_layout)

        # Load Widget
        self.versions_tree = QtWidgets.QTreeWidget()
        self.versions_tree.setColumnCount(3)
        # self.versions_tree.setColumnWidth(1, 50)
        # self.versions_tree.setColumnWidth(2, 200)
        self.versions_tree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Name', 'Version', 'Flags']))
        self.versions_tree.expandAll()
        self.loadtab_layout.addWidget(self.versions_tree)

        # Publish Tab
        self.publish_widget = QtWidgets.QWidget()
        self.publish_tab = self.main_tabs.addTab(self.publish_widget, 'Publish')
        self.publishtab_layout = QtWidgets.QGridLayout()
        self.publish_widget.setLayout(self.publishtab_layout)

        # Publish Widget
        self.comment_group = QtWidgets.QGroupBox('Comment')
        self.publishtab_layout.addWidget(self.comment_group)
        self.comment_group_layout = QtWidgets.QVBoxLayout()
        self.comment_group.setLayout(self.comment_group_layout)
        self.comment_text = QtWidgets.QTextEdit()
        self.comment_group_layout.addWidget(self.comment_text)
        self.todo_text = QtWidgets.QTextEdit()
        self.todo_text.setPlaceholderText('TODO')
        self.comment_group_layout.addWidget(self.todo_text)
        self.done_text = QtWidgets.QTextEdit()
        self.done_text.setPlaceholderText('Done')
        self.comment_group_layout.addWidget(self.done_text)

        self.publishtab_layout.addWidget(QtWidgets.QLabel('Version'))
        self.version_text = QtWidgets.QTextEdit()
        self.publishtab_layout.addWidget(self.version_text)
        self.publishtab_layout.addWidget(QtWidgets.QLabel('Flags'))
        self.flags_text = QtWidgets.QTextEdit()
        self.publishtab_layout.addWidget(self.flags_text)
        self.publish_button = QtWidgets.QPushButton('Publish')
        self.publishtab_layout.addWidget(self.publish_button)

        # populate Ui
        self.hou_env_check()
        self.fill_projects()
        auto_setup = self.hou_env_in_ui()
        if auto_setup is True:
            self.get_project_files()

        # set connections
        self.set_connections()

    def hou_env_check(self):
        self.proj_path = hou.getenv('JOB')
        self.site_path = hou.getenv('HSITE')
        if os.path.exists(self.site_path) is False:
            raise Exception("HSITE path doesn't exists : {}".format(self.site_path))
        if os.path.exists(self.proj_path) is False:
            hou.putenv('job', self.site_path)
            self.proj_path = self.site_path

        if self.proj_path.startswith("C:"):
            self.proj_name = None  # TODO Overwrite $JOB ??
        else:
            self.proj_name = os.path.basename(self.proj_path)

        proj_list = os.listdir(self.site_path)
        filter = ['Substance Designer']
        for i in proj_list:
            if i in filter:
                proj_list.remove(i)
        self.proj_list = proj_list

    def fill_projects(self):
        self.ui_proj_name.clear()
        self.ui_proj_name.addItems(self.proj_list)

    def hou_env_in_ui(self):
        self.ui_proj_path.setText(self.proj_path)
        if self.proj_name is None:
            self.set_style_sheet_custom(self.ui_proj_path, self.style['bg_warning'])
            return False
        elif self.proj_name in self.proj_list and self.proj_path.startswith(self.site_path):
            self.set_style_sheet_custom(self.ui_proj_path, self.style['bg_valid'])
            return True
        else:
            self.set_style_sheet_custom(self.ui_proj_path, self.style['bg_warning'])
            return False

    def action_set_project(self):
        path = os.path.join(self.site_path, self.ui_proj_name.currentText())
        if os.path.exists(path) is False:
            raise Exception('Error while setting project to {}'.format(path))
        self.proj_path = path
        self.proj_name = os.path.basename(self.proj_path)
        hou.putenv('job', path)
        self.hou_env_in_ui()
        self.get_project_files()

    def get_project_files(self):
        # load tab
        files_tree = self.list_project_versions()
        files_tree = self.rebuild_tree(files_tree)
        self.set_files_in_ui(files_tree)

        # publish tab
        self.retrieve_last_comment()

    def set_connections(self):
        self.publish_button.clicked.connect(self.action_publish)
        self.set_proj_button.clicked.connect(self.action_set_project)

    def set_style_sheet_custom(self, qt_object, bg_color=None, color=None):
        sheet = ''
        if bg_color is not None:
            sheet += 'background-color: rgb' + str(bg_color) + ';'
        if color is not None:
            sheet += 'color: rgb' + str(color) + ';'
        qt_object.setStyleSheet(sheet)

    def set_color(self, qt_item, color, column=None):
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor(color[0], color[1], color[2]))
        if column == None:
            qt_item.setForeground(brush)
        else:
            qt_item.setForeground(column, brush)

    def set_item_background(self, qt_item, bg_color, column=None):
        qt_item.setBackgroundColor(column, QtGui.QColor(bg_color[0], bg_color[1], bg_color[2]))

    def create_version(self):

        full_path = hou.hipFile.path()
        name = hou.hipFile.basename()
        path = full_path[:-len(name)]

        attrs = {
            'date_versionning': True,
            'version': self.version_text.toPlainText(),
            'comment': self.comment_text.toPlainText(),
            'todo': self.todo_text.toPlainText(),
            'done': self.done_text.toPlainText(),
            'flags': self.flags_text.toPlainText(),
        }

        version = FileVersionning.Version(path, name, attrs)
        return version

    def action_publish(self):
        hou.hipFile.save(None, False)
        version = self.create_version()
        version.do_publish()

    def list_project_versions(self):
        cfg = {
            'limit_recursion': True,
            'file_tree_is_nested': True,
            'max_recursion': 4,
            'filter_files': True,
            'filter_type': ['houdini'],
        }
        files_tree_class = File.RecursiveWalk(self.proj_path, cfg)
        files_tree = files_tree_class.return_tree()
        return files_tree

    def rebuild_tree(self, files_tree):  # TODO
        def get_backup_scene_name(scene_obj):
            return scene_obj.name.split('_bak')[0] + scene_obj.extension

        def get_publish_scene_name(scene_obj):

            def is_time(str_parse):
                time_format = "%Y.%m.%d-%H.%M.%S"
                try:
                    time = strptime(str_parse, time_format)
                except:
                    return False
                else:
                    return True

            parent = scene_obj.name
            if ' - ' in scene_obj.name:
                parent = scene_obj.name.split(' - ')
                if is_time(parent[0]) is True:
                    parent = parent[1:]
                else:
                    parent = scene_obj.name
                self.cprint((scene_obj.name, parent), 1)
            return parent

        def recursive_tree(files_tree, main_scenes, type):
            new_tree = {}
            self.entries = []
            for key in files_tree:
                # type = None
                if isinstance(files_tree[key], dict) is True:  # folder
                    if key == 'backup':
                        type = 'backup'
                    elif key == '_Publish':
                        type = 'publish'
                    # else:
                    #     type = None

                    if type is None:
                        new_tree[key] = recursive_tree(files_tree[key], main_scenes, None)
                    else:
                        pass

                        # ####
                        # continue
                        # ####


                        # subscene : backup or publish parent it
                        # process folders after hip files
                        new_tree[key] = recursive_tree(files_tree[key], main_scenes, type)
                else:  # file
                    scene_obj = files_tree[key]

                    # set parent_scene
                    self.cprint((scene_obj.name, type, scene_obj.path), 0)
                    if type is None:
                        scene_obj.parent_scene = scene_obj.name
                    elif type is 'backup':
                        scene_obj.parent_scene = get_backup_scene_name(scene_obj)
                    else:  # type is 'publish'
                        scene_obj.parent_scene = get_publish_scene_name(scene_obj)

                    if scene_obj.parent_scene not in new_tree:
                        new_tree[scene_obj.parent_scene] = {}
                    if type is None:
                        new_tree[scene_obj.parent_scene] = scene_obj
                    else:
                        if type is 'backup':
                            if 'backup' not in new_tree[scene_obj.parent_scene]:
                                new_tree[scene_obj.parent_scene]['backup'] = {}
                            new_tree[scene_obj.parent_scene]['backup'][scene_obj.name] = scene_obj
                        else:
                            if '_Publish' not in new_tree[scene_obj.parent_scene]:
                                new_tree[scene_obj.parent_scene]['_Publish'] = {}
                            new_tree[scene_obj.parent_scene]['_Publish'][scene_obj.name] = scene_obj

            return new_tree
        # self.cprint(files_tree, 0, 'Orig')
        new_tree = recursive_tree(files_tree, [], None)
        # self.cprint(new_tree,0, 'New')
        return new_tree

    def set_files_in_ui(self, files_tree):
        def recursive_add(dic, parent_item):
            tops = []
            for obj in dic:
                if isinstance(dic[obj], dict) is True:
                    entry = [obj, '', '']
                    new_item = QtWidgets.QTreeWidgetItem(parent_item, entry)
                    self.set_item_background(new_item, self.style['bg_item_folder'], 1)
                    recursive_add(dic[obj], new_item)
                    tops.append(new_item)
                else:
                    file_obj = dic[obj]
                    entry = [file_obj.name, file_obj.path, '']
                    new_item = QtWidgets.QTreeWidgetItem(parent_item, entry)
                    self.set_item_background(new_item, self.style['bg_item_version'], 1)
                    tops.append(new_item)
            return tops

        self.versions_tree.clear()
        tops = recursive_add(files_tree, None)
        self.versions_tree.addTopLevelItems(tops)
        self.versions_tree.expandAll()

    def retrieve_last_comment(self):
        version = self.create_version()
        self.cprint((version.path, version.publish_folder, version.comments_file), 1)
        version.get_version_from_log()

        self.cprint((version.comment, version.todo, version.done, version.version), 1)

        self.comment_text.setText(version.comment)
        self.todo_text.setText(version.todo)
        self.done_text.setText(version.done)
        self.version_text.setText(version.version)


def main(parent=None):
    ui = ProjectManager(parent)
    return ui
