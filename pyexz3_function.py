# Copyright: see copyright.txt

import os
import sys
import logging
import traceback
from optparse import OptionParser

from RelativeTesting.symbolic.loader import *
from RelativeTesting.symbolic.explore import ExplorationEngine

def pyexz3_function(file_path):
	sys.path = [os.path.abspath(os.path.join(os.path.dirname(__file__)))] + sys.path
	sys.path.append(os.path.join(os.path.dirname(__file__), 'RelativeTesting'))
	print(sys.path)
	usage = "usage: %prog [options] <path to a *.py file>"
	parser = OptionParser(usage=usage)

	parser.add_option("-l", "--log", dest="logfile", action="store", help="Save log output to a file", default="")
	parser.add_option("-s", "--start", dest="entry", action="store", help="Specify entry point", default="")
	parser.add_option("-g", "--graph", dest="dot_graph", action="store_true", help="Generate a DOT graph of execution tree")
	parser.add_option("-m", "--max-iters", dest="max_iters", type="int", help="Run specified number of iterations", default=0)
	parser.add_option("-c", "--solution-count", dest="solution_count", type="int", help="Number of solutions to find", default=1)
	parser.add_option("--cvc", dest="cvc", action="store_true", help="Use the CVC SMT solver instead of Z3", default=False)
	parser.add_option("--z3", dest="cvc", action="store_false", help="Use the Z3 SMT solver")
	

	(options, args) = parser.parse_args()
	print("options", options)
	if not (options.logfile == ""):
		logging.basicConfig(filename=options.logfile,level=logging.DEBUG)

	solver = "cvc" if options.cvc else "z3"


	filename = os.path.abspath(file_path)

	# Get the object describing the application
	app = loaderFactory(filename, options.entry)
	print("entry", options)
	if app == None:
		sys.exit(1)

	# Which file is being explored now
	print ("Exploring " + app.getFile() + "." + app.getEntry())

	result = None
	try:
		engine = ExplorationEngine(app.createInvocation(), solver=solver, solution_limit=options.solution_count )
		generatedInputs, returnVals, path = engine.explore(options.max_iters)
		# check the result
		result = app.executionComplete(returnVals)

		# output DOT graph
		if (options.dot_graph):
			file = open(filename+".dot","w")
			file.write(path.toDot())
			file.close()

	except ImportError as e:
		# createInvocation can raise this
		logging.error(e)
		raise e

	if result == None or result == True:
		return True
	else:
		raise("Error: " + result)
