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
	
	# This method is used to add the constructor function for an argument. 
	# It takes the name parameter, which represents the argument name, 
	# the init parameter, which represents the initial value of the argument,
	# the constructor parameter, which represents the constructor function 
	# that generates the symbolic value for the argument
	def addArgumentConstructor(self, name, init, constructor):
		self.initial_value[name] = init
		self.arg_constructor[name] = constructor

	# returns the names of the defined arguments.
	def getNames(self):
		return self.arg_constructor.keys()

	# generates the symbolic value for a specific argument. 
	# It takes the name parameter, which represents the argument name,
	# and the optional val parameter, which represents the argument value
	def createArgumentValue(self,name,val=None):
		if val == None:
			val = self.initial_value[name]
		return self.arg_constructor[name](name,val)
	
	# takes the constraint parameter, which represents a constraint expression
	def addPreConstraint(self, constraint):
		self.pre_constraints.append(constraint)
		
	# takes the asserts parameter, which represents an assertion expression
	def addPreAsserts(self, asserts):
		self.pre_asserts.append(asserts)
		

	

