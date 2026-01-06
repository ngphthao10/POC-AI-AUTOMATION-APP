# Hướng Dẫn Build Lại với Playwright Bundled

## Chuẩn Bị

**Đã cài đặt trong venv:**
- Python packages (pip install -r requirements.txt)
- VIB certificate trong venv\Lib\site-packages\certifi\cacert.pem
- Playwright browsers: `playwright install chromium`

## Các Thay Đổi Mới

✅ **Build script đã được update:**
- Tự động copy Playwright browsers vào dist\ms-playwright
- App sẽ tự động tìm browsers từ folder bundled
- Không cần cài Playwright trên máy target

## Cách Build

**Bước 1:** Đảm bảo đã cài Playwright browsers
```bash
venv\Scripts\activate
playwright install chromium
```

**Bước 2:** Chạy build
```bash
build.bat
```

**Bước 3:** Kiểm tra dist folder
```
dist\
├── csp_automation.exe
├── ms-playwright\          ← ~400MB browsers
│   └── chromium-xxxx\
├── input.json
├── .env
├── template.json
├── logs\
└── screenshots\
```

**Bước 4:** Zip toàn bộ folder dist
```
Zip name: csp_automation_portable.zip
Size: ~450MB (bao gồm browsers)
```

## Gửi cho Team Test

**Package gửi đi:** csp_automation_portable.zip (~450MB)

**Hướng dẫn:**
1. Extract zip
2. Chỉnh sửa input.json và .env
3. Chạy csp_automation.exe
4. KHÔNG cần cài Python/Playwright

## Lưu Ý

- ⚠️ Playwright browsers chiếm ~400MB
- ✅ Portable, chạy được trên mọi máy Windows
- ✅ Đã bundled VIB certificate
- ✅ Không cần setup gì thêm trên máy target
