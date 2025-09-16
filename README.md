# AI Automation Python Application

Ứng dụng Python tự động hóa sử dụng Amazon Nova Act để thực hiện các tác vụ quản trị CSP (Customer Service Portal) với giao diện console tương tác.

## 📋 Tính năng

- **CSP Admin Automation**: Tự động thay đổi vai trò và chi nhánh người dùng
- **Amazon Nova Act Integration**: AI-powered browser automation
- **Single Worker Mode**: Xử lý tuần tự đảm bảo tính ổn định
- **Console Interface**: Giao diện menu tương tác bằng tiếng Việt
- **JSON Configuration**: Cấu hình dễ dàng qua file JSON
- **Debug Support**: HTML trace files và logging chi tiết
- **Cross-platform**: Hỗ trợ Windows, macOS, Linux

## 🚀 Cách chạy

### Chạy trực tiếp với Python

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
python console_app.py
```

### 📦 Đóng gói với PyInstaller

#### Sử dụng script build tự động (Khuyến nghị)

**macOS/Linux:**

```bash
chmod +x build.sh
./build.sh
```

**Windows:**

```cmd
build.bat
```

#### Thủ công

#### Bước 1: Tạo virtual environment

```bash
python3 -m venv venv
```

#### Bước 2: Kích hoạt virtual environment

macOS/Linux:

```bash
source venv/bin/activate
```

Windows:

```cmd
venv\Scripts\activate.bat
```

#### Bước 3: Cài đặt PyInstaller

```bash
pip install pyinstaller
```

#### Bước 4: Tạo file thực thi

```bash
pyinstaller --onefile --name="ai_automation_app" console_app.py
```

## 📂 Cấu trúc thư mục

```
ai_automation_python_app/
├── console_app.py              # Ứng dụng console chính
├── requirements.txt            # Python dependencies
├── README.md                  # Hướng dẫn này
├── AGENTS.md                  # Hướng dẫn cho AI coding agents
├── build.sh                   # Script build cho macOS/Linux  
├── build.bat                  # Script build cho Windows
├── ai_automation_app.spec     # File cấu hình PyInstaller
├── src/                       # Source code
│   ├── config/
│   │   └── nova_act_config.py # Cấu hình Nova Act API key
│   ├── csp/
│   │   ├── csp_admin_change_role_and_branch.py # Module automation chính
│   │   ├── input.json         # Template cấu hình
│   │   ├── input_test.json    # Cấu hình test
│   │   └── input_prod.json    # Cấu hình production
│   └── samples/
│       └── order_a_coffee_maker.py # Nova Act sample
├── releases/
│   └── HƯỚNG_DẪN_SỬ_DỤNG.md  # Hướng dẫn người dùng chi tiết
├── build/                     # Thư mục tạm (có thể xóa)
└── dist/                      # Chứa file thực thi
    ├── ai_automation_app      # File thực thi (macOS/Linux)
    └── ai_automation_app.exe  # File thực thi (Windows)
```

## 🔧 Cấu hình

### Nova Act API Key
1. Lấy API key từ https://nova.amazon.com/act
2. Cập nhật trong `src/config/nova_act_config.py`
3. Hoặc set environment variable: `export NOVA_ACT_API_KEY="your_key"`

### Input Configuration
Tạo file `input.json` cùng thư mục với executable:

```json
{
  "admin_credentials": {
    "username": "admin_user",
    "password": "admin_password",
    "csp_admin_url": "https://csp-portal.com/portal/users/list"
  },
  "users": [
    {
      "target_user": "user@example.com",
      "new_role": "CSP-RB-TELLER",
      "branch_hierarchy": ["VIB Bank", "North", "002"]
    }
  ]
}
```

## 🎯 Yêu cầu hệ thống

- **Python**: 3.10 trở lên
- **Nova Act**: 2.0+ (được cài tự động)
- **PyInstaller**: 6.0+ (cho build)
- **Dung lượng**: 50MB+ cho executable
- **Internet**: Kết nối ổn định cho Nova Act API
- **Browser**: Chrome/Chromium (được cài tự động bởi Nova Act)

## 🌍 Cross-platform Build

Để tạo file thực thi cho các platform khác:

1. **Windows executable**: Cần build trên Windows
2. **macOS executable**: Cần build trên macOS  
3. **Linux executable**: Cần build trên Linux

**Không thể build cross-platform từ một OS!**

## � Thay đổi gần đây

### v2.0 - Amazon Nova Act Integration
- **Nova Act AI**: Thay thế automation thủ công bằng AI browser automation
- **Single Worker Mode**: Chuyển từ parallel sang sequential processing
- **Hierarchical Navigation**: Cải tiến hệ thống điều hướng chi nhánh
- **Debug Enhancement**: HTML trace files và logging chi tiết

### Refactoring Highlights
- Gộp methods thành `change_user_branch_hierarchical`
- Loại bỏ parallel workers để tăng độ tin cậy
- Backward compatibility cho `new_branch` parameter
- Enhanced error handling và recovery

## �📞 Hỗ trợ

Nếu gặp vấn đề:

1. **Kiểm tra Nova Act API key**: `python -c "from src.config.nova_act_config import get_nova_act_api_key; print('OK')"`
2. **Kiểm tra file log**: `csp_automation_[timestamp].log`
3. **Xem HTML trace files**: Trong thư mục logs
4. **Kiểm tra cấu hình**: File `input.json` phải cùng thư mục executable
5. **Liên hệ team**: Với log files và mô tả lỗi cụ thể

## 📚 Tài liệu

- **Hướng dẫn người dùng**: [releases/HƯỚNG_DẪN_SỬ_DỤNG.md](releases/HƯỚNG_DẪN_SỬ_DỤNG.md)
- **Agent documentation**: [AGENTS.md](AGENTS.md)
- **Refactoring notes**: [REFACTOR_SUMMARY.md](REFACTOR_SUMMARY.md)
- **Nova Act docs**: [README_NOVA_ACT.md](README_NOVA_ACT.md)
