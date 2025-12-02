"""
Performance Optimization Demo
Demonstrates the performance optimization features including:
- Query result caching
- Prepared statements
- Background threading
- Debouncing
- Memory management
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import EnhancedDatabaseManager
from src.gui.ui_optimizer import get_ui_optimizer
from src.utils.memory_manager import get_memory_manager


def demo_query_optimization():
    """Demonstrate query optimization with caching"""
    print("\n" + "="*60)
    print("QUERY OPTIMIZATION DEMO")
    print("="*60)
    
    # Initialize database
    db = EnhancedDatabaseManager("data/demo_performance.db")
    
    # First query (cache miss)
    print("\n1. First query (cache miss):")
    start = time.time()
    results1 = db.execute_query("SELECT * FROM trips LIMIT 10")
    time1 = time.time() - start
    print(f"   Query time: {time1*1000:.2f}ms")
    print(f"   Results: {len(results1)} rows")
    
    # Second query (cache hit)
    print("\n2. Second query (cache hit):")
    start = time.time()
    results2 = db.execute_query("SELECT * FROM trips LIMIT 10")
    time2 = time.time() - start
    print(f"   Query time: {time2*1000:.2f}ms")
    print(f"   Results: {len(results2)} rows")
    if time2 > 0:
        print(f"   Speedup: {time1/time2:.1f}x faster")
    else:
        print(f"   Speedup: Very fast (cached)")
    
    # Cache statistics
    print("\n3. Cache statistics:")
    cache_stats = db.get_cache_stats()
    print(f"   Cache size: {cache_stats['size']}/{cache_stats['max_size']}")
    print(f"   Hit rate: {cache_stats['hit_rate']}")
    print(f"   Hits: {cache_stats['hits']}, Misses: {cache_stats['misses']}")
    
    # Query statistics
    print("\n4. Query statistics:")
    query_stats = db.get_query_stats()
    for query, stats in list(query_stats.items())[:3]:
        print(f"   Query: {query[:50]}...")
        print(f"   Count: {stats['count']}, Avg time: {stats['avg_time']*1000:.2f}ms")
    
    # Performance analysis
    print("\n5. Performance analysis:")
    analysis = db.analyze_performance()
    print(f"   Total queries tracked: {len(analysis['query_stats'])}")
    print(f"   Slow queries (>50ms): {len(analysis['slow_queries'])}")
    
    db.close()


def demo_prepared_statements():
    """Demonstrate prepared statements"""
    print("\n" + "="*60)
    print("PREPARED STATEMENTS DEMO")
    print("="*60)
    
    db = EnhancedDatabaseManager("data/demo_performance.db")
    
    # Using prepared statement
    print("\n1. Using prepared statement:")
    start = time.time()
    results = db.execute_prepared_query('get_trips_paginated', (10, 0))
    time_taken = time.time() - start
    print(f"   Query time: {time_taken*1000:.2f}ms")
    print(f"   Results: {len(results)} rows")
    
    # List available prepared statements
    print("\n2. Available prepared statements:")
    statements = db.query_optimizer.prepared_statements.list_all()
    print(f"   Total: {len(statements)}")
    for stmt in statements[:5]:
        print(f"   - {stmt}")
    
    db.close()


def demo_memory_management():
    """Demonstrate memory management"""
    print("\n" + "="*60)
    print("MEMORY MANAGEMENT DEMO")
    print("="*60)
    
    # Get memory manager
    mem_mgr = get_memory_manager(max_cache_size_mb=50.0)
    
    # Memory statistics
    print("\n1. Memory statistics:")
    mem_stats = mem_mgr.monitor.get_memory_stats()
    print(f"   Current memory: {mem_stats['current_mb']:.2f} MB")
    print(f"   Memory usage: {mem_stats['percent']:.1f}%")
    print(f"   Available: {mem_stats['available_mb']:.2f} MB")
    
    # Register a cache
    print("\n2. Registering cache:")
    test_cache = {}
    mem_mgr.cache_manager.register_cache('test_cache', test_cache, 10.0)
    cache_stats = mem_mgr.cache_manager.get_cache_stats()
    print(f"   Total caches: {cache_stats['total_caches']}")
    print(f"   Total size: {cache_stats['total_size_mb']:.2f} MB")
    
    # Garbage collection
    print("\n3. Garbage collection:")
    gc_stats = mem_mgr.gc_manager.collect()
    print(f"   Objects collected: {gc_stats['total_collected']}")
    print(f"   Gen0: {gc_stats['collected']['gen0']}")
    print(f"   Gen1: {gc_stats['collected']['gen1']}")
    print(f"   Gen2: {gc_stats['collected']['gen2']}")
    
    # Memory health check
    print("\n4. Memory health check:")
    health = mem_mgr.check_memory_health()
    print(f"   Status: {health['status']}")
    if health['warnings']:
        print(f"   Warnings: {', '.join(health['warnings'])}")
    if health['recommendations']:
        print(f"   Recommendations: {', '.join(health['recommendations'])}")
    
    # Full report
    print("\n5. Full memory report:")
    report = mem_mgr.get_memory_report()
    print(f"   Memory: {report['memory']['current_mb']:.2f} MB")
    print(f"   Cache: {report['cache']['total_size_mb']:.2f} MB")
    print(f"   GC collections: {report['gc']['collection_count']}")


def demo_ui_optimization():
    """Demonstrate UI optimization features"""
    print("\n" + "="*60)
    print("UI OPTIMIZATION DEMO")
    print("="*60)
    
    # Get UI optimizer
    ui_opt = get_ui_optimizer()
    
    # Debounced action
    print("\n1. Debounced action:")
    print("   Creating debounced search action (300ms delay)")
    
    def search_callback():
        print("   Search executed!")
    
    debounced_search = ui_opt.create_debounced_action(
        'search',
        search_callback,
        delay_ms=300
    )
    
    print("   Triggering search 3 times rapidly...")
    debounced_search.trigger()
    time.sleep(0.1)
    debounced_search.trigger()
    time.sleep(0.1)
    debounced_search.trigger()
    
    print("   Waiting for debounce...")
    time.sleep(0.4)
    
    # Lazy loader
    print("\n2. Lazy loader:")
    
    def load_data(limit, offset):
        # Simulate loading data
        return [f"Item {i}" for i in range(offset, offset + limit)]
    
    lazy_loader = ui_opt.create_lazy_loader(load_data, batch_size=5)
    
    print("   Loading first batch...")
    batch1 = lazy_loader.load_next_batch()
    print(f"   Loaded: {len(batch1)} items")
    
    print("   Loading second batch...")
    batch2 = lazy_loader.load_next_batch()
    print(f"   Loaded: {len(batch2)} items")
    
    print(f"   Total cached: {len(lazy_loader.get_cached_data())} items")
    
    # Background task
    print("\n3. Background task:")
    
    def long_running_task():
        print("   Task started in background...")
        time.sleep(1)
        return "Task completed!"
    
    def on_finished(result):
        print(f"   {result}")
    
    print("   Starting background task...")
    worker = ui_opt.run_in_background(long_running_task, on_finished)
    
    print("   Main thread continues...")
    worker.wait()  # Wait for completion in demo
    
    # Cleanup
    ui_opt.cleanup()


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("PERFORMANCE OPTIMIZATION DEMONSTRATION")
    print("="*60)
    
    try:
        demo_query_optimization()
        demo_prepared_statements()
        demo_memory_management()
        demo_ui_optimization()
        
        print("\n" + "="*60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
