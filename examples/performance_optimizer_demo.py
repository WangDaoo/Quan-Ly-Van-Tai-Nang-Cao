"""
Performance Optimizer Demo
Demonstrates usage of caching, query optimization, and memory profiling utilities
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import sqlite3

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


def demo_lru_cache():
    """Demonstrate LRU Cache usage"""
    print("\n=== LRU Cache Demo ===")
    
    cache = LRUCache(max_size=3, ttl=60)
    
    # Set values
    cache.set("user:1", {"name": "John", "age": 30})
    cache.set("user:2", {"name": "Jane", "age": 25})
    cache.set("user:3", {"name": "Bob", "age": 35})
    
    # Get values
    print(f"User 1: {cache.get('user:1')}")
    print(f"User 2: {cache.get('user:2')}")
    
    # Add another item (will evict least recently used)
    cache.set("user:4", {"name": "Alice", "age": 28})
    
    print(f"User 3 (evicted): {cache.get('user:3')}")
    print(f"User 4: {cache.get('user:4')}")
    
    # Show cache stats
    stats = cache.get_stats()
    print(f"\nCache Stats: {stats}")


def demo_cached_decorator():
    """Demonstrate cached decorator"""
    print("\n=== Cached Decorator Demo ===")
    
    @cached(ttl=60, max_size=100)
    def expensive_calculation(n):
        """Simulate expensive calculation"""
        print(f"  Computing factorial of {n}...")
        time.sleep(0.5)  # Simulate slow operation
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result
    
    # First call - will compute
    print("First call:")
    result1 = expensive_calculation(10)
    print(f"Result: {result1}")
    
    # Second call - will use cache
    print("\nSecond call (cached):")
    result2 = expensive_calculation(10)
    print(f"Result: {result2}")
    
    # Show cache stats
    print(f"\nCache Stats: {expensive_calculation.cache_stats()}")


def demo_timed_decorator():
    """Demonstrate timed decorator"""
    print("\n=== Timed Decorator Demo ===")
    
    @timed
    def process_data(items):
        """Simulate data processing"""
        time.sleep(0.2)
        return [item * 2 for item in items]
    
    result = process_data([1, 2, 3, 4, 5])
    print(f"Result: {result}")


def demo_query_optimizer():
    """Demonstrate Query Optimizer"""
    print("\n=== Query Optimizer Demo ===")
    
    # Create temporary database
    db_path = Path("data/demo_performance.db")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    
    # Create test table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert test data
    for i in range(100):
        conn.execute(
            "INSERT OR IGNORE INTO products (id, name, price, category) VALUES (?, ?, ?, ?)",
            (i, f"Product {i}", 10.0 + i, f"Category {i % 5}")
        )
    conn.commit()
    
    # Analyze query
    query = "SELECT * FROM products WHERE price > ? AND category = ?"
    params = (50.0, "Category 1")
    
    print("Analyzing query...")
    analysis = QueryOptimizer.analyze_query(conn, query, params)
    print(f"Execution time: {analysis['execution_time']:.4f}s")
    print(f"Query plan: {analysis['query_plan']}")
    
    # Suggest indexes
    print("\nSuggesting indexes...")
    suggestions = QueryOptimizer.suggest_indexes(conn, "products")
    for suggestion in suggestions:
        print(f"  {suggestion}")
    
    conn.close()


def demo_memory_profiler():
    """Demonstrate Memory Profiler"""
    print("\n=== Memory Profiler Demo ===")
    
    profiler = MemoryProfiler()
    profiler.start_tracing()
    
    # Take initial snapshot
    profiler.take_snapshot("start")
    
    # Allocate some memory
    print("Allocating memory...")
    data = []
    for i in range(10000):
        data.append({"id": i, "value": f"item_{i}" * 10})
    
    # Take second snapshot
    profiler.take_snapshot("after_allocation")
    
    # Show current memory
    memory = profiler.get_current_memory()
    print(f"Current memory: {memory['current_mb']:.2f} MB")
    print(f"Peak memory: {memory['peak_mb']:.2f} MB")
    
    # Show top allocations
    print("\nTop memory allocations:")
    allocations = profiler.get_top_allocations(top_n=5)
    for i, alloc in enumerate(allocations, 1):
        print(f"  {i}. {alloc['size_mb']:.2f} MB - {alloc['count']} objects")
    
    profiler.stop_tracing()


def demo_performance_monitor():
    """Demonstrate Performance Monitor"""
    print("\n=== Performance Monitor Demo ===")
    
    monitor = PerformanceMonitor()
    
    # Monitor operations using context manager
    print("Monitoring operations...")
    
    for i in range(5):
        with monitor.monitor("database_query"):
            time.sleep(0.1 + i * 0.02)
    
    for i in range(3):
        with monitor.monitor("api_call"):
            time.sleep(0.2)
    
    # Get statistics
    print("\nPerformance Statistics:")
    all_stats = monitor.get_stats()
    
    for operation, stats in all_stats.items():
        print(f"\n{operation}:")
        print(f"  Count: {stats['count']}")
        print(f"  Min: {stats['min']:.4f}s")
        print(f"  Max: {stats['max']:.4f}s")
        print(f"  Avg: {stats['avg']:.4f}s")
        print(f"  Median: {stats['median']:.4f}s")
        print(f"  P95: {stats['p95']:.4f}s")


def demo_global_instances():
    """Demonstrate global instances"""
    print("\n=== Global Instances Demo ===")
    
    # Use global cache
    cache = get_global_cache()
    cache.set("global_key", "global_value")
    print(f"Global cache value: {cache.get('global_key')}")
    
    # Use global profiler
    profiler = get_global_profiler()
    memory = profiler.get_current_memory()
    print(f"Global profiler - Current memory: {memory['current_mb']:.2f} MB")
    
    # Use global monitor
    monitor = get_global_monitor()
    with monitor.monitor("global_operation"):
        time.sleep(0.1)
    
    stats = monitor.get_stats("global_operation")
    print(f"Global monitor - Operation count: {stats['count']}")


def main():
    """Run all demos"""
    print("=" * 60)
    print("Performance Optimizer Demo")
    print("=" * 60)
    
    demo_lru_cache()
    demo_cached_decorator()
    demo_timed_decorator()
    demo_query_optimizer()
    demo_memory_profiler()
    demo_performance_monitor()
    demo_global_instances()
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
