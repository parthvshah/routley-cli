#!/usr/bin/env python3
"""
Shopping List CLI
-----------------
Keeps a shopping list using a doubly linked list and learns the order in which
items appear in your store based on the sequence you check them off.  Next
time you add the same items they are pre-sorted into the correct store order.

Data is persisted to ~/.shopping_list_data.json between sessions.

Usage:
    python shopping_list.py
"""

import store_memory
from linked_list import DoublyLinkedList


# ANSI colours (degrade gracefully if the terminal doesn't support them).
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_GREEN  = "\033[32m"
_CYAN   = "\033[36m"
_YELLOW = "\033[33m"
_DIM    = "\033[2m"


def _c(text: str, *codes: str) -> str:
    return "".join(codes) + text + _RESET


HELP_TEXT = f"""
{_c("Commands", _BOLD, _CYAN)}
  {_c("add", _BOLD)} <item> [, item …]   Add one or more items (comma-separated)
  {_c("check", _BOLD)} <item>             Check off an item and teach the store order
  {_c("uncheck", _BOLD)} <item>           Un-check an item
  {_c("remove", _BOLD)} <item>            Remove an item from the list
  {_c("list", _BOLD)}                    Show the current shopping list
  {_c("learned", _BOLD)}                 Show the learned store layout
  {_c("clear", _BOLD)}                   Clear the list  (keeps learned order)
  {_c("reset", _BOLD)}                   Clear the list AND erase all learned data
  {_c("help", _BOLD)}                    Show this help
  {_c("quit", _BOLD)}                    Exit

Shortcuts: a=add  c=check  r=remove  l=list  q=quit
"""


class ShoppingListApp:
    def __init__(self):
        self.shopping_list = DoublyLinkedList()
        self.data = store_memory.load()
        # Counts how many items have been checked off in the current trip.
        self._trip_position = 0

    # ------------------------------------------------------------------ #
    # Actions                                                              #
    # ------------------------------------------------------------------ #

    def add_item(self, item: str) -> None:
        item = item.strip()
        if not item:
            return
        if self.shopping_list.find(item):
            print(f"  {_c('!', _YELLOW)} '{item}' is already in the list.")
            return
        self.shopping_list.insert_sorted(item, self.data["learned_positions"])
        print(f"  {_c('+', _GREEN)} Added: {item}")

    def check_item(self, item: str) -> None:
        node = self.shopping_list.check_off(item)
        if node is None:
            existing = self.shopping_list.find(item)
            if existing and existing.checked:
                print(f"  {_c('!', _YELLOW)} '{item}' is already checked off.")
            else:
                print(f"  {_c('!', _YELLOW)} Item not found: '{item}'")
            return
        self._trip_position += 1
        store_memory.record_check(self.data, node.item, self._trip_position)
        store_memory.save(self.data)
        print(f"  {_c('✓', _GREEN)} Checked off: {node.item}  "
              f"{_c(f'(store position #{self._trip_position} learned)', _DIM)}")

    def uncheck_item(self, item: str) -> None:
        node = self.shopping_list.find(item)
        if node is None:
            print(f"  {_c('!', _YELLOW)} Item not found: '{item}'")
            return
        if not node.checked:
            print(f"  {_c('!', _YELLOW)} '{item}' is not checked off.")
            return
        node.checked = False
        print(f"  Unchecked: {node.item}")

    def remove_item(self, item: str) -> None:
        node = self.shopping_list.remove(item)
        if node:
            print(f"  {_c('-', _YELLOW)} Removed: {node.item}")
        else:
            print(f"  {_c('!', _YELLOW)} Item not found: '{item}'")

    def display_list(self) -> None:
        nodes = self.shopping_list.to_list()
        if not nodes:
            print(f"\n  {_c('Your shopping list is empty.', _DIM)}\n")
            return

        print()
        print(f"  {_c('Shopping List', _BOLD, _CYAN)}")
        print("  " + "─" * 34)
        for i, node in enumerate(nodes, 1):
            if node.checked:
                row = f"  {i:2}. {_c('[✓]', _GREEN)} {_c(node.item, _DIM)}"
            else:
                known = node.item.lower() in self.data["learned_positions"]
                tag = f" {_c('(known)', _DIM)}" if known else ""
                row = f"  {i:2}. [ ] {node.item}{tag}"
            print(row)
        print("  " + "─" * 34)
        checked = sum(1 for n in nodes if n.checked)
        print(f"  {_c(str(checked), _GREEN)}/{len(nodes)} items checked off\n")

    def clear_list(self) -> None:
        self.shopping_list.clear()
        self._trip_position = 0
        print(f"  {_c('List cleared.', _YELLOW)} Learned store order is preserved.")

    def reset_all(self) -> None:
        self.shopping_list.clear()
        store_memory.reset(self.data)
        store_memory.save(self.data)
        self._trip_position = 0
        print(f"  {_c('Reset complete.', _YELLOW)} All list data and learned order erased.")

    def show_learned(self) -> None:
        items = store_memory.sorted_items(self.data)
        if not items:
            print(f"\n  {_c('No store layout learned yet.', _DIM)}")
            print("  Check off items on your list to start teaching it.\n")
            return
        print()
        print(f"  {_c('Learned Store Order', _BOLD, _CYAN)}  "
              f"{_c('(earliest in store → latest)', _DIM)}")
        print("  " + "─" * 38)
        for rank, (item, score) in enumerate(items, 1):
            bar = "█" * min(int(score), 30)
            print(f"  {rank:2}. {item:<22} {_c(f'{score:5.1f}', _DIM)}  {_c(bar, _CYAN)}")
        print()

    # ------------------------------------------------------------------ #
    # REPL                                                                 #
    # ------------------------------------------------------------------ #

    def run(self) -> None:
        print()
        print(_c("  ╔══════════════════════════════════════════╗", _CYAN))
        print(_c("  ║   Shopping List — Learns Your Store      ║", _CYAN))
        print(_c("  ╚══════════════════════════════════════════╝", _CYAN))
        print()
        print("  Type 'help' for a command reference.\n")

        while True:
            try:
                raw = input(_c(">> ", _BOLD)).strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  Goodbye!")
                break

            if not raw:
                continue

            parts = raw.split(None, 1)
            cmd = parts[0].lower()
            arg = parts[1].strip() if len(parts) > 1 else ""

            # ---- add -------------------------------------------------- #
            if cmd in ("add", "a"):
                if not arg:
                    print("  Usage: add <item> [, item …]")
                else:
                    for item in arg.split(","):
                        self.add_item(item)
                    self.display_list()

            # ---- check ------------------------------------------------ #
            elif cmd in ("check", "c"):
                if not arg:
                    print("  Usage: check <item>")
                else:
                    self.check_item(arg)
                    self.display_list()

            # ---- uncheck ---------------------------------------------- #
            elif cmd in ("uncheck", "uc"):
                if not arg:
                    print("  Usage: uncheck <item>")
                else:
                    self.uncheck_item(arg)
                    self.display_list()

            # ---- remove ----------------------------------------------- #
            elif cmd in ("remove", "rm", "r"):
                if not arg:
                    print("  Usage: remove <item>")
                else:
                    self.remove_item(arg)
                    self.display_list()

            # ---- list ------------------------------------------------- #
            elif cmd in ("list", "ls", "l"):
                self.display_list()

            # ---- learned ---------------------------------------------- #
            elif cmd in ("learned", "learn"):
                self.show_learned()

            # ---- clear ------------------------------------------------ #
            elif cmd == "clear":
                confirm = input(
                    "  Clear the current list? (y/n): "
                ).strip().lower()
                if confirm in ("y", "yes"):
                    self.clear_list()
                else:
                    print("  Cancelled.")

            # ---- reset ------------------------------------------------ #
            elif cmd == "reset":
                print(f"  {_c('Warning:', _YELLOW, _BOLD)} This erases ALL learned store "
                      "data and cannot be undone.")
                confirm = input(
                    "  Type 'yes' to confirm reset: "
                ).strip().lower()
                if confirm == "yes":
                    self.reset_all()
                else:
                    print("  Reset cancelled.")

            # ---- help ------------------------------------------------- #
            elif cmd in ("help", "h", "?"):
                print(HELP_TEXT)

            # ---- quit ------------------------------------------------- #
            elif cmd in ("quit", "exit", "q"):
                print("  Goodbye!")
                break

            else:
                print(f"  Unknown command '{cmd}'. Type 'help' for options.")


if __name__ == "__main__":
    app = ShoppingListApp()
    app.run()
