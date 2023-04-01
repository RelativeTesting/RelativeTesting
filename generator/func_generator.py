import os
import re
import datetime

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

    tabbed_lines = []
    tabbed_lines.append("def function(")
    for line in lines:
        match = re.match(r'^(\s*)(.*)$', line)
        indentation, content = match.group(1), match.group(2)
        tabbed_line = '\t' + indentation + content
        tabbed_lines.append(tabbed_line)

    # pattern of an input statement
    pattern = r'input\s*\((.*?)\)(?![^(]*\))'

    count = 1
    for i, line in enumerate(tabbed_lines):

        if re.search(pattern, line):
            parameter_name = f'param{count}' 
            if count == 1:
                tabbed_lines[0] = tabbed_lines[0] + parameter_name
            else:
                tabbed_lines[0] = tabbed_lines[0] + ", " + parameter_name
            tabbed_lines[i] = re.sub(pattern, parameter_name + ")", line)
            count += 1

    # TODO parentheses handling in the input string

    tabbed_lines[0] = tabbed_lines[0] + "):"
    contents = '\n'.join(tabbed_lines)

    output_file_path = output_directory + "/" + file_name[:-3] + "_" + date_time + ".py"
    with open(output_file_path, 'w') as modified_file:
        modified_file.write(contents)
