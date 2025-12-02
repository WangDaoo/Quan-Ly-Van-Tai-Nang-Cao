"""
UI Optimizer Module
Provides background threading, lazy loading, virtual scrolling, and debouncing for UI operations
"""

import logging
from typing import Callable, Any, Optional, List
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QObject
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
import time


logger = logging.getLogger(__name__)


class BackgroundWorker(QThread):
    """Background worker thread for database operations"""
    
    # Signals
    finished = pyqtSignal(object)  # Emits result when done
    error = pyqtSignal(Exception)  # Emits exception if error occurs
    progress = pyqtSignal(int)  # Emits progress percentage (0-100)
    
    def __init__(self, func: Callable, *args, **kwargs):
        """
        Initialize background worker
        
        Args:
            func: Function to execute in background
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
        """
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self._is_cancelled = False
    
    def run(self):
        """Execute function in background thread"""
        try:
            logger.debug(f"Starting background task: {self.func.__name__}")
            start_time = time.time()
            
            self.result = self.func(*self.args, **self.kwargs)
            
            execution_time = time.time() - start_time
            logger.debug(f"Background task completed in {execution_time:.2f}s: {self.func.__name__}")
            
            if not self._is_cancelled:
                self.finished.emit(self.result)
        except Exception as e:
            logger.error(f"Background task failed: {self.func.__name__}", exc_info=True)
            if not self._is_cancelled:
                self.error.emit(e)
    
    def cancel(self):
        """Cancel the background task"""
        self._is_cancelled = True
        logger.debug(f"Background task cancelled: {self.func.__name__}")


class BackgroundTaskManager:
    """Manages multiple background tasks"""
    
    def __init__(self):
        """Initialize task manager"""
        self.active_tasks: List[BackgroundWorker] = []
    
    def run_task(
        self,
        func: Callable,
        on_finished: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> BackgroundWorker:
        """
        Run a function in background thread
        
        Args:
            func: Function to execute
            on_finished: Callback when task finishes
            on_error: Callback when task errors
            *args: Arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            BackgroundWorker instance
        """
        worker = BackgroundWorker(func, *args, **kwargs)
        
        if on_finished:
            worker.finished.connect(on_finished)
        
        if on_error:
            worker.error.connect(on_error)
        
        # Clean up when finished
        worker.finished.connect(lambda: self._cleanup_task(worker))
        worker.error.connect(lambda: self._cleanup_task(worker))
        
        self.active_tasks.append(worker)
        worker.start()
        
        return worker
    
    def _cleanup_task(self, worker: BackgroundWorker):
        """Remove completed task from active list"""
        if worker in self.active_tasks:
            self.active_tasks.remove(worker)
    
    def cancel_all(self):
        """Cancel all active tasks"""
        for task in self.active_tasks:
            task.cancel()
            task.wait()
        self.active_tasks.clear()
    
    def get_active_count(self) -> int:
        """Get number of active tasks"""
        return len(self.active_tasks)


class DebouncedAction(QObject):
    """Debounced action that delays execution until user stops typing/interacting"""
    
    triggered = pyqtSignal()
    
    def __init__(self, delay_ms: int = 300, parent: Optional[QObject] = None):
        """
        Initialize debounced action
        
        Args:
            delay_ms: Delay in milliseconds before triggering
            parent: Parent QObject
        """
        super().__init__(parent)
        self.delay_ms = delay_ms
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.triggered.emit)
    
    def trigger(self):
        """Trigger the action (will be delayed)"""
        self.timer.stop()
        self.timer.start(self.delay_ms)
    
    def cancel(self):
        """Cancel pending action"""
        self.timer.stop()
    
    def is_active(self) -> bool:
        """Check if action is pending"""
        return self.timer.isActive()


class LazyLoader:
    """Lazy loading utility for autocomplete and large datasets"""
    
    def __init__(self, load_func: Callable, batch_size: int = 20):
        """
        Initialize lazy loader
        
        Args:
            load_func: Function to load data
            batch_size: Number of items to load per batch
        """
        self.load_func = load_func
        self.batch_size = batch_size
        self.cache: List[Any] = []
        self.is_fully_loaded = False
        self.current_offset = 0
    
    def load_next_batch(self) -> List[Any]:
        """
        Load next batch of data
        
        Returns:
            List of loaded items
        """
        if self.is_fully_loaded:
            return []
        
        try:
            batch = self.load_func(limit=self.batch_size, offset=self.current_offset)
            
            if not batch or len(batch) < self.batch_size:
                self.is_fully_loaded = True
            
            self.cache.extend(batch)
            self.current_offset += len(batch)
            
            return batch
        except Exception as e:
            logger.error(f"Failed to load batch: {e}")
            return []
    
    def get_cached_data(self) -> List[Any]:
        """Get all cached data"""
        return self.cache
    
    def reset(self):
        """Reset loader state"""
        self.cache.clear()
        self.is_fully_loaded = False
        self.current_offset = 0
    
    def search(self, query: str, field: str = None) -> List[Any]:
        """
        Search in cached data
        
        Args:
            query: Search query
            field: Field to search in (if dict items)
            
        Returns:
            Matching items
        """
        query_lower = query.lower()
        results = []
        
        for item in self.cache:
            if isinstance(item, dict) and field:
                if field in item and query_lower in str(item[field]).lower():
                    results.append(item)
            elif isinstance(item, str):
                if query_lower in item.lower():
                    results.append(item)
        
        return results


class VirtualScrollHelper:
    """Helper for implementing virtual scrolling in tables"""
    
    def __init__(
        self,
        table: QTableWidget,
        total_rows: int,
        load_func: Callable,
        visible_rows: int = 50
    ):
        """
        Initialize virtual scroll helper
        
        Args:
            table: QTableWidget to optimize
            total_rows: Total number of rows in dataset
            load_func: Function to load data for specific range
            visible_rows: Number of rows to keep in memory
        """
        self.table = table
        self.total_rows = total_rows
        self.load_func = load_func
        self.visible_rows = visible_rows
        self.current_offset = 0
        self.cache: dict = {}
    
    def load_visible_range(self, start_row: int, end_row: int):
        """
        Load data for visible range
        
        Args:
            start_row: Start row index
            end_row: End row index
        """
        # Calculate which rows need to be loaded
        rows_to_load = []
        for row in range(start_row, min(end_row, self.total_rows)):
            if row not in self.cache:
                rows_to_load.append(row)
        
        if not rows_to_load:
            return
        
        # Load data
        try:
            data = self.load_func(
                limit=len(rows_to_load),
                offset=min(rows_to_load)
            )
            
            # Cache loaded data
            for i, row_data in enumerate(data):
                row_index = min(rows_to_load) + i
                self.cache[row_index] = row_data
            
            # Update table
            self._update_table_rows(start_row, end_row)
        except Exception as e:
            logger.error(f"Failed to load visible range: {e}")
    
    def _update_table_rows(self, start_row: int, end_row: int):
        """Update table with cached data"""
        for row in range(start_row, min(end_row, self.total_rows)):
            if row in self.cache:
                row_data = self.cache[row]
                # Update table cells with row_data
                # This is a placeholder - actual implementation depends on table structure
                pass
    
    def clear_cache(self):
        """Clear cached data"""
        self.cache.clear()
    
    def get_cache_size(self) -> int:
        """Get number of cached rows"""
        return len(self.cache)


class UIOptimizer:
    """Main UI optimizer with all optimization utilities"""
    
    def __init__(self):
        """Initialize UI optimizer"""
        self.task_manager = BackgroundTaskManager()
        self.debounced_actions: dict = {}
    
    def run_in_background(
        self,
        func: Callable,
        on_finished: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> BackgroundWorker:
        """
        Run function in background thread
        
        Args:
            func: Function to execute
            on_finished: Callback when finished
            on_error: Callback on error
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            BackgroundWorker instance
        """
        return self.task_manager.run_task(func, on_finished, on_error, *args, **kwargs)
    
    def create_debounced_action(
        self,
        action_id: str,
        callback: Callable,
        delay_ms: int = 300
    ) -> DebouncedAction:
        """
        Create a debounced action
        
        Args:
            action_id: Unique identifier for action
            callback: Function to call when triggered
            delay_ms: Delay in milliseconds
            
        Returns:
            DebouncedAction instance
        """
        if action_id in self.debounced_actions:
            return self.debounced_actions[action_id]
        
        action = DebouncedAction(delay_ms)
        action.triggered.connect(callback)
        self.debounced_actions[action_id] = action
        
        return action
    
    def create_lazy_loader(
        self,
        load_func: Callable,
        batch_size: int = 20
    ) -> LazyLoader:
        """
        Create a lazy loader
        
        Args:
            load_func: Function to load data
            batch_size: Batch size
            
        Returns:
            LazyLoader instance
        """
        return LazyLoader(load_func, batch_size)
    
    def create_virtual_scroll(
        self,
        table: QTableWidget,
        total_rows: int,
        load_func: Callable,
        visible_rows: int = 50
    ) -> VirtualScrollHelper:
        """
        Create virtual scroll helper
        
        Args:
            table: Table widget
            total_rows: Total rows
            load_func: Data loading function
            visible_rows: Visible rows count
            
        Returns:
            VirtualScrollHelper instance
        """
        return VirtualScrollHelper(table, total_rows, load_func, visible_rows)
    
    def cleanup(self):
        """Cleanup all resources"""
        self.task_manager.cancel_all()
        for action in self.debounced_actions.values():
            action.cancel()
        self.debounced_actions.clear()


# Global UI optimizer instance
_ui_optimizer: Optional[UIOptimizer] = None


def get_ui_optimizer() -> UIOptimizer:
    """Get or create global UI optimizer instance"""
    global _ui_optimizer
    if _ui_optimizer is None:
        _ui_optimizer = UIOptimizer()
    return _ui_optimizer


def reset_ui_optimizer():
    """Reset global UI optimizer instance"""
    global _ui_optimizer
    if _ui_optimizer:
        _ui_optimizer.cleanup()
    _ui_optimizer = None
