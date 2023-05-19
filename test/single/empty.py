import z3 
x = z3.String('x')
y = z3.String('y')

s = z3.Solver()

s.add(z3.Length(x) == 6)
s.add(z3.Length(y) == 3)

s.add(z3.IndexOf(x, y, 0) == 0)
s.add(z3.Contains(x, "a*a"))

print(s.check())

m = s.model()

print(m[x])
print(m[y])