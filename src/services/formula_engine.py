"""
Formula Engine Service

Provides formula parsing, validation, and evaluation for automatic calculations

Requirements: 6.1, 6.2, 6.3, 6.5, 17.1, 17.3, 17.4
"""
import logging
import re
from typing import Dict, Any, List, Optional
from src.models.formula import Formula
from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.utils.error_handler import FormulaError, ValidationError, handle_errors


logger = logging.getLogger(__name__)


class FormulaEngine:
    """
    Formula Engine for parsing, validating, and evaluating formulas
    
    Features:
    - Parse formula expressions with field references
    - Validate formula syntax
    - Evaluate formulas with field values
    - Support for 4 operators: +, -, *, /
    - Support for parentheses
    - Error handling for division by zero and invalid fields
    """
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        """
        Initialize formula engine
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
    
    def get_formulas_for_department(self, department_id: int) -> List[Formula]:
        """
        Get all active formulas for a department
        
        Args:
            department_id: Department ID
            
        Returns:
            List of Formula instances
        """
        try:
            query = """
                SELECT id, department_id, target_field, formula_expression, 
                       description, is_active, created_at
                FROM formulas
                WHERE department_id = ? AND is_active = 1
                ORDER BY id
            """
            rows = self.db_manager.execute_query(query, (department_id,))
            
            formulas = []
            for row in rows:
                formula = Formula(
                    id=row['id'],
                    department_id=row['department_id'],
                    target_field=row['target_field'],
                    formula_expression=row['formula_expression'],
                    description=row['description'],
                    is_active=bool(row['is_active']),
                    created_at=row['created_at']
                )
                formulas.append(formula)
            
            return formulas
            
        except Exception as e:
            logger.error(f"Error getting formulas for department {department_id}: {e}")
            return []
    
    def evaluate_formula(
        self,
        formula: Formula,
        field_values: Dict[str, Any]
    ) -> Optional[float]:
        """
        Evaluate a formula with given field values
        
        Args:
            formula: Formula instance
            field_values: Dictionary of field names to values
            
        Returns:
            Calculated result as float, or None if evaluation fails
        """
        try:
            # Get field references from formula
            field_refs = formula.get_field_references()
            
            # Replace field references with values
            expression = formula.formula_expression
            
            for field_ref in field_refs:
                field_value = field_values.get(field_ref)
                
                # Handle missing or invalid values
                if field_value is None:
                    logger.warning(f"Field '{field_ref}' not found in field_values")
                    return None
                
                # Convert to number
                try:
                    numeric_value = float(field_value)
                except (ValueError, TypeError):
                    logger.warning(f"Field '{field_ref}' has non-numeric value: {field_value}")
                    return None
                
                # Replace [Field_Name] with numeric value
                expression = expression.replace(f"[{field_ref}]", str(numeric_value))
            
            # Evaluate the expression
            result = eval(expression, {"__builtins__": {}}, {})
            
            return float(result)
            
        except ZeroDivisionError:
            logger.error(f"Division by zero in formula: {formula.formula_expression}")
            return None
        except Exception as e:
            logger.error(f"Error evaluating formula: {e}")
            return None
    
    def evaluate_all_formulas(
        self,
        department_id: int,
        field_values: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Evaluate all formulas for a department and return calculated values
        
        Args:
            department_id: Department ID
            field_values: Dictionary of field names to values
            
        Returns:
            Dictionary mapping target fields to calculated values
        """
        results = {}
        
        formulas = self.get_formulas_for_department(department_id)
        
        for formula in formulas:
            result = self.evaluate_formula(formula, field_values)
            if result is not None:
                results[formula.target_field] = result
        
        return results
    
    def validate_formula_syntax(self, formula_expression: str) -> tuple[bool, Optional[str]]:
        """
        Validate formula syntax
        
        Args:
            formula_expression: Formula expression string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Create a temporary formula to validate
            temp_formula = Formula(
                department_id=1,
                target_field="temp",
                formula_expression=formula_expression
            )
            return True, None
        except ValueError as e:
            return False, str(e)
    
    def get_dependent_fields(self, formula: Formula) -> List[str]:
        """
        Get list of fields that a formula depends on
        
        Args:
            formula: Formula instance
            
        Returns:
            List of field names
        """
        return formula.get_field_references()
    
    def test_formula(
        self,
        formula_expression: str,
        test_values: Dict[str, Any]
    ) -> tuple[bool, Optional[float], Optional[str]]:
        """
        Test a formula with sample values
        
        Args:
            formula_expression: Formula expression string
            test_values: Dictionary of field names to test values
            
        Returns:
            Tuple of (success, result, error_message)
        """
        try:
            # Validate syntax first
            is_valid, error = self.validate_formula_syntax(formula_expression)
            if not is_valid:
                return False, None, error
            
            # Create temporary formula
            temp_formula = Formula(
                department_id=1,
                target_field="test",
                formula_expression=formula_expression
            )
            
            # Evaluate
            result = self.evaluate_formula(temp_formula, test_values)
            
            if result is None:
                return False, None, "Không thể tính toán công thức với giá trị đã cho"
            
            return True, result, None
            
        except Exception as e:
            return False, None, str(e)
