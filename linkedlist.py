"""A simple singly linked list used by the /works/linkedlist page."""


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    # ---------- insertion ----------
    def insert_head(self, value):
        node = Node(value)
        node.next = self.head
        self.head = node
        self.size += 1
        return 0

    def insert_tail(self, value):
        node = Node(value)
        if self.head is None:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node
        self.size += 1
        return self.size - 1

    def insert_at(self, index, value):
        if index < 0 or index > self.size:
            raise IndexError(f"Index {index} is out of range (0 to {self.size}).")
        if index == 0:
            return self.insert_head(value)
        node = Node(value)
        prev = self.head
        for _ in range(index - 1):
            prev = prev.next
        node.next = prev.next
        prev.next = node
        self.size += 1
        return index

    # ---------- deletion ----------
    def delete_at(self, index):
        if self.head is None:
            raise IndexError("The list is empty.")
        if index < 0 or index >= self.size:
            raise IndexError(f"Index {index} is out of range (0 to {self.size - 1}).")
        if index == 0:
            removed = self.head
            self.head = removed.next
        else:
            prev = self.head
            for _ in range(index - 1):
                prev = prev.next
            removed = prev.next
            prev.next = removed.next
        self.size -= 1
        return removed.value

    def delete_value(self, value):
        idx = self.search(value)
        if idx == -1:
            raise ValueError(f'"{value}" was not found in the list.')
        self.delete_at(idx)
        return idx

    # ---------- other operations ----------
    def search(self, value):
        cur, i = self.head, 0
        while cur:
            if cur.value == value:
                return i
            cur, i = cur.next, i + 1
        return -1

    def reverse(self):
        prev, cur = None, self.head
        while cur:
            cur.next, prev, cur = prev, cur, cur.next
        self.head = prev

    def clear(self):
        self.head = None
        self.size = 0

    def to_list(self):
        out, cur = [], self.head
        while cur:
            out.append(cur.value)
            cur = cur.next
        return out
