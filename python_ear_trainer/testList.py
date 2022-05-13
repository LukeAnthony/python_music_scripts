listOne = [1, 300, 2, 3]
listTwo = [x for x in listOne]

listTwo.pop(1)

print(listOne)
print(listTwo)

print(set(listOne).symmetric_difference(set(listTwo)).pop())