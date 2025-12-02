"""
Workspace Manager Dialog - Dialog for managing employee workspaces
Provides create/edit/delete, switching, cloning, and export/import functionality
"""
import json
import logging
from typing import List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QMessageBox, QListWidget, QListWidgetItem, QGroupBox,
    QTextEdit, QFileDialog, QInputDialog, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.database.enhanced_db_manager import EnhancedDatabaseManager
from src.services.workspace_service import WorkspaceService
from src.models.employee_workspace import EmployeeWorkspace

logger = logging.getLogger(__name__)


class WorkspaceManagerDialog(QDialog):
    """
    Dialog for managing employee workspaces.
    
    Features:
    - Create/edit/delete workspace
    - Workspace switching functionality
    - Workspace clone
    - Export/import workspace configuration
    """
    
    workspace_switched = pyqtSignal(int)  # Emits workspace_id
    workspaces_changed = pyqtSignal()
    
    def __init__(self, db_manager: EnhancedDatabaseManager, employee_id: int, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.employee_id = employee_id
        self.workspace_service = WorkspaceService(db_manager)
        self.workspaces: List[EmployeeWorkspace] = []
        self.current_workspace: Optional[EmployeeWorkspace] = None
        
        self.setWindowTitle("Quản Lý Workspace")
        self.setMinimumSize(800, 500)
        self.setup_ui()
        self.load_workspaces()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Create splitter for list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Workspace list
        left_widget = self._create_workspace_list_section()
        splitter.addWidget(left_widget)
        
        # Right side - Details and configuration
        right_widget = self._create_details_section()
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("Xuất Cấu Hình")
        export_btn.clicked.connect(self.export_workspace)
        button_layout.addWidget(export_btn)
        
        import_btn = QPushButton("Nhập Cấu Hình")
        import_btn.clicked.connect(self.import_workspace)
        button_layout.addWidget(import_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _create_workspace_list_section(self):
        """Create the workspace list section"""
        widget = QGroupBox("Danh Sách Workspace")
        layout = QVBoxLayout(widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        create_btn = QPushButton("Tạo Mới")
        create_btn.clicked.connect(self.create_workspace)
        toolbar.addWidget(create_btn)
        
        self.clone_btn = QPushButton("Nhân Bản")
        self.clone_btn.clicked.connect(self.clone_workspace)
        self.clone_btn.setEnabled(False)
        toolbar.addWidget(self.clone_btn)
        
        self.delete_btn = QPushButton("Xóa")
        self.delete_btn.clicked.connect(self.delete_workspace)
        self.delete_btn.setEnabled(False)
        toolbar.addWidget(self.delete_btn)
        
        layout.addLayout(toolbar)
        
        # List widget
        self.workspace_list = QListWidget()
        self.workspace_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.workspace_list.itemDoubleClicked.connect(self.switch_workspace)
        layout.addWidget(self.workspace_list)
        
        # Switch button
        self.switch_btn = QPushButton("Chuyển Sang Workspace Này")
        self.switch_btn.clicked.connect(self.switch_workspace)
        self.switch_btn.setEnabled(False)
        layout.addWidget(self.switch_btn)
        
        return widget
    
    def _create_details_section(self):
        """Create the details section"""
        widget = QGroupBox("Chi Tiết Workspace")
        layout = QVBoxLayout(widget)
        
        # Workspace name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Tên:"))
        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        name_layout.addWidget(self.name_edit)
        
        self.edit_name_btn = QPushButton("Đổi Tên")
        self.edit_name_btn.clicked.connect(self.edit_workspace_name)
        self.edit_name_btn.setEnabled(False)
        name_layout.addWidget(self.edit_name_btn)
        
        layout.addLayout(name_layout)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Trạng Thái:"))
        self.status_label = QLabel("---")
        self.status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Configuration
        layout.addWidget(QLabel("Cấu Hình:"))
        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        layout.addWidget(self.config_text)
        
        # Edit config button
        self.edit_config_btn = QPushButton("Sửa Cấu Hình")
        self.edit_config_btn.clicked.connect(self.edit_configuration)
        self.edit_config_btn.setEnabled(False)
        layout.addWidget(self.edit_config_btn)
        
        return widget
    
    def load_workspaces(self):
        """Load workspaces from database"""
        try:
            self.workspaces = self.workspace_service.get_workspaces_for_employee(
                self.employee_id, active_only=False
            )
            self.refresh_list()
            
            # Try to get active workspace
            active_workspace = self.workspace_service.get_active_workspace(self.employee_id)
            if active_workspace:
                self.current_workspace = active_workspace
        except Exception as e:
            logger.error(f"Error loading workspaces: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải workspace: {str(e)}")
    
    def refresh_list(self):
        """Refresh the workspace list"""
        self.workspace_list.clear()
        
        for workspace in self.workspaces:
            item = QListWidgetItem(workspace.workspace_name)
            item.setData(Qt.ItemDataRole.UserRole, workspace.id)
            
            # Mark active workspace
            if self.current_workspace and workspace.id == self.current_workspace.id:
                item.setText(f"★ {workspace.workspace_name}")
                item.setForeground(Qt.GlobalColor.blue)
            
            # Mark inactive workspaces
            if not workspace.is_active:
                item.setForeground(Qt.GlobalColor.gray)
            
            self.workspace_list.addItem(item)
    
    def on_selection_changed(self):
        """Handle selection change"""
        has_selection = self.workspace_list.currentItem() is not None
        self.clone_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.switch_btn.setEnabled(has_selection)
        self.edit_name_btn.setEnabled(has_selection)
        self.edit_config_btn.setEnabled(has_selection)
        
        if has_selection:
            self.update_details()
    
    def update_details(self):
        """Update the details pane"""
        current_item = self.workspace_list.currentItem()
        if not current_item:
            self.name_edit.clear()
            self.status_label.setText("---")
            self.config_text.clear()
            return
        
        workspace_id = current_item.data(Qt.ItemDataRole.UserRole)
        workspace = next((w for w in self.workspaces if w.id == workspace_id), None)
        
        if workspace:
            self.name_edit.setText(workspace.workspace_name)
            
            if workspace.is_active:
                self.status_label.setText("Hoạt động")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.status_label.setText("Không hoạt động")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
            
            # Display configuration as formatted JSON
            if workspace.configuration:
                config_json = json.dumps(workspace.configuration, indent=2, ensure_ascii=False)
                self.config_text.setPlainText(config_json)
            else:
                self.config_text.setPlainText("{}")
    
    def create_workspace(self):
        """Create a new workspace"""
        name, ok = QInputDialog.getText(
            self,
            "Tạo Workspace Mới",
            "Tên workspace:"
        )
        
        if ok and name:
            try:
                workspace = self.workspace_service.create_workspace(
                    self.employee_id,
                    name.strip()
                )
                self.load_workspaces()
                self.workspaces_changed.emit()
                QMessageBox.information(self, "Thành Công", f"Đã tạo workspace '{name}'")
            except ValueError as e:
                QMessageBox.warning(self, "Lỗi", str(e))
            except Exception as e:
                logger.error(f"Error creating workspace: {e}")
                QMessageBox.critical(self, "Lỗi", f"Không thể tạo workspace: {str(e)}")
    
    def edit_workspace_name(self):
        """Edit workspace name"""
        current_item = self.workspace_list.currentItem()
        if not current_item:
            return
        
        workspace_id = current_item.data(Qt.ItemDataRole.UserRole)
        workspace = next((w for w in self.workspaces if w.id == workspace_id), None)
        
        if workspace:
            new_name, ok = QInputDialog.getText(
                self,
                "Đổi Tên Workspace",
                "Tên mới:",
                text=workspace.workspace_name
            )
            
            if ok and new_name:
                try:
                    self.workspace_service.update_workspace(
                        workspace_id,
                        workspace_name=new_name.strip()
                    )
                    self.load_workspaces()
                    self.workspaces_changed.emit()
                    QMessageBox.information(self, "Thành Công", "Đã đổi tên workspace")
                except ValueError as e:
                    QMessageBox.warning(self, "Lỗi", str(e))
                except Exception as e:
                    logger.error(f"Error renaming workspace: {e}")
                    QMessageBox.critical(self, "Lỗi", f"Không thể đổi tên: {str(e)}")
    
    def edit_configuration(self):
        """Edit workspace configuration"""
        current_item = self.workspace_list.currentItem()
        if not current_item:
            return
        
        workspace_id = current_item.data(Qt.ItemDataRole.UserRole)
        workspace = next((w for w in self.workspaces if w.id == workspace_id), None)
        
        if workspace:
            dialog = ConfigurationEditDialog(workspace, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                try:
                    new_config = dialog.get_configuration()
                    self.workspace_service.update_workspace(
                        workspace_id,
                        configuration=new_config
                    )
                    self.load_workspaces()
                    self.workspaces_changed.emit()
                    QMessageBox.information(self, "Thành Công", "Đã cập nhật cấu hình")
                except Exception as e:
                    logger.error(f"Error updating configuration: {e}")
                    QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật cấu hình: {str(e)}")
    
    def clone_workspace(self):
        """Clone selected workspace"""
        current_item = self.workspace_list.currentItem()
        if not current_item:
            return
        
        workspace_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        new_name, ok = QInputDialog.getText(
            self,
            "Nhân Bản Workspace",
            "Tên cho workspace mới:"
        )
        
        if ok and new_name:
            try:
                cloned = self.workspace_service.clone_workspace(workspace_id, new_name.strip())
                self.load_workspaces()
                self.workspaces_changed.emit()
                QMessageBox.information(self, "Thành Công", f"Đã nhân bản workspace thành '{new_name}'")
            except ValueError as e:
                QMessageBox.warning(self, "Lỗi", str(e))
            except Exception as e:
                logger.error(f"Error cloning workspace: {e}")
                QMessageBox.critical(self, "Lỗi", f"Không thể nhân bản workspace: {str(e)}")
    
    def delete_workspace(self):
        """Delete selected workspace"""
        current_item = self.workspace_list.currentItem()
        if not current_item:
            return
        
        workspace_id = current_item.data(Qt.ItemDataRole.UserRole)
        workspace = next((w for w in self.workspaces if w.id == workspace_id), None)
        
        if workspace:
            reply = QMessageBox.question(
                self,
                "Xác Nhận Xóa",
                f"Bạn có chắc muốn xóa workspace '{workspace.workspace_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self.workspace_service.delete_workspace(workspace_id)
                    self.load_workspaces()
                    self.workspaces_changed.emit()
                    QMessageBox.information(self, "Thành Công", "Đã xóa workspace")
                except Exception as e:
                    logger.error(f"Error deleting workspace: {e}")
                    QMessageBox.critical(self, "Lỗi", f"Không thể xóa workspace: {str(e)}")
    
    def switch_workspace(self):
        """Switch to selected workspace"""
        current_item = self.workspace_list.currentItem()
        if not current_item:
            return
        
        workspace_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        try:
            self.workspace_service.switch_workspace(self.employee_id, workspace_id)
            self.current_workspace = self.workspace_service.get_workspace_by_id(workspace_id)
            self.refresh_list()
            self.workspace_switched.emit(workspace_id)
            QMessageBox.information(self, "Thành Công", "Đã chuyển workspace")
        except Exception as e:
            logger.error(f"Error switching workspace: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể chuyển workspace: {str(e)}")
    
    def export_workspace(self):
        """Export workspace configuration to JSON file"""
        current_item = self.workspace_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn workspace để xuất")
            return
        
        workspace_id = current_item.data(Qt.ItemDataRole.UserRole)
        workspace = next((w for w in self.workspaces if w.id == workspace_id), None)
        
        if workspace:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Xuất Cấu Hình Workspace",
                f"{workspace.workspace_name}.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                try:
                    config_data = {
                        'workspace_name': workspace.workspace_name,
                        'configuration': workspace.configuration
                    }
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, ensure_ascii=False, indent=2)
                    
                    QMessageBox.information(self, "Thành Công", "Đã xuất cấu hình workspace")
                except Exception as e:
                    logger.error(f"Error exporting workspace: {e}")
                    QMessageBox.critical(self, "Lỗi", f"Không thể xuất cấu hình: {str(e)}")
    
    def import_workspace(self):
        """Import workspace configuration from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Nhập Cấu Hình Workspace",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                workspace_name = config_data.get('workspace_name', 'Imported Workspace')
                configuration = config_data.get('configuration', {})
                
                # Ask for name
                name, ok = QInputDialog.getText(
                    self,
                    "Nhập Workspace",
                    "Tên workspace:",
                    text=workspace_name
                )
                
                if ok and name:
                    workspace = self.workspace_service.create_workspace(
                        self.employee_id,
                        name.strip(),
                        configuration
                    )
                    self.load_workspaces()
                    self.workspaces_changed.emit()
                    QMessageBox.information(self, "Thành Công", "Đã nhập workspace")
            except ValueError as e:
                QMessageBox.warning(self, "Lỗi", str(e))
            except Exception as e:
                logger.error(f"Error importing workspace: {e}")
                QMessageBox.critical(self, "Lỗi", f"Không thể nhập cấu hình: {str(e)}")


class ConfigurationEditDialog(QDialog):
    """Dialog for editing workspace configuration"""
    
    def __init__(self, workspace: EmployeeWorkspace, parent=None):
        super().__init__(parent)
        self.workspace = workspace
        
        self.setWindowTitle("Sửa Cấu Hình Workspace")
        self.setMinimumSize(600, 400)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Cấu hình (JSON format):"))
        
        self.config_edit = QTextEdit()
        if self.workspace.configuration:
            config_json = json.dumps(self.workspace.configuration, indent=2, ensure_ascii=False)
            self.config_edit.setPlainText(config_json)
        else:
            self.config_edit.setPlainText("{}")
        
        layout.addWidget(self.config_edit)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def validate_and_accept(self):
        """Validate JSON and accept"""
        try:
            config_text = self.config_edit.toPlainText().strip()
            json.loads(config_text)  # Validate JSON
            self.accept()
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Lỗi", f"JSON không hợp lệ: {str(e)}")
    
    def get_configuration(self):
        """Get the configuration as dictionary"""
        config_text = self.config_edit.toPlainText().strip()
        return json.loads(config_text)
