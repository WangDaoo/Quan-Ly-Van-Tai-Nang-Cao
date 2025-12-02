"""
Excel Header View - Custom header with column resizing, reordering, freezing, and filtering
"""

from PyQt6.QtWidgets import QHeaderView, QPushButton, QMenu
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QIcon
from typing import Optional, Set


class ExcelHeaderView(QHeaderView):
    """
    Custom header view with Excel-like features:
    - Column resizing
    - Drag & drop column reordering
    - Column freezing
    - Filter button per column
    """
    
    # Signals
    filterClicked = pyqtSignal(int)  # Emitted when filter button clicked for a column
    columnFrozen = pyqtSignal(int)   # Emitted when a column is frozen
    columnUnfrozen = pyqtSignal(int) # Emitted when a column is unfrozen
    
    def __init__(self, orientation: Qt.Orientation, parent=None):
        super().__init__(orientation, parent)
        
        # Enable features
        self.setSectionsMovable(True)  # Drag & drop reordering
        self.setSectionsClickable(True)
        self.setHighlightSections(True)
        self.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # Column resizing
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Frozen columns tracking
        self._frozen_columns: Set[int] = set()
        
        # Filter buttons state
        self._filter_enabled = True
        self._filter_active_columns: Set[int] = set()
        
        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Connect signals
        self.sectionClicked.connect(self._handle_section_clicked)
        
    def paintSection(self, painter: QPainter, rect, logicalIndex: int):
        """
        Custom paint to add filter button and frozen indicator
        """
        painter.save()
        
        # Draw default header background
        super().paintSection(painter, rect, logicalIndex)
        
        # Draw frozen indicator
        if logicalIndex in self._frozen_columns:
            painter.fillRect(rect, QColor(230, 240, 255, 100))  # Light blue tint
            
        # Draw filter button if enabled
        if self._filter_enabled and self.orientation() == Qt.Orientation.Horizontal:
            button_size = 16
            button_margin = 4
            button_rect = rect.adjusted(
                rect.width() - button_size - button_margin,
                (rect.height() - button_size) // 2,
                -button_margin,
                -(rect.height() - button_size) // 2
            )
            
            # Draw filter icon
            if logicalIndex in self._filter_active_columns:
                painter.fillRect(button_rect, QColor(100, 150, 255))  # Active filter color
            else:
                painter.fillRect(button_rect, QColor(200, 200, 200))  # Inactive filter color
                
            # Draw simple triangle icon
            painter.setPen(QColor(255, 255, 255))
            center_x = button_rect.center().x()
            center_y = button_rect.center().y()
            points = [
                QPoint(center_x, center_y + 3),
                QPoint(center_x - 3, center_y - 3),
                QPoint(center_x + 3, center_y - 3)
            ]
            painter.drawPolygon(points)
        
        painter.restore()
        
    def _handle_section_clicked(self, logicalIndex: int):
        """
        Handle section click - check if filter button was clicked
        """
        if not self._filter_enabled:
            return
            
        # Get the position of the click
        pos = self.mapFromGlobal(self.cursor().pos())
        section_rect = self.sectionViewportPosition(logicalIndex)
        section_width = self.sectionSize(logicalIndex)
        
        # Check if click was in the filter button area (right side)
        button_size = 16
        button_margin = 4
        button_x_start = section_rect + section_width - button_size - button_margin
        
        if pos.x() >= button_x_start:
            # Filter button clicked
            self.filterClicked.emit(logicalIndex)
            
    def _show_context_menu(self, pos: QPoint):
        """
        Show context menu for column operations
        """
        logical_index = self.logicalIndexAt(pos)
        if logical_index < 0:
            return
            
        menu = QMenu(self)
        
        # Freeze/Unfreeze action
        if logical_index in self._frozen_columns:
            unfreeze_action = menu.addAction("Unfreeze Column")
            unfreeze_action.triggered.connect(lambda: self.unfreezeColumn(logical_index))
        else:
            freeze_action = menu.addAction("Freeze Column")
            freeze_action.triggered.connect(lambda: self.freezeColumn(logical_index))
            
        menu.addSeparator()
        
        # Auto-resize action
        auto_resize_action = menu.addAction("Auto-Resize Column")
        auto_resize_action.triggered.connect(lambda: self.resizeSection(logical_index, self.sectionSizeHint(logical_index)))
        
        # Auto-resize all action
        auto_resize_all_action = menu.addAction("Auto-Resize All Columns")
        auto_resize_all_action.triggered.connect(self.resizeSections)
        
        menu.addSeparator()
        
        # Hide column action
        hide_action = menu.addAction("Hide Column")
        hide_action.triggered.connect(lambda: self.hideSection(logical_index))
        
        menu.exec(self.mapToGlobal(pos))
        
    def freezeColumn(self, logicalIndex: int):
        """
        Freeze a column (visual indicator, actual freezing handled by parent table)
        """
        self._frozen_columns.add(logicalIndex)
        self.viewport().update()
        self.columnFrozen.emit(logicalIndex)
        
    def unfreezeColumn(self, logicalIndex: int):
        """
        Unfreeze a column
        """
        self._frozen_columns.discard(logicalIndex)
        self.viewport().update()
        self.columnUnfrozen.emit(logicalIndex)
        
    def isFrozen(self, logicalIndex: int) -> bool:
        """
        Check if a column is frozen
        """
        return logicalIndex in self._frozen_columns
        
    def getFrozenColumns(self) -> Set[int]:
        """
        Get all frozen columns
        """
        return self._frozen_columns.copy()
        
    def setFilterEnabled(self, enabled: bool):
        """
        Enable or disable filter buttons
        """
        self._filter_enabled = enabled
        self.viewport().update()
        
    def setFilterActive(self, logicalIndex: int, active: bool):
        """
        Mark a column filter as active or inactive
        """
        if active:
            self._filter_active_columns.add(logicalIndex)
        else:
            self._filter_active_columns.discard(logicalIndex)
        self.viewport().update()
        
    def isFilterActive(self, logicalIndex: int) -> bool:
        """
        Check if a column has an active filter
        """
        return logicalIndex in self._filter_active_columns
        
    def clearAllFilters(self):
        """
        Clear all active filters
        """
        self._filter_active_columns.clear()
        self.viewport().update()
