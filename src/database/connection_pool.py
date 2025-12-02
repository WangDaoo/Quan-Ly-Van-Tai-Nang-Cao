"""
Connection Pool for SQLite Database
Provides thread-safe connection pooling for improved performance
"""

import sqlite3
import threading
from queue import Queue, Empty
from typing import Optional
from pathlib import Path


class ConnectionPool:
    """Thread-safe connection pool for SQLite database"""
    
    def __init__(self, database_path: str, pool_size: int = 5):
        """
        Initialize connection pool
        
        Args:
            database_path: Path to SQLite database file
            pool_size: Number of connections to maintain in pool
        """
        self.database_path = database_path
        self.pool_size = pool_size
        self.pool: Queue = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Create initial connections and add to pool"""
        # Ensure database directory exists
        db_path = Path(self.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        for _ in range(self.pool_size):
            conn = self._create_connection()
            self.pool.put(conn)
    
    def _create_connection(self) -> sqlite3.Connection:
        """
        Create a new database connection with proper configuration
        
        Returns:
            Configured SQLite connection
        """
        conn = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
            timeout=30.0
        )
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Set row factory for dict-like access
        conn.row_factory = sqlite3.Row
        
        # Performance optimizations
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
        conn.execute("PRAGMA temp_store = MEMORY")
        
        return conn
    
    def get_connection(self, timeout: float = 5.0) -> sqlite3.Connection:
        """
        Get a connection from the pool
        
        Args:
            timeout: Maximum time to wait for available connection
            
        Returns:
            Database connection
            
        Raises:
            Empty: If no connection available within timeout
        """
        try:
            conn = self.pool.get(timeout=timeout)
            # Verify connection is still valid
            try:
                conn.execute("SELECT 1")
                return conn
            except sqlite3.Error:
                # Connection is broken, create new one
                conn.close()
                return self._create_connection()
        except Empty:
            raise RuntimeError(f"No database connection available within {timeout}s")
    
    def return_connection(self, conn: sqlite3.Connection):
        """
        Return a connection to the pool
        
        Args:
            conn: Connection to return
        """
        if conn:
            try:
                # Rollback any uncommitted transactions
                conn.rollback()
                self.pool.put(conn, block=False)
            except Exception:
                # If pool is full or connection is bad, close it
                conn.close()
    
    def close_all(self):
        """Close all connections in the pool"""
        with self.lock:
            while not self.pool.empty():
                try:
                    conn = self.pool.get_nowait()
                    conn.close()
                except Empty:
                    break
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close_all()
