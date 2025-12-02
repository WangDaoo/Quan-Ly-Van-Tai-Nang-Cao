-- Rollback initial schema migration
-- This drops all tables created in V001

DROP TRIGGER IF EXISTS trg_business_records_updated_at;
DROP TRIGGER IF EXISTS trg_trips_updated_at;

DROP INDEX IF EXISTS idx_business_records_created;
DROP INDEX IF EXISTS idx_business_records_workspace;
DROP INDEX IF EXISTS idx_business_records_employee;
DROP INDEX IF EXISTS idx_business_records_dept;
DROP INDEX IF EXISTS idx_workspaces_active;
DROP INDEX IF EXISTS idx_workspaces_employee;
DROP INDEX IF EXISTS idx_workflow_history_created;
DROP INDEX IF EXISTS idx_workflow_history_status;
DROP INDEX IF EXISTS idx_workflow_history_dept;
DROP INDEX IF EXISTS idx_workflow_history_record;
DROP INDEX IF EXISTS idx_push_conditions_active;
DROP INDEX IF EXISTS idx_push_conditions_dept;
DROP INDEX IF EXISTS idx_formulas_target;
DROP INDEX IF EXISTS idx_formulas_dept;
DROP INDEX IF EXISTS idx_field_configs_order;
DROP INDEX IF EXISTS idx_field_configs_dept;
DROP INDEX IF EXISTS idx_employees_active;
DROP INDEX IF EXISTS idx_employees_department;
DROP INDEX IF EXISTS idx_employees_username;
DROP INDEX IF EXISTS idx_departments_active;
DROP INDEX IF EXISTS idx_departments_name;
DROP INDEX IF EXISTS idx_company_prices_company;
DROP INDEX IF EXISTS idx_company_prices_khach_hang;
DROP INDEX IF EXISTS idx_company_prices_route;
DROP INDEX IF EXISTS idx_trips_diem;
DROP INDEX IF EXISTS idx_trips_khach_hang;

DROP TABLE IF EXISTS business_records;
DROP TABLE IF EXISTS employee_workspaces;
DROP TABLE IF EXISTS workflow_history;
DROP TABLE IF EXISTS push_conditions;
DROP TABLE IF EXISTS formulas;
DROP TABLE IF EXISTS field_configurations;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS company_prices;
DROP TABLE IF EXISTS trips;
