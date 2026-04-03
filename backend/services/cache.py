"""In-memory LRU cache for search results and API responses"""
from functools import lru_cache
from typing import Tuple, List, Dict, Optional
import threading
import time
from datetime import datetime, timedelta

class CacheStats:
    """Track cache performance metrics"""
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()
    
    def record_hit(self):
        with self.lock:
            self.hits += 1
    
    def record_miss(self):
        with self.lock:
            self.misses += 1
    
    def get_stats(self) -> dict:
        with self.lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0
            return {
                "hits": self.hits,
                "misses": self.misses,
                "total": total,
                "hit_rate": f"{hit_rate:.1f}%"
            }
    
    def reset(self):
        with self.lock:
            self.hits = 0
            self.misses = 0


class TimedLRUCache:
    """Thread-safe LRU cache with TTL (time-to-live) expiration"""
    
    def __init__(self, maxsize: int = 128, ttl_hours: float = 1.0):
        """
        Initialize cache with LRU eviction and TTL
        
        Args:
            maxsize: Maximum number of cached items
            ttl_hours: Time-to-live in hours before cache expires
        """
        self.maxsize = maxsize
        self.ttl = timedelta(hours=ttl_hours)
        self.cache = {}
        self.timestamps = {}
        self.lock = threading.Lock()
        self.stats = CacheStats()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry has expired"""
        if key not in self.timestamps:
            return True
        return datetime.now() - self.timestamps[key] > self.ttl
    
    def get(self, key: str) -> Optional[any]:
        """Get value from cache if exists and not expired"""
        with self.lock:
            if key not in self.cache or self._is_expired(key):
                self.stats.record_miss()
                # Clean up expired entry
                if key in self.cache:
                    del self.cache[key]
                    del self.timestamps[key]
                return None
            
            self.stats.record_hit()
            return self.cache[key]
    
    def set(self, key: str, value: any) -> None:
        """Set value in cache"""
        with self.lock:
            # Remove oldest entry if cache is full
            if len(self.cache) >= self.maxsize and key not in self.cache:
                oldest_key = min(self.timestamps.keys(), key=lambda k: self.timestamps[k])
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
            
            self.cache[key] = value
            self.timestamps[key] = datetime.now()
    
    def invalidate(self, key: Optional[str] = None) -> None:
        """Invalidate single key or entire cache"""
        with self.lock:
            if key is None:
                self.cache.clear()
                self.timestamps.clear()
            elif key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        with self.lock:
            return {
                "size": len(self.cache),
                "maxsize": self.maxsize,
                "ttl_hours": self.ttl.total_seconds() / 3600,
                **self.stats.get_stats()
            }


class SearchResultCache:
    """Specialized cache for vector search results"""
    
    def __init__(self, maxsize: int = 256, ttl_hours: float = 1.0):
        self._cache = TimedLRUCache(maxsize=maxsize, ttl_hours=ttl_hours)
    
    def get_cache_key(self, question: str, user_id: int, k: int = 5) -> str:
        """Generate cache key from search parameters"""
        # Normalize question (lowercase, strip whitespace)
        normalized = question.lower().strip()
        return f"search:{user_id}:{normalized}:{k}"
    
    def get(self, question: str, user_id: int, k: int = 5) -> Optional[List[Dict]]:
        """Get cached search results"""
        key = self.get_cache_key(question, user_id, k)
        return self._cache.get(key)
    
    def set(self, question: str, user_id: int, results: List[Dict], k: int = 5) -> None:
        """Cache search results"""
        key = self.get_cache_key(question, user_id, k)
        self._cache.set(key, results)
    
    def invalidate_user(self, user_id: int) -> None:
        """Invalidate all cache entries for a user (when new PDFs uploaded)"""
        with self._cache.lock:
            keys_to_delete = [k for k in self._cache.cache.keys() if f"search:{user_id}:" in k]
            for key in keys_to_delete:
                del self._cache.cache[key]
                del self._cache.timestamps[key]
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return self._cache.get_stats()


# Global cache instance
search_cache = SearchResultCache(maxsize=256, ttl_hours=1.0)
