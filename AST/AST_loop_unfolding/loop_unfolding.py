import ast
import astor

def convert_code_to_function(code):
    tree = ast.parse(code)
    
    new_function = ast.FunctionDef(
        name='new_function',  #function name
        args=ast.arguments(args=[], defaults=[], kwonlyargs=[], kw_defaults=[]),  # Arguments
        body=tree.body,  # Code inside 
        decorator_list=[]  
    )
    tree.body = [new_function]
    return astor.to_source(new_function)
class LoopObject:
    def __init__(self, loop_node, children = []):
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
        #self.children.sort(key=lambda x: x.lineno if isinstance(x, LoopObject) else x.sort_children()[0].lineno)
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
        self.code = [line+"\n" for line in code.split("\n")]
        self.unfold_count = unfold_count

    def find_loop(self):
        nodes = ast.walk(ast.parse(self.coderaw, mode='exec'))
        #print(ast.dump(ast.parse(code, mode='exec')))
        def_node = None
        for node in nodes:
            if isinstance(node, ast.FunctionDef):
                def_node = node
                break
        loops = self.node_consist_loop(def_node)
        #print("loops",loops)
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
            return "".join(self.code[def_node.lineno-1: def_node.end_lineno])
        

        start_func = def_node.lineno
        first_line = self.code[start_func]
        spacing = len(first_line) - len(first_line.lstrip())
        
        s = "".join(self.code[start_func-1])

        for lp in loop_nodes:
            node = lp.loop_node
            if start_func < node.lineno:
                interleaved = self.code[start_func: node.lineno-1]
                interleaved = self.unfold_interleaved(spacing, interleaved)
                s += "".join(interleaved)      
            
            start_func = node.end_lineno
            unfolded = self._unfolding(lp)
            unfolded = ["\t" + line for line in unfolded]
            s += "".join(unfolded)
        
        if start_func < def_node.end_lineno:
            interleaved = self.code[start_func: def_node.end_lineno]
            interleaved = self.unfold_interleaved(spacing, interleaved)
            s += "".join(interleaved)

        return s    
    
    def _unfolding(self, lp):
        if isinstance(lp, LoopObject):
            node = lp.loop_node
    
            if lp.is_leaf():
                codes = []
                cond = self.code[node.lineno-1]

                if isinstance(node, ast.For):
                    pre, cond, past  = self._forloop_helper(cond)
                    codes.append(pre)
                    
                if isinstance(node, ast.While):
                    cond = cond.replace("while", "if")

                cond = cond.lstrip()
                lines = self.code[node.lineno: node.end_lineno]
                first = lines[0]
                
                spacing = len(first) - len(first.lstrip())
                lines = self.unfold_interleaved(spacing, lines)

                for i in range(self.unfold_count):
                    cond_tmp = "\t"*i + cond
                    codes.append(cond_tmp)
                    if isinstance(node, ast.For):
                        codes += ["\t"*(i) + line for line in past]
                    lines_tmp = ["\t"*i + line for line in lines]                 
                    codes += lines_tmp

                assert_cond = cond.replace("if", "assert")
                assert_cond = assert_cond.replace(":", "")
                codes.append(assert_cond)
                return codes
            else:
                codes = []
                cond = self.code[node.lineno-1]
                if isinstance(node, ast.For):
                    pre, cond, past = self._forloop_helper(cond)
                    cond = cond.lstrip()
                    codes.append(cond)
                    codes += past
                elif isinstance(node, ast.While):
                    cond = cond.replace("while", "if")
                    cond = cond.lstrip()  
                    codes.append(cond)
            

                #lp.sort_children()
                start_lineno = node.lineno + 1
                first = self.code[start_lineno -1]
                spacing = len(first) - len(first.lstrip())
                for child in lp.children:
                    if start_lineno < child.loop_node.lineno:
                        interleaved = self.code[start_lineno-1: child.loop_node.lineno-1]
                        interleaved = self.unfold_interleaved(spacing, interleaved)

                        codes += interleaved
                    
                    child_codes = self._unfolding(child)
                    child_codes = ["\t" + line for line in child_codes]
                    codes += child_codes
                    start_lineno = child.loop_node.end_lineno + 1

                
                if start_lineno <= node.end_lineno:
                    last = self.code[start_lineno-1: node.end_lineno]
                    last = self.unfold_interleaved(spacing, last)
                    codes += last
                
                res = []
                if isinstance(node, ast.For):
                    res.append(pre)

                for i in range(self.unfold_count):    
                    tmp = ["\t"*i + line for line in codes]
                    res += tmp
                
                assert_cond = cond.replace("if", "assert")
                assert_cond = assert_cond.replace(":", "")
                res.append(assert_cond)

            return res

    def unfold_interleaved(self, spacing, interleaved):
        interleaved_new = []
        for line in interleaved:
            if line == "\n":
                interleaved_new.append(line)
                continue

            spacing_line = len(line) - len(line.lstrip())
            if spacing_line > spacing:
                new_line = "\t" + line[spacing:]
                interleaved_new.append(new_line)
            else:
                new_line = "\t" + line.lstrip()
                interleaved_new.append(new_line)
        return interleaved_new
    
    def _forloop_helper(self, statement):
        statement = statement.lstrip()
        first = statement[ :statement.find(" ")]
        statement = statement[statement.find(" ")+1: ]
        second = statement[ :statement.find(" ")]
        statement = statement[statement.find(" ")+1: ]
        third = statement[ :statement.find(" ")]
        fourth = statement[statement.find(" ")+1: -2]
        start = 0
        stop = 0
        step = 1
        cond = ""
        pre = ""
        if "range" in fourth:
            fourth = fourth.replace("range", "")
            fourth = fourth.replace("(", "")
            fourth = fourth.replace(")", "")
            fourth = fourth.replace(" ", "")
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
            pre = second + " = " + str(start) + "\n"
            cond = "if " + second + " < " + str(stop) + ":\n"
            past = ["\t" + second + " += " + str(step) + "\n"]
        else:
            idx = second + "_idx"
            pre = idx + " = 0\n"
            cond = "if " + idx + " < len(" + fourth + "):\n"
            past = ["\t" + second + " = " + fourth + "[" + idx + "]\n"] 
            past += ["\t" + idx + " += 1\n"]

        return pre, cond, past

    def __repr__(self): # print the function 
        nodes = ast.walk(ast.parse(self.code, mode='exec'))
        s = ""
        for node in nodes:
            if isinstance(node, ast.FunctionDef):
                lines = self.code[node.lineno-1: node.end_lineno]
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



# lp = LoopUnfolding("test1.py")
# #lp.find_loop()
# print(lp.unfold_loop())
code = "def test1():\n"
code += "\tfor x in 'hello':\n"
code += "\t\tprint(x)\n"

# while x < 10:
code2 = "def test2():\n"
code2 += "\tx = 0\n"
code2 += "\ty = 0\n"
code2 += "\twhile x < 10:\n"
code2 += "\t\tx += 1\n"
code2 += "\t\ty += 1\n"
code2 += "\t\tprint(x, y)\n"

code3 = "for i in range(10):\n"
code3 += "\tx = 1\n"
code3 += "\ty = 1\n"
code3 += "\tprint(x, y)\n"



def conversion_total(code, loopUnfoldingEnabled = False, loop_count = 3):
    code = convert_code_to_function(code)
    if loopUnfoldingEnabled:
        lp = LoopUnfolding(code, loop_count)
        return lp.unfold_loop()
    return code



print(conversion_total(code3, True, 3))