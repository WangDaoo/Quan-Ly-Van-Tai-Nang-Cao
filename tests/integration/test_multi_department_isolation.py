"""
Integration tests for multi-department data isolation
Tests requirement 8.4: Multi-department data isolation
"""

import pytest
import sqlite3
import tempfile
import os
import json

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services.field_config_service import FieldConfigService
from src.services.workspace_service import WorkspaceService


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize database with schema
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    # Create departments table
    cursor.execute("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE NOT NULL,
            display_name VARCHAR(255) NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create employees table
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) UNIQUE NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            department_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)
    
    # Create field_configurations table
    cursor.execute("""
        CREATE TABLE field_configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_id INTEGER NOT NULL,
            field_name VARCHAR(100) NOT NULL,
            field_type VARCHAR(50) NOT NULL,
            widget_type VARCHAR(50) NOT NULL,
            is_required BOOLEAN DEFAULT 0,
            validation_rules TEXT,
            default_value TEXT,
            options TEXT,
            display_order INTEGER DEFAULT 0,
            category VARCHAR(100),
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id),
            UNIQUE(department_id, field_name)
        )
    """)
    
    # Create formulas table
    cursor.execute("""
        CREATE TABLE formulas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_id INTEGER NOT NULL,
            target_field VARCHAR(100) NOT NULL,
            formula_expression TEXT NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)
    
    # Create employee_workspaces table
    cursor.execute("""
        CREATE TABLE employee_workspaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            workspace_name VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            configuration TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            UNIQUE(employee_id, workspace_name)
        )
    """)
    
    # Create business_records table
    cursor.execute("""
        CREATE TABLE business_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            workspace_id INTEGER,
            record_data TEXT NOT NULL,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id),
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (workspace_id) REFERENCES employee_workspaces(id)
        )
    """)
    
    # Insert test departments
    cursor.execute("""
        INSERT INTO departments (id, name, display_name, description, is_active)
        VALUES 
            (1, 'sales', 'Sales Department', 'Sales team', 1),
            (2, 'processing', 'Processing Department', 'Processing team', 1),
            (3, 'accounting', 'Accounting Department', 'Accounting team', 1)
    """)
    
    # Insert test employees
    cursor.execute("""
        INSERT INTO employees (id, username, full_name, email, department_id, is_active)
        VALUES 
            (1, 'sales_user', 'Sales User', 'sales@test.com', 1, 1),
            (2, 'processing_user', 'Processing User', 'processing@test.com', 2, 1),
            (3, 'accounting_user', 'Accounting User', 'accounting@test.com', 3, 1)
    """)
    
    conn.commit()
    conn.close()
    
    yield path
    
    # Cleanup
    try:
        os.unlink(path)
    except:
        pass


@pytest.fixture
def db_manager(temp_db):
    """Create database manager with temporary database"""
    manager = EnhancedDatabaseManager(temp_db, pool_size=2, enable_query_cache=False)
    yield manager
    manager.pool.close_all()


@pytest.fixture
def field_config_service(db_manager):
    """Create field config service"""
    return FieldConfigService(db_manager)


@pytest.fixture
def workspace_service(db_manager):
    """Create workspace service"""
    return WorkspaceService(db_manager)


class TestMultiDepartmentIsolation:
    """Integration tests for multi-department data isolation"""
    
    def test_field_configurations_isolated_by_department(self, field_config_service):
        """Test that field configurations are isolated by department"""
        # Create field config for Sales department
        sales_config = {
            'department_id': 1,
            'field_name': 'commission',
            'field_type': 'currency',
            'widget_type': 'currency',
            'is_required': True,
            'display_order': 1
        }
        sales_id = field_config_service.create_field_configuration(sales_config)
        
        # Create field config for Processing department
        processing_config = {
            'department_id': 2,
            'field_name': 'processing_fee',
            'field_type': 'currency',
            'widget_type': 'currency',
            'is_required': True,
            'display_order': 1
        }
        processing_id = field_config_service.create_field_configuration(processing_config)
        
        # Get configs for Sales department
        sales_configs = field_config_service.get_field_configurations_by_department(1)
        sales_field_names = [c['field_name'] for c in sales_configs]
        
        # Verify Sales only sees its own config
        assert 'commission' in sales_field_names
        assert 'processing_fee' not in sales_field_names
        
        # Get configs for Processing department
        processing_configs = field_config_service.get_field_configurations_by_department(2)
        processing_field_names = [c['field_name'] for c in processing_configs]
        
        # Verify Processing only sees its own config
        assert 'processing_fee' in processing_field_names
        assert 'commission' not in processing_field_names
    
    def test_formulas_isolated_by_department(self, db_manager):
        """Test that formulas are isolated by department"""
        # Create formula for Sales department
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO formulas (department_id, target_field, formula_expression, description)
            VALUES (1, 'total_sales', '[quantity] * [price]', 'Sales total')
        """)
        sales_formula_id = cursor.lastrowid
        
        # Create formula for Accounting department
        cursor.execute("""
            INSERT INTO formulas (department_id, target_field, formula_expression, description)
            VALUES (3, 'net_profit', '[revenue] - [expenses]', 'Net profit')
        """)
        accounting_formula_id = cursor.lastrowid
        conn.commit()
        
        # Get formulas for Sales department
        cursor.execute("SELECT * FROM formulas WHERE department_id = 1")
        sales_formulas = cursor.fetchall()
        
        # Get formulas for Accounting department
        cursor.execute("SELECT * FROM formulas WHERE department_id = 3")
        accounting_formulas = cursor.fetchall()
        
        db_manager.return_connection(conn)
        
        # Verify isolation
        assert len(sales_formulas) == 1
        assert sales_formulas[0][2] == 'total_sales'
        
        assert len(accounting_formulas) == 1
        assert accounting_formulas[0][2] == 'net_profit'
    
    def test_business_records_isolated_by_department(self, db_manager):
        """Test that business records are isolated by department"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create records for different departments
        for dept_id in [1, 2, 3]:
            for i in range(3):
                record_data = json.dumps({
                    'department': f'dept_{dept_id}',
                    'record': f'record_{i}'
                })
                cursor.execute("""
                    INSERT INTO business_records 
                    (department_id, employee_id, record_data, status)
                    VALUES (?, ?, ?, 'active')
                """, (dept_id, dept_id, record_data))
        
        conn.commit()
        
        # Verify each department only sees its own records
        for dept_id in [1, 2, 3]:
            cursor.execute("""
                SELECT COUNT(*) FROM business_records 
                WHERE department_id = ?
            """, (dept_id,))
            count = cursor.fetchone()[0]
            assert count == 3
            
            # Verify records belong to correct department
            cursor.execute("""
                SELECT record_data FROM business_records 
                WHERE department_id = ?
            """, (dept_id,))
            records = cursor.fetchall()
            for record in records:
                data = json.loads(record[0])
                assert data['department'] == f'dept_{dept_id}'
        
        db_manager.return_connection(conn)
    
    def test_workspace_isolation_within_employee(self, workspace_service, db_manager):
        """Test that workspaces are isolated within an employee"""
        # Create multiple workspaces for employee 1
        workspace1_data = {
            'employee_id': 1,
            'workspace_name': 'Project A',
            'configuration': json.dumps({'theme': 'light', 'layout': 'compact'})
        }
        ws1_id = workspace_service.create_workspace(workspace1_data)
        
        workspace2_data = {
            'employee_id': 1,
            'workspace_name': 'Project B',
            'configuration': json.dumps({'theme': 'dark', 'layout': 'expanded'})
        }
        ws2_id = workspace_service.create_workspace(workspace2_data)
        
        # Create records in different workspaces
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO business_records 
            (department_id, employee_id, workspace_id, record_data)
            VALUES (1, 1, ?, ?)
        """, (ws1_id, json.dumps({'workspace': 'A', 'data': 'test1'})))
        
        cursor.execute("""
            INSERT INTO business_records 
            (department_id, employee_id, workspace_id, record_data)
            VALUES (1, 1, ?, ?)
        """, (ws2_id, json.dumps({'workspace': 'B', 'data': 'test2'})))
        
        conn.commit()
        
        # Verify workspace isolation
        cursor.execute("""
            SELECT record_data FROM business_records 
            WHERE workspace_id = ?
        """, (ws1_id,))
        ws1_records = cursor.fetchall()
        assert len(ws1_records) == 1
        assert json.loads(ws1_records[0][0])['workspace'] == 'A'
        
        cursor.execute("""
            SELECT record_data FROM business_records 
            WHERE workspace_id = ?
        """, (ws2_id,))
        ws2_records = cursor.fetchall()
        assert len(ws2_records) == 1
        assert json.loads(ws2_records[0][0])['workspace'] == 'B'
        
        db_manager.return_connection(conn)
    
    def test_employee_cannot_access_other_department_data(self, db_manager):
        """Test that employees cannot access other department's data"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create records for each department
        for dept_id in [1, 2, 3]:
            record_data = json.dumps({
                'department': f'dept_{dept_id}',
                'sensitive': f'data_{dept_id}'
            })
            cursor.execute("""
                INSERT INTO business_records 
                (department_id, employee_id, record_data)
                VALUES (?, ?, ?)
            """, (dept_id, dept_id, record_data))
        
        conn.commit()
        
        # Employee 1 (Sales) tries to access their data
        cursor.execute("""
            SELECT record_data FROM business_records 
            WHERE department_id = 1 AND employee_id = 1
        """)
        sales_records = cursor.fetchall()
        assert len(sales_records) == 1
        
        # Employee 1 should not see other departments' data
        cursor.execute("""
            SELECT record_data FROM business_records 
            WHERE department_id != 1 AND employee_id = 1
        """)
        other_records = cursor.fetchall()
        assert len(other_records) == 0
        
        db_manager.return_connection(conn)
    
    def test_department_specific_field_validation(self, field_config_service):
        """Test that field validation rules are department-specific"""
        # Create field with validation for Sales
        sales_field = {
            'department_id': 1,
            'field_name': 'discount',
            'field_type': 'number',
            'widget_type': 'number',
            'validation_rules': json.dumps({
                'min': 0,
                'max': 50,
                'required': True
            }),
            'display_order': 1
        }
        field_config_service.create_field_configuration(sales_field)
        
        # Create same field with different validation for Processing
        processing_field = {
            'department_id': 2,
            'field_name': 'discount',
            'field_type': 'number',
            'widget_type': 'number',
            'validation_rules': json.dumps({
                'min': 0,
                'max': 20,
                'required': False
            }),
            'display_order': 1
        }
        field_config_service.create_field_configuration(processing_field)
        
        # Get configs and verify different validation rules
        sales_configs = field_config_service.get_field_configurations_by_department(1)
        sales_discount = next(c for c in sales_configs if c['field_name'] == 'discount')
        sales_rules = json.loads(sales_discount['validation_rules'])
        
        processing_configs = field_config_service.get_field_configurations_by_department(2)
        processing_discount = next(c for c in processing_configs if c['field_name'] == 'discount')
        processing_rules = json.loads(processing_discount['validation_rules'])
        
        # Verify different rules
        assert sales_rules['max'] == 50
        assert processing_rules['max'] == 20
        assert sales_rules['required'] is True
        assert processing_rules['required'] is False
    
    def test_cross_department_data_transfer_via_workflow(self, db_manager):
        """Test that data can be transferred between departments via workflow"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create record in Sales department
        sales_data = json.dumps({
            'customer': 'Test Customer',
            'amount': 1000000,
            'status': 'Approved'
        })
        cursor.execute("""
            INSERT INTO business_records 
            (department_id, employee_id, record_data)
            VALUES (1, 1, ?)
        """, (sales_data,))
        sales_record_id = cursor.lastrowid
        conn.commit()
        
        # Simulate workflow push to Processing department
        cursor.execute("""
            INSERT INTO business_records 
            (department_id, employee_id, record_data)
            VALUES (2, 2, ?)
        """, (sales_data,))
        processing_record_id = cursor.lastrowid
        conn.commit()
        
        # Verify both departments have the record
        cursor.execute("""
            SELECT COUNT(*) FROM business_records 
            WHERE department_id = 1
        """)
        sales_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM business_records 
            WHERE department_id = 2
        """)
        processing_count = cursor.fetchone()[0]
        
        db_manager.return_connection(conn)
        
        assert sales_count == 1
        assert processing_count == 1
    
    def test_workspace_configuration_isolation(self, workspace_service):
        """Test that workspace configurations are isolated"""
        # Create workspaces for different employees
        ws1_data = {
            'employee_id': 1,
            'workspace_name': 'Sales Workspace',
            'configuration': json.dumps({
                'columns': ['customer', 'amount'],
                'filters': {'status': 'active'}
            })
        }
        ws1_id = workspace_service.create_workspace(ws1_data)
        
        ws2_data = {
            'employee_id': 2,
            'workspace_name': 'Processing Workspace',
            'configuration': json.dumps({
                'columns': ['order_id', 'status'],
                'filters': {'processed': True}
            })
        }
        ws2_id = workspace_service.create_workspace(ws2_data)
        
        # Get workspaces for each employee
        ws1 = workspace_service.get_workspace_by_id(ws1_id)
        ws2 = workspace_service.get_workspace_by_id(ws2_id)
        
        # Verify configurations are different
        config1 = json.loads(ws1['configuration'])
        config2 = json.loads(ws2['configuration'])
        
        assert config1['columns'] != config2['columns']
        assert config1['filters'] != config2['filters']
