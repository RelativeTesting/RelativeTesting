import ast
import astor


class InputVisitorDetector(ast.NodeVisitor):
    def __init__(self):
        self.user_inputs_all = {}

    def visit_Assign(self, node):
        for child in ast.walk(node.value):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id == 'input':
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                print(target.id)
                                if (str(target.id) not in self.user_inputs_all):
                                    self.user_inputs_all[target.id] = "str"
                    elif child.func.id == 'int':
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                self.user_inputs_all[target.id] = "int"
                                break
                    elif child.func.id == 'float':
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                self.user_inputs_all[target.id] = "float"
                                break
        self.generic_visit(node)


class InputVisitor(ast.NodeTransformer):
    def __init__(self):
        self.user_inputs = {}
        # self.param_names = ["param" + str(i) for i in range(1, 11)] # Değişken isimleri
        self.count = 0

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "input":
            # input fonksiyonunu değiştir
            self.count += 1
            new_name = "param" + str(self.count)
            self.user_inputs[new_name] = str
            new_node = ast.Name(id=new_name, ctx=ast.Load())
            return ast.copy_location(new_node, node)
        else:
            return self.generic_visit(node)


import ast


class RemoveTypeConversions(ast.NodeTransformer):
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in ("int", "float", "str"):
            # int(param), float(param), veya str(param) gibi ifadeleri kaldır
            if isinstance(node.args[0], ast.Name):
                param_name = node.args[0].id
                return ast.copy_location(ast.Name(id=param_name, ctx=ast.Load()), node)
        return self.generic_visit(node)


def type_user_inputs(code_string):
    code = code_string
    tree = ast.parse(code)
    visitor = InputVisitorDetector()
    visitor.visit(tree)
    return visitor.user_inputs_all

def detect_user_inputs(code_string, function_name, destination_folder):
    code = code_string
    tree = ast.parse(code)
    visitor = InputVisitor()
    visitor.visit(tree)
    new_tree1 = ast.fix_missing_locations(tree)
    transformer = RemoveTypeConversions()
    new_tree = transformer.visit(new_tree1)
    new_tree = ast.fix_missing_locations(new_tree)
    my_real_inputs = list(type_user_inputs(code_string).values())
    print(my_real_inputs)
    function_node = ast.FunctionDef(
    name= function_name +"_final",
    args=ast.arguments(
        args=[ast.arg(arg=list(visitor.user_inputs.keys())[i], annotation=None) for i in range(len(visitor.user_inputs.keys()))],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[]
    ),
    body=new_tree.body,
    decorator_list=[],
    returns=None
)
    
    with open(destination_folder + function_name +'_final.py', "w") as f:
        f.write(astor.to_source(function_node))
    return visitor.user_inputs

