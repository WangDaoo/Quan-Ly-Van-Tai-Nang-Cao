"""
Excel Service Demo
Demonstrates how to use the Excel Service for import/export operations
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services.excel_service import ExcelService, DuplicateHandling
from src.services.trip_service import TripService


def progress_callback(current, total, message):
    """Progress callback for import/export operations"""
    percentage = (current / total) * 100 if total > 0 else 0
    print(f"Progress: {percentage:.1f}% - {message}")


def demo_export():
    """Demonstrate export functionality"""
    print("\n=== Excel Export Demo ===\n")
    
    # Initialize services
    db = EnhancedDatabaseManager("data/transport.db")
    excel_service = ExcelService(db)
    trip_service = TripService(db)
    
    # Get all trips
    result = trip_service.get_all_trips(page=1, page_size=100)
    trips = result['trips']
    
    print(f"Found {len(trips)} trips to export")
    
    # Export to Excel with formatting
    export_path = "exports/trips_export.xlsx"
    Path("exports").mkdir(exist_ok=True)
    
    success = excel_service.export_to_excel(
        export_path,
        trips,
        include_formatting=True,
        progress_callback=progress_callback
    )
    
    if success:
        print(f"\n✓ Successfully exported to {export_path}")
    else:
        print("\n✗ Export failed")
    
    db.close()


def demo_import():
    """Demonstrate import functionality"""
    print("\n=== Excel Import Demo ===\n")
    
    # Initialize services
    db = EnhancedDatabaseManager("data/transport.db")
    excel_service = ExcelService(db)
    
    # Preview file first
    import_path = "imports/sample_trips.xlsx"
    
    if not Path(import_path).exists():
        print(f"Import file not found: {import_path}")
        print("Please create a sample Excel file with trip data")
        db.close()
        return
    
    print("Previewing Excel file...")
    preview = excel_service.preview_excel_file(import_path, max_rows=5)
    
    print(f"Columns: {preview['columns']}")
    print(f"Total rows: {preview['total_rows']}")
    print(f"Validation errors: {len(preview['validation_errors'])}")
    
    if preview['validation_errors']:
        print("\nValidation errors found:")
        for error in preview['validation_errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    # Import with skip duplicates
    print("\nImporting data...")
    result = excel_service.import_excel_file(
        import_path,
        duplicate_handling=DuplicateHandling.SKIP,
        progress_callback=progress_callback
    )
    
    print(f"\n=== Import Results ===")
    print(f"✓ Success: {result['success_count']}")
    print(f"⊘ Skipped: {result['skipped_count']}")
    print(f"✗ Errors: {result['error_count']}")
    
    if result['errors']:
        print("\nErrors:")
        for error in result['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    db.close()


def demo_filtered_export():
    """Demonstrate filtered export"""
    print("\n=== Filtered Export Demo ===\n")
    
    # Initialize services
    db = EnhancedDatabaseManager("data/transport.db")
    excel_service = ExcelService(db)
    
    # Export filtered trips
    filters = {'khach_hang': 'Công ty'}  # Filter by customer name containing "Công ty"
    export_path = "exports/filtered_trips.xlsx"
    Path("exports").mkdir(exist_ok=True)
    
    print(f"Exporting trips with filter: {filters}")
    
    success = excel_service.export_filtered_trips(
        export_path,
        filters,
        include_formatting=True,
        progress_callback=progress_callback
    )
    
    if success:
        print(f"\n✓ Successfully exported filtered trips to {export_path}")
    else:
        print("\n✗ Export failed")
    
    db.close()


def main():
    """Main demo function"""
    print("=" * 60)
    print("Excel Service Demo")
    print("=" * 60)
    
    # Run demos
    demo_export()
    demo_filtered_export()
    # demo_import()  # Uncomment if you have a sample import file
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
