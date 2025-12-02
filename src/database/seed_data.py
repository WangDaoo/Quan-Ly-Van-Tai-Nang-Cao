"""
Data Seeding for Transport Management System
Provides sample data for development and testing
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class DataSeeder:
    """Seeds database with sample data"""
    
    def __init__(self, db_manager):
        """
        Initialize data seeder
        
        Args:
            db_manager: EnhancedDatabaseManager instance
        """
        self.db = db_manager
    
    def seed_all(self):
        """Seed all tables with sample data"""
        logger.info("Starting data seeding...")
        
        try:
            # Seed in order of dependencies
            self.seed_departments()
            self.seed_employees()
            self.seed_trips()
            self.seed_company_prices()
            self.seed_workspaces()
            
            logger.info("Data seeding completed successfully")
            return True
        except Exception as e:
            logger.error(f"Data seeding failed: {e}")
            return False
    
    def seed_departments(self):
        """Seed departments table"""
        logger.info("Seeding departments...")
        
        departments = [
            {
                'name': 'sales',
                'display_name': 'Phòng Kinh Doanh',
                'description': 'Phòng ban chịu trách nhiệm về kinh doanh và bán hàng',
                'is_active': 1
            },
            {
                'name': 'processing',
                'display_name': 'Phòng Điều Hành',
                'description': 'Phòng ban xử lý và điều hành các chuyến xe',
                'is_active': 1
            },
            {
                'name': 'accounting',
                'display_name': 'Phòng Kế Toán',
                'description': 'Phòng ban quản lý tài chính và kế toán',
                'is_active': 1
            }
        ]
        
        for dept in departments:
            try:
                self.db.insert_department(dept)
                logger.info(f"Created department: {dept['display_name']}")
            except Exception as e:
                logger.warning(f"Department {dept['name']} may already exist: {e}")
    
    def seed_employees(self):
        """Seed employees table"""
        logger.info("Seeding employees...")
        
        # Get department IDs
        departments = self.db.get_all_departments()
        dept_map = {d['name']: d['id'] for d in departments}
        
        employees = [
            {
                'username': 'nguyen_van_a',
                'full_name': 'Nguyễn Văn A',
                'email': 'nguyenvana@company.com',
                'department_id': dept_map.get('sales'),
                'is_active': 1
            },
            {
                'username': 'tran_thi_b',
                'full_name': 'Trần Thị B',
                'email': 'tranthib@company.com',
                'department_id': dept_map.get('sales'),
                'is_active': 1
            },
            {
                'username': 'le_van_c',
                'full_name': 'Lê Văn C',
                'email': 'levanc@company.com',
                'department_id': dept_map.get('processing'),
                'is_active': 1
            },
            {
                'username': 'pham_thi_d',
                'full_name': 'Phạm Thị D',
                'email': 'phamthid@company.com',
                'department_id': dept_map.get('processing'),
                'is_active': 1
            },
            {
                'username': 'hoang_van_e',
                'full_name': 'Hoàng Văn E',
                'email': 'hoangvane@company.com',
                'department_id': dept_map.get('accounting'),
                'is_active': 1
            }
        ]
        
        for emp in employees:
            try:
                self.db.insert_employee(emp)
                logger.info(f"Created employee: {emp['full_name']}")
            except Exception as e:
                logger.warning(f"Employee {emp['username']} may already exist: {e}")
    
    def seed_trips(self):
        """Seed trips table with 50+ records"""
        logger.info("Seeding trips...")
        
        customers = [
            'Công ty TNHH ABC',
            'Công ty CP XYZ',
            'Công ty TNHH Vận Tải Minh Anh',
            'Công ty CP Logistics Việt Nam',
            'Công ty TNHH Thương Mại Hòa Bình',
            'Công ty CP Vận Tải Sài Gòn',
            'Công ty TNHH Giao Nhận Hà Nội',
            'Công ty CP Logistics Đà Nẵng',
            'Công ty TNHH Vận Chuyển Nhanh',
            'Công ty CP Thương Mại Quốc Tế'
        ]
        
        locations = [
            'Hà Nội', 'TP. Hồ Chí Minh', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ',
            'Biên Hòa', 'Nha Trang', 'Huế', 'Vũng Tàu', 'Buôn Ma Thuột',
            'Quy Nhơn', 'Thái Nguyên', 'Nam Định', 'Hải Dương', 'Bắc Ninh'
        ]
        
        trips_data = []
        for i in range(1, 51):
            trip = {
                'ma_chuyen': f'C{i:03d}',
                'khach_hang': random.choice(customers),
                'diem_di': random.choice(locations),
                'diem_den': random.choice([loc for loc in locations if loc != random.choice(locations)]),
                'gia_ca': random.randint(2000000, 15000000),
                'khoan_luong': random.randint(500000, 3000000),
                'chi_phi_khac': random.randint(0, 500000),
                'ghi_chu': f'Chuyến xe số {i}' if i % 3 == 0 else ''
            }
            trips_data.append(trip)
        
        for trip in trips_data:
            try:
                self.db.insert_trip(trip)
                logger.debug(f"Created trip: {trip['ma_chuyen']}")
            except Exception as e:
                logger.warning(f"Trip {trip['ma_chuyen']} may already exist: {e}")
        
        logger.info(f"Created {len(trips_data)} trips")
    
    def seed_company_prices(self):
        """Seed company prices for 3 companies with 20+ routes each"""
        logger.info("Seeding company prices...")
        
        companies = ['A', 'B', 'C']
        
        customers = [
            'Công ty TNHH ABC',
            'Công ty CP XYZ',
            'Công ty TNHH Vận Tải Minh Anh',
            'Công ty CP Logistics Việt Nam',
            'Công ty TNHH Thương Mại Hòa Bình'
        ]
        
        routes = [
            ('Hà Nội', 'TP. Hồ Chí Minh'),
            ('Hà Nội', 'Đà Nẵng'),
            ('Hà Nội', 'Hải Phòng'),
            ('TP. Hồ Chí Minh', 'Đà Nẵng'),
            ('TP. Hồ Chí Minh', 'Cần Thơ'),
            ('TP. Hồ Chí Minh', 'Nha Trang'),
            ('Đà Nẵng', 'Huế'),
            ('Đà Nẵng', 'Quy Nhơn'),
            ('Hải Phòng', 'Hà Nội'),
            ('Cần Thơ', 'TP. Hồ Chí Minh'),
            ('Nha Trang', 'Đà Nẵng'),
            ('Huế', 'Hà Nội'),
            ('Quy Nhơn', 'TP. Hồ Chí Minh'),
            ('Vũng Tàu', 'TP. Hồ Chí Minh'),
            ('Biên Hòa', 'Hà Nội'),
            ('Buôn Ma Thuột', 'Đà Nẵng'),
            ('Thái Nguyên', 'Hà Nội'),
            ('Nam Định', 'Hải Phòng'),
            ('Hải Dương', 'Hà Nội'),
            ('Bắc Ninh', 'Hà Nội'),
            ('Hà Nội', 'Cần Thơ'),
            ('TP. Hồ Chí Minh', 'Huế'),
            ('Đà Nẵng', 'Vũng Tàu'),
            ('Hải Phòng', 'Đà Nẵng'),
            ('Cần Thơ', 'Nha Trang')
        ]
        
        prices_data = []
        for company in companies:
            # Each company has different pricing
            base_multiplier = {'A': 1.0, 'B': 0.95, 'C': 1.05}[company]
            
            for customer in customers:
                for diem_di, diem_den in routes[:20]:  # 20 routes per company
                    price = {
                        'company_name': company,
                        'khach_hang': customer,
                        'diem_di': diem_di,
                        'diem_den': diem_den,
                        'gia_ca': int(random.randint(2000000, 15000000) * base_multiplier),
                        'khoan_luong': int(random.randint(500000, 3000000) * base_multiplier)
                    }
                    prices_data.append(price)
        
        for price in prices_data:
            try:
                self.db.insert_company_price(price)
            except Exception as e:
                logger.warning(f"Price record may already exist: {e}")
        
        logger.info(f"Created {len(prices_data)} company price records")
    
    def seed_workspaces(self):
        """Seed employee workspaces"""
        logger.info("Seeding workspaces...")
        
        # Get employees
        departments = self.db.get_all_departments()
        
        workspaces_data = []
        for dept in departments:
            employees = self.db.get_employees_by_department(dept['id'])
            
            for emp in employees:
                # Create default workspace for each employee
                workspace = {
                    'employee_id': emp['id'],
                    'workspace_name': 'Default',
                    'is_active': 1,
                    'configuration': '{}'
                }
                workspaces_data.append(workspace)
                
                # Create additional workspace for some employees
                if emp['id'] % 2 == 0:
                    workspace2 = {
                        'employee_id': emp['id'],
                        'workspace_name': 'Project A',
                        'is_active': 1,
                        'configuration': '{}'
                    }
                    workspaces_data.append(workspace2)
        
        for workspace in workspaces_data:
            try:
                self.db.insert_workspace(workspace)
                logger.debug(f"Created workspace: {workspace['workspace_name']} for employee {workspace['employee_id']}")
            except Exception as e:
                logger.warning(f"Workspace may already exist: {e}")
        
        logger.info(f"Created {len(workspaces_data)} workspaces")
    
    def clear_all_data(self):
        """Clear all data from tables (for testing)"""
        logger.warning("Clearing all data from database...")
        
        tables = [
            'business_records',
            'employee_workspaces',
            'workflow_history',
            'push_conditions',
            'formulas',
            'field_configurations',
            'employees',
            'departments',
            'company_prices',
            'trips'
        ]
        
        with self.db.transaction() as conn:
            for table in tables:
                conn.execute(f"DELETE FROM {table}")
                logger.info(f"Cleared table: {table}")
        
        logger.info("All data cleared")


def seed_database(db_manager):
    """
    Convenience function to seed database
    
    Args:
        db_manager: EnhancedDatabaseManager instance
        
    Returns:
        True if successful, False otherwise
    """
    seeder = DataSeeder(db_manager)
    return seeder.seed_all()
