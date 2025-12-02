"""
Company Price Service - Business logic for managing company pricing information
Provides search, filtering, and caching for frequently accessed prices
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.models.company_price import CompanyPrice


logger = logging.getLogger(__name__)


class CompanyPriceService:
    """
    Service for managing company prices with search, filtering, and caching.
    
    Features:
    - Search prices by company, customer, locations
    - Filter by multiple criteria
    - Caching for frequently accessed prices
    - Support for multiple companies (A, B, C)
    """
    
    def __init__(self, db_manager: EnhancedDatabaseManager, cache_ttl: int = 300):
        """
        Initialize Company Price Service
        
        Args:
            db_manager: Database manager instance
            cache_ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)
        """
        self.db = db_manager
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
    
    def get_company_prices(
        self,
        company_name: str,
        filters: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> List[CompanyPrice]:
        """
        Get company prices with optional filters
        
        Args:
            company_name: Name of the company (e.g., "Company A", "Company B", "Company C")
            filters: Optional dictionary of filter criteria:
                    - khach_hang: Customer name (partial match)
                    - diem_di: Departure location (partial match)
                    - diem_den: Destination location (partial match)
            use_cache: Whether to use cached results (default: True)
        
        Returns:
            List of CompanyPrice objects matching criteria
        """
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(company_name, filters)
            
            # Check cache if enabled
            if use_cache and self._is_cache_valid(cache_key):
                logger.debug(f"Returning cached prices for {cache_key}")
                return self._cache[cache_key]['data']
            
            # Query database
            price_data_list = self.db.get_company_prices(company_name, filters or {})
            prices = [CompanyPrice(**price_data) for price_data in price_data_list]
            
            # Update cache
            if use_cache:
                self._update_cache(cache_key, prices)
            
            logger.info(f"Retrieved {len(prices)} prices for {company_name} with filters: {filters}")
            
            return prices
            
        except Exception as e:
            logger.error(f"Error retrieving company prices: {e}")
            raise
    
    def search_prices(
        self,
        company_name: str,
        khach_hang: Optional[str] = None,
        diem_di: Optional[str] = None,
        diem_den: Optional[str] = None,
        use_cache: bool = True
    ) -> List[CompanyPrice]:
        """
        Search company prices by customer and/or locations
        
        Args:
            company_name: Name of the company
            khach_hang: Customer name (partial match)
            diem_di: Departure location (partial match)
            diem_den: Destination location (partial match)
            use_cache: Whether to use cached results
        
        Returns:
            List of CompanyPrice objects matching search criteria
        """
        filters = {}
        
        if khach_hang:
            filters['khach_hang'] = khach_hang
        if diem_di:
            filters['diem_di'] = diem_di
        if diem_den:
            filters['diem_den'] = diem_den
        
        return self.get_company_prices(company_name, filters, use_cache)
    
    def get_price_for_route(
        self,
        company_name: str,
        khach_hang: str,
        diem_di: str,
        diem_den: str
    ) -> Optional[CompanyPrice]:
        """
        Get exact price for a specific route
        
        Args:
            company_name: Name of the company
            khach_hang: Customer name (exact match)
            diem_di: Departure location (exact match)
            diem_den: Destination location (exact match)
        
        Returns:
            CompanyPrice object if found, None otherwise
        """
        try:
            # Search with exact criteria
            prices = self.search_prices(
                company_name=company_name,
                khach_hang=khach_hang,
                diem_di=diem_di,
                diem_den=diem_den,
                use_cache=True
            )
            
            # Filter for exact matches
            for price in prices:
                if (price.khach_hang == khach_hang and
                    price.diem_di == diem_di and
                    price.diem_den == diem_den):
                    return price
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting price for route: {e}")
            raise
    
    def get_all_companies(self) -> List[str]:
        """
        Get list of all unique company names
        
        Returns:
            List of company names
        """
        try:
            query = "SELECT DISTINCT company_name FROM company_prices ORDER BY company_name"
            results = self.db.execute_query(query)
            return [row['company_name'] for row in results]
        except Exception as e:
            logger.error(f"Error getting company list: {e}")
            raise
    
    def get_unique_customers(self, company_name: Optional[str] = None) -> List[str]:
        """
        Get list of unique customer names for autocomplete
        
        Args:
            company_name: Optional company name to filter by
        
        Returns:
            List of unique customer names
        """
        try:
            if company_name:
                query = """
                    SELECT DISTINCT khach_hang 
                    FROM company_prices 
                    WHERE company_name = ? AND khach_hang IS NOT NULL AND khach_hang != ''
                    ORDER BY khach_hang
                """
                results = self.db.execute_query(query, (company_name,))
            else:
                query = """
                    SELECT DISTINCT khach_hang 
                    FROM company_prices 
                    WHERE khach_hang IS NOT NULL AND khach_hang != ''
                    ORDER BY khach_hang
                """
                results = self.db.execute_query(query)
            
            return [row['khach_hang'] for row in results]
        except Exception as e:
            logger.error(f"Error getting unique customers: {e}")
            raise
    
    def get_unique_locations(
        self,
        company_name: Optional[str] = None,
        location_type: str = 'both'
    ) -> Dict[str, List[str]]:
        """
        Get list of unique locations for autocomplete
        
        Args:
            company_name: Optional company name to filter by
            location_type: 'diem_di', 'diem_den', or 'both'
        
        Returns:
            Dictionary with 'diem_di' and/or 'diem_den' lists
        """
        try:
            result = {}
            
            if location_type in ['diem_di', 'both']:
                if company_name:
                    query = """
                        SELECT DISTINCT diem_di 
                        FROM company_prices 
                        WHERE company_name = ? AND diem_di IS NOT NULL AND diem_di != ''
                        ORDER BY diem_di
                    """
                    results = self.db.execute_query(query, (company_name,))
                else:
                    query = """
                        SELECT DISTINCT diem_di 
                        FROM company_prices 
                        WHERE diem_di IS NOT NULL AND diem_di != ''
                        ORDER BY diem_di
                    """
                    results = self.db.execute_query(query)
                
                result['diem_di'] = [row['diem_di'] for row in results]
            
            if location_type in ['diem_den', 'both']:
                if company_name:
                    query = """
                        SELECT DISTINCT diem_den 
                        FROM company_prices 
                        WHERE company_name = ? AND diem_den IS NOT NULL AND diem_den != ''
                        ORDER BY diem_den
                    """
                    results = self.db.execute_query(query, (company_name,))
                else:
                    query = """
                        SELECT DISTINCT diem_den 
                        FROM company_prices 
                        WHERE diem_den IS NOT NULL AND diem_den != ''
                        ORDER BY diem_den
                    """
                    results = self.db.execute_query(query)
                
                result['diem_den'] = [row['diem_den'] for row in results]
            
            return result
        except Exception as e:
            logger.error(f"Error getting unique locations: {e}")
            raise
    
    def create_company_price(self, price_data: Dict[str, Any]) -> CompanyPrice:
        """
        Create a new company price entry
        
        Args:
            price_data: Dictionary containing price information
        
        Returns:
            Created CompanyPrice object
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            # Validate using Pydantic model
            price = CompanyPrice(**price_data)
            
            # Insert into database
            price_id = self.db.insert_company_price(price.model_dump(exclude={'id', 'created_at'}))
            
            # Clear cache for this company
            self.invalidate_cache(price.company_name)
            
            # Retrieve and return the created price
            query = "SELECT * FROM company_prices WHERE id = ?"
            result = self.db.execute_query(query, (price_id,))
            
            if result:
                created_price = CompanyPrice(**result[0])
                logger.info(f"Created company price: {created_price.company_name} - {created_price.khach_hang}")
                return created_price
            
            raise Exception("Failed to retrieve created price")
            
        except ValueError as e:
            logger.error(f"Validation error creating company price: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating company price: {e}")
            raise
    
    def invalidate_cache(self, company_name: Optional[str] = None):
        """
        Invalidate cache entries
        
        Args:
            company_name: Optional company name to invalidate specific entries.
                         If None, invalidates all cache.
        """
        if company_name is None:
            self._cache.clear()
            self._cache_timestamps.clear()
            logger.debug("Cleared all price cache")
        else:
            # Remove cache entries for specific company
            keys_to_remove = [key for key in self._cache.keys() if company_name in key]
            for key in keys_to_remove:
                del self._cache[key]
                del self._cache_timestamps[key]
            logger.debug(f"Cleared cache for company: {company_name}")
    
    def _generate_cache_key(self, company_name: str, filters: Optional[Dict[str, Any]]) -> str:
        """
        Generate a cache key from company name and filters
        
        Args:
            company_name: Company name
            filters: Filter dictionary
        
        Returns:
            Cache key string
        """
        if not filters:
            return f"{company_name}:all"
        
        # Sort filters for consistent key generation
        filter_parts = [f"{k}={v}" for k, v in sorted(filters.items())]
        filter_str = ":".join(filter_parts)
        
        return f"{company_name}:{filter_str}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if cache entry is valid (exists and not expired)
        
        Args:
            cache_key: Cache key to check
        
        Returns:
            True if cache is valid, False otherwise
        """
        if cache_key not in self._cache:
            return False
        
        timestamp = self._cache_timestamps.get(cache_key)
        if not timestamp:
            return False
        
        # Check if cache has expired
        age = (datetime.now() - timestamp).total_seconds()
        return age < self.cache_ttl
    
    def _update_cache(self, cache_key: str, data: List[CompanyPrice]):
        """
        Update cache with new data
        
        Args:
            cache_key: Cache key
            data: Data to cache
        """
        self._cache[cache_key] = {'data': data}
        self._cache_timestamps[cache_key] = datetime.now()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'total_entries': len(self._cache),
            'cache_ttl': self.cache_ttl,
            'entries': list(self._cache.keys())
        }
