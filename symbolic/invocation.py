# Copyright: see copyright.txt

class FunctionInvocation:
	def __init__(self, function, reset):
		self.function = function
		self.reset = reset
		self.arg_constructor = {}
		self.initial_value = {}
		self.pre_asserts = []

	def callFunction(self,args):
		self.reset()
		return self.function(**args)

	def addArgumentConstructor(self, name, init, constructor):
		self.initial_value[name] = init
		self.arg_constructor[name] = constructor

	def getNames(self):
		return self.arg_constructor.keys()

	def createArgumentValue(self,name,val=None):
		if val == None:
			val = self.initial_value[name]
		return self.arg_constructor[name](name,val)
	
	def addPreConstraint(self, constraint):
		self.pre_constraints.append(constraint)

	def addPreAsserts(self, asserts):
		self.pre_asserts.append(asserts)
		

	

