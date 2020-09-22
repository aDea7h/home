import hou
sl = hou.selectedNodes()
for n in sl:
    colorr = n.parm('colorr')
    colorg = n.parm('colorg')
    colorb = n.parm('colorb')
    if None in [colorr, colorg, colorb]:
        continue
    n.setColor(hou.Color(colorr.eval(), colorg.eval(), colorb.eval()))