"""
Filtering Service - Real-time filtering with debouncing and fuzzy search
Provides multi-field filtering support for trips and other data
"""
import logging
import time
from typing import List, Dict, Any, Optional, Callable
from difflib import SequenceMatcher
from threading import Timer

from src.models.trip import Trip


logger = logging.getLogger(__name__)


class FilteringService:
    """
    Service for real-time filtering with debouncing and fuzzy search.
    
    Features:
    - Real-time filtering with debounce (300ms default)
    - Multi-field filtering support
    - Fuzzy search with configurable threshold
    - Case-insensitive matching
    - Partial string matching
    """
    
    def __init__(self, debounce_ms: int = 300, fuzzy_threshold: float = 0.6):
        """
        Initialize Filtering Service
        
        Args:
            debounce_ms: Debounce delay in milliseconds (default: 300ms)
            fuzzy_threshold: Minimum similarity ratio for fuzzy matching (0.0-1.0, default: 0.6)
        """
        self.debounce_ms = debounce_ms
        self.fuzzy_threshold = fuzzy_threshold
        self._debounce_timers: Dict[str, Timer] = {}
        logger.info(f"FilteringService initialized with debounce={debounce_ms}ms, fuzzy_threshold={fuzzy_threshold}")
    
    def filter_trips(
        self,
        trips: List[Trip],
        filters: Dict[str, Any],
        use_fuzzy: bool = True
    ) -> List[Trip]:
        """
        Filter trips based on multiple field criteria
        
        Args:
            trips: List of Trip objects to filter
            filters: Dictionary of field names and filter values
                    Example: {'khach_hang': 'ABC', 'diem_di': 'Hanoi'}
            use_fuzzy: Whether to use fuzzy matching (default: True)
        
        Returns:
            List of Trip objects matching all filter criteria
        """
        if not filters:
            return trips
        
        filtered_trips = trips
        
        for field_name, filter_value in filters.items():
            if filter_value is None or filter_value == "":
                continue
            
            filtered_trips = self._filter_by_field(
                filtered_trips,
                field_name,
                filter_value,
                use_fuzzy
            )
        
        logger.debug(f"Filtered {len(trips)} trips to {len(filtered_trips)} using filters: {filters}")
        
        return filtered_trips
    
    def _filter_by_field(
        self,
        trips: List[Trip],
        field_name: str,
        filter_value: Any,
        use_fuzzy: bool
    ) -> List[Trip]:
        """
        Filter trips by a single field
        
        Args:
            trips: List of Trip objects to filter
            field_name: Name of the field to filter on
            filter_value: Value to filter by
            use_fuzzy: Whether to use fuzzy matching
        
        Returns:
            List of Trip objects matching the field criteria
        """
        filtered = []
        
        for trip in trips:
            # Get field value from trip
            if not hasattr(trip, field_name):
                continue
            
            trip_value = getattr(trip, field_name)
            
            # Handle None values
            if trip_value is None:
                continue
            
            # Match based on field type
            if self._matches(trip_value, filter_value, use_fuzzy):
                filtered.append(trip)
        
        return filtered
    
    def _matches(self, trip_value: Any, filter_value: Any, use_fuzzy: bool) -> bool:
        """
        Check if a trip value matches a filter value
        
        Args:
            trip_value: Value from the trip object
            filter_value: Value to match against
            use_fuzzy: Whether to use fuzzy matching
        
        Returns:
            True if values match, False otherwise
        """
        # Convert to strings for comparison
        trip_str = str(trip_value).lower().strip()
        filter_str = str(filter_value).lower().strip()
        
        # Empty filter matches everything
        if not filter_str:
            return True
        
        # Exact match (case-insensitive)
        if trip_str == filter_str:
            return True
        
        # Substring match (case-insensitive)
        if filter_str in trip_str:
            return True
        
        # Fuzzy match if enabled
        if use_fuzzy:
            similarity = self._calculate_similarity(trip_str, filter_str)
            if similarity >= self.fuzzy_threshold:
                return True
        
        return False
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity ratio between two strings using SequenceMatcher
        
        Args:
            str1: First string
            str2: Second string
        
        Returns:
            Similarity ratio between 0.0 and 1.0
        """
        return SequenceMatcher(None, str1, str2).ratio()
    
    def fuzzy_search(
        self,
        items: List[str],
        query: str,
        threshold: Optional[float] = None
    ) -> List[tuple[str, float]]:
        """
        Perform fuzzy search on a list of strings
        
        Args:
            items: List of strings to search
            query: Search query string
            threshold: Minimum similarity threshold (uses instance default if None)
        
        Returns:
            List of tuples (item, similarity_score) sorted by similarity (highest first)
        """
        if not query:
            return [(item, 1.0) for item in items]
        
        threshold = threshold if threshold is not None else self.fuzzy_threshold
        query_lower = query.lower().strip()
        
        results = []
        
        for item in items:
            item_lower = item.lower().strip()
            
            # Check for exact substring match first
            if query_lower in item_lower:
                results.append((item, 1.0))
            else:
                # Calculate fuzzy similarity
                similarity = self._calculate_similarity(item_lower, query_lower)
                if similarity >= threshold:
                    results.append((item, similarity))
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        
        logger.debug(f"Fuzzy search for '{query}' found {len(results)} matches")
        
        return results
    
    def debounced_filter(
        self,
        callback: Callable,
        filter_id: str,
        *args,
        **kwargs
    ) -> None:
        """
        Execute a filter callback with debouncing
        
        Args:
            callback: Function to call after debounce delay
            filter_id: Unique identifier for this filter operation
            *args: Positional arguments to pass to callback
            **kwargs: Keyword arguments to pass to callback
        """
        # Cancel existing timer for this filter_id
        if filter_id in self._debounce_timers:
            self._debounce_timers[filter_id].cancel()
        
        # Create new timer
        delay_seconds = self.debounce_ms / 1000.0
        timer = Timer(delay_seconds, callback, args=args, kwargs=kwargs)
        self._debounce_timers[filter_id] = timer
        timer.start()
        
        logger.debug(f"Debounced filter '{filter_id}' scheduled for {self.debounce_ms}ms")
    
    def cancel_debounce(self, filter_id: str) -> None:
        """
        Cancel a pending debounced filter operation
        
        Args:
            filter_id: Unique identifier of the filter operation to cancel
        """
        if filter_id in self._debounce_timers:
            self._debounce_timers[filter_id].cancel()
            del self._debounce_timers[filter_id]
            logger.debug(f"Cancelled debounced filter '{filter_id}'")
    
    def cancel_all_debounces(self) -> None:
        """
        Cancel all pending debounced filter operations
        """
        for filter_id in list(self._debounce_timers.keys()):
            self.cancel_debounce(filter_id)
        
        logger.debug("Cancelled all debounced filters")
    
    def filter_by_multiple_fields(
        self,
        data: List[Dict[str, Any]],
        filters: Dict[str, Any],
        use_fuzzy: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Filter generic dictionary data by multiple fields
        
        Args:
            data: List of dictionaries to filter
            filters: Dictionary of field names and filter values
            use_fuzzy: Whether to use fuzzy matching (default: True)
        
        Returns:
            List of dictionaries matching all filter criteria
        """
        if not filters:
            return data
        
        filtered_data = data
        
        for field_name, filter_value in filters.items():
            if filter_value is None or filter_value == "":
                continue
            
            filtered_data = [
                item for item in filtered_data
                if field_name in item and self._matches(item[field_name], filter_value, use_fuzzy)
            ]
        
        logger.debug(f"Filtered {len(data)} items to {len(filtered_data)} using filters: {filters}")
        
        return filtered_data
    
    def get_unique_values(
        self,
        trips: List[Trip],
        field_name: str
    ) -> List[str]:
        """
        Get unique values for a specific field from a list of trips
        
        Args:
            trips: List of Trip objects
            field_name: Name of the field to extract unique values from
        
        Returns:
            Sorted list of unique non-empty values
        """
        unique_values = set()
        
        for trip in trips:
            if hasattr(trip, field_name):
                value = getattr(trip, field_name)
                if value is not None and str(value).strip():
                    unique_values.add(str(value).strip())
        
        return sorted(list(unique_values))
    
    def create_filter_suggestions(
        self,
        trips: List[Trip],
        field_name: str,
        query: str = ""
    ) -> List[str]:
        """
        Create filter suggestions for a field based on existing data
        
        Args:
            trips: List of Trip objects
            field_name: Name of the field to get suggestions for
            query: Optional query string for fuzzy matching
        
        Returns:
            List of suggested values sorted by relevance
        """
        unique_values = self.get_unique_values(trips, field_name)
        
        if not query:
            return unique_values
        
        # Use fuzzy search to find matching suggestions
        fuzzy_results = self.fuzzy_search(unique_values, query)
        
        # Return only the values (not the similarity scores)
        return [value for value, _ in fuzzy_results]
