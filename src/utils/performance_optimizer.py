"""
Performance Optimizer - Caching, query optimization, and memory profiling utilities
Provides tools for improving application performance and monitoring resource usage
"""
import logging
import time
import functools
import tracemalloc
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
import sqlite3


logger = logging.getLogger(__name__)


class LRUCache:
    """
    Least Recently Used (LRU) Cache implementation
    Thread-safe cache with size limit and TTL support
    """
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        """
        Initialize LRU Cache
        
        Args:
            max_size: Maximum number of items in cache
            ttl: Time-to-live in seconds (default: 300 = 5 minutes)
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, datetime] = {}
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value if found and valid, None otherwise
        """
        if key not in self._cache:
            self._misses += 1
            return None
        
        # Check if expired
        timestamp = self._timestamps.get(key)
        if timestamp and (datetime.now() - timestamp).total_seconds() > self.ttl:
            self.delete(key)
            self._misses += 1
            return None
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        self._hits += 1
        return self._cache[key]
    
    def set(self, key: str, value: Any):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Update existing key
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            # Add new key
            self._cache[key] = value
            
            # Remove oldest if over max size
            if len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                self.delete(oldest_key)
        
        self._cache[key] = value
        self._timestamps[key] = datetime.now()
    
    def delete(self, key: str):
        """
        Delete key from cache
        
        Args:
            key: Cache key to delete
        """
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]
    
    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
        self._timestamps.clear()
        self._hits = 0
        self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': f"{hit_rate:.2f}%",
            'ttl': self.ttl
        }



class QueryOptimizer:
    """
    Query optimization utilities for SQLite
    Provides tools for analyzing and optimizing database queries
    """
    
    @staticmethod
    def analyze_query(conn: sqlite3.Connection, query: str, params: Tuple = ()) -> Dict[str, Any]:
        """
        Analyze query execution plan
        
        Args:
            conn: Database connection
            query: SQL query to analyze
            params: Query parameters
        
        Returns:
            Dictionary with query analysis results
        """
        try:
            # Get query plan
            explain_query = f"EXPLAIN QUERY PLAN {query}"
            cursor = conn.cursor()
            cursor.execute(explain_query, params)
            plan = cursor.fetchall()
            
            # Measure execution time
            start_time = time.time()
            cursor.execute(query, params)
            cursor.fetchall()
            execution_time = time.time() - start_time
            
            return {
                'query': query,
                'execution_time': execution_time,
                'query_plan': plan,
                'params': params
            }
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {
                'query': query,
                'error': str(e)
            }
    
    @staticmethod
    def suggest_indexes(conn: sqlite3.Connection, table_name: str) -> List[str]:
        """
        Suggest indexes for a table based on query patterns
        
        Args:
            conn: Database connection
            table_name: Name of table to analyze
        
        Returns:
            List of suggested index creation statements
        """
        suggestions = []
        
        try:
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Check existing indexes
            cursor.execute(f"PRAGMA index_list({table_name})")
            existing_indexes = cursor.fetchall()
            existing_cols = set()
            
            for idx in existing_indexes:
                cursor.execute(f"PRAGMA index_info({idx[1]})")
                idx_cols = cursor.fetchall()
                for col in idx_cols:
                    existing_cols.add(col[2])
            
            # Suggest indexes for columns without indexes
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                
                # Skip if already indexed
                if col_name in existing_cols:
                    continue
                
                # Suggest index for common query columns
                if col_name.endswith('_id') or col_name in ['created_at', 'updated_at', 'status']:
                    suggestions.append(
                        f"CREATE INDEX idx_{table_name}_{col_name} ON {table_name}({col_name})"
                    )
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting indexes: {e}")
            return []
    
    @staticmethod
    def optimize_query(query: str) -> str:
        """
        Optimize SQL query by applying best practices
        
        Args:
            query: SQL query to optimize
        
        Returns:
            Optimized query string
        """
        optimized = query.strip()
        
        # Add LIMIT if not present for SELECT queries
        if optimized.upper().startswith('SELECT') and 'LIMIT' not in optimized.upper():
            logger.warning(f"Query without LIMIT clause: {query[:50]}...")
        
        # Suggest using indexes
        if 'WHERE' in optimized.upper() and 'INDEX' not in optimized.upper():
            logger.debug("Consider adding indexes for WHERE clause columns")
        
        return optimized
    
    @staticmethod
    def get_slow_queries(conn: sqlite3.Connection, threshold_ms: float = 100) -> List[Dict[str, Any]]:
        """
        Identify slow queries from SQLite stats (if available)
        
        Args:
            conn: Database connection
            threshold_ms: Threshold in milliseconds for slow queries
        
        Returns:
            List of slow query information
        """
        # Note: SQLite doesn't have built-in slow query log
        # This is a placeholder for custom implementation
        logger.info(f"Slow query detection threshold: {threshold_ms}ms")
        return []


class MemoryProfiler:
    """
    Memory profiling utilities
    Provides tools for monitoring and analyzing memory usage
    """
    
    def __init__(self):
        """Initialize memory profiler"""
        self._snapshots: List[Tuple[str, Any]] = []
        self._is_tracing = False
    
    def start_tracing(self):
        """Start memory tracing"""
        if not self._is_tracing:
            tracemalloc.start()
            self._is_tracing = True
            logger.info("Memory tracing started")
    
    def stop_tracing(self):
        """Stop memory tracing"""
        if self._is_tracing:
            tracemalloc.stop()
            self._is_tracing = False
            logger.info("Memory tracing stopped")
    
    def take_snapshot(self, label: str = ""):
        """
        Take a memory snapshot
        
        Args:
            label: Label for the snapshot
        """
        if not self._is_tracing:
            self.start_tracing()
        
        snapshot = tracemalloc.take_snapshot()
        self._snapshots.append((label or f"snapshot_{len(self._snapshots)}", snapshot))
        logger.info(f"Memory snapshot taken: {label}")
    
    def get_current_memory(self) -> Dict[str, Any]:
        """
        Get current memory usage
        
        Returns:
            Dictionary with memory usage information
        """
        if not self._is_tracing:
            self.start_tracing()
        
        current, peak = tracemalloc.get_traced_memory()
        
        return {
            'current_mb': current / 1024 / 1024,
            'peak_mb': peak / 1024 / 1024,
            'current_bytes': current,
            'peak_bytes': peak
        }
    
    def compare_snapshots(self, label1: str, label2: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Compare two memory snapshots
        
        Args:
            label1: Label of first snapshot
            label2: Label of second snapshot
            top_n: Number of top differences to return
        
        Returns:
            List of top memory differences
        """
        snapshot1 = None
        snapshot2 = None
        
        for label, snapshot in self._snapshots:
            if label == label1:
                snapshot1 = snapshot
            if label == label2:
                snapshot2 = snapshot
        
        if not snapshot1 or not snapshot2:
            logger.error(f"Snapshots not found: {label1}, {label2}")
            return []
        
        # Compare snapshots
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        results = []
        for stat in top_stats[:top_n]:
            results.append({
                'file': stat.traceback.format()[0] if stat.traceback else 'unknown',
                'size_diff_mb': stat.size_diff / 1024 / 1024,
                'count_diff': stat.count_diff,
                'size_mb': stat.size / 1024 / 1024
            })
        
        return results
    
    def get_top_allocations(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top memory allocations
        
        Args:
            top_n: Number of top allocations to return
        
        Returns:
            List of top memory allocations
        """
        if not self._is_tracing:
            logger.warning("Memory tracing not started")
            return []
        
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        results = []
        for stat in top_stats[:top_n]:
            results.append({
                'file': str(stat.traceback.format()[0]) if stat.traceback else 'unknown',
                'size_mb': stat.size / 1024 / 1024,
                'count': stat.count
            })
        
        return results
    
    def clear_snapshots(self):
        """Clear all snapshots"""
        self._snapshots.clear()
        logger.info("Memory snapshots cleared")



def cached(ttl: int = 300, max_size: int = 1000):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time-to-live in seconds
        max_size: Maximum cache size
    
    Returns:
        Decorated function with caching
    """
    cache = LRUCache(max_size=max_size, ttl=ttl)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        
        # Add cache management methods
        wrapper.cache_clear = cache.clear
        wrapper.cache_stats = cache.get_stats
        
        return wrapper
    
    return decorator


def timed(func: Callable) -> Callable:
    """
    Decorator for timing function execution
    
    Args:
        func: Function to time
    
    Returns:
        Decorated function with timing
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.info(f"{func.__name__} executed in {execution_time:.4f}s")
        
        return result
    
    return wrapper


class PerformanceMonitor:
    """
    Performance monitoring utilities
    Tracks execution times and provides statistics
    """
    
    def __init__(self):
        """Initialize performance monitor"""
        self._timings: Dict[str, List[float]] = {}
    
    def record_timing(self, operation: str, duration: float):
        """
        Record timing for an operation
        
        Args:
            operation: Name of operation
            duration: Duration in seconds
        """
        if operation not in self._timings:
            self._timings[operation] = []
        
        self._timings[operation].append(duration)
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics
        
        Args:
            operation: Optional operation name to get stats for.
                      If None, returns stats for all operations.
        
        Returns:
            Dictionary with performance statistics
        """
        if operation:
            if operation not in self._timings:
                return {}
            
            timings = self._timings[operation]
            return self._calculate_stats(operation, timings)
        
        # Return stats for all operations
        all_stats = {}
        for op, timings in self._timings.items():
            all_stats[op] = self._calculate_stats(op, timings)
        
        return all_stats
    
    def _calculate_stats(self, operation: str, timings: List[float]) -> Dict[str, Any]:
        """
        Calculate statistics for timings
        
        Args:
            operation: Operation name
            timings: List of timing values
        
        Returns:
            Dictionary with calculated statistics
        """
        if not timings:
            return {}
        
        sorted_timings = sorted(timings)
        count = len(timings)
        
        return {
            'operation': operation,
            'count': count,
            'min': min(timings),
            'max': max(timings),
            'avg': sum(timings) / count,
            'median': sorted_timings[count // 2],
            'p95': sorted_timings[int(count * 0.95)] if count > 1 else sorted_timings[0],
            'p99': sorted_timings[int(count * 0.99)] if count > 1 else sorted_timings[0],
            'total': sum(timings)
        }
    
    def clear(self, operation: Optional[str] = None):
        """
        Clear timing data
        
        Args:
            operation: Optional operation name to clear.
                      If None, clears all timing data.
        """
        if operation:
            if operation in self._timings:
                del self._timings[operation]
        else:
            self._timings.clear()
    
    def monitor(self, operation: str):
        """
        Context manager for monitoring operation performance
        
        Args:
            operation: Name of operation to monitor
        
        Returns:
            Context manager
        """
        return PerformanceContext(self, operation)


class PerformanceContext:
    """Context manager for performance monitoring"""
    
    def __init__(self, monitor: PerformanceMonitor, operation: str):
        """
        Initialize performance context
        
        Args:
            monitor: Performance monitor instance
            operation: Operation name
        """
        self.monitor = monitor
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        """Start timing"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and record"""
        duration = time.time() - self.start_time
        self.monitor.record_timing(self.operation, duration)
        logger.debug(f"{self.operation} took {duration:.4f}s")


# Global instances
_global_cache = LRUCache()
_global_profiler = MemoryProfiler()
_global_monitor = PerformanceMonitor()


def get_global_cache() -> LRUCache:
    """Get global cache instance"""
    return _global_cache


def get_global_profiler() -> MemoryProfiler:
    """Get global memory profiler instance"""
    return _global_profiler


def get_global_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    return _global_monitor
