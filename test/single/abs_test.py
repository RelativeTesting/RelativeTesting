def abs_test(a,b):
	print("check smart move1")
	if (a < 0):
		if (abs(a) == b):
			return 0
		return 1
	print("check smart move2")
	return 2

def expected_result():
	return [0,1,2]

