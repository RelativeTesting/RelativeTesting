import ast
import random
import re
import astor


def convert_code_to_function(code):
    tree = ast.parse(code)

    new_function = ast.FunctionDef(
        name='new_function',  # function name
        args=ast.arguments(args=[], defaults=[], kwonlyargs=[], kw_defaults=[]),  # Arguments
        body=tree.body,  # Code inside 
        decorator_list=[]
    )
    tree.body = [new_function]
    return astor.to_source(new_function)


class LoopObject:
    def __init__(self, loop_node, children=[]):
        self.loop_node = loop_node
        self.children = children

    def add_child(self, child):
        if child == self:
            return
        if isinstance(child, LoopObject):
            self.children.append(child)
        elif isinstance(child, list):
            for c in child:
                self.add_child(c)

    def copy(self):
        return LoopObject(self.loop_node, self.children.copy())

    def is_leaf(self):
        return self.children == []

    def sort_children(self):
        # self.children.sort(key=lambda x: x.lineno if isinstance(x, LoopObject) else x.sort_children()[0].lineno)
        pass

    def __repr__(self):
        s = ""
        if self.is_leaf():
            s += str(self.loop_node)
        else:
            s += str(self.loop_node)
            for child in self.children:
                s += "\n" + str(child)
        return s


class LoopUnfolding(ast.NodeTransformer):
    def __init__(self, code, unfold_count=3):

        self.coderaw = code
        self.code = [line + "\n" for line in code.split("\n")]
        self.unfold_count = unfold_count

    def find_loop(self):
        nodes = ast.walk(ast.parse(self.coderaw, mode='exec'))
        # print(ast.dump(ast.parse(code, mode='exec')))
        def_node = None
        for node in nodes:
            if isinstance(node, ast.FunctionDef):
                def_node = node
                break
        loops = self.node_consist_loop(def_node)
        # print("loops",loops)
        return def_node, loops

    def node_consist_loop(self, node):
        res = []
        if isinstance(node, ast.For) or isinstance(node, ast.While):

            lp = LoopObject(node, [])
            for child in list(ast.iter_child_nodes(node)):
                tmp = self.node_consist_loop(child)
                if tmp is not None and tmp != []:
                    lp.add_child(tmp)
            res.append(lp)
        else:
            for child in list(ast.iter_child_nodes(node)):
                tmp = self.node_consist_loop(child)
                if tmp is not None and tmp != []:
                    res += tmp
        if res == []:
            return None

        return res

    def unfold_loop(self):
        def_node, loop_nodes = self.find_loop()
        if def_node is None:
            return
        if loop_nodes == [] or loop_nodes == None:
            return "".join(self.code[def_node.lineno - 1: def_node.end_lineno])

        start_func = def_node.lineno

        s = "".join(self.code[start_func - 1])

        for lp in loop_nodes:
            node = lp.loop_node
            if start_func < node.lineno:
                interleaved = self.code[start_func: node.lineno - 1]
                s += "".join(interleaved)

            start_func = node.end_lineno
            unfolded = self._unfolding(lp)
            s += "".join(unfolded)

        if start_func < def_node.end_lineno:
            interleaved = self.code[start_func: def_node.end_lineno]
            s += "".join(interleaved)

        return s

    def _unfolding(self, lp):
        if isinstance(lp, LoopObject):
            node = lp.loop_node

            if lp.is_leaf():
                codes = []
                cond = self.code[node.lineno - 1]

                ## shift of loop
                loop_shift = cond[:len(cond) - len(cond.lstrip())]
                
                print("loop_shift", loop_shift, len(loop_shift))
                i = 0
                first_line = self.code[node.lineno + i]
                while first_line.lstrip() == "":
                    i += 1
                    first_line = self.code[node.lineno + i]

                #shift of first line
                first_line_shift_len = len(first_line) - len(first_line.lstrip())
                first_line_shift = first_line[len(loop_shift):first_line_shift_len]

                if isinstance(node, ast.For):
                    pre, cond, past = self._forloop_helper(cond, loop_shift, first_line_shift)
                    codes.append(pre)

                elif isinstance(node, ast.While):
                    cond = cond.replace("while", "if")
                
                lines = self.code[node.lineno: node.end_lineno]
                lines_new = []
                for line in lines:
                    if line.lstrip() == "":
                        lines_new.append("\n")
                    else:
                        lines_new.append("\t" + loop_shift + line[first_line_shift_len:])
                lines = lines_new
               

                for i in range(self.unfold_count):
                    codes.append("\t" * i + cond)
                    if isinstance(node, ast.For):
                        codes += ["\t" * i + line for line in past]
                    codes += ["\t" * i + line for line in lines]
                    
                assert_cond = cond.replace("if", "assert")
                assert_cond = assert_cond.replace(":", "")
                codes.append(assert_cond)

                return codes
            else:
                codes = []
                cond = self.code[node.lineno - 1]

                ## shift of loop
                loop_shift = cond[:len(cond) - len(cond.lstrip())]
                
                print("loop_shift", loop_shift, len(loop_shift))
                i = 0
                first_line = self.code[node.lineno + i]
                while first_line.lstrip() == "":
                    i += 1
                    first_line = self.code[node.lineno + i]

                #shift of first line
                first_line_shift_len = len(first_line) - len(first_line.lstrip())
                first_line_shift = first_line[len(loop_shift):first_line_shift_len]

                # Type of loop
                if isinstance(node, ast.For):
                    pre, cond, past = self._forloop_helper(cond, loop_shift, first_line_shift)

                elif isinstance(node, ast.While):
                    cond = cond.replace("while", "if")

                codes.append(cond)
                
                start_lineno = node.lineno + 1
                for child in lp.children:
                    if start_lineno < child.loop_node.lineno:
                        interleaved = self.code[start_lineno - 1: child.loop_node.lineno - 1]
                        interleaved_new = []
                        for line in interleaved:
                            if line.lstrip() == "":
                                interleaved_new.append("\n")
                            else:
                                interleaved_new.append("\t" + loop_shift + line[first_line_shift_len:])
                        codes += interleaved_new

                    child_codes = self._unfolding(child)
                    codes += child_codes
                    start_lineno = child.loop_node.end_lineno + 1

                if start_lineno <= node.end_lineno:
                    last = self.code[start_lineno - 1: node.end_lineno]
                    last_new = []
                    for line in last:
                        if line.lstrip() == "":
                            last_new.append("\n")
                        else:
                            last_new.append("\t" + loop_shift + line[first_line_shift_len:])
                    codes += last_new

                res = []
                if isinstance(node, ast.For):
                    res.append(pre)

                for i in range(self.unfold_count):
                    tmp = ["\t" * i + line for line in codes]
                    res += tmp

                assert_cond = cond.replace("if", "assert")
                assert_cond = assert_cond.replace(":", "")
                res.append(assert_cond)

            return res

    def _forloop_helper(self, code, loop_shift, first_line_shift):
        
        statement = code.lstrip()
        first = statement[:statement.find(" ")]
        statement = statement[statement.find(" ") + 1:]
        second = statement[:statement.find(" ")]
        statement = statement[statement.find(" ") + 1:]
        third = statement[:statement.find(" ")]
        fourth = statement[statement.find(" ") + 1: -2]
        start = 0
        stop = 0
        step = 1
        cond = ""
        pre = ""
        if "range" in fourth:
            fourth = fourth.replace("range", "")
            fourth = fourth.replace("(", "")
            fourth = fourth.replace(")", "")
            fourth = fourth.replace(":", "")
            fourth = fourth.split(",")
            fourth = [int(i) for i in fourth]
            if len(fourth) == 1:
                stop = fourth[0]
            elif len(fourth) == 2:
                start = fourth[0]
                stop = fourth[1]
            elif len(fourth) == 3:
                start = fourth[0]
                stop = fourth[1]
                step = fourth[2]
            pre = loop_shift + second + " = " + str(start) + "\n"
            cond = loop_shift + "if " + second + " < " + str(stop) + ":\n"
            print("cond", cond)
            past = ["\t" + loop_shift + second + " += " + str(step) + "\n"]
        else:
            idx = second + "_idx"
            pre = loop_shift + idx + " = 0\n"
            cond = loop_shift + "if " + idx + " < len(" + fourth + "):\n"
            past = ["\t" + loop_shift + second + " = " + fourth + "[" + idx + "]\n"]
            past += ["\t" + loop_shift + idx + " += 1\n"]

        return pre, cond, past

    def __repr__(self):  # print the function
        nodes = ast.walk(ast.parse(self.code, mode='exec'))
        s = ""
        for node in nodes:
            if isinstance(node, ast.FunctionDef):
                lines = self.code[node.lineno - 1: node.end_lineno]
                for line in lines:
                    s += line
        return s

    def print_ast_tree(self, node, indent=0):
        if isinstance(node, ast.AST):
            print('  ' * indent + f'{type(node).__name__}')
            for child_name, child_value in ast.iter_fields(node):
                if isinstance(child_value, list):
                    for child in child_value:
                        self.print_ast_tree(child, indent + 1)
                elif isinstance(child_value, ast.AST):
                    print('  ' * (indent + 1) + f'{child_name}:')
                    self.print_ast_tree(child_value, indent + 2)
                else:
                    print('  ' * (indent + 1) + f'{child_name}: {child_value}')


def check_single_function(code):
    try:
        parsed = ast.parse(code)
        function_count = 0
        for node in ast.walk(parsed):
            if isinstance(node, ast.FunctionDef):
                function_count += 1
                if function_count > 1:  # Birden fazla fonksiyon varsa
                    return False
        return function_count == 1  # Tek fonksiyon varsa True
    except SyntaxError:
        return False


def extract_function_name(code: str):
    function_pattern = r"def\s+([a-zA-Z_][a-zA-Z0-9_]+)\s*\("
    match = re.search(function_pattern, code, re.MULTILINE)
    if match:
        return match.group(1)
    else:
        return None


def conversion_total(code, loop_unfolding_enabled=False, loop_count=3):
    # if it is function get the function name if not generate a function name
    function_name = "wrapper_" + str(random.randint(0, 10000000000))
    if check_single_function(code):
        new_name = extract_function_name(code)
        print("new_name", new_name)
        if new_name:
            function_name = new_name
    else:
        code = convert_code_to_function(code)

    if loop_unfolding_enabled:
        lp = LoopUnfolding(code, loop_count)
        code = lp.unfold_loop()
    return code, function_name


code = """
def func():
    if True:
        for i in range(10):
            x = input()
            print(y)
"""

code1 = """
def func():
    if True:
        x = int(input())
        while x < 10:
            x += 1
            print(x)
"""

code2 = """
def func():
    print("hello")
    for i in range(10):
        print(i)
    
    print("world")

    for i in range(10):
        print(i)

    if True:
        print("hello")
"""

code3 = """
def func():

    print("hello")

    if True:
    
        for x in range(10):
        
            if x > 5:
            
                for y in range(10):
                
                    print(x, y)

            print(x)

    print("world")
"""

code4 = """
def func():
    print("hello")

    
    for x in range(10):
        if x > 5:
            for y in range(10):
                print(x, y)
        print(x)

    print("world")
"""

code4 = """
def func():

    print("zkna1")

    print("zkna2")
    print("zkna3")
    print("zkna4")

    while True:
        print("zkna")
        print("zkna")
        print("zkna")
        print("zkna")
        if "yes" == "yes":
            print("zkna")
            print("zkna")
        print("zkna")
    print("zkna")
    print("zkna")

"""

code5 = """
def func():
    for i in range(5):
    
        print(i)
    if x < 5:
        for i in range(10):
            
            print(i)
    else:
        print("hello")
""" 

code6 = """
def func():
    for i in range(5):
    
        print(i)
""" 


code7 = """
def func():

    print("hello")

    if True:
    
        for x in range(10):
        
            
            for y in range(10):
            
                print(x, y)
                    
            print(x)

    print("world")
"""

code8 = """
x = input()

if x >4:
    print(x)
"""

code9 = """
def func():

    print("hello")

    if True:
    
        for x in range(10):
        
            if x > 5:
                for y in range(10):
                
                    print(x, y)
                    
            print(x)

    print("world")
"""

#print(conversion_total(code9, loopUnfoldingEnabled=True, loop_count=3))