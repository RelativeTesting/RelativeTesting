import ast

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