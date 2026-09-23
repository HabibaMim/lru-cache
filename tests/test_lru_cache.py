import os
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from lru_cache import LRUCache


class TestLRUCacheBasics(unittest.TestCase):
    def test_capacity_must_be_positive(self):
        with self.assertRaises(ValueError):
            LRUCache(0)
        with self.assertRaises(ValueError):
            LRUCache(-3)

    def test_get_missing_key_returns_minus_one(self):
        cache = LRUCache(2)
        self.assertEqual(cache.get("nope"), -1)

    def test_put_and_get_single_key(self):
        cache = LRUCache(2)
        cache.put("A", 10)
        self.assertEqual(cache.get("A"), 10)

    def test_example_from_spec(self):
        cache = LRUCache(2)
        cache.put("A", 10)
        cache.put("B", 20)
        self.assertEqual(cache.get("A"), 10)   # A becomes MRU
        cache.put("C", 30)                     # evicts B (LRU)
        self.assertEqual(cache.get("B"), -1)
        self.assertEqual(cache.get("C"), 30)
        self.assertEqual(cache.get("A"), 10)

    def test_update_existing_key_refreshes_recency(self):
        cache = LRUCache(2)
        cache.put("X", 1)
        cache.put("Y", 2)
        cache.put("X", 100)   # update -> X is now MRU
        cache.put("Z", 3)     # evicts Y, not X
        self.assertEqual(cache.get("Y"), -1)
        self.assertEqual(cache.get("X"), 100)
        self.assertEqual(cache.get("Z"), 3)

    def test_get_marks_most_recently_used(self):
        cache = LRUCache(2)
        cache.put("A", 1)
        cache.put("B", 2)
        cache.get("A")        # A is now MRU, B is LRU
        cache.put("C", 3)     # evicts B
        self.assertEqual(cache.get("B"), -1)
        self.assertEqual(cache.get("A"), 1)
        self.assertEqual(cache.get("C"), 3)

    def test_capacity_one(self):
        cache = LRUCache(1)
        cache.put("only", "first")
        cache.put("only2", "second")
        self.assertEqual(cache.get("only"), -1)
        self.assertEqual(cache.get("only2"), "second")

    def test_len_and_contains(self):
        cache = LRUCache(3)
        cache.put("A", 1)
        cache.put("B", 2)
        self.assertEqual(len(cache), 2)
        self.assertIn("A", cache)
        self.assertNotIn("Z", cache)

    def test_eviction_order_multiple_steps(self):
        cache = LRUCache(3)
        cache.put(1, "a")
        cache.put(2, "b")
        cache.put(3, "c")
        cache.get(1)          # order MRU->LRU: 1,3,2
        cache.put(4, "d")     # evicts 2
        self.assertEqual(cache.get(2), -1)
        self.assertEqual(cache.get(1), "a")
        self.assertEqual(cache.get(3), "c")
        self.assertEqual(cache.get(4), "d")


class TestLRUCacheTTL(unittest.TestCase):
    def test_key_expires_after_ttl(self):
        cache = LRUCache(2)
        cache.put("short", "value", ttl=0.2)
        self.assertEqual(cache.get("short"), "value")
        time.sleep(0.3)
        self.assertEqual(cache.get("short"), -1)

    def test_key_without_ttl_never_expires(self):
        cache = LRUCache(2)
        cache.put("permanent", "value")
        time.sleep(0.2)
        self.assertEqual(cache.get("permanent"), "value")

    def test_default_ttl_applied(self):
        cache = LRUCache(2, default_ttl=0.2)
        cache.put("A", 1)               # uses default ttl
        cache.put("B", 2, ttl=None)     # explicit None falls back to default_ttl
        time.sleep(0.3)
        self.assertEqual(cache.get("A"), -1)
        self.assertEqual(cache.get("B"), -1)

    def test_expired_key_does_not_count_against_capacity_after_access(self):
        cache = LRUCache(1)
        cache.put("A", 1, ttl=0.1)
        time.sleep(0.2)
        cache.put("B", 2)   # A is expired; B should simply take the slot
        self.assertEqual(cache.get("A"), -1)
        self.assertEqual(cache.get("B"), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
