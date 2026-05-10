"""Caching Layer: Performance optimization with multiple caching strategies."""

from typing import Dict, Any, List, Optional, Union, Callable
import json
import hashlib
import time
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from collections import OrderedDict
import pickle
import sqlite3
from pathlib import Path


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    timestamp: datetime
    ttl: Optional[int]  # Time to live in seconds
    access_count: int
    last_access: datetime
    size_bytes: int


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get cache size."""
        pass
    
    @abstractmethod
    def keys(self) -> List[str]:
        """Get all cache keys."""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache with LRU eviction."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default time to live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = OrderedDict()  # LRU cache
        self.lock = threading.RLock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            entry = self.cache.get(key)
            
            if entry is None:
                self.stats["misses"] += 1
                return None
            
            # Check TTL
            if entry.ttl and (datetime.now() - entry.timestamp).total_seconds() > entry.ttl:
                del self.cache[key]
                self.stats["misses"] += 1
                return None
            
            # Update access info
            entry.access_count += 1
            entry.last_access = datetime.now()
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            self.stats["hits"] += 1
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        with self.lock:
            try:
                # Calculate size
                size_bytes = len(pickle.dumps(value))
                
                # Check if we need to evict
                if key not in self.cache and len(self.cache) >= self.max_size:
                    self._evict_lru()
                
                # Create entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    timestamp=datetime.now(),
                    ttl=ttl or self.default_ttl,
                    access_count=0,
                    last_access=datetime.now(),
                    size_bytes=size_bytes
                )
                
                self.cache[key] = entry
                self.cache.move_to_end(key)
                self.stats["sets"] += 1
                
                return True
                
            except Exception:
                return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.stats["deletes"] += 1
                return True
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            return True
    
    def size(self) -> int:
        """Get cache size."""
        with self.lock:
            return len(self.cache)
    
    def keys(self) -> List[str]:
        """Get all cache keys."""
        with self.lock:
            return list(self.cache.keys())
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self.cache:
            lru_key = next(iter(self.cache))
            del self.cache[lru_key]
            self.stats["evictions"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
            
            total_size = sum(entry.size_bytes for entry in self.cache.values())
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": hit_rate,
                "total_requests": total_requests,
                "total_size_bytes": total_size,
                **self.stats
            }


class RedisCache(CacheBackend):
    """Redis cache backend (placeholder implementation)."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, default_ttl: int = 3600):
        """
        Initialize Redis cache.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database
            default_ttl: Default time to live in seconds
        """
        self.host = host
        self.port = port
        self.db = db
        self.default_ttl = default_ttl
        self.redis_client = None
        self.connected = False
        
        try:
            import redis
            self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.redis_client.ping()
            self.connected = True
        except ImportError:
            print("Redis not installed. Using fallback memory cache.")
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.connected:
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.connected:
            return False
        
        try:
            data = pickle.dumps(value)
            ttl = ttl or self.default_ttl
            return self.redis_client.setex(key, ttl, data)
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.connected:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception:
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        if not self.connected:
            return False
        
        try:
            return self.redis_client.flushdb()
        except Exception:
            return False
    
    def size(self) -> int:
        """Get cache size."""
        if not self.connected:
            return 0
        
        try:
            return self.redis_client.dbsize()
        except Exception:
            return 0
    
    def keys(self) -> List[str]:
        """Get all cache keys."""
        if not self.connected:
            return []
        
        try:
            return self.redis_client.keys()
        except Exception:
            return []


class SQLiteCache(CacheBackend):
    """SQLite-based persistent cache."""
    
    def __init__(self, db_path: str = "cache.db", default_ttl: int = 3600):
        """
        Initialize SQLite cache.
        
        Args:
            db_path: Path to SQLite database
            default_ttl: Default time to live in seconds
        """
        self.db_path = db_path
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database tables."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    timestamp REAL,
                    ttl INTEGER,
                    access_count INTEGER DEFAULT 0,
                    last_access REAL,
                    size_bytes INTEGER
                )
            """)
            conn.commit()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("""
                        SELECT value, timestamp, ttl, access_count
                        FROM cache_entries
                        WHERE key = ?
                    """, (key,))
                    
                    row = cursor.fetchone()
                    if not row:
                        return None
                    
                    value_blob, timestamp, ttl, access_count = row
                    
                    # Check TTL
                    if ttl and (time.time() - timestamp) > ttl:
                        self.delete(key)
                        return None
                    
                    # Update access info
                    conn.execute("""
                        UPDATE cache_entries
                        SET access_count = ?, last_access = ?
                        WHERE key = ?
                    """, (access_count + 1, time.time(), key))
                    conn.commit()
                    
                    return pickle.loads(value_blob)
                    
            except Exception:
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        with self.lock:
            try:
                value_blob = pickle.dumps(value)
                size_bytes = len(value_blob)
                ttl = ttl or self.default_ttl
                
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO cache_entries
                        (key, value, timestamp, ttl, access_count, last_access, size_bytes)
                        VALUES (?, ?, ?, ?, 1, ?, ?)
                    """, (key, value_blob, time.time(), ttl, time.time(), size_bytes))
                    conn.commit()
                
                return True
                
            except Exception:
                return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                    conn.commit()
                    return cursor.rowcount > 0
            except Exception:
                return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM cache_entries")
                    conn.commit()
                    return True
            except Exception:
                return False
    
    def size(self) -> int:
        """Get cache size."""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
                    return cursor.fetchone()[0]
            except Exception:
                return 0
    
    def keys(self) -> List[str]:
        """Get all cache keys."""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT key FROM cache_entries")
                    return [row[0] for row in cursor.fetchall()]
            except Exception:
                return []
    
    def cleanup_expired(self) -> int:
        """Clean up expired entries."""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("""
                        DELETE FROM cache_entries
                        WHERE ttl > 0 AND (timestamp + ttl) < ?
                    """, (time.time(),))
                    conn.commit()
                    return cursor.rowcount
            except Exception:
                return 0


class CacheManager:
    """High-level cache manager with multiple backends and strategies."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize cache manager.
        
        Args:
            config: Cache configuration
        """
        self.config = config or self._get_default_config()
        self.backends = {}
        self.default_backend = None
        self.cache_stats = {}
        
        # Initialize backends
        self._init_backends()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default cache configuration."""
        return {
            "default_backend": "memory",
            "backends": {
                "memory": {
                    "type": "memory",
                    "max_size": 1000,
                    "default_ttl": 3600
                },
                "redis": {
                    "type": "redis",
                    "host": "localhost",
                    "port": 6379,
                    "db": 0,
                    "default_ttl": 3600
                },
                "sqlite": {
                    "type": "sqlite",
                    "db_path": "data/cache.db",
                    "default_ttl": 3600
                }
            },
            "key_prefix": "rec_app:",
            "key_hashing": True,
            "cleanup_interval": 300  # 5 minutes
        }
    
    def _init_backends(self) -> None:
        """Initialize cache backends."""
        for name, backend_config in self.config["backends"].items():
            backend_type = backend_config["type"]
            
            if backend_type == "memory":
                self.backends[name] = MemoryCache(
                    max_size=backend_config.get("max_size", 1000),
                    default_ttl=backend_config.get("default_ttl", 3600)
                )
            elif backend_type == "redis":
                self.backends[name] = RedisCache(
                    host=backend_config.get("host", "localhost"),
                    port=backend_config.get("port", 6379),
                    db=backend_config.get("db", 0),
                    default_ttl=backend_config.get("default_ttl", 3600)
                )
            elif backend_type == "sqlite":
                self.backends[name] = SQLiteCache(
                    db_path=backend_config.get("db_path", "cache.db"),
                    default_ttl=backend_config.get("default_ttl", 3600)
                )
        
        # Set default backend
        default_name = self.config["default_backend"]
        if default_name in self.backends:
            self.default_backend = self.backends[default_name]
        else:
            self.default_backend = list(self.backends.values())[0] if self.backends else None
    
    def _prepare_key(self, key: str) -> str:
        """Prepare cache key with prefix and optional hashing."""
        # Add prefix
        full_key = f"{self.config['key_prefix']}{key}"
        
        # Hash if enabled and key is long
        if self.config["key_hashing"] and len(full_key) > 64:
            full_key = hashlib.md5(full_key.encode()).hexdigest()
        
        return full_key
    
    def get(self, key: str, backend: Optional[str] = None) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            backend: Specific backend to use
            
        Returns:
            Cached value or None
        """
        if not self.default_backend:
            return None
        
        backend_obj = self.backends.get(backend, self.default_backend)
        prepared_key = self._prepare_key(key)
        
        return backend_obj.get(prepared_key)
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        backend: Optional[str] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            backend: Specific backend to use
            
        Returns:
            True if successful
        """
        if not self.default_backend:
            return False
        
        backend_obj = self.backends.get(backend, self.default_backend)
        prepared_key = self._prepare_key(key)
        
        return backend_obj.set(prepared_key, value, ttl)
    
    def delete(self, key: str, backend: Optional[str] = None) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            backend: Specific backend to use
            
        Returns:
            True if successful
        """
        if not self.default_backend:
            return False
        
        backend_obj = self.backends.get(backend, self.default_backend)
        prepared_key = self._prepare_key(key)
        
        return backend_obj.delete(prepared_key)
    
    def clear(self, backend: Optional[str] = None) -> bool:
        """
        Clear cache.
        
        Args:
            backend: Specific backend to clear
            
        Returns:
            True if successful
        """
        if backend:
            backend_obj = self.backends.get(backend)
            if backend_obj:
                return backend_obj.clear()
            return False
        else:
            # Clear all backends
            success = True
            for backend_obj in self.backends.values():
                success &= backend_obj.clear()
            return success
    
    def get_or_set(
        self,
        key: str,
        value_func: Callable[[], Any],
        ttl: Optional[int] = None,
        backend: Optional[str] = None
    ) -> Any:
        """
        Get value from cache or set if not exists.
        
        Args:
            key: Cache key
            value_func: Function to generate value if not cached
            ttl: Time to live in seconds
            backend: Specific backend to use
            
        Returns:
            Cached or generated value
        """
        value = self.get(key, backend)
        if value is not None:
            return value
        
        # Generate and cache value
        value = value_func()
        self.set(key, value, ttl, backend)
        return value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {}
        
        for name, backend in self.backends.items():
            if hasattr(backend, 'get_stats'):
                stats[name] = backend.get_stats()
            else:
                stats[name] = {
                    "size": backend.size(),
                    "type": type(backend).__name__
                }
        
        return stats
    
    def cleanup_expired(self) -> Dict[str, int]:
        """Clean up expired entries across all backends."""
        results = {}
        
        for name, backend in self.backends.items():
            if hasattr(backend, 'cleanup_expired'):
                results[name] = backend.cleanup_expired()
            else:
                results[name] = 0
        
        return results


# Decorators for easy caching
def cache_result(
    key_func: Optional[Callable] = None,
    ttl: int = 3600,
    backend: Optional[str] = None
):
    """
    Decorator to cache function results.
    
    Args:
        key_func: Function to generate cache key
        ttl: Time to live in seconds
        backend: Specific backend to use
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cache_manager = CacheManager()
            cached_result = cache_manager.get(cache_key, backend)
            
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl, backend)
            
            return result
        
        return wrapper
    return decorator


def cache_recommendations(ttl: int = 1800):  # 30 minutes
    """
    Decorator specifically for caching recommendations.
    
    Args:
        ttl: Time to live in seconds
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract preferences for cache key
            preferences = kwargs.get('preferences', args[1] if len(args) > 1 else {})
            
            # Create cache key from preferences
            key_parts = [
                f"location={preferences.get('location', 'any')}",
                f"cuisine={preferences.get('cuisine', 'any')}",
                f"budget={preferences.get('max_cost_for_two', 'any')}",
                f"rating={preferences.get('min_rating', 'any')}",
                f"occasion={preferences.get('occasion', 'any')}"
            ]
            
            cache_key = f"recommendations:{'|'.join(key_parts)}"
            
            # Try to get from cache
            cache_manager = CacheManager()
            cached_result = cache_manager.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Global cache manager instance
cache_manager = CacheManager()
