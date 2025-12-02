"""
Memory Manager Module
Provides memory management utilities including cleanup, cache limits, and garbage collection
"""

import gc
import logging
import psutil
import os
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import QTableWidget, QWidget
from PyQt6.QtCore import QTimer


logger = logging.getLogger(__name__)


class MemoryMonitor:
    """Monitor memory usage of the application"""
    
    def __init__(self):
        """Initialize memory monitor"""
        self.process = psutil.Process(os.getpid())
        self.baseline_memory = self.get_current_memory()
    
    def get_current_memory(self) -> float:
        """
        Get current memory usage in MB
        
        Returns:
            Memory usage in megabytes
        """
        try:
            mem_info = self.process.memory_info()
            return mem_info.rss / 1024 / 1024  # Convert to MB
        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return 0.0
    
    def get_memory_percent(self) -> float:
        """
        Get memory usage as percentage of system memory
        
        Returns:
            Memory usage percentage
        """
        try:
            return self.process.memory_percent()
        except Exception as e:
            logger.error(f"Failed to get memory percent: {e}")
            return 0.0
    
    def get_memory_delta(self) -> float:
        """
        Get memory increase since baseline
        
        Returns:
            Memory delta in MB
        """
        return self.get_current_memory() - self.baseline_memory
    
    def reset_baseline(self):
        """Reset baseline memory measurement"""
        self.baseline_memory = self.get_current_memory()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive memory statistics
        
        Returns:
            Dictionary with memory stats
        """
        current = self.get_current_memory()
        return {
            'current_mb': round(current, 2),
            'baseline_mb': round(self.baseline_memory, 2),
            'delta_mb': round(current - self.baseline_memory, 2),
            'percent': round(self.get_memory_percent(), 2),
            'available_mb': round(psutil.virtual_memory().available / 1024 / 1024, 2),
            'total_mb': round(psutil.virtual_memory().total / 1024 / 1024, 2)
        }


class CacheLimitManager:
    """Manage cache size limits across the application"""
    
    def __init__(self, max_cache_size_mb: float = 100.0):
        """
        Initialize cache limit manager
        
        Args:
            max_cache_size_mb: Maximum cache size in megabytes
        """
        self.max_cache_size_mb = max_cache_size_mb
        self.caches: Dict[str, Any] = {}
        self.cache_sizes: Dict[str, float] = {}
    
    def register_cache(self, cache_id: str, cache_obj: Any, estimated_size_mb: float = 0.0):
        """
        Register a cache for monitoring
        
        Args:
            cache_id: Unique identifier for cache
            cache_obj: Cache object (must have clear() method)
            estimated_size_mb: Estimated size in MB
        """
        self.caches[cache_id] = cache_obj
        self.cache_sizes[cache_id] = estimated_size_mb
        logger.debug(f"Registered cache: {cache_id} ({estimated_size_mb:.2f} MB)")
    
    def unregister_cache(self, cache_id: str):
        """
        Unregister a cache
        
        Args:
            cache_id: Cache identifier
        """
        if cache_id in self.caches:
            del self.caches[cache_id]
            del self.cache_sizes[cache_id]
            logger.debug(f"Unregistered cache: {cache_id}")
    
    def get_total_cache_size(self) -> float:
        """
        Get total estimated cache size
        
        Returns:
            Total size in MB
        """
        return sum(self.cache_sizes.values())
    
    def clear_cache(self, cache_id: str):
        """
        Clear a specific cache
        
        Args:
            cache_id: Cache identifier
        """
        if cache_id in self.caches:
            cache = self.caches[cache_id]
            if hasattr(cache, 'clear'):
                cache.clear()
                self.cache_sizes[cache_id] = 0.0
                logger.info(f"Cleared cache: {cache_id}")
    
    def clear_all_caches(self):
        """Clear all registered caches"""
        for cache_id in list(self.caches.keys()):
            self.clear_cache(cache_id)
        logger.info("Cleared all caches")
    
    def enforce_limits(self):
        """Enforce cache size limits by clearing oldest caches"""
        total_size = self.get_total_cache_size()
        
        if total_size > self.max_cache_size_mb:
            logger.warning(f"Cache size ({total_size:.2f} MB) exceeds limit ({self.max_cache_size_mb:.2f} MB)")
            
            # Sort caches by size (largest first)
            sorted_caches = sorted(
                self.cache_sizes.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Clear caches until under limit
            for cache_id, size in sorted_caches:
                if self.get_total_cache_size() <= self.max_cache_size_mb:
                    break
                self.clear_cache(cache_id)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        return {
            'total_caches': len(self.caches),
            'total_size_mb': round(self.get_total_cache_size(), 2),
            'max_size_mb': self.max_cache_size_mb,
            'utilization_percent': round(
                (self.get_total_cache_size() / self.max_cache_size_mb * 100), 2
            ) if self.max_cache_size_mb > 0 else 0,
            'caches': {
                cache_id: round(size, 2)
                for cache_id, size in self.cache_sizes.items()
            }
        }


class TableMemoryOptimizer:
    """Optimize memory usage for QTableWidget"""
    
    @staticmethod
    def clear_table(table: QTableWidget):
        """
        Clear table and free memory
        
        Args:
            table: QTableWidget to clear
        """
        try:
            # Clear selection
            table.clearSelection()
            
            # Clear contents
            table.clearContents()
            
            # Reset row count
            table.setRowCount(0)
            
            logger.debug(f"Cleared table with {table.columnCount()} columns")
        except Exception as e:
            logger.error(f"Failed to clear table: {e}")
    
    @staticmethod
    def optimize_table_memory(table: QTableWidget, max_rows: int = 1000):
        """
        Optimize table memory by limiting rows
        
        Args:
            table: QTableWidget to optimize
            max_rows: Maximum number of rows to keep
        """
        try:
            current_rows = table.rowCount()
            
            if current_rows > max_rows:
                # Remove excess rows from the end
                rows_to_remove = current_rows - max_rows
                for _ in range(rows_to_remove):
                    table.removeRow(table.rowCount() - 1)
                
                logger.info(f"Removed {rows_to_remove} rows from table to optimize memory")
        except Exception as e:
            logger.error(f"Failed to optimize table memory: {e}")
    
    @staticmethod
    def get_table_memory_estimate(table: QTableWidget) -> float:
        """
        Estimate memory usage of table
        
        Args:
            table: QTableWidget to analyze
            
        Returns:
            Estimated memory in MB
        """
        try:
            rows = table.rowCount()
            cols = table.columnCount()
            
            # Rough estimate: 100 bytes per cell
            estimated_bytes = rows * cols * 100
            estimated_mb = estimated_bytes / 1024 / 1024
            
            return estimated_mb
        except Exception as e:
            logger.error(f"Failed to estimate table memory: {e}")
            return 0.0


class GarbageCollectionManager:
    """Manage garbage collection triggers"""
    
    def __init__(self, auto_collect: bool = True, collect_interval_ms: int = 60000):
        """
        Initialize garbage collection manager
        
        Args:
            auto_collect: Whether to automatically trigger GC
            collect_interval_ms: Interval between auto collections in milliseconds
        """
        self.auto_collect = auto_collect
        self.collect_interval_ms = collect_interval_ms
        self.timer: Optional[QTimer] = None
        self.collection_count = 0
        
        if auto_collect:
            self._start_auto_collection()
    
    def _start_auto_collection(self):
        """Start automatic garbage collection timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.collect)
        self.timer.start(self.collect_interval_ms)
        logger.info(f"Started automatic garbage collection (interval: {self.collect_interval_ms}ms)")
    
    def collect(self) -> Dict[str, int]:
        """
        Trigger garbage collection
        
        Returns:
            Dictionary with collection stats
        """
        logger.debug("Triggering garbage collection")
        
        # Get counts before collection
        before_counts = gc.get_count()
        
        # Collect all generations
        collected = {
            'gen0': gc.collect(0),
            'gen1': gc.collect(1),
            'gen2': gc.collect(2)
        }
        
        # Get counts after collection
        after_counts = gc.get_count()
        
        self.collection_count += 1
        
        logger.info(
            f"Garbage collection #{self.collection_count} completed: "
            f"collected {sum(collected.values())} objects"
        )
        
        return {
            'collected': collected,
            'before_counts': before_counts,
            'after_counts': after_counts,
            'total_collected': sum(collected.values())
        }
    
    def stop_auto_collection(self):
        """Stop automatic garbage collection"""
        if self.timer:
            self.timer.stop()
            self.timer = None
            logger.info("Stopped automatic garbage collection")
    
    def get_gc_stats(self) -> Dict[str, Any]:
        """
        Get garbage collection statistics
        
        Returns:
            Dictionary with GC stats
        """
        return {
            'enabled': gc.isenabled(),
            'counts': gc.get_count(),
            'thresholds': gc.get_threshold(),
            'collection_count': self.collection_count,
            'auto_collect': self.auto_collect
        }


class MemoryManager:
    """Main memory manager coordinating all memory management utilities"""
    
    def __init__(
        self,
        max_cache_size_mb: float = 100.0,
        auto_gc: bool = True,
        gc_interval_ms: int = 60000
    ):
        """
        Initialize memory manager
        
        Args:
            max_cache_size_mb: Maximum cache size in MB
            auto_gc: Enable automatic garbage collection
            gc_interval_ms: GC interval in milliseconds
        """
        self.monitor = MemoryMonitor()
        self.cache_manager = CacheLimitManager(max_cache_size_mb)
        self.gc_manager = GarbageCollectionManager(auto_gc, gc_interval_ms)
        self.table_optimizer = TableMemoryOptimizer()
        self.widgets_to_cleanup: List[QWidget] = []
    
    def register_widget_for_cleanup(self, widget: QWidget):
        """
        Register widget for cleanup on close
        
        Args:
            widget: Widget to cleanup
        """
        self.widgets_to_cleanup.append(widget)
    
    def cleanup_widget(self, widget: QWidget):
        """
        Cleanup a widget and free memory
        
        Args:
            widget: Widget to cleanup
        """
        try:
            # If it's a table, clear it
            if isinstance(widget, QTableWidget):
                self.table_optimizer.clear_table(widget)
            
            # Delete later
            widget.deleteLater()
            
            # Remove from tracking
            if widget in self.widgets_to_cleanup:
                self.widgets_to_cleanup.remove(widget)
            
            logger.debug(f"Cleaned up widget: {widget.__class__.__name__}")
        except Exception as e:
            logger.error(f"Failed to cleanup widget: {e}")
    
    def cleanup_all_widgets(self):
        """Cleanup all registered widgets"""
        for widget in list(self.widgets_to_cleanup):
            self.cleanup_widget(widget)
    
    def perform_full_cleanup(self):
        """Perform full memory cleanup"""
        logger.info("Performing full memory cleanup")
        
        # Clear all caches
        self.cache_manager.clear_all_caches()
        
        # Cleanup widgets
        self.cleanup_all_widgets()
        
        # Force garbage collection
        self.gc_manager.collect()
        
        logger.info("Full memory cleanup completed")
    
    def get_memory_report(self) -> Dict[str, Any]:
        """
        Get comprehensive memory report
        
        Returns:
            Dictionary with memory report
        """
        return {
            'memory': self.monitor.get_memory_stats(),
            'cache': self.cache_manager.get_cache_stats(),
            'gc': self.gc_manager.get_gc_stats()
        }
    
    def check_memory_health(self) -> Dict[str, Any]:
        """
        Check memory health and return recommendations
        
        Returns:
            Dictionary with health status and recommendations
        """
        memory_stats = self.monitor.get_memory_stats()
        cache_stats = self.cache_manager.get_cache_stats()
        
        health = {
            'status': 'healthy',
            'warnings': [],
            'recommendations': []
        }
        
        # Check memory usage
        if memory_stats['percent'] > 80:
            health['status'] = 'critical'
            health['warnings'].append(f"High memory usage: {memory_stats['percent']:.1f}%")
            health['recommendations'].append("Consider clearing caches or restarting application")
        elif memory_stats['percent'] > 60:
            health['status'] = 'warning'
            health['warnings'].append(f"Elevated memory usage: {memory_stats['percent']:.1f}%")
            health['recommendations'].append("Monitor memory usage closely")
        
        # Check cache usage
        if cache_stats['utilization_percent'] > 90:
            health['warnings'].append(f"Cache nearly full: {cache_stats['utilization_percent']:.1f}%")
            health['recommendations'].append("Clear some caches to free memory")
        
        # Check memory delta
        if memory_stats['delta_mb'] > 500:
            health['warnings'].append(f"Large memory increase: {memory_stats['delta_mb']:.1f} MB")
            health['recommendations'].append("Check for memory leaks")
        
        return health
    
    def shutdown(self):
        """Shutdown memory manager and cleanup"""
        logger.info("Shutting down memory manager")
        
        # Stop auto GC
        self.gc_manager.stop_auto_collection()
        
        # Perform final cleanup
        self.perform_full_cleanup()


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager(
    max_cache_size_mb: float = 100.0,
    auto_gc: bool = True,
    gc_interval_ms: int = 60000
) -> MemoryManager:
    """Get or create global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(max_cache_size_mb, auto_gc, gc_interval_ms)
    return _memory_manager


def reset_memory_manager():
    """Reset global memory manager instance"""
    global _memory_manager
    if _memory_manager:
        _memory_manager.shutdown()
    _memory_manager = None
