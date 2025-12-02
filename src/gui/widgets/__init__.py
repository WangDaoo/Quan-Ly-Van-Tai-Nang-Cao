"""Custom widgets for the application"""

from .field_widgets import (
    BaseFieldWidget,
    TextboxWidget,
    NumberWidget,
    CurrencyWidget,
    DateEditWidget,
    ComboboxWidget,
    CheckboxWidget,
    EmailWidget,
    PhoneWidget,
    TextAreaWidget,
    URLWidget
)

from .form_validator import (
    BaseValidator,
    RequiredValidator,
    NumberOnlyValidator,
    TextOnlyValidator,
    NoSpecialCharsValidator,
    EmailFormatValidator,
    PatternMatchingValidator,
    FormValidator,
    ValidationRuleBuilder
)

from .form_builder import (
    WidgetFactory,
    FormBuilder
)

from .dynamic_form_widget import (
    DynamicFormWidget
)

from .excel_header_view import (
    ExcelHeaderView
)

from .excel_like_table import (
    ExcelLikeTable,
    NumberFormatDelegate,
    CurrencyFormatDelegate
)

from .copy_paste_handler import (
    CopyPasteHandler
)

from .excel_filter_dialog import (
    ExcelFilterDialog
)

from .column_visibility_dialog import (
    ColumnVisibilityDialog
)

from .autocomplete_combobox import (
    AutocompleteComboBox,
    FuzzyFilterProxyModel
)

from .autocomplete_integration import (
    AutocompleteIntegration
)

from .input_form_widget import (
    InputFormWidget
)

from .main_table_widget import (
    MainTableWidget
)

from .suggestion_tab_widget import (
    SuggestionTabWidget
)

from .employee_tab_widget import (
    EmployeeTabWidget,
    DepartmentWidget
)

from .pagination_widget import (
    PaginationWidget
)

__all__ = [
    'BaseFieldWidget',
    'TextboxWidget',
    'NumberWidget',
    'CurrencyWidget',
    'DateEditWidget',
    'ComboboxWidget',
    'CheckboxWidget',
    'EmailWidget',
    'PhoneWidget',
    'TextAreaWidget',
    'URLWidget',
    'BaseValidator',
    'RequiredValidator',
    'NumberOnlyValidator',
    'TextOnlyValidator',
    'NoSpecialCharsValidator',
    'EmailFormatValidator',
    'PatternMatchingValidator',
    'FormValidator',
    'ValidationRuleBuilder',
    'WidgetFactory',
    'FormBuilder',
    'DynamicFormWidget',
    'ExcelHeaderView',
    'ExcelLikeTable',
    'NumberFormatDelegate',
    'CurrencyFormatDelegate',
    'CopyPasteHandler',
    'ExcelFilterDialog',
    'ColumnVisibilityDialog',
    'AutocompleteComboBox',
    'FuzzyFilterProxyModel',
    'AutocompleteIntegration',
    'InputFormWidget',
    'MainTableWidget',
    'SuggestionTabWidget',
    'EmployeeTabWidget',
    'DepartmentWidget',
    'PaginationWidget'
]
