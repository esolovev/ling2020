import typing as tp


class Node:
    def __init__(self, value):
        self.value = value
        self.next: tp.Optional[Node] = None


class LinkedList:
    def __init__(self):
        self.head: tp.Optional[Node] = None
        # self.__length = 0
        # self.tail =

    def append(self, value: int):  # O(длина), можно О(1)
        if self.head is None:
            self.head = Node(value)
            return

        tail = self.head
        while tail.next:  # exists and not None
            tail = tail.next

        tail.next = Node(value)

    def __len__(self):  # O(длина), можно O(1)
        length = 0

        for _ in self:
            length += 1

        return length

    def __iter__(self):
        if self.head is None:
            return

        tail = self.head
        while tail.next:
            yield tail.value
            tail = tail.next
        yield tail.value


# Node(value: 1) -[next]> Node(value: 2) -> Node(value: 3) -> None
#                                            ^[tail]

linked_list = LinkedList()


assert len(linked_list) == 0
linked_list.append(5)
assert len(linked_list) == 1
linked_list.append(6)
assert len(linked_list) == 2
linked_list.append(7)
#

for x in linked_list:
    print(x)
