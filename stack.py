class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Stack:
    def __init__(self):
        self.top = None

    def push(self, data):
        new_node = Node(data)
        if self.top:
            new_node.next = self.top
        self.top = new_node


    def pop(self):
        if self.top is None:
            return None
        else:
            popped_node = self.top
            self.top = self.top.next
            popped_node.next = None
            return popped_node.data

    def peek(self):
        if self.top:
            return self.top.data
        else:
            return None


    def print_stack(self):
        if self.top is None:
            print("Stack is empty")
        else:
            current = self.top
            print("Stack elements (top → bottom):")
            while current:
                print(current.data)
                current = current.next


if __name__ == "__main__":
    # Create an empty stack
    stack = Stack()
    stack.print_stack()

    # Push some elements onto the stack
    stack.push(10)
    stack.push(20)
    stack.push(30)
    stack.print_stack()

    # Peek at the top element without removing it
    print("Top element:", stack.peek())

    # Pop elements off the stack
    print("Popped:", stack.pop())
    print("Popped:", stack.pop())
    stack.print_stack()

    # Pop the last element, then try popping from an empty stack
    print("Popped:", stack.pop())
    print("Popped from empty stack:", stack.pop())
    print("Peek on empty stack:", stack.peek())
    stack.print_stack()


