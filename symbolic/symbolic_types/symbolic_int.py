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
	code += "	ret = bool(self.getConcrValue()) \n"
	code += "	change_operators(self.expr, '==') \n"
	code += "	#print(%s, '%s', %s, %s, self.expr)\n" % ("'method:'", op, a, "'return is:'")
	code += "	SymbolicObject.SI.whichBranch(True, self)\n"
	code += "	#change_operators(self.expr, '!=') \n"
	code += "	#SymbolicObject.SI.whichBranch(True, self)\n"
	code += "	#if self.expr != None: \n"
	code += "	#	self.expr[0] = expr \n"
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
	#print("change_operators", expr)
	if isinstance(expr, list):
		nested = False
		for i in range(len(expr)-1, -1, -1):
			if isinstance(expr[i], list):
				nested = True
				change_operators(expr[i], op)
			elif isinstance(expr[i], str):
				if nested:
					expr[i] = '&'
				else:
					expr[i] = op
	print("change_operators", expr)