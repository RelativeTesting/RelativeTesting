from z3 import *
# x = String('x')
# y = String('y')

# # z = Int('z')

# s = Solver()

# cons1 = Not(If(x == StringVal("bbbb"), True, False) )
# cons =Not(If(y < StringVal("as"), True, False))

# s.assert_exprs([cons1, cons])
# #s.add(Length(x) < z)#
# #s.add(Length(y) == 3)



# #s.add(IndexOf(x, y, 0) == 0)
# #s.add(Contains(x, "a*a"))

# print(s.assertions())
# print(s.check())

# m = s.model()
# print(m)
# print("x", m[x])
# print("y", m[y])
# # print("z", m[z])


# s = Solver()

# x = z3.Real('x')

# cons1 = If(x > 3.2, True, False)
# cons2 = If(x < 3.9, True, False)

# s.add(cons1)
# s.add(cons2)

# s.check()
# m = s.model()
# print(m)


s = Solver()

x = z3.Array('x', IntSort(), IntSort())

cons1 = If(Length(x) > 4, True, False)

s.add(cons1)

s.check()
m = s.model()
print(m)