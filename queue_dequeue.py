"""A queue (first in, first out) built from linked-list nodes. Used by the /works/queue page.

Named queue_dequeue.py (not queue.py) so it does not clash with Python's own "queue" module.
"""


class Node:
    def __init__(self, value):
        self.value = value      # what is stored
        self.next = None        # the node behind this one in the line


class Queue:
    def __init__(self, max_size=None):
        self.front = None       # the node at the FRONT (leaves first)
        self.rear = None        # the node at the REAR (joined last)
        self.size = 0
        self.max_size = max_size

    def is_empty(self):
        return self.front is None

    def enqueue(self, value):
        """Add a new node at the REAR."""
        if self.max_size is not None and self.size >= self.max_size:
            raise OverflowError(f"The queue is full (this demo holds up to {self.max_size}).")
        node = Node(value)
        if self.rear is None:           # empty queue: the new node is both front and rear
            self.front = node
            self.rear = node
        else:
            self.rear.next = node       # the old rear points to the new node
            self.rear = node            # the new node becomes the rear
        self.size += 1
        return self.size - 1

    def dequeue(self):
        """Remove the node at the FRONT and return its value."""
        if self.front is None:
            raise IndexError("The queue is empty, so there is nothing to dequeue (underflow).")
        removed = self.front
        self.front = removed.next       # the next node becomes the front
        if self.front is None:          # the queue became empty
            self.rear = None
        removed.next = None
        self.size -= 1
        return removed.value

    def peek(self):
        """Look at the FRONT value without removing it."""
        if self.front is None:
            raise IndexError("The queue is empty, so there is nothing to peek at.")
        return self.front.value

    def clear(self):
        self.front = None
        self.rear = None
        self.size = 0

    def to_list(self):
        out, cur = [], self.front
        while cur:
            out.append(cur.value)
            cur = cur.next
        return out


# =====================================================================
#  Used by the web page (app.py calls these)
# =====================================================================
MAX_DEMO_SIZE = 12     # keeps the picture on the page tidy


def create_demo_queue():
    """The queue that is shown when the page first opens."""
    q = Queue(max_size=MAX_DEMO_SIZE)
    for v in ("Job 1", "Job 2", "Job 3"):
        q.enqueue(v)
    return q


def snapshot(q, message, highlight=None, ok=True, removed=None):
    """Everything the page needs to redraw the queue."""
    return {"ok": ok, "message": message, "nodes": q.to_list(), "size": q.size,
            "highlight": highlight, "removed": removed, "max": q.max_size}


def run_operation(q, op, raw_value=""):
    """Run one button (op) on the queue and return a snapshot for the page."""
    value = str(raw_value).strip()
    try:
        if op == "enqueue":
            if not value:
                raise ValueError("Please enter a value to enqueue.")
            i = q.enqueue(value)
            return snapshot(q, f'Enqueued "{value}" at the rear.', i)
        if op == "dequeue":
            v = q.dequeue()
            return snapshot(q, f'Dequeued "{v}" from the front.', removed=v)
        if op == "peek":
            v = q.peek()
            return snapshot(q, f'The front is "{v}" (peek does not remove it).', 0)
        if op == "clear":
            q.clear()
            return snapshot(q, "Queue cleared.")
        return snapshot(q, "Unknown operation.", None, ok=False)
    except (ValueError, IndexError, OverflowError) as e:
        return snapshot(q, str(e), None, ok=False)
