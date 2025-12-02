# Performance Optimizer

Caching, query optimization, and memory profiling utilities for improving application performance and monitoring resource usage.

## Features

### 1. LRU Cache
- Least Recently Used (LRU) eviction policy
- Time-to-live (TTL) support
- Size limits
- Hit/miss statistics
- Thread-safe operations

### 2. Query Optimizer
- Query execution analysis
- Index suggestions
- Query plan inspection
- Performance recommendations

### 3. Memory Profiler
- Memory usage tracking
- Snapshot comparison
- Top allocation analysis
- Memory leak detection

### 4. Performance Monitor
- Operation timing
- Statistical analysis (min, max, avg, median, p95, p99)
- Context manager support
- Multi-operation tracking

## Usage Examples

### LRU Cache

```python
from src.utils.performance_optimizer import LRUCache

# Create cache with max size and TTL
cache = LRUCache(max_size=1000, ttl=300)  # 5 minutes TTL

# Set values
cache.set("user:123", {"name": "John", "age": 30})

# Get values
user = cache.get("user:123")

# Delete specific key
cache.delete("user:123")

# Clear all cache
cache.clear()

# Get statistics
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']}")
```

### Cached Decorator

```python
from src.utils.performance_optimizer import cached

@cached(ttl=300, max_size=100)
def expensive_function(param):
    # Expensive computation
    return result

# First call - executes function
result1 = expensive_function(10)

# Second call - returns cached result
result2 = expensive_function(10)

# Clear cache
expensive_function.cache_clear()

# Get cache stats
stats = expensive_function.cache_stats()
```

### Timed Decorator

```python
from src.utils.performance_optimizer import timed

@timed
def slow_operation():
    # Operation to time
    pass

# Automatically logs execution time
slow_operation()
```

### Query Optimizer

```python
from src.utils.performance_optimizer import QueryOptimizer
import sqlite3

conn = sqlite3.connect("database.db")

# Analyze query performance
query = "SELECT * FROM trips WHERE customer = ?"
analysis = QueryOptimizer.analyze_query(conn, query, ("ABC Corp",))
print(f"Execution time: {analysis['execution_time']:.4f}s")
print(f"Query plan: {analysis['query_plan']}")

# Get index suggestions
suggestions = QueryOptimizer.suggest_indexes(conn, "trips")
for suggestion in suggestions:
    print(suggestion)
    # CREATE INDEX idx_trips_customer ON trips(customer)

# Optimize query
optimized = QueryOptimizer.optimize_query(query)
```

### Memory Profiler

```python
from src.utils.performance_optimizer import MemoryProfiler

profiler = MemoryProfiler()

# Start tracing
profiler.start_tracing()

# Take snapshot
profiler.take_snapshot("before")

# ... allocate memory ...

# Take another snapshot
profiler.take_snapshot("after")

# Get current memory usage
memory = profiler.get_current_memory()
print(f"Current: {memory['current_mb']:.2f} MB")
print(f"Peak: {memory['peak_mb']:.2f} MB")

# Compare snapshots
diff = profiler.compare_snapshots("before", "after", top_n=10)
for item in diff:
    print(f"{item['file']}: {item['size_diff_mb']:.2f} MB")

# Get top allocations
allocations = profiler.get_top_allocations(top_n=10)
for alloc in allocations:
    print(f"{alloc['file']}: {alloc['size_mb']:.2f} MB")

# Stop tracing
profiler.stop_tracing()
```

### Performance Monitor

```python
from src.utils.performance_optimizer import PerformanceMonitor

monitor = PerformanceMonitor()

# Using context manager
with monitor.monitor("database_query"):
    # Execute database query
    pass

# Manual recording
monitor.record_timing("api_call", 0.5)

# Get statistics for specific operation
stats = monitor.get_stats("database_query")
print(f"Average: {stats['avg']:.4f}s")
print(f"P95: {stats['p95']:.4f}s")

# Get all statistics
all_stats = monitor.get_stats()
for operation, stats in all_stats.items():
    print(f"{operation}: {stats['avg']:.4f}s")

# Clear statistics
monitor.clear("database_query")  # Clear specific
monitor.clear()  # Clear all
```

### Global Instances

```python
from src.utils.performance_optimizer import (
    get_global_cache,
    get_global_profiler,
    get_global_monitor
)

# Use global cache instance
cache = get_global_cache()
cache.set("key", "value")

# Use global profiler instance
profiler = get_global_profiler()
memory = profiler.get_current_memory()

# Use global monitor instance
monitor = get_global_monitor()
with monitor.monitor("operation"):
    pass
```

## Integration with Services

### Caching Database Queries

```python
from src.utils.performance_optimizer import cached

class TripService:
    @cached(ttl=300, max_size=100)
    def get_unique_customers(self):
        # Expensive database query
        return self.db.execute_query("SELECT DISTINCT customer FROM trips")
```

### Monitoring Performance

```python
from src.utils.performance_optimizer import get_global_monitor

class TripService:
    def __init__(self, db_manager):
        self.db = db_manager
        self.monitor = get_global_monitor()
    
    def create_trip(self, trip_data):
        with self.monitor.monitor("create_trip"):
            # Create trip logic
            pass
```

### Profiling Memory Usage

```python
from src.utils.performance_optimizer import get_global_profiler

profiler = get_global_profiler()
profiler.start_tracing()

# Take snapshot before operation
profiler.take_snapshot("before_import")

# Import large dataset
import_service.import_excel(large_file)

# Take snapshot after operation
profiler.take_snapshot("after_import")

# Compare memory usage
diff = profiler.compare_snapshots("before_import", "after_import")
```

## Best Practices

### Caching
- Use appropriate TTL based on data freshness requirements
- Set reasonable max_size to prevent memory issues
- Clear cache when underlying data changes
- Monitor hit rates to optimize cache effectiveness

### Query Optimization
- Analyze slow queries regularly
- Implement suggested indexes
- Use EXPLAIN QUERY PLAN to understand query execution
- Add LIMIT clauses to prevent large result sets

### Memory Profiling
- Profile during development and testing
- Take snapshots at key points in execution
- Compare snapshots to identify memory leaks
- Monitor peak memory usage for large operations

### Performance Monitoring
- Monitor critical operations
- Set up alerts for slow operations
- Track trends over time
- Use percentiles (P95, P99) for SLA monitoring

## Configuration

### Cache Configuration
```python
# Small cache for frequently accessed data
cache = LRUCache(max_size=100, ttl=60)

# Large cache for expensive computations
cache = LRUCache(max_size=10000, ttl=3600)

# Short-lived cache for real-time data
cache = LRUCache(max_size=1000, ttl=30)
```

### Performance Thresholds
```python
# Set thresholds for slow operations
SLOW_QUERY_THRESHOLD = 0.1  # 100ms
SLOW_API_THRESHOLD = 1.0    # 1 second

# Monitor and alert
stats = monitor.get_stats("database_query")
if stats['p95'] > SLOW_QUERY_THRESHOLD:
    logger.warning(f"Slow queries detected: P95={stats['p95']:.4f}s")
```

## Performance Metrics

### Cache Metrics
- **Hit Rate**: Percentage of cache hits vs total requests
- **Size**: Current number of cached items
- **Evictions**: Number of items evicted due to size/TTL

### Query Metrics
- **Execution Time**: Time to execute query
- **Query Plan**: Database execution plan
- **Index Usage**: Whether indexes are being used

### Memory Metrics
- **Current Memory**: Current memory usage
- **Peak Memory**: Maximum memory usage
- **Allocations**: Number and size of allocations

### Performance Metrics
- **Min/Max/Avg**: Basic statistics
- **Median**: 50th percentile
- **P95/P99**: 95th and 99th percentiles
- **Count**: Number of operations

## Troubleshooting

### High Memory Usage
1. Check top allocations with `get_top_allocations()`
2. Compare snapshots to identify leaks
3. Clear caches if memory is constrained
4. Reduce cache max_size

### Slow Queries
1. Analyze query with `analyze_query()`
2. Check if indexes are being used
3. Implement suggested indexes
4. Add LIMIT clauses

### Low Cache Hit Rate
1. Check cache stats with `get_stats()`
2. Increase cache size if evictions are high
3. Increase TTL if data doesn't change frequently
4. Review cache key generation

## See Also

- [Error Handler](README_ERROR_HANDLER.md)
- [Excel Service](../services/README_EXCEL_SERVICE.md)
- [Filtering Service](../services/README_FILTERING_SERVICE.md)
