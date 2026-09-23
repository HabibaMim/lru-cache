"""
LRU (Least Recently Used) Cache
--------------------------------

Data structures:
    * A hash map (dict)              key -> Node
        Gives O(1) average lookup of any key's node.
    * A doubly linked list of Nodes  head <-> ... <-> tail
        Keeps entries ordered from most-recently-used (right after head)
        to least-recently-used (right before tail). Because every node
        stores pointers to its neighbours, moving a node to the front or
        unlinking it from the middle is O(1) -- no shifting of elements
        like a list/array would require.

Combining the two gives O(1) average time for both get() and put():
    dict lookup  -> find the node instantly
    linked list  -> reorder / evict instantly once the node is found

Two sentinel nodes (self.head, self.tail) simplify the linked-list code
by removing all the "is this the first/last node?" edge cases.

Bonus: optional per-key TTL (time-to-live). Each node stores an
`expires_at` timestamp (or None for "never expires"). Expiration is
checked lazily -- only when a key is touched by get()/put() -- so we
avoid the cost/complexity of a background sweeper thread. This keeps
the O(1) guarantee but means a dead key can sit in memory until it is
next accessed (see README for the trade-off discussion).
"""

from __future__ import annotations
import time
from typing import Any, Optional


class _Node:
    __slots__ = ("key", "value", "expires_at", "prev", "next")

    def __init__(self, key: Any, value: Any, expires_at: Optional[float] = None):
        self.key = key
        self.value = value
        self.expires_at = expires_at  # epoch seconds, or None = no expiry
        self.prev: Optional["_Node"] = None
        self.next: Optional["_Node"] = None


class LRUCache:
    def __init__(self, capacity: int, default_ttl: Optional[float] = None):
        """
        capacity:    maximum number of entries the cache may hold. Must be > 0.
        default_ttl: optional default seconds-to-live applied to put()
                      calls that don't specify their own ttl. None = no expiry.
        """
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")

        self.capacity = capacity
        self.default_ttl = default_ttl
        self._map: dict[Any, _Node] = {}

        # sentinels: head.next ... tail.prev is the real chain,
        # ordered most-recently-used -> least-recently-used
        self.head = _Node(None, None)
        self.tail = _Node(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

    # ---------- internal linked-list helpers (all O(1)) ----------

    def _remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_at_front(self, node: _Node) -> None:
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def _move_to_front(self, node: _Node) -> None:
        self._remove(node)
        self._insert_at_front(node)

    def _evict_lru(self) -> None:
        lru_node = self.tail.prev
        if lru_node is self.head:
            return  # cache empty
        self._remove(lru_node)
        del self._map[lru_node.key]

    def _is_expired(self, node: _Node) -> bool:
        return node.expires_at is not None and node.expires_at <= time.time()

    def _evict_node(self, node: _Node) -> None:
        self._remove(node)
        del self._map[node.key]

    # ---------- public API ----------

    def get(self, key: Any) -> Any:
        """Return the value for key, or -1 if absent/expired.
        A successful get marks the key as most recently used."""
        node = self._map.get(key)
        if node is None:
            return -1

        if self._is_expired(node):
            self._evict_node(node)
            return -1

        self._move_to_front(node)
        return node.value

    def put(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        """Insert or update key with value.
        ttl: optional seconds-to-live for this entry; falls back to
             self.default_ttl when not given; None means "never expires"
             only if default_ttl is also None."""
        effective_ttl = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + effective_ttl if effective_ttl is not None else None

        node = self._map.get(key)
        if node is not None:
            if self._is_expired(node):
                # treat as a fresh insert
                self._evict_node(node)
                node = None

        if node is not None:
            node.value = value
            node.expires_at = expires_at
            self._move_to_front(node)
            return

        new_node = _Node(key, value, expires_at)
        self._map[key] = new_node
        self._insert_at_front(new_node)

        if len(self._map) > self.capacity:
            self._evict_lru()

    def __len__(self) -> int:
        return len(self._map)

    def __contains__(self, key: Any) -> bool:
        node = self._map.get(key)
        return node is not None and not self._is_expired(node)

    def keys_mru_to_lru(self) -> list:
        """Debug helper: list keys ordered most-recently-used -> least."""
        out = []
        node = self.head.next
        while node is not self.tail:
            out.append(node.key)
            node = node.next
        return out
