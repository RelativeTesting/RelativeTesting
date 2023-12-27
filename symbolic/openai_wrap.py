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
            return "Not (" + self._simplify_constraint(constraint.children()[0]) + ")"
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
            return str(constraint.children()[0])
        elif isinstance(constraint, z3.IntNumRef) or isinstance(constraint, z3.BitVecNumRef) or isinstance(constraint, z3.SeqRef):
            return ""
        else:
            return str(constraint)
            
    
    def general_prompt(self):
        return "You are a constraint solver. You will be provided with list of queries. Each query is a list of constraints. \
                You will solve the queries independently and find the parameters that satisfies the constraints in the query. \
                You need to find the parameters such that each constraint in the query should evaluate True. There can be multiple parameters for each query. \
                Give the result in JSON format, Do not add explanations. \
                Each query will be between 'Query Start:' and 'END' keywords. \
                The constraints should be reseted after each query.\
                If you cannot find parameters to satisfy all the query constraints, simply return None \
                If you can solve the query constraints, return the parameters that satisfies ALL the constraints. \
                For each query, return the result that satisfies the constraints in a dictionary format. \
                Each result of a query should be in the following format: query1_res = {param1: value1, param2: value2, ...} \
                Always check the result you provided. If it is not correct, try again. \
                There should be exactly one dictionary for each query. \
                A result dictionary should contain all the parameters in the query. \
                For example, if the constraint is '[x > 3, x < 10, y > 5]' the param dictionary should be {x: 4, y: 6}. \
                You will be provided with list of queries. \
                Overall result should be in the following format: [query1_res, query2_res, ...] \
                A general example: \
                Queries To Be Solved \
                Query 0: [x > 3 and x < 10, y > 5] \
                Query 1: [x < 3, y > 8] \
                Query 2: [x > 27, y > 5, z > 3] \
                You will return the following: \
                [{x: 4, y: 6}, {x: 2, y: 9}, {x: 28, y: 6, z: 4}] \
                "
   
    def full_conversation(self):
        system_prompt = self.general_prompt()
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
            if sol == None:
                continue
            inpt = inputs[i]
            res = {}
            for key, val in inpt.items():
                if key in sol:
                    res[key] = sol[key]
                else:
                    res[key] = val
            combine_gpt.append(res)
        
        
        #print("GPT Result:", combine_gpt)

        return combine_gpt
