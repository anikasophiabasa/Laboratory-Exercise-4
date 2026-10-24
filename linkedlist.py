"""A simple singly linked list used by the /works/linkedlist page.

The LinkedList class is at the top. The functions at the bottom run the buttons on the page."""


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


# =====================================================================
#  Used by the web page (app.py calls these)
# =====================================================================
def create_demo_list():
    """The list that is shown when the page first opens."""
    ll = LinkedList()
    for v in ("Flask", "Python", "Portfolio"):
        ll.insert_tail(v)
    return ll


def snapshot(ll, message, highlight=None, ok=True):
    """Everything the page needs to redraw the list."""
    return {"ok": ok, "message": message, "nodes": ll.to_list(),
            "size": ll.size, "highlight": highlight}


def run_operation(ll, op, raw_value="", raw_index=""):
    """Run one button (op) on the list and return a snapshot for the page."""
    value = str(raw_value).strip()
    try:
        needs_value = {"insert_head", "insert_tail", "insert_at", "delete_value", "search"}
        if op in needs_value and not value:
            raise ValueError("Please enter a value.")
        if op in {"insert_at", "delete_at"}:
            try:
                index = int(raw_index)
            except (TypeError, ValueError):
                raise ValueError("Please enter a whole number for the index.")

        if op == "insert_head":
            i = ll.insert_head(value); return snapshot(ll, f'Inserted "{value}" at the head.', i)
        if op == "insert_tail":
            i = ll.insert_tail(value); return snapshot(ll, f'Inserted "{value}" at the tail.', i)
        if op == "insert_at":
            i = ll.insert_at(index, value); return snapshot(ll, f'Inserted "{value}" at index {i}.', i)
        if op == "delete_head":
            v = ll.delete_at(0); return snapshot(ll, f'Deleted head node "{v}".')
        if op == "delete_tail":
            v = ll.delete_at(ll.size - 1) if ll.size else ll.delete_at(0)
            return snapshot(ll, f'Deleted tail node "{v}".')
        if op == "delete_at":
            v = ll.delete_at(index); return snapshot(ll, f'Deleted "{v}" at index {index}.')
        if op == "delete_value":
            i = ll.delete_value(value); return snapshot(ll, f'Deleted "{value}" (was at index {i}).')
        if op == "search":
            i = ll.search(value)
            if i == -1:
                return snapshot(ll, f'"{value}" was not found.', None, ok=False)
            return snapshot(ll, f'Found "{value}" at index {i}.', i)
        if op == "reverse":
            ll.reverse(); return snapshot(ll, "List reversed.")
        if op == "clear":
            ll.clear(); return snapshot(ll, "List cleared.")
        return snapshot(ll, "Unknown operation.", None, ok=False)
    except (ValueError, IndexError) as e:
        return snapshot(ll, str(e), None, ok=False)
