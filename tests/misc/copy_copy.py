import copy
# copy.copy(x) ==> x.dup

old_list = [ [1,1], [2,2], [3,3] ]

new_list = copy.copy(old_list)

new_list[2] = [4,4]
new_list[1][1] = 5

print("old list:", old_list)
print("new list:", new_list)

