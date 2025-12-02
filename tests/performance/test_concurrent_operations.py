"""
Performance Concurrent Operations Testing
Tests system performance with concurrent database operations

Requirements: 16.3
"""

import pytest
import time
import threading
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services.trip_service import TripService


class TestConcurrentOperations:
    """Test concurrent database operations"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database with larger connection pool"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_concurrent.db")
        
        # Use larger pool for concurrent operations
        db_manager = EnhancedDatabaseManager(db_path, pool_size=20, enable_query_cache=True)
        
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
    
    def test_concurrent_inserts(self, trip_service):
        """Test concurrent insert operations"""
        num_threads = 10
        inserts_per_thread = 100
        
        def insert_trips(thread_id: int) -> int:
            """Insert trips in a thread"""
            count = 0
            for i in range(inserts_per_thread):
                try:
                    trip_service.create_trip({
                        'khach_hang': f'Customer_T{thread_id}_{i}',
                        'diem_di': f'Location_A_{thread_id}',
                        'diem_den': f'Location_B_{thread_id}',
                        'gia_ca': 1000000 + i,
                        'khoan_luong': 500000,
                        'chi_phi_khac': 100000,
                        'ghi_chu': f'Thread {thread_id} trip {i}'
                    })
                    count += 1
                except Exception as e:
                    print(f"Thread {thread_id} error: {e}")
            return count
        
        # Execute concurrent inserts
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(insert_trips, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        elapsed_time = time.time() - start_time
        
        # Verify results
        total_inserted = sum(results)
        expected_total = num_threads * inserts_per_thread
        
        assert total_inserted == expected_total, f"Expected {expected_total} inserts, got {total_inserted}"
        assert elapsed_time < 30.0, f"Concurrent inserts took {elapsed_time:.2f}s, expected < 30s"
        
        # Verify in database
        total_count = trip_service.get_total_count()
        assert total_count == expected_total
        
        throughput = total_inserted / elapsed_time
        
        print(f"\nConcurrent Insert Performance:")
        print(f"  Threads: {num_threads}")
        print(f"  Inserts per thread: {inserts_per_thread}")
        print(f"  Total inserts: {total_inserted}")
        print(f"  Time: {elapsed_time:.2f}s")
        print(f"  Throughput: {throughput:.2f} inserts/sec")
    
    def test_concurrent_reads(self, trip_service, temp_db):
        """Test concurrent read operations"""
        # Insert test data
        num_records = 1000
        for i in range(num_records):
            temp_db.insert_trip({
                'ma_chuyen': f'C{i+1:05d}',
                'khach_hang': f'Customer_{i % 50}',
                'diem_di': f'Location_A_{i % 20}',
                'diem_den': f'Location_B_{i % 20}',
                'gia_ca': 1000000,
                'khoan_luong': 500000,
                'chi_phi_khac': 100000,
                'ghi_chu': ''
            })
        
        num_threads = 20
        reads_per_thread = 50
        
        def read_trips(thread_id: int) -> int:
            """Read trips in a thread"""
            count = 0
            for i in range(reads_per_thread):
                try:
                    # Mix of different read operations
                    if i % 3 == 0:
                        trip_service.get_all_trips(page=1, page_size=100)
                    elif i % 3 == 1:
                        trip_service.search_trips({'khach_hang': f'Customer_{i % 50}'})
                    else:
                        trip_service.get_unique_customers()
                    count += 1
                except Exception as e:
                    print(f"Thread {thread_id} read error: {e}")
            return count
        
        # Execute concurrent reads
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(read_trips, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        elapsed_time = time.time() - start_time
        
        # Verify results
        total_reads = sum(results)
        expected_total = num_threads * reads_per_thread
        
        assert total_reads == expected_total, f"Expected {expected_total} reads, got {total_reads}"
        assert elapsed_time < 20.0, f"Concurrent reads took {elapsed_time:.2f}s, expected < 20s"
        
        throughput = total_reads / elapsed_time
        
        print(f"\nConcurrent Read Performance:")
        print(f"  Threads: {num_threads}")
        print(f"  Reads per thread: {reads_per_thread}")
        print(f"  Total reads: {total_reads}")
        print(f"  Time: {elapsed_time:.2f}s")
        print(f"  Throughput: {throughput:.2f} reads/sec")
    
    def test_concurrent_mixed_operations(self, trip_service, temp_db):
        """Test mixed concurrent operations (reads, writes, updates)"""
        # Insert initial data
        initial_records = 500
        trip_ids = []
        for i in range(initial_records):
            trip_id = temp_db.insert_trip({
                'ma_chuyen': f'C{i+1:05d}',
                'khach_hang': f'Customer_{i % 50}',
                'diem_di': 'Location_A',
                'diem_den': 'Location_B',
                'gia_ca': 1000000,
                'khoan_luong': 500000,
                'chi_phi_khac': 100000,
                'ghi_chu': ''
            })
            trip_ids.append(trip_id)
        
        num_threads = 15
        operations_per_thread = 30
        
        def mixed_operations(thread_id: int) -> dict:
            """Perform mixed operations in a thread"""
            stats = {'reads': 0, 'writes': 0, 'updates': 0, 'errors': 0}
            
            for i in range(operations_per_thread):
                try:
                    op_type = i % 3
                    
                    if op_type == 0:  # Read
                        trip_service.get_all_trips(page=1, page_size=50)
                        stats['reads'] += 1
                    elif op_type == 1:  # Write
                        trip_service.create_trip({
                            'khach_hang': f'Customer_T{thread_id}_{i}',
                            'diem_di': 'Location_A',
                            'diem_den': 'Location_B',
                            'gia_ca': 1000000,
                            'khoan_luong': 500000,
                            'chi_phi_khac': 100000,
                            'ghi_chu': f'Thread {thread_id}'
                        })
                        stats['writes'] += 1
                    else:  # Update
                        if trip_ids:
                            trip_id = trip_ids[i % len(trip_ids)]
                            trip_service.update_trip(trip_id, {
                                'ghi_chu': f'Updated by thread {thread_id}'
                            })
                            stats['updates'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    print(f"Thread {thread_id} error: {e}")
            
            return stats
        
        # Execute mixed operations
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(mixed_operations, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        elapsed_time = time.time() - start_time
        
        # Aggregate stats
        total_stats = {
            'reads': sum(r['reads'] for r in results),
            'writes': sum(r['writes'] for r in results),
            'updates': sum(r['updates'] for r in results),
            'errors': sum(r['errors'] for r in results)
        }
        
        total_operations = sum(total_stats.values())
        
        assert total_stats['errors'] == 0, f"Had {total_stats['errors']} errors"
        assert elapsed_time < 30.0, f"Mixed operations took {elapsed_time:.2f}s, expected < 30s"
        
        throughput = total_operations / elapsed_time
        
        print(f"\nConcurrent Mixed Operations Performance:")
        print(f"  Threads: {num_threads}")
        print(f"  Operations per thread: {operations_per_thread}")
        print(f"  Total reads: {total_stats['reads']}")
        print(f"  Total writes: {total_stats['writes']}")
        print(f"  Total updates: {total_stats['updates']}")
        print(f"  Total operations: {total_operations}")
        print(f"  Errors: {total_stats['errors']}")
        print(f"  Time: {elapsed_time:.2f}s")
        print(f"  Throughput: {throughput:.2f} ops/sec")
    
    def test_connection_pool_efficiency(self, temp_db):
        """Test connection pool handles concurrent requests efficiently"""
        num_threads = 30  # More threads than pool size
        queries_per_thread = 20
        
        def execute_queries(thread_id: int) -> float:
            """Execute queries and measure wait time"""
            total_wait = 0.0
            for i in range(queries_per_thread):
                start = time.time()
                temp_db.execute_query("SELECT COUNT(*) as count FROM trips", use_cache=False)
                query_time = time.time() - start
                total_wait += query_time
            return total_wait
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(execute_queries, i) for i in range(num_threads)]
            wait_times = [future.result() for future in as_completed(futures)]
        
        elapsed_time = time.time() - start_time
        
        avg_wait = sum(wait_times) / len(wait_times)
        max_wait = max(wait_times)
        
        print(f"\nConnection Pool Efficiency:")
        print(f"  Threads: {num_threads}")
        print(f"  Queries per thread: {queries_per_thread}")
        print(f"  Total time: {elapsed_time:.2f}s")
        print(f"  Avg thread wait: {avg_wait:.2f}s")
        print(f"  Max thread wait: {max_wait:.2f}s")
        
        # Pool should handle requests without excessive waiting
        assert max_wait < 10.0, f"Max wait time {max_wait:.2f}s is too high"
    
    def test_transaction_isolation(self, trip_service, temp_db):
        """Test that concurrent transactions are properly isolated"""
        num_threads = 10
        
        def concurrent_transaction(thread_id: int) -> bool:
            """Perform transaction in thread"""
            try:
                # Each thread creates a trip and verifies it
                trip = trip_service.create_trip({
                    'khach_hang': f'Customer_T{thread_id}',
                    'diem_di': 'Location_A',
                    'diem_den': 'Location_B',
                    'gia_ca': 1000000 + thread_id,
                    'khoan_luong': 500000,
                    'chi_phi_khac': 100000,
                    'ghi_chu': f'Thread {thread_id}'
                })
                
                # Verify the trip was created correctly
                retrieved = trip_service.get_trip_by_id(trip.id)
                assert retrieved is not None
                assert retrieved.khach_hang == f'Customer_T{thread_id}'
                assert retrieved.gia_ca == 1000000 + thread_id
                
                return True
            except Exception as e:
                print(f"Thread {thread_id} transaction error: {e}")
                return False
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(concurrent_transaction, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        elapsed_time = time.time() - start_time
        
        # All transactions should succeed
        assert all(results), "Some transactions failed"
        assert elapsed_time < 10.0, f"Transactions took {elapsed_time:.2f}s, expected < 10s"
        
        # Verify all records in database
        total_count = trip_service.get_total_count()
        assert total_count == num_threads
        
        print(f"\nTransaction Isolation Test:")
        print(f"  Concurrent transactions: {num_threads}")
        print(f"  Success rate: {sum(results)}/{len(results)}")
        print(f"  Time: {elapsed_time:.2f}s")
        print(f"  All transactions isolated correctly: {all(results)}")
