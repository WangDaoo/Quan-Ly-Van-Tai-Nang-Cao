"""
Query Optimizer Module
Provides query result caching, prepared statements, and query optimization utilities
"""

import sqlite3
import logging
import hashlib
import time
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache
from collections import OrderedDict


logger = logging.getLogger(__name__)


class LRUCache:
    """LRU Cache implementation for query results"""
    
    def __init__(self, max_size: int = 100):
        """
        Initialize LRU cache
        
        Args:
            max_size: Maximum number of items to cache
        """
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self.cache:
            self.hits += 1
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        self.misses += 1
        return None
    
    def put(self, key: str, value: Any):
        """Put item in cache"""
        if key in self.cache:
            # Update existing item
            self.cache.move_to_end(key)
        else:
            # Add new item
            if len(self.cache) >= self.max_size:
                # Remove least recently used item
                self.cache.popitem(last=False)
        self.cache[key] = value
    
    def clear(self):
        """Clear all cached items"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def invalidate(self, pattern: str = None):
        """
        Invalidate cache entries matching pattern
        
        Args:
            pattern: Pattern to match keys (None = clear all)
        """
        if pattern is None:
            self.clear()
        else:
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.2f}%"
        }


class PreparedStatementCache:
    """Cache for prepared SQL statements"""
    
    def __init__(self):
        """Initialize prepared statement cache"""
        self.statements: Dict[str, str] = {}
        
        # Common queries that benefit from prepared statements
        self._initialize_common_queries()
    
    def _initialize_common_queries(self):
        """Initialize commonly used prepared statements"""
        # Trip queries
        self.statements['get_trip_by_id'] = "SELECT * FROM trips WHERE id = ?"
        self.statements['get_trips_paginated'] = "SELECT * FROM trips ORDER BY created_at DESC LIMIT ? OFFSET ?"
        self.statements['search_trips_by_customer'] = "SELECT * FROM trips WHERE khach_hang LIKE ? ORDER BY created_at DESC"
        self.statements['search_trips_by_route'] = "SELECT * FROM trips WHERE diem_di LIKE ? AND diem_den LIKE ? ORDER BY created_at DESC"
        self.statements['get_next_trip_code'] = "SELECT ma_chuyen FROM trips ORDER BY id DESC LIMIT 1"
        
        # Company price queries
        self.statements['get_company_prices'] = "SELECT * FROM company_prices WHERE company_name = ? ORDER BY created_at DESC"
        self.statements['search_company_prices'] = """
            SELECT * FROM company_prices 
            WHERE company_name = ? AND khach_hang LIKE ? AND diem_di LIKE ? AND diem_den LIKE ?
            ORDER BY created_at DESC
        """
        
        # Department queries
        self.statements['get_all_departments'] = "SELECT * FROM departments WHERE is_active = 1 ORDER BY name"
        self.statements['get_department_by_id'] = "SELECT * FROM departments WHERE id = ?"
        
        # Employee queries
        self.statements['get_employees_by_dept'] = "SELECT * FROM employees WHERE department_id = ? AND is_active = 1"
        
        # Field configuration queries
        self.statements['get_field_configs'] = """
            SELECT * FROM field_configurations 
            WHERE department_id = ? AND is_active = 1 
            ORDER BY display_order, field_name
        """
        
        # Formula queries
        self.statements['get_formulas'] = "SELECT * FROM formulas WHERE department_id = ? AND is_active = 1"
        
        # Push condition queries
        self.statements['get_push_conditions'] = """
            SELECT * FROM push_conditions 
            WHERE source_department_id = ? AND target_department_id = ? AND is_active = 1
            ORDER BY condition_order
        """
        
        # Workflow history queries
        self.statements['get_workflow_history'] = """
            SELECT * FROM workflow_history 
            WHERE record_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """
        
        # Workspace queries
        self.statements['get_workspaces'] = "SELECT * FROM employee_workspaces WHERE employee_id = ? ORDER BY workspace_name"
        
        # Autocomplete queries
        self.statements['autocomplete_customers'] = "SELECT DISTINCT khach_hang FROM trips WHERE khach_hang LIKE ? LIMIT 20"
        self.statements['autocomplete_diem_di'] = "SELECT DISTINCT diem_di FROM trips WHERE diem_di LIKE ? LIMIT 20"
        self.statements['autocomplete_diem_den'] = "SELECT DISTINCT diem_den FROM trips WHERE diem_den LIKE ? LIMIT 20"
    
    def get(self, query_name: str) -> Optional[str]:
        """Get prepared statement by name"""
        return self.statements.get(query_name)
    
    def add(self, query_name: str, query: str):
        """Add a prepared statement"""
        self.statements[query_name] = query
    
    def list_all(self) -> List[str]:
        """List all prepared statement names"""
        return list(self.statements.keys())


class QueryOptimizer:
    """Query optimization utilities with caching and prepared statements"""
    
    def __init__(self, cache_size: int = 100, enable_cache: bool = True):
        """
        Initialize query optimizer
        
        Args:
            cache_size: Maximum number of cached query results
            enable_cache: Whether to enable query result caching
        """
        self.cache = LRUCache(max_size=cache_size)
        self.prepared_statements = PreparedStatementCache()
        self.enable_cache = enable_cache
        self.query_stats: Dict[str, Dict[str, Any]] = {}
    
    def _generate_cache_key(self, query: str, params: tuple) -> str:
        """Generate cache key from query and parameters"""
        key_str = f"{query}:{params}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def execute_cached_query(
        self, 
        conn: sqlite3.Connection, 
        query: str, 
        params: tuple = (),
        cache_ttl: int = 300
    ) -> List[Dict[str, Any]]:
        """
        Execute query with caching
        
        Args:
            conn: Database connection
            query: SQL query
            params: Query parameters
            cache_ttl: Cache time-to-live in seconds (not implemented yet)
            
        Returns:
            Query results
        """
        # Generate cache key
        cache_key = self._generate_cache_key(query, params)
        
        # Check cache if enabled
        if self.enable_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return cached_result
        
        # Execute query
        start_time = time.time()
        try:
            cursor = conn.execute(query, params)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Cache results
            if self.enable_cache:
                self.cache.put(cache_key, results)
            
            # Track query stats
            execution_time = time.time() - start_time
            self._track_query_stats(query, execution_time, len(results))
            
            return results
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}\nQuery: {query}")
            raise
    
    def execute_prepared_query(
        self,
        conn: sqlite3.Connection,
        query_name: str,
        params: tuple = (),
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute a prepared statement
        
        Args:
            conn: Database connection
            query_name: Name of prepared statement
            params: Query parameters
            use_cache: Whether to use caching
            
        Returns:
            Query results
        """
        query = self.prepared_statements.get(query_name)
        if query is None:
            raise ValueError(f"Prepared statement '{query_name}' not found")
        
        if use_cache:
            return self.execute_cached_query(conn, query, params)
        else:
            cursor = conn.execute(query, params)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def _track_query_stats(self, query: str, execution_time: float, result_count: int):
        """Track query execution statistics"""
        # Use first 100 chars of query as key
        query_key = query[:100]
        
        if query_key not in self.query_stats:
            self.query_stats[query_key] = {
                'count': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'max_time': 0.0,
                'min_time': float('inf'),
                'total_results': 0
            }
        
        stats = self.query_stats[query_key]
        stats['count'] += 1
        stats['total_time'] += execution_time
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['max_time'] = max(stats['max_time'], execution_time)
        stats['min_time'] = min(stats['min_time'], execution_time)
        stats['total_results'] += result_count
    
    def invalidate_cache(self, pattern: str = None):
        """
        Invalidate cached queries
        
        Args:
            pattern: Pattern to match (None = clear all)
        """
        self.cache.invalidate(pattern)
        logger.info(f"Cache invalidated: {pattern or 'all'}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def get_query_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get query execution statistics"""
        return self.query_stats
    
    def get_slow_queries(self, threshold_ms: float = 100.0) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get queries that exceed execution time threshold
        
        Args:
            threshold_ms: Threshold in milliseconds
            
        Returns:
            List of (query, stats) tuples
        """
        threshold_sec = threshold_ms / 1000.0
        slow_queries = [
            (query, stats) 
            for query, stats in self.query_stats.items() 
            if stats['avg_time'] > threshold_sec
        ]
        return sorted(slow_queries, key=lambda x: x[1]['avg_time'], reverse=True)
    
    def optimize_query(self, query: str) -> str:
        """
        Suggest optimizations for a query
        
        Args:
            query: SQL query to optimize
            
        Returns:
            Optimized query or original if no optimizations found
        """
        optimized = query
        
        # Add LIMIT if not present in SELECT queries
        if 'SELECT' in query.upper() and 'LIMIT' not in query.upper():
            logger.warning(f"Query without LIMIT clause: {query[:50]}...")
            # Don't auto-add LIMIT, just warn
        
        # Suggest using indexes
        if 'WHERE' in query.upper():
            logger.debug("Query uses WHERE clause - ensure appropriate indexes exist")
        
        return optimized
    
    def analyze_table(self, conn: sqlite3.Connection, table_name: str) -> Dict[str, Any]:
        """
        Analyze table statistics
        
        Args:
            conn: Database connection
            table_name: Name of table to analyze
            
        Returns:
            Table statistics
        """
        stats = {}
        
        # Get row count
        cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        stats['row_count'] = cursor.fetchone()[0]
        
        # Get table info
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        stats['columns'] = [row[1] for row in cursor.fetchall()]
        
        # Get index info
        cursor = conn.execute(f"PRAGMA index_list({table_name})")
        stats['indexes'] = [row[1] for row in cursor.fetchall()]
        
        return stats
    
    def suggest_indexes(self, conn: sqlite3.Connection) -> List[str]:
        """
        Suggest missing indexes based on query patterns
        
        Args:
            conn: Database connection
            
        Returns:
            List of suggested CREATE INDEX statements
        """
        suggestions = []
        
        # Analyze slow queries
        slow_queries = self.get_slow_queries(threshold_ms=50.0)
        
        for query, stats in slow_queries:
            # Simple heuristic: look for WHERE clauses without indexes
            if 'WHERE' in query.upper() and stats['avg_time'] > 0.1:
                suggestions.append(f"-- Consider adding index for: {query[:80]}...")
        
        return suggestions


# Global query optimizer instance
_query_optimizer: Optional[QueryOptimizer] = None


def get_query_optimizer(cache_size: int = 100) -> QueryOptimizer:
    """Get or create global query optimizer instance"""
    global _query_optimizer
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer(cache_size=cache_size)
    return _query_optimizer


def reset_query_optimizer():
    """Reset global query optimizer instance"""
    global _query_optimizer
    _query_optimizer = None
