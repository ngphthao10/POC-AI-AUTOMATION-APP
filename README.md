# CSP Admin Automation

**AI-Powered Browser Automation for CSP Admin Portal**

Ứng dụng tự động hóa thao tác quản lý user trên CSP Admin Portal sử dụng **Nova Act AI Agent**.

---

## 🎯 Tính Năng

- ✅ **Tự động login** với admin credentials
- ✅ **Tìm kiếm user** theo username
- ✅ **Thay đổi role** user (optional)
- ✅ **Thay đổi branch** theo hierarchy (optional)
- ✅ **Lưu thay đổi** tự động
- ✅ **Smart retry** với exponential backoff
- ✅ **Circuit breaker** tự động phát hiện network down
- ✅ **Screenshot** tự động khi có lỗi
- ✅ **Logging** chi tiết cho troubleshooting

---

## 📋 Yêu Cầu Hệ Thống

- **Python:** 3.8 trở lên
- **OS:** Windows 10+, macOS 10.15+, hoặc Linux
- **RAM:** Tối thiểu 4GB
- **Internet:** Kết nối ổn định
- **Nova Act API Key:** Liên hệ admin để lấy key

---

## 🚀 Cài Đặt & Chạy (Development)

### 1. Clone Repository

```bash
git clone https://github.com/ngphthao10/POC-AI-AUTOMATION-APP.git
cd POC-AI-AUTOMATION-APP
```

### 2. Cài Đặt Dependencies

```bash
# Tạo virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 3. Cấu Hình

Tạo file `.env` trong thư mục gốc:

```env
NOVA_ACT_API_KEY=your_nova_act_api_key_here
AWS_REGION=us-east-1
AGENTCORE_IDENTIFIER=your_identifier
AGENTCORE_SESSION_TIMEOUT=20000
```

Chỉnh sửa file `input.json`:

```json
{
  "admin_credentials": {
    "username": "mb\\admin.username",
    "password": "your_password",
    "csp_admin_url": "https://your-csp-portal.com/portal/users/list"
  },
  "users": [
    {
      "target_user": "user1@example.com",
      "new_role": "CSP-RB-TELLER",
      "branch_hierarchy": ["VIB Bank", "North Region", "002_HA NOI"]
    },
    {
      "target_user": "user2@example.com",
      "new_role": "CSP_Inquiry",
      "branch_hierarchy": []
    }
  ]
}
```

**Lưu ý:**
- `new_role`: Để trống hoặc bỏ field nếu không muốn đổi role
- `branch_hierarchy`: Để array rỗng `[]` nếu không muốn đổi branch
- `branch_hierarchy` cần đúng 3 levels: [Bank, Region, Branch]

### 4. Chạy Ứng Dụng

```bash
# Console app
python console_app.py
```

Ứng dụng sẽ:
1. Đọc cấu hình từ `input.json`
2. Hiển thị danh sách users cần xử lý
3. Yêu cầu xác nhận
4. Chạy automation cho từng user

---

## 📦 Đóng Gói cho Windows

### Yêu Cầu

- **Windows 10** trở lên
- **Python 3.8+** đã cài đặt
- **Git Bash** hoặc Command Prompt

### Các Bước Build

#### 1. Chuẩn Bị

```cmd
# Clone repo (nếu chưa có)
git clone https://github.com/ngphthao10/POC-AI-AUTOMATION-APP.git
cd POC-AI-AUTOMATION-APP
```

#### 2. Chạy Build Script

```cmd
build.bat
```

Script sẽ tự động:
- ✅ Tạo virtual environment
- ✅ Cài đặt dependencies
- ✅ Cài đặt Playwright chromium
- ✅ Build executable với PyInstaller
- ✅ Copy file cần thiết vào `dist/`
- ✅ Tạo README cho end-user

#### 3. Kết Quả

Sau khi build xong, folder `dist/` sẽ có cấu trúc:

```
dist/
├── csp_automation.exe    # File thực thi chính
├── input.json            # File cấu hình
├── template.json         # Template mẫu
├── .env                  # Environment variables (cần config)
├── README.txt            # Hướng dẫn sử dụng
├── logs/                 # Folder chứa logs
└── screenshots/          # Folder chứa screenshots
```

#### 4. Phân Phối

**Cách 1: Zip toàn bộ folder `dist/`**

```cmd
# Nén folder dist
tar -a -c -f csp_automation.zip dist

# Hoặc dùng 7-Zip, WinRAR
```

**Cách 2: Copy folder `dist/` sang USB/Network**

```cmd
xcopy /E /I dist D:\deployment\csp_automation
```

---

## 👥 Hướng Dẫn End-User (Windows)

### 1. Giải Nén

Giải nén file `csp_automation.zip` vào folder bất kỳ, ví dụ `C:\CSP_Automation\`

### 2. Cấu Hình

**File `.env`:** (Quan trọng!)

```env
NOVA_ACT_API_KEY=<hỏi admin để lấy key>
AWS_REGION=us-east-1
AGENTCORE_IDENTIFIER=<hỏi admin>
AGENTCORE_SESSION_TIMEOUT=20000
```

**File `input.json`:**

```json
{
  "admin_credentials": {
    "username": "mb\\your.admin.username",
    "password": "your_password",
    "csp_admin_url": "https://csp-portal.example.com/portal/users/list"
  },
  "users": [
    {
      "target_user": "john.doe@example.com",
      "new_role": "CSP-RB-TELLER",
      "branch_hierarchy": ["VIB Bank", "North", "002_HA NOI"]
    }
  ]
}
```

### 3. Chạy

**Double-click** vào `csp_automation.exe`

Hoặc mở Command Prompt:

```cmd
cd C:\CSP_Automation
csp_automation.exe
```

### 4. Theo Dõi

- **Logs:** Xem file log trong folder `logs/`
- **Screenshots:** Xem ảnh lỗi trong folder `screenshots/` (nếu có lỗi)

---

## 📂 Cấu Trúc Project

```
poc-ai-automation-app/
├── console_app.py                    # Entry point - Console UI
├── input.json                        # Configuration file
├── template.json                     # Template mẫu
├── build.bat                         # Build script cho Windows
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables (git ignored)
│
├── src/
│   ├── features/csp/
│   │   ├── csp_admin_simple_v2.py   # Main automation logic
│   │   └── handlers/                 # Individual step handlers
│   │       ├── csp_login_handler.py
│   │       ├── csp_user_search_handler.py
│   │       ├── csp_role_handler.py
│   │       ├── csp_branch_handler.py
│   │       └── csp_save_handler.py
│   │
│   └── shared/                       # Shared utilities
│       ├── nova_manager.py           # Nova Act manager
│       ├── handler_wrapper.py        # Retry logic wrapper
│       ├── retry_utils.py            # Retry & circuit breaker
│       ├── logger.py                 # Logging setup
│       └── screenshot_utils.py       # Screenshot utilities
│
├── logs/                             # Automation logs (auto-created)
└── screenshots/                      # Debug screenshots (auto-created)
```

---

## 🔧 Configuration Guide

### input.json Chi Tiết

```json
{
  "admin_credentials": {
    "username": "mb\\admin.user",     // Username (format: domain\\username)
    "password": "SecureP@ssw0rd",     // Password
    "csp_admin_url": "https://..."    // URL trang danh sách users
  },
  "users": [
    {
      "target_user": "john.doe",      // Username cần xử lý (không cần domain)
      "new_role": "CSP-RB-TELLER",    // Role mới (optional - có thể bỏ)
      "branch_hierarchy": [            // Branch hierarchy (optional - có thể để [])
        "VIB Bank",                    // Level 1: Bank
        "North",                       // Level 2: Region
        "002_HA NOI"                   // Level 3: Branch code
      ]
    }
  ]
}
```

### Các Role Hợp Lệ

- `CSP-RB-TELLER`
- `CSP_Inquiry`
- `CSP_Admin`
- (Liên hệ admin để biết danh sách đầy đủ)

### Branch Hierarchy Format

**Luôn cần 3 levels:**
1. **Bank name** (VD: "VIB Bank")
2. **Region** (VD: "North", "South", "Central")
3. **Branch code** (VD: "002_HA NOI", "001_HCM")

**Ví dụ:**
```json
"branch_hierarchy": ["VIB Bank", "North Region", "002_HA NOI"]
```

---

## 🎯 Workflow Steps

Automation thực hiện 5 bước cho mỗi user:

1. **Login** → Đăng nhập admin (max 5 retries)
2. **Search User** → Tìm user theo username (max 5 retries)
3. **Change Role** → Đổi role nếu có (max 5 retries) - OPTIONAL
4. **Change Branch** → Đổi branch nếu có (max 5 retries) - OPTIONAL
5. **Save Changes** → Lưu thay đổi (max 3 retries)

**Retry Strategy:**
- Network errors: Exponential backoff (5s → 10s → 20s → 40s → 80s)
- Other errors: Linear backoff (2s → 4s → 6s)
- Circuit breaker: Tự động dừng sau 3 lỗi liên tiếp, chờ 60s

---

## 🐛 Troubleshooting

### Lỗi: "NOVA_ACT_API_KEY not found"

**Nguyên nhân:** File `.env` chưa được cấu hình

**Giải pháp:**
1. Mở file `.env`
2. Thêm dòng: `NOVA_ACT_API_KEY=your_actual_key`
3. Lưu file và chạy lại

### Lỗi: "File not found: input.json"

**Nguyên nhân:** File `input.json` không có hoặc sai vị trí

**Giải pháp:**
- Đảm bảo `input.json` nằm cùng folder với `csp_automation.exe`

### Lỗi: "Login failed after 5 attempts"

**Nguyên nhân:**
- Sai username/password
- Network không ổn định
- CSP Portal bị down

**Giải pháp:**
1. Kiểm tra lại username/password trong `input.json`
2. Kiểm tra kết nối internet
3. Thử login manual vào CSP Portal

### Lỗi: "User not found"

**Nguyên nhân:** Username không tồn tại trong hệ thống

**Giải pháp:**
- Kiểm tra lại `target_user` trong `input.json`
- Đảm bảo user đã được tạo trong CSP

### Program bị "stuck" không chạy

**Nguyên nhân:** Page loading lâu, AI agent đang chờ

**Giải pháp:**
- Đợi 2-3 phút
- Nếu vẫn stuck, bấm `Ctrl+C` để dừng
- Chạy lại program

### Xem Logs Chi Tiết

```cmd
# Mở file log mới nhất
cd logs\csp_admin_simple_v2
dir /O-D
notepad <execution_id>\automation.log
```

### Xem Screenshots Lỗi

```cmd
cd screenshots
# Mở folder có tên execution_id tương ứng
explorer <execution_id>_user1_<username>
```

---

## 📊 Monitoring & Logs

### Log Files

Logs được lưu tại:
```
logs/csp_admin_simple_v2/<execution_id>/automation.log
```

**Execution ID format:** `YYYYMMDD_HHMMSS` (VD: `20260105_143000`)

### Log Levels

- `INFO` - Thông tin chung
- `WARNING` - Cảnh báo (có retry)
- `ERROR` - Lỗi nghiêm trọng
- `DEBUG` - Debug chi tiết (nếu cần troubleshoot)

### Screenshots

Screenshots tự động được chụp khi:
- ✅ Login thành công
- ✅ Mở form edit user
- ✅ Trước khi save
- ✅ Sau khi save
- ❌ Khi có lỗi xảy ra

Lưu tại: `screenshots/<execution_id>_user<n>_<username>/`

---

## 🔐 Security Notes

### Bảo Mật Credentials

**QUAN TRỌNG:**
- ⚠️ **KHÔNG BAO GIỜ** commit file `.env` lên Git
- ⚠️ **KHÔNG BAO GIỜ** share file `.env` qua email/chat
- ⚠️ **KHÔNG BAO GIỜ** để file `.env` trong shared folder

### Best Practices

1. **Lưu `.env` local only** trên máy cá nhân
2. **Encrypt `.env`** nếu cần lưu trữ
3. **Đổi password định kỳ** trong CSP
4. **Revoke API key** khi không dùng nữa
5. **Kiểm tra logs** để đảm bảo không log sensitive data

---

## 🚀 Performance Tips

### Tối Ưu Tốc Độ

1. **Network ổn định:** Sử dụng kết nối có dây thay vì WiFi
2. **Đóng apps không cần:** Giải phóng RAM cho browser
3. **Batch nhỏ:** Xử lý 5-10 users/lần thay vì quá nhiều
4. **Chạy off-peak:** Chạy khi CSP Portal ít traffic

### Xử Lý Nhiều Users

Nếu có **nhiều hơn 50 users**, chia nhỏ:

**File:** `input_batch1.json`
```json
{
  "users": [
    // User 1-50
  ]
}
```

**File:** `input_batch2.json`
```json
{
  "users": [
    // User 51-100
  ]
}
```

Chạy từng batch:
```cmd
# Edit input.json → copy content từ input_batch1.json
csp_automation.exe

# Sau khi xong, edit input.json → copy content từ input_batch2.json
csp_automation.exe
```

---

## 📞 Support

### Liên Hệ

- **Technical Issues:** Tạo issue trên [GitHub](https://github.com/ngphthao10/POC-AI-AUTOMATION-APP/issues)
- **API Key:** Liên hệ Admin
- **CSP Portal Issues:** Liên hệ CSP Support Team

### Resources

- **Nova Act Documentation:** [Link if available]
- **Playwright Docs:** https://playwright.dev/python/

---

## 📝 Changelog

### Version 1.0.0 (2026-01-05)

**Features:**
- ✅ Console app với UI thân thiện
- ✅ Batch processing multiple users
- ✅ Smart retry với circuit breaker
- ✅ Auto screenshot on errors
- ✅ Comprehensive logging
- ✅ Windows build script

**Improvements:**
- Refactored codebase (~514 lines removed)
- Simplified retry logic (single layer)
- Removed unnecessary helpers
- Better error messages

**Known Issues:**
- Agent có thể stuck nếu page loading lâu (workaround: Ctrl+C và chạy lại)

---

## 📄 License

Internal use only - VIB Bank

---

**Built with ❤️ using Nova Act AI Agent**

**Last Updated:** January 5, 2026
