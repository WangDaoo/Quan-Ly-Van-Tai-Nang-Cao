"""
Pytest configuration and fixtures
"""

import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit the app as it may be used by other tests


@pytest.fixture
def qtbot(qapp, qtbot):
    """Provide qtbot fixture with QApplication"""
    return qtbot
