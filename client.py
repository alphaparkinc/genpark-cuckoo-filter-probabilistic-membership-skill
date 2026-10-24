"""Cuckoo Filter Probabilistic Set Membership Engine.
100% Python Standard Library.
"""

import hashlib
import random
from typing import Dict, List, Any

class CuckooFilter:
    """Cuckoo Filter supporting dynamic insertions, lookups, and deletions with bounded false positives."""

    def __init__(self, capacity: int = 1000, bucket_size: int = 4, max_kicks: int = 500):
        self.capacity = max(16, capacity)
        self.bucket_size = bucket_size
        self.max_kicks = max_kicks
        self.num_buckets = 1
        while self.num_buckets < capacity // bucket_size:
            self.num_buckets <<= 1
        self.buckets: List[List[int]] = [[] for _ in range(self.num_buckets)]
        self.size = 0

    def _hash(self, item: str) -> int:
        h = hashlib.sha256(item.encode("utf-8")).digest()
        return int.from_bytes(h[:4], "big")

    def _fingerprint(self, item: str) -> int:
        h = hashlib.sha256(("fp:" + item).encode("utf-8")).digest()
        return int.from_bytes(h[:2], "big") % 65535 + 1

    def _alt_index(self, i: int, fp: int) -> int:
        fp_hash = int.from_bytes(hashlib.md5(str(fp).encode("utf-8")).digest()[:4], "big")
        return (i ^ fp_hash) % self.num_buckets

    def insert(self, item: str) -> bool:
        fp = self._fingerprint(item)
        i1 = self._hash(item) % self.num_buckets
        i2 = self._alt_index(i1, fp)

        if len(self.buckets[i1]) < self.bucket_size:
            self.buckets[i1].append(fp)
            self.size += 1
            return True
        if len(self.buckets[i2]) < self.bucket_size:
            self.buckets[i2].append(fp)
            self.size += 1
            return True

        curr_i = random.choice([i1, i2])
        curr_fp = fp
        for _ in range(self.max_kicks):
            slot = random.randint(0, self.bucket_size - 1)
            evicted_fp = self.buckets[curr_i][slot]
            self.buckets[curr_i][slot] = curr_fp
            curr_fp = evicted_fp
            curr_i = self._alt_index(curr_i, curr_fp)
            if len(self.buckets[curr_i]) < self.bucket_size:
                self.buckets[curr_i].append(curr_fp)
                self.size += 1
                return True
        return False

    def contains(self, item: str) -> bool:
        fp = self._fingerprint(item)
        i1 = self._hash(item) % self.num_buckets
        i2 = self._alt_index(i1, fp)
        return (fp in self.buckets[i1]) or (fp in self.buckets[i2])

    def delete(self, item: str) -> bool:
        fp = self._fingerprint(item)
        i1 = self._hash(item) % self.num_buckets
        i2 = self._alt_index(i1, fp)
        if fp in self.buckets[i1]:
            self.buckets[i1].remove(fp)
            self.size -= 1
            return True
        if fp in self.buckets[i2]:
            self.buckets[i2].remove(fp)
            self.size -= 1
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        load_factor = self.size / (self.num_buckets * self.bucket_size)
        return {
            "size": self.size,
            "num_buckets": self.num_buckets,
            "bucket_size": self.bucket_size,
            "load_factor": round(load_factor, 4)
        }
