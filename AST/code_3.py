database = input("Please enter the database: ")
database = database.replace(":", ";").replace(",",";").split(";")

painting = database[::3]
movement = database[1::3]
price = database[2::3]

flag = True

movement_ = input("Please enter the movement name that you want to purchase: ")

#Check if entered movement in the database or not.
if movement_ not in movement:
  print("There are no paintings belonging to ", movement_, ".", sep="")

#Create sublists that will contain only the paintings belong to the given movement.
else:
  painting_ = []
  price_ = []

  for indx in range(len(movement)):

    if movement[indx] == movement_:
      painting_.append(painting[indx])
      price_.append(price[indx])

  budget =   float(input("Please enter the amount of money you have (in million): "))
  purchases =  input("Please enter the name of the painting that you want to buy: ")

  #Check if there are multiple purchases or not.
  if "," in purchases:
    purchase_list = purchases.split(",")
    islist = True
    checked = []

    #Displays an error if willing painting is not in database.
    for purchase in range(len(purchase_list)):
      if purchase_list[purchase] not in painting:
        print(purchase_list[purchase]," is not in the database.", sep="")
        flag = False

      #Displays an error if willing painting is not in filtered sublist.
      elif purchase_list[purchase] not in painting_:
        print(purchase_list[purchase]," does not belong to ", movement_, " movement.",sep="")
        flag = False

  #Display an error if the painting is not in database.
  elif purchases not in painting:
    print(purchases,"is not in the database.")
    flag = False

  #Display an error if the painting is not in filtered sublist.
  elif purchases not in painting_:
    print(purchases," does not belong to ", movement_, " movement.",sep="")
    flag = False

  else:
    purchase_list = purchases
    islist=False

  #Calculate the total cost of painting(s).
  if flag:
    total_cost = 0

    if islist:

      for paint in purchase_list:
        indx = painting_.index(paint)
        total_cost += float(price_[indx].replace("M", ""))

    else:
      indx = painting_.index(purchase_list)
      total_cost = float(price_[indx].replace("M", ""))

    #Display that user has purchased his/her items.
    if total_cost <= budget:
      print("You have successfully purchased ", purchases, ".", sep="")

    #Display and error if total cost is higher than your budget.
    else:
      print("Willing painting(s) value(s) are higher than your current budget.")