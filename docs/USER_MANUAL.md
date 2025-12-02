# Hướng Dẫn Sử Dụng - Hệ Thống Quản Lý Vận Tải Toàn Diện

## Mục Lục

1. [Giới Thiệu](#giới-thiệu)
2. [Cài Đặt và Khởi Động](#cài-đặt-và-khởi-động)
3. [Giao Diện Chính](#giao-diện-chính)
4. [Quản Lý Chuyến Xe](#quản-lý-chuyến-xe)
5. [Tìm Kiếm và Lọc Dữ Liệu](#tìm-kiếm-và-lọc-dữ-liệu)
6. [Tra Cứu Bảng Giá](#tra-cứu-bảng-giá)
7. [Quản Lý Form Động](#quản-lý-form-động)
8. [Công Thức Tự Động](#công-thức-tự-động)
9. [Workflow Automation](#workflow-automation)
10. [Quản Lý Nhiều Phòng Ban](#quản-lý-nhiều-phòng-ban)
11. [Workspace Management](#workspace-management)
12. [Import/Export Excel](#importexport-excel)
13. [Thống Kê và Báo Cáo](#thống-kê-và-báo-cáo)
14. [Phím Tắt](#phím-tắt)
15. [Xử Lý Sự Cố](#xử-lý-sự-cố)

---

## Giới Thiệu

Hệ Thống Quản Lý Vận Tải Toàn Diện là ứng dụng desktop giúp quản lý thông tin chuyến xe, theo dõi chi phí, tra cứu bảng giá và tự động hóa quy trình nghiệp vụ cho các công ty vận tải.

### Tính Năng Chính

- ✅ Quản lý thông tin chuyến xe với form nhập liệu linh hoạt
- ✅ Autocomplete thông minh cho khách hàng, điểm đi, điểm đến
- ✅ Tìm kiếm và lọc nâng cao như Excel
- ✅ Tra cứu bảng giá của nhiều công ty
- ✅ Form động có thể tùy chỉnh không cần code
- ✅ Công thức tự động tính toán
- ✅ Workflow automation giữa các phòng ban
- ✅ Quản lý nhiều phòng ban và workspace
- ✅ Import/Export Excel với validation
- ✅ Thống kê và báo cáo chi tiết

### Yêu Cầu Hệ Thống

- **Hệ điều hành**: Windows 10/11, macOS 10.14+, Linux
- **RAM**: Tối thiểu 4GB (khuyến nghị 8GB)
- **Ổ cứng**: 500MB dung lượng trống
- **Màn hình**: Độ phân giải tối thiểu 1366x768

---

## Cài Đặt và Khởi Động

### Cài Đặt từ Source Code


```bash
# 1. Clone repository
git clone <repository-url>
cd transport-management-system

# 2. Cài đặt Python dependencies
pip install -r requirements.txt

# 3. Khởi tạo database
python test_database_setup.py

# 4. Chạy ứng dụng
python main.py
```

### Khởi Động Ứng Dụng

1. Mở terminal/command prompt
2. Di chuyển đến thư mục ứng dụng
3. Chạy lệnh: `python main.py`
4. Giao diện chính sẽ hiển thị sau vài giây

---

## Giao Diện Chính

### Cấu Trúc Giao Diện

```
┌────────────────────────────────────────────────────────────┐
│  Menu Bar: File | Edit | View | Tools | Department | Help  │
├────────────────────────────────────────────────────────────┤
│  Toolbar: [New] [Save] [Import] [Export] [Filter] [...]   │
├────────────────────────────────────────────────────────────┤
│  Department Tabs: [Sales] [Processing] [Accounting]       │
├────────────────────────────────────────────────────────────┤
│  ┌──────────────┬──────────────────────────────────────┐  │
│  │ Input Form   │  Main Table (Excel-like)             │  │
│  │              │                                      │  │
│  └──────────────┴──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Suggestion Tabs: [Filtered] [Company A] [B] [C]    │  │
│  └──────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────┤
│  Status Bar: Records: 150 | Filtered: 25 | Selected: 3    │
└────────────────────────────────────────────────────────────┘
```

### Các Thành Phần Chính

1. **Menu Bar**: Truy cập tất cả chức năng của hệ thống
2. **Toolbar**: Các thao tác thường dùng
3. **Department Tabs**: Chuyển đổi giữa các phòng ban
4. **Input Form**: Nhập liệu chuyến xe mới
5. **Main Table**: Hiển thị và chỉnh sửa dữ liệu
6. **Suggestion Tabs**: Tra cứu bảng giá và gợi ý
7. **Status Bar**: Hiển thị trạng thái và thống kê

---

## Quản Lý Chuyến Xe

### Thêm Chuyến Xe Mới

1. **Nhập thông tin vào form bên trái**:
   - Mã chuyến: Tự động tạo (C001, C002, ...)
   - Khách hàng: Bắt buộc (có autocomplete)
   - Điểm đi: Tùy chọn (có autocomplete)
   - Điểm đến: Tùy chọn (có autocomplete)
   - Giá cả: Bắt buộc
   - Khoán lương: Tùy chọn
   - Chi phí khác: Tùy chọn
   - Ghi chú: Tùy chọn

2. **Nhấn nút "Thêm" hoặc Ctrl+S**

3. **Kiểm tra kết quả**:
   - Chuyến xe mới xuất hiện trong bảng
   - Form được reset tự động
   - Status bar cập nhật số lượng records

### Chỉnh Sửa Chuyến Xe

**Cách 1: Chỉnh sửa trực tiếp trên bảng**

1. Double-click vào ô cần sửa (hoặc nhấn F2)
2. Nhập giá trị mới
3. Nhấn Enter hoặc Tab để lưu
4. Thay đổi được lưu tự động vào database

**Cách 2: Sử dụng context menu**
1. Click phải vào dòng cần sửa
2. Chọn "Edit Row"
3. Form sẽ được điền với dữ liệu hiện tại
4. Chỉnh sửa và nhấn "Update"

### Xóa Chuyến Xe

1. Chọn một hoặc nhiều dòng (Ctrl+Click hoặc Shift+Click)
2. Nhấn phím Delete hoặc click phải → "Delete Rows"
3. Xác nhận xóa trong dialog
4. Dữ liệu được xóa khỏi database

### Sao Chép Chuyến Xe

1. Click phải vào dòng cần sao chép
2. Chọn "Duplicate Row" (hoặc Ctrl+D)
3. Dòng mới được tạo với mã chuyến tự động

---

## Tìm Kiếm và Lọc Dữ Liệu

### Lọc Nhanh (Quick Filter)

1. Nhập giá trị vào các trường trong Input Form
2. Bảng suggestion "Filtered" tự động cập nhật
3. Debounce 300ms để tối ưu performance

### Lọc Nâng Cao (Advanced Filter)

1. **Mở Filter Dialog**:
   - Click vào icon filter ở header cột
   - Hoặc Menu → View → Advanced Filter

2. **Sử dụng Filter Dialog**:
   - ☑️ Checkbox list hiển thị tất cả giá trị unique
   - 🔍 Search box để tìm kiếm nhanh
   - ✅ Select All / ❌ Deselect All
   - Nhấn "Apply" để áp dụng filter

3. **Multi-Column Filtering**:
   - Có thể filter nhiều cột cùng lúc
   - Các filter được kết hợp với logic AND
   - Icon filter ở header sẽ đổi màu khi có filter active

4. **Xóa Filter**:
   - Click "Clear Filter" trong dialog
   - Hoặc Menu → View → Clear All Filters

### Tìm Kiếm Fuzzy

- Autocomplete hỗ trợ fuzzy search
- Ví dụ: Gõ "hcm" sẽ tìm "Hồ Chí Minh"
- Không phân biệt hoa thường
- Tìm kiếm theo substring

---

## Tra Cứu Bảng Giá

### Sử Dụng Suggestion Tabs

1. **Tab "Filtered"**: 
   - Hiển thị kết quả lọc từ Input Form
   - Tự động cập nhật khi nhập liệu

2. **Tab "Company A/B/C"**:
   - Hiển thị bảng giá của từng công ty
   - Read-only, không thể chỉnh sửa
   - Đồng bộ filter với Input Form

### Click to Fill

1. Click vào bất kỳ dòng nào trong Suggestion Tabs
2. Thông tin tự động điền vào Input Form:
   - Khách hàng
   - Điểm đi
   - Điểm đến
   - Giá cả
   - Khoán lương
3. Kiểm tra và điều chỉnh nếu cần
4. Nhấn "Thêm" để lưu

---

## Quản Lý Form Động

### Mở Field Manager

Menu → Tools → Field Manager (hoặc Ctrl+Shift+F)

### Thêm Field Mới

1. Nhấn "Add Field" trong Field Manager Dialog
2. Điền thông tin:

   - **Field Name**: Tên trường (unique)
   - **Display Name**: Tên hiển thị
   - **Field Type**: Chọn từ 10 loại
   - **Category**: Nhóm trường (optional)
   - **Required**: Bắt buộc hay không
   - **Default Value**: Giá trị mặc định
   - **Validation Rules**: Quy tắc validation
   - **Options**: Danh sách options (cho Dropdown)

3. Nhấn "Save"
4. Field mới xuất hiện trong form

### 10 Loại Field Hỗ Trợ

| Loại | Widget | Validation | Tính Năng |
|------|--------|------------|-----------|
| Text | QLineEdit | Max length, pattern | Autocomplete, placeholder |
| Number | QSpinBox | Min/max, decimals | Step increment, suffix/prefix |
| Currency | Custom QLineEdit | Positive only | Thousand separator, symbol |
| Date | QDateEdit | Date range | Calendar picker |
| Dropdown | QComboBox | Valid option | Fuzzy search, dynamic |
| Checkbox | QCheckBox | Boolean | Tri-state optional |
| Email | QLineEdit | RFC 5322 | Domain suggestions |
| Phone | QLineEdit | Phone pattern | Auto-formatting |
| TextArea | QTextEdit | Max length | Word count |
| URL | QLineEdit | URL format | Protocol auto-add |

### Sắp Xếp Fields

1. Trong Field Manager, sử dụng drag & drop
2. Kéo field lên/xuống để thay đổi thứ tự
3. Thứ tự mới được lưu tự động
4. Form được render lại theo thứ tự mới

### Xóa Field

1. Chọn field trong Field Manager
2. Nhấn "Delete"
3. Xác nhận xóa
4. Field bị xóa khỏi form và database config

### Preview Form

- Field Manager có panel preview real-time
- Xem form sẽ hiển thị như thế nào
- Test validation và behavior

---

## Công Thức Tự Động

### Mở Formula Builder

Menu → Tools → Formula Builder (hoặc Ctrl+Shift+M)

### Tạo Công Thức Mới

1. **Chọn Target Field**: Field sẽ chứa kết quả
2. **Nhập Formula Expression**:
   ```
   [Giá cả] - [Khoán lương] - [Chi phí khác]
   ```
3. **Sử dụng Field Selector**: Click để chèn field name
4. **Test Formula**: Nhập sample data để test
5. **Save Formula**

### Cú Pháp Công Thức

**Operators hỗ trợ**:
- `+` : Cộng
- `-` : Trừ
- `*` : Nhân
- `/` : Chia
- `()` : Dấu ngoặc đơn

**Field References**:
- Sử dụng `[Field_Name]` để tham chiếu field
- Ví dụ: `[Số lượng] * [Đơn giá]`

**Ví dụ công thức**:
```
Lợi nhuận = [Giá cả] - [Khoán lương] - [Chi phí khác]
Tổng tiền = [Số lượng] * [Đơn giá] * (1 - [Giảm giá] / 100)
Trung bình = ([Giá trị 1] + [Giá trị 2] + [Giá trị 3]) / 3
```

### Tự Động Tính Toán

- Công thức được tính tự động khi field phụ thuộc thay đổi
- Kết quả được format theo loại field (currency, number, ...)
- Lỗi được hiển thị rõ ràng (division by zero, invalid field, ...)

### Quản Lý Công Thức

- Xem danh sách tất cả công thức
- Edit công thức hiện có
- Deactivate/Activate công thức
- Delete công thức không dùng

---

## Workflow Automation

### Mở Push Conditions Dialog

Menu → Tools → Push Conditions (hoặc Ctrl+Shift+P)

### Cấu Hình Push Conditions

1. **Chọn Source Department**: Phòng ban nguồn
2. **Chọn Target Department**: Phòng ban đích
3. **Thêm Conditions**:

   - Field: Chọn field để kiểm tra
   - Operator: Chọn từ 12 operators
   - Value: Giá trị so sánh
   - Logic: AND hoặc OR (cho multi-condition)

4. **Test Conditions**: Test với sample data
5. **Save Configuration**

### 12 Operators Hỗ Trợ

| Operator | Mô Tả | Ví Dụ |
|----------|-------|-------|
| equals | Bằng chính xác | Trạng thái = "Hoàn thành" |
| not_equals | Không bằng | Trạng thái ≠ "Hủy" |
| contains | Chứa substring | Khách hàng chứa "Viettel" |
| not_contains | Không chứa | Ghi chú không chứa "test" |
| starts_with | Bắt đầu với | Mã chuyến bắt đầu "C" |
| ends_with | Kết thúc với | Email kết thúc "@gmail.com" |
| greater_than | Lớn hơn | Giá cả > 1000000 |
| less_than | Nhỏ hơn | Chi phí < 500000 |
| greater_or_equal | Lớn hơn hoặc bằng | Số lượng ≥ 10 |
| less_or_equal | Nhỏ hơn hoặc bằng | Giảm giá ≤ 20 |
| is_empty | Rỗng | Ghi chú rỗng |
| is_not_empty | Không rỗng | Khách hàng có giá trị |

### Logic Operators

**AND**: Tất cả conditions phải đúng
```
Trạng thái = "Hoàn thành" AND Giá cả > 1000000
```

**OR**: Ít nhất một condition đúng
```
Khách hàng = "Viettel" OR Khách hàng = "VNPT"
```

### Tự Động Push

- Khi record được lưu, hệ thống tự động kiểm tra conditions
- Nếu thỏa mãn, record được push sang department đích
- Workflow history được ghi log
- Notification hiển thị kết quả

### Manual Push

1. Chọn records trong bảng
2. Click phải → "Push to Department"
3. Chọn target department
4. Xác nhận push

### Xem Workflow History

Menu → Tools → Workflow History

- Xem tất cả push operations
- Filter theo date range, department, status
- Export history to Excel
- Xem chi tiết từng workflow entry

---

## Quản Lý Nhiều Phòng Ban

### Chuyển Đổi Department

1. Click vào Department Tab ở đầu window
2. Chọn department: Sales, Processing, Accounting
3. Form và table tự động chuyển đổi
4. Dữ liệu được cô lập giữa các department

### Cấu Hình Riêng Cho Department

Mỗi department có thể có:
- **Field configurations riêng**: Các trường khác nhau
- **Formulas riêng**: Công thức tính toán khác nhau
- **Validation rules riêng**: Quy tắc validation khác nhau
- **Workflow rules riêng**: Push conditions khác nhau

### Inter-Department Workflow

- Dữ liệu có thể được push giữa departments
- Sử dụng Push Conditions để tự động hóa
- Workflow history tracking đầy đủ
- Data transformation khi push

---

## Workspace Management

### Mở Workspace Manager

Menu → Department → Workspace Manager (hoặc Ctrl+Shift+W)

### Tạo Workspace Mới

1. Nhấn "New Workspace"
2. Nhập tên workspace
3. Chọn configuration:
   - Copy from existing workspace
   - Start with default configuration
4. Nhấn "Create"

### Switch Workspace

1. Mở Workspace Manager
2. Chọn workspace từ danh sách
3. Nhấn "Switch"
4. Giao diện reload với configuration mới

### Export/Import Workspace

**Export**:
1. Chọn workspace
2. Nhấn "Export"
3. Chọn file path
4. Configuration được lưu dạng JSON

**Import**:
1. Nhấn "Import"
2. Chọn JSON file
3. Nhập tên workspace mới
4. Nhấn "Import"

### Clone Workspace

1. Chọn workspace cần clone
2. Nhấn "Clone"
3. Nhập tên workspace mới
4. Workspace mới được tạo với cùng configuration

---

## Import/Export Excel

### Import từ Excel

1. **Mở Import Dialog**:
   Menu → File → Import (hoặc Ctrl+I)

2. **Chọn File**:
   - Click "Browse"
   - Chọn file Excel (.xlsx, .xls)
   - Nhấn "Open"

3. **Preview Data**:

   - Xem preview dữ liệu sẽ import
   - Kiểm tra column mapping
   - Xem validation errors (nếu có)

4. **Chọn Duplicate Handling**:
   - **Skip**: Bỏ qua records trùng
   - **Overwrite**: Ghi đè records cũ
   - **Create New**: Tạo records mới

5. **Import**:
   - Nhấn "Import"
   - Progress bar hiển thị tiến trình
   - Kết quả hiển thị: success/error count

### Export ra Excel

1. **Mở Export Dialog**:
   Menu → File → Export (hoặc Ctrl+E)

2. **Chọn Export Options**:
   - **All Records**: Export tất cả
   - **Filtered Records**: Export records đã filter
   - **Selected Rows**: Export rows đã chọn

3. **Chọn Columns**:
   - Select/Deselect columns cần export
   - Sắp xếp thứ tự columns

4. **Export Settings**:
   - ☑️ Include Headers
   - ☑️ Auto-fit Columns
   - ☑️ Apply Formatting
   - ☑️ Freeze Header Row

5. **Export**:
   - Chọn file path
   - Nhấn "Export"
   - File Excel được tạo

### Export/Import Presets

**Export Preset**:
1. Menu → Tools → Export Preset
2. Chọn loại preset:
   - Field Configurations
   - Formulas
   - Push Conditions
   - All (Complete preset)
3. Chọn file path
4. Preset được lưu dạng JSON

**Import Preset**:
1. Menu → Tools → Import Preset
2. Chọn JSON file
3. Preview preset
4. Validate preset
5. Nhấn "Import"

---

## Thống Kê và Báo Cáo

### Mở Statistics Dashboard

Menu → View → Statistics (hoặc Ctrl+Shift+S)

### Metrics Hiển Thị

**General Statistics**:
- Total Records: Tổng số records
- Active Records: Records đang active
- Department Count: Số phòng ban
- Employee Count: Số nhân viên
- Workspace Count: Số workspace

**Push Statistics**:
- Total Pushes: Tổng số push operations
- Success Rate: Tỷ lệ thành công
- Error Rate: Tỷ lệ lỗi
- Average Push Time: Thời gian push trung bình

**Performance Metrics**:
- Query Time: Thời gian query trung bình
- Memory Usage: Bộ nhớ đang sử dụng
- UI Response Time: Thời gian phản hồi UI
- Database Size: Kích thước database

### Export Statistics

1. Trong Statistics Dialog, nhấn "Export"
2. Chọn format: Excel hoặc PDF
3. Chọn file path
4. Statistics được export

---

## Phím Tắt

### Phím Tắt Chung

| Phím Tắt | Chức Năng |
|----------|-----------|
| Ctrl+N | New Record |
| Ctrl+S | Save Record |
| Ctrl+I | Import Excel |
| Ctrl+E | Export Excel |
| Ctrl+F | Focus Filter |
| Ctrl+Q | Quit Application |
| F1 | Help |
| F5 | Refresh |

### Phím Tắt Table

| Phím Tắt | Chức Năng |
|----------|-----------|
| F2 | Edit Cell |
| Enter | Move Down |
| Tab | Move Right |
| Shift+Tab | Move Left |
| Ctrl+C | Copy Cells |
| Ctrl+V | Paste Cells |
| Ctrl+Shift+V | Paste as New Rows |
| Ctrl+D | Duplicate Row |
| Delete | Delete Rows |
| Ctrl+Plus | Insert Row Below |
| Ctrl+Shift+Plus | Insert Row Above |
| Ctrl+A | Select All |
| Escape | Cancel Edit |

### Phím Tắt Tools

| Phím Tắt | Chức Năng |
|----------|-----------|
| Ctrl+Shift+F | Field Manager |
| Ctrl+Shift+M | Formula Builder |
| Ctrl+Shift+P | Push Conditions |
| Ctrl+Shift+W | Workspace Manager |
| Ctrl+Shift+S | Statistics |
| Ctrl+Shift+H | Workflow History |

### Phím Tắt Navigation

| Phím Tắt | Chức Năng |
|----------|-----------|
| Ctrl+1 | Switch to Sales |
| Ctrl+2 | Switch to Processing |
| Ctrl+3 | Switch to Accounting |
| Ctrl+Tab | Next Tab |
| Ctrl+Shift+Tab | Previous Tab |

---

## Xử Lý Sự Cố

### Ứng Dụng Không Khởi Động

**Nguyên nhân**: Thiếu dependencies

**Giải pháp**:
```bash
pip install -r requirements.txt
```

**Nguyên nhân**: Database không tồn tại

**Giải pháp**:
```bash
python test_database_setup.py
```

### Lỗi Import Excel

**Lỗi**: "Invalid file format"

**Giải pháp**:
- Kiểm tra file có đúng format .xlsx hoặc .xls
- Đảm bảo file không bị corrupt
- Thử mở file bằng Excel để kiểm tra

**Lỗi**: "Validation failed"

**Giải pháp**:
- Xem chi tiết lỗi trong preview dialog
- Sửa dữ liệu trong Excel file
- Import lại

### Công Thức Không Hoạt Động

**Lỗi**: "Invalid field reference"

**Giải pháp**:
- Kiểm tra field name có đúng không
- Sử dụng Field Selector để chèn field name
- Đảm bảo field tồn tại trong configuration

**Lỗi**: "Division by zero"

**Giải pháp**:
- Kiểm tra giá trị field mẫu số
- Thêm validation để đảm bảo không chia cho 0
- Sử dụng conditional formula (future feature)

### Performance Chậm

**Nguyên nhân**: Quá nhiều records

**Giải pháp**:
- Sử dụng pagination
- Áp dụng filter để giảm số records hiển thị
- Tăng page size trong settings

**Nguyên nhân**: Database không được optimize

**Giải pháp**:
```bash
# Chạy database optimization
python -c "from src.database.enhanced_db_manager import EnhancedDatabaseManager; db = EnhancedDatabaseManager(); db.optimize_database()"
```

### Lỗi Database

**Lỗi**: "Database is locked"

**Giải pháp**:
- Đóng tất cả instances của ứng dụng
- Restart ứng dụng
- Kiểm tra không có process nào đang giữ database

**Lỗi**: "Constraint violation"

**Giải pháp**:
- Kiểm tra dữ liệu nhập vào
- Đảm bảo không vi phạm unique constraints
- Kiểm tra foreign key references

### Lỗi Workflow

**Lỗi**: "Push failed"

**Giải pháp**:
- Xem workflow history để biết chi tiết lỗi
- Kiểm tra target department có tồn tại không
- Kiểm tra field mapping có đúng không
- Kiểm tra permissions (future feature)

### Backup và Restore

**Backup Database**:
```bash
# Manual backup
cp data/transport.db backups/transport_backup_$(date +%Y%m%d).db
```

**Restore Database**:
```bash
# Restore from backup
cp backups/transport_backup_YYYYMMDD.db data/transport.db
```

### Liên Hệ Hỗ Trợ

Nếu gặp vấn đề không thể tự giải quyết:

1. Kiểm tra log file: `logs/transportapp.log`
2. Tìm error message và stack trace
3. Liên hệ support team với thông tin:
   - Error message
   - Steps to reproduce
   - Log file
   - System information

---

## Phụ Lục

### Glossary

- **Record**: Một dòng dữ liệu trong bảng
- **Field**: Một cột/trường dữ liệu
- **Widget**: Thành phần giao diện (textbox, dropdown, ...)
- **Validation**: Kiểm tra tính hợp lệ của dữ liệu
- **Formula**: Công thức tính toán tự động
- **Push**: Đẩy dữ liệu sang department khác
- **Workspace**: Không gian làm việc riêng
- **Preset**: Cấu hình đã lưu

### Tips và Tricks

1. **Sử dụng Autocomplete**: Gõ vài ký tự đầu và chọn từ dropdown
2. **Copy từ Excel**: Ctrl+C trong Excel, Ctrl+V trong ứng dụng
3. **Multi-select**: Ctrl+Click để chọn nhiều rows
4. **Quick Filter**: Nhập vào form để filter nhanh
5. **Keyboard Navigation**: Sử dụng phím tắt để làm việc nhanh hơn
6. **Save Presets**: Lưu configuration để tái sử dụng
7. **Export Filtered**: Export chỉ dữ liệu đã filter
8. **Clone Workspace**: Tạo workspace mới từ workspace hiện tại

---

**Phiên bản**: 1.0  
**Ngày cập nhật**: 2024  
**Tác giả**: Transport Management System Team
