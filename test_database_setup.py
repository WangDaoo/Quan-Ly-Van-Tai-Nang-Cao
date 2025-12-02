"""
Test script to verify database setup
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import EnhancedDatabaseManager, MigrationRunner, seed_database

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_database_setup():
    """Test database setup and seeding"""
    
    # Use test database
    test_db_path = "data/test_transport.db"
    
    # Remove existing test database
    test_db_file = Path(test_db_path)
    if test_db_file.exists():
        test_db_file.unlink()
        logger.info("Removed existing test database")
    
    try:
        # Initialize database manager
        logger.info("Initializing database manager...")
        db = EnhancedDatabaseManager(test_db_path)
        
        # Test connection
        logger.info("Testing database connection...")
        with db.get_connection() as conn:
            result = conn.execute("SELECT 1").fetchone()
            assert result[0] == 1
            logger.info("✓ Database connection successful")
        
        # Test table creation
        logger.info("Verifying tables...")
        with db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'business_records',
                'company_prices',
                'departments',
                'employee_workspaces',
                'employees',
                'field_configurations',
                'formulas',
                'push_conditions',
                'schema_migrations',
                'trips',
                'workflow_history'
            ]
            
            for table in expected_tables:
                if table in tables:
                    logger.info(f"✓ Table '{table}' exists")
                else:
                    logger.error(f"✗ Table '{table}' missing")
        
        # Test migration system
        logger.info("\nTesting migration system...")
        migration_runner = MigrationRunner(test_db_path)
        status = migration_runner.get_migration_status()
        logger.info(f"Current version: {status['current_version']}")
        logger.info(f"Applied migrations: {status['applied_count']}")
        
        # Test data seeding
        logger.info("\nSeeding database with sample data...")
        success = seed_database(db)
        
        if success:
            logger.info("✓ Data seeding successful")
            
            # Verify seeded data
            logger.info("\nVerifying seeded data...")
            
            departments = db.get_all_departments()
            logger.info(f"✓ Departments: {len(departments)}")
            
            trips = db.get_all_trips(limit=100)
            logger.info(f"✓ Trips: {len(trips)}")
            
            company_prices = db.get_company_prices('A')
            logger.info(f"✓ Company A prices: {len(company_prices)}")
            
            # Test trip code generation
            next_code = db.get_next_trip_code()
            logger.info(f"✓ Next trip code: {next_code}")
            
            # Test search functionality
            search_results = db.search_trips({'khach_hang': 'ABC'})
            logger.info(f"✓ Search results: {len(search_results)}")
            
        else:
            logger.error("✗ Data seeding failed")
        
        # Test CRUD operations
        logger.info("\nTesting CRUD operations...")
        
        # Insert test trip
        test_trip = {
            'ma_chuyen': 'TEST001',
            'khach_hang': 'Test Customer',
            'diem_di': 'Hà Nội',
            'diem_den': 'TP. Hồ Chí Minh',
            'gia_ca': 5000000,
            'khoan_luong': 1000000,
            'chi_phi_khac': 100000,
            'ghi_chu': 'Test trip'
        }
        
        trip_id = db.insert_trip(test_trip)
        logger.info(f"✓ Inserted trip with ID: {trip_id}")
        
        # Read trip
        retrieved_trip = db.get_trip_by_id(trip_id)
        assert retrieved_trip['ma_chuyen'] == 'TEST001'
        logger.info(f"✓ Retrieved trip: {retrieved_trip['ma_chuyen']}")
        
        # Update trip
        test_trip['gia_ca'] = 6000000
        db.update_trip(trip_id, test_trip)
        updated_trip = db.get_trip_by_id(trip_id)
        assert updated_trip['gia_ca'] == 6000000
        logger.info(f"✓ Updated trip price: {updated_trip['gia_ca']}")
        
        # Delete trip
        db.delete_trip(trip_id)
        deleted_trip = db.get_trip_by_id(trip_id)
        assert deleted_trip is None
        logger.info("✓ Deleted trip successfully")
        
        # Test transaction rollback
        logger.info("\nTesting transaction rollback...")
        try:
            with db.transaction() as conn:
                conn.execute("INSERT INTO trips (ma_chuyen, khach_hang, gia_ca) VALUES (?, ?, ?)",
                           ('ROLLBACK001', 'Test', 1000000))
                # Force an error
                conn.execute("INSERT INTO trips (ma_chuyen, khach_hang, gia_ca) VALUES (?, ?, ?)",
                           ('ROLLBACK001', 'Test', 1000000))  # Duplicate key
        except Exception:
            pass
        
        # Verify rollback
        rollback_trip = db.execute_query("SELECT * FROM trips WHERE ma_chuyen = ?", ('ROLLBACK001',))
        assert len(rollback_trip) == 0
        logger.info("✓ Transaction rollback successful")
        
        logger.info("\n" + "="*50)
        logger.info("All tests passed! ✓")
        logger.info("="*50)
        
        # Cleanup
        db.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_database_setup()
    sys.exit(0 if success else 1)
