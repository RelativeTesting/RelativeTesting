import openai
import os
from dotenv import load_dotenv
import inspect
import ast
import json
import z3
class Openai_wrap:
    def __init__(self) -> None:
        self.constraints = {}
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def reset(self):
        self.constraints = {}

    def add_constraint(self, constraint, input):
        self.constraints[constraint] = input
        #print("Openai_wrap constraints", self.constraints)
    

    def constraint_prompt(self):
        prompt = "Queries To Be Solved\n"
        for i, constraint in enumerate(self.constraints.keys()):
            c_line = self.simplfy_constraint(constraint)
            prompt += f"Query Start: {c_line} END\n"
            
        return prompt
    
    def simplfy_constraint(self, constraints):
        c_line = ""
        for i, constraint in enumerate(constraints):
            res = self._simplify_constraint(constraint)
            res = res.replace("Not (Not ", "(")

            if i == 0:
                c_line += res
            else:
                c_line += " and " + res
            
        return c_line
            
    
    def _simplify_constraint(self, constraint):
        if z3.is_not(constraint):
            return "(Not " + self._simplify_constraint(constraint.children()[0]) + ")"
        elif z3.is_and(constraint):
            children = constraint.children()
            children = [self._simplify_constraint(child) for child in children]
            return " and ".join(children)
        elif z3.is_or(constraint):
            children = constraint.children()
            children = [self._simplify_constraint(child) for child in children]
            return " or ".join(children)
        elif z3.is_bool(constraint):
            child1, child2 = constraint.children()
            return self._simplify_constraint(child1) + self._simplify_constraint(child2)
        elif isinstance(constraint, z3.ArithRef):
            
            if isinstance(constraint, z3.IntNumRef) or isinstance(constraint, z3.BitVecNumRef) or isinstance(constraint, z3.SeqRef):
                return ""
            if "str" in str(constraint.children()[0]):
                return self._string_helper(str(constraint.children()[0])) 
            return str(constraint.children()[0])
        elif isinstance(constraint, z3.IntNumRef) or isinstance(constraint, z3.BitVecNumRef) or isinstance(constraint, z3.SeqRef):
            return ""
        else:
            return str(constraint)
            
    def _string_helper(self, constraint_line):
        if "str.<" in constraint_line:
            constraint_line = constraint_line.replace("str.<", "")[1:-1].split(",")
            constraint_line = constraint_line[0] + " < " + constraint_line[1]
        elif "str.>" in constraint_line:
            constraint_line = constraint_line.replace("str.>", "")[1:-1].split(",")
            constraint_line = constraint_line[0] + " > " + constraint_line[1]
        elif "str.==" in constraint_line:
            constraint_line = constraint_line.replace("str.==", "")[1:-1].split(",")
            constraint_line = constraint_line[0] + " == " + constraint_line[1]
        elif "str.!=" in constraint_line:
            constraint_line = constraint_line.replace("str.!=", "")[1:-1].split(",")
            constraint_line = constraint_line[0] + " != " + constraint_line[1]
        elif "str.<=" in constraint_line:
            constraint_line = constraint_line.replace("str.<=", "")[1:-1].split(",")
            constraint_line = constraint_line[0] + " <= " + constraint_line[1]
        elif "str.>=" in constraint_line:
            constraint_line = constraint_line.replace("str.>=", "")[1:-1].split(",")
            constraint_line = constraint_line[0] + " >= " + constraint_line[1]
        elif "str.substr" in constraint_line:
            constraint_line = constraint_line.replace("str.substr", "")[1:]
            idx = constraint_line.find(')')
            value = constraint_line[:idx].split(",")
            remain = constraint_line[idx+1:]
            constraint_line = value[0] + "[" + value[1] + "]" + remain



        return constraint_line

    def general_prompt(self, additional_prompt=""):
        return "You are a constraint solver. You are provided with list of queries. Each query is a list of constraints.\n \
                Solve the queries independently and find the parameters that satisfies the constraints in the query.\n \
                Find the parameters such that each constraint in the query should evaluate True.\n \
                Each query will be between 'Query Start:' and 'END' keywords.\n \
                The constraints should be reseted after each query.\n \
                Give the result in JSON format, Do not add explanations.\n \
                If you cannot find parameters to satisfy all the query constraints, simply return {} empty dictionary.\n \
                For each query, return the result that satisfies the constraints in a dictionary format.\n \
                Example: query1_res = {param1: value1, param2: value2, ...}.\n \
                Check the result you provided. If it is not correct, try again.\n \
                There should be exactly one dictionary for each query.\n \
                Another example: if the constraint is '[x > 3, x < 10, y > 5]' the param dictionary should be {x: 4, y: 6}.\n \
                A general example:\n \
                Queries To Be Solved\n \
                Query Start: x > 3 and x < 10 and y > 5 END\n \
                Query Start: x < 3 and y > 8 END\n \
                Query Start: x > 27 and y > 5 and z > 3 END\n \
                You will return the following:\n \
                [{x: 4, y: 6}, {x: 2, y: 9}, {x: 28, y: 6, z: 4}]\n \
                Finally, satisfy the semantic constraints in the additional prompt. Additional prompt: \
                " + additional_prompt
   
    def full_conversation(self, constraint_input):
        
        try:

            system_prompt = self.general_prompt(constraint_input)
            constraint_promt = self.constraint_prompt()

            print("GPT Prompt:",constraint_promt)

            completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": constraint_promt},
            ]
            )
            
            gpt_res = completion.choices[0].message.content
            gpt_res = json.loads(gpt_res)
            combine_gpt = []
            inputs = list(self.constraints.values())

            for i, sol in enumerate(gpt_res):
                if sol == {}:
                    continue
                inpt = inputs[i]
                res = {}
                for key, val in inpt.items():
                    if key in sol:
                        res[key] = sol[key]
                    else:
                        res[key] = val
                combine_gpt.append(res)
                return combine_gpt
        except:
            return []

