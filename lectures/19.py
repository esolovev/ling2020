import numpy as np


class MyList:
    def __init__(self):
        self.__items = np.array([])
        self.__length = 0  # кол-во элементов, которое мы добавили в MyList (не в __items)

    def append(self, new_item):
        self.__length += 1
        if len(self.__items) < self.__length:
            zeros = np.zeros(max(1, (self.__length-1)*2))
            for i, item in enumerate(self.__items):  # O(self.__length)
                zeros[i] = item
            self.__items = zeros
        self.__items[self.__length-1] = new_item

    def __str__(self):  # support for str(my_list)
        s = '['
        for i in range(self.__length):
            s += str(self.__items[i]) + " "

        return s.strip() + ']'

    def __setitem__(self, key, value):  # my_list[key] = value
        if key <= self.__length - 1:
            self.__items[key] = value
        else:
            raise IndexError(key)

    def __getitem__(self, key):  # my_list[key]
        if key <= self.__length - 1:
            return self.__items[key]
        else:
            raise IndexError(key)

    def __len__(self):
        return self.__length

    def __iter__(self):  # делаем объект итерируемым через генератор, перечисляющий все значения
        for i in range(self.__length):
            yield self.__items[i]


my_list = MyList()  # self.__length = 0
assert len(my_list) == 0
my_list.append(5)  # self.__length = 1
assert my_list[0] == 5
my_list[0] = 6
print(my_list)
assert my_list[0] == 6
print(my_list[0])
my_list.append(10)  # self.__length = 2
print(my_list)
my_list.append(10)  # self.__length = 4, len(list) = 3
# print(list[3])
print(len(my_list))
assert len(my_list) == 3

print('Перечисляем')
for j in my_list:
    print(j)
