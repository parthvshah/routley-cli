"""
Doubly linked list implementation for the shopping list.
"""


class Node:
    def __init__(self, item: str, checked: bool = False):
        self.item = item
        self.checked = checked
        self.prev: "Node | None" = None
        self.next: "Node | None" = None

    def __repr__(self):
        return f"Node({self.item!r}, checked={self.checked})"


class DoublyLinkedList:
    def __init__(self):
        self.head: Node | None = None
        self.tail: Node | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        current = self.head
        while current:
            yield current
            current = current.next

    # ------------------------------------------------------------------ #
    # Internal node manipulation                                           #
    # ------------------------------------------------------------------ #

    def _insert_before(self, anchor: Node, new_node: Node) -> None:
        """Insert new_node immediately before anchor."""
        new_node.next = anchor
        new_node.prev = anchor.prev
        if anchor.prev:
            anchor.prev.next = new_node
        else:
            self.head = new_node
        anchor.prev = new_node

    def _append_node(self, node: Node) -> None:
        """Append node at the tail."""
        if self.tail is None:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node

    def _unlink(self, node: Node) -> None:
        """Remove node from the chain without freeing it."""
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = node.next = None

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def insert_sorted(self, item: str, learned_positions: dict[str, float]) -> Node:
        """
        Insert a new node in ascending order of learned store positions.
        Items with no learned position are treated as infinity (appended last).
        Items with equal position are inserted after existing equal-position nodes
        (stable ordering).
        """
        new_node = Node(item)
        item_score = learned_positions.get(item.lower(), float("inf"))

        current = self.head
        while current is not None:
            curr_score = learned_positions.get(current.item.lower(), float("inf"))
            if item_score < curr_score:
                self._insert_before(current, new_node)
                self._size += 1
                return new_node
            current = current.next

        # Falls past all existing nodes — append at end.
        self._append_node(new_node)
        self._size += 1
        return new_node

    def find(self, item: str) -> "Node | None":
        """Case-insensitive search; returns first matching node."""
        for node in self:
            if node.item.lower() == item.lower():
                return node
        return None

    def check_off(self, item: str) -> "Node | None":
        """
        Mark the first unchecked node matching item as checked.
        Returns the node, or None if not found / already checked.
        """
        node = self.find(item)
        if node and not node.checked:
            node.checked = True
            return node
        return None

    def remove(self, item: str) -> "Node | None":
        """Remove and return the first node matching item, or None."""
        node = self.find(item)
        if node:
            self._unlink(node)
            self._size -= 1
        return node

    def to_list(self) -> list[Node]:
        return list(self)

    def clear(self) -> None:
        self.head = self.tail = None
        self._size = 0
