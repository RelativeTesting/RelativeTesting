import os
import sys
import inspect
import ast

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
    def __init__(self, file_name, unfold_count=3):
        dir = os.path.dirname(__file__) + '/inputs/'
        sys.path = [ dir ] + sys.path
        
        self.file_name = file_name[:-3]
        self.func = __import__(self.file_name).__dict__[self.file_name]
        self.unfold_count = unfold_count

    def find_loop(self):
        nodes = ast.walk(ast.parse(inspect.getsource(self.func)))
        #print(ast.dump(ast.parse(inspect.getsource(self.func))))
        def_node = None
        for node in nodes:
            if isinstance(node, ast.FunctionDef):
                def_node = node
                break
        loops = self.node_consist_loop(def_node)
        print("loops",loops)
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
            return "".join(inspect.getsourcelines(self.func)[0][def_node.lineno-1: def_node.end_lineno])
        

        start_func = def_node.lineno
        first_line = inspect.getsourcelines(self.func)[0][start_func]
        spacing = len(first_line) - len(first_line.lstrip())
        
        s = "".join(inspect.getsourcelines(self.func)[0][start_func-1])

        for lp in loop_nodes:
            node = lp.loop_node
            if start_func < node.lineno:
                interleaved = inspect.getsourcelines(self.func)[0][start_func: node.lineno-1]
                interleaved = self.unfold_interleaved(spacing, interleaved)
                s += "".join(interleaved)      
            
            start_func = node.end_lineno
            unfolded = self._unfolding(lp)
            unfolded = ["\t" + line for line in unfolded]
            s += "".join(unfolded)
        
        if start_func < def_node.end_lineno:
            interleaved = inspect.getsourcelines(self.func)[0][start_func: def_node.end_lineno]
            interleaved = self.unfold_interleaved(spacing, interleaved)
            s += "".join(interleaved)

        return s    
    
    def _unfolding(self, lp):
        if isinstance(lp, LoopObject):
            node = lp.loop_node
    
            if lp.is_leaf():
                codes = []
                cond = inspect.getsourcelines(self.func)[0][node.lineno-1]
                if isinstance(node, ast.For):
                    cond = cond.replace("for", "if")
                if isinstance(node, ast.While):
                    cond = cond.replace("while", "if")

                cond = cond.lstrip()
                lines = inspect.getsourcelines(self.func)[0][node.lineno: node.end_lineno]
                first = lines[0]
                
                spacing = len(first) - len(first.lstrip())
                lines = self.unfold_interleaved(spacing, lines)

                for i in range(self.unfold_count):
                    cond_tmp = "\t"*i + cond
                    codes.append(cond_tmp)
                    lines_tmp = ["\t"*i + line for line in lines]                 
                    codes += lines_tmp

                return codes
            else:
                codes = []
                cond = inspect.getsourcelines(self.func)[0][node.lineno-1]
                if isinstance(node, ast.For):
                    cond = cond.replace("for", "if")
        
                elif isinstance(node, ast.While):
                    cond = cond.replace("while", "if")
                cond = cond.lstrip()
                
                codes.append(cond)

                #lp.sort_children()
                start_lineno = node.lineno + 1
                first = inspect.getsourcelines(self.func)[0][start_lineno -1]
                spacing = len(first) - len(first.lstrip())
                for child in lp.children:
                    if start_lineno < child.loop_node.lineno:
                        interleaved = inspect.getsourcelines(self.func)[0][start_lineno-1: child.loop_node.lineno-1]
                        interleaved = self.unfold_interleaved(spacing, interleaved)

                        codes += interleaved
                    
                    child_codes = self._unfolding(child)
                    child_codes = ["\t" + line for line in child_codes]
                    codes += child_codes
                    start_lineno = child.loop_node.end_lineno + 1

                
                if start_lineno <= node.end_lineno:
                    last = inspect.getsourcelines(self.func)[0][start_lineno-1: node.end_lineno]
                    last = self.unfold_interleaved(spacing, last)
                    codes += last
                
                res = []
                for i in range(self.unfold_count):    
                    tmp = ["\t"*i + line for line in codes]
                    res += tmp

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
    

    def __repr__(self): # print the function 
        nodes = ast.walk(ast.parse(inspect.getsource(self.func)))
        s = ""
        for node in nodes:
            if isinstance(node, ast.FunctionDef):
                lines = inspect.getsourcelines(self.func)[0][node.lineno-1: node.end_lineno]
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


lp = LoopUnfolding("test3.py")
#lp.find_loop()
print(lp.unfold_loop())
