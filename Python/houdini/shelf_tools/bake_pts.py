import hou

def bake():
    node = hou.selectedNodes()
    if node != ():
        node = node[0]
        position = node.position()
        geo = node.geometry()
        ptList = geo.points()

        addNode = node.parent().createNode('add', 'Bake_Points_{}'.format(node.name()))
        addNode.setPosition(position+hou.Vector2([1.5, 0]))

        parms = {'points':len(ptList)}
        addNode.setParms(parms)
        parms = {}
        idx = 0
        print(parms)
        for pt in ptList:
            pos = pt.attribValue('P')
            parms['usept{}'.format(idx)] = True
            parms['pt{}x'.format(idx)] = pos[0]
            parms['pt{}y'.format(idx)] = pos[1]
            parms['pt{}z'.format(idx)] = pos[2]
            idx += 1
            print(idx, pos, 'pt{}x'.format(idx), pos)

        addNode.setParms(parms)

if __name__ == '__main__':
    bake()