"""
Performance Memory Usage Testing
Tests memory usage with large datasets

Requirements: 16.3
"""

import pytest
import time
import tempfile
import os
import gc

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services.trip_service import TripService
from src.utils.memory_manager import MemoryMonitor, MemoryManager, TableMemoryOptimizer


class TestMemoryUsage:
    """Test memory usage with large datasets"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_memory.db")
        
        db_manager = EnhancedDatabaseManager(db_path, pool_size=5, enable_query_cache=True)
        
        yield db_manager
        
        # Cleanup
        db_manager.close()
        try:
            os.remove(db_path)
            os.rmdir(temp_dir)
        except:
            pass
    
    @pytest.fixture
    def trip_service(self, temp_db):
        """Create trip service"""
        return TripService(temp_db)
    
    @pytest.fixture
    def memory_monitor(self):
        """Create memory monitor"""
        monitor = MemoryMonitor()
        monitor.reset_baseline()
        return monitor
    
    def test_memory_usage_with_10000_records(self, trip_service, memory_monitor):
        """Test memory usage when loading 10,000 records"""
        # Get baseline memory
        gc.collect()
        time.sleep(0.1)
        memory_monitor.reset_baseline()
        baseline = memory_monitor.get_current_memory()
        
        # Insert 10,000 records
        num_records = 10000
        for i in range(num_records):
            trip_service.create_trip({
                'khach_hang': f'Customer_{i % 100}',
                'diem_di': f'Location_A_{i % 50}',
                'diem_den': f'Location_B_{i % 50}',
                'gia_ca': 1000000,
                'khoan_luong': 500000,
                'chi_phi_khac': 100000,
                'ghi_chu': f'Trip {i}'
            })
        
        # Load all records
        result = trip_service.get_all_trips(page=1, page_size=num_records)
        trips = result['trips']
        
        # Measure memory after loading
        gc.collect()
        time.sleep(0.1)
        after_load = memory_monitor.get_current_memory()
        memory_increase = after_load - baseline
        
        # Calculate memory per record
        memory_per_record = memory_increase / num_records
        
        print(f"\nMemory Usage (10,000 records):")
        print(f"  Baseline: {baseline:.2f} MB")
        print(f"  After load: {after_load:.2f} MB")
        print(f"  Increase: {memory_increase:.2f} MB")
        print(f"  Per record: {memory_per_record*1024:.2f} KB")
        
        # Memory increase should be reasonable (< 200 MB for 10k records)
        assert memory_increase < 200, f"Memory increase {memory_increase:.2f} MB is too high"
        
        # Cleanup
        del trips
        gc.collect()
        
        # Verify memory is released
        time.sleep(0.1)
        after_cleanup = memory_monitor.get_current_memory()
        memory_released = after_load - after_cleanup
        
        print(f"  After cleanup: {after_cleanup:.2f} MB")
        print(f"  Memory released: {memory_released:.2f} MB")
    
    def test_memory_leak_detection(self, trip_service, memory_monitor):
        """Test for memory leaks with repeated operations"""
        gc.collect()
        memory_monitor.reset_baseline()
        
        memory_samples = []
        iterations = 10
        records_per_iteration = 100
        
        for iteration in range(iterations):
            # Create and load records
            for i in range(records_per_iteration):
                trip_service.create_trip({
                    'khach_hang': f'Customer_{iteration}_{i}',
                    'diem_di': 'Location_A',
                    'diem_den': 'Location_B',
                    'gia_ca': 1000000,
                    'khoan_luong': 500000,
                    'chi_phi_khac': 100000,
                    'ghi_chu': ''
                })
            
            # Load and discard
            result = trip_service.get_all_trips(page=1, page_size=100)
            trips = result['trips']
            del trips
            
            # Force garbage collection
            gc.collect()
            time.sleep(0.1)
            
            # Sample memory
            current_memory = memory_monitor.get_current_memory()
            memory_samples.append(current_memory)
        
        # Analyze memory trend
        memory_deltas = [memory_samples[i+1] - memory_samples[i] for i in range(len(memory_samples)-1)]
        avg_delta = sum(memory_deltas) / len(memory_deltas)
        max_delta = max(memory_deltas)
        
        print(f"\nMemory Leak Detection ({iterations} iterations):")
        print(f"  Initial memory: {memory_samples[0]:.2f} MB")
        print(f"  Final memory: {memory_samples[-1]:.2f} MB")
        print(f"  Total increase: {memory_samples[-1] - memory_samples[0]:.2f} MB")
        print(f"  Avg delta per iteration: {avg_delta:.2f} MB")
        print(f"  Max delta: {max_delta:.2f} MB")
        
        # Average delta should be small (< 5 MB per iteration)
        assert avg_delta < 5.0, f"Possible memory leak: avg delta {avg_delta:.2f} MB per iteration"
    
    def test_cache_memory_management(self, temp_db, memory_monitor):
        """Test that cache doesn't consume excessive memory"""
        gc.collect()
        memory_monitor.reset_baseline()
        baseline = memory_monitor.get_current_memory()
        
        # Insert test data
        num_records = 5000
        for i in range(num_records):
            temp_db.insert_trip({
                'ma_chuyen': f'C{i+1:05d}',
                'khach_hang': f'Customer_{i % 100}',
                'diem_di': 'Location_A',
                'diem_den': 'Location_B',
                'gia_ca': 1000000,
                'khoan_luong': 500000,
                'chi_phi_khac': 100000,
                'ghi_chu': ''
            })
        
        # Execute many different queries to fill cache
        for i in range(200):
            temp_db.execute_query(
                "SELECT * FROM trips WHERE khach_hang = ? LIMIT 10",
                (f'Customer_{i % 100}',),
                use_cache=True
            )
        
        # Measure memory with full cache
        gc.collect()
        time.sleep(0.1)
        with_cache = memory_monitor.get_current_memory()
        cache_memory = with_cache - baseline
        
        # Get cache stats
        cache_stats = temp_db.get_cache_stats()
        
        print(f"\nCache Memory Management:")
        print(f"  Baseline: {baseline:.2f} MB")
        print(f"  With cache: {with_cache:.2f} MB")
        print(f"  Cache memory: {cache_memory:.2f} MB")
        print(f"  Cache stats: {cache_stats}")
        
        # Cache should not consume excessive memory (< 50 MB)
        assert cache_memory < 50, f"Cache memory {cache_memory:.2f} MB is too high"
        
        # Clear cache and verify memory is released
        temp_db.invalidate_cache()
        gc.collect()
        time.sleep(0.1)
        after_clear = memory_monitor.get_current_memory()
        
        print(f"  After cache clear: {after_clear:.2f} MB")
        print(f"  Memory released: {with_cache - after_clear:.2f} MB")
    
    def test_memory_manager_functionality(self, memory_monitor):
        """Test memory manager utilities"""
        # Create memory manager
        memory_manager = MemoryManager(
            max_cache_size_mb=50.0,
            auto_gc=False,  # Manual control for testing
            gc_interval_ms=60000
        )
        
        # Register some test caches
        test_cache_1 = {}
        test_cache_2 = {}
        
        memory_manager.cache_manager.register_cache('test_cache_1', test_cache_1, 10.0)
        memory_manager.cache_manager.register_cache('test_cache_2', test_cache_2, 15.0)
        
        # Get cache stats
        cache_stats = memory_manager.cache_manager.get_cache_stats()
        
        print(f"\nMemory Manager Functionality:")
        print(f"  Cache stats: {cache_stats}")
        
        assert cache_stats['total_caches'] == 2
        assert cache_stats['total_size_mb'] == 25.0
        
        # Test cache clearing
        memory_manager.cache_manager.clear_cache('test_cache_1')
        cache_stats = memory_manager.cache_manager.get_cache_stats()
        
        assert cache_stats['total_size_mb'] == 15.0
        
        # Test garbage collection
        gc_stats = memory_manager.gc_manager.collect()
        
        print(f"  GC stats: {gc_stats}")
        assert gc_stats['total_collected'] >= 0
        
        # Get memory report
        memory_report = memory_manager.get_memory_report()
        
        print(f"  Memory report: {memory_report}")
        
        # Check memory health
        health = memory_manager.check_memory_health()
        
        print(f"  Memory health: {health}")
        assert health['status'] in ['healthy', 'warning', 'critical']
        
        # Cleanup
        memory_manager.shutdown()
    
    def test_large_result_set_memory(self, trip_service, memory_monitor):
        """Test memory usage with large result sets"""
        # Insert 5,000 records
        num_records = 5000
        for i in range(num_records):
            trip_service.create_trip({
                'khach_hang': f'Customer_{i % 100}',
                'diem_di': 'Location_A',
                'diem_den': 'Location_B',
                'gia_ca': 1000000,
                'khoan_luong': 500000,
                'chi_phi_khac': 100000,
                'ghi_chu': f'Trip {i}'
            })
        
        gc.collect()
        memory_monitor.reset_baseline()
        baseline = memory_monitor.get_current_memory()
        
        # Load large result set
        result = trip_service.get_all_trips(page=1, page_size=5000)
        trips = result['trips']
        
        gc.collect()
        time.sleep(0.1)
        after_load = memory_monitor.get_current_memory()
        memory_used = after_load - baseline
        
        print(f"\nLarge Result Set Memory:")
        print(f"  Records loaded: {len(trips)}")
        print(f"  Memory used: {memory_used:.2f} MB")
        print(f"  Memory per record: {memory_used/len(trips)*1024:.2f} KB")
        
        # Memory should be reasonable
        assert memory_used < 150, f"Memory usage {memory_used:.2f} MB is too high for {len(trips)} records"
        
        # Test pagination reduces memory
        del trips
        gc.collect()
        memory_monitor.reset_baseline()
        baseline = memory_monitor.get_current_memory()
        
        # Load with pagination
        result = trip_service.get_all_trips(page=1, page_size=100)
        trips_paginated = result['trips']
        
        gc.collect()
        time.sleep(0.1)
        after_paginated = memory_monitor.get_current_memory()
        memory_paginated = after_paginated - baseline
        
        print(f"  Paginated (100 records): {memory_paginated:.2f} MB")
        
        # Paginated should use less memory
        assert memory_paginated < memory_used, "Pagination should reduce memory usage"
    
    def test_memory_with_repeated_queries(self, temp_db, memory_monitor):
        """Test memory doesn't grow with repeated queries"""
        # Insert test data
        num_records = 1000
        for i in range(num_records):
            temp_db.insert_trip({
                'ma_chuyen': f'C{i+1:05d}',
                'khach_hang': f'Customer_{i % 50}',
                'diem_di': 'Location_A',
                'diem_den': 'Location_B',
                'gia_ca': 1000000,
                'khoan_luong': 500000,
                'chi_phi_khac': 100000,
                'ghi_chu': ''
            })
        
        gc.collect()
        memory_monitor.reset_baseline()
        
        memory_samples = []
        
        # Execute same query 100 times
        for i in range(100):
            result = temp_db.execute_query(
                "SELECT * FROM trips WHERE khach_hang = ? LIMIT 50",
                ('Customer_25',),
                use_cache=True
            )
            
            if i % 10 == 0:
                gc.collect()
                time.sleep(0.05)
                memory_samples.append(memory_monitor.get_current_memory())
        
        # Memory should stabilize (not grow linearly)
        memory_growth = memory_samples[-1] - memory_samples[0]
        
        print(f"\nRepeated Query Memory:")
        print(f"  Queries executed: 100")
        print(f"  Initial memory: {memory_samples[0]:.2f} MB")
        print(f"  Final memory: {memory_samples[-1]:.2f} MB")
        print(f"  Growth: {memory_growth:.2f} MB")
        
        # Memory growth should be minimal (< 10 MB)
        assert memory_growth < 10, f"Memory grew {memory_growth:.2f} MB with repeated queries"
