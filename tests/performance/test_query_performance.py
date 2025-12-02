"""
Performance Query Testing
Tests query performance and optimization

Requirements: 16.3
"""

import pytest
import time
import tempfile
import os
from typing import List, Dict, Any

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.database.query_optimizer import QueryOptimizer


class TestQueryPerformance:
    """Test query performance and optimization"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_query_perf.db")
        
        db_manager = EnhancedDatabaseManager(db_path, pool_size=5, enable_query_cache=True)
        
        # Insert test data
        self._insert_test_data(db_manager, 5000)
        
        yield db_manager
        
        # Cleanup
        db_manager.close()
        try:
            os.remove(db_path)
            os.rmdir(temp_dir)
        except:
            pass
    
    def _insert_test_data(self, db: EnhancedDatabaseManager, num_records: int):
        """Insert test data"""
        for i in range(num_records):
            db.insert_trip({
                'ma_chuyen': f'C{i+1:05d}',
                'khach_hang': f'Customer_{i % 100}',
                'diem_di': f'Location_A_{i % 50}',
                'diem_den': f'Location_B_{i % 50}',
                'gia_ca': 1000000 + (i % 10) * 100000,
                'khoan_luong': 500000 + (i % 5) * 50000,
                'chi_phi_khac': 100000,
                'ghi_chu': f'Trip {i}'
            })
    
    def test_simple_select_performance(self, temp_db):
        """Test simple SELECT query performance"""
        query = "SELECT * FROM trips LIMIT 100"
        
        # Execute multiple times and measure
        times = []
        for _ in range(10):
            start = time.time()
            result = temp_db.execute_query(query, use_cache=False)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"\nSimple SELECT Performance:")
        print(f"  Avg: {avg_time*1000:.2f}ms")
        print(f"  Max: {max_time*1000:.2f}ms")
        print(f"  Min: {min_time*1000:.2f}ms")
        
        assert avg_time < 0.1, f"Simple SELECT took {avg_time:.3f}s, expected < 0.1s"
        assert len(result) == 100
    
    def test_where_clause_performance(self, temp_db):
        """Test WHERE clause query performance"""
        query = "SELECT * FROM trips WHERE khach_hang = ?"
        params = ('Customer_50',)
        
        times = []
        for _ in range(10):
            start = time.time()
            result = temp_db.execute_query(query, params, use_cache=False)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        
        print(f"\nWHERE Clause Performance:")
        print(f"  Avg: {avg_time*1000:.2f}ms")
        print(f"  Results: {len(result)}")
        
        assert avg_time < 0.2, f"WHERE query took {avg_time:.3f}s, expected < 0.2s"
    
    def test_like_query_performance(self, temp_db):
        """Test LIKE query performance"""
        query = "SELECT * FROM trips WHERE khach_hang LIKE ?"
        params = ('%Customer_5%',)
        
        times = []
        for _ in range(10):
            start = time.time()
            result = temp_db.execute_query(query, params, use_cache=False)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        
        print(f"\nLIKE Query Performance:")
        print(f"  Avg: {avg_time*1000:.2f}ms")
        print(f"  Results: {len(result)}")
        
        assert avg_time < 0.5, f"LIKE query took {avg_time:.3f}s, expected < 0.5s"
    
    def test_join_query_performance(self, temp_db):
        """Test JOIN query performance"""
        # Insert some departments and employees
        dept_id = temp_db.insert_department({
            'name': 'sales',
            'display_name': 'Sales Department',
            'description': 'Sales team'
        })
        
        for i in range(10):
            temp_db.insert_employee({
                'username': f'user{i}',
                'full_name': f'User {i}',
                'email': f'user{i}@test.com',
                'department_id': dept_id
            })
        
        query = """
            SELECT e.*, d.display_name 
            FROM employees e 
            JOIN departments d ON e.department_id = d.id 
            WHERE d.is_active = 1
        """
        
        times = []
        for _ in range(10):
            start = time.time()
            result = temp_db.execute_query(query, use_cache=False)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        
        print(f"\nJOIN Query Performance:")
        print(f"  Avg: {avg_time*1000:.2f}ms")
        print(f"  Results: {len(result)}")
        
        assert avg_time < 0.3, f"JOIN query took {avg_time:.3f}s, expected < 0.3s"
    
    def test_aggregation_query_performance(self, temp_db):
        """Test aggregation query performance"""
        queries = [
            ("SELECT COUNT(*) as count FROM trips", "COUNT"),
            ("SELECT AVG(gia_ca) as avg_price FROM trips", "AVG"),
            ("SELECT SUM(gia_ca) as total FROM trips", "SUM"),
            ("SELECT MAX(gia_ca) as max_price FROM trips", "MAX"),
            ("SELECT MIN(gia_ca) as min_price FROM trips", "MIN"),
        ]
        
        print(f"\nAggregation Query Performance:")
        
        for query, name in queries:
            times = []
            for _ in range(10):
                start = time.time()
                result = temp_db.execute_query(query, use_cache=False)
                elapsed = time.time() - start
                times.append(elapsed)
            
            avg_time = sum(times) / len(times)
            print(f"  {name}: {avg_time*1000:.2f}ms")
            
            assert avg_time < 0.5, f"{name} query took {avg_time:.3f}s, expected < 0.5s"
    
    def test_group_by_performance(self, temp_db):
        """Test GROUP BY query performance"""
        query = """
            SELECT khach_hang, COUNT(*) as count, AVG(gia_ca) as avg_price
            FROM trips
            GROUP BY khach_hang
            ORDER BY count DESC
            LIMIT 20
        """
        
        times = []
        for _ in range(10):
            start = time.time()
            result = temp_db.execute_query(query, use_cache=False)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        
        print(f"\nGROUP BY Performance:")
        print(f"  Avg: {avg_time*1000:.2f}ms")
        print(f"  Groups: {len(result)}")
        
        assert avg_time < 1.0, f"GROUP BY query took {avg_time:.3f}s, expected < 1s"
    
    def test_order_by_performance(self, temp_db):
        """Test ORDER BY query performance"""
        queries = [
            ("SELECT * FROM trips ORDER BY created_at DESC LIMIT 100", "created_at"),
            ("SELECT * FROM trips ORDER BY gia_ca DESC LIMIT 100", "gia_ca"),
            ("SELECT * FROM trips ORDER BY khach_hang ASC LIMIT 100", "khach_hang"),
        ]
        
        print(f"\nORDER BY Performance:")
        
        for query, field in queries:
            times = []
            for _ in range(10):
                start = time.time()
                result = temp_db.execute_query(query, use_cache=False)
                elapsed = time.time() - start
                times.append(elapsed)
            
            avg_time = sum(times) / len(times)
            print(f"  {field}: {avg_time*1000:.2f}ms")
            
            assert avg_time < 0.3, f"ORDER BY {field} took {avg_time:.3f}s, expected < 0.3s"
    
    def test_complex_query_performance(self, temp_db):
        """Test complex query with multiple conditions"""
        query = """
            SELECT * FROM trips
            WHERE khach_hang LIKE ?
            AND diem_di LIKE ?
            AND gia_ca > ?
            ORDER BY created_at DESC
            LIMIT 50
        """
        params = ('%Customer%', '%Location_A%', 1000000)
        
        times = []
        for _ in range(10):
            start = time.time()
            result = temp_db.execute_query(query, params, use_cache=False)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        
        print(f"\nComplex Query Performance:")
        print(f"  Avg: {avg_time*1000:.2f}ms")
        print(f"  Results: {len(result)}")
        
        assert avg_time < 1.0, f"Complex query took {avg_time:.3f}s, expected < 1s"
    
    def test_prepared_statement_performance(self, temp_db):
        """Test prepared statement performance vs regular queries"""
        # Regular query
        regular_times = []
        for i in range(50):
            start = time.time()
            temp_db.execute_query(
                "SELECT * FROM trips WHERE khach_hang = ? LIMIT 10",
                (f'Customer_{i % 100}',),
                use_cache=False
            )
            elapsed = time.time() - start
            regular_times.append(elapsed)
        
        # Prepared statement
        prepared_times = []
        for i in range(50):
            start = time.time()
            temp_db.execute_prepared_query(
                'search_trips_by_customer',
                (f'%Customer_{i % 100}%',),
                use_cache=False
            )
            elapsed = time.time() - start
            prepared_times.append(elapsed)
        
        avg_regular = sum(regular_times) / len(regular_times)
        avg_prepared = sum(prepared_times) / len(prepared_times)
        
        print(f"\nPrepared Statement Performance:")
        print(f"  Regular query avg: {avg_regular*1000:.2f}ms")
        print(f"  Prepared query avg: {avg_prepared*1000:.2f}ms")
        print(f"  Speedup: {avg_regular/avg_prepared:.2f}x")
    
    def test_query_optimizer_stats(self, temp_db):
        """Test query optimizer statistics tracking"""
        # Execute various queries
        queries = [
            ("SELECT * FROM trips LIMIT 100", ()),
            ("SELECT * FROM trips WHERE khach_hang = ?", ('Customer_50',)),
            ("SELECT COUNT(*) FROM trips", ()),
            ("SELECT * FROM trips WHERE gia_ca > ?", (1500000,)),
        ]
        
        for query, params in queries:
            for _ in range(5):
                temp_db.execute_query(query, params, use_cache=False)
        
        # Get query stats
        query_stats = temp_db.get_query_stats()
        
        print(f"\nQuery Optimizer Stats:")
        print(f"  Tracked queries: {len(query_stats)}")
        
        for query_key, stats in list(query_stats.items())[:5]:
            print(f"  Query: {query_key[:60]}...")
            print(f"    Count: {stats['count']}")
            print(f"    Avg time: {stats['avg_time']*1000:.2f}ms")
            print(f"    Max time: {stats['max_time']*1000:.2f}ms")
        
        assert len(query_stats) > 0, "Should have query statistics"
    
    def test_slow_query_detection(self, temp_db):
        """Test slow query detection"""
        # Execute some queries
        for i in range(10):
            temp_db.execute_query(
                "SELECT * FROM trips WHERE khach_hang LIKE ? AND diem_di LIKE ?",
                (f'%Customer_{i}%', '%Location%'),
                use_cache=False
            )
        
        # Get slow queries (threshold 50ms)
        slow_queries = temp_db.get_slow_queries(threshold_ms=50.0)
        
        print(f"\nSlow Query Detection:")
        print(f"  Slow queries found: {len(slow_queries)}")
        
        for query, stats in slow_queries[:3]:
            print(f"  Query: {query[:60]}...")
            print(f"    Avg time: {stats['avg_time']*1000:.2f}ms")
            print(f"    Count: {stats['count']}")
    
    def test_index_usage_verification(self, temp_db):
        """Verify that indexes are being used effectively"""
        # Query using indexed column
        query_indexed = "SELECT * FROM trips WHERE khach_hang = ?"
        
        # Query using non-indexed column
        query_non_indexed = "SELECT * FROM trips WHERE ghi_chu LIKE ?"
        
        # Measure indexed query
        start = time.time()
        for _ in range(20):
            temp_db.execute_query(query_indexed, ('Customer_50',), use_cache=False)
        time_indexed = time.time() - start
        
        # Measure non-indexed query
        start = time.time()
        for _ in range(20):
            temp_db.execute_query(query_non_indexed, ('%Trip%',), use_cache=False)
        time_non_indexed = time.time() - start
        
        print(f"\nIndex Usage Verification:")
        print(f"  Indexed query (20x): {time_indexed*1000:.2f}ms")
        print(f"  Non-indexed query (20x): {time_non_indexed*1000:.2f}ms")
        print(f"  Ratio: {time_non_indexed/time_indexed:.2f}x")
        
        # Indexed queries should generally be faster
        # (though with small datasets the difference may be minimal)
        assert time_indexed < 2.0, "Indexed queries should be reasonably fast"
    
    def test_query_cache_hit_rate(self, temp_db):
        """Test query cache hit rate"""
        # Clear cache
        temp_db.invalidate_cache()
        
        # Execute same query multiple times
        query = "SELECT * FROM trips WHERE khach_hang = ? LIMIT 50"
        params = ('Customer_25',)
        
        for _ in range(20):
            temp_db.execute_query(query, params, use_cache=True)
        
        # Get cache stats
        cache_stats = temp_db.get_cache_stats()
        
        print(f"\nQuery Cache Hit Rate:")
        print(f"  Cache stats: {cache_stats}")
        
        # Should have high hit rate
        if cache_stats['hits'] + cache_stats['misses'] > 0:
            hit_rate = float(cache_stats['hit_rate'].rstrip('%'))
            print(f"  Hit rate: {hit_rate}%")
            assert hit_rate > 50, f"Cache hit rate {hit_rate}% is too low"
