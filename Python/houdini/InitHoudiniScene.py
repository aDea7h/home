from collections import OrderedDict
import hou
from pprint import pprint as pprint
#mport houdiniCustomScripts as scripts
#reload(scripts)
import houdiniNodes as houNodes
reload(houNodes)

class InitHoudiniScene():
	def __init__(self, cfg={}, verbose=1):
		self.verbose = verbose
		obj_setup = OrderedDict()
		obj_setup['config'] = {
			'nodeType': 'null',
			'nodeName': 'Config',
			}
		obj_setup['static'] = {
			'nodeType': 'geo',
			'nodeName': 'Static',
			}
		obj_setup['animated'] = {
			'nodeType': 'geo',
			'nodeName': 'Animated',
			'inputs': ['static', 'animated'],
			}

		out_setup = OrderedDict()
		out_setup['input_Static'] = {
			'nodeType': 'merge',
			'nodeName': 'input_Static',
			}
		out_setup['input_Animated'] = {
			'nodeType': 'merge',
			'nodeName': 'input_Animated',
			}
		out_setup['allInputs'] = {
			'nodeType': 'merge',
			'nodeName': 'all_inputs',
			'inputs': ['input_Static', 'input_Animated'],
			}
		scene_setup = OrderedDict()
		scene_setup['freezeAnimation'] = {
			'nodeType':'timeshift',
			'nodeName':'Freeze_Animation',
			'inputs':[True],
			'expressions':{"frame":'$RFSTART',},
		}
		scene_setup['setName'] = {
			'nodeType':'name',
			'nodeName':'setName',
			'inputs':[True],
			'expressions':{'name1':'$OS'},
		}
		# scene_setup['setNameShape'] = {
		# 	'nodeType':'group_to_attr_ql',
		# 	'nodeName':'Set_Shape_Name',
		# 	'inputs':[True],
		# 	'parameters':{
		# 		'groupmask':'* ^*_Mtl*',
		# 		'defgrp_name':'no_shape',
		# 		'name':'shapeName',
		# 		},
		# }
		scene_setup['outPackedGeo'] = {
			'nodeType':'null',
			'nodeName':"outPackedGeo",
			'inputs':[True],
		}
		scene_setup['convert'] = {
			'nodeType':'convert',
			'nodeName':'convertToPoly',
			'inputs':[True],
		}
		scene_setup['copyAttrs'] = {
			'nodeType':'attribcopy',
			'nodeName':'Get_Attribs_From_Packed',
			'inputs':[True, 'outPackedGeo'],
			'parameters':{
				'attribname':'name path shapeName',
				},
		}
		scene_setup['computeVel'] = {
			'nodeType':'trail',
			'nodeName':'Compute_Velocity',
			'inputs':[True],
			'parameters':{'result':3},
		}
		# scene_setup['setMtlName'] = {
		# 	'nodeType':'group_to_attr_ql',
		# 	'nodeName':'Set_Mtl_Name',
		# 	'inputs':[True],
		# 	'parameters':{
		# 		'groupmask':'*_Mtl*',
		# 		'defgrp_name':'no_mtl',
		# 		'name':'mtlName',
		# 		},
		# }
		scene_setup['computeNormals'] = {
			'nodeType':'facet',
			'nodeName':'Compute_Normals',
			'inputs':[True],
			'parameters':{'postnml':True,},
		}
		scene_setup['cleanAttribs'] = {
			'nodeType':'attribdelete',
			'nodeName':'Clean_Attributes',
			'inputs':[True],
			'parameters':{'primdel':'path varmap'},
		}
		scene_setup['inputBake'] = {
			'nodeType':'null',
			'nodeName':"OUT_inputBake_GeometryName",
			'inputs':[True],
		}
		scene_setup['output'] = {
			'nodeType':'output',
			'nodeName':'OUT_GeometryName',
			'inputs':[True],
		}

		scene_connections = [
			("/obj/CAMERA", '/obj/Config'),
			("/obj/CAMERA/CAMERA", '/obj/CAMERA/1'),
			("/obj/Static", '/obj/Config'),
			("/obj/Animated", '/obj/Config'),
		]

		self.cfg = {
			'scene_setup_path': '/obj/SCENE_SETUP/',
			'obj_setup': obj_setup,
			'out_setup': out_setup,
			'scene_setup': scene_setup,
			'scene_connections': scene_connections,
		}

		self.cfg.update(cfg)
		self.buildNodesDict()

	def buildNodesDict(self):
		self.cfg['obj_nodes'] = OrderedDict()
		parent = hou.node('/obj/')
		for node in self.cfg['obj_setup']:
			self.cfg['obj_setup'][node]['parentGeometry'] = parent
			self.cfg['obj_nodes'][node] = houNodes.Node(self.cfg['obj_setup'][node])

		self.cfg['out_nodes'] = OrderedDict()
		parent = hou.node('/out/')
		for node in self.cfg['out_setup']:
			self.cfg['out_setup'][node]['parentGeometry'] = parent
			self.cfg['out_nodes'][node] = houNodes.Node(self.cfg['out_setup'][node])

		# self.cfg['obj_nodes'] = OrderedDict()
		# parent = hou.node(self.cfg['scene_setup_path'])
		# for node in self.cfg['scene_setup_path']:
		# 	self.cfg['scene_setup_nodes'][node] = houNodes(self.cfg['scene_setup_path'][node])
		# 	self.cfg['scene_setup_nodes'][node].parentGeometry = hou.node('/obj/')


	def full_setup(self):
		self.obj_setup()
		self.out_setup()
		# self.scenesetup()
		self.set_scene_connections()

	def obj_setup(self):
		self.setup(self.cfg['obj_nodes'])

	def out_setup(self):
		self.setup(self.cfg['out_nodes'])

	def setup(self, nodeDict):
		# scripts.createMultiNodes(self.cfg['obj_setup'], hou.node('/obj/'), False, None)
		previousNode = None
		for nodeName in nodeDict:
			print('creating :'+nodeName)
			nodeObj = nodeDict[nodeName]
			nodeObj.create()

			idx = 0
			for inputName in nodeObj.inputs:
				if inputName is True:
					nodeObj.inputs[idx] = previousNode
				if isinstance(inputName, str) is True:
					nodeObj.inputs[idx] = hou.node(str(nodeObj.parentGeometry)+'/'+inputName)
				idx +=1
			nodeObj.set_inputs()

			previousNode = nodeObj.houNode


	

	def scenesetup(self):
		sceneSetup = hou.node(self.cfg['scenesetup_path'])
		allGeometry = sceneSetup.children()
		houColor = hou.Color((0, 0.5, 0))
		for geometry in allGeometry:
			if geometry.name().startswith('SETDRESS') is True:
				continue

			print(geometry)
			nullOut = hou.node(geometry.path()+'/OUT')
			alembic = hou.node(geometry.path()+'/IN')
			#alembic cfg
			alembicParm = {
			'groupnames':4,
			}
			alembic.setParms(alembicParm)
			#create nodes
			self.cfg['scene_setup']['setName']['nodeName'] = geometry.name()
			self.cfg['scene_setup']['outPackedGeo']['nodeName'] = 'OUT_{}_PACKED'.format(geometry.name())
			self.cfg['scene_setup']['inputBake']['nodeName'] = 'OUT_inputBake_{}'.format(geometry.name())
			self.cfg['scene_setup']['output']['nodeName'] = 'OUT_{}'.format(geometry.name())
			scripts.createMultiNodes(self.cfg['scene_setup'], geometry, True, nullOut)

			nullPacked = hou.node(geometry.path()+'/OUT_' + geometry.name() + '_PACKED')
			nullBake  = hou.node(geometry.path()+'/OUT_inputBake_' + geometry.name())
			nullOutput = hou.node(geometry.path()+'/OUT_' + geometry.name())
			for node in [nullOutput, nullOut, nullPacked, nullBake]:
				node.setColor(houColor)
			# nullOutput.setDisplayFlag(1)
			# nullOutput.setRenderFlag(1)

	def set_scene_connections(self):
		# cfg_node = hou.node('/obj/Config')
		# if cfg_node is None:
		# 	cfg_node = hou.node('/obj').createNode('null', 'Config')
		# for geometry in self.cfg['scene_scale']:
		#
		# 	geometryNode = hou.node(geometry)
		# 	geometryNode.setInput(0, cfg_node)
		for node, inputNode in self.cfg['scene_connections']:
			node = hou.node(node)
			inputNode = hou.item(inputNode)
			if None in [node, inputNode]:
				print('unable to connect {} to {}'.format(inputNode, node))
				continue
			node.setInput(0, inputNode)
