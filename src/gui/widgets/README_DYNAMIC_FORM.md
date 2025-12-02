# Dynamic Form System

## Tổng Quan

Hệ thống Dynamic Form cung cấp khả năng tạo form động từ cấu hình, hỗ trợ 10 loại widget, 6 loại validator, và tích hợp validation theo thời gian thực.

## Các Thành Phần

### 1. Field Widgets (10 loại)

#### 1.1 TextboxWidget
- Widget nhập text cơ bản
- Hỗ trợ placeholder và max length
- Validation theo thời gian thực

```python
widget = TextboxWidget(placeholder="Nhập tên", max_length=100)
widget.set_value("John Doe")
value = widget.get_value()
```

#### 1.2 NumberWidget
- Widget nhập số với min/max và step
- Hỗ trợ cả số nguyên và số thập phân
- Spin buttons để tăng/giảm giá trị

```python
widget = NumberWidget(min_value=0, max_value=100, step=5, decimals=2)
widget.set_value(50.5)
```

#### 1.3 CurrencyWidget
- Widget nhập tiền tệ với auto-formatting
- Tự động thêm dấu phân cách hàng nghìn
- Hiển thị ký hiệu tiền tệ

```python
widget = CurrencyWidget(currency_symbol="VND")
widget.set_value(1000000)  # Hiển thị: 1,000,000 VND
```

#### 1.4 DateEditWidget
- Widget chọn ngày với calendar picker
- Hỗ trợ keyboard input
- Format: dd/MM/yyyy

```python
widget = DateEditWidget()
widget.set_value("2024-01-15")
```

#### 1.5 ComboboxWidget
- Dropdown với autocomplete
- Hỗ trợ editable mode
- Fuzzy search trong options

```python
widget = ComboboxWidget(options=["Hà Nội", "HCMC", "Đà Nẵng"], editable=True)
widget.set_value("Hà Nội")
```

#### 1.6 CheckboxWidget
- Checkbox đơn giản
- Hỗ trợ label tùy chỉnh

```python
widget = CheckboxWidget(label="Đã thanh toán")
widget.set_value(True)
```

#### 1.7 EmailWidget
- Widget nhập email với validation
- Kiểm tra format email theo RFC 5322
- Visual feedback cho email không hợp lệ

```python
widget = EmailWidget(placeholder="email@example.com")
widget.set_value("user@domain.com")
```

#### 1.8 PhoneWidget
- Widget nhập số điện thoại
- Auto-formatting
- Validation độ dài tối thiểu

```python
widget = PhoneWidget(placeholder="0123456789")
widget.set_value("0987654321")
```

#### 1.9 TextAreaWidget
- Multi-line text input
- Word count display
- Max length enforcement

```python
widget = TextAreaWidget(placeholder="Nhập ghi chú", max_length=500)
widget.set_value("Đây là ghi chú dài...")
```

#### 1.10 URLWidget
- Widget nhập URL với validation
- Auto-add protocol (http://)
- Kiểm tra format URL

```python
widget = URLWidget(placeholder="https://example.com")
widget.set_value("example.com")  # Tự động thành http://example.com
```

### 2. Form Validators (6 loại)

#### 2.1 RequiredValidator
Kiểm tra field không được để trống

```python
validator = RequiredValidator(error_message="Trường này bắt buộc")
is_valid, msg = validator.validate("value")
```

#### 2.2 NumberOnlyValidator
Kiểm tra chỉ chứa số

```python
validator = NumberOnlyValidator(allow_decimals=True)
is_valid, msg = validator.validate("123.45")
```

#### 2.3 TextOnlyValidator
Kiểm tra chỉ chứa chữ cái

```python
validator = TextOnlyValidator(allow_spaces=True, allow_unicode=True)
is_valid, msg = validator.validate("Nguyễn Văn A")
```

#### 2.4 NoSpecialCharsValidator
Kiểm tra không chứa ký tự đặc biệt

```python
validator = NoSpecialCharsValidator(allowed_chars="-_")
is_valid, msg = validator.validate("user_name-123")
```

#### 2.5 EmailFormatValidator
Kiểm tra format email

```python
validator = EmailFormatValidator()
is_valid, msg = validator.validate("user@example.com")
```

#### 2.6 PatternMatchingValidator
Kiểm tra theo regex pattern

```python
validator = PatternMatchingValidator(r'^\d{3}-\d{4}$')
is_valid, msg = validator.validate("123-4567")
```

### 3. FormValidator

Quản lý validation cho toàn bộ form

```python
form_validator = FormValidator()

# Add validators cho từng field
form_validator.add_validator("name", RequiredValidator())
form_validator.add_validator("age", NumberOnlyValidator())

# Validate single field
is_valid, msg = form_validator.validate_field("name", "John")

# Validate entire form
form_data = {"name": "John", "age": "25"}
is_valid, errors = form_validator.validate_form(form_data)

# Add cross-field validator
def validate_dates(form_data):
    if form_data['end_date'] < form_data['start_date']:
        return False, "End date must be after start date", "end_date"
    return True, "", ""

form_validator.add_cross_field_validator(validate_dates)
```

### 4. ValidationRuleBuilder

Build validators từ configuration

```python
config = {
    "required": True,
    "type": "number",
    "no_special_chars": True,
    "pattern": r'^\d+$',
    "error_messages": {
        "required": "Vui lòng nhập giá trị",
        "number": "Chỉ được nhập số"
    }
}

validators = ValidationRuleBuilder.build_from_config(config)
```

### 5. WidgetFactory

Tạo widget từ FieldConfiguration

```python
from src.models.field_configuration import FieldConfiguration

config = FieldConfiguration(
    department_id=1,
    field_name="Tên khách hàng",
    field_type="text",
    widget_type="textbox",
    is_required=True,
    validation_rules={"max_length": 100}
)

widget = WidgetFactory.create_widget(config)
```

### 6. FormBuilder

Build form từ danh sách FieldConfiguration

```python
configs = [
    FieldConfiguration(
        department_id=1,
        field_name="Tên",
        field_type="text",
        widget_type="textbox",
        is_required=True,
        display_order=1,
        category="Thông tin cơ bản"
    ),
    FieldConfiguration(
        department_id=1,
        field_name="Tuổi",
        field_type="number",
        widget_type="number",
        display_order=2,
        category="Thông tin cơ bản"
    )
]

form_builder = FormBuilder()
form_widget = form_builder.build_form(configs)

# Get/Set form data
form_builder.set_form_data({"Tên": "John", "Tuổi": 25})
data = form_builder.get_form_data()

# Validate form
is_valid, errors = form_builder.validate_form()

# Get specific field widget
name_widget = form_builder.get_field_widget("Tên")
```

### 7. DynamicFormWidget

High-level widget tích hợp tất cả

```python
from src.gui.widgets import DynamicFormWidget

# Create form
form = DynamicFormWidget(field_configs, show_buttons=True)

# Connect signals
form.formSubmitted.connect(on_submit)
form.formCleared.connect(on_clear)
form.formDataChanged.connect(on_change)
form.validationFailed.connect(on_validation_error)

# Get/Set data
form.set_form_data({"Tên": "John"})
data = form.get_form_data()

# Validate
is_valid = form.validate_form(show_errors=True)

# Submit
form.submit_form()

# Clear
form.clear_form()

# Field operations
form.set_field_value("Tên", "Jane")
value = form.get_field_value("Tên")
form.set_field_enabled("Tên", False)
form.set_field_visible("Tuổi", False)
```

## Signals

### DynamicFormWidget Signals

- `formSubmitted(dict)`: Emitted khi form được submit với data hợp lệ
- `formCleared()`: Emitted khi form được clear
- `formDataChanged(dict)`: Emitted khi bất kỳ field nào thay đổi
- `validationFailed(dict)`: Emitted khi validation thất bại với errors

### BaseFieldWidget Signals

- `valueChanged(object)`: Emitted khi giá trị thay đổi
- `validationChanged(bool)`: Emitted khi trạng thái validation thay đổi

## Visual Feedback

- **Valid field**: Border mặc định
- **Invalid field**: Border đỏ 2px
- **Error message**: Hiển thị dưới field hoặc trong status label
- **Required fields**: Đánh dấu bằng dấu * sau label

## Ví Dụ Hoàn Chỉnh

```python
from PyQt6.QtWidgets import QApplication, QMainWindow
from src.models.field_configuration import FieldConfiguration
from src.gui.widgets import DynamicFormWidget

# Create field configurations
configs = [
    FieldConfiguration(
        department_id=1,
        field_name="Tên khách hàng",
        field_type="text",
        widget_type="textbox",
        is_required=True,
        validation_rules={"max_length": 100},
        display_order=1,
        category="Thông tin cơ bản"
    ),
    FieldConfiguration(
        department_id=1,
        field_name="Email",
        field_type="email",
        widget_type="email",
        is_required=True,
        display_order=2,
        category="Liên hệ"
    ),
    FieldConfiguration(
        department_id=1,
        field_name="Giá cả",
        field_type="currency",
        widget_type="currency",
        is_required=True,
        display_order=3,
        category="Thông tin cơ bản"
    )
]

# Create application
app = QApplication([])

# Create form
form = DynamicFormWidget(configs, show_buttons=True)

# Connect signals
def on_submit(data):
    print("Form submitted:", data)

form.formSubmitted.connect(on_submit)

# Show form
window = QMainWindow()
window.setCentralWidget(form)
window.show()

app.exec()
```

## Best Practices

1. **Validation**: Luôn validate form trước khi submit
2. **Error Handling**: Xử lý validation errors một cách thân thiện
3. **Visual Feedback**: Sử dụng visual feedback để hướng dẫn người dùng
4. **Cross-field Validation**: Sử dụng cho các validation phức tạp giữa nhiều fields
5. **Configuration**: Lưu field configurations trong database để dễ quản lý
6. **Reusability**: Tái sử dụng validators và widgets cho nhiều forms

## Testing

Xem `tests/unit/test_widgets_simple.py` để biết cách test các components.

```bash
python tests/unit/test_widgets_simple.py
```

## Demo

Chạy demo để xem tất cả widgets hoạt động:

```bash
python examples/dynamic_form_demo.py
```
