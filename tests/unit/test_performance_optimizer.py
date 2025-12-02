"""
Unit tests for Performance Optimizer
Tests caching, query optimization, and memory profiling utilities
"""
import pytest
import time
import sqlite3
from pathlib import Path

from src.utils.performance_optimizer import (
    LRUCache,
    QueryOptimizer,
    MemoryProfiler,
    PerformanceMonitor,
    cached,
    timed,
    get_global_cache,
    get_global_profiler,
    get_global_monitor
)


class TestLRUCache:
    """Test LRU Cache implementation"""
    
    def test_cache_basic_operations(self):
        """Test basic cache get/set operations"""
        cache = LRUCache(max_size=3, ttl=60)
        
        # Set values
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Get values
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") is None
    
    def test_cache_max_size(self):
        """Test cache respects max size limit"""
        cache = LRUCache(max_size=2, ttl=60)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_cache_ttl(self):
        """Test cache TTL expiration"""
        cache = LRUCache(max_size=10, ttl=1)  # 1 second TTL
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Wait for TTL to expire
        time.sleep(1.1)
        assert cache.get("key1") is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction policy"""
        cache = LRUCache(max_size=2, ttl=60)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Access key1 to make it most recently used
        cache.get("key1")
        
        # Add key3, should evict key2 (least recently used)
        cache.set("key3", "value3")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"
    
    def test_cache_delete(self):
        """Test cache delete operation"""
        cache = LRUCache(max_size=10, ttl=60)
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        cache.delete("key1")
        assert cache.get("key1") is None
    
    def test_cache_clear(self):
        """Test cache clear operation"""
        cache = LRUCache(max_size=10, ttl=60)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = LRUCache(max_size=10, ttl=60)
        
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        stats = cache.get_stats()
        
        assert stats['size'] == 1
        assert stats['max_size'] == 10
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert 'hit_rate' in stats


class TestQueryOptimizer:
    """Test Query Optimizer utilities"""
    
    @pytest.fixture
    def test_db(self, tmp_path):
        """Create a test database"""
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        
        # Create test table
        conn.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER,
                created_at TIMESTAMP
            )
        """)
        
        # Insert test data
        for i in range(100):
            conn.execute(
                "INSERT INTO test_table (name, value, created_at) VALUES (?, ?, datetime('now'))",
                (f"name_{i}", i)
            )
        
        conn.commit()
        yield conn
        conn.close()
    
    def test_analyze_query(self, test_db):
        """Test query analysis"""
        query = "SELECT * FROM test_table WHERE value > ?"
        params = (50,)
        
        result = QueryOptimizer.analyze_query(test_db, query, params)
        
        assert 'query' in result
        assert 'execution_time' in result
        assert 'query_plan' in result
        assert result['execution_time'] >= 0
    
    def test_suggest_indexes(self, test_db):
        """Test index suggestions"""
        suggestions = QueryOptimizer.suggest_indexes(test_db, "test_table")
        
        assert isinstance(suggestions, list)
        # Should suggest indexes for created_at and other columns
        assert any('created_at' in s for s in suggestions)
    
    def test_optimize_query(self):
        """Test query optimization"""
        query = "SELECT * FROM test_table WHERE value > 50"
        optimized = QueryOptimizer.optimize_query(query)
        
        assert isinstance(optimized, str)
        assert optimized.strip() == query


class TestMemoryProfiler:
    """Test Memory Profiler utilities"""
    
    def test_start_stop_tracing(self):
        """Test starting and stopping memory tracing"""
        profiler = MemoryProfiler()
        
        profiler.start_tracing()
        assert profiler._is_tracing
        
        profiler.stop_tracing()
        assert not profiler._is_tracing
    
    def test_take_snapshot(self):
        """Test taking memory snapshots"""
        profiler = MemoryProfiler()
        
        profiler.take_snapshot("snapshot1")
        assert len(profiler._snapshots) == 1
        assert profiler._snapshots[0][0] == "snapshot1"
    
    def test_get_current_memory(self):
        """Test getting current memory usage"""
        profiler = MemoryProfiler()
        
        memory = profiler.get_current_memory()
        
        assert 'current_mb' in memory
        assert 'peak_mb' in memory
        assert 'current_bytes' in memory
        assert 'peak_bytes' in memory
        assert memory['current_mb'] >= 0
    
    def test_get_top_allocations(self):
        """Test getting top memory allocations"""
        profiler = MemoryProfiler()
        profiler.start_tracing()
        
        # Allocate some memory
        data = [i for i in range(1000)]
        
        allocations = profiler.get_top_allocations(top_n=5)
        
        assert isinstance(allocations, list)
        assert len(allocations) <= 5
    
    def test_clear_snapshots(self):
        """Test clearing snapshots"""
        profiler = MemoryProfiler()
        
        profiler.take_snapshot("snapshot1")
        profiler.take_snapshot("snapshot2")
        
        profiler.clear_snapshots()
        assert len(profiler._snapshots) == 0


class TestCachedDecorator:
    """Test cached decorator"""
    
    def test_cached_decorator(self):
        """Test function caching with decorator"""
        call_count = 0
        
        @cached(ttl=60, max_size=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - should execute
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call with same args - should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented
        
        # Different args - should execute
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2
    
    def test_cache_clear_method(self):
        """Test cache clear method on decorated function"""
        @cached(ttl=60, max_size=10)
        def test_function(x):
            return x * 2
        
        test_function(5)
        test_function.cache_clear()
        
        stats = test_function.cache_stats()
        assert stats['size'] == 0
    
    def test_cache_stats_method(self):
        """Test cache stats method on decorated function"""
        @cached(ttl=60, max_size=10)
        def test_function(x):
            return x * 2
        
        test_function(5)
        test_function(5)  # Cache hit
        
        stats = test_function.cache_stats()
        assert stats['hits'] >= 1


class TestTimedDecorator:
    """Test timed decorator"""
    
    def test_timed_decorator(self):
        """Test function timing with decorator"""
        @timed
        def slow_function():
            time.sleep(0.1)
            return "done"
        
        result = slow_function()
        assert result == "done"


class TestPerformanceMonitor:
    """Test Performance Monitor"""
    
    def test_record_timing(self):
        """Test recording timing"""
        monitor = PerformanceMonitor()
        
        monitor.record_timing("operation1", 0.5)
        monitor.record_timing("operation1", 0.3)
        
        stats = monitor.get_stats("operation1")
        
        assert stats['count'] == 2
        assert stats['min'] == 0.3
        assert stats['max'] == 0.5
        assert stats['avg'] == 0.4
    
    def test_get_all_stats(self):
        """Test getting stats for all operations"""
        monitor = PerformanceMonitor()
        
        monitor.record_timing("op1", 0.5)
        monitor.record_timing("op2", 0.3)
        
        all_stats = monitor.get_stats()
        
        assert 'op1' in all_stats
        assert 'op2' in all_stats
    
    def test_clear_specific_operation(self):
        """Test clearing specific operation"""
        monitor = PerformanceMonitor()
        
        monitor.record_timing("op1", 0.5)
        monitor.record_timing("op2", 0.3)
        
        monitor.clear("op1")
        
        assert monitor.get_stats("op1") == {}
        assert monitor.get_stats("op2") != {}
    
    def test_clear_all(self):
        """Test clearing all operations"""
        monitor = PerformanceMonitor()
        
        monitor.record_timing("op1", 0.5)
        monitor.record_timing("op2", 0.3)
        
        monitor.clear()
        
        assert monitor.get_stats() == {}
    
    def test_monitor_context_manager(self):
        """Test performance monitoring context manager"""
        monitor = PerformanceMonitor()
        
        with monitor.monitor("test_operation"):
            time.sleep(0.1)
        
        stats = monitor.get_stats("test_operation")
        
        assert stats['count'] == 1
        assert stats['min'] >= 0.1


class TestGlobalInstances:
    """Test global instance getters"""
    
    def test_get_global_cache(self):
        """Test getting global cache instance"""
        cache = get_global_cache()
        assert isinstance(cache, LRUCache)
    
    def test_get_global_profiler(self):
        """Test getting global profiler instance"""
        profiler = get_global_profiler()
        assert isinstance(profiler, MemoryProfiler)
    
    def test_get_global_monitor(self):
        """Test getting global monitor instance"""
        monitor = get_global_monitor()
        assert isinstance(monitor, PerformanceMonitor)
