# 🤖 Hướng Dẫn Sử Dụng AI Automation App

Ứng dụng tự động hóa AI sử dụng Amazon Nova Act để thực hiện các tác vụ quản trị CSP Admin một cách tự động thông qua giao diện console với chế độ single worker đảm bảo tính ổn định.

## 📋 Mục Lục

- [Giới thiệu](#-giới-thiệu)
- [Cài đặt và Chạy ứng dụng](#-cài-đặt-và-chạy-ứng-dụng)
- [Cấu hình File JSON](#-cấu-hình-file-json)
- [Hướng dẫn sử dụng từng tính năng](#-hướng-dẫn-sử-dụng-từng-tính-năng)
- [Thay đổi gần đây](#-thay-đổi-gần-đây)
- [Xử lý lỗi thường gặp](#-xử-lý-lỗi-thường-gặp)
- [FAQ](#-faq)

## 🎯 Giới thiệu

AI Automation App là một ứng dụng console sử dụng **Amazon Nova Act** để tự động hóa các tác vụ quản trị hệ thống CSP, bao gồm:

- **CSP Admin**: Tự động thay đổi vai trò và chi nhánh cho người dùng sử dụng hệ thống điều hướng phân cấp
- **Chế độ Single Worker**: Đảm bảo tính ổn định bằng cách xử lý tuần tự từng người dùng
- **Nova Act Integration**: Sử dụng AI browser automation của Amazon để thực hiện các thao tác web
- Các tính năng khác sẽ được bổ sung trong tương lai

### Công nghệ sử dụng
- **Amazon Nova Act**: AI-powered browser automation
- **Python 3.10+**: Ngôn ngữ lập trình chính
- **PyInstaller**: Đóng gói thành file thực thi độc lập
- **Pydantic**: Validation dữ liệu JSON

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

**Lưu ý quan trọng**: Ứng dụng hiện sử dụng hệ thống điều hướng phân cấp (`branch_hierarchy`) thay vì `new_branch` đơn giản để đảm bảo tính chính xác và nhất quán.

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

#### Cấu trúc chi nhánh phân cấp:
```json
["Tên Bank", "Vùng", "Mã Chi nhánh"]
```

Ví dụ:
- `["VIB Bank", "North", "002"]` - Chi nhánh 002 vùng Bắc
- `["VIB Bank", "South", "403"]` - Chi nhánh 403 vùng Nam
- `null` - Không thay đổi chi nhánh

**Tính năng tương thích ngược**: Nếu sử dụng `new_branch` thay vì `branch_hierarchy`, hệ thống sẽ tự động chuyển đổi sang định dạng phân cấp với vùng mặc định là "North".

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
   - **Ứng dụng chạy ở chế độ single worker để đảm bảo tính ổn định và tránh xung đột session**
   - Bắt đầu quá trình tự động hóa với Amazon Nova Act AI browser automation

### Quy trình tự động hóa

1. **Đọc file cấu hình**: Load `input.json` từ thư mục ứng dụng
2. **Xác thực thông tin**: Kiểm tra định dạng và tính hợp lệ với Pydantic validation
3. **Hiển thị preview**: Danh sách users và thay đổi sẽ thực hiện
4. **Xác nhận**: Người dùng confirm trước khi chạy
5. **Nova Act Browser Automation**: Mở browser và thực hiện các thao tác bằng AI
6. **Xử lý tuần tự**: Từng user được xử lý riêng biệt (single worker mode)
7. **Lưu kết quả**: Xuất báo cáo JSON với chi tiết từng user
8. **Debug logs**: Tạo file log chi tiết và HTML trace files cho debugging

## 🔄 Thay đổi gần đây

### Cải tiến Hệ thống Điều hướng Chi nhánh (Refactoring v2.0)

#### 🎯 **Thay đổi chính**
- **Gộp phương thức**: Loại bỏ `change_bank_user_hierarchical` và `change_user_branch`, chỉ sử dụng `change_user_branch_hierarchical`
- **Single Worker Mode**: Chuyển từ xử lý song song sang tuần tự để tăng độ tin cậy
- **Nova Act Integration**: Nâng cấp lên Amazon Nova Act 2.0 với AI browser automation

#### ✅ **Lợi ích**
1. **Tính nhất quán**: Tất cả thay đổi chi nhánh dùng cùng một phương thức
2. **Độ tin cậy**: Single worker tránh xung đột session và lỗi race condition  
3. **Bảo trì dễ dàng**: Ít code hơn, logic đơn giản hơn
4. **AI-Powered**: Sử dụng Amazon Nova Act để automation thông minh hơn

#### 🔄 **Tương thích ngược**
- File cấu hình cũ vẫn hoạt động
- `new_branch` tự động chuyển đổi thành `branch_hierarchy`
- Không cần thay đổi cấu hình hiện tại

### Cải tiến Kỹ thuật

#### **Amazon Nova Act Integration**
- **AI Browser Automation**: Thay thế automation thủ công bằng AI
- **Trace Files**: Tạo HTML trace files cho debugging chi tiết
- **Error Recovery**: Xử lý lỗi thông minh với AI
- **Multi-platform**: Hỗ trợ Windows, macOS, Linux

#### **Single Worker Architecture**
- **Tính ổn định**: Xử lý tuần tự tránh xung đột
- **Resource Management**: Quản lý tài nguyên browser hiệu quả
- **Error Isolation**: Lỗi ở một user không ảnh hưởng user khác
- **Debugging**: Dễ debug và trace lỗi

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

**Nguyên nhân**: Chưa cấu hình API key cho Amazon Nova Act

**Giải pháp**:
1. Liên hệ admin để lấy Nova Act API key từ https://nova.amazon.com/act
2. Cập nhật key trong file cấu hình (nếu chạy từ source)
3. Đối với file thực thi, API key đã được cấu hình sẵn

### Lỗi: "Browser automation failed"

**Nguyên nhân**: Lỗi trong quá trình automation browser với Nova Act

**Giải pháp**:
1. Kiểm tra file HTML trace được tạo trong thư mục logs
2. Đảm bảo kết nối internet ổn định
3. Kiểm tra URL CSP admin có đúng không
4. Thử chạy lại với một user để test

### Lỗi: "Session conflict detected"

**Nguyên nhân**: Có thể có session browser xung đột

**Giải pháp**:
1. Đóng tất cả browser đang chạy
2. Xóa thư mục temp browser data
3. Chạy lại ứng dụng
4. Single worker mode sẽ tránh vấn đề này

## ❓ FAQ

### Q: File input.json có cần đặt ở đâu?
**A**: Phải đặt cùng thư mục với file thực thi ứng dụng.

### Q: Có thể xử lý bao nhiêu user cùng lúc?
**A**: Ứng dụng xử lý tuần tự từng user (single worker mode) để đảm bảo tính ổn định. Không giới hạn số lượng user trong một lần chạy, nhưng khuyến nghị batch 10-20 users để tối ưu hiệu suất.

### Q: Ứng dụng có lưu lại mật khẩu không?
**A**: Không. Mật khẩu chỉ được đọc từ file JSON khi chạy và sử dụng qua Nova Act API. Không lưu trữ ở đâu khác và được xóa sau khi kết thúc session.

### Q: Có thể chạy nhiều lần liên tiếp không?
**A**: Có, chỉ cần cập nhật file `input.json` và chạy lại. Single worker mode đảm bảo không xung đột giữa các lần chạy.

### Q: Làm sao biết quá trình thành công?
**A**: Ứng dụng sẽ hiển thị trạng thái real-time, lưu kết quả chi tiết vào file JSON, và tạo HTML trace files cho debugging.

### Q: Có thể dừng giữa chừng không?
**A**: Có, nhấn `Ctrl+C` để dừng. Các thao tác đã hoàn thành sẽ được giữ nguyên nhờ single worker mode.

### Q: Tại sao chuyển sang single worker mode?
**A**: Để tăng độ tin cậy và ổn định. Parallel processing có thể gây xung đột browser session và khó debug. Single worker dễ quản lý và trace lỗi hơn.

### Q: Nova Act trace files là gì?
**A**: Là file HTML chi tiết ghi lại từng bước automation của browser, giúp debug khi có lỗi. File được lưu trong thư mục logs với tên có timestamp.

### Q: Có thể chạy headless (không hiển thị browser) không?
**A**: Có, Nova Act hỗ trợ headless mode. Có thể cấu hình trong code hoặc liên hệ team phát triển để enable.

## 📞 Hỗ trợ

Nếu gặp vấn đề:

1. **Kiểm tra file log** được tạo cùng thư mục ứng dụng (format: `csp_automation_[timestamp].log`)
2. **Kiểm tra HTML trace files** trong thư mục logs để xem chi tiết automation
3. **Xem thông báo lỗi** chi tiết trong console
4. **Liên hệ team phát triển** với thông tin:
   - Mô tả lỗi cụ thể
   - File log và trace files
   - Cấu hình input.json (đã ẩn password)
   - Screenshots nếu có

### Debug Information
- **Log files**: `csp_automation_[timestamp].log` 
- **Nova Act traces**: HTML files trong thư mục logs
- **Console output**: Real-time status và error messages
- **JSON results**: File kết quả với timestamp

---

**Lưu ý**: 
- Ứng dụng yêu cầu quyền truy cập internet và Nova Act API key
- Có thể cần quyền quản trị để chạy browser automation
- Single worker mode đảm bảo tính ổn định nhưng thời gian xử lý sẽ lâu hơn khi có nhiều user
