# Hệ Thống Quản Lý Vận Tải Toàn Diện

Ứng dụng desktop quản lý vận tải toàn diện được phát triển bằng Python/PyQt6, cung cấp giải pháp hoàn chỉnh cho việc quản lý thông tin chuyến xe, theo dõi chi phí, tra cứu bảng giá và tự động hóa quy trình nghiệp vụ.

## Tính Năng Chính

- ✅ **Quản lý chuyến xe**: Nhập, chỉnh sửa, tìm kiếm thông tin chuyến xe
- ✅ **Form động**: Tạo và quản lý form nhập liệu không cần code
- ✅ **Autocomplete thông minh**: Gợi ý tự động khi nhập liệu
- ✅ **Excel-like interface**: Copy/paste, filtering, column management
- ✅ **Công thức tự động**: Tính toán tự động theo công thức
- ✅ **Workflow automation**: Tự động đẩy dữ liệu giữa phòng ban
- ✅ **Multi-department**: Hỗ trợ nhiều phòng ban độc lập
- ✅ **Import/Export Excel**: Tích hợp với Excel
- ✅ **Tra cứu bảng giá**: So sánh giá từ nhiều công ty

## Yêu Cầu Hệ Thống

- Python 3.10 hoặc cao hơn
- Windows 10/11 (khuyến nghị)
- RAM: 4GB trở lên
- Dung lượng: 500MB trống

## Cài Đặt

### 1. Clone repository

```bash
git clone https://github.com/yourusername/Quan-Ly-Van-Tai-Nang-Cao.git
cd Quan-Ly-Van-Tai-Nang-Cao
```

### 2. Tạo virtual environment

```bash
python -m venv venv
```

### 3. Kích hoạt virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

## Chạy Ứng Dụng

```bash
python main.py
```

## Cấu Trúc Dự Án

```
Quan-Ly-Van-Tai-Nang-Cao/
├── src/                    # Source code
│   ├── gui/               # GUI components
│   │   ├── widgets/       # Custom widgets
│   │   └── dialogs/       # Dialog windows
│   ├── services/          # Business logic
│   ├── models/            # Data models
│   ├── database/          # Database layer
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── performance/      # Performance tests
│   └── fixtures/         # Test fixtures
├── data/                  # Database files
├── logs/                  # Log files
├── backups/              # Database backups
├── main.py               # Entry point
├── config.py             # Configuration
└── requirements.txt      # Dependencies
```

## Testing

Chạy tất cả tests:

```bash
pytest
```

Chạy với coverage:

```bash
pytest --cov=src --cov-report=html
```

Chạy specific test:

```bash
pytest tests/unit/test_trip_service.py
```

## Development

### Logging

Logs được lưu tại `logs/transportapp.log` với rotation tự động.

### Database

SQLite database được lưu tại `data/transport.db`. Backup tự động hàng ngày tại `backups/`.

### Configuration

Cấu hình ứng dụng trong file `config.py`.

## Đóng Góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Liên Hệ

Project Link: [https://github.com/yourusername/Quan-Ly-Van-Tai-Nang-Cao](https://github.com/yourusername/Quan-Ly-Van-Tai-Nang-Cao)

## Acknowledgments

- PyQt6 for the GUI framework
- pandas for data processing
- pydantic for data validation
