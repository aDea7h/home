""" Houdini script ui launcher
import sys;
sys.path.append("/u/pets2/Users/dsuarez/Sandbox/Labo/scripts/")
import grassSetup
reload(grassSetup)

class GrassUi():
    def __init__(self, parent=None):
        self.ui = grassSetup.GrassSetupUi()
        self.ui.show()

ui = GrassUi()
"""

import hou
from pprint import pprint as pprint
def houGetLinkedUpNode():
	selectedNodes = hou.selectedNodes()
	for selectedNode in selectedNodes:
		inputNodes = selectedNode.inputs()
		for node in inputNodes:
			node.setSelected(True)

def exportSelectedGeom(mgExporter=True):
	selectedNodes = hou.selectedNodes()
	exportList = []
	for selectedNode in selectedNodes:
		childrenList = selectedNode.children()
		for child in childrenList:
			if child.name().startswith("EXPORT_") is True:
				if mgExporter is True:
					outNodes = hou.node("/out").children()
					for outNode in outNodes:
						if child.name() == outNode.name():
							exportList.append(child)
				else:
					exportList.append(child)

	idx = 0
	for export in exportList:
		print("------------>>> Processing : "+"/".join([str(idx), str(len(exportList))])+" - "+export.name())
        export.parm("render").pressButton()
        idx += 1

def refreshToManualOrAutoSwitch():
	mode = hou.updateModeSetting().name()
	if mode == 'AutoUpdate':
	    hou.setUpdateMode(hou.updateMode.Manual)
	if mode == 'Manual':
	    hou.setUpdateMode(hou.updateMode.AutoUpdate)	

def exportFromGroup(searchedString=None, regroup=True, byUniqueActor=True, verbose=2):
	if searchedString is None:
		result, searchedString = hou.ui.readInput("type Actor or LIB name", buttons=["OK", "Cancel"], close_choice=1, title="Extract Objects by Name")
		if result == 1:
			return()
	selectedNodes = hou.selectedNodes()
	print("-->> exportFromGroup START")
	hou.setUpdateMode(hou.updateMode.AutoUpdate)
	print("-->> Extracting Name : "+searchedString)
	noMatch = True
	for node in selectedNodes:
		print("Processing Node : "+node.name())
		if node.name().endswith(".abc") is True:
			node = node.children()[0]
		if node.name().endswith(".abc_cache") is True:
			try:
				node.setParms({"loadmode":"houdini", "groupnames":4})
			except:
				try:
					node.setParms({"loadmode":"houdini", "groupnames":2})
				except:
					pass
		parentNode = node.parent()
		parentName = parentNode.name().split("_BDD_")[0]
		keptGroup = {}
		groupList = node.geometry().primGroups()
		for group in groupList:
			if searchedString.lower() in group.name().lower():
				if byUniqueActor is True:
					actorName = group.name().split("_FULL_BDD_")
					libName = actorName[-1].split("_")
					try:
						int(libName[1])
					except ValueError:
						libName = libName[0]
						# libName = actorName[0]+"_FULL_BDD_"+libName[0]
						if libName not in keptGroup.keys():
							keptGroup[libName] = [libName, []]
						else:
							keptGroup[libName][0] = libName
					else:
						# fullNameSpace = actorName[0]+"_FULL_BDD_"+"_".join(libName[0:2])
						# libName = actorName[0]+"_FULL_BDD_"+libName[0]
						fullNameSpace = "_".join(libName[0:2])
						libName = libName[0]
						if fullNameSpace not in keptGroup.keys():
							if libName not in keptGroup.keys():
								keptGroup[libName] = [None, [fullNameSpace]]
							else:
								if fullNameSpace not in keptGroup[libName][1]:
									keptGroup[libName][1].append(fullNameSpace)
							keptGroup[fullNameSpace] = [fullNameSpace, []]
						else:
							if fullNameSpace not in keptGroup[libName][1]:
								keptGroup[libName][1].append(fullNameSpace)
							else:
								continue
				else:
					keptGroup[group.name()] = group
					print(group.name())
		print("-->> Process Result : Exporting :")
		if verbose >= 1:
			pprint(keptGroup)
		else:
			for key in keptGroup.keys():
				if keptGroup[key][0] is not None:
					print(key)

		if len(keptGroup.keys()) == 0: #no match found
			continue
		noMatch = False
		root = hou.node("/obj").createNode("geo", searchedString+"_From_"+node.name())
		root.children()[0].destroy()
		objectMergeNode = root.createNode("object_merge", node.name())
		objectMergeNode.setParms({"objpath1":node.path()})
		nullSplitNode = root.createNode("null", "splitBy_"+searchedString)
		nullSplitNode.setInput(0, objectMergeNode)
		if regroup is True:
			mergeNode = root.createNode("merge", "mergeAllGroups")
			outNode = root.createNode("null", "OUT_"+searchedString+"_From_"+node.name())
			outNode.setInput(0, mergeNode)
			outNode.setDisplayFlag(1)
			outNode.setRenderFlag(1)
		idx = 0
		for group in keptGroup.keys():
			if keptGroup[group][0] is None or group == "Mtl":
				continue
			if verbose >= 2:
				print("Creating Nodes for : "+group)
			deleteNode = root.createNode("delete", "keep_"+group)
			deleteNode.setInput(0, nullSplitNode)
			deleteNode.setParms({"group":"*"+keptGroup[group][0]+"_*", "negate":True})
			groupInput = deleteNode

			if keptGroup[group][1] != []:
				scdDeleteNode = root.createNode("delete", "keepOnly_"+group)
				scdDeleteNode.setInput(0, deleteNode)
				scdDeleteNode.setParms({"group":"*"+"* *".join(keptGroup[group][1])+"*"})
				groupInput = scdDeleteNode

			if regroup is True:
				groupNode = root.createNode("group", "group_"+group)
				groupNode.setInput(0, groupInput)
				groupNode.setParms({"crname":parentName+"_"+group, "pattern":"*", "destroyname":"* ^"+parentName+"_"+group+" ^*_Mtl_*"})

				mergeNode.setInput(idx, groupNode)

			idx += 1
	if noMatch is True:
		print("-->> Nothing Matched for : "+searchedString)
		hou.ui.displayMessage("Nothing Matched for :\n"+searchedString)
	else:	
		print("-->> Done Extracting : "+searchedString)
		hou.ui.displayMessage("Done Extracting :\n"+searchedString)

def createHouNode(inputCfg):
	cfg = {
		'nodeType':None,
		'nodeName':None,
		'parentGeometry':None,
		'inputs':[],
		# 'inputIdx':0,
		'parameters':{},
		'expressions':{},
		}
	cfg.update(inputCfg)

	if None in [cfg['nodeType'], cfg['nodeName'], cfg['parentGeometry']]:
		return -1;

	print('creating : ' + str(cfg))
	node = cfg['parentGeometry'].createNode(cfg['nodeType'], cfg['nodeName'])
	if cfg['inputs'] != [None]:
		idx = 0
		for inputNode in cfg['inputs']:
			if isinstance(inputNode, str) is True:
				inputNode = hou.node(cfg['parentGeometry'].path()+'/'+inputNode)
			print(inputNode)
			node.setInput(idx, inputNode)
			idx += 1
	if cfg['parameters'] != {}:
		node.setParms(cfg['parameters'])
	if cfg['expressions'] != {}:
		node.setParmExpressions(cfg['expressions'])
	return node

def deleteMultiNodes(inputCfg, geometry):
	print('------->> Cleaning')
	existing = geometry.children()
	print(existing)
	for node in existing:
		nodename = node.name()
		for nodecfg in inputCfg:
			if nodecfg['nodeName'] == nodename:
				print('deleting : '+nodename)
				node.destroy()
	print('------->> Cleaning Done')

def createMultiNodes(nodesSetup, geometry, clean=False, connectTo=None):
	print(nodesSetup)
	if clean is True:
		deleteMultiNodes(nodesSetup, geometry)
	previousNode = connectTo
	for node in nodesSetup:
		if 'create' in node.keys():
			if node['create'] is False:
				print('------->> Do not create :' + node['nodeName'])
				continue
		node['parentGeometry'] = geometry
		if node['inputs'][0] is True:
			node['inputs'][0] = previousNode
		print('------->> Create Node : '+ str(node['nodeName']))
		print(node)
		previousNode = createHouNode(node)


def cleanSceneSetup():
	abcPath = '/obj/SCENE_SETUP/'
	sceneSetup = hou.node(abcPath)
	allGeometry = sceneSetup.children()
	houColor = hou.Color((0, 0.5, 0))
	for geometry in allGeometry:
		if geometry.name().startswith('SETDRESS') is True:
			continue
		nodesSetup = [
		{ # Timeshift
			'nodeType':'timeshift',
			'create':True,
			'nodeName':'Freeze_Animation',
			'parentGeometry':None,
			# 'inputNode':None,
			# 'inputIdx':0,
			'inputs':[True],
			'parameters':{},
			'expressions':{"frame":'$RFSTART',},
		},
		{ # Set name
			'nodeType':'name',
			'create':True,
			'nodeName':geometry.name(),
			'parentGeometry':None,
			# 'inputNode':None,
			# 'inputIdx':0,
			'inputs':[True],
			'parameters':{},
			'expressions':{'name1':'$OS'},
		},
		{ # Set Shape name
			'nodeType':'group_to_attr_ql',
			'create':True,
			'nodeName':'Set_Shape_Name',
			'parentGeometry':None,
			# 'inputNode':None,
			# 'inputIdx':0,
			'inputs':[True],
			'parameters':{
				'groupmask':'* ^*_Mtl*',
				'defgrp_name':'no_shape',
				'name':'shapeName',
				},
			'expressions':{},
		},
		{ # OUT_GEO_PACKED
			'nodeType':'null',
			'create':True,
			'nodeName':"OUT_"+geometry.name()+"_PACKED",
			'parentGeometry':None,
			# 'inputNode':None,
			# 'inputIdx':0,
			'inputs':[True],
			'parameters':{},
			'expressions':{},
		},
		{ # Convert
			'nodeType':'convert',
			'create':True,
			'nodeName':'convertToPoly',
			'parentGeometry':None,
			# 'inputNode':None,
			# 'inputIdx':0,
			'inputs':[True],
			'parameters':{},
			'expressions':{},
		},
		{ # Attrib Copy
			'nodeType':'attribcopy',
			'create':True,
			'nodeName':'Get_Attribs_From_Packed',
			'parentGeometry':None,
			# 'inputNode':None,
			# 'inputIdx':0,
			'inputs':[True, 'OUT_'+geometry.name()+'_PACKED'],
			'parameters':{
				'attribname':'name path shapeName',
				},
			'expressions':{},
		},
		{ # Trail
			'nodeType':'trail',
			'create':True,
			'nodeName':'Compute_Velocity',
			'parentGeometry':None,
			# 'inputNode':None,
			# 'inputIdx':0,
			'inputs':[True],
			'parameters':{'result':3},
			'expressions':{},
		},
		
		{ # Set Mtl name
			'nodeType':'group_to_attr_ql',
			'create':True,
			'nodeName':'Set_Mtl_Name',
			'parentGeometry':None,
			# 'inputNode':None,
			# 'inputIdx':0,
			'inputs':[True],
			'parameters':{
				'groupmask':'*_Mtl*',
				'defgrp_name':'no_mtl',
				'name':'mtlName',
				},
			'expressions':{},
		},
		{ # Facet
			'nodeType':'facet',
			'create':True,
			'nodeName':'Compute_Normals',
			'parentGeometry':None,
			# 'inputNode':None,
			# 'inputIdx':0,
			'inputs':[True],
			'parameters':{'postnml':True,},
			'expressions':{},
		},
		{ # Attrib Delete
			'nodeType':'attribdelete',
			'create':True,
			'nodeName':'Clean_Attributes',
			'parentGeometry':None,
			# 'inputNode':None,
			# 'inputIdx':0,
			'inputs':[True],
			'parameters':{'primdel':'path varmap'},
			'expressions':{},
		},
		{ # OUT_Bake
			'nodeType':'null',
			'create':True,
			'nodeName':"OUT_inputBake_"+geometry.name(),
			'parentGeometry':None,
			# 'inputNode':None,
			# 'inputIdx':0,
			'inputs':[True],
			'parameters':{},
			'expressions':{},
		},
		{ # Output
			'nodeType':'output',
			'create':True,
			'nodeName':'OUT_'+geometry.name(),
			'parentGeometry':None,
			# 'inputNode':None,
			# 'inputIdx':0,
			'inputs':[True],
			'parameters':{},
			'expressions':{},
		},
		]

		print(geometry)
		nullOut = hou.node(geometry.path()+'/OUT')
		alembic = hou.node(geometry.path()+'/IN')
		alembicParm = {
		'groupnames':4,
		}
		alembic.setParms(alembicParm)
		createMultiNodes(nodesSetup, geometry, True, nullOut)
		nullPacked = hou.node(geometry.path()+'/OUT_' + geometry.name() + '_PACKED')
		nullBake  = hou.node(geometry.path()+'/OUT_inputBake_' + geometry.name())
		nullOutput = hou.node(geometry.path()+'/OUT_' + geometry.name())
		for node in [nullOutput, nullOut, nullPacked, nullBake]:
			node.setColor(houColor)
		# nullOutput.setDisplayFlag(1)
		# nullOutput.setRenderFlag(1)




################ FROM PABLO IMPORT
FORBIDDENVARS = ['NFRAMES','FF','F','T','FPS','FSTART','FEND','RFSTART','RFEND','TSTART','TEND','PI','E','UNITLENGTH','UNITMASS']
def getGlobalVars(forbiddenvars): 
    '''returns a dictionary of the current hip file's global variables, expects a list of variable names that should be ignored'''
    d = {key.strip(): value.strip() for (key, value) in [x.split('\t=') for x in hou.hscript('set')[0].splitlines()] if key.strip() not in forbiddenvars}
    return d

def mergeHip(shottuple,hipname):
    #'/u/pets2/Users/pablop/Files/text/PETS2/S0683/P0840/Vfx_Houdini_TallGrass/PETS2_S0683_P0840-Vfx_Houdini_TallGrass.hip'
    hf = '/u/{0[0]}/Users/COM/Files/text/{0[1]}/{0[2]}/{0[3]}/Vfx_Houdini_{1}/{0[1]}_{0[2]}_{0[3]}-Vfx_Houdini_{1}.hip'.format(shottuple,hipname)
    if not os.path.isfile(hf): 
        print('file to merge not found: \n'+hf)
        return
    if os.path.getsize(hf) == 0:
        print('file to merge is empty (has it ever been published?): \n'+hf)
        return
    print '----------------------'
    print hf
    print '----------------------'
    cmdFile = "/var/tmp/houImport.cmd"
    tmpHip = "/var/tmp/toImport.hip"
    subnetName = "_".join(shottuple)+"_"+hipname
    globalvars=getGlobalVars(FORBIDDENVARS)

    with open(cmdFile,'w') as file:
        cmd2='''
hou.hipFile.merge( "{sourceHip}", node_pattern="*", ignore_load_warnings=1)
subnet = hou.node("/obj").createNode("subnet","{subnetName}")
contextdico = {{'obj':'subnet','out':'ropnet','ch':'chopnet','shop':'shopnet','img':'cop2net','vex':'vopnet'}}
for context in hou.node("/").children():
    [x.destroy() for x in context.stickyNotes()]
    [x.destroy() for x in context.networkBoxes()]
    if context.type().name() in contextdico and context.children():
        if context.type().name() == 'img': continue #does not work with img networks yet
        exports = [x for x in context.allSubChildren() if "mg_universalExporter" in x.type().name()]
        if len(exports):
            for export in exports:
                export.hide(1)
                export.destroy()
        contextroot = subnet.createNode(contextdico[context.type().name()],context.name())
        if not len(context.children()): continue
        childs = [x for x in list(context.children()) if x !=subnet]
        if not len(childs): continue
        print '-------------------------------'
        print contextroot
        print '-------------------------------'
        for node in childs:
            print "   "+node.name()
        hou.copyNodesTo(childs,contextroot)
        for node in childs:
            node.destroy()
subnet.layoutChildren()
hou.hipFile.save("{tmpHip}")
'''.format(sourceHip=hf,tmpHip=tmpHip,subnetName=subnetName)
        file.write(cmd2)
    val = os.system("hython " + cmdFile)
    print val
    #TRYING TO RECOVER THE PROPER VARIABLES, AND PREVENTING THE MERGE IF THE CMDS FAILED
    if val ==0:
        #print 'would have merged'
        hou.hipFile.merge(tmpHip) #this executes even if the file creation failed
        hou.setUpdateMode(hou.updateMode.Manual)
        for (key,value) in globalvars.iteritems():
            hou.hscript('setenv {}={}'.format(key,value))#recover all global var values
        newglobalvars = getGlobalVars(FORBIDDENVARS)
        importedVars = [x for x in globalvars.keys() if x not in newglobalvars.keys()]
        for var in importedVars: #unset all global variables that were not present before the merge
            hou.hscript('setenv -u {}'.format(var))
    else:
        print val
        raise ValueError('failed the merge, send pablop '+cmdFile+" to debug")

def renameObjectMerge():
	selection = hou.selectedNodes()
	for obj in selection:
		print(obj.type().name())
		if obj.type().name() == 'object_merge':
			mergingObj = str(obj.parm('objpath1').eval())
			print(mergingObj)
			obj.setName('merge_'+mergingObj.split('/')[-1])