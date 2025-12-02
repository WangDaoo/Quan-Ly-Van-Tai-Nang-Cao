# Hướng Dẫn Kiểm Thử Thủ Công - Hệ Thống Quản Lý Vận Tải

## Mục Lục
1. [Kiểm Thử GUI Interactions](#1-kiểm-thử-gui-interactions)
2. [Kiểm Thử Keyboard Shortcuts](#2-kiểm-thử-keyboard-shortcuts)
3. [Kiểm Thử Responsive Design](#3-kiểm-thử-responsive-design)
4. [Kiểm Thử Error Scenarios](#4-kiểm-thử-error-scenarios)

---

## 1. Kiểm Thử GUI Interactions

### 1.1 Main Window
- [ ] **Khởi động ứng dụng**
  - Ứng dụng khởi động không lỗi
  - Menu bar hiển thị đầy đủ: File, Edit, View, Tools, Department, Help
  - Toolbar hiển thị các nút: New, Save, Import, Export, Filter, Settings
  - Status bar hiển thị thông tin records

- [ ] **Menu Actions**
  - File menu: New, Open, Save, Import, Export, Exit hoạt động
  - Edit menu: Undo, Redo, Copy, Paste, Delete hoạt động
  - View menu: Column visibility, Filters, Zoom hoạt động
  - Tools menu: Field Manager, Formula Builder, Push Conditions mở dialog
  - Department menu: Switch department, Department settings hoạt động
  - Help menu: User manual, About hiển thị thông tin

### 1.2 Input Form Widget
- [ ] **Form Display**
  - Form hiển thị đầy đủ các trường: mã chuyến, khách hàng, điểm đi, điểm đến, giá cả, khoán lương, chi phí khác, ghi chú
  - Các trường bắt buộc có dấu * hoặc visual indicator
  - Placeholder text hiển thị rõ ràng

- [ ] **Form Submission**
  - Nhập đầy đủ thông tin và nhấn "Thêm"
  - Mã chuyến tự động tạo (C001, C002, ...)
  - Dữ liệu được thêm vào bảng
  - Form được reset sau khi thêm thành công
  - Thông báo thành công hiển thị

- [ ] **Form Validation**
  - Để trống trường bắt buộc → Hiển thị lỗi
  - Nhập số âm vào giá cả → Hiển thị lỗi
  - Nhập ký tự đặc biệt không hợp lệ → Hiển thị lỗi
  - Visual feedback (màu đỏ) cho trường lỗi

### 1.3 Autocomplete
- [ ] **Khách Hàng Autocomplete**
  - Gõ vào trường khách hàng
  - Dropdown hiển thị gợi ý
  - Fuzzy search hoạt động (gõ "abc" tìm "ABC Company")
  - Click vào gợi ý → Điền vào form

- [ ] **Điểm Đi/Đến Autocomplete**
  - Gõ vào trường điểm đi/đến
  - Dropdown hiển thị gợi ý địa điểm
  - Gợi ý cập nhật real-time (300ms debounce)
  - Arrow keys để navigate dropdown
  - Enter để chọn gợi ý

### 1.4 Main Table Widget
- [ ] **Table Display**
  - Bảng hiển thị dữ liệu đầy đủ
  - Alternating row colors
  - Header có filter buttons
  - Scrollbar hoạt động

- [ ] **Cell Editing**
  - Double-click hoặc F2 để edit cell
  - Chỉnh sửa giá trị và nhấn Enter
  - Dữ liệu tự động lưu vào database
  - Cột mã chuyến không thể edit

- [ ] **Row Selection**
  - Click để chọn row
  - Ctrl+Click để multi-select
  - Shift+Click để select range
  - Selected rows có highlight

### 1.5 Excel-Like Features
- [ ] **Copy/Paste**
  - Select cells và Ctrl+C
  - Paste vào Excel → Format đúng
  - Copy từ Excel và Ctrl+V vào table
  - Ctrl+Shift+V paste as new rows

- [ ] **Context Menu**
  - Right-click trên row
  - Menu hiển thị: Insert row above/below, Duplicate, Delete, Clear, Copy/Paste
  - Các action hoạt động đúng

- [ ] **Column Management**
  - Right-click trên header
  - Show/Hide columns
  - Drag & drop để reorder columns
  - Resize columns
  - Freeze columns

### 1.6 Advanced Filtering
- [ ] **Filter Dialog**
  - Click filter button trên column header
  - Dialog hiển thị checkbox list
  - Search box trong dialog hoạt động
  - Select/Deselect all
  - Apply filter → Table cập nhật

- [ ] **Multi-Column Filtering**
  - Apply filter trên nhiều columns
  - Kết quả filter đúng (AND logic)
  - Clear filter hoạt động
  - Filter count hiển thị trên status bar

### 1.7 Suggestion Tabs
- [ ] **Filtered Results Tab**
  - Nhập thông tin vào form
  - Tab "Filtered" hiển thị kết quả phù hợp
  - Click vào row → Điền vào form

- [ ] **Company Price Tabs**
  - Tab A, B, C hiển thị bảng giá công ty
  - Bảng giá read-only
  - Filter đồng bộ với input form
  - Click vào row → Điền giá vào form

### 1.8 Employee Tab Widget
- [ ] **Department Tabs**
  - Tabs hiển thị: Sales, Processing, Accounting
  - Mỗi tab có form và table riêng
  - Switch tab → Dữ liệu độc lập
  - Tab state được lưu

### 1.9 Pagination Widget
- [ ] **Page Navigation**
  - Previous/Next buttons hoạt động
  - Jump to page hoạt động
  - Page size selection (10, 25, 50, 100)
  - Total records hiển thị đúng

### 1.10 Dialogs
- [ ] **Field Manager Dialog**
  - Tools → Field Manager
  - Dialog mở với danh sách fields
  - Add/Edit/Delete field hoạt động
  - Drag & drop để sắp xếp
  - Preview form real-time

- [ ] **Formula Builder Dialog**
  - Tools → Formula Builder
  - Formula editor với syntax highlighting
  - Field selector dropdown
  - Test formula với sample data
  - Validation hiển thị lỗi rõ ràng

- [ ] **Push Conditions Dialog**
  - Tools → Push Conditions
  - Condition builder UI
  - 12 operators available
  - AND/OR logic operators
  - Test conditions
  - Save/Load conditions

- [ ] **Workspace Manager Dialog**
  - Department → Workspace Manager
  - Create/Edit/Delete workspace
  - Switch workspace
  - Clone workspace
  - Export/Import configuration

- [ ] **Field Preset Dialog**
  - Tools → Field Presets
  - Preset list view
  - Load preset
  - Preview preset
  - Validate preset

- [ ] **Workflow History Dialog**
  - Tools → Workflow History
  - History list với filters
  - Filter by date range, department, status
  - Export history to Excel
  - Detail view

- [ ] **Statistics Dialog**
  - Tools → Statistics
  - Dashboard với metrics
  - Total records, departments, employees
  - Push statistics
  - Performance metrics
  - Export statistics

### 1.11 Import/Export
- [ ] **Excel Import**
  - File → Import
  - Select Excel file
  - Preview dialog hiển thị
  - Duplicate handling options: skip, overwrite, create new
  - Progress bar hiển thị
  - Error reporting với line numbers

- [ ] **Excel Export**
  - File → Export
  - Export options: all, filtered, selected
  - Formatting preserved
  - Auto-fit columns
  - Header styling
  - Progress bar hiển thị

---

## 2. Kiểm Thử Keyboard Shortcuts

### 2.1 Table Shortcuts
- [ ] **F2** - Edit cell
  - Select cell và nhấn F2
  - Cell vào edit mode
  
- [ ] **Enter** - Move down
  - Edit cell và nhấn Enter
  - Focus move xuống cell dưới

- [ ] **Tab** - Move right
  - Edit cell và nhấn Tab
  - Focus move sang cell phải

- [ ] **Shift+Tab** - Move left
  - Edit cell và nhấn Shift+Tab
  - Focus move sang cell trái

- [ ] **Ctrl+C** - Copy
  - Select cells và Ctrl+C
  - Data copied to clipboard

- [ ] **Ctrl+V** - Paste
  - Ctrl+V vào table
  - Data pasted correctly

- [ ] **Ctrl+Shift+V** - Paste as new rows
  - Ctrl+Shift+V
  - New rows created

- [ ] **Ctrl+D** - Duplicate row
  - Select row và Ctrl+D
  - Row duplicated

- [ ] **Delete** - Delete rows
  - Select rows và Delete
  - Confirmation dialog
  - Rows deleted

- [ ] **Ctrl+Plus** - Insert row below
  - Select row và Ctrl+Plus
  - New row inserted below

- [ ] **Ctrl+Shift+Plus** - Insert row above
  - Select row và Ctrl+Shift+Plus
  - New row inserted above

### 2.2 Application Shortcuts
- [ ] **Ctrl+N** - New record
- [ ] **Ctrl+S** - Save
- [ ] **Ctrl+O** - Open
- [ ] **Ctrl+Z** - Undo
- [ ] **Ctrl+Y** - Redo
- [ ] **Ctrl+F** - Find/Filter
- [ ] **Ctrl+Q** - Quit
- [ ] **F1** - Help
- [ ] **F5** - Refresh

---

## 3. Kiểm Thử Responsive Design

### 3.1 Window Resizing
- [ ] **Minimum Size**
  - Resize window xuống minimum
  - UI không bị vỡ layout
  - Scrollbars xuất hiện khi cần

- [ ] **Maximum Size**
  - Maximize window
  - UI scale đúng
  - Không có khoảng trống lớn

- [ ] **Normal Sizes**
  - Test với 1024x768
  - Test với 1366x768
  - Test với 1920x1080
  - Test với 2560x1440

### 3.2 Splitter Behavior
- [ ] **Horizontal Splitter**
  - Drag splitter giữa form và table
  - Resize smooth
  - Minimum size respected

- [ ] **Vertical Splitter**
  - Drag splitter giữa main area và suggestions
  - Resize smooth
  - Content reflow correctly

### 3.3 Component Scaling
- [ ] **Form Scaling**
  - Form fields scale với window size
  - Labels không bị truncate
  - Buttons accessible

- [ ] **Table Scaling**
  - Table fills available space
  - Columns auto-resize hoặc scrollbar
  - Header visible

- [ ] **Dialog Scaling**
  - Dialogs có size phù hợp
  - Content không bị cut off
  - Buttons accessible

### 3.4 Font Scaling
- [ ] **Normal Font (100%)**
  - Text readable
  - No overlap

- [ ] **Large Font (125%)**
  - UI scale correctly
  - No text truncation

- [ ] **Extra Large Font (150%)**
  - UI still usable
  - Scrollbars if needed

---

## 4. Kiểm Thử Error Scenarios

### 4.1 Database Errors
- [ ] **Database Locked**
  - Mở 2 instances cùng lúc
  - Thao tác đồng thời
  - Error message user-friendly
  - Recovery mechanism hoạt động

- [ ] **Database Corrupted**
  - Corrupt database file
  - Error message rõ ràng
  - Suggest backup restore

- [ ] **Database Missing**
  - Xóa database file
  - Auto-create new database
  - Seed data if needed

### 4.2 Validation Errors
- [ ] **Required Field Empty**
  - Submit form với required field empty
  - Error message: "Trường [field] là bắt buộc"
  - Field highlighted red

- [ ] **Invalid Number**
  - Nhập text vào number field
  - Error message: "Giá trị phải là số"
  - Field highlighted red

- [ ] **Invalid Email**
  - Nhập email không hợp lệ
  - Error message: "Email không hợp lệ"
  - Field highlighted red

- [ ] **Invalid Phone**
  - Nhập phone không hợp lệ
  - Error message: "Số điện thoại không hợp lệ"
  - Field highlighted red

- [ ] **Invalid URL**
  - Nhập URL không hợp lệ
  - Error message: "URL không hợp lệ"
  - Field highlighted red

### 4.3 Formula Errors
- [ ] **Syntax Error**
  - Nhập formula sai syntax: "[Field1] +"
  - Error message: "Lỗi cú pháp công thức"
  - Highlight vị trí lỗi

- [ ] **Invalid Field Reference**
  - Nhập formula với field không tồn tại: "[NonExistent] * 2"
  - Error message: "Trường [NonExistent] không tồn tại"

- [ ] **Division by Zero**
  - Formula: "[Field1] / [Field2]" với Field2 = 0
  - Error message: "Lỗi chia cho 0"
  - Result hiển thị "Error"

- [ ] **Circular Reference**
  - Field A formula references Field B
  - Field B formula references Field A
  - Error message: "Phát hiện tham chiếu vòng"

### 4.4 Import/Export Errors
- [ ] **Invalid File Format**
  - Import file không phải Excel
  - Error message: "File không đúng định dạng"

- [ ] **Empty File**
  - Import file Excel rỗng
  - Error message: "File không có dữ liệu"

- [ ] **Invalid Data**
  - Import file với dữ liệu không hợp lệ
  - Error report với line numbers
  - Option to skip invalid rows

- [ ] **File Not Found**
  - Import file đã bị xóa
  - Error message: "Không tìm thấy file"

- [ ] **Permission Denied**
  - Export vào folder không có quyền
  - Error message: "Không có quyền ghi file"
  - Suggest alternative location

### 4.5 Workflow Errors
- [ ] **Condition Evaluation Error**
  - Push condition với field không tồn tại
  - Error logged
  - Workflow skipped
  - User notified

- [ ] **Target Department Not Found**
  - Push to department không tồn tại
  - Error message: "Phòng ban đích không tồn tại"

- [ ] **Permission Denied**
  - Push without permission
  - Error message: "Không có quyền đẩy dữ liệu"

### 4.6 Network/Resource Errors
- [ ] **Out of Memory**
  - Load very large dataset (100,000+ records)
  - Pagination prevents crash
  - Warning message if needed

- [ ] **Disk Full**
  - Save when disk full
  - Error message: "Không đủ dung lượng đĩa"
  - Suggest cleanup

### 4.7 UI Errors
- [ ] **Dialog Already Open**
  - Open same dialog twice
  - Bring existing dialog to front
  - Don't create duplicate

- [ ] **Invalid State**
  - Perform action in invalid state
  - Error message or action disabled
  - No crash

### 4.8 Recovery Testing
- [ ] **Transaction Rollback**
  - Start transaction
  - Cause error mid-transaction
  - Verify rollback successful
  - Data integrity maintained

- [ ] **Auto-Save Recovery**
  - Make changes
  - Crash application (kill process)
  - Restart
  - Verify auto-save recovery

- [ ] **Backup Restore**
  - Corrupt database
  - Restore from backup
  - Verify data integrity

---

## Kết Quả Kiểm Thử

### Summary
- Total Test Cases: ___
- Passed: ___
- Failed: ___
- Blocked: ___
- Not Tested: ___

### Issues Found
| ID | Severity | Description | Status |
|----|----------|-------------|--------|
| 1  |          |             |        |
| 2  |          |             |        |

### Recommendations
1. 
2. 
3. 

---

## Ghi Chú
- Kiểm thử trên Windows 10/11
- Python 3.8+
- PyQt6 6.0+
- Screen resolution: 1920x1080
- Test date: ___________
- Tester: ___________
