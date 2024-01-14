import logging
from optparse import OptionParser

from RelativeTesting.symbolic.loader import *
from RelativeTesting.symbolic.explore import ExplorationEngine


def pyexz3_function(file_path, test_case_count, constraint_input):
    sys.path = [os.path.abspath(os.path.join(os.path.dirname(__file__)))] + sys.path
    sys.path.append(os.path.join(os.path.dirname(__file__), 'RelativeTesting'))
    print(sys.path)
    usage = "usage: %prog [options] <path to a *.py file>"
    parser = OptionParser(usage=usage)

    parser.add_option("-l", "--log", dest="logfile", action="store", help="Save log output to a file", default="")
    parser.add_option("-s", "--start", dest="entry", action="store", help="Specify entry point", default="")
    parser.add_option("-g", "--graph", dest="dot_graph", action="store_true",
                      help="Generate a DOT graph of execution tree")
    parser.add_option("-m", "--max-iters", dest="max_iters", type="int", help="Run specified number of iterations",
                      default=0)
    parser.add_option("--cvc", dest="cvc", action="store_true", help="Use the CVC SMT solver instead of Z3",
                      default=False)
    parser.add_option("--z3", dest="cvc", action="store_false", help="Use the Z3 SMT solver")

    (options, args) = parser.parse_args()
    print("options", options)
    if not (options.logfile == ""):
        logging.basicConfig(filename=options.logfile, level=logging.DEBUG)

    solver = "cvc" if options.cvc else "z3"

    filename = os.path.abspath(file_path)

    # Get the object describing the application
    app = loaderFactory(filename, options.entry)
    print("entry", options)
    if not app:
        print("Unable to load %s" % filename)
        return False

    # Which file is being explored now
    print("Exploring " + app.getFile() + "." + app.getEntry())

    result = None
    try:
        engine = ExplorationEngine(app.createInvocation(), constraint_input, solver=solver, solution_limit=test_case_count)
        generatedInputs, returnVals, path, gpt_ans = engine.explore(options.max_iters)
        # check the result
        result = app.executionComplete(returnVals)

    except ImportError as e:
        # createInvocation can raise this
        logging.error(e)
        return False

    if result == None or result == True:
        return {"PyXZ3": generatedInputs, "ChatGPT": gpt_ans}
    else:
        return False
