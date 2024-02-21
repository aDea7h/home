import hou
node = hou.selectedNodes()
if node != ():
    node = node[0]
    position = node.position()
    bbox = node.geometry().boundingBox()
    print(bbox)
    
    size = [bbox.sizevec()[0], bbox.sizevec()[1], bbox.sizevec()[2]]
    center = [bbox.center()[0], bbox.center()[1], bbox.center()[2]]
    
    newNode = node.parent().createNode("box", "Bound_{}".format(node.name()))
    newNode.setParms({'sizex':size[0], 'sizey':size[1],'sizez':size[2],'tx':center[0],'ty':center[1],'tz':center[2]})# 'center':bbox.center()})
    newNode.setPosition(position+hou.Vector2([1.5, 0]))