# Copyright: copyright.txt

import inspect
import re
import os
import sys
from .invocation import FunctionInvocation
from .symbolic_types import SymbolicInteger, getSymbolic, SymbolicStr
from .constraint import Constraint
from .predicate import Predicate
from .ast_wrap import AstWrapper

# The built-in definition of len wraps the return value in an int() constructor, destroying any symbolic types.
# By redefining len here we can preserve symbolic integer types.
import builtins
builtins.len = (lambda x : x.__len__())

class Loader:
	def __init__(self, filename, entry):
		self._fileName = os.path.basename(filename)
		self._fileName = self._fileName[:-3]
		if (entry == ""):
			self._entryPoint = self._fileName
		else:
			self._entryPoint = entry;
		self._resetCallback(True)

	def getFile(self):
		return self._fileName

	def getEntry(self):
		return self._entryPoint
	
	def createInvocation(self):
		inv = FunctionInvocation(self._execute,self._resetCallback)
		func = self.app.__dict__[self._entryPoint]
		argspec = inspect.getfullargspec(func)

		# check to see if user specified types of arguments
		cons_dict = {}
		type_dict = {}
		initial_dict = {}
		if "type_args" in func.__dict__:
			for (p,t) in func.type_args.items():
				if not p in argspec.args:
					print("Error in @types: " +  self._entryPoint + " has no argument named " + f)
					raise ImportError()
				else:
					if t == "int":
						cons_dict[p] = SymbolicInteger
						type_dict[p] = int
						initial_dict[p] = 0
					elif t == "str":
						cons_dict[p] = SymbolicStr
						type_dict[p] = str
						initial_dict[p] = ""
					else:
						print("Error in @types: " +  self._entryPoint + " has no type " + t)
						raise ImportError()
						
		# check to see if user specified initial values of arguments
		if "concrete_args" in func.__dict__:
			for (f,v) in func.concrete_args.items():
				if not f in argspec.args:
					print("Error in @concrete: " +  self._entryPoint + " has no argument named " + f)
					raise ImportError()
				else:
					Loader._initializeArgumentConcrete(inv,f,v)

		# check to see if user specified symbolic values of arguments
		if "symbolic_args" in func.__dict__:
			for (f,v) in func.symbolic_args.items():
				if not f in argspec.args:
					print("Error (@symbolic): " +  self._entryPoint + " has no argument named " + f)
					raise ImportError()
				elif f in inv.getNames():
					print("Argument " + f + " defined in both @concrete and @symbolic")
					raise ImportError()
				else:
					symbolic_constructor = getSymbolic(v)
					if (symbolic_constructor == None):
						print("Error at argument " + f + " of entry point " + self._entryPoint + " : no corresponding symbolic type found for type " + str(type(v)))
						raise ImportError()
					
					if v[0] != "@": # not a constraint
						Loader._initializeArgumentSymbolic(inv, f, v, symbolic_constructor)
					else:
						v = v[1:]
						self._annotationHelper(v, inv, f, type_dict, cons_dict, initial_dict)

		for a in argspec.args:
			if not a in inv.getNames():
				if a in type_dict:
					Loader._initializeArgumentSymbolic(inv, a, initial_dict[a], cons_dict[a])
				else:
					Loader._initializeArgumentSymbolic(inv, a, 0, SymbolicInteger)
		
		return inv

	# need these here (rather than inline above) to correctly capture values in lambda
	def _initializeArgumentConcrete(inv,f,val):
		inv.addArgumentConstructor(f, val, lambda n,v: val)

	def _initializeArgumentSymbolic(inv,f,val,st, type_dict={}):
		inv.addArgumentConstructor(f, val, lambda n,v: st(n,v))

	def executionComplete(self, return_vals):
		if "expected_result" in self.app.__dict__:
			return self._check(return_vals, self.app.__dict__["expected_result"]())
		if "expected_result_set" in self.app.__dict__:
			return self._check(return_vals, self.app.__dict__["expected_result_set"](),False)
		else:
			print(self._fileName + ".py contains no expected_result function")
			return None

	# -- private

	def _resetCallback(self,firstpass=False):
		self.app = None
		if firstpass and self._fileName in sys.modules:
			print("There already is a module loaded named " + self._fileName)
			raise ImportError()
		try:
			if (not firstpass and self._fileName in sys.modules):
				del(sys.modules[self._fileName])
			self.app =__import__(self._fileName)
			if not self._entryPoint in self.app.__dict__ or not callable(self.app.__dict__[self._entryPoint]):
				print("File " +  self._fileName + ".py doesn't contain a function named " + self._entryPoint)
				raise ImportError()
		except Exception as arg:
			print("Couldn't import " + self._fileName)
			print(arg)
			raise ImportError()

	def _execute(self, **args):
		return self.app.__dict__[self._entryPoint](**args)

	def _toBag(self,l):
		bag = {}
		for i in l:
			if i in bag:
				bag[i] += 1
			else:
				bag[i] = 1
		return bag

	def _check(self, computed, expected, as_bag=True):
		b_c = self._toBag(computed)
		b_e = self._toBag(expected)
		if as_bag and b_c != b_e or not as_bag and set(computed) != set(expected):
			print("-------------------> %s test failed <---------------------" % self._fileName)
			print("Expected: %s, found: %s" % (b_e, b_c))
			return False
		else:
			print("%s test passed <---" % self._fileName)
			return True
	
	def _annotationHelper(self, constraint_line, inv, f, type_dict, cons_dict, initial_dict):
		if f in type_dict:
			constructor = cons_dict[f]
			type_func = type_dict[f]
			initial_val = initial_dict[f]
	
			annotation_constraint = AstWrapper(constraint_line, f, constructor, initial_val, type_func)
			predicate = annotation_constraint.find_constraint()
			inv.addPreAsserts(predicate)
		else:
			constructor = SymbolicInteger
			type_func = int
			initial_val = 0

			annotation_constraint = AstWrapper(constraint_line, f, constructor, initial_val, type_func)
			predicate = annotation_constraint.find_constraint()
			inv.addPreAsserts(predicate)
			
			

	
def loaderFactory(filename,entry):
	if not os.path.isfile(filename) or not re.search(".py$",filename):
		print("Please provide a Python file to load")
		return None
	try: 
		dir = os.path.dirname(filename)
		sys.path = [ dir ] + sys.path
		ret = Loader(filename,entry)
		return ret
	except ImportError:
		sys.path = sys.path[1:]
		return None

def do_op(op, left, right):
	match op:
		case ">":
			return left > right
		case "<":
			return left < right
		case ">=":
			return left >= right
		case "<=":
			return left <= right
		case "==":
			return left == right
		case "!=":
			return left != right
		case _:
			return False
