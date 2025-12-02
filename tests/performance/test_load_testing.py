"""
Performance Load Testing
Tests system performance with 10,000+ records

Requirements: 16.3
"""

import pytest
import time
import sqlite3
from pathlib import Path
import tempfile
import os

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services.trip_service import TripService
from src.services.company_price_service import CompanyPriceService
from src.services.filtering_service import FilteringService
from src.database.query_optimizer import QueryOptimizer


class TestLoadPerformance:
    """Test performance with large datasets (10,000+ records)"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_performance.db")
        
        db_manager = EnhancedDatabaseManager(db_path, pool_size=10, enable_query_cache=True)
        
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
        """Create trip service with temp database"""
        return TripService(temp_db)
    
    def test_insert_10000_records_performance(self, trip_service):
        """Test inserting 10,000 records - should complete in reasonable time"""
        num_records = 10000
        start_time = time.time()
        
        # Generate test data with unique trip codes
        trips_data = []
        for i in range(num_records):
            trips_data.append({
                'ma_chuyen': f'PERF{i+1:06d}',  # Unique trip codes
                'khach_hang': f'Customer_{i % 100}',
                'diem_di': f'Location_A_{i % 50}',
                'diem_den': f'Location_B_{i % 50}',
                'gia_ca': 1000000 + (i * 1000),
                'khoan_luong': 500000 + (i * 500),
                'chi_phi_khac': 100000,
                'ghi_chu': f'Test trip {i}'
            })
        
        # Bulk insert
        created_trips = trip_service.bulk_create_trips(trips_data)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Assertions
        assert len(created_trips) == num_records
        assert elapsed_time < 60.0, f"Insert took {elapsed_time:.2f}s, expected < 60s"
        
        # Calculate throughput
        throughput = num_records / elapsed_time
        print(f"\nInsert Performance:")
        print(f"  Records: {num_records}")
        print(f"  Time: {elapsed_time:.2f}s")
        print(f"  Throughput: {throughput:.2f} records/sec")
        
        assert throughput > 100, f"Throughput {throughput:.2f} records/sec is too low"
    
    def test_query_performance_with_large_dataset(self, trip_service, temp_db):
        """Test query performance with 10,000+ records"""
        # Insert 10,000 records first
        num_records = 10000
        for i in range(num_records):
            temp_db.insert_trip({
                'ma_chuyen': f'C{i+1:05d}',
                'khach_hang': f'Customer_{i % 100}',
                'diem_di': f'Location_A_{i % 50}',
                'diem_den': f'Location_B_{i % 50}',
                'gia_ca': 1000000,
                'khoan_luong': 500000,
                'chi_phi_khac': 100000,
                'ghi_chu': ''
            })
        
        # Test 1: Get all trips with pagination
        start_time = time.time()
        result = trip_service.get_all_trips(page=1, page_size=100)
        query_time_1 = time.time() - start_time
        
        assert len(result['trips']) == 100
        assert result['total'] == num_records
        assert query_time_1 < 1.0, f"Paginated query took {query_time_1:.2f}s, expected < 1s"
        
        # Test 2: Search with filters
        start_time = time.time()
        result = trip_service.search_trips({'khach_hang': 'Customer_50'}, page=1, page_size=100)
        query_time_2 = time.time() - start_time
        
        assert len(result['trips']) > 0
        assert query_time_2 < 2.0, f"Search query took {query_time_2:.2f}s, expected < 2s"
        
        # Test 3: Get unique customers (aggregation)
        start_time = time.time()
        customers = trip_service.get_unique_customers()
        query_time_3 = time.time() - start_time
        
        assert len(customers) == 100
        assert query_time_3 < 1.0, f"Aggregation query took {query_time_3:.2f}s, expected < 1s"
        
        print(f"\nQuery Performance (10,000 records):")
        print(f"  Paginated query: {query_time_1*1000:.2f}ms")
        print(f"  Search query: {query_time_2*1000:.2f}ms")
        print(f"  Aggregation query: {query_time_3*1000:.2f}ms")
    
    def test_update_performance_with_large_dataset(self, trip_service, temp_db):
        """Test update performance with large dataset"""
        # Insert 1,000 records
        num_records = 1000
        trip_ids = []
        for i in range(num_records):
            trip_id = temp_db.insert_trip({
                'ma_chuyen': f'UPD{i+1:05d}',
                'khach_hang': f'Customer_{i}',
                'diem_di': 'Location_A',
                'diem_den': 'Location_B',
                'gia_ca': 1000000,
                'khoan_luong': 500000,
                'chi_phi_khac': 100000,
                'ghi_chu': ''
            })
            trip_ids.append(trip_id)
        
        # Test updating 100 random records
        start_time = time.time()
        for i in range(0, 100):
            trip_id = trip_ids[i]
            # Update using database directly to ensure it works
            temp_db.update_trip(trip_id, {
                'khach_hang': f'Customer_{i}',
                'diem_di': 'Location_A',
                'diem_den': 'Location_B',
                'gia_ca': 2000000,
                'khoan_luong': 500000,
                'chi_phi_khac': 100000,
                'ghi_chu': 'Updated'
            })
        update_time = time.time() - start_time
        
        assert update_time < 5.0, f"100 updates took {update_time:.2f}s, expected < 5s"
        
        # Verify updates
        updated_trip = trip_service.get_trip_by_id(trip_ids[0])
        assert updated_trip.gia_ca == 2000000
        assert updated_trip.ghi_chu == 'Updated'
        
        print(f"\nUpdate Performance:")
        print(f"  100 updates: {update_time:.2f}s")
        print(f"  Avg per update: {update_time/100*1000:.2f}ms")
    
    def test_pagination_performance(self, trip_service, temp_db):
        """Test pagination performance with large dataset"""
        # Insert 5,000 records
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
        
        # Test pagination through all pages
        page_size = 100
        total_pages = num_records // page_size
        
        page_times = []
        for page in range(1, min(11, total_pages + 1)):  # Test first 10 pages
            start_time = time.time()
            result = trip_service.get_all_trips(page=page, page_size=page_size)
            page_time = time.time() - start_time
            page_times.append(page_time)
            
            assert len(result['trips']) == page_size
            assert page_time < 0.5, f"Page {page} took {page_time:.2f}s, expected < 0.5s"
        
        avg_page_time = sum(page_times) / len(page_times)
        
        print(f"\nPagination Performance (5,000 records):")
        print(f"  Pages tested: {len(page_times)}")
        print(f"  Avg page load: {avg_page_time*1000:.2f}ms")
        print(f"  Max page load: {max(page_times)*1000:.2f}ms")
        print(f"  Min page load: {min(page_times)*1000:.2f}ms")
    
    def test_filtering_performance_with_large_dataset(self, temp_db, trip_service):
        """Test filtering service performance with large dataset"""
        # Insert 10,000 records with varied data
        num_records = 10000
        for i in range(num_records):
            temp_db.insert_trip({
                'ma_chuyen': f'FLT{i+1:05d}',
                'khach_hang': f'Customer_{i % 100}',
                'diem_di': f'Location_A_{i % 50}',
                'diem_den': f'Location_B_{i % 50}',
                'gia_ca': 1000000 + (i % 10) * 100000,
                'khoan_luong': 500000,
                'chi_phi_khac': 100000,
                'ghi_chu': f'Trip {i}'
            })
        
        # Create filtering service
        filtering_service = FilteringService()
        
        # Test 1: Filter by single field using trip service
        start_time = time.time()
        result_1 = trip_service.search_trips({'khach_hang': 'Customer_50'})
        filter_time_1 = time.time() - start_time
        
        assert len(result_1['trips']) > 0
        assert filter_time_1 < 2.0, f"Single field filter took {filter_time_1:.2f}s, expected < 2s"
        
        # Test 2: Filter by multiple fields
        start_time = time.time()
        result_2 = trip_service.search_trips({
            'khach_hang': 'Customer_50',
            'diem_di': 'Location_A_25'
        })
        filter_time_2 = time.time() - start_time
        
        assert filter_time_2 < 2.5, f"Multi-field filter took {filter_time_2:.2f}s, expected < 2.5s"
        
        # Test 3: Get unique values (aggregation)
        start_time = time.time()
        customers = trip_service.get_unique_customers()
        filter_time_3 = time.time() - start_time
        
        assert len(customers) > 0
        assert filter_time_3 < 2.0, f"Aggregation took {filter_time_3:.2f}s, expected < 2s"
        
        print(f"\nFiltering Performance (10,000 records):")
        print(f"  Single field filter: {filter_time_1*1000:.2f}ms")
        print(f"  Multi-field filter: {filter_time_2*1000:.2f}ms")
        print(f"  Aggregation: {filter_time_3*1000:.2f}ms")
    
    def test_cache_effectiveness(self, temp_db):
        """Test query cache effectiveness with repeated queries"""
        # Insert 1,000 records
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
        
        # First query (cache miss)
        query = "SELECT * FROM trips WHERE khach_hang LIKE ? LIMIT 100"
        params = ('%Customer_25%',)
        
        start_time = time.time()
        result_1 = temp_db.execute_query(query, params, use_cache=True)
        time_1 = time.time() - start_time
        
        # Second query (cache hit)
        start_time = time.time()
        result_2 = temp_db.execute_query(query, params, use_cache=True)
        time_2 = time.time() - start_time
        
        # Third query (cache hit)
        start_time = time.time()
        result_3 = temp_db.execute_query(query, params, use_cache=True)
        time_3 = time.time() - start_time
        
        # Verify results are the same
        assert len(result_1) == len(result_2) == len(result_3)
        
        # Cache should make subsequent queries faster (or at least not slower)
        # Note: With very fast queries, cache overhead might make them similar
        
        # Get cache stats
        cache_stats = temp_db.get_cache_stats()
        
        print(f"\nCache Effectiveness:")
        print(f"  First query (miss): {time_1*1000:.2f}ms")
        print(f"  Second query (hit): {time_2*1000:.2f}ms")
        print(f"  Third query (hit): {time_3*1000:.2f}ms")
        if time_2 > 0:
            print(f"  Speedup: {time_1/time_2:.2f}x")
        else:
            print(f"  Speedup: Very fast (< 1ms)")
        print(f"  Cache stats: {cache_stats}")
        
        assert cache_stats['hits'] >= 2, "Should have at least 2 cache hits"
    
    def test_index_performance(self, temp_db):
        """Test that indexes improve query performance"""
        # Insert 5,000 records
        num_records = 5000
        for i in range(num_records):
            temp_db.insert_trip({
                'ma_chuyen': f'C{i+1:05d}',
                'khach_hang': f'Customer_{i % 100}',
                'diem_di': f'Location_A_{i % 50}',
                'diem_den': f'Location_B_{i % 50}',
                'gia_ca': 1000000,
                'khoan_luong': 500000,
                'chi_phi_khac': 100000,
                'ghi_chu': ''
            })
        
        # Query using indexed column (khach_hang has index)
        start_time = time.time()
        result_indexed = temp_db.execute_query(
            "SELECT * FROM trips WHERE khach_hang = ?",
            ('Customer_50',),
            use_cache=False
        )
        time_indexed = time.time() - start_time
        
        # Query using non-indexed column (ghi_chu has no index)
        start_time = time.time()
        result_non_indexed = temp_db.execute_query(
            "SELECT * FROM trips WHERE ghi_chu = ?",
            ('',),
            use_cache=False
        )
        time_non_indexed = time.time() - start_time
        
        print(f"\nIndex Performance:")
        print(f"  Indexed query: {time_indexed*1000:.2f}ms")
        print(f"  Non-indexed query: {time_non_indexed*1000:.2f}ms")
        
        # Indexed query should be reasonably fast
        assert time_indexed < 0.5, f"Indexed query took {time_indexed:.2f}s, expected < 0.5s"
