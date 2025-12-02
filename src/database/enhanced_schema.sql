-- Enhanced Database Schema for Transport Management System
-- Version: 1.0
-- Created: 2025-12-01

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================================================
-- Core Tables
-- ============================================================================

-- Trips table: Main table for transport trip records
CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_chuyen VARCHAR(10) UNIQUE NOT NULL,
    khach_hang VARCHAR(255) NOT NULL,
    diem_di VARCHAR(255),
    diem_den VARCHAR(255),
    gia_ca INTEGER NOT NULL,
    khoan_luong INTEGER DEFAULT 0,
    chi_phi_khac INTEGER DEFAULT 0,
    ghi_chu TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_gia_ca_positive CHECK (gia_ca >= 0),
    CONSTRAINT chk_khoan_luong_positive CHECK (khoan_luong >= 0),
    CONSTRAINT chk_chi_phi_khac_positive CHECK (chi_phi_khac >= 0)
);

-- Company prices table: Price lists from different companies
CREATE TABLE IF NOT EXISTS company_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name VARCHAR(100) NOT NULL,
    khach_hang VARCHAR(255) NOT NULL,
    diem_di VARCHAR(255) NOT NULL,
    diem_den VARCHAR(255) NOT NULL,
    gia_ca INTEGER NOT NULL,
    khoan_luong INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_company_gia_ca_positive CHECK (gia_ca >= 0),
    CONSTRAINT chk_company_khoan_luong_positive CHECK (khoan_luong >= 0),
    CONSTRAINT chk_company_name_valid CHECK (company_name IN ('A', 'B', 'C'))
);

-- ============================================================================
-- Organization Tables
-- ============================================================================

-- Departments table: Organization departments
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_is_active_boolean CHECK (is_active IN (0, 1))
);

-- Employees table: System users
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    department_id INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    CONSTRAINT chk_employee_active_boolean CHECK (is_active IN (0, 1)),
    CONSTRAINT chk_email_format CHECK (email IS NULL OR email LIKE '%@%')
);

-- ============================================================================
-- Configuration Tables
-- ============================================================================

-- Field configurations table: Dynamic form field definitions
CREATE TABLE IF NOT EXISTS field_configurations (
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
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
    CONSTRAINT chk_field_required_boolean CHECK (is_required IN (0, 1)),
    CONSTRAINT chk_field_active_boolean CHECK (is_active IN (0, 1)),
    CONSTRAINT chk_field_type_valid CHECK (field_type IN ('text', 'number', 'currency', 'date', 'dropdown', 'checkbox', 'email', 'phone', 'textarea', 'url')),
    CONSTRAINT chk_widget_type_valid CHECK (widget_type IN ('textbox', 'number', 'currency', 'dateedit', 'combobox', 'checkbox', 'email', 'phone', 'textarea', 'url')),
    UNIQUE(department_id, field_name)
);

-- Formulas table: Automatic calculation formulas
CREATE TABLE IF NOT EXISTS formulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,
    target_field VARCHAR(100) NOT NULL,
    formula_expression TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
    CONSTRAINT chk_formula_active_boolean CHECK (is_active IN (0, 1))
);

-- ============================================================================
-- Workflow Tables
-- ============================================================================

-- Push conditions table: Workflow automation rules
CREATE TABLE IF NOT EXISTS push_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_department_id INTEGER NOT NULL,
    target_department_id INTEGER NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    operator VARCHAR(50) NOT NULL,
    value TEXT,
    logic_operator VARCHAR(10) DEFAULT 'AND',
    condition_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_department_id) REFERENCES departments(id) ON DELETE CASCADE,
    FOREIGN KEY (target_department_id) REFERENCES departments(id) ON DELETE CASCADE,
    CONSTRAINT chk_push_active_boolean CHECK (is_active IN (0, 1)),
    CONSTRAINT chk_operator_valid CHECK (operator IN ('equals', 'not_equals', 'contains', 'not_contains', 'starts_with', 'ends_with', 'greater_than', 'less_than', 'greater_or_equal', 'less_or_equal', 'is_empty', 'is_not_empty')),
    CONSTRAINT chk_logic_operator_valid CHECK (logic_operator IN ('AND', 'OR')),
    CONSTRAINT chk_different_departments CHECK (source_department_id != target_department_id)
);

-- Workflow history table: Audit trail for workflow operations
CREATE TABLE IF NOT EXISTS workflow_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,
    source_department_id INTEGER NOT NULL,
    target_department_id INTEGER NOT NULL,
    pushed_by INTEGER,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_department_id) REFERENCES departments(id) ON DELETE CASCADE,
    FOREIGN KEY (target_department_id) REFERENCES departments(id) ON DELETE CASCADE,
    FOREIGN KEY (pushed_by) REFERENCES employees(id) ON DELETE SET NULL,
    CONSTRAINT chk_status_valid CHECK (status IN ('success', 'failed', 'pending'))
);

-- ============================================================================
-- Workspace Tables
-- ============================================================================

-- Employee workspaces table: Personal workspace configurations
CREATE TABLE IF NOT EXISTS employee_workspaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    workspace_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    configuration TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    CONSTRAINT chk_workspace_active_boolean CHECK (is_active IN (0, 1)),
    UNIQUE(employee_id, workspace_name)
);

-- Business records table: Department-specific business data
CREATE TABLE IF NOT EXISTS business_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    workspace_id INTEGER,
    record_data TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (workspace_id) REFERENCES employee_workspaces(id) ON DELETE SET NULL,
    CONSTRAINT chk_record_status_valid CHECK (status IN ('active', 'archived', 'deleted'))
);

-- ============================================================================
-- Performance Indexes
-- ============================================================================

-- Trips table indexes
CREATE INDEX IF NOT EXISTS idx_trips_khach_hang ON trips(khach_hang);
CREATE INDEX IF NOT EXISTS idx_trips_diem ON trips(diem_di, diem_den);
CREATE INDEX IF NOT EXISTS idx_trips_created_at ON trips(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_trips_ma_chuyen ON trips(ma_chuyen);

-- Company prices indexes
CREATE INDEX IF NOT EXISTS idx_company_prices_route ON company_prices(company_name, diem_di, diem_den);
CREATE INDEX IF NOT EXISTS idx_company_prices_khach_hang ON company_prices(khach_hang);
CREATE INDEX IF NOT EXISTS idx_company_prices_company ON company_prices(company_name);

-- Departments indexes
CREATE INDEX IF NOT EXISTS idx_departments_name ON departments(name);
CREATE INDEX IF NOT EXISTS idx_departments_active ON departments(is_active);

-- Employees indexes
CREATE INDEX IF NOT EXISTS idx_employees_username ON employees(username);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_active ON employees(is_active);

-- Field configurations indexes
CREATE INDEX IF NOT EXISTS idx_field_configs_dept ON field_configurations(department_id, is_active);
CREATE INDEX IF NOT EXISTS idx_field_configs_order ON field_configurations(department_id, display_order);

-- Formulas indexes
CREATE INDEX IF NOT EXISTS idx_formulas_dept ON formulas(department_id, is_active);
CREATE INDEX IF NOT EXISTS idx_formulas_target ON formulas(target_field);

-- Push conditions indexes
CREATE INDEX IF NOT EXISTS idx_push_conditions_dept ON push_conditions(source_department_id, target_department_id);
CREATE INDEX IF NOT EXISTS idx_push_conditions_active ON push_conditions(is_active);

-- Workflow history indexes
CREATE INDEX IF NOT EXISTS idx_workflow_history_record ON workflow_history(record_id, created_at);
CREATE INDEX IF NOT EXISTS idx_workflow_history_dept ON workflow_history(source_department_id, target_department_id);
CREATE INDEX IF NOT EXISTS idx_workflow_history_status ON workflow_history(status);
CREATE INDEX IF NOT EXISTS idx_workflow_history_created ON workflow_history(created_at DESC);

-- Employee workspaces indexes
CREATE INDEX IF NOT EXISTS idx_workspaces_employee ON employee_workspaces(employee_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_active ON employee_workspaces(is_active);

-- Business records indexes
CREATE INDEX IF NOT EXISTS idx_business_records_dept ON business_records(department_id, status);
CREATE INDEX IF NOT EXISTS idx_business_records_employee ON business_records(employee_id);
CREATE INDEX IF NOT EXISTS idx_business_records_workspace ON business_records(workspace_id);
CREATE INDEX IF NOT EXISTS idx_business_records_created ON business_records(created_at DESC);

-- ============================================================================
-- Triggers for automatic timestamp updates
-- ============================================================================

-- Trips update trigger
CREATE TRIGGER IF NOT EXISTS trg_trips_updated_at
AFTER UPDATE ON trips
FOR EACH ROW
BEGIN
    UPDATE trips SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Business records update trigger
CREATE TRIGGER IF NOT EXISTS trg_business_records_updated_at
AFTER UPDATE ON business_records
FOR EACH ROW
BEGIN
    UPDATE business_records SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
