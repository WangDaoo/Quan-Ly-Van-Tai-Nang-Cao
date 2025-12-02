"""
Field Configuration Service - Business logic for managing dynamic field configurations
Provides CRUD operations, validation, field ordering, and grouping
"""
import logging
from typing import List, Dict, Optional, Any
import json

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.models.field_configuration import FieldConfiguration, FieldType, WidgetType


logger = logging.getLogger(__name__)


class FieldConfigService:
    """
    Service for managing field configurations with CRUD operations, validation, ordering, and grouping.
    
    Features:
    - CRUD operations for field configurations
    - Validation of field config data
    - Field ordering and reordering
    - Field grouping by category
    - Support for 10 field types
    """
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        """Initialize Field Configuration Service"""
        self.db = db_manager
    
    def create_field_config(self, config_data: Dict[str, Any]) -> FieldConfiguration:
        """Create a new field configuration"""
        try:
            field_config = FieldConfiguration(**config_data)
            db_data = self._prepare_for_database(field_config)
            config_id = self.db.insert_field_configuration(db_data)
            created_config = self.get_field_config_by_id(config_id)
            logger.info(f"Created field config: {created_config.field_name} for department {created_config.department_id} (ID: {config_id})")
            return created_config
        except ValueError as e:
            logger.error(f"Validation error creating field config: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating field config: {e}")
            raise
    
    def update_field_config(self, config_id: int, config_data: Dict[str, Any]) -> FieldConfiguration:
        """Update an existing field configuration"""
        try:
            existing_config = self.get_field_config_by_id(config_id)
            if not existing_config:
                raise ValueError(f"Field configuration với ID {config_id} không tồn tại")
            
            updated_data = existing_config.model_dump()
            updated_data.update(config_data)
            field_config = FieldConfiguration(**updated_data)
            db_data = self._prepare_for_database(field_config)
            
            query = """
                UPDATE field_configurations 
                SET field_name = ?, field_type = ?, widget_type = ?, is_required = ?,
                    validation_rules = ?, default_value = ?, options = ?, 
                    display_order = ?, category = ?, is_active = ?
                WHERE id = ?
            """
            params = (
                db_data['field_name'], db_data['field_type'], db_data['widget_type'], db_data['is_required'],
                db_data['validation_rules'], db_data['default_value'], db_data['options'], 
                db_data['display_order'], db_data['category'], db_data['is_active'], config_id
            )
            self.db.execute_update(query, params)
            updated_config = self.get_field_config_by_id(config_id)
            logger.info(f"Updated field config: {updated_config.field_name} (ID: {config_id})")
            return updated_config
        except ValueError as e:
            logger.error(f"Validation error updating field config: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating field config: {e}")
            raise
    
    def delete_field_config(self, config_id: int, soft_delete: bool = True) -> bool:
        """Delete a field configuration (soft or hard delete)"""
        try:
            existing_config = self.get_field_config_by_id(config_id)
            if not existing_config:
                raise ValueError(f"Field configuration với ID {config_id} không tồn tại")
            
            if soft_delete:
                query = "UPDATE field_configurations SET is_active = 0 WHERE id = ?"
                rows_affected = self.db.execute_update(query, (config_id,))
                logger.info(f"Soft deleted field config: {existing_config.field_name} (ID: {config_id})")
            else:
                query = "DELETE FROM field_configurations WHERE id = ?"
                rows_affected = self.db.execute_update(query, (config_id,))
                logger.info(f"Hard deleted field config: {existing_config.field_name} (ID: {config_id})")
            
            return rows_affected > 0
        except ValueError as e:
            logger.error(f"Error deleting field config: {e}")
            raise
        except Exception as e:
            logger.error(f"Error deleting field config: {e}")
            raise
    
    def get_field_config_by_id(self, config_id: int) -> Optional[FieldConfiguration]:
        """Get a field configuration by ID"""
        try:
            query = "SELECT * FROM field_configurations WHERE id = ?"
            results = self.db.execute_query(query, (config_id,))
            if results:
                return self._parse_from_database(results[0])
            return None
        except Exception as e:
            logger.error(f"Error retrieving field config {config_id}: {e}")
            raise
    
    def get_field_configs_by_department(self, department_id: int, active_only: bool = True) -> List[FieldConfiguration]:
        """Get all field configurations for a department, ordered by display_order"""
        try:
            config_data_list = self.db.get_field_configurations(department_id, active_only)
            configs = [self._parse_from_database(config_data) for config_data in config_data_list]
            logger.info(f"Retrieved {len(configs)} field configs for department {department_id}")
            return configs
        except Exception as e:
            logger.error(f"Error retrieving field configs for department {department_id}: {e}")
            raise
    
    def get_field_configs_by_category(self, department_id: int, category: str, active_only: bool = True) -> List[FieldConfiguration]:
        """Get field configurations for a department filtered by category"""
        try:
            query = "SELECT * FROM field_configurations WHERE department_id = ? AND category = ?"
            params = [department_id, category]
            if active_only:
                query += " AND is_active = 1"
            query += " ORDER BY display_order, field_name"
            results = self.db.execute_query(query, tuple(params))
            configs = [self._parse_from_database(config_data) for config_data in results]
            logger.info(f"Retrieved {len(configs)} field configs for department {department_id}, category '{category}'")
            return configs
        except Exception as e:
            logger.error(f"Error retrieving field configs by category: {e}")
            raise
    
    def get_grouped_field_configs(self, department_id: int, active_only: bool = True) -> Dict[str, List[FieldConfiguration]]:
        """Get field configurations grouped by category"""
        try:
            configs = self.get_field_configs_by_department(department_id, active_only)
            grouped = {}
            for config in configs:
                category = config.category or "Uncategorized"
                if category not in grouped:
                    grouped[category] = []
                grouped[category].append(config)
            sorted_grouped = dict(sorted(grouped.items()))
            logger.info(f"Grouped {len(configs)} field configs into {len(sorted_grouped)} categories for department {department_id}")
            return sorted_grouped
        except Exception as e:
            logger.error(f"Error grouping field configs: {e}")
            raise
    
    def reorder_field_configs(self, config_orders: List[Dict[str, int]]) -> bool:
        """Reorder field configurations by updating their display_order"""
        try:
            if not config_orders:
                raise ValueError("Config orders list không được để trống")
            
            for item in config_orders:
                if 'id' not in item or 'display_order' not in item:
                    raise ValueError("Mỗi item phải có 'id' và 'display_order'")
                config = self.get_field_config_by_id(item['id'])
                if not config:
                    raise ValueError(f"Field configuration với ID {item['id']} không tồn tại")
            
            query = "UPDATE field_configurations SET display_order = ? WHERE id = ?"
            params_list = [(item['display_order'], item['id']) for item in config_orders]
            self.db.execute_many(query, params_list)
            logger.info(f"Reordered {len(config_orders)} field configurations")
            return True
        except ValueError as e:
            logger.error(f"Validation error reordering field configs: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reordering field configs: {e}")
            raise
    
    def validate_field_config_data(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate field configuration data"""
        errors = []
        warnings = []
        try:
            field_config = FieldConfiguration(**config_data)
            if 'department_id' in config_data and 'field_name' in config_data:
                existing_configs = self.get_field_configs_by_department(config_data['department_id'], active_only=False)
                config_id = config_data.get('id')
                for existing in existing_configs:
                    if existing.field_name == config_data['field_name'] and existing.id != config_id:
                        errors.append(f"Trường '{config_data['field_name']}' đã tồn tại trong phòng ban này")
                        break
            if config_data.get('display_order', 0) > 100:
                warnings.append("Display order rất cao, có thể gây khó khăn trong quản lý")
            if not config_data.get('category'):
                warnings.append("Không có category, trường sẽ được nhóm vào 'Uncategorized'")
            is_valid = len(errors) == 0
            return {'is_valid': is_valid, 'errors': errors, 'warnings': warnings}
        except ValueError as e:
            errors.append(str(e))
            return {'is_valid': False, 'errors': errors, 'warnings': warnings}
        except Exception as e:
            logger.error(f"Error validating field config data: {e}")
            errors.append(f"Lỗi validation: {str(e)}")
            return {'is_valid': False, 'errors': errors, 'warnings': warnings}
    
    def get_available_field_types(self) -> List[Dict[str, str]]:
        """Get list of available field types"""
        return [
            {'value': FieldType.TEXT, 'label': 'Text'},
            {'value': FieldType.NUMBER, 'label': 'Number'},
            {'value': FieldType.CURRENCY, 'label': 'Currency'},
            {'value': FieldType.DATE, 'label': 'Date'},
            {'value': FieldType.DROPDOWN, 'label': 'Dropdown'},
            {'value': FieldType.CHECKBOX, 'label': 'Checkbox'},
            {'value': FieldType.EMAIL, 'label': 'Email'},
            {'value': FieldType.PHONE, 'label': 'Phone'},
            {'value': FieldType.TEXTAREA, 'label': 'TextArea'},
            {'value': FieldType.URL, 'label': 'URL'}
        ]
    
    def get_widget_type_for_field_type(self, field_type: FieldType) -> WidgetType:
        """Get the appropriate widget type for a given field type"""
        mapping = {
            FieldType.TEXT: WidgetType.TEXTBOX,
            FieldType.NUMBER: WidgetType.NUMBER_WIDGET,
            FieldType.CURRENCY: WidgetType.CURRENCY_WIDGET,
            FieldType.DATE: WidgetType.DATE_EDIT,
            FieldType.DROPDOWN: WidgetType.COMBOBOX,
            FieldType.CHECKBOX: WidgetType.CHECKBOX_WIDGET,
            FieldType.EMAIL: WidgetType.EMAIL_WIDGET,
            FieldType.PHONE: WidgetType.PHONE_WIDGET,
            FieldType.TEXTAREA: WidgetType.TEXTAREA_WIDGET,
            FieldType.URL: WidgetType.URL_WIDGET
        }
        return mapping.get(field_type, WidgetType.TEXTBOX)
    
    def get_categories_by_department(self, department_id: int) -> List[str]:
        """Get list of unique categories for a department"""
        try:
            query = """
                SELECT DISTINCT category 
                FROM field_configurations 
                WHERE department_id = ? AND is_active = 1 AND category IS NOT NULL
                ORDER BY category
            """
            results = self.db.execute_query(query, (department_id,))
            categories = [row['category'] for row in results if row['category']]
            return categories
        except Exception as e:
            logger.error(f"Error getting categories for department {department_id}: {e}")
            raise
    
    def duplicate_field_config(self, config_id: int, new_field_name: Optional[str] = None) -> FieldConfiguration:
        """Duplicate an existing field configuration"""
        try:
            source_config = self.get_field_config_by_id(config_id)
            if not source_config:
                raise ValueError(f"Field configuration với ID {config_id} không tồn tại")
            
            duplicate_data = source_config.model_dump(exclude={'id', 'created_at'})
            if new_field_name:
                duplicate_data['field_name'] = new_field_name
            else:
                duplicate_data['field_name'] = f"{source_config.field_name}_copy"
            
            existing_configs = self.get_field_configs_by_department(source_config.department_id, active_only=False)
            max_order = max([c.display_order for c in existing_configs], default=-1)
            duplicate_data['display_order'] = max_order + 1
            
            duplicated_config = self.create_field_config(duplicate_data)
            logger.info(f"Duplicated field config {config_id} to new config {duplicated_config.id}")
            return duplicated_config
        except ValueError as e:
            logger.error(f"Error duplicating field config: {e}")
            raise
        except Exception as e:
            logger.error(f"Error duplicating field config: {e}")
            raise
    
    def _prepare_for_database(self, field_config: FieldConfiguration) -> Dict[str, Any]:
        """Prepare FieldConfiguration object for database storage"""
        data = field_config.model_dump(exclude={'id', 'created_at'})
        if data.get('validation_rules'):
            data['validation_rules'] = json.dumps(data['validation_rules'])
        if data.get('options'):
            data['options'] = json.dumps(data['options'])
        return data
    
    def _parse_from_database(self, db_data: Dict[str, Any]) -> FieldConfiguration:
        """Parse database row into FieldConfiguration object"""
        if db_data.get('validation_rules'):
            try:
                db_data['validation_rules'] = json.loads(db_data['validation_rules'])
            except (json.JSONDecodeError, TypeError):
                db_data['validation_rules'] = None
        if db_data.get('options'):
            try:
                db_data['options'] = json.loads(db_data['options'])
            except (json.JSONDecodeError, TypeError):
                db_data['options'] = None
        return FieldConfiguration(**db_data)
