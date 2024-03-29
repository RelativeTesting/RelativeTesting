# Copyright: see copyright.txt

from collections import deque
import logging
import os

from .z3_wrap import Z3Wrapper
from .path_to_constraint import PathToConstraint
from .constraint import Constraint
from .predicate import Predicate
from .invocation import FunctionInvocation
from .symbolic_types import SymbolicInteger, SymbolicStr
from .symbolic_types import symbolic_type, SymbolicType
from .openai_wrap import Openai_wrap

log = logging.getLogger("se.conc")

class ExplorationEngine:
	def __init__(self, funcinv, constraint_input, solver="z3", solution_limit=1):
		self.invocation = funcinv
		self.solution_limit = solution_limit
		self.constraint_input = constraint_input
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
			self.openai_wrap = Openai_wrap()
			self.solver = Z3Wrapper(self.openai_wrap)
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
			model = self.solver.findCounterexample(self.invocation.pre_asserts, None , self.symbolic_inputs, self.solution_limit )
			if model == None:
				log.info("Pre-asserts are unsatisfiable, terminating")
				return self.generated_inputs, self.execution_return_values, self.path, []
			else:
				for name in model[0].keys():
					self._updateSymbolicParameter(name,model[0][name])

		self._oneExecution()
		iterations = 1
		if max_iterations != 0 and iterations >= max_iterations:
			log.debug("Maximum number of iterations reached, terminating")
			return [], self.execution_return_values, self.path, []
		while not self._isExplorationComplete():
			selected = self.constraints_to_solve.popleft()
			if selected.processed:
				continue
			self._setInputs(selected.inputs)			

			log.info("Selected constraint %s" % selected)
			asserts, query = selected.getAssertsAndQuery()
			#print("ASSERTS, QUERY", asserts, query)
			self.solver.addPreAsserts(self.invocation.pre_asserts)
			models = self.solver.findCounterexample(asserts, query, self.symbolic_inputs, self.solution_limit)

			if models == None or len(models) == 0:
				continue
			
			#print("models", models)
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

		#gptRes = None
		gptRes = self.openai_wrap.full_conversation(self.constraint_input) 
		generetadInputs = []
		for i in range(len(self.generated_inputs)):
			lst = self.generated_inputs[i]
			d = {}
			for j in range(len(lst)):
				d[lst[j][0]] = lst[j][1]
			generetadInputs.append(d)
		print("generetadInputs", generetadInputs)
		print("gptRes", gptRes)
		return generetadInputs, self.execution_return_values, self.path, gptRes

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
		try:
			self._recordInputs()
			self.path.reset(expected_path)
			ret = self.invocation.callFunction(self.symbolic_inputs)
			
			self.execution_return_values.append(ret)
		except:
			self.generated_inputs.pop()
			print("Unexpected error:")
			self.createFailedInputConstraint()
	
	#Creates assertion based on execution failure
	def createFailedInputConstraint(self):
		
		symbolic_expressions = []
		for k in self.symbolic_inputs.keys():
			arg_cons  = self.findArgCons(self.symbolic_inputs[k].getConcrValue())
			st = arg_cons(k, self.symbolic_inputs[k].getConcrValue())
			expr = ["==", st, self.symbolic_inputs[k].getConcrValue()]
			se = arg_cons("se", 0, expr)
			symbolic_expressions.append(se)
		
		se = symbolic_expressions[0]
		for i in range(1, len(symbolic_expressions)):
			expr = ["&", se, symbolic_expressions[i]]
			se = SymbolicInteger("se", 0, expr)
			
		pred = Predicate(se, False)
		self.solver.addFailedInputPred(pred)
		models = self.solver.findCounterexample(None, None, self.symbolic_inputs, self.solution_limit)
		if models == None or len(models) == 0:
			return
			

		model = models[0]
		for name in model.keys():
			self._updateSymbolicParameter(name,model[name])

		self._oneExecution()

		
		
		
	def findArgCons(self, val):
		if isinstance(val, int):
			return SymbolicInteger
		elif isinstance(val, str):
			return SymbolicStr
		return SymbolicInteger

