import hou

# TODO Exporter
#  reset connexion on creation, update connexions
#  open folder and render stats
#  comments
#  read autoRange from files


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
