# 🤖 Hướng Dẫn Sử Dụng AI Automation App

Ứng dụng tự động hóa AI giúp thực hiện các tác vụ quản trị CSP Admin một cách tự động thông qua giao diện console.

## 📋 Mục Lục

- [Giới thiệu](#-giới-thiệu)
- [Cài đặt và Chạy ứng dụng](#-cài-đặt-và-chạy-ứng-dụng)
- [Cấu hình File JSON](#-cấu-hình-file-json)
- [Hướng dẫn sử dụng từng tính năng](#-hướng-dẫn-sử-dụng-từng-tính-năng)
- [Xử lý lỗi thường gặp](#-xử-lý-lỗi-thường-gặp)
- [FAQ](#-faq)

## 🎯 Giới thiệu

AI Automation App là một ứng dụng console hỗ trợ tự động hóa các tác vụ quản trị hệ thống CSP, bao gồm:

- **CSP Admin**: Tự động thay đổi vai trò và chi nhánh cho người dùng
- Các tính năng khác sẽ được bổ sung trong tương lai

## 🚀 Cài đặt và Chạy ứng dụng

### Phương pháp 1: Chạy file thực thi đã build (Khuyến nghị)

1. **Tải file ứng dụng:**
   - Windows: `ai_automation_app.exe` 
   - macOS: `ai_automation_app`
   - Linux: `ai_automation_app`

2. **Chạy ứng dụng:**
   ```bash
   # Windows
   ai_automation_app.exe
   
   # macOS/Linux
   ./ai_automation_app
   ```

### Phương pháp 2: Chạy từ source code

1. **Cài đặt Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Chạy ứng dụng:**
   ```bash
   python console_app.py
   ```

## 📝 Cấu hình File JSON

### Vị trí file cấu hình

File `input.json` phải được đặt **cùng thư mục** với file thực thi của ứng dụng:

```
📁 Thư mục ứng dụng/
├── ai_automation_app.exe    # File thực thi (Windows)
├── ai_automation_app        # File thực thi (macOS/Linux) 
└── input.json              # File cấu hình (PHẢI có)
```

### Cấu trúc file input.json

```json
{
  "admin_credentials": {
    "username": "tên_đăng_nhập_admin",
    "password": "mật_khẩu_admin", 
    "csp_admin_url": "https://địa_chỉ_csp_portal.com/portal/users/list"
  },
  "users": [
    {
      "target_user": "email_người_dùng_1@example.com",
      "new_role": "CSP-RB-TELLER",
      "branch_hierarchy": ["VIB Bank", "North", "002"]
    },
    {
      "target_user": "email_người_dùng_2@example.com",
      "new_role": "CSP_Inquiry", 
      "branch_hierarchy": ["VIB Bank", "South", "403"]
    }
  ]
}
```

### Chi tiết từng trường

#### 1. admin_credentials (Bắt buộc)

| Trường | Mô tả | Ví dụ |
|--------|-------|-------|
| `username` | Tên đăng nhập admin CSP | `"admin_user"` |
| `password` | Mật khẩu admin CSP | `"password123"` |
| `csp_admin_url` | URL trang quản lý users | `"https://csp-portal.com/portal/users/list"` |

#### 2. users (Mảng người dùng cần xử lý)

| Trường | Mô tả | Bắt buộc | Ví dụ |
|--------|-------|----------|-------|
| `target_user` | Email/username người dùng | ✅ Có | `"user@example.com"` |
| `new_role` | Vai trò mới cần gán | ❌ Không | `"CSP-RB-TELLER"` |
| `branch_hierarchy` | Cấu trúc chi nhánh | ❌ Không | `["VIB Bank", "North", "002"]` |

#### Cấu trúc chi nhánh:
```json
["Tên Bank", "Vùng", "Mã Chi nhánh"]
```

Ví dụ:
- `["VIB Bank", "North", "002"]` - Chi nhánh 002 vùng Bắc
- `["VIB Bank", "South", "403"]` - Chi nhánh 403 vùng Nam
- `null` - Không thay đổi chi nhánh

### Ví dụ file input.json hoàn chỉnh

```json
{
  "admin_credentials": {
    "username": "mb\\admin.user",
    "password": "AdminPass@2024",
    "csp_admin_url": "https://10.50.142.37:7051/branchgui-web-client/portal/users/list"
  },
  "users": [
    {
      "target_user": "nguyen.vana",
      "new_role": "CSP-RB-TELLER", 
      "branch_hierarchy": ["VIB Bank", "North", "002"]
    },
    {
      "target_user": "tran.thib",
      "new_role": "CSP_Inquiry",
      "branch_hierarchy": null
    },
    {
      "target_user": "le.vanc", 
      "new_role": null,
      "branch_hierarchy": ["VIB Bank", "South", "403"]
    }
  ]
}
```

## 🎮 Hướng dẫn sử dụng từng tính năng

### CSP Admin - Thay đổi vai trò và chi nhánh

1. **Khởi động ứng dụng**
   ```bash
   ./ai_automation_app
   ```

2. **Chọn tính năng CSP Admin**
   - Nhập `1` trong menu chính
   - Chọn "CSP Admin - Thay đổi vai trò và chi nhánh"

3. **Menu CSP Admin có các tùy chọn:**
   - `1`: 🚀 Chạy tự động hóa CSP
   - `2`: 📄 Xem file đầu vào hiện tại
   - `3`: 📝 Xem định dạng mẫu
   - `4`: ← Quay lại menu chính

4. **Xem file đầu vào (tùy chọn 2)**
   - Hiển thị nội dung file `input.json` hiện tại
   - Giúp kiểm tra cấu hình trước khi chạy

5. **Xem định dạng mẫu (tùy chọn 3)**
   - Hiển thị template file JSON mẫu
   - Copy và chỉnh sửa theo nhu cầu

6. **Chạy tự động hóa (tùy chọn 1)**
   - Ứng dụng sẽ đọc và kiểm tra file `input.json`
   - Hiển thị danh sách users sẽ được xử lý
   - Xác nhận trước khi chạy
   - Chọn số lượng worker song song (1-4)
   - Bắt đầu quá trình tự động hóa

### Quy trình tự động hóa

1. **Đọc file cấu hình**: Load `input.json` từ thư mục ứng dụng
2. **Xác thực thông tin**: Kiểm tra định dạng và tính hợp lệ
3. **Hiển thị preview**: Danh sách users và thay đổi sẽ thực hiện
4. **Xác nhận**: Người dùng confirm trước khi chạy
5. **Tự động hóa trình duyệt**: Mở browser và thực hiện các thao tác
6. **Lưu kết quả**: Xuất báo cáo JSON với chi tiết từng user

## ⚠️ Xử lý lỗi thường gặp

### Lỗi: "Không tìm thấy file input.json"

**Nguyên nhân**: File `input.json` không ở cùng thư mục với ứng dụng

**Giải pháp**:
1. Tạo file `input.json` trong cùng thư mục với file thực thi
2. Copy template từ tùy chọn "Xem định dạng mẫu"
3. Chỉnh sửa thông tin phù hợp

### Lỗi: "JSON không hợp lệ"

**Nguyên nhân**: Syntax lỗi trong file JSON

**Giải pháp**:
1. Kiểm tra dấu phạy, ngoặc đúng định dạng
2. Sử dụng JSON validator online 
3. So sánh với template mẫu

### Lỗi: "Nova Act API key not configured"

**Nguyên nhân**: Chưa cấu hình API key

**Giải pháp**:
1. Liên hệ admin để lấy Nova Act API key
2. Cập nhật key trong file cấu hình (nếu chạy từ source)

## ❓ FAQ

### Q: File input.json có cần đặt ở đâu?
**A**: Phải đặt cùng thư mục với file thực thi ứng dụng.

### Q: Có thể xử lý bao nhiêu user cùng lúc?
**A**: Không giới hạn số lượng user, nhưng khuyến nghị batch 10-20 users để tối ưu hiệu suất.

### Q: Ứng dụng có lưu lại mật khẩu không?
**A**: Không. Mật khẩu chỉ được đọc từ file JSON khi chạy và không lưu trữ ở đâu khác.

### Q: Có thể chạy nhiều lần liên tiếp không?
**A**: Có, chỉ cần cập nhật file `input.json` và chạy lại.

### Q: Làm sao biết quá trình thành công?
**A**: Ứng dụng sẽ hiển thị trạng thái real-time và lưu kết quả chi tiết vào file JSON.

### Q: Có thể dừng giữa chừng không?
**A**: Có, nhấn `Ctrl+C` để dừng. Các thao tác đã hoàn thành sẽ được giữ nguyên.

## 📞 Hỗ trợ

Nếu gặp vấn đề:

1. **Kiểm tra file log** được tạo cùng thư mục ứng dụng
2. **Xem thông báo lỗi** chi tiết trong console
3. **Liên hệ team phát triển** với thông tin lỗi cụ thể

---

**Lưu ý**: Ứng dụng yêu cầu quyền truy cập internet và có thể cần quyền quản trị để chạy trình duyệt tự động.
