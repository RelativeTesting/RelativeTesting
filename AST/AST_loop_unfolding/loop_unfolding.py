import ast
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


# the files in the desired directory

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
        if loop_nodes is []:
            return "".join(self.code[def_node.lineno - 1: def_node.end_lineno])

        start_func = def_node.lineno
        first_line = self.code[start_func]
        spacing = len(first_line) - len(first_line.lstrip())

        s = "".join(self.code[start_func - 1])

        for lp in loop_nodes:
            node = lp.loop_node
            if start_func < node.lineno:
                interleaved = self.code[start_func: node.lineno - 1]
                interleaved = self.unfold_interleaved(spacing, interleaved)
                s += "".join(interleaved)

            start_func = node.end_lineno
            unfolded = self._unfolding(lp, spacing)
            unfolded = ["\t" + line for line in unfolded]
            s += "".join(unfolded)

        if start_func < def_node.end_lineno:
            interleaved = self.code[start_func: def_node.end_lineno]
            interleaved = self.unfold_interleaved(spacing, interleaved)
            s += "".join(interleaved)

        return s

    def _unfolding(self, lp, spacing):
        if isinstance(lp, LoopObject):
            node = lp.loop_node

            if lp.is_leaf():
                codes = []
                cond = self.code[node.lineno - 1]

                right_shift = ""
                if len(cond) - len(cond.lstrip()) > spacing:
                    right_shift = cond[spacing:len(cond) - len(cond.lstrip())]

                if isinstance(node, ast.For):
                    pre, cond, past = self._forloop_helper(cond, right_shift)
                    codes.append(pre)

                if isinstance(node, ast.While):
                    cond = cond.replace("while", "if")
                    cond = cond.lstrip()
                    cond = right_shift + cond
                
                lines = self.code[node.lineno: node.end_lineno]
                first = lines[0]

                spacing2 = len(first) - len(first.lstrip())
                lines = self.unfold_interleaved(spacing2, lines, right_shift)

                for i in range(self.unfold_count):
                    cond_tmp = "\t" * i + cond
                    codes.append(cond_tmp)
                    if isinstance(node, ast.For):
                        codes += ["\t" * (i) + line for line in past]
                    lines_tmp = ["\t" * i + line for line in lines]
                    codes += lines_tmp

                assert_cond = cond.replace("if", "assert")
                assert_cond = assert_cond.replace(":", "")
                codes.append(assert_cond)
                return codes
            else:
                codes = []
                cond = self.code[node.lineno - 1]

                right_shift = ""
                if len(cond) - len(cond.lstrip()) > spacing:
                    right_shift = cond[spacing:len(cond) - len(cond.lstrip())]

                if isinstance(node, ast.For):
                    pre, cond, past = self._forloop_helper(cond, right_shift)
                    codes.append(cond)
                    codes += past
                elif isinstance(node, ast.While):
                    cond = cond.replace("while", "if")
                    cond = cond.lstrip()
                    cond = right_shift + cond
                    codes.append(cond)

                # lp.sort_children()
                start_lineno = node.lineno + 1
                first = self.code[start_lineno - 1]
                print("first", first)
                spacing = len(first) - len(first.lstrip())
                for child in lp.children:
                    if start_lineno < child.loop_node.lineno:
                        interleaved = self.code[start_lineno - 1: child.loop_node.lineno - 1]
                        interleaved = self.unfold_interleaved(spacing, interleaved, right_shift)

                        codes += interleaved

                    child_codes = self._unfolding(child, spacing)
                    child_codes = ["\t" + right_shift + line for line in child_codes]
                    codes += child_codes
                    start_lineno = child.loop_node.end_lineno + 1

                if start_lineno <= node.end_lineno:
                    last = self.code[start_lineno - 1: node.end_lineno]
                    last = self.unfold_interleaved(spacing, last, right_shift)
                    codes += last

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

    def unfold_interleaved(self, spacing, interleaved, shift=""):
        interleaved_new = []
        for line in interleaved:
            if line == "\n":
                interleaved_new.append(line)
                continue

            spacing_line = len(line) - len(line.lstrip())
            if spacing_line > spacing:
                new_line = "\t" + shift +  line[spacing:]
                interleaved_new.append(new_line)
            else:
                new_line = "\t" + shift + line.lstrip()
                interleaved_new.append(new_line)
        return interleaved_new

    def _forloop_helper(self, statement, shift):
        statement = statement.lstrip()
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
            pre = shift + second + " = " + str(start) + "\n"
            cond = shift + "if " + second + " < " + str(stop) + ":\n"
            print("cond", cond)
            past = ["\t" + shift + second + " += " + str(step) + "\n"]
        else:
            idx = second + "_idx"
            pre = shift + idx + " = 0\n"
            cond = shift + "if " + idx + " < len(" + fourth + "):\n"
            past = ["\t" + shift  + second + " = " + fourth + "[" + idx + "]\n"]
            past += ["\t" + shift + idx + " += 1\n"]

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


def conversion_total(code, loopUnfoldingEnabled=False, loop_count=3):
    if not check_single_function(code):
        code = convert_code_to_function(code)

    if loopUnfoldingEnabled:
        lp = LoopUnfolding(code, loop_count)
        return lp.unfold_loop()
    return code


# code = """
# def func():
#     if True:
#         for i in range(10):
#             x = input()
#             print(y)
# """

# code1 = """
# def func():
#     if True:
#         x = int(input())
#         while x < 10:
#             x += 1
#             print(x)
# """

# code2 = """
# def func():
#     print("hello")
#     for i in range(10):
#         print(i)
    
#     print("world")

#     for i in range(10):
#         print(i)

#     if True:
#         print("hello")
# """

# code3 = """
# def func():
#     print("hello")

#     if True:
#         for x in range(10):
#             if x > 5:
#                 for y in range(10):
#                     print(x, y)
#             print(x)

#     print("world")
# """

# code4 = """
# def func():
#     print("hello")

    
#     for x in range(10):
#         if x > 5:
#             for y in range(10):
#                 print(x, y)
#         print(x)

#     print("world")
# """

# code4 = """
# def func():

#     print("zkna1")

#     print("zkna2")
#     print("zkna3")
#     print("zkna4")

#     while True:
#         print("zkna")
#         print("zkna")
#         print("zkna")
#         print("zkna")
#         if "yes" == "yes":
#             print("zkna")
#             print("zkna")
#         print("zkna")
#     print("zkna")
#     print("zkna")

# """


# print(conversion_total(code4, loopUnfoldingEnabled=True, loop_count=3))