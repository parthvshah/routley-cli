# Shopping List CLI

A terminal shopping list that learns the layout of your store. The first time you use it, items appear in the order you added them. As you check items off during each shopping trip, the app records the sequence — and on your next visit, it automatically sorts new items into the order you'll encounter them in the store.

## Requirements

- Python 3.10 or later (no external dependencies)

## Installation

Make the wrapper executable and add it to your PATH so you can invoke it from anywhere:

```bash
chmod +x /path/to/routley-cli/routley-cli

# Option A — symlink into a directory already on your PATH
ln -s /path/to/routley-cli/routley-cli /usr/local/bin/routley-cli

# Option B — add the repo directory to your PATH (in ~/.zshrc or ~/.bashrc)
export PATH="$PATH:/path/to/routley-cli"
```

Then reload your shell:

```bash
source ~/.zshrc   # or source ~/.bashrc
```

## Running

```bash
routley-cli
```

From the repo directory you can also invoke it directly without installation:

```bash
./routley-cli
```

## Quickstart

```
>> add milk, eggs, bread, apples
>> list
>> check bread
>> check milk
>> check apples
>> check eggs
>> clear          # start a fresh trip — learned order is saved
>> add eggs, milk, bread, apples
>> list           # now sorted: bread → milk → apples → eggs
```

## Commands

| Command | Shortcut | Description |
|---|---|---|
| `add <item> [, item …]` | `a` | Add one or more items (comma-separated). Known items are inserted at their learned store position; new items go to the end. |
| `check <item>` | `c` | Check off an item. Records its position in the current trip to teach the store layout. |
| `uncheck <item>` | `uc` | Un-check a previously checked item. |
| `remove <item>` | `r` | Remove an item from the list entirely. |
| `list` | `l` | Display the current shopping list. |
| `learned` | — | Show the full learned store order with position scores. |
| `clear` | — | Wipe the current list. Learned store data is preserved. |
| `reset` | — | Wipe the current list **and** erase all learned store data. Requires confirmation. |
| `help` | `h` | Show the in-app command reference. |
| `quit` | `q` | Exit. |

## How the learning works

Each time you check off an item, the app notes its **trip position** — the count of items already checked off before it in that shopping trip. Position 1 means it was the first item you grabbed; position 5 means four others came before it.

Over multiple trips, those positions are averaged using a **recency-weighted mean** (up to the last 15 trips): more recent trips count more, so if your store rearranges its shelves the app gradually adapts. When you add a known item, it is inserted into the doubly linked list at the spot that matches its learned score, automatically sorting your list into aisle order.

Items tagged `(known)` in the list view have a learned position. Untagged items have never been checked off and will be placed at the end.

## Data storage

Learned positions are saved to `~/.shopping_list_data.json` and persist between sessions. The file is plain JSON and safe to inspect or back up manually.

## Files

| File | Description |
|---|---|
| `routley-cli` | Executable wrapper — invoke this directly |
| `shopping_list.py` | REPL and display logic |
| `linked_list.py` | `Node` and `DoublyLinkedList` implementation |
| `store_memory.py` | Persistence and position-learning algorithm |

## Example session

```
>> add yogurt, chicken, pasta, onions, bananas
  + Added: yogurt
  + Added: chicken
  + Added: pasta
  + Added: onions
  + Added: bananas

  Shopping List
  ──────────────────────────────────
   1. [ ] yogurt
   2. [ ] chicken
   3. [ ] pasta
   4. [ ] onions
   5. [ ] bananas
  ──────────────────────────────────
  0/5 items checked off

>> check onions          # first item you pass in the store
>> check chicken
>> check pasta
>> check yogurt
>> check bananas

>> learned
  Learned Store Order  (earliest in store → latest)
  ──────────────────────────────────────
   1. onions                    1.0  █
   2. chicken                   2.0  ██
   3. pasta                     3.0  ███
   4. yogurt                    4.0  ████
   5. bananas                   5.0  █████

>> clear
>> add bananas, yogurt, onions, pasta, chicken
  # Added in random order, but the list shows:
   1. [ ] onions     (known)
   2. [ ] chicken    (known)
   3. [ ] pasta      (known)
   4. [ ] yogurt     (known)
   5. [ ] bananas    (known)
```

## Resetting

To start completely fresh — wiping both the current list and all learned store data:

```
>> reset
  Warning: This erases ALL learned store data and cannot be undone.
  Type 'yes' to confirm reset: yes
  Reset complete. All list data and learned order erased.
```

To clear only the current trip's list while keeping what the app has learned:

```
>> clear
  Clear the current list? (y/n): y
  List cleared. Learned store order is preserved.
```
