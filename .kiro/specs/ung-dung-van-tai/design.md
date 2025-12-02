# Tài Liệu Thiết Kế - Ứng Dụng Quản Lý Vận Tải

## Tổng Quan

Ứng dụng quản lý vận tải được thiết kế như một ứng dụng desktop Python sử dụng PyQt6 để cung cấp giao diện người dùng hiện đại và mạnh mẽ. Hệ thống áp dụng kiến trúc Model-View-Controller (MVC) để đảm bảo tính module hóa và dễ bảo trì.

## Kiến Trúc Hệ Thống

### Kiến Trúc Tổng Thể
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Presentation  │    │    Business     │    │      Data       │
│     Layer       │◄──►│     Logic       │◄──►│     Layer       │
│   (PyQt6 GUI)   │    │   (Services)    │    │   (SQLite DB)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Công Nghệ Sử Dụng
- **GUI Framework**: PyQt6 - Giao diện mạnh mẽ với QTableWidget hỗ trợ copy/paste
- **Cơ sở dữ liệu**: SQLite3 - Nhẹ, không cần cài đặt server
- **Xử lý Excel**: pandas + openpyxl - Import/export dữ liệu
- **Validation**: Pydantic - Xác thực dữ liệu đầu vào
- **Logging**: Python logging - Ghi log hệ thống

## Thành Phần và Giao Diện

### Cấu Trúc Giao Diện Chính
```
┌─────────────────────────────────────────────────────────────┐
│                    Main Window (1200x800)                   │
├─────────────────┬───────────────────────────────────────────┤
│                 │              Bảng Chính                   │
│   Form Nhập     │           (QTableWidget)                  │
│     Liệu        │                                           │
│  (QGroupBox)    ├───────────────────────────────────────────┤
│                 │            Bảng Gợi Ý                    │
│                 │          (QTabWidget)                     │
└─────────────────┴───────────────────────────────────────────┘
```##
# Widget Components

#### 1. Form Nhập Liệu (InputFormWidget)
- **QLineEdit** cho mã chuyến (readonly)
- **QComboBox** với autocomplete cho khách hàng, điểm đi, điểm đến
- **QSpinBox** cho các trường số (giá cả, khoán lương, chi phí)
- **QTextEdit** cho ghi chú
- **QPushButton** để thêm chuyến mới

#### 2. Bảng Chính (MainTableWidget)
- **QTableWidget** với 8 cột
- Hỗ trợ chỉnh sửa trực tiếp (trừ cột mã chuyến)
- Custom delegate cho định dạng số tiền
- Context menu cho copy/paste/delete

#### 3. Bảng Gợi Ý (SuggestionTabWidget)
- **QTabWidget** với 4 tab:
  - Tab "Lọc Chuyến": Hiển thị kết quả lọc từ bảng chính
  - Tab "Giá Cty A/B/C": Hiển thị bảng giá các công ty
- Mỗi tab chứa **QTableWidget** ở chế độ readonly

## Mô Hình Dữ Liệu

### Database Schema
```sql
-- Bảng chuyến xe
CREATE TABLE trips (
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng giá công ty
CREATE TABLE company_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name VARCHAR(100) NOT NULL,
    khach_hang VARCHAR(255) NOT NULL,
    diem_di VARCHAR(255) NOT NULL,
    diem_den VARCHAR(255) NOT NULL,
    gia_ca INTEGER NOT NULL,
    khoan_luong INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index để tối ưu tìm kiếm
CREATE INDEX idx_trips_khach_hang ON trips(khach_hang);
CREATE INDEX idx_trips_diem ON trips(diem_di, diem_den);
CREATE INDEX idx_company_prices_route ON company_prices(company_name, diem_di, diem_den);
```

### Data Models (Pydantic)
```python
class Trip(BaseModel):
    id: Optional[int] = None
    ma_chuyen: str
    khach_hang: str
    diem_di: Optional[str] = ""
    diem_den: Optional[str] = ""
    gia_ca: int
    khoan_luong: int = 0
    chi_phi_khac: int = 0
    ghi_chu: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CompanyPrice(BaseModel):
    id: Optional[int] = None
    company_name: str
    khach_hang: str
    diem_di: str
    diem_den: str
    gia_ca: int
    khoan_luong: int
```## Xử 
Lý Lỗi

### Validation Rules
- **Khách hàng**: Bắt buộc, tối đa 255 ký tự
- **Giá cả**: Bắt buộc, số nguyên dương
- **Mã chuyến**: Tự động tạo, định dạng C001-C999
- **Số tiền**: Chỉ chấp nhận số nguyên, hiển thị với dấu phân cách

### Error Handling Strategy
```python
class ValidationError(Exception):
    """Lỗi validation dữ liệu đầu vào"""
    pass

class DatabaseError(Exception):
    """Lỗi cơ sở dữ liệu"""
    pass

class ExportError(Exception):
    """Lỗi export/import dữ liệu"""
    pass
```

### User Feedback
- **QMessageBox** cho thông báo lỗi và xác nhận
- **QStatusBar** hiển thị trạng thái thao tác
- **QProgressBar** cho các thao tác dài (import/export)
- **Tooltip** hướng dẫn sử dụng các trường

## Chiến Lược Testing

### Unit Testing
- Test các model và validation rules
- Test database operations (CRUD)
- Test business logic trong services
- Mock external dependencies (file I/O, database)

### Integration Testing  
- Test tương tác giữa GUI và business logic
- Test import/export Excel workflow
- Test autocomplete và filtering functionality

### UI Testing
- Manual testing cho user experience
- Test keyboard shortcuts và navigation
- Test responsive layout với các kích thước cửa sổ khác nhau

### Test Data
- Tạo fixture data cho development và testing
- Sample data bao gồm:
  - 50+ chuyến xe mẫu với đa dạng khách hàng và tuyến đường
  - Bảng giá của 3 công ty với 20+ tuyến phổ biến
  - Edge cases: tên dài, ký tự đặc biệt, số tiền lớn

## Performance Considerations

### Database Optimization
- Index trên các cột thường xuyên tìm kiếm
- Pagination cho bảng lớn (>1000 records)
- Lazy loading cho autocomplete suggestions

### UI Responsiveness
- Background threads cho database operations
- Debounce cho real-time filtering (300ms delay)
- Virtual scrolling cho bảng lớn
- Cache autocomplete data trong memory

### Memory Management
- Giới hạn số dòng hiển thị trong bảng (max 1000)
- Clear unused QTableWidget items
- Proper cleanup khi đóng ứng dụng