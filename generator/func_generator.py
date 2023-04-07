import os
import re
import datetime
import ast

class InputVisitor(ast.NodeVisitor):
    def __init__(self):
        self.user_inputs = {}

    def visit_Assign(self, node):
        for child in ast.walk(node.value):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id == 'input':
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                print(target.id)
                                if(str(target.id)  not in self.user_inputs):
                                   self.user_inputs[target.id]=str
                    elif child.func.id == 'int':
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                self.user_inputs[target.id] = int
                                break
                    elif child.func.id == 'float':
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                self.user_inputs[target.id] = float
                                break
        self.generic_visit(node)


def detect_user_inputs(code):
    tree = ast.parse(code)
    visitor = InputVisitor()
    visitor.visit(tree)
    return visitor.user_inputs



# current date and time info
now = datetime.datetime.now()
date_time = now.strftime("%Y%m%d_%H%M%S")

input_directory = 'inputs'
output_directory = 'outputs'

# the absolute path
input_directory_path = os.path.abspath(input_directory)

# the files in the desired directory
file_list = os.listdir(input_directory_path)

# the full paths of the files
# file_list = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, file))]

for file_name in file_list:
    file_path = input_directory + "/" + file_name

    # get the lines of the original function
    lines = []
    with open(file_path, 'r') as file:
        contents = file.read()
        lines = contents.splitlines()
    user_inputs = detect_user_inputs(contents)
    # convert input statements to function parameters
    new_params = []
    for param_name, param_type in user_inputs.items():
        new_params.append(f'{param_name}: {param_type.__name__}')
        
    # remove input statements and create function signature
    function_lines = []
    for i, line in enumerate(lines):
        pattern = r'input\s*\((.*?)\)(?![^(]*\))'
        if re.search(pattern, line):
            # skip input lines
            continue
        # indent line
        match = re.match(r'^(\s*)(.*)$', line)
        indentation, content = match.group(1), match.group(2)
        tabbed_line = '\t' + indentation + content
        function_lines.append(tabbed_line)

    # add function signature
    function_lines.insert(0, 'def my_function(' + ', '.join(new_params) + '):')

    # combine lines and return function code
    function_code = '\n'.join(function_lines)


    output_file_path = output_directory + "/" + file_name[:-3] + "_" + date_time + ".py"
    with open(output_file_path, 'w') as modified_file:
        modified_file.write(function_code)
