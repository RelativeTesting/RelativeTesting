import ast
from .predicate import Predicate
from .symbolic_types import SymbolicType

class AstWrapper:
    def __init__(self, constraint_line, arg, arg_constructor, initial_val, type_func) -> None:
        self.constraint_line = constraint_line
        self.arg = arg
        self.arg_constructor = arg_constructor
        self.initial_val = initial_val
        self.type_func = type_func
        self.constraints = []

    def find_constraint(self):
        tree = ast.parse(self.constraint_line)
        expr = self.parse_tree(tree.body[0])
        se = self.arg_constructor("se", 0, expr)
        pred = Predicate(se, True)
        return pred
    
    def parse_tree(self, expr, func=None):
        if isinstance(expr, ast.Expr):
            return self.parse_tree(expr.value)
        elif isinstance(expr, ast.Compare):
            return self.parse_compare(expr)
        elif isinstance(expr, ast.BoolOp):
            return self.parse_boolop(expr)
        elif isinstance(expr, ast.BinOp):
            return self.parse_binop(expr)
        elif isinstance(expr, ast.UnaryOp):
            return self.parse_unaryop(expr)
        elif isinstance(expr, ast.Call):
            return self.parse_call(expr)
        elif isinstance(expr, ast.Name):
            return self.parse_name(expr, func)
        elif isinstance(expr, ast.Constant):
            return self.parse_constant(expr, func)
        elif isinstance(expr, ast.Subscript):
            return self.parse_subscript(expr)
        elif isinstance(expr, ast.Slice):
            return self.parse_slice(expr)
        else:
            print(type(expr).__name__)
            raise NotImplementedError("Weird expression")
        


    def parse_boolop(self, expr):
        if expr.op.__class__.__name__ == "And":
            return self.parse_and(expr)
        elif expr.op.__class__.__name__ == "Or":
            return self.parse_or(expr)
        else:
            raise NotImplementedError("Weird boolop operator")

    def parse_and(self, expr):
        type_func = self.type_func
        pred1 = self.parse_tree(expr.values[0])
        self.type_func = type_func
        pred2 = self.parse_tree(expr.values[1])
        expr = ["&", pred1, pred2]
        return expr
        
    def parse_or(self, expr):
        type_func = self.type_func
        pred1 = self.parse_tree(expr.values[0])
        self.type_func = type_func
        pred2 = self.parse_tree(expr.values[1])
        expr = ["|", pred1, pred2]
        return expr
    
    def parse_subscript(self, expr):
        v = self.parse_tree(expr.value)
        slce = expr.slice
        if isinstance(slce, ast.Constant):
            s = self.parse_tree(slce, int)
            return v[s]
        else:
            l = self.parse_tree(slce.lower, int)
            u = None
            s = None
            if slce.upper != None:
                u = self.parse_tree(slce.upper, int)
            if slce.step != None:
                s = self.parse_tree(slce.step, int)

            print("l", l, "u", u, "s", s)
            if u == None:
                return v[l:]
            elif s == None:
                return v[l:u]
            else:
                return v[l:u:s]
        
    
    def parse_slice(self, expr):
        raise NotImplementedError("Weird slice operator")


    
    def parse_compare(self, expr):
        if expr.ops[0].__class__.__name__ == "Eq":
            return self.parse_eq(expr)
        elif expr.ops[0].__class__.__name__ == "NotEq":
            return self.parse_ne(expr)
        elif expr.ops[0].__class__.__name__ == "Lt":
            return self.parse_lt(expr)
        elif expr.ops[0].__class__.__name__ == "LtE":
            return self.parse_lte(expr)
        elif expr.ops[0].__class__.__name__ == "Gt":
            return self.parse_gt(expr)
        elif expr.ops[0].__class__.__name__ == "GtE":
            return self.parse_gte(expr)
        else:
            raise NotImplementedError("Weird compare operator")

    def parse_eq(self, expr):
        if isinstance(expr.left, ast.Constant):
            val = self.parse_tree(expr.comparators[0])
            st = self.parse_tree(expr.left)
        else:    
            st = self.parse_tree(expr.left)
            val = self.parse_tree(expr.comparators[0])
        if isinstance(val, SymbolicType):
            expr = ["==", st, val]
        else:
            expr = ["==", st, self.type_func(val)]
        return expr
        
    def parse_ne(self, expr):
        if isinstance(expr.left, ast.Constant):
            val = self.parse_tree(expr.comparators[0])
            st = self.parse_tree(expr.left)
        else:    
            st = self.parse_tree(expr.left)
            val = self.parse_tree(expr.comparators[0])
        if isinstance(val, SymbolicType):
            expr = ["!=", st, val]
        else:
            expr = ["!=", st, self.type_func(val)]
        return expr
        
    def parse_lt(self, expr):
        if isinstance(expr.left, ast.Constant):
            val = self.parse_tree(expr.comparators[0])
            st = self.parse_tree(expr.left)
        else:    
            st = self.parse_tree(expr.left)
            val = self.parse_tree(expr.comparators[0])
        if isinstance(val, SymbolicType):
            expr = ["<", st, val]
        else:
            expr = ["<", st, self.type_func(val)]        
        return expr
    
    def parse_lte(self, expr):
        if isinstance(expr.left, ast.Constant):
            val = self.parse_tree(expr.comparators[0])
            st = self.parse_tree(expr.left)
        else:    
            st = self.parse_tree(expr.left)
            val = self.parse_tree(expr.comparators[0])
        if isinstance(val, SymbolicType):
            expr = ["<=", st, val]
        else:
            expr = ["<=", st, self.type_func(val)]
        return expr
    
    def parse_gt(self, expr):
        if isinstance(expr.left, ast.Constant):
            val = self.parse_tree(expr.comparators[0])
            st = self.parse_tree(expr.left)
        else:    
            st = self.parse_tree(expr.left)
            val = self.parse_tree(expr.comparators[0])
        if isinstance(val, SymbolicType):
            expr = [">", st, val]
        else:
            expr = [">", st, self.type_func(val)]
        return expr
    
    def parse_gte(self, expr):
        if isinstance(expr.left, ast.Constant):
            val = self.parse_tree(expr.comparators[0])
            st = self.parse_tree(expr.left)
        else:    
            st = self.parse_tree(expr.left)
            val = self.parse_tree(expr.comparators[0])
        if isinstance(val, SymbolicType):
            expr = [">=", st, val]
        else:
            expr = [">=", st, self.type_func(val)]
        return expr
        
    def parse_name(self, expr, func=None):
        if func:
            return expr.id
        return self.arg_constructor(expr.id , self.initial_val)
    
    def parse_constant(self, expr, func = None):
        if func:
            return func(expr.value)
        return self.type_func(expr.value)

    def parse_binop(self, expr):
        raise NotImplementedError("Weird binop operator")

    def parse_unaryop(self, expr):
        raise NotImplementedError("Weird unaryop operator")

    def parse_call(self, expr):
        func = self.parse_tree(expr.func, True)
        if func == "len":
            param = self.parse_tree(expr.args[0])
            self.type_func = int
            return len(param)
        raise NotImplementedError("Weird call operator")


def do_op(op, left, right):
    match op:
        case "&":
            return left and right
        case "|":
            return left or right
        case "==":
            return left == right
        case "!=":
            return left != right
        case "<":
            return left < right
        case "<=":
            return left <= right
        case ">":
            return left > right
        case ">=":
            return left >= right
        case _:
            return False
