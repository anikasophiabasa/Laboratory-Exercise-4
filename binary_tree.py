"""A binary tree for the /works/binarytree page (from the Trees lesson)."""
from collections import deque


class Node:
    """A node in a binary tree."""
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


class BinaryTree:
    """A binary tree data structure."""
    def __init__(self, root_value=None):
        self.root = Node(root_value) if root_value is not None else None

    # ---------- insert ----------
    def insert_left(self, current_node, value):
        if current_node.left is None:
            current_node.left = Node(value)
        else:
            new_node = Node(value)
            new_node.left = current_node.left      # the old left child moves down
            current_node.left = new_node

    def insert_right(self, current_node, value):
        if current_node.right is None:
            current_node.right = Node(value)
        else:
            new_node = Node(value)
            new_node.right = current_node.right    # the old right child moves down
            current_node.right = new_node

    # ---------- traversals ----------
    def preorder_traversal(self, start, traversal):
        if start:
            traversal += (str(start.value) + " ")
            traversal = self.preorder_traversal(start.left, traversal)
            traversal = self.preorder_traversal(start.right, traversal)
        return traversal

    def inorder_traversal(self, start, traversal):
        if start:
            traversal = self.inorder_traversal(start.left, traversal)
            traversal += (str(start.value) + " ")
            traversal = self.inorder_traversal(start.right, traversal)
        return traversal

    def postorder_traversal(self, start, traversal):
        """Left, right, root."""
        if start:
            traversal = self.postorder_traversal(start.left, traversal)
            traversal = self.postorder_traversal(start.right, traversal)
            traversal += (str(start.value) + " ")
        return traversal

    post_traversal = postorder_traversal   # the lab calls it post_traversal

    # ---------- search ----------
    def search(self, root, key):
        """Return the node that holds key, or None."""
        if root is None:
            return None
        if root.value == key:
            return root
        found = self.search(root.left, key)
        if found:
            return found
        return self.search(root.right, key)

    # ---------- delete ----------
    def delete_node(self, root, key):
        """Delete the node with key and return the root.
        Copy the deepest, right-most node's value into the target, then remove that deepest node."""
        if root is None:
            return None
        if root.left is None and root.right is None:          # single-node tree
            return None if root.value == key else root

        target, deepest, parent = None, None, None
        queue = deque([(root, None)])                          # level order: (node, parent)
        while queue:
            deepest, parent = queue.popleft()
            if deepest.value == key and target is None:
                target = deepest
            if deepest.left:
                queue.append((deepest.left, deepest))
            if deepest.right:
                queue.append((deepest.right, deepest))

        if target is None:                                     # key not found
            return root
        target.value = deepest.value                           # copy the deepest value up
        if parent.right is deepest:                            # cut the deepest node off
            parent.right = None
        else:
            parent.left = None
        return root


# =====================================================================
#  Used by the web page (app.py calls these)
# =====================================================================
MAX_NODES = 15


def create_demo_tree():
    """The tree from the lesson slides."""
    tree = BinaryTree("R")
    tree.insert_left(tree.root, "A")
    tree.insert_right(tree.root, "B")
    tree.insert_left(tree.root.left, "C")
    tree.insert_right(tree.root.left, "D")
    tree.insert_left(tree.root.right, "E")
    tree.insert_right(tree.root.right, "F")
    tree.insert_left(tree.root.right.right, "G")
    return tree


def to_dict(node):
    if node is None:
        return None
    return {"value": node.value, "left": to_dict(node.left), "right": to_dict(node.right)}


def count_nodes(node):
    return 0 if node is None else 1 + count_nodes(node.left) + count_nodes(node.right)


def height(node):
    return 0 if node is None else 1 + max(height(node.left), height(node.right))


def snapshot(tree, message, ok=True, highlight=None, path=None, order=None):
    return {"ok": ok, "message": message, "tree": to_dict(tree.root),
            "size": count_nodes(tree.root), "height": height(tree.root),
            "highlight": highlight, "path": path or [], "order": order or []}


def search_path(tree, key):
    """Visit nodes in preorder until key is found. Returns (visited, found)."""
    visited, found = [], False

    def walk(node):
        nonlocal found
        if node is None or found:
            return
        visited.append(node.value)
        if node.value == key:
            found = True
            return
        walk(node.left)
        walk(node.right)

    walk(tree.root)
    return visited, found


def run_operation(tree, op, raw_value="", raw_parent=""):
    """Run one button on the tree and return a snapshot for the page."""
    value, parent = str(raw_value).strip(), str(raw_parent).strip()
    try:
        if op in ("preorder", "inorder", "postorder"):
            if tree.root is None:
                raise ValueError("The tree is empty.")
            text = getattr(tree, op + "_traversal")(tree.root, "").split()
            names = {"preorder": "root, left, right", "inorder": "left, root, right",
                     "postorder": "left, right, root"}
            return snapshot(tree, f"{op.capitalize()} ({names[op]}): {' '.join(text)}", order=text)

        if op == "clear":
            tree.root = None
            return snapshot(tree, "Tree cleared. Type a value and press “Set root” to start a new one.")
        if op == "reset":
            tree.root = create_demo_tree().root
            return snapshot(tree, "Tree reset to the one from the lesson.")

        if not value:
            raise ValueError("Please enter a value.")

        if op == "set_root":
            if tree.root is not None:
                raise ValueError("The tree already has a root. Insert under a parent, or clear the tree first.")
            tree.root = Node(value)
            return snapshot(tree, f'"{value}" is now the root.', highlight=value)

        if op in ("insert_left", "insert_right"):
            if tree.root is None:
                raise ValueError("The tree is empty. Press “Set root” first.")
            if not parent:
                raise ValueError("Please enter the parent value (or click a node in the tree).")
            if count_nodes(tree.root) >= MAX_NODES:
                raise ValueError(f"This demo holds up to {MAX_NODES} nodes so the drawing stays readable.")
            if tree.search(tree.root, value):
                raise ValueError(f'"{value}" is already in the tree. Use a different value.')
            node = tree.search(tree.root, parent)
            if node is None:
                raise ValueError(f'Parent "{parent}" was not found in the tree.')
            side = "left" if op == "insert_left" else "right"
            pushed = getattr(node, side) is not None
            getattr(tree, op)(node, value)
            extra = f" The old {side} child moved down under it." if pushed else ""
            return snapshot(tree, f'Inserted "{value}" as the {side} child of "{parent}".{extra}', highlight=value)

        if op == "search":
            visited, found = search_path(tree, value)
            if tree.search(tree.root, value) is None:
                return snapshot(tree, f'"{value}" was not found (checked {len(visited)} nodes).',
                                ok=False, path=visited)
            return snapshot(tree, f'Found "{value}" after visiting {len(visited)} node(s): {" → ".join(visited)}.',
                            highlight=value, path=visited)

        if op == "delete":
            if tree.search(tree.root, value) is None:
                raise ValueError(f'"{value}" was not found, so nothing was deleted.')
            tree.root = tree.delete_node(tree.root, value)
            return snapshot(tree, f'Deleted "{value}". The deepest, right-most node took its place so the tree stays connected.')

        return snapshot(tree, "Unknown operation.", ok=False)
    except ValueError as e:
        return snapshot(tree, str(e), ok=False)