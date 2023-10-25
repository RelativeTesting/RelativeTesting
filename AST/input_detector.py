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
                                if(str(target.id)  not in self.user_inputs_all):
                                   self.user_inputs_all[target.id]="str"
                    elif child.func.id == 'int':
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                self.user_inputs_all[target.id] ="int"
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
        #self.param_names = ["param" + str(i) for i in range(1, 11)] # Değişken isimleri
        self.count=0

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "input":
            # input fonksiyonunu değiştir
            self.count+=1
            new_name = "param"+str(self.count)
            self.user_inputs[new_name] = str
            new_node=ast.Name(id=new_name, ctx=ast.Load())
            return ast.copy_location(new_node, node)
        else:
            return self.generic_visit(node)


def type_user_inputs(code_file):
    with open(code_file, 'r') as f:
        code = f.read()
    tree = ast.parse(code)
    visitor = InputVisitorDetector()
    visitor.visit(tree)
    with open(code_file[:-3]+"_inputs_types.txt", "w") as file:
        file.write("Our Actual Inputs with Types\n")
        for key, value in visitor.user_inputs_all.items():
            file.write(f"{key}: {value}\n")
    file.close()
    return visitor.user_inputs_all

def detect_user_inputs(code_file):
    with open(code_file, 'r') as f:
        code = f.read()
    tree = ast.parse(code)
    visitor = InputVisitor()
    visitor.visit(tree)
    new_tree=ast.fix_missing_locations(tree)
    my_real_inputs=list(type_user_inputs(code_file).values())
    #print(my_real_inputs)
    function_node = ast.FunctionDef(
    name=code_file[:-3],
    args=ast.arguments(
        args=[ast.arg(arg=list(visitor.user_inputs.keys())[i], annotation=my_real_inputs[i]) for i in range(len(visitor.user_inputs.keys()))],
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
    
    with open("final_file_"+code_file, "w") as f:
        f.write(astor.to_source(function_node))
    f.close()
    with open(code_file[:-3]+"_inputs_types.txt", "a") as file:
        file.write("\nOur Converted Inputs with Types\n")
        for key, value in visitor.user_inputs.items():
            file.write(f"{key}: {value}\n")
    file.close()
    return visitor.user_inputs

file_name=input("Enter your code file name: ")
detect_user_inputs(code_file=file_name)