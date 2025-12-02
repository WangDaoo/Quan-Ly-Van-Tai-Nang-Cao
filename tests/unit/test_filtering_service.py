"""
Unit tests for FilteringService
Tests real-time filtering, debouncing, multi-field filtering, and fuzzy search
"""
import pytest
import time
from typing import List
from unittest.mock import Mock

from src.services.filtering_service import FilteringService
from src.models.trip import Trip


@pytest.fixture
def filtering_service():
    """Create a FilteringService instance for testing"""
    return FilteringService(debounce_ms=100, fuzzy_threshold=0.6)


@pytest.fixture
def sample_trips():
    """Create sample trips for testing"""
    return [
        Trip(
            id=1,
            ma_chuyen="C001",
            khach_hang="ABC Company",
            diem_di="Hanoi",
            diem_den="Ho Chi Minh",
            gia_ca=1000000,
            khoan_luong=500000,
            chi_phi_khac=100000
        ),
        Trip(
            id=2,
            ma_chuyen="C002",
            khach_hang="XYZ Corporation",
            diem_di="Da Nang",
            diem_den="Hanoi",
            gia_ca=800000,
            khoan_luong=400000,
            chi_phi_khac=50000
        ),
        Trip(
            id=3,
            ma_chuyen="C003",
            khach_hang="ABC Trading",
            diem_di="Hanoi",
            diem_den="Hai Phong",
            gia_ca=500000,
            khoan_luong=250000,
            chi_phi_khac=30000
        ),
        Trip(
            id=4,
            ma_chuyen="C004",
            khach_hang="Global Logistics",
            diem_di="Ho Chi Minh",
            diem_den="Can Tho",
            gia_ca=600000,
            khoan_luong=300000,
            chi_phi_khac=40000
        ),
    ]


class TestFilteringServiceBasic:
    """Test basic filtering functionality"""
    
    def test_initialization(self):
        """Test FilteringService initialization"""
        service = FilteringService(debounce_ms=300, fuzzy_threshold=0.7)
        assert service.debounce_ms == 300
        assert service.fuzzy_threshold == 0.7
    
    def test_filter_trips_no_filters(self, filtering_service, sample_trips):
        """Test filtering with no filters returns all trips"""
        result = filtering_service.filter_trips(sample_trips, {})
        assert len(result) == len(sample_trips)
        assert result == sample_trips
    
    def test_filter_trips_empty_filter_value(self, filtering_service, sample_trips):
        """Test filtering with empty filter value returns all trips"""
        result = filtering_service.filter_trips(sample_trips, {'khach_hang': ''})
        assert len(result) == len(sample_trips)
    
    def test_filter_trips_none_filter_value(self, filtering_service, sample_trips):
        """Test filtering with None filter value returns all trips"""
        result = filtering_service.filter_trips(sample_trips, {'khach_hang': None})
        assert len(result) == len(sample_trips)


class TestSingleFieldFiltering:
    """Test filtering by single field"""
    
    def test_filter_by_customer_exact_match(self, filtering_service, sample_trips):
        """Test filtering by customer name with exact substring match"""
        result = filtering_service.filter_trips(sample_trips, {'khach_hang': 'ABC'})
        assert len(result) == 2
        assert all('ABC' in trip.khach_hang for trip in result)
    
    def test_filter_by_customer_case_insensitive(self, filtering_service, sample_trips):
        """Test filtering is case-insensitive"""
        result = filtering_service.filter_trips(sample_trips, {'khach_hang': 'abc'})
        assert len(result) == 2
        assert all('ABC' in trip.khach_hang for trip in result)
    
    def test_filter_by_departure_location(self, filtering_service, sample_trips):
        """Test filtering by departure location"""
        result = filtering_service.filter_trips(sample_trips, {'diem_di': 'Hanoi'})
        assert len(result) == 2
        assert all(trip.diem_di == 'Hanoi' for trip in result)
    
    def test_filter_by_destination_location(self, filtering_service, sample_trips):
        """Test filtering by destination location"""
        result = filtering_service.filter_trips(sample_trips, {'diem_den': 'Hanoi'})
        assert len(result) == 1
        assert result[0].diem_den == 'Hanoi'
    
    def test_filter_by_trip_code(self, filtering_service, sample_trips):
        """Test filtering by trip code with substring match"""
        # "C001" will match C001, C002, C003, C004 as substring
        result = filtering_service.filter_trips(sample_trips, {'ma_chuyen': 'C00'})
        assert len(result) == 4  # All trip codes contain "C00"
        
        # Exact match for specific trip
        result = filtering_service.filter_trips(sample_trips, {'ma_chuyen': 'C001'}, use_fuzzy=False)
        assert len(result) == 1
        assert result[0].ma_chuyen == 'C001'
    
    def test_filter_no_matches(self, filtering_service, sample_trips):
        """Test filtering with no matches returns empty list"""
        result = filtering_service.filter_trips(sample_trips, {'khach_hang': 'NonExistent'})
        assert len(result) == 0


class TestMultiFieldFiltering:
    """Test filtering by multiple fields"""
    
    def test_filter_by_customer_and_departure(self, filtering_service, sample_trips):
        """Test filtering by customer and departure location"""
        filters = {
            'khach_hang': 'ABC',
            'diem_di': 'Hanoi'
        }
        result = filtering_service.filter_trips(sample_trips, filters)
        assert len(result) == 2
        assert all('ABC' in trip.khach_hang and trip.diem_di == 'Hanoi' for trip in result)
    
    def test_filter_by_three_fields(self, filtering_service, sample_trips):
        """Test filtering by three fields"""
        filters = {
            'khach_hang': 'ABC',
            'diem_di': 'Hanoi',
            'diem_den': 'Hai Phong'
        }
        result = filtering_service.filter_trips(sample_trips, filters)
        assert len(result) == 1
        assert result[0].ma_chuyen == 'C003'
    
    def test_filter_multiple_fields_no_match(self, filtering_service, sample_trips):
        """Test filtering with multiple fields that don't match any trip"""
        filters = {
            'khach_hang': 'ABC',
            'diem_di': 'Da Nang'  # ABC trips don't depart from Da Nang
        }
        result = filtering_service.filter_trips(sample_trips, filters)
        assert len(result) == 0


class TestFuzzySearch:
    """Test fuzzy search functionality"""
    
    def test_fuzzy_search_exact_match(self, filtering_service):
        """Test fuzzy search with exact match"""
        items = ['Hanoi', 'Ho Chi Minh', 'Da Nang', 'Hai Phong']
        result = filtering_service.fuzzy_search(items, 'Hanoi')
        assert len(result) > 0
        assert result[0][0] == 'Hanoi'
        assert result[0][1] == 1.0
    
    def test_fuzzy_search_partial_match(self, filtering_service):
        """Test fuzzy search with partial match"""
        items = ['ABC Company', 'XYZ Corporation', 'ABC Trading']
        result = filtering_service.fuzzy_search(items, 'ABC')
        assert len(result) == 2
        assert all('ABC' in item for item, _ in result)
    
    def test_fuzzy_search_typo(self, filtering_service):
        """Test fuzzy search handles typos"""
        items = ['Hanoi', 'Ho Chi Minh', 'Da Nang']
        result = filtering_service.fuzzy_search(items, 'Hano')  # Missing 'i'
        assert len(result) > 0
        # Should find Hanoi with high similarity
        assert any('Hanoi' in item for item, _ in result)
    
    def test_fuzzy_search_empty_query(self, filtering_service):
        """Test fuzzy search with empty query returns all items"""
        items = ['Hanoi', 'Ho Chi Minh', 'Da Nang']
        result = filtering_service.fuzzy_search(items, '')
        assert len(result) == len(items)
        assert all(score == 1.0 for _, score in result)
    
    def test_fuzzy_search_sorted_by_similarity(self, filtering_service):
        """Test fuzzy search results are sorted by similarity"""
        items = ['ABC Company', 'ABC Trading', 'XYZ Corporation']
        result = filtering_service.fuzzy_search(items, 'ABC')
        # Results should be sorted by similarity (highest first)
        scores = [score for _, score in result]
        assert scores == sorted(scores, reverse=True)
    
    def test_fuzzy_search_custom_threshold(self, filtering_service):
        """Test fuzzy search with custom threshold"""
        items = ['Hanoi', 'Ho Chi Minh', 'Da Nang']
        # High threshold should return fewer results
        result = filtering_service.fuzzy_search(items, 'Han', threshold=0.9)
        assert len(result) <= 1


class TestFuzzyFiltering:
    """Test filtering with fuzzy matching"""
    
    def test_filter_with_fuzzy_enabled(self, filtering_service, sample_trips):
        """Test filtering with fuzzy matching enabled"""
        # "Compan" should match "Company" with fuzzy search
        result = filtering_service.filter_trips(
            sample_trips,
            {'khach_hang': 'Compan'},
            use_fuzzy=True
        )
        assert len(result) >= 1
    
    def test_filter_with_fuzzy_disabled(self, filtering_service, sample_trips):
        """Test filtering with fuzzy matching disabled still does substring matching"""
        # "Compan" is a substring of "Company" so it will match even without fuzzy
        result = filtering_service.filter_trips(
            sample_trips,
            {'khach_hang': 'Compan'},
            use_fuzzy=False
        )
        assert len(result) == 1  # Matches "ABC Company"
        
        # But a typo won't match without fuzzy
        result = filtering_service.filter_trips(
            sample_trips,
            {'khach_hang': 'Compny'},  # Typo: missing 'a'
            use_fuzzy=False
        )
        assert len(result) == 0
    
    def test_filter_fuzzy_threshold(self):
        """Test filtering respects fuzzy threshold"""
        # Create service with high threshold
        service = FilteringService(fuzzy_threshold=0.9)
        trips = [
            Trip(
                ma_chuyen="C001",
                khach_hang="ABC Company",
                diem_di="Hanoi",
                diem_den="Ho Chi Minh",
                gia_ca=1000000
            )
        ]
        
        # Very different string should not match with high threshold
        result = service.filter_trips(trips, {'khach_hang': 'XYZ'}, use_fuzzy=True)
        assert len(result) == 0


class TestDebouncing:
    """Test debounced filtering"""
    
    def test_debounced_filter_executes_after_delay(self, filtering_service):
        """Test debounced filter executes after delay"""
        callback = Mock()
        filtering_service.debounced_filter(callback, 'test_filter', arg1='value1')
        
        # Should not execute immediately
        assert not callback.called
        
        # Wait for debounce delay
        time.sleep(0.15)  # 150ms > 100ms debounce
        
        # Should have executed
        assert callback.called
        callback.assert_called_once_with(arg1='value1')
    
    def test_debounced_filter_cancels_previous(self, filtering_service):
        """Test debounced filter cancels previous timer"""
        callback = Mock()
        
        # First call
        filtering_service.debounced_filter(callback, 'test_filter', call=1)
        time.sleep(0.05)  # 50ms < 100ms debounce
        
        # Second call should cancel first
        filtering_service.debounced_filter(callback, 'test_filter', call=2)
        time.sleep(0.15)  # Wait for second to execute
        
        # Should only be called once (second call)
        assert callback.call_count == 1
        callback.assert_called_with(call=2)
    
    def test_cancel_debounce(self, filtering_service):
        """Test canceling a debounced filter"""
        callback = Mock()
        filtering_service.debounced_filter(callback, 'test_filter')
        
        # Cancel before execution
        filtering_service.cancel_debounce('test_filter')
        time.sleep(0.15)
        
        # Should not have executed
        assert not callback.called
    
    def test_cancel_all_debounces(self, filtering_service):
        """Test canceling all debounced filters"""
        callback1 = Mock()
        callback2 = Mock()
        
        filtering_service.debounced_filter(callback1, 'filter1')
        filtering_service.debounced_filter(callback2, 'filter2')
        
        # Cancel all
        filtering_service.cancel_all_debounces()
        time.sleep(0.15)
        
        # Neither should have executed
        assert not callback1.called
        assert not callback2.called


class TestGenericDictionaryFiltering:
    """Test filtering generic dictionary data"""
    
    def test_filter_dictionary_data(self, filtering_service):
        """Test filtering generic dictionary data"""
        data = [
            {'name': 'John', 'age': 30, 'city': 'Hanoi'},
            {'name': 'Jane', 'age': 25, 'city': 'Ho Chi Minh'},
            {'name': 'Bob', 'age': 35, 'city': 'Hanoi'},
        ]
        
        result = filtering_service.filter_by_multiple_fields(data, {'city': 'Hanoi'})
        assert len(result) == 2
        assert all(item['city'] == 'Hanoi' for item in result)
    
    def test_filter_dictionary_multiple_fields(self, filtering_service):
        """Test filtering dictionary data by multiple fields"""
        data = [
            {'name': 'John', 'age': 30, 'city': 'Hanoi'},
            {'name': 'Jane', 'age': 25, 'city': 'Ho Chi Minh'},
            {'name': 'Bob', 'age': 30, 'city': 'Hanoi'},
        ]
        
        filters = {'age': 30, 'city': 'Hanoi'}
        result = filtering_service.filter_by_multiple_fields(data, filters)
        assert len(result) == 2
        assert all(item['age'] == 30 and item['city'] == 'Hanoi' for item in result)


class TestUtilityMethods:
    """Test utility methods"""
    
    def test_get_unique_values(self, filtering_service, sample_trips):
        """Test getting unique values from trips"""
        unique_customers = filtering_service.get_unique_values(sample_trips, 'khach_hang')
        assert len(unique_customers) == 4
        assert 'ABC Company' in unique_customers
        assert 'XYZ Corporation' in unique_customers
    
    def test_get_unique_values_sorted(self, filtering_service, sample_trips):
        """Test unique values are sorted"""
        unique_locations = filtering_service.get_unique_values(sample_trips, 'diem_di')
        assert unique_locations == sorted(unique_locations)
    
    def test_create_filter_suggestions_no_query(self, filtering_service, sample_trips):
        """Test creating filter suggestions without query"""
        suggestions = filtering_service.create_filter_suggestions(sample_trips, 'diem_di')
        assert len(suggestions) == 3  # Da Nang, Hanoi, Ho Chi Minh
        assert 'Hanoi' in suggestions
    
    def test_create_filter_suggestions_with_query(self, filtering_service, sample_trips):
        """Test creating filter suggestions with query"""
        suggestions = filtering_service.create_filter_suggestions(
            sample_trips,
            'khach_hang',
            'ABC'
        )
        assert len(suggestions) >= 2
        assert all('ABC' in s for s in suggestions)
    
    def test_calculate_similarity(self, filtering_service):
        """Test similarity calculation"""
        # Exact match
        assert filtering_service._calculate_similarity('test', 'test') == 1.0
        
        # Partial match
        similarity = filtering_service._calculate_similarity('testing', 'test')
        assert 0.5 < similarity < 1.0
        
        # No match
        similarity = filtering_service._calculate_similarity('abc', 'xyz')
        assert similarity < 0.5


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_filter_empty_trip_list(self, filtering_service):
        """Test filtering empty trip list"""
        result = filtering_service.filter_trips([], {'khach_hang': 'ABC'})
        assert result == []
    
    def test_filter_invalid_field_name(self, filtering_service, sample_trips):
        """Test filtering with invalid field name"""
        result = filtering_service.filter_trips(
            sample_trips,
            {'invalid_field': 'value'}
        )
        # Should return empty list since no trips have this field
        assert len(result) == 0
    
    def test_filter_with_none_values_in_trips(self, filtering_service):
        """Test filtering trips with None values"""
        trips = [
            Trip(
                ma_chuyen="C001",
                khach_hang="ABC",
                diem_di=None,  # None value
                diem_den="Hanoi",
                gia_ca=1000000
            )
        ]
        
        result = filtering_service.filter_trips(trips, {'diem_di': 'Hanoi'})
        assert len(result) == 0  # Should not match None
    
    def test_fuzzy_search_empty_items(self, filtering_service):
        """Test fuzzy search with empty items list"""
        result = filtering_service.fuzzy_search([], 'query')
        assert result == []
    
    def test_filter_whitespace_handling(self, filtering_service, sample_trips):
        """Test filtering handles whitespace correctly"""
        result = filtering_service.filter_trips(
            sample_trips,
            {'khach_hang': '  ABC  '}  # Extra whitespace
        )
        assert len(result) == 2  # Should still match


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
