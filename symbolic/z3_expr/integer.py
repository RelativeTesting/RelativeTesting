from z3 import *
from .expression import Z3Expression

class Z3Integer(Z3Expression):
	def _isIntVar(self,v):
		#return isinstance(v,IntNumRef)
		return isinstance(v,ArithRef)
	
	def _isStrVar(self,v):
		return isinstance(v, StringVal)

	def _variable(self,name,solver):
		return Int(name,solver.ctx)

	def _constant(self,v,solver):
		return IntVal(v,solver.ctx)

	def _or(self, l, r, solver):
		if isinstance(l, ArithRef) and isinstance(r, ArithRef):
			l = 0 != l
			r = 0 != r
			return Or(l, r)
		return Z3Expression._mod(self,l, r,solver)

	def _and(self, l, r, solver):
		if isinstance(l, ArithRef) and isinstance(r, ArithRef):
			l = 0 != l
			r = 0 != r
			return And(l, r)
		if isinstance(l, ArithRef) and isinstance(r, BoolRef):
			l = 0 != l
			return And(l, r)
		if isinstance(l, BoolRef) and isinstance(r, ArithRef):
			r = 0 != r
			return And(l, r)
		return Z3Expression._and(self,l, r,solver)(l, r)
