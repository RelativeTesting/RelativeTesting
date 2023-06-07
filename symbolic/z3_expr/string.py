from z3 import *
from .expression import Z3Expression

class Z3String(Z3Expression):


    def _isIntVar(self,v):
        return isinstance(v,str)
    
    def _variable(self,name,solver):
        return String(name,solver.ctx)

    def _constant(self,v,solver):
        return  StringVal(str(v),solver.ctx)

    # def _mod(self, l, r, solver):
    #     mod_fun = Function('str_mod', StringSort(), StringSort(), StringSort())
    #     return mod_fun(l, r)

    # def _lsh(self, l, r, solver):
    #     lsh_fun = Function('str_lsh', StringSort(), StringSort(), StringSort())
    #     return lsh_fun(l, r)

    # def _rsh(self, l, r, solver):
    #     rsh_fun = Function('str_rsh', StringSort(), StringSort(), StringSort())
    #     return rsh_fun(l, r)

    # def _xor(self, l, r, solver):
    #     xor_fun = Function('str_xor', StringSort(), StringSort(), StringSort())
    #     return xor_fun(l, r)

    # def _or(self, l, r, solver):
    #     or_fun = Function('str_or', StringSort(), StringSort(), StringSort())
    #     return or_fun(l, r)

    # def _and(self, l, r, solver):
    #     and_fun = Function('str_and', StringSort(), StringSort(), StringSort())
    #     return and_fun(l, r)