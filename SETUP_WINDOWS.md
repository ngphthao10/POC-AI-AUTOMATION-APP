# Hướng Dẫn Cài Đặt - CSP Automation (Windows)

## 📋 Yêu Cầu

- Windows 10 trở lên
- Quyền Administrator
- Có thể truy cập CSP Portal

---

## 🔧 Bước 1: Config Hosts File

Để app có thể kết nối tới CSP Portal (private domain), bạn cần thêm hostname vào hosts file.

### Cách Làm:

**1. Mở Notepad với quyền Administrator:**
- Click phải vào **Notepad**
- Chọn **"Run as administrator"**

**2. Mở file hosts:**
- Trong Notepad, chọn **File → Open**
- Paste đường dẫn này vào ô File name:
  ```
  C:\Windows\System32\drivers\etc\hosts
  ```
- Chọn **"All Files (*.*)"** trong dropdown (thay vì "Text Documents")
- Click **Open**

**3. Thêm dòng sau vào cuối file:**
```
10.50.142.37    csp.local
```

**4. Lưu file:**
- **File → Save** (hoặc Ctrl+S)
- Đóng Notepad

**5. Flush DNS cache:**

Mở **Command Prompt** (cmd) và chạy:
```cmd
ipconfig /flushdns
```

---

## ✅ Bước 2: Test Kết Nối

### Test 1: Ping hostname

Mở Command Prompt và chạy:
```cmd
ping csp.local
```

**Kết quả mong đợi:**
```
Reply from 10.50.142.37: bytes=32 time<1ms TTL=128
```

Nếu thấy "Reply from 10.50.142.37" → **OK!**

### Test 2: Test trên Browser

Mở Chrome/Edge, truy cập:
```
https://csp.local:7051/branchgui-web-client/portal/users/list
```

**Nếu thấy warning SSL:**
1. Click **"Advanced"**
2. Click **"Proceed to csp.local (unsafe)"**
3. Nếu thấy trang login CSP → **OK!**

---

## 🚀 Bước 3: Chạy Automation

### 1. Config file input.json

Đảm bảo `input.json` dùng hostname `csp.local`:

```json
{
  "admin_credentials": {
    "username": "mb\\your.username",
    "password": "your_password",
    "csp_admin_url": "https://csp.local:7051/branchgui-web-client/portal/users/list"
  },
  "users": [
    {
      "target_user": "user.name",
      "new_role": "CSP_Inquiry",
      "branch_hierarchy": null
    }
  ]
}
```

### 2. Chạy app

Double-click **csp_automation.exe**
