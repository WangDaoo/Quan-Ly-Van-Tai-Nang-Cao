"""
Autocomplete Integration Module
Provides utilities to integrate autocomplete widgets with forms and database
"""

import logging
from typing import Dict, Optional
from PyQt6.QtWidgets import QWidget

from .autocomplete_combobox import AutocompleteComboBox
from .field_widgets import ComboboxWidget, BaseFieldWidget
from src.services.autocomplete_service import AutocompleteService


logger = logging.getLogger(__name__)


class AutocompleteIntegration:
    """
    Helper class to integrate autocomplete functionality into forms
    Replaces standard ComboBox widgets with AutocompleteComboBox for specific fields
    """
    
    # Field mappings for autocomplete
    AUTOCOMPLETE_FIELDS = {
        'khach_hang': 'customer',
        'khách hàng': 'customer',
        'customer': 'customer',
        'diem_di': 'diem_di',
        'điểm đi': 'diem_di',
        'departure': 'diem_di',
        'diem_den': 'diem_den',
        'điểm đến': 'diem_den',
        'destination': 'diem_den',
    }
    
    def __init__(self, autocomplete_service: AutocompleteService):
        """
        Initialize Autocomplete Integration
        
        Args:
            autocomplete_service: AutocompleteService instance
        """
        self.autocomplete_service = autocomplete_service
        self._autocomplete_widgets: Dict[str, AutocompleteComboBox] = {}
    
    def setup_autocomplete_for_field(self, field_name: str, 
                                     widget: BaseFieldWidget) -> Optional[AutocompleteComboBox]:
        """
        Setup autocomplete for a specific field widget
        
        Args:
            field_name: Name of the field
            widget: The widget to enhance with autocomplete
        
        Returns:
            AutocompleteComboBox if created, None otherwise
        """
        # Normalize field name
        field_name_lower = field_name.lower().strip()
        
        # Check if this field should have autocomplete
        if field_name_lower not in self.AUTOCOMPLETE_FIELDS:
            return None
        
        # Get field type for data loading
        field_type = self.AUTOCOMPLETE_FIELDS[field_name_lower]
        
        # Check if widget is a ComboboxWidget
        if not isinstance(widget, ComboboxWidget):
            logger.debug(f"Field {field_name} is not a ComboboxWidget, skipping autocomplete")
            return None
        
        # Get the internal QComboBox
        if not hasattr(widget, '_input_widget'):
            logger.warning(f"Widget for {field_name} doesn't have _input_widget")
            return None
        
        internal_combobox = widget._input_widget
        
        # Replace with AutocompleteComboBox
        autocomplete_widget = AutocompleteComboBox(internal_combobox.parent())
        
        # Copy properties from original combobox
        autocomplete_widget.setEditable(internal_combobox.isEditable())
        
        # Setup data loader
        data_loader = self.autocomplete_service.create_data_loader(field_type)
        autocomplete_widget.set_data_loader(data_loader)
        
        # Set debounce delay (300ms as per requirements)
        autocomplete_widget.set_debounce_delay(300)
        
        # Enable caching
        autocomplete_widget.set_cache_enabled(True)
        
        # Store reference
        self._autocomplete_widgets[field_name] = autocomplete_widget
        
        logger.info(f"Setup autocomplete for field: {field_name} (type: {field_type})")
        
        return autocomplete_widget
    
    def replace_widget_in_form(self, field_name: str, 
                               old_widget: BaseFieldWidget,
                               new_widget: AutocompleteComboBox,
                               parent_layout) -> bool:
        """
        Replace a widget in a form layout with autocomplete widget
        
        Args:
            field_name: Name of the field
            old_widget: Original widget to replace
            new_widget: New autocomplete widget
            parent_layout: Parent layout containing the widget
        
        Returns:
            True if replacement successful
        """
        try:
            # Find the widget in the layout
            for i in range(parent_layout.count()):
                item = parent_layout.itemAt(i)
                if item and item.widget() == old_widget:
                    # Remove old widget
                    parent_layout.removeWidget(old_widget)
                    old_widget.setParent(None)
                    
                    # Insert new widget at same position
                    parent_layout.insertWidget(i, new_widget)
                    
                    # Connect signals
                    new_widget.textChanged.connect(old_widget.valueChanged.emit)
                    new_widget.itemSelected.connect(old_widget.valueChanged.emit)
                    
                    logger.info(f"Replaced widget for field: {field_name}")
                    return True
            
            logger.warning(f"Could not find widget for field {field_name} in layout")
            return False
            
        except Exception as e:
            logger.error(f"Error replacing widget for {field_name}: {e}")
            return False
    
    def integrate_with_form_builder(self, form_builder, form_widget: QWidget):
        """
        Integrate autocomplete with a form built by FormBuilder
        
        Args:
            form_builder: FormBuilder instance
            form_widget: The widget containing the form
        """
        # Get all field widgets from form builder
        field_widgets = form_builder.get_all_field_widgets()
        
        for field_name, widget in field_widgets.items():
            # Check if field should have autocomplete
            field_name_lower = field_name.lower().strip()
            
            if field_name_lower in self.AUTOCOMPLETE_FIELDS:
                # Get field type
                field_type = self.AUTOCOMPLETE_FIELDS[field_name_lower]
                
                # Check if it's a ComboboxWidget
                if isinstance(widget, ComboboxWidget) and hasattr(widget, '_input_widget'):
                    # Get the internal QComboBox
                    internal_combobox = widget._input_widget
                    
                    # Create autocomplete widget
                    autocomplete_widget = AutocompleteComboBox(internal_combobox.parent())
                    
                    # Setup data loader
                    data_loader = self.autocomplete_service.create_data_loader(field_type)
                    autocomplete_widget.set_data_loader(data_loader)
                    autocomplete_widget.set_debounce_delay(300)
                    autocomplete_widget.set_cache_enabled(True)
                    
                    # Replace the internal widget
                    # Get parent layout
                    parent = internal_combobox.parent()
                    if parent and hasattr(parent, 'layout'):
                        layout = parent.layout()
                        if layout:
                            # Find and replace
                            for i in range(layout.count()):
                                item = layout.itemAt(i)
                                if item and item.widget() == internal_combobox:
                                    layout.removeWidget(internal_combobox)
                                    internal_combobox.setParent(None)
                                    layout.insertWidget(i, autocomplete_widget)
                                    
                                    # Update widget reference
                                    widget._input_widget = autocomplete_widget
                                    
                                    # Connect signals
                                    autocomplete_widget.textChanged.connect(widget._on_text_changed)
                                    autocomplete_widget.itemSelected.connect(
                                        lambda text, w=widget: w.valueChanged.emit(text)
                                    )
                                    
                                    # Store reference
                                    self._autocomplete_widgets[field_name] = autocomplete_widget
                                    
                                    logger.info(f"Integrated autocomplete for field: {field_name}")
                                    break
    
    def get_autocomplete_widget(self, field_name: str) -> Optional[AutocompleteComboBox]:
        """
        Get autocomplete widget for a field
        
        Args:
            field_name: Name of the field
        
        Returns:
            AutocompleteComboBox if exists, None otherwise
        """
        return self._autocomplete_widgets.get(field_name)
    
    def refresh_all_data(self):
        """Refresh data for all autocomplete widgets"""
        # Clear cache
        self.autocomplete_service.clear_cache()
        
        # Reload data for all widgets
        for field_name, widget in self._autocomplete_widgets.items():
            widget.clear_cache()
            widget.load_data()
        
        logger.info("Refreshed data for all autocomplete widgets")
    
    def clear_all_caches(self):
        """Clear all caches"""
        self.autocomplete_service.clear_cache()
        
        for widget in self._autocomplete_widgets.values():
            widget.clear_cache()
        
        logger.info("Cleared all autocomplete caches")
