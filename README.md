# LRU Cache

A Least Recently Used (LRU) cache implemented in Python, with O(1) average
time `get()` / `put()`, plus an optional bonus: per-key TTL (expiration).

## Files

```
lru-cache/
├── README.md
├── src/
│   ├── lru_cache.py     # the LRUCache implementation
│   └── example.py       # runnable demo (produces the output shown below)
├── tests/
│   └── test_lru_cache.py  # unittest suite
└── screenshots/
    ├── demo_output.png
    └── test_output.png
```

## Data structures used, and why

The cache combines two structures:

1. **Hash map (`dict[key -> Node]`)**
   Gives O(1) average-time lookup: "does this key exist, and if so, where
   is it in the ordering?"

2. **Doubly linked list of `Node`s**
   Maintains the recency ordering. The node right after the `head`
   sentinel is the **most recently used** entry; the node right before
   the `tail` sentinel is the **least recently used** entry.

   A doubly linked list is used (rather than, say, a plain Python list)
   because each node knows its `prev` and `next` neighbour directly.
   That means:
   - Moving a node to the front (on a `get()` hit or a `put()` update) is
     just re-pointing a handful of pointers — **O(1)**, no shifting of
     elements.
   - Removing the least-recently-used node (on eviction) is also just
     re-pointing pointers at the tail — **O(1)**.

   Two **sentinel nodes** (`self.head`, `self.tail`) are used so the code
   never has to special-case "is this the first/last real node?" — every
   real node always has a valid `prev` and `next`.

Putting the two together: the dict tells you *which* node to touch in
O(1), and the linked list lets you *reorder or evict* that node in O(1).
Neither structure alone gives you both fast lookup **and** fast
reordering — that's why both are needed.

## How LRU ordering is maintained

- On `get(key)`:
  - If the key isn't in the map (or has expired — see TTL below), return
    `-1`.
  - Otherwise, unlink the node from its current position and re-insert it
    right after `head` (making it the most recently used), then return
    its value.

- On `put(key, value)`:
  - If the key already exists, update its value, refresh its expiration,
    and move it to the front (most recently used) — same as a `get()` hit.
  - If the key is new, create a node and insert it at the front. If this
    pushes the cache size above `capacity`, remove the node just before
    `tail` (the least recently used entry) and delete it from the map.

Because every access (`get` or `put`) moves the touched key to the front,
the tail of the list always naturally decays into the least-recently-used
entry, which is exactly the one evicted on overflow.

## Time complexity

| Operation | Average case | Notes |
|---|---|---|
| `get(key)` | **O(1)** | dict lookup + O(1) linked-list unlink/relink |
| `put(key, value)` | **O(1)** | dict lookup/insert + O(1) linked-list ops + O(1) eviction |

(Python dict lookups are amortized O(1); worst-case degenerate hash
collisions are O(n) but not relevant in practice.)

## Space complexity

**O(capacity)** — the cache stores at most `capacity` entries at once,
each represented by one dict entry (key → Node) and one linked-list node
(key, value, prev/next pointers, and optionally an expiration timestamp).
Space grows linearly with `capacity`, not with the number of operations
performed.

## How to run

Requires Python 3.9+ (uses `dict[Any, _Node]` built-in generic syntax;
lower on 3.7/3.8 by removing `from __future__ import annotations`... but
`from __future__ import annotations` is already included, so 3.7+ works
too).

```bash
# Run the demo (shows put/get, eviction, and the TTL bonus)
python3 src/example.py

# Run the automated test suite
python3 -m unittest tests.test_lru_cache -v
```

No external dependencies — standard library only (`time`, `typing`,
`unittest`).

## Example usage

```python
from src.lru_cache import LRUCache

cache = LRUCache(2)
cache.put("A", 10)
cache.put("B", 20)
cache.get("A")      # -> 10   (A becomes most recently used)
cache.put("C", 30)  # capacity exceeded -> evicts "B" (least recently used)
cache.get("B")      # -> -1   (evicted)
cache.get("C")      # -> 30
cache.get("A")      # -> 10
```

## Bonus: TTL / expiration support

`LRUCache` optionally supports per-key time-to-live:

```python
cache = LRUCache(capacity=5)
cache.put("session", "abc123", ttl=60)   # expires 60s from now
cache.put("config", {"x": 1})            # no ttl -> never expires

cache = LRUCache(capacity=5, default_ttl=300)  # every put() defaults to 5 min TTL
```

**Approach:** each node stores an `expires_at` epoch timestamp (or `None`
for "never expires"). Expiration is checked **lazily** — only when a key
is actually touched by `get()` or `put()`. If a node is found to be past
its `expires_at`, it's evicted on the spot and treated as absent (`get`
returns `-1`; `put` treats it as a fresh insert).

**Trade-offs of the lazy approach:**
- ✅ Keeps `get`/`put` O(1) with no extra data structures (no timer heap,
  no background thread/sweeper, no locks).
- ✅ Simple and correct: an expired key is *never* returned to the caller,
  even if it hasn't been physically removed yet.
- ❌ A key that expires and is never accessed again will sit in memory
  (and count against `capacity`) until it's evicted by normal LRU
  pressure or happens to be looked up. This is a **memory/precision**
  trade-off, not a correctness one — capacity is still enforced, so
  worst case you just get slightly "stale-but-invisible" occupants
  taking up slots that would otherwise hold live data.
- An alternative (not implemented here) would be a background sweeper or
  a min-heap keyed by `expires_at` to proactively purge expired entries;
  that adds complexity and, for a heap, an O(log n) step per operation,
  in exchange for freeing memory sooner. For a cache workload this
  simple lazy check is usually the better trade.

Demo output for TTL is included in `src/example.py`'s `demo_ttl_bonus()`
and in `screenshots/demo_output.png`.

## Pushing to your own GitHub repo

```bash
cd lru-cache
git init
git add .
git commit -m "Implement LRU cache with O(1) get/put and TTL bonus"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```
