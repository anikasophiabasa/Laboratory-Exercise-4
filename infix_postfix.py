"""Infix -> postfix conversion (and finding the value) using a stack.

The stack is the linked-list Stack from stack.py (every item is a Node).
app.py only calls infix_to_postfix() and evaluate_postfix() from this file.
"""
import re

from stack import Stack

PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "^": 3}
TOKEN_RE = re.compile(r"\s*(\d+\.\d+|[A-Za-z0-9]+|\S)")
OPERAND_RE = re.compile(r"\d+\.\d+|[A-Za-z0-9]+")
NUMBER_RE = re.compile(r"\d+(\.\d+)?")


def stack_to_list(stack):
    """Walk the nodes from top to bottom and return their data as a list."""
    items = []
    current = stack.top
    while current:
        items.append(current.data)
        current = current.next
    return items


def infix_to_postfix(expression):
    """Return (postfix_string, steps). Raises ValueError if the expression is not valid."""
    if len(expression) > 200:
        raise ValueError("That expression is too long (200 characters max).")
    tokens = TOKEN_RE.findall(expression)
    if not tokens:
        raise ValueError("Please type an infix expression first, like A+B*C.")

    stack = Stack()
    output = []
    steps = []
    expect_operand = True          # True when the next token must be a value or "("

    def record(token, action):
        steps.append({"token": token, "action": action,
                      "stack": stack_to_list(stack), "output": " ".join(output)})

    for tok in tokens:
        if OPERAND_RE.fullmatch(tok):                      # operand (A, b, 12, 3.5, x1 ...)
            if not expect_operand:
                raise ValueError(f"Two values in a row near '{tok}'. Is an operator missing?")
            output.append(tok)
            expect_operand = False
            record(tok, "Operand → goes straight to the output")

        elif tok == "(":
            if not expect_operand:
                raise ValueError("An operator is missing before '('.")
            stack.push(tok)
            record(tok, "Push '(' onto the stack")

        elif tok == ")":
            if expect_operand:
                raise ValueError("Something is missing before ')'.")
            popped = []
            while stack.peek() is not None and stack.peek() != "(":
                item = stack.pop()
                output.append(item)
                popped.append(item)
            if stack.peek() != "(":
                raise ValueError("Mismatched parentheses: a ')' has no matching '('.")
            stack.pop()                                    # throw away the "("
            moved = ", ".join(popped) if popped else "nothing"
            record(tok, f"Pop {moved} to the output until '(' , then remove '('")

        elif tok in PRECEDENCE:
            if expect_operand:
                raise ValueError(f"The operator '{tok}' needs a value before it.")
            popped = []
            while True:
                top = stack.peek()
                if top is None or top == "(":
                    break
                same = PRECEDENCE[top] == PRECEDENCE[tok]
                # pop higher precedence, or equal precedence (except ^ which goes right-to-left)
                if PRECEDENCE[top] > PRECEDENCE[tok] or (same and tok != "^"):
                    item = stack.pop()
                    output.append(item)
                    popped.append(item)
                else:
                    break
            stack.push(tok)
            expect_operand = True
            action = f"Push '{tok}'"
            if popped:
                action = f"Pop {', '.join(popped)} to the output first, then push '{tok}'"
            record(tok, action)

        else:
            raise ValueError(f"'{tok}' is not allowed. Use letters, numbers, + - * / % ^ and ( ).")

    if expect_operand:
        raise ValueError("The expression ends too early. A value is missing at the end.")

    while stack.peek() is not None:                        # empty the stack at the end
        item = stack.pop()
        if item == "(":
            raise ValueError("Mismatched parentheses: a '(' was never closed.")
        output.append(item)
        record("end", f"No more tokens → pop '{item}' to the output")

    joiner = "" if all(len(x) == 1 for x in output) else " "
    return joiner.join(output), steps, output


def evaluate_postfix(tokens):
    """Evaluate postfix tokens with the same linked-list Stack.
    Returns (value, steps). Only works when every operand is a number."""
    stack = Stack()
    steps = []

    def record(token, action):
        steps.append({"token": token, "action": action, "stack": stack_to_list(stack)})

    def show(n):
        return f"{n:.10g}" if isinstance(n, float) else str(n)

    for tok in tokens:
        if NUMBER_RE.fullmatch(tok):
            stack.push(float(tok) if "." in tok else int(tok))
            record(tok, f"Number → push {tok}")
        else:
            b = stack.pop()                                # the top is the RIGHT side
            a = stack.pop()
            try:
                if tok == "+":
                    r = a + b
                elif tok == "-":
                    r = a - b
                elif tok == "*":
                    r = a * b
                elif tok == "/":
                    r = a / b
                elif tok == "%":
                    r = a % b
                else:                                      # "^"
                    if abs(b) > 1000:
                        raise OverflowError
                    r = a ** b
                if isinstance(r, complex) or abs(r) > 1e300:
                    raise OverflowError
            except ZeroDivisionError:
                raise ValueError("Can't divide by zero, so this expression has no value.")
            except OverflowError:
                raise ValueError("That calculation is too big (or not a real number), so there is no value.")
            stack.push(r)
            record(tok, f"Pop {show(b)} and {show(a)}, calculate {show(a)} {tok} {show(b)} = {show(r)}, push {show(r)}")
    return stack.pop(), steps
