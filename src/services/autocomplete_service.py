"""
Autocomplete Service
Provides data loading for autocomplete widgets with caching and database integration
"""

import logging
from typing import List, Dict, Optional, Callable
from src.database.enhanced_db_manager import EnhancedDatabaseManager


logger = logging.getLogger(__name__)


class AutocompleteService:
    """
    Service for managing autocomplete data
    Provides data loaders for different field types with caching
    """
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        """
        Initialize Autocomplete Service
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self._cache: Dict[str, List[str]] = {}
    
    def get_customers(self, use_cache: bool = True) -> List[str]:
        """
        Get list of unique customer names for autocomplete
        
        Args:
            use_cache: Whether to use cached data
        
        Returns:
            List of unique customer names
        """
        cache_key = 'customers'
        
        # Check cache
        if use_cache and cache_key in self._cache:
            logger.debug(f"Using cached data for {cache_key}")
            return self._cache[cache_key]
        
        try:
            # Query database
            query = """
                SELECT DISTINCT khach_hang 
                FROM trips 
                WHERE khach_hang IS NOT NULL AND khach_hang != '' 
                ORDER BY khach_hang
            """
            results = self.db.execute_query(query)
            customers = [row['khach_hang'] for row in results]
            
            # Update cache
            self._cache[cache_key] = customers
            
            logger.info(f"Loaded {len(customers)} unique customers")
            return customers
            
        except Exception as e:
            logger.error(f"Error loading customers: {e}")
            return []
    
    def get_departure_locations(self, use_cache: bool = True) -> List[str]:
        """
        Get list of unique departure locations for autocomplete
        
        Args:
            use_cache: Whether to use cached data
        
        Returns:
            List of unique departure locations
        """
        cache_key = 'diem_di'
        
        # Check cache
        if use_cache and cache_key in self._cache:
            logger.debug(f"Using cached data for {cache_key}")
            return self._cache[cache_key]
        
        try:
            # Query database - combine from trips and company_prices
            query = """
                SELECT DISTINCT diem_di 
                FROM (
                    SELECT diem_di FROM trips WHERE diem_di IS NOT NULL AND diem_di != ''
                    UNION
                    SELECT diem_di FROM company_prices WHERE diem_di IS NOT NULL AND diem_di != ''
                )
                ORDER BY diem_di
            """
            results = self.db.execute_query(query)
            locations = [row['diem_di'] for row in results]
            
            # Update cache
            self._cache[cache_key] = locations
            
            logger.info(f"Loaded {len(locations)} unique departure locations")
            return locations
            
        except Exception as e:
            logger.error(f"Error loading departure locations: {e}")
            return []
    
    def get_destination_locations(self, use_cache: bool = True) -> List[str]:
        """
        Get list of unique destination locations for autocomplete
        
        Args:
            use_cache: Whether to use cached data
        
        Returns:
            List of unique destination locations
        """
        cache_key = 'diem_den'
        
        # Check cache
        if use_cache and cache_key in self._cache:
            logger.debug(f"Using cached data for {cache_key}")
            return self._cache[cache_key]
        
        try:
            # Query database - combine from trips and company_prices
            query = """
                SELECT DISTINCT diem_den 
                FROM (
                    SELECT diem_den FROM trips WHERE diem_den IS NOT NULL AND diem_den != ''
                    UNION
                    SELECT diem_den FROM company_prices WHERE diem_den IS NOT NULL AND diem_den != ''
                )
                ORDER BY diem_den
            """
            results = self.db.execute_query(query)
            locations = [row['diem_den'] for row in results]
            
            # Update cache
            self._cache[cache_key] = locations
            
            logger.info(f"Loaded {len(locations)} unique destination locations")
            return locations
            
        except Exception as e:
            logger.error(f"Error loading destination locations: {e}")
            return []
    
    def get_all_locations(self, use_cache: bool = True) -> List[str]:
        """
        Get list of all unique locations (both departure and destination)
        
        Args:
            use_cache: Whether to use cached data
        
        Returns:
            List of unique locations
        """
        cache_key = 'all_locations'
        
        # Check cache
        if use_cache and cache_key in self._cache:
            logger.debug(f"Using cached data for {cache_key}")
            return self._cache[cache_key]
        
        try:
            # Combine departure and destination locations
            departure = set(self.get_departure_locations(use_cache))
            destination = set(self.get_destination_locations(use_cache))
            
            # Merge and sort
            all_locations = sorted(departure.union(destination))
            
            # Update cache
            self._cache[cache_key] = all_locations
            
            logger.info(f"Loaded {len(all_locations)} unique locations")
            return all_locations
            
        except Exception as e:
            logger.error(f"Error loading all locations: {e}")
            return []
    
    def clear_cache(self, cache_key: Optional[str] = None):
        """
        Clear cached data
        
        Args:
            cache_key: Specific cache key to clear, or None to clear all
        """
        if cache_key:
            if cache_key in self._cache:
                del self._cache[cache_key]
                logger.debug(f"Cleared cache for {cache_key}")
        else:
            self._cache.clear()
            logger.debug("Cleared all cache")
    
    def invalidate_cache_on_update(self):
        """
        Invalidate cache when data is updated
        Should be called after insert/update/delete operations
        """
        self.clear_cache()
        logger.debug("Cache invalidated due to data update")
    
    def create_data_loader(self, field_type: str) -> Callable[[], List[str]]:
        """
        Create a data loader function for a specific field type
        
        Args:
            field_type: Type of field ('customer', 'diem_di', 'diem_den', 'location')
        
        Returns:
            Callable that returns list of strings
        """
        field_type = field_type.lower()
        
        if field_type in ('customer', 'khach_hang'):
            return lambda: self.get_customers()
        elif field_type in ('diem_di', 'departure'):
            return lambda: self.get_departure_locations()
        elif field_type in ('diem_den', 'destination'):
            return lambda: self.get_destination_locations()
        elif field_type in ('location', 'all_locations'):
            return lambda: self.get_all_locations()
        else:
            logger.warning(f"Unknown field type: {field_type}")
            return lambda: []
    
    def get_filtered_suggestions(self, field_type: str, filter_text: str, 
                                 max_results: int = 10) -> List[str]:
        """
        Get filtered suggestions for a field type
        
        Args:
            field_type: Type of field
            filter_text: Text to filter by
            max_results: Maximum number of results to return
        
        Returns:
            List of filtered suggestions
        """
        # Get all data for field type
        loader = self.create_data_loader(field_type)
        all_data = loader()
        
        if not filter_text:
            return all_data[:max_results]
        
        # Simple fuzzy matching
        filter_lower = filter_text.lower()
        
        # Exact matches first
        exact_matches = [item for item in all_data if item.lower() == filter_lower]
        
        # Starts with matches
        starts_with = [item for item in all_data 
                      if item.lower().startswith(filter_lower) and item not in exact_matches]
        
        # Contains matches
        contains = [item for item in all_data 
                   if filter_lower in item.lower() and item not in exact_matches and item not in starts_with]
        
        # Combine results
        results = exact_matches + starts_with + contains
        
        return results[:max_results]
