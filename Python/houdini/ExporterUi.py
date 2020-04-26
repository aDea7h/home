#import hou
import os
# from PySide2 import QtCore, QtGui, QtUiTools, QtWidgets
from PySide import QtCore, QtGui, QtUiTools
import sys
import math
from datetime import datetime as datetime

# TODO General
#  split file houdini sop rop exporter / file processing and ui

# TODO Exporter
#  reset connexion on creation, update connexions
#  open folder and render stats
#  comments
#  read autoRange from files


# TODO FileObj
#  test validity by weight

# TODO ExportFile
# compute process time : time n - time n-1
# graph time and weight and rendertime
# Correction of datetime bug on time diff
# Todo how to display extra files (keep in recap)

# TODO ExportFilUi
# set a tab ui to manage multi file sequence

class Exporter:
    def __init__(self):
        selected_node = hou.selectedNodes()
        if len(selected_node) != 1:
            raise Exception("Select only one node")

        self.selection = selected_node[0]
        if hou.nodeType(self.selection.path()).name() != 'null':  # subnet if hda selected
            raise Exception("select a Null node")

        if self.selection.name().startswith('OUT_') is False or len(self.selection.name()) < 5:
            raise Exception("node should be prefixed with OUT_")

        self.sop_hda_name = 'Export' + self.selection.name()[3:]
        # print(self.sop_hda_name)
        self.rop_hda = hou.node('/out/' + self.sop_hda_name)
        if self.rop_hda is not None:
            raise Exception('ROP already exists')
        self.parent = self.selection.parent()
        self.sop_exporter_node = None
        self.rop_exporter_node = None
        self.out_node = self.selection
        self.out_node_cxion = self.out_node.outputs()
        self.cache_node = None

    def create_exporter(self):
        self.create_sop_exporter()
        self.create_rop_exporter()
        self.set_sop_attribute()
        self.set_rop_attributes()

    def create_sop_exporter(self):
        # process out node
        self.out_node.setColor(hou.Color((0.9, 0.4, 0)))
        self.out_node.setUserData('nodeshape', 'bulge')

        # create exporter hda
        self.sop_exporter_node = self.parent.createNode('exporter', self.sop_hda_name)
        self.sop_exporter_node.setPosition(self.out_node.position() + hou.Vector2([0, -1.3]))
        self.sop_exporter_node.setInput(0, self.out_node)
        self.sop_exporter_node.setColor(hou.Color((0, 0, 0)))

        # process cache node
        self.cache_node = hou.node(self.out_node.name().replace('OUT_', 'CACHE_'))
        if self.cache_node is None:
            self.cache_node = self.parent.createNode('null', self.out_node.name().replace('OUT_', 'CACHE_'))
            self.cache_node.setPosition(self.sop_exporter_node.position() + hou.Vector2([0, -1.3]))
            self.cache_node.setInput(0, self.sop_exporter_node)
            self.out_node_connexion_transfer()
        else:
            if self.cache_node.inputs in [(self.out_node,), ()]:
                self.cache_node.setInput(0, self.sop_exporter_node)
                self.out_node_connexion_transfer()
            else:
                pass  # node has been connected to another node, skip
        self.cache_node.setColor(hou.Color((0.9, 0.4, 0)))
        self.cache_node.setUserData('nodeshape', 'bulge_down')

    def create_rop_exporter(self):
        out_node = hou.node('/out')
        self.rop_exporter_node = out_node.createNode('rop_exporter', self.sop_hda_name)
        self.rop_exporter_node.setColor(hou.Color((0, 0, 0)))

    def set_sop_attribute(self):
        self.sop_exporter_node.setParms({'rop_exporter': self.rop_exporter_node.path(),
                                         'export_name': "`chs(chs('rop_exporter')/export_name)`"})

    def set_rop_attributes(self):
        export_name = self.sop_exporter_node.name()
        if export_name.startswith('Export') is True:
            export_name = export_name[7:]
        self.rop_exporter_node.setParms({'sop_exporter': self.sop_exporter_node.path(),
                                         'export_name': export_name})

    def out_node_connexion_transfer(self):  # TODO add each cxion from OUT_node
        for cxion in self.out_node_cxion:
            pass


class FileObj:
    def __init__(self, path, name=None, cfg= {}):
        extension_dic = {
            '.sc': ('.bgeo.sc', 'cache'),
            '.bgeo': ('.bgeo', 'cache'),
            '.vdb': ('.vdb', 'cache'),
            '.abc': ('.abc', 'cache'),
            '.exr': ('.exr', 'image'),
            '.jpg': ('.exr', 'image'),
            '': ('', 'folder'),
        }

        self.cfg = {
            'idx_separator': ".",
            'idx_pos': -1,
            'extension_dic': extension_dic,
        }
        self.cfg.update(cfg)

        if name is None:
            self.path = os.path.dirname(path)
            self.name = os.path.basename(path)
        else:
            self.path = path
            self.name = name
        self.type = None
        self.extension = None
        self.exists = None

        self.size = None
        self.time = None
        self.idx = None
        self.is_valid = None

        self.get_extension(self.cfg['extension_dic'])
        self.check_existence()
        if self.exists is True:
            self.get_file_infos()

        self.get_index(self.cfg['idx_separator'], self.cfg['idx_pos'])
        self.check_validity()

    def get_extension(self, extension_dic):
        base_name, os_ext = os.path.splitext('{0}/{1}'.format(self.path, self.name))
        if os_ext in extension_dic.keys():
            self.extension = extension_dic[os_ext][0]
            self.type = extension_dic[os_ext][1]
        else:
            self.extension = os_ext
            self.type = "unknown"

    def check_existence(self):
        self.exists = os.path.exists(os.path.join(self.path, self.name))
        if self.exists is False:  # Flag as invalid if folder doesn't exists
            self.is_valid = os.path.exists(self.path)

    def get_file_infos(self):
        self.time = os.path.getmtime(os.path.join(self.path, self.name))
        self.size = os.path.getsize(os.path.join(self.path, self.name))

    def get_index(self, idx_separator, idx_pos):
        base_name = self.name[:-len(self.extension)]
        if idx_separator in base_name:
            self.idx = int(base_name.split(idx_separator)[idx_pos])
        else:
            self.idx = False

    def check_validity(self):
        if self.is_valid is False:
            return
        # TODO Test weight
        self.is_valid = True


class FileUi(QtGui.QWidget):
    def __init__(self, file_obj, bg_color):
        super(FileUi, self).__init__()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        # self.setMinimumSize(50, 50)
        # self.setFixedSize(QtCore.QSize(20, 20))
        self.layout.setSpacing(0)
        self.layout.setRowStretch(0, 0)
        self.button = QtGui.QPushButton()
        self.layout.addWidget(self.button)

        all_keys = ['name', 'size', 'time', 'render_time', 'exists', 'is_valid']
        switch_display = {x: x for x in all_keys}
        switch_display.update({'time': 'date', 'render_time': 'render time', "is_valid": 'is valid'})
        description = []
        if file_obj is None:
            description = ['{} : NA'.format(switch_display[x]) for x in all_keys]
        else:
            for key in all_keys:
                if key in file_obj.__dict__.keys():
                    if eval('file_obj.'+key) is None:
                        description.append('{} : NA'.format(switch_display[key]))
                    else:
                        description.append('{} : {}'.format(switch_display[key], eval('file_obj.'+key)))
        self.setToolTip('\n'.join(description))
        bg_color = '{}, {}, {}'.format(bg_color[0]*255, bg_color[1]*255, bg_color[2]*255)
        self.setStyleSheet("background-color: rgb({}); border: 1px solid black;".format(bg_color))


class ExportFileUi(QtGui.QMainWindow):
    def __init__(self):
        super(ExportFileUi, self).__init__()

        self.setWindowTitle('Check Files')
        self.setGeometry(250, 500, 700, 400)
        self.color_invalid = (1.0, 0, 0)
        self.color_inexistant = (0, 0, 0, 0)
        # self.bg_1 = (46, 46, 46)
        # self.bg_2 = (30, 30, 30)
        self.color_ramp = [(0.0, 0.5, 0.0), (0.004999999888241291, 0.4950000047683716, 0.0),
                           (0.009999999776482582, 0.49000000953674316, 0.0),
                           (0.014999999664723873, 0.48500001430511475, 0.0),
                           (0.019999999552965164, 0.47999998927116394, 0.0),
                           (0.02500000037252903, 0.4749999940395355, 0.0),
                           (0.029999999329447746, 0.4699999988079071, 0.0),
                           (0.03500000014901161, 0.4650000035762787, 0.0),
                           (0.03999999910593033, 0.46000000834465027, 0.0),
                           (0.04500000178813934, 0.45499998331069946, 0.0),
                           (0.05000000074505806, 0.44999998807907104, 0.0),
                           (0.054999999701976776, 0.4449999928474426, 0.0),
                           (0.05999999865889549, 0.4399999976158142, 0.0),
                           (0.06499999761581421, 0.4350000023841858, 0.0),
                           (0.07000000029802322, 0.4300000071525574, 0.0),
                           (0.07500000298023224, 0.42500001192092896, 0.0),
                           (0.07999999821186066, 0.42000001668930054, 0.0),
                           (0.08500000089406967, 0.41499999165534973, 0.0),
                           (0.09000000357627869, 0.4099999964237213, 0.0),
                           (0.0949999988079071, 0.4050000011920929, 0.0),
                           (0.10000000149011612, 0.4000000059604645, 0.0),
                           (0.10499999672174454, 0.39500001072883606, 0.0),
                           (0.10999999940395355, 0.38999998569488525, 0.0),
                           (0.11500000208616257, 0.38499999046325684, 0.0),
                           (0.11999999731779099, 0.3799999952316284, 0.0), (0.125, 0.375, 0.0),
                           (0.12999999523162842, 0.3700000047683716, 0.0),
                           (0.13500000536441803, 0.36500000953674316, 0.0),
                           (0.14000000059604645, 0.36000001430511475, 0.0),
                           (0.14499999582767487, 0.35500001907348633, 0.0),
                           (0.15000000596046448, 0.3499999940395355, 0.0),
                           (0.1550000011920929, 0.3449999988079071, 0.0),
                           (0.1599999964237213, 0.3400000035762787, 0.0),
                           (0.16500000655651093, 0.3349999785423279, 0.0),
                           (0.17000000178813934, 0.32999998331069946, 0.0),
                           (0.17499999701976776, 0.32499998807907104, 0.0),
                           (0.18000000715255737, 0.3199999928474426, 0.0),
                           (0.1850000023841858, 0.3149999976158142, 0.0),
                           (0.1899999976158142, 0.3100000023841858, 0.0),
                           (0.19499999284744263, 0.3050000071525574, 0.0),
                           (0.20000000298023224, 0.30000001192092896, 0.0),
                           (0.20499999821186066, 0.29500001668930054, 0.0),
                           (0.20999999344348907, 0.2900000214576721, 0.0),
                           (0.2150000035762787, 0.2849999964237213, 0.0),
                           (0.2199999988079071, 0.2800000011920929, 0.0),
                           (0.22499999403953552, 0.2750000059604645, 0.0),
                           (0.23000000417232513, 0.26999998092651367, 0.0),
                           (0.23499999940395355, 0.26499998569488525, 0.0),
                           (0.23999999463558197, 0.25999999046325684, 0.0),
                           (0.24500000476837158, 0.2549999952316284, 0.0),
                           (0.25, 0.25, 0.0), (0.2549999952316284, 0.24500000476837158, 0.0),
                           (0.25999999046325684, 0.24000000953674316, 0.0),
                           (0.26499998569488525, 0.23500001430511475, 0.0),
                           (0.27000001072883606, 0.22999998927116394, 0.0),
                           (0.2750000059604645, 0.22499999403953552, 0.0),
                           (0.2800000011920929, 0.2199999988079071, 0.0), (0.2849999964237213, 0.2150000035762787, 0.0),
                           (0.28999999165534973, 0.21000000834465027, 0.0),
                           (0.29499998688697815, 0.20500001311302185, 0.0),
                           (0.30000001192092896, 0.19999998807907104, 0.0),
                           (0.3050000071525574, 0.19499999284744263, 0.0),
                           (0.3100000023841858, 0.1899999976158142, 0.0), (0.3149999976158142, 0.1850000023841858, 0.0),
                           (0.3199999928474426, 0.18000000715255737, 0.0),
                           (0.32499998807907104, 0.17500001192092896, 0.0),
                           (0.33000001311302185, 0.16999998688697815, 0.0),
                           (0.33500000834465027, 0.16499999165534973, 0.0),
                           (0.3400000035762787, 0.1599999964237213, 0.0), (0.3449999988079071, 0.1550000011920929, 0.0),
                           (0.3499999940395355, 0.15000000596046448, 0.0),
                           (0.35499998927116394, 0.14500001072883606, 0.0),
                           (0.36000001430511475, 0.13999998569488525, 0.0),
                           (0.36500000953674316, 0.13499999046325684, 0.0),
                           (0.3700000047683716, 0.12999999523162842, 0.0), (0.375, 0.125, 0.0),
                           (0.3799999952316284, 0.12000000476837158, 0.0),
                           (0.38499999046325684, 0.11500000953674316, 0.0),
                           (0.38999998569488525, 0.11000001430511475, 0.0),
                           (0.39500001072883606, 0.10499998927116394, 0.0),
                           (0.4000000059604645, 0.09999999403953552, 0.0),
                           (0.4050000011920929, 0.0949999988079071, 0.0),
                           (0.4099999964237213, 0.09000000357627869, 0.0),
                           (0.41499999165534973, 0.08500000834465027, 0.0),
                           (0.41999998688697815, 0.08000001311302185, 0.0),
                           (0.42500001192092896, 0.07499998807907104, 0.0),
                           (0.4300000071525574, 0.06999999284744263, 0.0),
                           (0.4350000023841858, 0.06499999761581421, 0.0),
                           (0.4399999976158142, 0.06000000238418579, 0.0),
                           (0.4449999928474426, 0.05500000715255737, 0.0),
                           (0.44999998807907104, 0.050000011920928955, 0.0),
                           (0.45500001311302185, 0.04499998688697815, 0.0),
                           (0.46000000834465027, 0.03999999165534973, 0.0),
                           (0.4650000035762787, 0.034999996423721313, 0.0),
                           (0.4699999988079071, 0.030000001192092896, 0.0),
                           (0.4749999940395355, 0.025000005960464478, 0.0),
                           (0.47999998927116394, 0.02000001072883606, 0.0),
                           (0.48500001430511475, 0.014999985694885254, 0.0),
                           (0.49000000953674316, 0.009999990463256836, 0.0),
                           (0.4950000047683716, 0.004999995231628418, 0.0),
                           (0.5, 0.0, 0.0)]

        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QtGui.QGridLayout()
        self.central_widget.setLayout(self.central_layout)
        # self.setStyleSheet("background-color: rgb{};".format(self.bg_1))

        self.seq_widget = QtGui.QWidget()
        self.seq_layout = QtGui.QGridLayout()
        self.seq_layout.setSpacing(0)
        self.seq_layout.setRowStretch(0, 0)
        self.seq_widget.setLayout(self.seq_layout)
        self.central_layout.addWidget(self.seq_widget)

        self.legend_widget = QtGui.QWidget()
        self.legend_layout = QtGui.QGridLayout()
        self.legend_widget.setLayout(self.legend_layout)
        self.central_layout.addWidget(self.legend_widget)

        self.refresh_button = QtGui.QPushButton('Refresh')
        self.legend_layout.addWidget(self.refresh_button, 0, 0)
        self.refresh_checkbox = QtGui.QCheckBox("Auto Refresh", checked=True)
        self.legend_layout.addWidget(self.refresh_checkbox, 0, 1)

    def setup_ui(self, file_obj_list, seq_val, file_type):
        i = 0
        j = 0
        idx = 0
        for obj in file_obj_list:
            if file_type == 'image':
                bg_color = self.get_bg_color(obj, 'render_time', seq_val['time'])
            else:
                bg_color = self.get_bg_color(obj, 'size', seq_val['size'])
            widget = FileUi(obj, bg_color)
            self.seq_layout.addWidget(widget, i, j)
            idx += 1
            i = int(idx/10)
            j = idx % 10

    def get_bg_color(self, obj, key, min_max):
        if obj is None or obj.exists is False:
            return self.color_inexistant
        if obj.is_valid is False:
            return self.color_invalid
        # calc reramp NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
        val = (((eval('obj.' + key) - min_max[0]) * 100) / (min_max[1] - min_max[0]) + 0)
        print(key, eval('obj.' + key), min_max, val)
        return self.color_ramp[int(val)]


class ExportFile:
    def __init__(self, export_path, file_type=None):
        assert os.path.isdir(export_path)
        self.export_path = export_path
        print('Path : {}'.format(self.export_path))

        self.extension_dic = {
            'sc': ('.bgeo.sc', 'cache'),
            'bgeo': ('.bgeo', 'cache'),
            'vdb': ('.vdb', 'cache'),
            'abc': ('.abc', 'cache'),
            'exr': ('.exr', 'image'),
            'jpg': ('.exr', 'image'),
            '': ('', 'folder'),
        }

        self.ui = ExportFileUi()
        self.file_type = file_type
        self.file_main_type = self.extension_dic[self.file_type]
        self.all_index_file = []
        self.seq_val = {
            'time': [None, None],
            'size': [None, None, None],
            'idx': [None, None],
            'render_time': [None, None, None],
        }

        self.list_files()
        print('--->> Data processed, Generating Ui')
        self.ui.setup_ui(self.all_index_file, self.seq_val, self.file_main_type)

    def list_files(self):
        files = os.listdir(self.export_path)
        file_obj_list, valid_list = ([], [])
        times, sizes, idxs = ([], [], [])
        for file_name in files:
            if self.file_type is not None and file_name.endswith(self.file_type) is False:
                # Todo how to display extra files (keep in recap)
                continue
            file_obj = FileObj(self.export_path, file_name)
            file_obj_list.append(file_obj)
            if file_obj.is_valid is True:
                valid_list.append(file_obj)
            if self.seq_val['time'][0] is None:
                self.seq_val['time'][0] = file_obj.time
                self.seq_val['time'][1] = file_obj.time
                self.seq_val['size'][0] = file_obj.size
                self.seq_val['size'][1] = file_obj.size
                self.seq_val['idx'][0] = file_obj.idx
                self.seq_val['idx'][1] = file_obj.idx
                continue
            if file_obj.time is not None:
                times.append(file_obj.time)
                self.seq_val['time'][0] = min(self.seq_val['time'][0], file_obj.time)
                self.seq_val['time'][1] = max(self.seq_val['time'][1], file_obj.time)
            if file_obj.size is not None:
                sizes.append(file_obj.size)
                self.seq_val['size'][0] = min(self.seq_val['size'][0], file_obj.size)
                self.seq_val['size'][1] = max(self.seq_val['size'][1], file_obj.size)
            if file_obj.idx not in [None, False]:
                idxs.append(file_obj.idx)
                self.seq_val['idx'][0] = min(self.seq_val['idx'][0], file_obj.idx)
                self.seq_val['idx'][1] = max(self.seq_val['idx'][1], file_obj.idx)

        print('--->> Seq Values : {}'.format(self.seq_val))
        if sizes != []:
                self.seq_val['size'][2] = self.calc_median(sizes)
                print('--->> Median Weight : {}'.format(self.display_size(self.seq_val['size'][2])))
        if idxs != []:
            missing = self.get_sequence_by_idx(idxs, file_obj_list)
            print('--->> Missing Frames : {}'.format(', '.join(str(x) for x in missing)))
            self.calc_render_time()

        print('--->> Seq Values : {}'.format(self.seq_val))


    def calc_median(self, sizes):
        sizes = sorted(sizes)
        return sizes[int(len(sizes)/2)]

    def display_size(self, size):
        if size == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size, 1024)))
        p = math.pow(1024, i)
        s = round(size / p, 2)
        return "%s %s" % (s, size_name[i])

    def display_time(self, render_time):
        print(render_time)
        d1 = datetime.fromtimestamp(render_time)
        return d1.strftime('%H:%M:%S')

    def get_sequence_by_idx(self, idxs, file_obj_list):
        idxs = sorted(idxs)
        i = idxs[0]

        missing = []
        while i < idxs[-1]:
            if i not in idxs:
                missing.append(i)
                self.all_index_file.append(None)
            else:
                self.all_index_file.append(file_obj_list[idxs.index(i)])
            i += 1
        return missing

    def calc_render_time(self):
        render_times = []
        for i in self.all_index_file:
            if i is None or isinstance(i, FileObj) is False:
                continue
            prev = self.all_index_file.index(i)-1
            if prev < 0:
                continue
            prev = self.all_index_file[prev]
            if prev is None:
                i.render_time = None
            else:
                # TODO Bug in render time adds 1 hour
                i.render_time = i.time - prev.time
                render_times.append(i.render_time)
                if self.seq_val['render_time'][0] is None:
                    self.seq_val['render_time'][0] = i.render_time
                    self.seq_val['render_time'][1] = i.render_time
                    continue
                self.seq_val['render_time'][0] = min(self.seq_val['render_time'][0], i.render_time)
                self.seq_val['render_time'][1] = max(self.seq_val['render_time'][1], i.render_time)

        self.seq_val['render_time'][2] = self.calc_median(render_times)


def palette():
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtGui.QColor(127, 127, 127))
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(42, 42, 42))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(66, 66, 66))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 0, 0))
    dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(127, 127, 127))
    dark_palette.setColor(QtGui.QPalette.Dark, QtGui.QColor(35, 35, 35))
    dark_palette.setColor(QtGui.QPalette.Shadow, QtGui.QColor(20, 20, 20))

    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 255, 53))

    dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtGui.QColor(127, 127, 127))
    dark_palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    # dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, QtGui.QColor(80, 80, 80))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText, QtGui.QColor(127, 127, 127))
    return dark_palette


def launch_ui():
    app = QtGui.QApplication(sys.argv)

    # app.setStyle(QtGui.QStyleFactory.create("Fusion"))
    dark_palette = palette()
    app.setPalette(dark_palette)

    main_window = ExportFile(path, file_type)
    # main_window = ExportFileUi()
    print(main_window)
    main_window.ui.show()
    app.exec_()

if __name__ == "__main__":
    ui = True
    file_type = 'exr'
    path = "F:/Work/Tuto - Applied Houdini Volumetrics/geo/Sim_Volumetric_2/001-000"
    path = "D:/Desktop/test/render/Volumetrics 2.2/v001"
    if ui is True:
        launch_ui()
    else:
        main_window = ExportFile(path, file_type)


"""
# Open Folder Button script
import os,platform,subprocess;path=os.path.dirname(hou.pwd().parm('sopoutput').eval(
));os.startfile(path) if platform.system()=='Windows' else subprocess.check_call(['open', path])
"""

"""
# Check Files Button script 
import sys,os;sys.path.append("E:Scripts/Python/houdini");import exporter;reload(exporter);
exporter.ExportFile(os.path.dirname(hou.pwd().parm('sopoutput').eval()))
"""

"""
# call script from houdini ?
cmd3 = 'python -c "import sys;sys.path.append(\\"E:/Scripts/Python/houdini\\");import exporter;exporter.launch()"'
cmd3 = 'python -i -c "import sys;sys.path.append(\\"E:/Scripts/Python/houdini\\");import exporter;exporter.launch()"'
subprocess.call(cmd3, shell=True)
"""
