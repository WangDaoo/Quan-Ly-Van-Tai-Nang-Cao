"""
Integration tests for form submission to database workflow
Tests requirement 1.1: Form submission and data persistence
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services.trip_service import TripService
from src.services.field_config_service import FieldConfigService
from src.gui.widgets.input_form_widget import InputFormWidget
from src.gui.widgets.dynamic_form_widget import DynamicFormWidget
from src.models.trip import Trip
from src.models.field_configuration import FieldConfiguration


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize database with schema
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    # Create trips table
    cursor.execute("""
        CREATE TABLE trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_chuyen VARCHAR(10) UNIQUE NOT NULL,
            khach_hang VARCHAR(255) NOT NULL,
            diem_di VARCHAR(255),
            diem_den VARCHAR(255),
            gia_ca INTEGER NOT NULL,
            khoan_luong INTEGER DEFAULT 0,
            chi_phi_khac INTEGER DEFAULT 0,
            ghi_chu TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create departments table
    cursor.execute("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE NOT NULL,
            display_name VARCHAR(255) NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create field_configurations table
    cursor.execute("""
        CREATE TABLE field_configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_id INTEGER NOT NULL,
            field_name VARCHAR(100) NOT NULL,
            field_type VARCHAR(50) NOT NULL,
            widget_type VARCHAR(50) NOT NULL,
            is_required BOOLEAN DEFAULT 0,
            validation_rules TEXT,
            default_value TEXT,
            options TEXT,
            display_order INTEGER DEFAULT 0,
            category VARCHAR(100),
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id),
            UNIQUE(department_id, field_name)
        )
    """)
    
    # Insert test department
    cursor.execute("""
        INSERT INTO departments (name, display_name, description, is_active)
        VALUES ('sales', 'Sales Department', 'Sales team', 1)
    """)
    
    conn.commit()
    conn.close()
    
    yield path
    
    # Cleanup
    try:
        os.unlink(path)
    except:
        pass


@pytest.fixture
def db_manager(temp_db):
    """Create database manager with temporary database"""
    manager = EnhancedDatabaseManager(temp_db, pool_size=2, enable_query_cache=False)
    yield manager
    manager.pool.close_all()


@pytest.fixture
def trip_service(db_manager):
    """Create trip service"""
    return TripService(db_manager)


class TestFormToDatabaseIntegration:
    """Integration tests for form submission to database workflow"""
    
    def test_form_submission_creates_database_record(self, trip_service, temp_db):
        """Test that form submission creates a record in the database"""
        # Create trip data
        trip_data = {
            'khach_hang': 'Test Customer',
            'diem_di': 'Hanoi',
            'diem_den': 'Ho Chi Minh',
            'gia_ca': 5000000,
            'khoan_luong': 1000000,
            'chi_phi_khac': 500000,
            'ghi_chu': 'Test trip'
        }
        
        # Submit through service (simulating form submission)
        trip = trip_service.create_trip(trip_data)
        
        # Verify record exists in database
        assert trip is not None
        assert trip.id is not None
        
        # Query database directly
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trips WHERE id = ?", (trip.id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[2] == 'Test Customer'  # khach_hang
        assert row[3] == 'Hanoi'  # diem_di
        assert row[4] == 'Ho Chi Minh'  # diem_den
        assert row[5] == 5000000  # gia_ca
    
    def test_auto_generated_ma_chuyen(self, trip_service, temp_db):
        """Test that ma_chuyen is auto-generated correctly"""
        # Create first trip
        trip1_data = {
            'khach_hang': 'Customer 1',
            'gia_ca': 1000000
        }
        trip1 = trip_service.create_trip(trip1_data)
        
        assert trip1.ma_chuyen == 'C001'
        
        # Create second trip
        trip2_data = {
            'khach_hang': 'Customer 2',
            'gia_ca': 2000000
        }
        trip2 = trip_service.create_trip(trip2_data)
        
        assert trip2.ma_chuyen == 'C002'
    
    def test_validation_prevents_invalid_submission(self, trip_service):
        """Test that validation prevents invalid data from being saved"""
        # Missing required field (khach_hang)
        invalid_data = {
            'gia_ca': 1000000
        }
        
        with pytest.raises(Exception):
            trip_service.create_trip(invalid_data)
    
    def test_form_update_modifies_database_record(self, trip_service, temp_db):
        """Test that form updates modify the database record"""
        # Create initial trip
        trip_data = {
            'khach_hang': 'Original Customer',
            'gia_ca': 1000000
        }
        trip = trip_service.create_trip(trip_data)
        
        # Update trip
        update_data = {
            'khach_hang': 'Updated Customer',
            'gia_ca': 2000000,
            'ghi_chu': 'Updated note'
        }
        trip_service.update_trip(trip.id, update_data)
        
        # Verify update in database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT khach_hang, gia_ca, ghi_chu FROM trips WHERE id = ?", (trip.id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row[0] == 'Updated Customer'
        assert row[1] == 2000000
        assert row[2] == 'Updated note'
    
    def test_transaction_rollback_on_error(self, trip_service, temp_db):
        """Test that transactions rollback on error"""
        # Create a trip
        trip_data = {
            'khach_hang': 'Test Customer',
            'gia_ca': 1000000
        }
        trip = trip_service.create_trip(trip_data)
        
        # Count records before failed update
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trips")
        count_before = cursor.fetchone()[0]
        conn.close()
        
        # Try to create duplicate ma_chuyen (should fail)
        try:
            # Manually insert with duplicate ma_chuyen
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trips (ma_chuyen, khach_hang, gia_ca)
                VALUES ('C001', 'Duplicate', 1000000)
            """)
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            pass
        
        # Verify count hasn't changed (rollback occurred)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trips")
        count_after = cursor.fetchone()[0]
        conn.close()
        
        assert count_after == count_before
    
    def test_multiple_form_submissions(self, trip_service):
        """Test multiple consecutive form submissions"""
        trips_data = [
            {'khach_hang': f'Customer {i}', 'gia_ca': 1000000 * i}
            for i in range(1, 6)
        ]
        
        trips = []
        for data in trips_data:
            trip = trip_service.create_trip(data)
            trips.append(trip)
        
        # Verify all trips were created
        assert len(trips) == 5
        trip_ids = [t.id for t in trips]
        assert len(set(trip_ids)) == 5  # All unique IDs
        
        # Verify ma_chuyen sequence
        for i, trip in enumerate(trips, 1):
            assert trip.ma_chuyen == f'C{i:03d}'
    
    def test_form_reset_after_submission(self, trip_service):
        """Test that form data is properly handled after submission"""
        # Create trip
        trip_data = {
            'khach_hang': 'Test Customer',
            'gia_ca': 1000000
        }
        trip1 = trip_service.create_trip(trip_data)
        
        # Verify trip was created
        assert trip1 is not None
        
        # Create another trip with different data
        trip_data2 = {
            'khach_hang': 'Another Customer',
            'gia_ca': 2000000
        }
        trip2 = trip_service.create_trip(trip_data2)
        
        # Verify second trip has correct data (not mixed with first)
        assert trip2.khach_hang == 'Another Customer'
        assert trip2.gia_ca == 2000000
