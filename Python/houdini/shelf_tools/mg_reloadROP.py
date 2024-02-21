
import hou

def listChildren():
    keep = []
    children = hou.node('/out').children()
    for c in children:
        if 'mg_universalExporterOut' in str(c.type()):
            keep.append(c)
    return keep

ls = hou.selectedNodes()
if len(ls) == 0:
    ls = listChildren()
    
for rop in ls:
    sop = rop.parm('sop').eval()
    sop = hou.node(sop)
    sop.parm('reload').pressButton()