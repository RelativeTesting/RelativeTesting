# Copyright: copyright.txt

from . symbolic_type import SymbolicObject

# we use multiple inheritance to achieve concrete execution for any
# operation for which we don't have a symbolic representation. As
# we can see a SymbolicInteger is both symbolic (SymbolicObject) and 
# concrete (int)

class SymbolicInteger(SymbolicObject,int):
	# since we are inheriting from int, we need to use new
	# to perform construction correctly
	def __new__(cls, name, v, expr=None):
		return int.__new__(cls, v)

	def __init__(self, name, v, expr=None):
		SymbolicObject.__init__(self, name, expr)
		self.val = v

	def getConcrValue(self):
		return self.val

	def wrap(conc,sym):
		return SymbolicInteger("se",conc,sym)

	def __hash__(self):
		return hash(self.val)

	def _op_worker(self,args,fun,op):
		#print("Is it here?", op)
		return self._do_sexpr(args, fun, op, SymbolicInteger.wrap)

# now update the SymbolicInteger class for operations we
# will build symbolic terms for

ops =  [("add",    "+"  ),\
	("sub",    "-"  ),\
	("mul",    "*"  ),\
	("mod",    "%"  ),\
	("floordiv", "//" ),\
	("and",    "&"  ),\
	("or",     "|"  ),\
	("xor",    "^"  ),\
	("lshift", "<<" ),\
	("rshift", ">>" ), \
	("truediv", "/") ]

def make_method(method,op,a):
	
	code  = "def %s(self,other):\n" % method
	# code += "	if isinstance(other, SymbolicInteger): \n"
	# code += "		self_parent = find_parent(self) \n"
	# code += "		other_parent = find_parent(other) \n"	
	# code += "		if self_parent != other_parent: \n"
	# code += "			ret = self.getConcrValue() == int(other) \n"
	# code += "			expr = ['==', self, int(other)]\n"
	# code += "			se = SymbolicInteger('se', ret, expr) \n"
	# code += "			SymbolicObject.SI.arithmeticBranch(ret, se)\n"

	# code += "	else: \n"
	# code += "		ret = self.getConcrValue() == int(other) \n"
	# code += "		expr = ['==', self, int(other)]\n"
	# code += "		se = SymbolicInteger('se', ret, expr) \n"
	# code += "		SymbolicObject.SI.arithmeticBranch(ret, se)\n"
	code += "	return self._op_worker(%s,lambda x,y : x %s y, \"%s\")" % (a,op,op)
	locals_dict = {}
	exec(code, globals(), locals_dict)
	setattr(SymbolicInteger,method,locals_dict[method])

def make_method2(method,op,a):
	code  = "def %s(self,other):\n" % method
	code += "	return self._op_worker(%s,lambda x,y : x %s y, \"%s\")" % (a,op,op)
	locals_dict = {}
	exec(code, globals(), locals_dict)
	setattr(SymbolicInteger,method,locals_dict[method])


for (name,op) in ops:
	
	method  = "__%s__" % name
	make_method(method,op,"[self,other]")
	rmethod  = "__r%s__" % name
	make_method(rmethod,op,"[other,self]")
	


def change_operators(expr, op=None):
	if isinstance(expr, list):
		nested = False
		for i in range(len(expr)-1, -1, -1):
			if isinstance(expr[i], list):
				nested = True
				change_operators(expr[i], op)
			elif isinstance(expr[i], str):
				if nested:
					expr[i] = '=='
				else:
					expr[i] = op

def find_parent(symbolic_object):
	if isinstance(symbolic_object, SymbolicObject):
		if symbolic_object.expr == None:
			return symbolic_object.name
		else:
			return find_parent(symbolic_object.expr[1])
	elif isinstance(symbolic_object, list):
		return find_parent(symbolic_object[1])