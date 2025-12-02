"""
Migration Runner for Database Schema Management
Handles database version tracking and migration execution
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class Migration:
    """Represents a single database migration"""
    
    def __init__(self, version: int, name: str, up_sql: str, down_sql: str = ""):
        """
        Initialize migration
        
        Args:
            version: Migration version number
            name: Migration name/description
            up_sql: SQL to apply migration
            down_sql: SQL to rollback migration
        """
        self.version = version
        self.name = name
        self.up_sql = up_sql
        self.down_sql = down_sql
    
    def __repr__(self):
        return f"Migration(version={self.version}, name='{self.name}')"


class MigrationRunner:
    """Manages database migrations and version tracking"""
    
    def __init__(self, database_path: str):
        """
        Initialize migration runner
        
        Args:
            database_path: Path to SQLite database
        """
        self.database_path = database_path
        self.migrations: List[Migration] = []
        self._ensure_migrations_table()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _ensure_migrations_table(self):
        """Create migrations tracking table if not exists"""
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("Migrations table ensured")
        except sqlite3.Error as e:
            logger.error(f"Failed to create migrations table: {e}")
            raise
        finally:
            conn.close()
    
    def register_migration(self, migration: Migration):
        """
        Register a migration
        
        Args:
            migration: Migration to register
        """
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
    
    def get_current_version(self) -> int:
        """
        Get current database version
        
        Returns:
            Current version number (0 if no migrations applied)
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT MAX(version) as version FROM schema_migrations"
            )
            result = cursor.fetchone()
            version = result['version'] if result['version'] is not None else 0
            return version
        except sqlite3.Error as e:
            logger.error(f"Failed to get current version: {e}")
            return 0
        finally:
            conn.close()
    
    def get_applied_migrations(self) -> List[Dict]:
        """
        Get list of applied migrations
        
        Returns:
            List of applied migration records
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT version, name, applied_at FROM schema_migrations ORDER BY version"
            )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
        finally:
            conn.close()
    
    def get_pending_migrations(self) -> List[Migration]:
        """
        Get list of pending migrations
        
        Returns:
            List of migrations not yet applied
        """
        current_version = self.get_current_version()
        return [m for m in self.migrations if m.version > current_version]
    
    def migrate_up(self, target_version: Optional[int] = None) -> bool:
        """
        Apply pending migrations up to target version
        
        Args:
            target_version: Target version (None = apply all)
            
        Returns:
            True if successful, False otherwise
        """
        current_version = self.get_current_version()
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("No pending migrations")
            return True
        
        if target_version:
            pending = [m for m in pending if m.version <= target_version]
        
        logger.info(f"Applying {len(pending)} migration(s) from version {current_version}")
        
        for migration in pending:
            if not self._apply_migration(migration):
                logger.error(f"Migration {migration.version} failed, stopping")
                return False
        
        logger.info(f"Successfully migrated to version {self.get_current_version()}")
        return True
    
    def _apply_migration(self, migration: Migration) -> bool:
        """
        Apply a single migration
        
        Args:
            migration: Migration to apply
            
        Returns:
            True if successful, False otherwise
        """
        conn = self._get_connection()
        try:
            logger.info(f"Applying migration {migration.version}: {migration.name}")
            
            # Execute migration SQL
            conn.executescript(migration.up_sql)
            
            # Record migration
            conn.execute(
                "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                (migration.version, migration.name)
            )
            
            conn.commit()
            logger.info(f"Migration {migration.version} applied successfully")
            return True
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Failed to apply migration {migration.version}: {e}")
            return False
        finally:
            conn.close()
    
    def migrate_down(self, target_version: int) -> bool:
        """
        Rollback migrations to target version
        
        Args:
            target_version: Target version to rollback to
            
        Returns:
            True if successful, False otherwise
        """
        current_version = self.get_current_version()
        
        if target_version >= current_version:
            logger.info("Target version is current or higher, nothing to rollback")
            return True
        
        # Get migrations to rollback (in reverse order)
        to_rollback = [
            m for m in reversed(self.migrations)
            if target_version < m.version <= current_version
        ]
        
        if not to_rollback:
            logger.warning("No migrations found to rollback")
            return False
        
        logger.info(f"Rolling back {len(to_rollback)} migration(s) to version {target_version}")
        
        for migration in to_rollback:
            if not self._rollback_migration(migration):
                logger.error(f"Rollback of migration {migration.version} failed, stopping")
                return False
        
        logger.info(f"Successfully rolled back to version {self.get_current_version()}")
        return True
    
    def _rollback_migration(self, migration: Migration) -> bool:
        """
        Rollback a single migration
        
        Args:
            migration: Migration to rollback
            
        Returns:
            True if successful, False otherwise
        """
        if not migration.down_sql:
            logger.error(f"Migration {migration.version} has no rollback SQL")
            return False
        
        conn = self._get_connection()
        try:
            logger.info(f"Rolling back migration {migration.version}: {migration.name}")
            
            # Execute rollback SQL
            conn.executescript(migration.down_sql)
            
            # Remove migration record
            conn.execute(
                "DELETE FROM schema_migrations WHERE version = ?",
                (migration.version,)
            )
            
            conn.commit()
            logger.info(f"Migration {migration.version} rolled back successfully")
            return True
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Failed to rollback migration {migration.version}: {e}")
            return False
        finally:
            conn.close()
    
    def get_migration_status(self) -> Dict:
        """
        Get migration status summary
        
        Returns:
            Dictionary with migration status information
        """
        current_version = self.get_current_version()
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        return {
            'current_version': current_version,
            'total_migrations': len(self.migrations),
            'applied_count': len(applied),
            'pending_count': len(pending),
            'applied_migrations': applied,
            'pending_migrations': [
                {'version': m.version, 'name': m.name}
                for m in pending
            ]
        }
    
    def load_migrations_from_directory(self, migrations_dir: str):
        """
        Load migration files from directory
        
        Args:
            migrations_dir: Path to migrations directory
        """
        migrations_path = Path(migrations_dir)
        
        if not migrations_path.exists():
            logger.warning(f"Migrations directory not found: {migrations_dir}")
            return
        
        # Look for migration files (format: V001__migration_name.sql)
        for sql_file in sorted(migrations_path.glob("V*.sql")):
            try:
                # Parse version from filename
                filename = sql_file.stem
                parts = filename.split("__", 1)
                
                if len(parts) != 2:
                    logger.warning(f"Invalid migration filename format: {sql_file.name}")
                    continue
                
                version_str = parts[0][1:]  # Remove 'V' prefix
                version = int(version_str)
                name = parts[1].replace("_", " ")
                
                # Read SQL content
                with open(sql_file, 'r', encoding='utf-8') as f:
                    up_sql = f.read()
                
                # Look for corresponding down migration
                down_file = migrations_path / f"V{version_str}__down__{parts[1]}.sql"
                down_sql = ""
                if down_file.exists():
                    with open(down_file, 'r', encoding='utf-8') as f:
                        down_sql = f.read()
                
                migration = Migration(version, name, up_sql, down_sql)
                self.register_migration(migration)
                logger.debug(f"Loaded migration: {migration}")
                
            except Exception as e:
                logger.error(f"Failed to load migration {sql_file.name}: {e}")
        
        logger.info(f"Loaded {len(self.migrations)} migration(s) from {migrations_dir}")
