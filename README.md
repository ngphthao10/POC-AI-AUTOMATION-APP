# CSP Automation Application

Ứng dụng Python tự động hóa quản trị CSP (Customer Service Portal) sử dụng Amazon Nova Act AI.

## Tính năng

- Tự động thay đổi vai trò và chi nhánh người dùng CSP
- AI-powered browser automation với Amazon Nova Act
- Console interface bằng tiếng Việt
- JSON configuration
- Logging và tracing chi tiết

## Yêu cầu

- **Windows 10+** (khuyến nghị - không cần code signing)
- macOS 10.13+ (cần thêm bước bypass Gatekeeper - xem hướng dẫn dưới)
- Python 3.10+ (nếu chạy từ source code)
- Internet connection
- Nova Act API key

## Cài đặt & Chạy

### Chạy trực tiếp

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Cài đặt Playwright browsers
playwright install chromium

# Chạy ứng dụng
python console_app.py
```

### Build executable

**macOS/Linux:**
```bash
# Build với Makefile
make build

# Hoặc chạy script trực tiếp
bash build_new.sh
```

**Windows:**
```cmd
build.bat
```

**Chạy sau khi build:**
```bash
cd dist
./launch.sh       # macOS/Linux
launch.bat        # Windows
```

**Lưu ý:** Build script tự động bundle Playwright browsers (~300MB) vào dist/ để end-users không cần cài thêm gì.

## Cấu hình

### 1. Nova Act API Key

Tạo file `.env`:
```
NOVA_ACT_API_KEY=your_api_key_here
```

### 2. Input Configuration

Tạo file `input.json`:
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

## Cấu trúc thư mục

```
├── console_app.py          # Entry point
├── requirements.txt        # Dependencies
├── Makefile               # Build commands
├── build_new.sh           # Build script
├── csp_automation.spec    # PyInstaller config
├── .env                   # API keys
├── input.json             # Configuration
├── src/                   # Source code
│   ├── csp/              # CSP automation modules
│   ├── features/         # Feature modules
│   └── shared/           # Shared utilities
├── logs/                  # Log files
├── screenshots/           # Debug screenshots
└── dist/                  # Build output
```

## Build commands

```bash
make build        # Build executable
make build-fast   # Build without clean
make package      # Build + create zip
make clean        # Clean build artifacts
make run          # Run dev mode
```

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. File log trong `logs/`
2. Screenshots trong `screenshots/`
3. Cấu hình `.env` và `input.json`

## Troubleshooting

### macOS: "Cannot verify that it is free from malware"

**Vấn đề:** macOS Gatekeeper chặn ứng dụng vì không được code-sign với Apple Developer certificate.

**Giải pháp 1 - Workaround cho người dùng (Khuyến nghị):**

Sau khi giải nén `dist.zip`, chạy lệnh sau để gỡ bỏ quarantine flag:

```bash
cd /path/to/dist
xattr -cr .
```

Sau đó có thể chạy `./launch.sh` bình thường.

**Giải pháp 2 - Sử dụng Windows (Đơn giản nhất):**

Build và phân phối trên Windows không gặp vấn đề này. Chạy `build.bat` trên máy Windows.

**Giải pháp 3 - Code Signing (Tốn phí):**

Nếu cần phân phối chính thức cho macOS, cần:
- Apple Developer Account ($99/năm)
- Code sign với `codesign` command
- Notarize với Apple
