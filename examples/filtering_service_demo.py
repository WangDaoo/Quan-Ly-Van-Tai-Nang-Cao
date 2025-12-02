"""
Demo script for FilteringService
Demonstrates real-time filtering, debouncing, multi-field filtering, and fuzzy search
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.filtering_service import FilteringService
from src.models.trip import Trip


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_basic_filtering():
    """Demonstrate basic filtering functionality"""
    print_section("1. Basic Filtering")
    
    # Create sample trips
    trips = [
        Trip(ma_chuyen="C001", khach_hang="ABC Company", diem_di="Hanoi", diem_den="Ho Chi Minh", gia_ca=1000000),
        Trip(ma_chuyen="C002", khach_hang="XYZ Corporation", diem_di="Da Nang", diem_den="Hanoi", gia_ca=800000),
        Trip(ma_chuyen="C003", khach_hang="ABC Trading", diem_di="Hanoi", diem_den="Hai Phong", gia_ca=500000),
        Trip(ma_chuyen="C004", khach_hang="Global Logistics", diem_di="Ho Chi Minh", diem_den="Can Tho", gia_ca=600000),
    ]
    
    # Create filtering service
    service = FilteringService()
    
    # Filter by customer
    print("Filter by customer 'ABC':")
    filtered = service.filter_trips(trips, {'khach_hang': 'ABC'})
    for trip in filtered:
        print(f"  - {trip.ma_chuyen}: {trip.khach_hang}")
    
    # Filter by departure location
    print("\nFilter by departure 'Hanoi':")
    filtered = service.filter_trips(trips, {'diem_di': 'Hanoi'})
    for trip in filtered:
        print(f"  - {trip.ma_chuyen}: {trip.diem_di} -> {trip.diem_den}")


def demo_multi_field_filtering():
    """Demonstrate multi-field filtering"""
    print_section("2. Multi-Field Filtering")
    
    trips = [
        Trip(ma_chuyen="C001", khach_hang="ABC Company", diem_di="Hanoi", diem_den="Ho Chi Minh", gia_ca=1000000),
        Trip(ma_chuyen="C002", khach_hang="XYZ Corporation", diem_di="Da Nang", diem_den="Hanoi", gia_ca=800000),
        Trip(ma_chuyen="C003", khach_hang="ABC Trading", diem_di="Hanoi", diem_den="Hai Phong", gia_ca=500000),
        Trip(ma_chuyen="C004", khach_hang="Global Logistics", diem_di="Ho Chi Minh", diem_den="Can Tho", gia_ca=600000),
    ]
    
    service = FilteringService()
    
    # Filter by multiple fields
    filters = {
        'khach_hang': 'ABC',
        'diem_di': 'Hanoi'
    }
    
    print(f"Filter by: {filters}")
    filtered = service.filter_trips(trips, filters)
    for trip in filtered:
        print(f"  - {trip.ma_chuyen}: {trip.khach_hang} | {trip.diem_di} -> {trip.diem_den}")


def demo_fuzzy_search():
    """Demonstrate fuzzy search functionality"""
    print_section("3. Fuzzy Search")
    
    service = FilteringService(fuzzy_threshold=0.6)
    
    # Sample customer names
    customers = ['ABC Company', 'XYZ Corporation', 'ABC Trading', 'Global Logistics', 'Vietnam Express']
    
    # Exact match
    print("Search for 'ABC':")
    results = service.fuzzy_search(customers, 'ABC')
    for item, score in results[:3]:
        print(f"  - {item} (similarity: {score:.2f})")
    
    # Fuzzy match with typo
    print("\nSearch for 'Compny' (typo):")
    results = service.fuzzy_search(customers, 'Compny')
    for item, score in results[:3]:
        print(f"  - {item} (similarity: {score:.2f})")
    
    # Partial match
    print("\nSearch for 'Viet':")
    results = service.fuzzy_search(customers, 'Viet')
    for item, score in results[:3]:
        print(f"  - {item} (similarity: {score:.2f})")


def demo_debouncing():
    """Demonstrate debounced filtering"""
    print_section("4. Debounced Filtering")
    
    service = FilteringService(debounce_ms=300)
    
    call_count = [0]  # Use list to allow modification in nested function
    
    def filter_callback(query: str):
        call_count[0] += 1
        print(f"  Filter executed for query: '{query}' (call #{call_count[0]})")
    
    print("Simulating rapid user input (debouncing prevents excessive calls):")
    print("  User types: 'A' -> 'AB' -> 'ABC'")
    
    # Simulate rapid typing
    service.debounced_filter(filter_callback, 'search', query='A')
    time.sleep(0.1)  # 100ms
    
    service.debounced_filter(filter_callback, 'search', query='AB')
    time.sleep(0.1)  # 100ms
    
    service.debounced_filter(filter_callback, 'search', query='ABC')
    
    # Wait for debounce to complete
    time.sleep(0.4)  # 400ms
    
    print(f"\nTotal filter executions: {call_count[0]} (only the last one)")


def demo_filter_suggestions():
    """Demonstrate filter suggestions"""
    print_section("5. Filter Suggestions")
    
    trips = [
        Trip(ma_chuyen="C001", khach_hang="ABC Company", diem_di="Hanoi", diem_den="Ho Chi Minh", gia_ca=1000000),
        Trip(ma_chuyen="C002", khach_hang="XYZ Corporation", diem_di="Da Nang", diem_den="Hanoi", gia_ca=800000),
        Trip(ma_chuyen="C003", khach_hang="ABC Trading", diem_di="Hanoi", diem_den="Hai Phong", gia_ca=500000),
        Trip(ma_chuyen="C004", khach_hang="Global Logistics", diem_di="Ho Chi Minh", diem_den="Can Tho", gia_ca=600000),
    ]
    
    service = FilteringService()
    
    # Get unique values
    print("Unique departure locations:")
    locations = service.get_unique_values(trips, 'diem_di')
    for loc in locations:
        print(f"  - {loc}")
    
    # Get suggestions with query
    print("\nSuggestions for customer starting with 'ABC':")
    suggestions = service.create_filter_suggestions(trips, 'khach_hang', 'ABC')
    for suggestion in suggestions:
        print(f"  - {suggestion}")


def demo_case_insensitive():
    """Demonstrate case-insensitive filtering"""
    print_section("6. Case-Insensitive Filtering")
    
    trips = [
        Trip(ma_chuyen="C001", khach_hang="ABC Company", diem_di="Hanoi", diem_den="Ho Chi Minh", gia_ca=1000000),
        Trip(ma_chuyen="C002", khach_hang="xyz corporation", diem_di="Da Nang", diem_den="Hanoi", gia_ca=800000),
    ]
    
    service = FilteringService()
    
    # Test case insensitivity
    print("Filter by 'abc' (lowercase):")
    filtered = service.filter_trips(trips, {'khach_hang': 'abc'})
    for trip in filtered:
        print(f"  - {trip.ma_chuyen}: {trip.khach_hang}")
    
    print("\nFilter by 'XYZ' (uppercase):")
    filtered = service.filter_trips(trips, {'khach_hang': 'XYZ'})
    for trip in filtered:
        print(f"  - {trip.ma_chuyen}: {trip.khach_hang}")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("  FilteringService Demo")
    print("  Real-time filtering with debouncing and fuzzy search")
    print("="*60)
    
    try:
        demo_basic_filtering()
        demo_multi_field_filtering()
        demo_fuzzy_search()
        demo_debouncing()
        demo_filter_suggestions()
        demo_case_insensitive()
        
        print("\n" + "="*60)
        print("  Demo completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
