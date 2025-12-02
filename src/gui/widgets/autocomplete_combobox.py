"""
Autocomplete ComboBox Widget
Provides intelligent autocomplete with fuzzy search, debouncing, caching, and keyboard navigation
"""

from PyQt6.QtWidgets import QComboBox, QCompleter, QLineEdit
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSortFilterProxyModel, QStringListModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from typing import List, Callable, Optional
import logging


logger = logging.getLogger(__name__)


class FuzzyFilterProxyModel(QSortFilterProxyModel):
    """
    Proxy model that implements fuzzy search filtering
    Matches items that contain all characters from the filter in order
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    
    def filterAcceptsRow(self, source_row: int, source_parent) -> bool:
        """
        Custom filter that implements fuzzy matching
        
        Args:
            source_row: Row index in source model
            source_parent: Parent index
        
        Returns:
            True if row matches filter pattern
        """
        if not self.filterRegularExpression().pattern():
            return True
        
        # Get the text from the source model
        index = self.sourceModel().index(source_row, 0, source_parent)
        text = self.sourceModel().data(index, Qt.ItemDataRole.DisplayRole)
        
        if not text:
            return False
        
        # Implement fuzzy search: check if all filter characters appear in order
        filter_text = self.filterRegularExpression().pattern().lower()
        text_lower = text.lower()
        
        # Simple fuzzy match: all characters must appear in order
        text_pos = 0
        for char in filter_text:
            text_pos = text_lower.find(char, text_pos)
            if text_pos == -1:
                return False
            text_pos += 1
        
        return True


class AutocompleteComboBox(QComboBox):
    """
    Enhanced ComboBox with autocomplete features:
    - Fuzzy search in dropdown
    - Keyboard navigation (Arrow keys, Enter, Escape)
    - Debounced search (300ms)
    - Caching for autocomplete data
    - Dynamic data loading from callback
    
    Signals:
        textChanged: Emitted when text changes
        itemSelected: Emitted when an item is selected from dropdown
    """
    
    textChanged = pyqtSignal(str)
    itemSelected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuration
        self._debounce_delay = 300  # milliseconds
        self._cache_enabled = True
        self._cached_items: List[str] = []
        self._data_loader: Optional[Callable[[], List[str]]] = None
        
        # Setup editable combobox
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        # Setup completer with fuzzy search
        self._setup_completer()
        
        # Setup debounce timer
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._on_debounce_timeout)
        
        # Connect signals
        self.lineEdit().textEdited.connect(self._on_text_edited)
        self.activated.connect(self._on_item_activated)
        
        # Track if we're programmatically setting text
        self._programmatic_change = False
        
        logger.debug("AutocompleteComboBox initialized")
    
    def _setup_completer(self):
        """Setup the completer with fuzzy search capability"""
        # Create completer
        self._completer = QCompleter(self)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setMaxVisibleItems(10)
        
        # Create model for completer
        self._string_model = QStringListModel()
        
        # Create fuzzy filter proxy model
        self._proxy_model = FuzzyFilterProxyModel()
        self._proxy_model.setSourceModel(self._string_model)
        
        # Set proxy model to completer
        self._completer.setModel(self._proxy_model)
        
        # Set completer to line edit
        self.setCompleter(self._completer)
        
        # Connect completer signals
        self._completer.activated.connect(self._on_completion_selected)
    
    def _on_text_edited(self, text: str):
        """
        Handle text edited event with debouncing
        
        Args:
            text: Current text in the line edit
        """
        if self._programmatic_change:
            return
        
        # Restart debounce timer
        self._debounce_timer.stop()
        self._debounce_timer.start(self._debounce_delay)
        
        # Update filter immediately for responsive UI
        self._update_filter(text)
    
    def _on_debounce_timeout(self):
        """Handle debounce timeout - emit signal after delay"""
        text = self.currentText()
        self.textChanged.emit(text)
        logger.debug(f"Debounced text change: {text}")
    
    def _update_filter(self, text: str):
        """
        Update the filter for fuzzy search
        
        Args:
            text: Filter text
        """
        # Update proxy model filter
        self._proxy_model.setFilterFixedString(text)
        
        # Show popup if there are matches and text is not empty
        if text and self._proxy_model.rowCount() > 0:
            self._completer.complete()
    
    def _on_completion_selected(self, text: str):
        """
        Handle completion selection from dropdown
        
        Args:
            text: Selected text
        """
        self._programmatic_change = True
        self.setCurrentText(text)
        self._programmatic_change = False
        
        self.itemSelected.emit(text)
        logger.debug(f"Item selected: {text}")
    
    def _on_item_activated(self, index: int):
        """
        Handle item activation (Enter key or click)
        
        Args:
            index: Index of activated item
        """
        text = self.itemText(index)
        self.itemSelected.emit(text)
        logger.debug(f"Item activated: {text}")
    
    def set_items(self, items: List[str]):
        """
        Set the list of items for autocomplete
        
        Args:
            items: List of strings to show in autocomplete
        """
        # Update cache
        if self._cache_enabled:
            self._cached_items = items.copy()
        
        # Update models
        self._string_model.setStringList(items)
        
        # Also update combobox items for dropdown
        self.clear()
        self.addItems(items)
        
        logger.debug(f"Set {len(items)} items for autocomplete")
    
    def set_data_loader(self, loader: Callable[[], List[str]]):
        """
        Set a callback function to load data dynamically
        
        Args:
            loader: Callable that returns list of strings
        """
        self._data_loader = loader
        logger.debug("Data loader callback set")
    
    def load_data(self):
        """Load data using the data loader callback"""
        if self._data_loader:
            try:
                # Check cache first
                if self._cache_enabled and self._cached_items:
                    logger.debug("Using cached data")
                    return
                
                # Load data from callback
                items = self._data_loader()
                self.set_items(items)
                logger.info(f"Loaded {len(items)} items from data loader")
                
            except Exception as e:
                logger.error(f"Error loading data: {e}")
    
    def clear_cache(self):
        """Clear the cached items"""
        self._cached_items = []
        logger.debug("Cache cleared")
    
    def set_debounce_delay(self, delay_ms: int):
        """
        Set the debounce delay in milliseconds
        
        Args:
            delay_ms: Delay in milliseconds (default: 300)
        """
        self._debounce_delay = delay_ms
        logger.debug(f"Debounce delay set to {delay_ms}ms")
    
    def set_cache_enabled(self, enabled: bool):
        """
        Enable or disable caching
        
        Args:
            enabled: True to enable caching, False to disable
        """
        self._cache_enabled = enabled
        if not enabled:
            self.clear_cache()
        logger.debug(f"Cache {'enabled' if enabled else 'disabled'}")
    
    def get_cached_items(self) -> List[str]:
        """
        Get the cached items
        
        Returns:
            List of cached items
        """
        return self._cached_items.copy()
    
    def keyPressEvent(self, event):
        """
        Handle keyboard events for navigation
        
        Supported keys:
        - Arrow Up/Down: Navigate through items
        - Enter/Return: Select current item
        - Escape: Close dropdown and clear selection
        """
        key = event.key()
        
        if key == Qt.Key.Key_Escape:
            # Close dropdown and clear
            self.hidePopup()
            self._completer.popup().hide()
            event.accept()
            
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Select current item
            if self._completer.popup().isVisible():
                # Let completer handle it
                super().keyPressEvent(event)
            else:
                # Emit signal for current text
                self.itemSelected.emit(self.currentText())
                event.accept()
        
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            # Navigate through items
            if not self._completer.popup().isVisible() and self.count() > 0:
                self.showPopup()
            super().keyPressEvent(event)
        
        else:
            # Default handling
            super().keyPressEvent(event)
    
    def showPopup(self):
        """Override to load data before showing popup"""
        # Load data if not cached
        if self._cache_enabled and not self._cached_items:
            self.load_data()
        
        super().showPopup()
    
    def focusInEvent(self, event):
        """Handle focus in event - load data if needed"""
        # Load data when widget receives focus
        if self._cache_enabled and not self._cached_items:
            self.load_data()
        
        super().focusInEvent(event)
