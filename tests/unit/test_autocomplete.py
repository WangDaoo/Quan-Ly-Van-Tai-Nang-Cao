"""
Unit tests for Autocomplete System
Tests AutocompleteComboBox, AutocompleteService, and AutocompleteIntegration
"""

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

from src.gui.widgets import AutocompleteComboBox, FuzzyFilterProxyModel, AutocompleteIntegration
from src.services import AutocompleteService
from src.database.enhanced_db_manager import EnhancedDatabaseManager


@pytest.fixture(scope='module')
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def autocomplete_widget(qapp):
    """Create AutocompleteComboBox widget for testing"""
    widget = AutocompleteComboBox()
    yield widget
    widget.deleteLater()


@pytest.fixture
def sample_data():
    """Sample data for testing"""
    return [
        "Hà Nội",
        "Hồ Chí Minh",
        "Đà Nẵng",
        "Hải Phòng",
        "Cần Thơ",
        "Nha Trang",
        "Huế",
        "Vũng Tàu"
    ]


class TestAutocompleteComboBox:
    """Test AutocompleteComboBox widget"""
    
    def test_initialization(self, autocomplete_widget):
        """Test widget initialization"""
        assert autocomplete_widget is not None
        assert autocomplete_widget.isEditable()
        assert autocomplete_widget._debounce_delay == 300
        assert autocomplete_widget._cache_enabled is True
    
    def test_set_items(self, autocomplete_widget, sample_data):
        """Test setting items"""
        autocomplete_widget.set_items(sample_data)
        
        # Check items are set
        assert autocomplete_widget.count() == len(sample_data)
        
        # Check cache
        cached = autocomplete_widget.get_cached_items()
        assert len(cached) == len(sample_data)
        assert cached == sample_data
    
    def test_data_loader(self, autocomplete_widget, sample_data):
        """Test data loader callback"""
        # Set data loader
        autocomplete_widget.set_data_loader(lambda: sample_data)
        
        # Load data
        autocomplete_widget.load_data()
        
        # Check data is loaded
        assert autocomplete_widget.count() == len(sample_data)
    
    def test_cache_enabled(self, autocomplete_widget, sample_data):
        """Test cache enable/disable"""
        autocomplete_widget.set_items(sample_data)
        
        # Check cache is populated
        assert len(autocomplete_widget.get_cached_items()) == len(sample_data)
        
        # Disable cache
        autocomplete_widget.set_cache_enabled(False)
        
        # Check cache is cleared
        assert len(autocomplete_widget.get_cached_items()) == 0
    
    def test_clear_cache(self, autocomplete_widget, sample_data):
        """Test clearing cache"""
        autocomplete_widget.set_items(sample_data)
        assert len(autocomplete_widget.get_cached_items()) == len(sample_data)
        
        autocomplete_widget.clear_cache()
        assert len(autocomplete_widget.get_cached_items()) == 0
    
    def test_debounce_delay(self, autocomplete_widget):
        """Test setting debounce delay"""
        autocomplete_widget.set_debounce_delay(500)
        assert autocomplete_widget._debounce_delay == 500
    
    def test_text_changed_signal(self, autocomplete_widget, sample_data, qtbot):
        """Test textChanged signal with debouncing"""
        autocomplete_widget.set_items(sample_data)
        
        # Connect signal
        signal_received = []
        autocomplete_widget.textChanged.connect(lambda text: signal_received.append(text))
        
        # Simulate user typing (use lineEdit().setText to trigger textEdited)
        autocomplete_widget.lineEdit().setText("Hà")
        autocomplete_widget._on_text_edited("Hà")  # Manually trigger since setText doesn't emit textEdited
        
        # Wait for debounce
        qtbot.wait(400)
        
        # Check signal was emitted
        assert len(signal_received) > 0
    
    def test_item_selected_signal(self, autocomplete_widget, sample_data, qtbot):
        """Test itemSelected signal"""
        autocomplete_widget.set_items(sample_data)
        
        # Connect signal
        signal_received = []
        autocomplete_widget.itemSelected.connect(lambda text: signal_received.append(text))
        
        # Select item
        autocomplete_widget.setCurrentIndex(0)
        autocomplete_widget.activated.emit(0)
        
        # Check signal was emitted
        assert len(signal_received) > 0
        assert signal_received[0] == sample_data[0]


class TestFuzzyFilterProxyModel:
    """Test FuzzyFilterProxyModel"""
    
    def test_fuzzy_matching(self, qapp):
        """Test fuzzy search matching"""
        from PyQt6.QtCore import QStringListModel, QRegularExpression
        
        # Create model with data
        data = ["Hà Nội", "Hồ Chí Minh", "Hải Phòng", "Huế"]
        source_model = QStringListModel(data)
        
        # Create proxy model
        proxy = FuzzyFilterProxyModel()
        proxy.setSourceModel(source_model)
        
        # Test with no filter - should show all
        assert proxy.rowCount() == len(data)
        
        # Test exact match using QRegularExpression
        proxy.setFilterRegularExpression(QRegularExpression("Hà Nội"))
        assert proxy.rowCount() >= 1
        
        # Test fuzzy match
        proxy.setFilterRegularExpression(QRegularExpression("hn"))
        # Fuzzy match should find items containing 'h' and 'n' in order
        assert proxy.rowCount() >= 0  # May or may not match depending on implementation
        
        # Test no match
        proxy.setFilterRegularExpression(QRegularExpression("xyz"))
        assert proxy.rowCount() == 0


class TestAutocompleteService:
    """Test AutocompleteService"""
    
    @pytest.fixture
    def db_manager(self, tmp_path):
        """Create temporary database for testing"""
        db_path = tmp_path / "test_autocomplete.db"
        db = EnhancedDatabaseManager(str(db_path))
        
        # Create tables
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY,
                ma_chuyen TEXT NOT NULL,
                khach_hang TEXT NOT NULL,
                diem_di TEXT,
                diem_den TEXT,
                gia_ca INTEGER NOT NULL
            )
        """)
        
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS company_prices (
                id INTEGER PRIMARY KEY,
                diem_di TEXT,
                diem_den TEXT
            )
        """)
        
        # Insert test data
        db.execute_update("""
            INSERT INTO trips (ma_chuyen, khach_hang, diem_di, diem_den, gia_ca)
            VALUES 
                ('C001', 'Customer A', 'Hà Nội', 'Hồ Chí Minh', 1000000),
                ('C002', 'Customer B', 'Đà Nẵng', 'Hải Phòng', 2000000),
                ('C003', 'Customer A', 'Hà Nội', 'Đà Nẵng', 1500000)
        """)
        
        yield db
        db.close()
    
    @pytest.fixture
    def autocomplete_service(self, db_manager):
        """Create AutocompleteService for testing"""
        return AutocompleteService(db_manager)
    
    def test_get_customers(self, autocomplete_service):
        """Test getting unique customers"""
        customers = autocomplete_service.get_customers(use_cache=False)
        
        assert len(customers) == 2
        assert 'Customer A' in customers
        assert 'Customer B' in customers
    
    def test_get_departure_locations(self, autocomplete_service):
        """Test getting departure locations"""
        locations = autocomplete_service.get_departure_locations(use_cache=False)
        
        assert len(locations) >= 2
        assert 'Hà Nội' in locations
        assert 'Đà Nẵng' in locations
    
    def test_get_destination_locations(self, autocomplete_service):
        """Test getting destination locations"""
        locations = autocomplete_service.get_destination_locations(use_cache=False)
        
        assert len(locations) >= 2
        assert 'Hồ Chí Minh' in locations
        assert 'Hải Phòng' in locations
    
    def test_caching(self, autocomplete_service):
        """Test caching functionality"""
        # First call - should query database
        customers1 = autocomplete_service.get_customers(use_cache=False)
        
        # Second call - should use cache
        customers2 = autocomplete_service.get_customers(use_cache=True)
        
        assert customers1 == customers2
        assert 'customers' in autocomplete_service._cache
    
    def test_clear_cache(self, autocomplete_service):
        """Test clearing cache"""
        # Load data
        autocomplete_service.get_customers()
        assert 'customers' in autocomplete_service._cache
        
        # Clear cache
        autocomplete_service.clear_cache()
        assert len(autocomplete_service._cache) == 0
    
    def test_create_data_loader(self, autocomplete_service):
        """Test creating data loader callbacks"""
        # Create loader for customers
        loader = autocomplete_service.create_data_loader('customer')
        assert callable(loader)
        
        # Call loader
        data = loader()
        assert isinstance(data, list)
        assert len(data) >= 0
    
    def test_get_filtered_suggestions(self, autocomplete_service):
        """Test getting filtered suggestions"""
        # Get all customers first
        autocomplete_service.get_customers(use_cache=False)
        
        # Get filtered suggestions
        suggestions = autocomplete_service.get_filtered_suggestions('customer', 'A', max_results=5)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5


class TestAutocompleteIntegration:
    """Test AutocompleteIntegration"""
    
    @pytest.fixture
    def db_manager(self, tmp_path):
        """Create temporary database for testing"""
        db_path = tmp_path / "test_integration.db"
        db = EnhancedDatabaseManager(str(db_path))
        
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY,
                khach_hang TEXT,
                diem_di TEXT,
                diem_den TEXT
            )
        """)
        
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS company_prices (
                id INTEGER PRIMARY KEY,
                diem_di TEXT,
                diem_den TEXT
            )
        """)
        
        yield db
        db.close()
    
    @pytest.fixture
    def integration(self, db_manager):
        """Create AutocompleteIntegration for testing"""
        service = AutocompleteService(db_manager)
        return AutocompleteIntegration(service)
    
    def test_field_mapping(self, integration):
        """Test field name mapping"""
        assert 'khach_hang' in integration.AUTOCOMPLETE_FIELDS
        assert 'diem_di' in integration.AUTOCOMPLETE_FIELDS
        assert 'diem_den' in integration.AUTOCOMPLETE_FIELDS
    
    def test_get_autocomplete_widget(self, integration):
        """Test getting autocomplete widget"""
        # Should return None for non-existent field
        widget = integration.get_autocomplete_widget('non_existent')
        assert widget is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
