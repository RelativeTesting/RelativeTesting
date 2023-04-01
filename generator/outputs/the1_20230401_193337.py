def function():
	take_off_distance = 300 #km
	flight_distance = 384400 #km
	landing_distance = 100 #km
	
	take_off_v = int(input("Please enter the average take-off velocity (m/s): ")) #m/s
	flight_v = int(input("Please enter the average flight velocity (m/s): ")) #m/s
	landing_v = int(input("Please enter the average landing velocity (m/s): ")) #m/s
	
	t1 = take_off_distance*1000 / take_off_v
	t2 = flight_distance*1000 / flight_v
	t3 = landing_distance*1000 / landing_v
	
	total_secs = t1+t2+t3
	#print("Total_secs:", total_secs)
	
	days = total_secs // (24 * 60 * 60)
	total_secs %= (24 * 60 * 60)
	
	hours = total_secs // (60 * 60)
	total_secs %= (60 * 60)
	
	minutes = total_secs // 60
	seconds = total_secs % 60
	
	print("The mission will take", format(days,".0f"),"day(s),", format(hours,".0f"), "hour(s),", format(minutes,".0f"), "minute(s)," , format(seconds,".2f"), "second(s).")