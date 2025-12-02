"""
Enhanced Database Manager with Connection Pooling
Provides CRUD operations, transaction support, and query optimization

Requirements: 16.1, 16.2, 17.1, 17.3, 17.5
"""

import sqlite3
import logging
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from contextlib import contextmanager

from .connection_pool import ConnectionPool
from .query_optimizer import QueryOptimizer
from ..utils.error_handler import DatabaseError, ErrorHandler, handle_errors


logger = logging.getLogger(__name__)


class EnhancedDatabaseManager:
    """Enhanced database manager with connection pooling and transaction support"""
    
    def __init__(self, database_path: str = "data/transport.db", pool_size: int = 5, enable_query_cache: bool = True):
        """
        Initialize database manager
        
        Args:
            database_path: Path to SQLite database file
            pool_size: Number of connections in pool
            enable_query_cache: Whether to enable query result caching
        """
        self.database_path = database_path
        self.pool = ConnectionPool(database_path, pool_size)
        self.query_optimizer = QueryOptimizer(cache_size=100, enable_cache=enable_query_cache)
        self._initialize_database()
    
    @handle_errors(context="Database initialization", reraise=True)
    def _initialize_database(self):
        """Initialize database with schema if not exists"""
        schema_path = Path(__file__).parent / "enhanced_schema.sql"
        
        if not schema_path.exists():
            raise DatabaseError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn = self.pool.get_connection()
        try:
            conn.executescript(schema_sql)
            conn.commit()
            logger.info("Database schema initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise DatabaseError(f"Schema initialization failed: {str(e)}")
        finally:
            self.pool.return_connection(conn)
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for getting and returning connections
        
        Yields:
            Database connection
        """
        conn = self.pool.get_connection()
        try:
            yield conn
        finally:
            self.pool.return_connection(conn)
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions with automatic rollback
        
        Yields:
            Database connection
        """
        conn = self.pool.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rolled back due to error: {e}")
            raise
        finally:
            self.pool.return_connection(conn)
    
    # ========================================================================
    # Generic CRUD Operations
    # ========================================================================
    
    def execute_query(self, query: str, params: tuple = (), use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
            use_cache: Whether to use query result caching
            
        Returns:
            List of result rows as dictionaries
        """
        with self.get_connection() as conn:
            try:
                if use_cache:
                    return self.query_optimizer.execute_cached_query(conn, query, params)
                else:
                    cursor = conn.execute(query, params)
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    return results
            except sqlite3.Error as e:
                logger.error(f"Query execution failed: {e}\nQuery: {query}")
                raise DatabaseError(f"Query failed: {str(e)}", query=query)
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        with self.transaction() as conn:
            try:
                cursor = conn.execute(query, params)
                return cursor.rowcount
            except sqlite3.Error as e:
                logger.error(f"Update execution failed: {e}\nQuery: {query}")
                raise DatabaseError(f"Update failed: {str(e)}", query=query)
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT query and return the last inserted row ID
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Last inserted row ID
        """
        with self.transaction() as conn:
            try:
                cursor = conn.execute(query, params)
                return cursor.lastrowid
            except sqlite3.Error as e:
                logger.error(f"Insert execution failed: {e}\nQuery: {query}")
                raise DatabaseError(f"Insert failed: {str(e)}", query=query)
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute a query multiple times with different parameters
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Total number of affected rows
        """
        with self.transaction() as conn:
            try:
                cursor = conn.executemany(query, params_list)
                return cursor.rowcount
            except sqlite3.Error as e:
                logger.error(f"Batch execution failed: {e}\nQuery: {query}")
                raise DatabaseError(f"Batch execution failed: {str(e)}", query=query)
    
    # ========================================================================
    # Trips Table Operations
    # ========================================================================
    
    def insert_trip(self, trip_data: Dict[str, Any]) -> int:
        """Insert a new trip record"""
        query = """
            INSERT INTO trips (ma_chuyen, khach_hang, diem_di, diem_den, 
                             gia_ca, khoan_luong, chi_phi_khac, ghi_chu)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            trip_data.get('ma_chuyen'),
            trip_data.get('khach_hang'),
            trip_data.get('diem_di', ''),
            trip_data.get('diem_den', ''),
            trip_data.get('gia_ca'),
            trip_data.get('khoan_luong', 0),
            trip_data.get('chi_phi_khac', 0),
            trip_data.get('ghi_chu', '')
        )
        return self.execute_insert(query, params)
    
    def update_trip(self, trip_id: int, trip_data: Dict[str, Any]) -> int:
        """Update an existing trip record"""
        query = """
            UPDATE trips 
            SET khach_hang = ?, diem_di = ?, diem_den = ?, 
                gia_ca = ?, khoan_luong = ?, chi_phi_khac = ?, ghi_chu = ?
            WHERE id = ?
        """
        params = (
            trip_data.get('khach_hang'),
            trip_data.get('diem_di', ''),
            trip_data.get('diem_den', ''),
            trip_data.get('gia_ca'),
            trip_data.get('khoan_luong', 0),
            trip_data.get('chi_phi_khac', 0),
            trip_data.get('ghi_chu', ''),
            trip_id
        )
        return self.execute_update(query, params)
    
    def delete_trip(self, trip_id: int) -> int:
        """Delete a trip record"""
        query = "DELETE FROM trips WHERE id = ?"
        return self.execute_update(query, (trip_id,))
    
    def get_trip_by_id(self, trip_id: int) -> Optional[Dict[str, Any]]:
        """Get a trip by ID"""
        query = "SELECT * FROM trips WHERE id = ?"
        results = self.execute_query(query, (trip_id,))
        return results[0] if results else None
    
    def get_all_trips(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all trips with pagination"""
        query = "SELECT * FROM trips ORDER BY created_at DESC LIMIT ? OFFSET ?"
        return self.execute_query(query, (limit, offset))
    
    def search_trips(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search trips with filters"""
        conditions = []
        params = []
        
        if 'khach_hang' in filters:
            conditions.append("khach_hang LIKE ?")
            params.append(f"%{filters['khach_hang']}%")
        
        if 'diem_di' in filters:
            conditions.append("diem_di LIKE ?")
            params.append(f"%{filters['diem_di']}%")
        
        if 'diem_den' in filters:
            conditions.append("diem_den LIKE ?")
            params.append(f"%{filters['diem_den']}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM trips WHERE {where_clause} ORDER BY created_at DESC"
        
        return self.execute_query(query, tuple(params))
    
    def get_next_trip_code(self) -> str:
        """Generate next trip code (C001, C002, etc.)"""
        query = "SELECT ma_chuyen FROM trips ORDER BY id DESC LIMIT 1"
        results = self.execute_query(query)
        
        if not results:
            return "C001"
        
        last_code = results[0]['ma_chuyen']
        if last_code and last_code.startswith('C'):
            try:
                number = int(last_code[1:])
                return f"C{number + 1:03d}"
            except ValueError:
                pass
        
        return "C001"
    
    # ========================================================================
    # Company Prices Table Operations
    # ========================================================================
    
    def insert_company_price(self, price_data: Dict[str, Any]) -> int:
        """Insert a company price record"""
        query = """
            INSERT INTO company_prices (company_name, khach_hang, diem_di, 
                                       diem_den, gia_ca, khoan_luong)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            price_data.get('company_name'),
            price_data.get('khach_hang'),
            price_data.get('diem_di'),
            price_data.get('diem_den'),
            price_data.get('gia_ca'),
            price_data.get('khoan_luong')
        )
        return self.execute_insert(query, params)
    
    def get_company_prices(self, company_name: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get company prices with optional filters"""
        conditions = ["company_name = ?"]
        params = [company_name]
        
        if filters:
            if 'khach_hang' in filters:
                conditions.append("khach_hang LIKE ?")
                params.append(f"%{filters['khach_hang']}%")
            
            if 'diem_di' in filters:
                conditions.append("diem_di LIKE ?")
                params.append(f"%{filters['diem_di']}%")
            
            if 'diem_den' in filters:
                conditions.append("diem_den LIKE ?")
                params.append(f"%{filters['diem_den']}%")
        
        where_clause = " AND ".join(conditions)
        query = f"SELECT * FROM company_prices WHERE {where_clause} ORDER BY created_at DESC"
        
        return self.execute_query(query, tuple(params))
    
    # ========================================================================
    # Departments Table Operations
    # ========================================================================
    
    def insert_department(self, dept_data: Dict[str, Any]) -> int:
        """Insert a department"""
        query = """
            INSERT INTO departments (name, display_name, description, is_active)
            VALUES (?, ?, ?, ?)
        """
        params = (
            dept_data.get('name'),
            dept_data.get('display_name'),
            dept_data.get('description', ''),
            dept_data.get('is_active', 1)
        )
        return self.execute_insert(query, params)
    
    def get_all_departments(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all departments"""
        query = "SELECT * FROM departments"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        return self.execute_query(query)
    
    def get_department_by_id(self, dept_id: int) -> Optional[Dict[str, Any]]:
        """Get department by ID"""
        query = "SELECT * FROM departments WHERE id = ?"
        results = self.execute_query(query, (dept_id,))
        return results[0] if results else None
    
    # ========================================================================
    # Employees Table Operations
    # ========================================================================
    
    def insert_employee(self, emp_data: Dict[str, Any]) -> int:
        """Insert an employee"""
        query = """
            INSERT INTO employees (username, full_name, email, department_id, is_active)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            emp_data.get('username'),
            emp_data.get('full_name'),
            emp_data.get('email'),
            emp_data.get('department_id'),
            emp_data.get('is_active', 1)
        )
        return self.execute_insert(query, params)
    
    def get_employees_by_department(self, dept_id: int) -> List[Dict[str, Any]]:
        """Get employees by department"""
        query = "SELECT * FROM employees WHERE department_id = ? AND is_active = 1"
        return self.execute_query(query, (dept_id,))
    
    # ========================================================================
    # Field Configurations Table Operations
    # ========================================================================
    
    def insert_field_configuration(self, config_data: Dict[str, Any]) -> int:
        """Insert a field configuration"""
        query = """
            INSERT INTO field_configurations 
            (department_id, field_name, field_type, widget_type, is_required,
             validation_rules, default_value, options, display_order, category, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            config_data.get('department_id'),
            config_data.get('field_name'),
            config_data.get('field_type'),
            config_data.get('widget_type'),
            config_data.get('is_required', 0),
            config_data.get('validation_rules'),
            config_data.get('default_value'),
            config_data.get('options'),
            config_data.get('display_order', 0),
            config_data.get('category'),
            config_data.get('is_active', 1)
        )
        return self.execute_insert(query, params)
    
    def get_field_configurations(self, dept_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get field configurations for a department"""
        query = "SELECT * FROM field_configurations WHERE department_id = ?"
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY display_order, field_name"
        return self.execute_query(query, (dept_id,))
    
    # ========================================================================
    # Formulas Table Operations
    # ========================================================================
    
    def insert_formula(self, formula_data: Dict[str, Any]) -> int:
        """Insert a formula"""
        query = """
            INSERT INTO formulas (department_id, target_field, formula_expression, description, is_active)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            formula_data.get('department_id'),
            formula_data.get('target_field'),
            formula_data.get('formula_expression'),
            formula_data.get('description', ''),
            formula_data.get('is_active', 1)
        )
        return self.execute_insert(query, params)
    
    def get_formulas(self, dept_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get formulas for a department"""
        query = "SELECT * FROM formulas WHERE department_id = ?"
        if active_only:
            query += " AND is_active = 1"
        return self.execute_query(query, (dept_id,))
    
    # ========================================================================
    # Push Conditions Table Operations
    # ========================================================================
    
    def insert_push_condition(self, condition_data: Dict[str, Any]) -> int:
        """Insert a push condition"""
        query = """
            INSERT INTO push_conditions 
            (source_department_id, target_department_id, field_name, operator, 
             value, logic_operator, condition_order, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            condition_data.get('source_department_id'),
            condition_data.get('target_department_id'),
            condition_data.get('field_name'),
            condition_data.get('operator'),
            condition_data.get('value'),
            condition_data.get('logic_operator', 'AND'),
            condition_data.get('condition_order', 0),
            condition_data.get('is_active', 1)
        )
        return self.execute_insert(query, params)
    
    def get_push_conditions(self, source_dept_id: int, target_dept_id: int) -> List[Dict[str, Any]]:
        """Get push conditions between departments"""
        query = """
            SELECT * FROM push_conditions 
            WHERE source_department_id = ? AND target_department_id = ? AND is_active = 1
            ORDER BY condition_order
        """
        return self.execute_query(query, (source_dept_id, target_dept_id))
    
    # ========================================================================
    # Workflow History Table Operations
    # ========================================================================
    
    def insert_workflow_history(self, history_data: Dict[str, Any]) -> int:
        """Insert workflow history record"""
        query = """
            INSERT INTO workflow_history 
            (record_id, source_department_id, target_department_id, pushed_by, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            history_data.get('record_id'),
            history_data.get('source_department_id'),
            history_data.get('target_department_id'),
            history_data.get('pushed_by'),
            history_data.get('status'),
            history_data.get('error_message')
        )
        return self.execute_insert(query, params)
    
    def get_workflow_history(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get workflow history with filters"""
        conditions = []
        params = []
        
        if filters:
            if 'record_id' in filters:
                conditions.append("record_id = ?")
                params.append(filters['record_id'])
            
            if 'source_department_id' in filters:
                conditions.append("source_department_id = ?")
                params.append(filters['source_department_id'])
            
            if 'status' in filters:
                conditions.append("status = ?")
                params.append(filters['status'])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM workflow_history WHERE {where_clause} ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        return self.execute_query(query, tuple(params))
    
    # ========================================================================
    # Employee Workspaces Table Operations
    # ========================================================================
    
    def insert_workspace(self, workspace_data: Dict[str, Any]) -> int:
        """Insert an employee workspace"""
        query = """
            INSERT INTO employee_workspaces (employee_id, workspace_name, is_active, configuration)
            VALUES (?, ?, ?, ?)
        """
        params = (
            workspace_data.get('employee_id'),
            workspace_data.get('workspace_name'),
            workspace_data.get('is_active', 1),
            workspace_data.get('configuration')
        )
        return self.execute_insert(query, params)
    
    def get_workspaces(self, employee_id: int) -> List[Dict[str, Any]]:
        """Get workspaces for an employee"""
        query = "SELECT * FROM employee_workspaces WHERE employee_id = ? ORDER BY workspace_name"
        return self.execute_query(query, (employee_id,))
    
    # ========================================================================
    # Business Records Table Operations
    # ========================================================================
    
    def insert_business_record(self, record_data: Dict[str, Any]) -> int:
        """Insert a business record"""
        query = """
            INSERT INTO business_records 
            (department_id, employee_id, workspace_id, record_data, status)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            record_data.get('department_id'),
            record_data.get('employee_id'),
            record_data.get('workspace_id'),
            record_data.get('record_data'),
            record_data.get('status', 'active')
        )
        return self.execute_insert(query, params)
    
    def get_business_records(self, dept_id: int, status: str = 'active') -> List[Dict[str, Any]]:
        """Get business records for a department"""
        query = "SELECT * FROM business_records WHERE department_id = ? AND status = ? ORDER BY created_at DESC"
        return self.execute_query(query, (dept_id, status))
    
    # ========================================================================
    # Query Optimization Methods
    # ========================================================================
    
    def execute_prepared_query(self, query_name: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a prepared statement with caching
        
        Args:
            query_name: Name of prepared statement
            params: Query parameters
            
        Returns:
            Query results
        """
        with self.get_connection() as conn:
            return self.query_optimizer.execute_prepared_query(conn, query_name, params)
    
    def invalidate_cache(self, pattern: str = None):
        """
        Invalidate query cache
        
        Args:
            pattern: Pattern to match (None = clear all)
        """
        self.query_optimizer.invalidate_cache(pattern)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get query cache statistics"""
        return self.query_optimizer.get_cache_stats()
    
    def get_query_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get query execution statistics"""
        return self.query_optimizer.get_query_stats()
    
    def get_slow_queries(self, threshold_ms: float = 100.0) -> List[tuple]:
        """
        Get slow queries exceeding threshold
        
        Args:
            threshold_ms: Threshold in milliseconds
            
        Returns:
            List of (query, stats) tuples
        """
        return self.query_optimizer.get_slow_queries(threshold_ms)
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze database performance
        
        Returns:
            Performance analysis report
        """
        with self.get_connection() as conn:
            report = {
                'cache_stats': self.get_cache_stats(),
                'query_stats': self.get_query_stats(),
                'slow_queries': self.get_slow_queries(threshold_ms=50.0),
                'table_stats': {}
            }
            
            # Analyze key tables
            for table in ['trips', 'company_prices', 'field_configurations', 'workflow_history']:
                try:
                    report['table_stats'][table] = self.query_optimizer.analyze_table(conn, table)
                except sqlite3.Error:
                    pass
            
            return report
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def close(self):
        """Close all database connections"""
        self.pool.close_all()
        logger.info("Database connections closed")
