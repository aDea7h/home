def reorderAssetsByTypes(nodePath, colorNode=True, alignNode=True):
    node = hou.pwd()
    
    def getNaskCasting():
        path = "E:/WIP/Work/casting-nask.csv"

        file = open(path, "r")
        fileText = file.readlines()
        file.close()
        fileText.pop(0)

        assetDic = {}

        for line in fileText:
            assetType = line.split(",")
            assetName = assetType[2]
            assetType = assetType[1].split("/")[0]
            assetDic[assetName] = assetType.lower()

        return assetDic
    
    assetList = getNaskCasting()
    colorList = {"sets":(0, 0.4, 1), "chars":(0.4, 1, 0.4), "props":(0.6, 0.4, 1)}
    assetTypeList = {"sets":[], "props":[], "chars":[]}
    
    nodeChildren = hou.node(nodePath).children()
    
    #colorize nodes by asset type
    for child in list(nodeChildren):
        if str(child) in assetList.keys():
            type = assetList[str(child)]
            if colorNode == True:
                child.setColor(hou.Color(colorList[type]))
            assetTypeList[type].append(child)
    
    #reorder nodes layout by asset type
    if alignNode == True:
        u = 0
        v = 0
        for type in sorted(assetTypeList.keys()):
            v = 0
            for asset in sorted(assetTypeList[type]):
                pos = hou.Vector2 (u,v)
                asset.setPosition(pos)
                v -= 1
            u -= 3

reorderAssetsByTypes("/obj/geo1")
