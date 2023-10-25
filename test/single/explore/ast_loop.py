import ast
import inspect

def uses_loop(function):
    loop_statements = ast.For, ast.While, ast.AsyncFor

    nodes = ast.walk(ast.parse(inspect.getsource(function)))
    return nodes
    #return any(isinstance(node, loop_statements) for node in nodes)


def dummy_uses_while_loop():
    answer = "yes"
    while answer != "no":

        answer = input("Do you want to listen this song (enter either yes or no): ").lower()

def dummy_uses_for_loop():
    for i in range(10):
        print(i)

res = uses_loop(dummy_uses_while_loop)
for r in res:
    if isinstance(r, ast.For):
        print(r.__dict__)
        print(r.body[0].__dict__)
        print(r.body[0].lineno)
        print(inspect.getsourcelines(dummy_uses_while_loop)[0][r.lineno: r.end_lineno])
    if isinstance(r, ast.While):
        print(r.lineno)
        print(r.__dict__)
        print(inspect.getsourcelines(dummy_uses_while_loop)[0][r.lineno-1: r.end_lineno])
#print(res)