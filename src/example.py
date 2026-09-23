"""
Runnable demo of the LRUCache.

Run with:
    python3 src/example.py
"""
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from lru_cache import LRUCache


def demo_basic():
    print("=" * 60)
    print("DEMO 1: Basic put/get + LRU eviction (capacity = 2)")
    print("=" * 60)

    cache = LRUCache(2)

    cache.put("A", 10)
    print('put("A", 10)')

    cache.put("B", 20)
    print('put("B", 20)')

    result = cache.get("A")
    print(f'get("A") -> {result}   (expected 10)')

    cache.put("C", 30)
    print('put("C", 30)   # capacity exceeded -> evicts LRU key "B"')

    result = cache.get("B")
    print(f'get("B") -> {result}   (expected -1, evicted)')

    result = cache.get("C")
    print(f'get("C") -> {result}   (expected 30)')

    result = cache.get("A")
    print(f'get("A") -> {result}   (expected 10, was refreshed earlier)')

    print(f"\nFinal order (MRU -> LRU): {cache.keys_mru_to_lru()}")
    print()


def demo_update_and_capacity_one():
    print("=" * 60)
    print("DEMO 2: Updating an existing key + capacity = 1 edge case")
    print("=" * 60)

    cache = LRUCache(2)
    cache.put("X", 1)
    cache.put("Y", 2)
    cache.put("X", 100)  # update, X becomes MRU
    print('put("X", 1); put("Y", 2); put("X", 100)  # update existing key')
    print(f'get("X") -> {cache.get("X")}   (expected 100)')

    cache.put("Z", 3)  # should evict Y (LRU), not X
    print('put("Z", 3)   # evicts LRU which is now "Y"')
    print(f'get("Y") -> {cache.get("Y")}   (expected -1)')
    print(f'get("X") -> {cache.get("X")}   (expected 100)')
    print(f'get("Z") -> {cache.get("Z")}   (expected 3)')

    print("\nCapacity = 1 edge case:")
    small = LRUCache(1)
    small.put("only", "first")
    print('cache = LRUCache(1); put("only", "first")')
    small.put("only2", "second")
    print('put("only2", "second")   # evicts "only"')
    print(f'get("only") -> {small.get("only")}   (expected -1)')
    print(f'get("only2") -> {small.get("only2")}   (expected "second")')
    print()


def demo_invalid_capacity():
    print("=" * 60)
    print("DEMO 3: Invalid capacity raises ValueError")
    print("=" * 60)
    try:
        LRUCache(0)
    except ValueError as e:
        print(f'LRUCache(0) -> raised ValueError: "{e}"')
    try:
        LRUCache(-5)
    except ValueError as e:
        print(f'LRUCache(-5) -> raised ValueError: "{e}"')
    print()


def demo_ttl_bonus():
    print("=" * 60)
    print("BONUS DEMO: TTL / expiration support")
    print("=" * 60)

    cache = LRUCache(capacity=5)

    cache.put("short_lived", "I will expire", ttl=1)  # 1 second TTL
    cache.put("long_lived", "I will stay", ttl=10)     # 10 second TTL
    cache.put("permanent", "no ttl set")                # no expiry

    print('put("short_lived", ..., ttl=1)')
    print('put("long_lived", ..., ttl=10)')
    print('put("permanent", ...)   # no ttl -> never expires')

    print(f'\nImmediately after inserting:')
    print(f'get("short_lived") -> {cache.get("short_lived")}')
    print(f'get("long_lived")  -> {cache.get("long_lived")}')
    print(f'get("permanent")   -> {cache.get("permanent")}')

    print("\nSleeping 1.5 seconds so short_lived's TTL passes...")
    time.sleep(1.5)

    print(f'\nAfter 1.5s:')
    print(f'get("short_lived") -> {cache.get("short_lived")}   (expected -1, expired)')
    print(f'get("long_lived")  -> {cache.get("long_lived")}   (expected "I will stay", still alive)')
    print(f'get("permanent")   -> {cache.get("permanent")}   (expected "no ttl set")')
    print()


if __name__ == "__main__":
    demo_basic()
    demo_update_and_capacity_one()
    demo_invalid_capacity()
    demo_ttl_bonus()
