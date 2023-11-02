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
		
		self.asserts = None
		self.query = None
		
		self.z3_expr = None
		self.pre_asserts = None

	def findCounterexample(self, asserts, query, solution_limit=1):
		"""Tries to find a counterexample to the query while
	  	 asserts remains valid."""
		self.solver = Solver()
		self.query = query
		self.solution_limit = solution_limit
		#self.asserts = self._coneOfInfluence(asserts,query)

		self.asserts = asserts
		print("Asserts",self.asserts)
		print("Query",self.query)
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
		
		self.solver.push()
		self.z3_expr = Z3Integer()
		
		if self.pre_asserts != None:
			pre_asserts = self.z3_expr.preAssertsToZ3(self.pre_asserts, self.solver)
			for assert_expr in pre_asserts:
				self.solver.assert_exprs(assert_expr)

		self.z3_expr.toZ3(self.solver,self.asserts,self.query)		

		print("Solver assertions", self.solver.assertions)

		res = self.solver.check()
		if res == unsat:
			return None

		sol = self._get_solutions()
		models = []
		for i in range(self.solution_limit):
			res = next(sol)
			if res == None:
				break
			print("Solution is ", res)
			model = self._getModel()
			models.append(model)
			print("Model is ", model)
		
		self.solver.pop()
		return models


	def _setAssertsQuery(self):
		self.z3_expr.toZ3(self.solver,self.asserts,self.query)

	def _getModel(self):
		res = {}
		try: 
			#print("Solver assertions2", self.solver.assertions)
			model = self.solver.model()
			#print("Real model is", model)

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
		except:
			print("Error in _getModel")
			return None

	def addPreAsserts(self, pre_asserts):
		self.pre_asserts = pre_asserts
		

	def _get_solutions(self):
		result = self.solver.check()
		# While we still get solutions
		while (result == z3.sat):
			m = self.solver.model()
			yield m
			# Add new solution as a constraint
			block = []
			for var in m:
				block.append(var() != m[var])
			self.solver.add(z3.Or(block))
			# Look for new solution
			result = self.solver.check()


