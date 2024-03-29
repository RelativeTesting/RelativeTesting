import utils

from RelativeTesting.symbolic.symbolic_types.symbolic_int import SymbolicInteger
from RelativeTesting.symbolic.symbolic_types.symbolic_str import SymbolicStr
from RelativeTesting.symbolic.symbolic_types.symbolic_type import SymbolicType
from ..predicate import Predicate
from z3 import *

class Z3Expression(object):
	def __init__(self):
		self.z3_vars = {}

	def toZ3(self,solver,asserts,query, reset=True):
		if reset:
			self.z3_vars = {}

		if asserts != None:
			solver.assert_exprs([self.predToZ3(p,solver) for p in asserts])
		
		if query != None:
			solver.assert_exprs(Not(self.predToZ3(query,solver)))
		#solver.assert_exprs(Not(self.predToZ3(query,solver)))
		

	def predToZ3(self,pred,solver,env=None):
		sym_expr = self._astToZ3Expr(pred.symtype,solver,env)
		if env == None:
			if not is_bool(sym_expr):
				sym_expr = sym_expr != self._getConstant(0,solver)
			if not pred.result:
				sym_expr = Not(sym_expr)
		else:
			if not pred.result:
				if not is_bool(sym_expr):
					sym_expr = not sym_expr
				else:
					sym_expr = Not(sym_expr)
		return sym_expr

	def getIntVars(self):
		return [ v[1] for v in self.z3_vars.items() if self._isIntVar(v[1]) ]

	# ----------- private ---------------

	def _isIntVar(self, v):
		raise NotImplementedException
	
	def _isStringVar(self, v):
		raise NotImplementedException

	def _getVariable(self,expr,solver):
		name = expr.name
		if name not in self.z3_vars:
			if isinstance(expr, SymbolicInteger):
				self.z3_vars[name] = self._variable(name,solver)
			elif isinstance(expr, SymbolicStr):
				self.z3_vars[name] = String(name,solver.ctx)
		return self.z3_vars[name]

	def _getConstant(self,expr,solver):
		if isinstance(expr, int):
			return self._constant(expr,solver)
		elif isinstance(expr, str):
			return StringVal(expr,solver.ctx)

	def _variable(self,name,solver):
		raise NotImplementedException

	def _constant(self,v,solver):
		raise NotImplementedException

	def _wrapIf(self,e,solver,env):
		if env == None:
			return If(e,self._constant(1,solver),self._constant(0,solver))
		else:
			return e

	# add concrete evaluation to this, to check
	def _astToZ3Expr(self,expr,solver,env=None):
		#print("Hello", expr, type(expr).__name__)
		if isinstance(expr, list) and len(expr) == 3:
			op = expr[0]
			args = [ self._astToZ3Expr(a,solver,env) for a in expr[1:] ]
			z3_l,z3_r = args[0],args[1]
			return self._opToZ3Expr(op,z3_l,z3_r,solver,env)
		
		elif isinstance(expr, list) and len(expr) == 2:
			op = expr[0]
			arg =  self._astToZ3Expr(expr[1],solver,env)
			tmp =  self._getConstant(expr[1], solver)
			if op == "str.len":
				return Length(arg)
		elif isinstance(expr, list) and len(expr) > 3:
			op = expr[0]
			if op == "slice":
				if len(expr) == 4:
					val, l, u = expr[1], expr[2], expr[3]
					return SubString(val, l, u-l)
				elif len(expr) == 5:
					val, l, u, s = expr[1], expr[2], expr[3], expr[4]
					return SubString(val, l, u, s)

		elif isinstance(expr, SymbolicInteger) or isinstance(expr, SymbolicStr):
			if expr.isVariable():
				if env == None or expr.name not in env:
					return self._getVariable(expr,solver)
				else:
					return env[expr.name]
			else:
				return self._astToZ3Expr(expr.expr,solver,env)

		elif isinstance(expr, SymbolicType):
			utils.crash("{} is an unsupported SymbolicType of {}".
						format(expr, type(expr)))

		elif isinstance(expr, int) or isinstance(expr, str):
			if env == None:
				return self._getConstant(expr,solver)
			else:
				return expr
		else:
			utils.crash("Unknown node during conversion from ast to Z3 (expressions): %s" % expr)

	def preAssertsToZ3(self,pre_asserts,solver):
		sym_expr = []
		for pre_assert in pre_asserts:
			tmp = self._astToZ3Expr(pre_assert.symtype,solver)
			if isinstance(tmp, ArithRef):
				tmp = 0 != tmp
			elif is_bool(tmp):
				tmp = tmp
			sym_expr.append(tmp)
		return sym_expr

	def _opToZ3Expr(self,op,z3_l,z3_r,solver, env=None):
		# arithmetical operations
		if op == "+":
			return self._add(z3_l, z3_r, solver)
		elif op == "-":
			return self._sub(z3_l, z3_r, solver)
		elif op == "*":
			return self._mul(z3_l, z3_r, solver)
		elif op == "/":
			return self._div(z3_l, z3_r, solver)
		elif op == "//":
			return self._floordiv(z3_l, z3_r, solver)
		elif op == "%":
			return self._mod(z3_l, z3_r, solver)

		# bitwise
		elif op == "<<":
			return self._lsh(z3_l, z3_r, solver)
		elif op == ">>":
			return self._rsh(z3_l, z3_r, solver)
		elif op == "^":
			return self._xor(z3_l, z3_r, solver)
		elif op == "|":
			return self._or(z3_l, z3_r, solver)
		elif op == "&":
			return self._and(z3_l, z3_r, solver)

		# equality gets coerced to integer
		elif op == "==":
			return self._wrapIf(z3_l == z3_r,solver,env)
		elif op == "!=":
			return self._wrapIf(z3_l != z3_r,solver,env)
		elif op == "<":

			return self._wrapIf(z3_l < z3_r,solver,env)
		elif op == ">":
			return self._wrapIf(z3_l > z3_r,solver,env)
		elif op == "<=":
			return self._wrapIf(z3_l <= z3_r,solver,env)
		elif op == ">=":
			return self._wrapIf(z3_l >= z3_r,solver,env)
		

		# string operations

		elif op == "getitem":
			return SubString(z3_l,z3_r, 1)


		else:
			utils.crash("Unknown BinOp during conversion from ast to Z3 (expressions): %s" % op)	




	def _add(self, l, r, solver):
		return l + r

	def _sub(self, l, r, solver):
		return l - r

	def _mul(self, l, r, solver):
		return l * r

	def _div(self, l, r, solver):
		return l / r
	
	def _floordiv(self, l, r, solver):
		return l.__truediv__(r)

	def _mod(self, l, r, solver):
		return l % r

	def _lsh(self, l, r, solver):
		return l << r

	def _rsh(self, l, r, solver):
		return l >> r

	def _xor(self, l, r, solver):
		return l ^ r

	def _or(self, l, r, solver):
		return l | r

	def _and(self, l, r, solver):
		return l & r
