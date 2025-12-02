# Tài Liệu Yêu Cầu - Hệ Thống Quản Lý Vận Tải Toàn Diện

## Giới Thiệu

Hệ Thống Quản Lý Vận Tải Toàn Diện là một ứng dụng desktop được phát triển bằng Python/PyQt6, cung cấp giải pháp toàn diện cho việc quản lý thông tin chuyến xe, theo dõi chi phí, tra cứu bảng giá và tự động hóa quy trình nghiệp vụ cho các công ty vận tải. Hệ thống hỗ trợ quản lý form động, công thức tự động, workflow automation và các tính năng Excel-like hiện đại.

## Thuật Ngữ

- **Hệ_Thống**: Ứng dụng Quản Lý Vận Tải Toàn Diện
- **Người_Dùng**: Nhân viên sử dụng hệ thống
- **Chuyến_Xe**: Một lần vận chuyển hàng hóa
- **Form_Động**: Form được tạo tự động từ cấu hình
- **Trường_Dữ_Liệu**: Một field trong form nhập liệu
- **Công_Thức**: Biểu thức tính toán tự động
- **Điều_Kiện_Đẩy**: Quy tắc tự động chuyển dữ liệu
- **Phòng_Ban**: Department trong tổ chức
- **Workspace**: Không gian làm việc của nhân viên
- **Bảng_Giá**: Danh sách giá cước vận chuyển
- **Validation**: Xác thực dữ liệu đầu vào
- **Widget**: Thành phần giao diện người dùng

## Yêu Cầu

### Yêu Cầu 1: Quản Lý Chuyến Xe Cơ Bản

**Câu Chuyện Người Dùng:** Là một nhân viên điều hành, tôi muốn nhập và quản lý thông tin chuyến xe một cách nhanh chóng và chính xác, để theo dõi tất cả các chuyến vận tải hiệu quả.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL hiển thị form nhập liệu với các trường: mã chuyến, khách hàng, điểm đi, điểm đến, giá cả, khoán lương, chi phí khác, ghi chú
2. WHEN Người_Dùng nhập thông tin và nhấn nút thêm, THE Hệ_Thống SHALL tự động tạo mã chuyến theo định dạng C001, C002, C003
3. THE Hệ_Thống SHALL xác thực dữ liệu với khách hàng và giá cả là bắt buộc
4. THE Hệ_Thống SHALL hiển thị bảng dữ liệu với khả năng chỉnh sửa trực tiếp trừ cột mã chuyến
5. WHEN dữ liệu được thay đổi trên bảng, THE Hệ_Thống SHALL tự động lưu thay đổi vào cơ sở dữ liệu

### Yêu Cầu 2: Autocomplete và Gợi Ý Thông Minh

**Câu Chuyện Người Dùng:** Là một nhân viên điều hành, tôi muốn có gợi ý tự động khi nhập liệu, để tăng tốc độ nhập và giảm thiểu sai sót.

#### Tiêu Chí Chấp Nhận

1. WHEN Người_Dùng gõ vào trường khách hàng, THE Hệ_Thống SHALL hiển thị dropdown gợi ý các khách hàng đã có
2. WHEN Người_Dùng gõ vào trường điểm đi hoặc điểm đến, THE Hệ_Thống SHALL hiển thị dropdown gợi ý các địa điểm đã có
3. THE Hệ_Thống SHALL hỗ trợ fuzzy search trong dropdown gợi ý
4. THE Hệ_Thống SHALL cập nhật gợi ý theo thời gian thực với debounce 300ms
5. WHEN Người_Dùng click vào gợi ý, THE Hệ_Thống SHALL điền thông tin vào form nhập liệu

### Yêu Cầu 3: Tìm Kiếm và Lọc Nâng Cao

**Câu Chuyện Người Dùng:** Là một nhân viên điều hành, tôi muốn tìm kiếm và lọc dữ liệu theo nhiều tiêu chí như Excel, để nhanh chóng tìm thông tin cần thiết.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL cung cấp advanced filtering với checkbox filter dialog cho mỗi cột
2. THE Hệ_Thống SHALL hỗ trợ lọc đồng thời theo nhiều cột
3. THE Hệ_Thống SHALL cung cấp search box trong filter dialog
4. THE Hệ_Thống SHALL hiển thị số lượng items được chọn trong filter
5. WHEN Người_Dùng áp dụng filter, THE Hệ_Thống SHALL cập nhật bảng theo thời gian thực

### Yêu Cầu 4: Quản Lý Form Động

**Câu Chuyện Người Dùng:** Là một quản trị viên, tôi muốn tạo và quản lý form nhập liệu mà không cần viết code, để dễ dàng thay đổi theo yêu cầu nghiệp vụ.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL hỗ trợ 10 loại trường: Text, Number, Currency, Date, Dropdown, Checkbox, Email, Phone, TextArea, URL
2. THE Hệ_Thống SHALL tự động tạo widget phù hợp cho mỗi loại trường
3. THE Hệ_Thống SHALL cung cấp dialog quản lý cấu hình trường với thêm, sửa, xóa
4. THE Hệ_Thống SHALL hỗ trợ drag and drop để sắp xếp thứ tự trường
5. THE Hệ_Thống SHALL cung cấp preview form real-time khi cấu hình

### Yêu Cầu 5: Hệ Thống Validation Mạnh Mẽ

**Câu Chuyện Người Dùng:** Là một nhân viên nhập liệu, tôi muốn hệ thống kiểm tra dữ liệu ngay khi nhập, để phát hiện lỗi sớm và đảm bảo chất lượng dữ liệu.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL hỗ trợ 6 loại validation: Required, Number Only, Text Only, No Special Characters, Email Format, Pattern Matching
2. THE Hệ_Thống SHALL thực hiện validation theo thời gian thực khi Người_Dùng nhập
3. THE Hệ_Thống SHALL hiển thị visual feedback với màu đỏ cho trường lỗi
4. THE Hệ_Thống SHALL hiển thị custom error message cho mỗi loại lỗi
5. THE Hệ_Thống SHALL hỗ trợ cross-field validation giữa nhiều trường

### Yêu Cầu 6: Công Thức Tự Động

**Câu Chuyện Người Dùng:** Là một nhân viên kế toán, tôi muốn hệ thống tự động tính toán các trường theo công thức, để giảm thiểu nhập liệu thủ công và sai sót.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL hỗ trợ công thức với 4 phép toán: cộng, trừ, nhân, chia
2. THE Hệ_Thống SHALL hỗ trợ dấu ngoặc đơn trong công thức
3. WHEN giá trị trường thay đổi, THE Hệ_Thống SHALL tự động tính lại công thức
4. THE Hệ_Thống SHALL cung cấp formula builder dialog để tạo và test công thức
5. THE Hệ_Thống SHALL validate syntax công thức và hiển thị lỗi rõ ràng

### Yêu Cầu 7: Workflow Automation

**Câu Chuyện Người Dùng:** Là một quản lý, tôi muốn tự động hóa quy trình đẩy dữ liệu giữa các phòng ban theo điều kiện, để tăng hiệu quả và giảm thao tác thủ công.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL hỗ trợ 12 operators: equals, not_equals, contains, not_contains, starts_with, ends_with, greater_than, less_than, greater_or_equal, less_or_equal, is_empty, is_not_empty
2. THE Hệ_Thống SHALL hỗ trợ logic operators AND và OR cho multi-condition
3. THE Hệ_Thống SHALL cung cấp push conditions dialog để cấu hình điều kiện
4. WHEN điều kiện được thỏa mãn, THE Hệ_Thống SHALL tự động đẩy dữ liệu sang phòng ban đích
5. THE Hệ_Thống SHALL lưu workflow history với timestamp, user, status

### Yêu Cầu 8: Quản Lý Nhiều Phòng Ban

**Câu Chuyện Người Dùng:** Là một nhân viên, tôi muốn làm việc với dữ liệu của phòng ban mình mà không ảnh hưởng đến phòng ban khác, để đảm bảo tính độc lập và bảo mật.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL hỗ trợ nhiều phòng ban với tab riêng biệt
2. THE Hệ_Thống SHALL cung cấp form và table độc lập cho mỗi phòng ban
3. THE Hệ_Thống SHALL cho phép cấu hình field riêng cho mỗi phòng ban
4. THE Hệ_Thống SHALL cho phép cấu hình công thức riêng cho mỗi phòng ban
5. THE Hệ_Thống SHALL hỗ trợ inter-department workflow với push conditions

### Yêu Cầu 9: Workspace Management

**Câu Chuyện Người Dùng:** Là một nhân viên, tôi muốn có nhiều workspace để tổ chức công việc khác nhau, để dễ dàng chuyển đổi giữa các dự án hoặc nhiệm vụ.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL cho phép tạo nhiều workspace cho mỗi nhân viên
2. THE Hệ_Thống SHALL cung cấp workspace manager dialog để quản lý workspace
3. THE Hệ_Thống SHALL hỗ trợ switch workspace nhanh chóng
4. THE Hệ_Thống SHALL cô lập dữ liệu giữa các workspace
5. THE Hệ_Thống SHALL cho phép export và import workspace configuration

### Yêu Cầu 10: Excel-Like Features

**Câu Chuyện Người Dùng:** Là một người dùng quen với Excel, tôi muốn sử dụng các tính năng quen thuộc như copy/paste, column management, keyboard shortcuts, để làm việc hiệu quả hơn.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL hỗ trợ copy cells với Ctrl+C và paste với Ctrl+V
2. THE Hệ_Thống SHALL hỗ trợ column visibility, reordering, freezing, auto-resize
3. THE Hệ_Thống SHALL cung cấp context menu với các thao tác: insert row, duplicate row, delete rows, clear content
4. THE Hệ_Thống SHALL hỗ trợ keyboard shortcuts: F2 edit, Enter move down, Tab move right, Delete xóa
5. THE Hệ_Thống SHALL hỗ trợ multi-select với Ctrl+Click và Shift+Click

### Yêu Cầu 11: Import/Export Excel

**Câu Chuyện Người Dùng:** Là một nhân viên, tôi muốn import dữ liệu từ Excel và export kết quả ra Excel, để tích hợp với các công cụ khác và chia sẻ dữ liệu.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL hỗ trợ import dữ liệu từ file Excel với preview trước khi import
2. THE Hệ_Thống SHALL cung cấp 3 options xử lý duplicate: skip, overwrite, create new
3. THE Hệ_Thống SHALL validate dữ liệu khi import và báo lỗi rõ ràng
4. THE Hệ_Thống SHALL hỗ trợ export all records, filtered records, hoặc selected rows
5. THE Hệ_Thống SHALL preserve formatting khi export ra Excel

### Yêu Cầu 12: Export/Import Presets

**Câu Chuyện Người Dùng:** Là một quản trị viên, tôi muốn lưu và chia sẻ cấu hình hệ thống, để dễ dàng triển khai cho nhiều người dùng hoặc backup cấu hình.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL cho phép export field configurations ra file JSON
2. THE Hệ_Thống SHALL cho phép export formulas ra file JSON
3. THE Hệ_Thống SHALL cho phép export push conditions ra file JSON
4. THE Hệ_Thống SHALL cung cấp preset dialog để quản lý và load presets
5. THE Hệ_Thống SHALL validate preset file trước khi import

### Yêu Cầu 13: Statistics và Reporting

**Câu Chuyện Người Dùng:** Là một quản lý, tôi muốn xem thống kê tổng quan về hệ thống, để đánh giá hiệu quả hoạt động và đưa ra quyết định.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL hiển thị statistics dashboard với total records, active records, department count
2. THE Hệ_Thống SHALL hiển thị push statistics với success rate và error rate
3. THE Hệ_Thống SHALL cung cấp workflow history dialog để xem lịch sử đẩy dữ liệu
4. THE Hệ_Thống SHALL hiển thị performance metrics: query time, memory usage, UI response time
5. THE Hệ_Thống SHALL cung cấp export statistics ra Excel

### Yêu Cầu 14: Tra Cứu Bảng Giá

**Câu Chuyện Người Dùng:** Là một nhân viên kinh doanh, tôi muốn tra cứu bảng giá của các công ty khác nhau, để so sánh và đưa ra quyết định giá cả phù hợp.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL hiển thị bảng giá của 3 công ty trong các tab riêng biệt
2. THE Hệ_Thống SHALL cho phép lọc bảng giá theo khách hàng, điểm đi, điểm đến
3. WHEN Người_Dùng click vào dòng trong bảng giá, THE Hệ_Thống SHALL điền thông tin vào form
4. THE Hệ_Thống SHALL hiển thị bảng giá ở chế độ read-only
5. THE Hệ_Thống SHALL đồng bộ filter bảng giá với các trường nhập liệu

### Yêu Cầu 15: Giao Diện Người Dùng Hiện Đại

**Câu Chuyện Người Dùng:** Là một người dùng, tôi muốn giao diện thân thiện, responsive và dễ sử dụng, để làm việc hiệu quả mà không cần đào tạo phức tạp.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL sử dụng layout responsive thích ứng với kích thước cửa sổ
2. THE Hệ_Thống SHALL sử dụng màu sắc và font chữ dễ đọc, thân thiện với mắt
3. THE Hệ_Thống SHALL cung cấp status bar hiển thị trạng thái thao tác
4. THE Hệ_Thống SHALL cung cấp toolbar với các thao tác thường dùng
5. THE Hệ_Thống SHALL hiển thị loading indicator cho các thao tác dài

### Yêu Cầu 16: Database và Performance

**Câu Chuyện Người Dùng:** Là một người dùng, tôi muốn hệ thống hoạt động nhanh và ổn định với dữ liệu lớn, để không bị gián đoạn công việc.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL sử dụng SQLite với connection pooling
2. THE Hệ_Thống SHALL sử dụng indexes để tối ưu query performance
3. THE Hệ_Thống SHALL implement pagination cho bảng lớn hơn 1000 records
4. THE Hệ_Thống SHALL sử dụng lazy loading cho autocomplete suggestions
5. THE Hệ_Thống SHALL tự động backup database hàng ngày

### Yêu Cầu 17: Error Handling và Logging

**Câu Chuyện Người Dùng:** Là một người dùng, tôi muốn hệ thống xử lý lỗi một cách thân thiện và ghi log để debug, để dễ dàng khắc phục sự cố khi có vấn đề.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL hiển thị user-friendly error messages khi có lỗi
2. THE Hệ_Thống SHALL ghi log tất cả errors vào file với timestamp và stack trace
3. THE Hệ_Thống SHALL cung cấp error recovery mechanisms
4. THE Hệ_Thống SHALL validate tất cả user inputs trước khi xử lý
5. THE Hệ_Thống SHALL rollback transactions khi có lỗi database

### Yêu Cầu 18: Utilities và Helper Functions

**Câu Chuyện Người Dùng:** Là một developer, tôi muốn có các utility functions để xử lý date, number, text, để code dễ maintain và reusable.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống SHALL cung cấp datetime utils: format, parse, calculations, timezone handling
2. THE Hệ_Thống SHALL cung cấp number utils: format currency, parse number, validation, rounding
3. THE Hệ_Thống SHALL cung cấp text utils: normalize, remove special chars, slug generation
4. THE Hệ_Thống SHALL sử dụng consistent formatting across toàn bộ ứng dụng
5. THE Hệ_Thống SHALL handle edge cases trong tất cả utility functions
