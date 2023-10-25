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
        print("hello there", ast.dump(tree))
        pred = self.parse_tree(tree.body[0])
        print(type(pred).__name__, pred)
        return pred
    
    def parse_tree(self, expr):
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
            return self.parse_name(expr)
        elif isinstance(expr, ast.Constant):
            return self.parse_constant(expr)
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
        pred1 = self.parse_tree(expr.values[0])
        pred2 = self.parse_tree(expr.values[1])
        expr = ["&", pred1, pred2]
        se = self.arg_constructor("se", self.initial_val, expr)
        return Predicate(se, do_op("&", pred1.result, pred2.result))
    def parse_or(self, expr):
        pred1 = self.parse_tree(expr.values[0])
        pred2 = self.parse_tree(expr.values[1])
        expr = ["|", pred1, pred2]
        se = self.arg_constructor("se", self.initial_val, expr)
        return Predicate(se, do_op("|", pred1.result, pred2.result))

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
        st = self.parse_tree(expr.left)
        val = self.parse_tree(expr.comparators[0])
        if isinstance(val, SymbolicType):
            expr = ["==", st, val]
        else:
            expr = ["==", st, self.type_func(val)]
        se = self.arg_constructor("se", self.initial_val, expr)
        return Predicate(se, do_op("==", self.initial_val, self.type_func(val)))
    def parse_ne(self, expr):
        st = self.parse_tree(expr.left)
        val = self.parse_tree(expr.comparators[0])
        if isinstance(val, SymbolicType):
            expr = ["!=", st, val]
        else:
            expr = ["!=", st, self.type_func(val)]
        se = self.arg_constructor("se", self.initial_val, expr)
        return Predicate(se, do_op("!=", self.initial_val, self.type_func(val)))
    def parse_lt(self, expr):
        st = self.parse_tree(expr.left)
        val = self.parse_tree(expr.comparators[0])
        if isinstance(val, SymbolicType):
            expr = ["<", st, val]
        else:
            expr = ["<", st, self.type_func(val)]
            
        se = self.arg_constructor("se", self.initial_val, expr)
        return Predicate(se, do_op("<", self.initial_val, self.type_func(val)))
    def parse_lte(self, expr):
        st = self.parse_tree(expr.left)
        val = self.parse_tree(expr.comparators[0])
        if isinstance(val, SymbolicType):
            expr = ["<=", st, val]
        else:
            expr = ["<=", st, self.type_func(val)]
        se = self.arg_constructor("se", self.initial_val, expr)
        return Predicate(se, do_op("<=", self.initial_val, self.type_func(val)))
    def parse_gt(self, expr):
        st = self.parse_tree(expr.left)
        val = self.parse_tree(expr.comparators[0])
        if isinstance(val, SymbolicType):
            expr = [">", st, val]
        else:
            expr = [">", st, self.type_func(val)]
        se = self.arg_constructor("se", self.initial_val, expr)
        return Predicate(se, do_op(">", self.initial_val, self.type_func(val)))
    def parse_gte(self, expr):
        st = self.parse_tree(expr.left)
        val = self.parse_tree(expr.comparators[0])
        if isinstance(val, SymbolicType):
            expr = [">=", st, val]
        else:
            expr = [">=", st, self.type_func(val)]
        se = self.arg_constructor("se", self.initial_val, expr)
        return Predicate(se, do_op(">=", self.initial_val, self.type_func(val)))
        
    def parse_name(self, expr):
        return self.arg_constructor(expr.id , self.initial_val)
    
    def parse_constant(self, expr):
        return self.type_func(expr.value)
    


    def parse_binop(self, expr):
        raise NotImplementedError("Weird binop operator")

    def parse_unaryop(self, expr):
        raise NotImplementedError("Weird unaryop operator")

    def parse_call(self, expr):
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
