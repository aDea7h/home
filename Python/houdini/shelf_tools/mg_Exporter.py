import sys
path = '/u/dsuarez/Documents/scripts/'
if not path in sys.path:
    sys.path.append(path)
import exporter
exp = exporter.Exporter()
exp.create_exporter()

#overrides
ropOv = {
'folder_path':'`mglpath()`/export/`chs("file_type")`/$HIPNAME-`chs("export_name")`/',
}
sopOv = {
'folder_path':'`mglpath()`/export/`chs("file_type")`/$HIPNAME-`chs("export_name")`/',
}
exp.sop_exporter_node.setParms(sopOv)
exp.rop_exporter_node.setParms(ropOv)