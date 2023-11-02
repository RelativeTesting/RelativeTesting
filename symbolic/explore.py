# Copyright: see copyright.txt

from collections import deque
import logging
import os

from .z3_wrap import Z3Wrapper
from .path_to_constraint import PathToConstraint
from .invocation import FunctionInvocation
from .symbolic_types import symbolic_type, SymbolicType

log = logging.getLogger("se.conc")

class ExplorationEngine:
	def __init__(self, funcinv, solver="z3", solution_limit=1):
		self.invocation = funcinv
		self.solution_limit = solution_limit
		# the input to the function
		self.symbolic_inputs = {}  # string -> SymbolicType
		# initialize
		for n in funcinv.getNames():
			self.symbolic_inputs[n] = funcinv.createArgumentValue(n)

		
		#print("init input", self.symbolic_inputs)
		self.constraints_to_solve = deque([])
		self.num_processed_constraints = 0

		self.path = PathToConstraint(lambda c : self.addConstraint(c))
		# link up SymbolicObject to PathToConstraint in order to intercept control-flow


		symbolic_type.SymbolicObject.SI = self.path

		if solver == "z3":
			self.solver = Z3Wrapper()
		elif solver == "cvc":
			from .cvc_wrap import CVCWrapper
			self.solver = CVCWrapper()
		else:
			raise Exception("Unknown solver %s" % solver)

		# outputs
		self.generated_inputs = []
		self.execution_return_values = []

	def addConstraint(self, constraint):
		self.constraints_to_solve.append(constraint)
		# make sure to remember the input that led to this constraint
		constraint.inputs = self._getInputs()

	def explore(self, max_iterations=0):
		if self.invocation.pre_asserts != None and len(self.invocation.pre_asserts) > 0:
			log.info("Adding pre-asserts")
			model = self.solver.findCounterexample(self.invocation.pre_asserts, None , self.solution_limit )
			if model == None:
				log.info("Pre-asserts are unsatisfiable, terminating")
				return self.generated_inputs, self.execution_return_values, self.path
			else:
				for name in model.keys():
					self._updateSymbolicParameter(name,model[name])

		self._oneExecution()
		iterations = 1
		if max_iterations != 0 and iterations >= max_iterations:
			log.debug("Maximum number of iterations reached, terminating")
			return self.execution_return_values
		while not self._isExplorationComplete():
			#print("CONSTRAINTS", self.constraints_to_solve)
			
			selected = self.constraints_to_solve.popleft()
			if selected.processed:
				continue
			self._setInputs(selected.inputs)			

			log.info("Selected constraint %s" % selected)
			asserts, query = selected.getAssertsAndQuery()
			#print("ASSERTS, QUERY", asserts, query)
			self.solver.addPreAsserts(self.invocation.pre_asserts)
			models = self.solver.findCounterexample(asserts, query, self.solution_limit)

			if models == None or len(models) == 0:
				continue
			
			print("models", models)
			for mdl in models[1:]:
				self._recordInputs(mdl)

			model = models[0]
			for name in model.keys():
				self._updateSymbolicParameter(name,model[name])

			self._oneExecution(selected)

			iterations += 1			
			self.num_processed_constraints += 1

			if max_iterations != 0 and iterations >= max_iterations:
				log.info("Maximum number of iterations reached, terminating")
				break

	
		print("self.generated", self.generated_inputs)
		return self.generated_inputs, self.execution_return_values, self.path

	# private

	def _updateSymbolicParameter(self, name, val):
		self.symbolic_inputs[name] = self.invocation.createArgumentValue(name,val)

	def _getInputs(self):
		return self.symbolic_inputs.copy()

	def _setInputs(self,d):
		self.symbolic_inputs = d

	def _isExplorationComplete(self):
		num_constr = len(self.constraints_to_solve)
		#print("num_cons", num_constr)
		if num_constr == 0:
			log.info("Exploration complete")
			return True
		else:
			log.info("%d constraints yet to solve (total: %d, already solved: %d)" % (num_constr, self.num_processed_constraints + num_constr, self.num_processed_constraints))
			return False

	def _getConcrValue(self,v):
		if isinstance(v,SymbolicType):
			return v.getConcrValue()
		else:
			return v

	def _recordInputs(self, args=None):
		if args == None:
			args = self.symbolic_inputs
			inputs = [ (k,self._getConcrValue(args[k])) for k in args ]
			self.generated_inputs.append(inputs)
		else: 
			inputs = [ (k,self._getConcrValue(args[k])) for k in args ]
			for x in self.symbolic_inputs.keys():
				if x not in args:
					inputs.append((x,self._getConcrValue(self.symbolic_inputs[x])))
			self.generated_inputs.append(inputs)
		#print(inputs)
		
	def _oneExecution(self,expected_path=None):
		self._recordInputs()
		self.path.reset(expected_path)
		#print("sym in", self.symbolic_inputs)
		ret = self.invocation.callFunction(self.symbolic_inputs)
		#print(ret, "hello")
		self.execution_return_values.append(ret)

