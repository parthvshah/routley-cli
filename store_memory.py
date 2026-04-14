"""
Persistence layer for learned store layout.

For each item we track the sequence of positions at which it was checked off
across shopping trips (position 1 = first item grabbed, 2 = second, etc.).
The learned score is a recency-weighted average of those positions so the
app adapts if the store rearranges its shelves.
"""

import json
from pathlib import Path

DATA_FILE = Path.home() / ".shopping_list_data.json"

# How many historical check-off positions to remember per item.
_HISTORY_WINDOW = 15


def load() -> dict:
    """Return persisted data, or a fresh structure if none exists."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE) as fh:
                data = json.load(fh)
            # Migrate older files that are missing keys.
            data.setdefault("learned_positions", {})
            data.setdefault("check_history", {})
            return data
        except (json.JSONDecodeError, KeyError):
            pass
    return {"learned_positions": {}, "check_history": {}}


def save(data: dict) -> None:
    with open(DATA_FILE, "w") as fh:
        json.dump(data, fh, indent=2)


def record_check(data: dict, item: str, trip_position: int) -> None:
    """
    Record that *item* was checked off at *trip_position* in this shopping
    trip, then recompute its weighted-average learned position.

    Recent observations are weighted more heavily so the score adapts over
    time.  Weight of the k-th oldest entry (1-indexed) = k / total_weight,
    so the newest entry gets the highest weight.
    """
    key = item.lower()
    history: list[int] = data["check_history"].get(key, [])
    history.append(trip_position)
    history = history[-_HISTORY_WINDOW:]          # keep only the window
    data["check_history"][key] = history

    n = len(history)
    # Weights: 1, 2, 3, … n  (oldest → newest)
    total_weight = n * (n + 1) / 2
    weighted_sum = sum(pos * weight for weight, pos in enumerate(history, 1))
    data["learned_positions"][key] = weighted_sum / total_weight


def reset(data: dict) -> None:
    """Erase all learned data in-place."""
    data["learned_positions"].clear()
    data["check_history"].clear()


def sorted_items(data: dict) -> list[tuple[str, float]]:
    """Return (item, score) pairs sorted by learned store position."""
    return sorted(data["learned_positions"].items(), key=lambda x: x[1])
