import hou

class Node:
	def __init__(self, tweakCfg={}):
		#TODO positions
		cfg = {
			'nodeType':None,
			'nodeName':None,
			'parentGeometry':None,
			'inputs':[],
			'parameters':{},
			'expressions':{},
			'houNode':None,
			'isValid':None,
		}
		cfg.update(tweakCfg)

		for key in cfg:
			setattr(self, key, cfg[key])

		self.check_validity()

	def __repr__(self):
		return self.nodeName

	def check_validity(self):
		if None in [self.nodeType, self.nodeName, self.parentGeometry]:
			print('should have type, name, parent found : {}, {}, {}'.format(self.nodeType, self.nodeName, self.parentGeometry))
			self.isValid = False
		elif isinstance(self.parentGeometry, str) is True:
			self.parentGeometry = hou.node(self.parentGeometry)
		elif type(self.parentGeometry) not in [hou.SopNode, hou.RopNode, hou.ObjNode, hou.Node]:
			print('not a houdini object : {}'.format(self.parentGeometry))
			self.isValid = False
		else:
			self.isValid = True

	def create(self):
		if self.isValid is False:
			print('invalid node {} : {}'.format(self.nodeType, self.nodeName))
			# print(self.__dict__)
			return

		self.houNode = self.parentGeometry.createNode(self.nodeType, self.nodeName)

	def set_inputs(self):
		idx = 0
		for inputNode in self.inputs:
			if isinstance(inputNode, str) is True:
				inputNode = hou.node(str(self.parentGeometry)+'/'+inputNode)
			elif type(inputNode) not in [hou.SopNode, hou.RopNode, hou.ObjNode]:
				return
			print(idx, inputNode, self.inputs)
			self.houNode.setInput(idx, inputNode)
			idx += 1

	def setParmAndExpr(self):
		if self.parameters != {}:
			self.houNode.setParms(self.parameters)
		if self.expressions != {}:
			self.houNode.setParmExpressions(self.expressions)