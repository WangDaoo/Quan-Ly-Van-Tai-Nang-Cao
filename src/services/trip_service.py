"""
Trip Service - Business logic for managing transportation trips
Provides CRUD operations, auto-generate trip codes, search, filtering, and pagination
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.models.trip import Trip


logger = logging.getLogger(__name__)


class TripService:
    """
    Service for managing trips with CRUD operations, search, filtering, and pagination.
    
    Features:
    - Auto-generate trip codes (C001, C002, ...)
    - Search and filtering by customer, locations
    - Pagination for large datasets
    - Validation using Trip model
    """
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        """
        Initialize Trip Service
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def create_trip(self, trip_data: Dict[str, Any]) -> Trip:
        """
        Create a new trip with auto-generated trip code
        
        Args:
            trip_data: Dictionary containing trip information
                      (ma_chuyen will be auto-generated if not provided)
        
        Returns:
            Created Trip object
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            # Auto-generate trip code if not provided
            if 'ma_chuyen' not in trip_data or not trip_data['ma_chuyen']:
                trip_data['ma_chuyen'] = self.generate_next_trip_code()
            
            # Validate using Pydantic model
            trip = Trip(**trip_data)
            
            # Insert into database
            trip_id = self.db.insert_trip(trip.model_dump(exclude={'id', 'created_at', 'updated_at'}))
            
            # Retrieve and return the created trip
            created_trip = self.get_trip_by_id(trip_id)
            
            logger.info(f"Created trip: {created_trip.ma_chuyen} (ID: {trip_id})")
            
            return created_trip
            
        except ValueError as e:
            logger.error(f"Validation error creating trip: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating trip: {e}")
            raise
    
    def update_trip(self, trip_id: int, trip_data: Dict[str, Any]) -> Trip:
        """
        Update an existing trip
        
        Args:
            trip_id: ID of trip to update
            trip_data: Dictionary containing updated trip information
        
        Returns:
            Updated Trip object
            
        Raises:
            ValueError: If trip not found or validation fails
            Exception: If database operation fails
        """
        try:
            # Check if trip exists
            existing_trip = self.get_trip_by_id(trip_id)
            if not existing_trip:
                raise ValueError(f"Trip với ID {trip_id} không tồn tại")
            
            # Merge existing data with updates
            updated_data = existing_trip.model_dump()
            updated_data.update(trip_data)
            
            # Validate using Pydantic model
            trip = Trip(**updated_data)
            
            # Update in database
            self.db.update_trip(trip_id, trip.model_dump(exclude={'id', 'ma_chuyen', 'created_at', 'updated_at'}))
            
            # Retrieve and return the updated trip
            updated_trip = self.get_trip_by_id(trip_id)
            
            logger.info(f"Updated trip: {updated_trip.ma_chuyen} (ID: {trip_id})")
            
            return updated_trip
            
        except ValueError as e:
            logger.error(f"Validation error updating trip: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating trip: {e}")
            raise
    
    def delete_trip(self, trip_id: int) -> bool:
        """
        Delete a trip
        
        Args:
            trip_id: ID of trip to delete
        
        Returns:
            True if deleted successfully
            
        Raises:
            ValueError: If trip not found
            Exception: If database operation fails
        """
        try:
            # Check if trip exists
            existing_trip = self.get_trip_by_id(trip_id)
            if not existing_trip:
                raise ValueError(f"Trip với ID {trip_id} không tồn tại")
            
            # Delete from database
            rows_affected = self.db.delete_trip(trip_id)
            
            if rows_affected > 0:
                logger.info(f"Deleted trip: {existing_trip.ma_chuyen} (ID: {trip_id})")
                return True
            
            return False
            
        except ValueError as e:
            logger.error(f"Error deleting trip: {e}")
            raise
        except Exception as e:
            logger.error(f"Error deleting trip: {e}")
            raise
    
    def get_trip_by_id(self, trip_id: int) -> Optional[Trip]:
        """
        Get a trip by ID
        
        Args:
            trip_id: ID of trip to retrieve
        
        Returns:
            Trip object if found, None otherwise
        """
        try:
            trip_data = self.db.get_trip_by_id(trip_id)
            
            if trip_data:
                return Trip(**trip_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving trip {trip_id}: {e}")
            raise
    
    def get_all_trips(self, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """
        Get all trips with pagination
        
        Args:
            page: Page number (1-based)
            page_size: Number of records per page
        
        Returns:
            Dictionary containing:
            - trips: List of Trip objects
            - total: Total number of trips
            - page: Current page number
            - page_size: Records per page
            - total_pages: Total number of pages
        """
        try:
            # Calculate offset
            offset = (page - 1) * page_size
            
            # Get trips from database
            trip_data_list = self.db.get_all_trips(limit=page_size, offset=offset)
            trips = [Trip(**trip_data) for trip_data in trip_data_list]
            
            # Get total count
            total = self.get_total_count()
            total_pages = (total + page_size - 1) // page_size  # Ceiling division
            
            return {
                'trips': trips,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages
            }
            
        except Exception as e:
            logger.error(f"Error retrieving trips: {e}")
            raise
    
    def search_trips(self, filters: Dict[str, Any], page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """
        Search trips with filters and pagination
        
        Args:
            filters: Dictionary of filter criteria:
                    - khach_hang: Customer name (partial match)
                    - diem_di: Departure location (partial match)
                    - diem_den: Destination location (partial match)
                    - ma_chuyen: Trip code (partial match)
            page: Page number (1-based)
            page_size: Number of records per page
        
        Returns:
            Dictionary containing:
            - trips: List of Trip objects matching filters
            - total: Total number of matching trips
            - page: Current page number
            - page_size: Records per page
            - total_pages: Total number of pages
            - filters: Applied filters
        """
        try:
            # Get all matching trips (we'll handle pagination in memory for simplicity)
            trip_data_list = self.db.search_trips(filters)
            
            # Convert to Trip objects
            all_trips = [Trip(**trip_data) for trip_data in trip_data_list]
            
            # Apply pagination
            total = len(all_trips)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_trips = all_trips[start_idx:end_idx]
            
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1
            
            logger.info(f"Search found {total} trips matching filters: {filters}")
            
            return {
                'trips': paginated_trips,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'filters': filters
            }
            
        except Exception as e:
            logger.error(f"Error searching trips: {e}")
            raise
    
    def generate_next_trip_code(self) -> str:
        """
        Generate the next trip code in sequence (C001, C002, ...)
        
        Returns:
            Next trip code string
        """
        try:
            return self.db.get_next_trip_code()
        except Exception as e:
            logger.error(f"Error generating trip code: {e}")
            raise
    
    def get_total_count(self) -> int:
        """
        Get total count of all trips
        
        Returns:
            Total number of trips
        """
        try:
            query = "SELECT COUNT(*) as count FROM trips"
            result = self.db.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting trip count: {e}")
            raise
    
    def get_unique_customers(self) -> List[str]:
        """
        Get list of unique customer names for autocomplete
        
        Returns:
            List of unique customer names
        """
        try:
            query = "SELECT DISTINCT khach_hang FROM trips WHERE khach_hang IS NOT NULL AND khach_hang != '' ORDER BY khach_hang"
            results = self.db.execute_query(query)
            return [row['khach_hang'] for row in results]
        except Exception as e:
            logger.error(f"Error getting unique customers: {e}")
            raise
    
    def get_unique_locations(self, location_type: str = 'both') -> Dict[str, List[str]]:
        """
        Get list of unique locations for autocomplete
        
        Args:
            location_type: 'diem_di', 'diem_den', or 'both'
        
        Returns:
            Dictionary with 'diem_di' and/or 'diem_den' lists
        """
        try:
            result = {}
            
            if location_type in ['diem_di', 'both']:
                query = "SELECT DISTINCT diem_di FROM trips WHERE diem_di IS NOT NULL AND diem_di != '' ORDER BY diem_di"
                results = self.db.execute_query(query)
                result['diem_di'] = [row['diem_di'] for row in results]
            
            if location_type in ['diem_den', 'both']:
                query = "SELECT DISTINCT diem_den FROM trips WHERE diem_den IS NOT NULL AND diem_den != '' ORDER BY diem_den"
                results = self.db.execute_query(query)
                result['diem_den'] = [row['diem_den'] for row in results]
            
            return result
        except Exception as e:
            logger.error(f"Error getting unique locations: {e}")
            raise
    
    def bulk_create_trips(self, trips_data: List[Dict[str, Any]]) -> List[Trip]:
        """
        Create multiple trips in a single transaction
        
        Args:
            trips_data: List of trip data dictionaries
        
        Returns:
            List of created Trip objects
            
        Raises:
            ValueError: If any validation fails
            Exception: If database operation fails
        """
        created_trips = []
        
        try:
            for trip_data in trips_data:
                trip = self.create_trip(trip_data)
                created_trips.append(trip)
            
            logger.info(f"Bulk created {len(created_trips)} trips")
            
            return created_trips
            
        except Exception as e:
            logger.error(f"Error in bulk create trips: {e}")
            raise
