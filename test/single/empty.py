from z3 import *
x = String('x')
y = String('y')

# z = Int('z')

s = Solver()

cons1 = Not(If(x == StringVal("bbbb"), True, False) )
cons =Not(If(y < StringVal("as"), True, False))

s.assert_exprs([cons1, cons])
#s.add(Length(x) < z)#
#s.add(Length(y) == 3)

#s.add(IndexOf(x, y, 0) == 0)
#s.add(Contains(x, "a*a"))

print(s.assertions())
print(s.check())

m = s.model()
print(m)
print("x", m[x])
print("y", m[y])
# print("z", m[z])



