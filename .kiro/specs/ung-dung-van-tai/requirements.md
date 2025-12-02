# Tài Liệu Yêu Cầu - Ứng Dụng Quản Lý Vận Tải

## Giới Thiệu

Ứng dụng quản lý vận tải là một hệ thống desktop được phát triển bằng Python để hỗ trợ các công ty vận tải quản lý thông tin chuyến xe, theo dõi chi phí và tra cứu bảng giá. Ứng dụng cung cấp giao diện trực quan với khả năng nhập liệu nhanh, tìm kiếm thông minh và quản lý dữ liệu hiệu quả.

## Thuật Ngữ

- **Hệ_Thống_Vận_Tải**: Ứng dụng Python quản lý thông tin vận tải
- **Chuyến_Xe**: Một lần vận chuyển hàng hóa từ điểm đi đến điểm đến
- **Bảng_Giá**: Danh sách giá cước vận chuyển của các công ty
- **Form_Nhập_Liệu**: Giao diện nhập thông tin chuyến xe mới
- **Bảng_Dữ_Liệu**: Hiển thị danh sách các chuyến xe dạng bảng
- **Hệ_Thống_Gợi_Ý**: Tính năng autocomplete và lọc dữ liệu
- **Người_Dùng**: Nhân viên điều hành vận tải sử dụng ứng dụng

## Yêu Cầu

### Yêu Cầu 1

**Câu Chuyện Người Dùng:** Là một nhân viên điều hành, tôi muốn nhập thông tin chuyến xe mới một cách nhanh chóng, để có thể theo dõi và quản lý tất cả các chuyến vận tải.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống_Vận_Tải SHALL hiển thị form nhập liệu với các trường: mã chuyến, khách hàng, điểm đi, điểm đến, giá cả, khoán lương, chi phí khác, ghi chú
2. WHEN người dùng nhập thông tin và nhấn nút thêm, THE Hệ_Thống_Vận_Tải SHALL tự động tạo mã chuyến theo định dạng C001, C002, C003...
3. THE Hệ_Thống_Vận_Tải SHALL xác thực dữ liệu đầu vào với khách hàng và giá cả là bắt buộc
4. WHEN thêm chuyến thành công, THE Hệ_Thống_Vận_Tải SHALL xóa sạch form và focus vào trường khách hàng
5. THE Hệ_Thống_Vận_Tải SHALL lưu trữ dữ liệu chuyến xe vào cơ sở dữ liệu local

### Yêu Cầu 2

**Câu Chuyện Người Dùng:** Là một nhân viên điều hành, tôi muốn xem danh sách tất cả các chuyến xe dạng bảng có thể chỉnh sửa, để dễ dàng theo dõi và cập nhật thông tin.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống_Vận_Tải SHALL hiển thị bảng dữ liệu với các cột: mã chuyến, khách hàng, điểm đi, điểm đến, giá cả, khoán lương, chi phí khác, ghi chú
2. THE Hệ_Thống_Vận_Tải SHALL cho phép chỉnh sửa trực tiếp trên bảng trừ cột mã chuyến
3. THE Hệ_Thống_Vận_Tải SHALL hỗ trợ copy và paste dữ liệu từ Excel hoặc ứng dụng khác
4. WHEN dữ liệu được thay đổi trên bảng, THE Hệ_Thống_Vận_Tải SHALL tự động lưu thay đổi
5. THE Hệ_Thống_Vận_Tải SHALL hiển thị định dạng số tiền với dấu phân cách hàng nghìn

### Yêu Cầu 3

**Câu Chuyện Người Dùng:** Là một nhân viên điều hành, tôi muốn có gợi ý tự động khi nhập liệu, để tăng tốc độ nhập và giảm sai sót.

#### Tiêu Chí Chấp Nhận

1. WHEN người dùng gõ vào trường khách hàng, THE Hệ_Thống_Vận_Tải SHALL hiển thị dropdown gợi ý các khách hàng đã có
2. WHEN người dùng gõ vào trường điểm đi hoặc điểm đến, THE Hệ_Thống_Vận_Tải SHALL hiển thị dropdown gợi ý các địa điểm đã có
3. THE Hệ_Thống_Vận_Tải SHALL hỗ trợ tìm kiếm mờ trong dropdown gợi ý
4. WHEN người dùng nhấn phím mũi tên lên/xuống, THE Hệ_Thống_Vận_Tải SHALL điều hướng trong danh sách gợi ý
5. WHEN người dùng nhấn Enter hoặc click, THE Hệ_Thống_Vận_Tải SHALL chọn giá trị gợi ý và đóng dropdown

### Yêu Cầu 4

**Câu Chuyện Người Dùng:** Là một nhân viên điều hành, tôi muốn tìm kiếm và lọc các chuyến xe theo nhiều tiêu chí, để nhanh chóng tìm thông tin cần thiết.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống_Vận_Tải SHALL cung cấp bảng lọc hiển thị kết quả tìm kiếm theo thời gian thực
2. WHEN người dùng nhập vào bất kỳ trường nào trong form, THE Hệ_Thống_Vận_Tải SHALL lọc và hiển thị các chuyến phù hợp
3. THE Hệ_Thống_Vận_Tải SHALL hỗ trợ lọc đồng thời theo nhiều trường
4. WHEN người dùng click vào một dòng trong bảng lọc, THE Hệ_Thống_Vận_Tải SHALL điền thông tin vào form nhập liệu
5. THE Hệ_Thống_Vận_Tải SHALL giới hạn kết quả lọc tối đa 20 dòng để tối ưu hiệu suất

### Yêu Cầu 5

**Câu Chuyện Người Dùng:** Là một nhân viên điều hành, tôi muốn tra cứu bảng giá của các công ty khác nhau, để so sánh và đưa ra quyết định giá cả phù hợp.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống_Vận_Tải SHALL hiển thị các tab bảng giá cho từng công ty (Công ty A, B, C)
2. THE Hệ_Thống_Vận_Tải SHALL cho phép lọc bảng giá theo khách hàng, điểm đi, điểm đến
3. WHEN người dùng click vào một dòng trong bảng giá, THE Hệ_Thống_Vận_Tải SHALL điền thông tin vào form nhập liệu
4. THE Hệ_Thống_Vận_Tải SHALL hiển thị bảng giá ở chế độ chỉ đọc
5. THE Hệ_Thống_Vận_Tải SHALL đồng bộ lọc bảng giá với các trường nhập liệu

### Yêu Cầu 6

**Câu Chuyện Người Dùng:** Là một nhân viên điều hành, tôi muốn ứng dụng có giao diện thân thiện và dễ sử dụng, để làm việc hiệu quả mà không cần đào tạo phức tạp.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống_Vận_Tải SHALL sử dụng layout chia 3 vùng: form nhập liệu bên trái, bảng chính trên phải, bảng gợi ý dưới phải
2. THE Hệ_Thống_Vận_Tải SHALL có giao diện responsive thích ứng với kích thước cửa sổ
3. THE Hệ_Thống_Vận_Tải SHALL sử dụng màu sắc và font chữ dễ đọc, thân thiện với mắt
4. THE Hệ_Thống_Vận_Tải SHALL cung cấp phím tắt cho các thao tác thường dùng
5. THE Hệ_Thống_Vận_Tải SHALL hiển thị thông báo lỗi rõ ràng khi có sự cố

### Yêu Cầu 7

**Câu Chuyện Người Dùng:** Là một nhân viên điều hành, tôi muốn dữ liệu được lưu trữ an toàn và có thể khôi phục, để đảm bảo không mất thông tin quan trọng.

#### Tiêu Chí Chấp Nhận

1. THE Hệ_Thống_Vận_Tải SHALL sử dụng cơ sở dữ liệu SQLite để lưu trữ dữ liệu local
2. THE Hệ_Thống_Vận_Tải SHALL tự động tạo backup dữ liệu hàng ngày
3. THE Hệ_Thống_Vận_Tải SHALL cung cấp chức năng export dữ liệu ra Excel
4. THE Hệ_Thống_Vận_Tải SHALL cung cấp chức năng import dữ liệu từ Excel
5. WHEN khởi động lần đầu, THE Hệ_Thống_Vận_Tải SHALL tạo dữ liệu mẫu để người dùng làm quen