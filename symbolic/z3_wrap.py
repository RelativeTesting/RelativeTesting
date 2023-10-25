# Copyright: see copyright.txt

import sys
import ast
import logging

from z3 import *
from .z3_expr.integer import Z3Integer
from .z3_expr.bitvector import Z3BitVector
from .z3_expr.string import Z3String

log = logging.getLogger("se.z3")

class Z3Wrapper(object):
	def __init__(self):
		self.N = 32
		self.asserts = None
		self.query = None
		self.use_lia = True
		self.z3_expr = None
		self.pre_asserts = None

	def findCounterexample(self, asserts, query):
		"""Tries to find a counterexample to the query while
	  	 asserts remains valid."""
		self.solver = Solver()
		self.query = query
		#self.asserts = self._coneOfInfluence(asserts,query)
		self.asserts = asserts
		res = self._findModel()
		log.debug("Query -- %s" % self.query)
		log.debug("Asserts -- %s" % asserts)
		log.debug("Cone -- %s" % self.asserts)
		log.debug("Result -- %s" % res)
		return res

	# private

	# this is very inefficient
	def _coneOfInfluence(self,asserts,query):
		cone = []
		cone_vars = set(query.getVars())
		ws = [ a for a in asserts if len(set(a.getVars()) & cone_vars) > 0 ]
		remaining = [ a for a in asserts if a not in ws ]
		while len(ws) > 0:
			a = ws.pop()
			a_vars = set(a.getVars())
			cone_vars = cone_vars.union(a_vars)
			cone.append(a)
			new_ws = [ a for a in remaining if len(set(a.getVars()) & cone_vars) > 0 ]
			remaining = [ a for a in remaining if a not in new_ws ]
			ws = ws + new_ws
		return cone

	def _findModel(self):
		if self.use_lia:
			self.solver.push()
			self.z3_expr = Z3Integer()
			
			if self.pre_asserts != None:
				pre_asserts = self.z3_expr.preAssertsToZ3(self.pre_asserts, self.solver)
				self.solver.assert_exprs(pre_asserts)

			self.z3_expr.toZ3(self.solver,self.asserts,self.query)			
			res = self.solver.check()
			self.solver.pop()
			if res == unsat:
				return None

		(ret,mismatch) = self._findModel2()
		if ret == unsat:
			res = None
		elif ret == unknown:
			res = None
		elif not mismatch:
			res = self._getModel()
		else:
			res = None
		#if self.N<=64: self.solver.pop()
		return res


	def _setAssertsQuery(self):
		
		self.z3_expr.toZ3(self.solver,self.asserts,self.query)

	def _findModel2(self):
		if self.pre_asserts != None:
			pre_asserts = self.z3_expr.preAssertsToZ3(self.pre_asserts, self.solver)
			self.solver.assert_exprs(pre_asserts)
		self._setAssertsQuery()
		
		print("solver", self.solver.assertions())
		res = unsat
		res = self.solver.check()
		if res == sat:
			# Does concolic agree with Z3? If not, it may be due to overflow
			model = self._getModel()
			print("model", model)
			mismatch = False
			if self.asserts != None:
				for a in self.asserts:
					eval = self.z3_expr.predToZ3(a,self.solver,model)
					if (not is_bool(eval) and not eval):
						mismatch = True
						break
			if ((not mismatch) and (self.query != None)):
				a = self.z3_expr.predToZ3(self.query,self.solver,model)
				if not is_bool(a):
					mismatch = not (not a)
			#print(mismatch)
			return (res,mismatch)
		elif res == unknown:
			self.solver.pop()
		return (res,False)

	def _getModel(self):
		res = {}
		model = self.solver.model()
		for name in self.z3_expr.z3_vars.keys():
			try:
				ce = model.eval(self.z3_expr.z3_vars[name])
				if isinstance(self.z3_expr.z3_vars[name], SeqRef):
					res[name] = ce.as_string()
				elif isinstance(self.z3_expr.z3_vars[name], ArithRef):
					res[name] = ce.as_long()
			except:
				pass
		return res

	def addPreAsserts(self, pre_asserts):
		self.pre_asserts = pre_asserts
		
	# def _boundIntegers(self,vars,val):
	# 	bval = BitVecVal(val,self.N,self.solver.ctx)
	# 	bval_neg = BitVecVal(-val-1,self.N,self.solver.ctx)
	# 	return And([ v <= bval for v in vars]+[ bval_neg <= v for v in vars])

	# def _getModel(self):
	# 	res = {}
	# 	model = self.solver.model()
	# 	for name in self.z3_expr.z3_vars.keys():
	# 		try:
	# 			ce = model.eval(self.z3_expr.z3_vars[name])
	# 			res[name] = ce.as_signed_long()
	# 			#res[name] = ce.as_string()
	# 		except:
	# 			pass
	# 	return res


	# def _findModelString(self):
	# 	if self.use_lia:
	# 		self.solver.push()
	# 		self.z3_expr = Z3String()
	# 		self.z3_expr.toZ3(self.solver,self.asserts,self.query)			
	# 		res = self.solver.check()
	# 		self.solver.pop()
	# 		if res == unsat:
	# 			return None
		
	# 	(ret, mismatch) = self._findModel2string()
	# 	if ret == unsat:
	# 		res = None
	# 	elif ret == unknown:
	# 		res = None
	# 	elif not mismatch:
	# 		res = self._getModel()
	# 	else:
	# 		res = None
	# 	return res
		
	# 	(ret, mismatch) = self._findModel2string()
	# def _findModel2string(self):
	# 	self.z3_expr.toZ3(self.solver,self.asserts,self.query)
	# 	print("solver ", self.solver.assertions())
	# 	res = unsat
	# 	self.solver.push()		
	# 	res = self.solver.check()

	# 	if res == sat:
	# 		ans = {}
	# 		#print("solver ", self.solver.assertions())
	# 		model = self.solver.model()
	# 		print("model", model)
	# 		for name in self.z3_expr.z3_vars.keys():
	# 			try:
	# 				ce = model.eval(self.z3_expr.z3_vars[name])
	# 				ans[name] = ce
	# 			except:
	# 				pass
	# 		return (ans,False)
	# 	return (res,False)

	# def _findModel(self):
	# # Try QF_LIA first (as it may fairly easily recognize unsat instances)
	# type_name = "Z3Integer"
	# if type_name == "Z3Integer":
	# 	return self._findModelInt()
	# elif type_name == "Z3String":
	# 	return self._findModelString()


	# def _setAssertsQuery(self):
	# 	self.z3_expr = Z3BitVector(self.N)
	# 	self.z3_expr.toZ3(self.solver,self.asserts,self.query)

	# def _findModel2(self):
	# 	self._setAssertsQuery()
	# 	int_vars = self.z3_expr.getIntVars()
	# 	res = unsat
	# 	while res == unsat and self.bound <= (1 << (self.N-1))-1:
	# 		self.solver.push()
	# 		constraints = self._boundIntegers(int_vars,self.bound)
	# 		self.solver.assert_exprs(constraints)
	# 		res = self.solver.check()
	# 		if res == unsat:
	# 			self.bound = (self.bound << 1)+1
	# 			self.solver.pop()
	# 	if res == sat:
	# 		# Does concolic agree with Z3? If not, it may be due to overflow
	# 		model = self._getModel()
	# 		print("model", model)
	# 		self.solver.pop()
	# 		mismatch = False
	# 		for a in self.asserts:
	# 			eval = self.z3_expr.predToZ3(a,self.solver,model)
	# 			if (not eval):
	# 				mismatch = True
	# 				break
	# 		if (not mismatch):
	# 			a = self.z3_expr.predToZ3(self.query,self.solver,model)
	# 			mismatch = not (not a)
	# 		#print(mismatch)
	# 		return (res,mismatch)
	# 	elif res == unknown:
	# 		self.solver.pop()
	# 	return (res,False)


# def _findModel(self):
# 		if self.use_lia:
# 			self.solver.push()
# 			self.z3_expr = Z3Integer()
# 			self.z3_expr.toZ3(self.solver,self.asserts,self.query)			
# 			res = self.solver.check()
# 			self.solver.pop()
# 			if res == unsat:
# 				return None

# 		# now, go for SAT with bounds
# 		self.N = 32
# 		self.bound = (1 << 4) - 1
# 		while self.N <= 64:
# 			self.solver.push()
# 			(ret,mismatch) = self._findModel2()
# 			if (not mismatch):
# 				break
# 			self.solver.pop()
# 			self.N = self.N+8
# 			if self.N <= 64: print("expanded bit width to "+str(self.N)) 
# 		if ret == unsat:
# 			res = None
# 		elif ret == unknown:
# 			res = None
# 		elif not mismatch or ret == sat:
# 			res = self._getModel()
# 		else:
# 			res = None
# 		if self.N<=64: self.solver.pop()
# 		return res


# 	def _setAssertsQuery(self):
# 		self.z3_expr = Z3BitVector(self.N)
# 		self.z3_expr.toZ3(self.solver,self.asserts,self.query)

# 	def _findModel2(self):
# 		self._setAssertsQuery()
# 		int_vars = self.z3_expr.getIntVars()
# 		res = unsat
# 		while res == unsat and self.bound <= (1 << (self.N-1))-1:
# 			self.solver.push()
# 			constraints = self._boundIntegers(int_vars,self.bound)
# 			self.solver.assert_exprs(constraints)
# 			res = self.solver.check()
# 			if res == unsat:
# 				self.bound = (self.bound << 1)+1
# 				self.solver.pop()
# 		if res == sat:
# 			# Does concolic agree with Z3? If not, it may be due to overflow
# 			model = self._getModel()
# 			print("model", model)
# 			self.solver.pop()
# 			mismatch = False
# 			for a in self.asserts:
# 				eval = self.z3_expr.predToZ3(a,self.solver,model)
# 				if (not eval):
# 					mismatch = True
# 					break
# 			if (not mismatch):
# 				a = self.z3_expr.predToZ3(self.query,self.solver,model)
# 				mismatch = not (not a)
# 			#print(mismatch)
# 			return (res,mismatch)
# 		elif res == unknown:
# 			self.solver.pop()
# 		return (res,False)

# 	def _getModel(self):
# 		res = {}
# 		model = self.solver.model()
# 		print("KEYS ARE", self.z3_expr.z3_vars)
# 		for name in self.z3_expr.z3_vars.keys():
# 			try:
# 				ce = model.eval(self.z3_expr.z3_vars[name])
# 				if isinstance(self.z3_expr.z3_vars[name], SeqRef):
# 					res[name] = ce.as_string()
# 				elif isinstance(self.z3_expr.z3_vars[name], ArithRef):
# 					res[name] = ce.as_long()
# 			except:
# 				pass
# 		return res