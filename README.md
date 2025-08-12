# Simple Python Console Application

Một ứng dụng Python đơn giản với giao diện console tương tác.

## 📋 Tính năng

- WIP

## 🚀 Cách chạy

### Chạy trực tiếp với Python

```bash
python3 console_app.py
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

## 📂 Cấu trúc thư mục sau khi build

``` txt
simple_python_console_app/
├── console_app.py          # Ứng dụng chính
├── requirements.txt        # Dependencies
├── README.md              # Hướng dẫn này
├── build.sh               # Script build cho macOS/Linux
├── build.bat              # Script build cho Windows
├── venv/                  # Virtual environment
├── build/                 # Thư mục tạm (có thể xóa)
├── dist/                  # Chứa file thực thi
│   └── ai_automation_app   # File thực thi (macOS/Linux)
│   └── ai_automation_app.exe # File thực thi (Windows)
└── ai_automation_app.spec  # File cấu hình PyInstaller
```

## 🔧 Tùy chọn PyInstaller hữu ích

- `--onefile`: Tạo một file thực thi duy nhất
- `--windowed`: Ẩn cửa sổ console (chỉ dành cho GUI apps)
- `--icon=icon.ico`: Thêm icon cho ứng dụng
- `--name=MyApp`: Đặt tên cho file thực thi
- `--distpath=dist`: Thư mục chứa file thực thi
- `--exclude-module=module_name`: Loại bỏ module không cần thiết

## 💡 Mẹo và Lưu ý

### ✅ Ưu điểm của PyInstaller

- File thực thi độc lập, không cần cài Python
- Hỗ trợ nhiều platform (Windows, macOS, Linux)
- Tự động đóng gói dependencies

### ⚠️ Lưu ý

- Kích thước file khá lớn (5-20MB+) do chứa Python runtime
- Thời gian khởi động có thể chậm hơn script Python thông thường
- File thực thi chỉ chạy trên platform tương ứng được build

### 🔍 Troubleshooting

**Lỗi "Module not found":**

```bash
pip install missing_module
pyinstaller --onefile console_app.py
```

**File quá lớn:**

```bash
pyinstaller --onefile --exclude-module=unused_module console_app.py
```

**Cần icon tùy chỉnh:**

```bash
pyinstaller --onefile --icon=myicon.ico console_app.py
```

## 🎯 Yêu cầu hệ thống

- Python 3.6 trở lên
- PyInstaller 6.0+ (sẽ được cài tự động)
- Đủ dung lượng ổ cứng (50MB+)

## 🌍 Cross-platform Build

Để tạo file thực thi cho các platform khác:

1. **Windows executable**: Cần build trên Windows
2. **macOS executable**: Cần build trên macOS  
3. **Linux executable**: Cần build trên Linux

**Không thể build cross-platform từ một OS!**

## 📞 Hỗ trợ

Nếu gặp vấn đề:

1. Kiểm tra Python version: `python3 --version`
2. Kiểm tra PyInstaller: `pyinstaller --version`
3. Xóa thư mục `build` và `dist`, build lại
4. Kiểm tra log build để tìm lỗi cụ thể
