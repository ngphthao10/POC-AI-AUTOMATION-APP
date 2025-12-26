# HƯỚNG DẪN MIGRATE SANG POWER AUTOMATE DESKTOP

## 1. SO SÁNH CÔNG NGHỆ

| | AWS Nova Act | Power Automate | Playwright |
|---|---|---|---|
| **Loại** | AI Vision Agent | RPA với UI Builder | Code-based Browser Automation |
| **Approach** | Prompt AI → AI tự click | Record/Build flow → Replay | Code selectors → Execute |
| **Speed** | Chậm (AI thinking) | Nhanh | Nhanh nhất |
| **Reliability** | 70-85% | 95-99% | 98-99% |
| **Cost** | $$$ (API calls) | FREE | FREE |
| **Skill** | Viết prompts | Kéo thả UI | Code Python/JS |

**Kết luận:** Power Automate ≈ Playwright nhưng có UI Builder, dễ maintain hơn code.

---

## 2. CÀI ĐẶT

### Power Automate Desktop
1. **Download**: [Microsoft Power Automate Desktop](https://www.microsoft.com/en-us/power-platform/products/power-automate)
2. **Cài đặt**: Free, đi kèm Windows 10/11
3. **Sign in**: Dùng Microsoft account

---

## 3. SO SÁNH CODE

### Ví dụ: Click button "Submit"

**Nova Act (hiện tại):**
```python
nova.act("Click the Submit button")
# → AI tự tìm và click, mất ~5-10s
```

**Playwright (alternative):**
```python
page.click("button:has-text('Submit')")
# → Selector cụ thể, <1s
```

**Power Automate Desktop:**
```
[UI automation] Click button
  Selector: button[text='Submit']
  Wait: 5 seconds
```
→ Kéo thả block, config selector qua UI

---

## 4. WORKFLOW MIGRATE

### Bước 1: Record flow
1. Mở Power Automate Desktop
2. New Flow → "CSP Change Branch"
3. Click **"Recorder"** → record thao tác trên CSP
4. Thực hiện thao tác thủ công 1 lần
5. Stop recording → Flow tự generate

### Bước 2: Edit flow
1. Review các steps được record
2. Thay giá trị hardcode bằng variables:
   - `bank`, `region`, `branch`
   - `username`, `password`
3. Thêm loops cho multiple users
4. Thêm error handling

### Bước 3: Parametrize
```
Input: JSON file (như hiện tại)
Loop: For each user in users
  - Login CSP
  - Search user
  - Change role (if needed)
  - Change branch (if needed)
  - Verify
  - Logout
Output: Success/Fail log
```

### Bước 4: Integration với Python
Power Automate có thể gọi Python script:
```python
# Giữ lại Python logic hiện tại
# Power Automate chỉ làm UI automation
```

---

## 5. SELECTORS

### Power Automate tự generate selectors khi record:

**Ví dụ selector cho CSP:**
```
// Input field username
input[name='username']

// Button login
button:contains('Login')

// Dropdown region
select[id='region-selector']

// Tree node "VIB Bank"
treeitem[text='VIB Bank']
```

**Giống Playwright:**
```python
# Playwright
page.fill("input[name='username']", username)
page.click("button:has-text('Login')")

# Power Automate (UI)
[Fill text field] input[name='username'] with {username}
[Click button] button:contains('Login')
```

---

## 6. XỬ LÝ HIERARCHICAL TREE

### CSP có hierarchical selector (Bank → Region → Branch)

**Nova Act (hiện tại - chậm):**
```python
nova.act("Click VIB Bank")  # AI thinking: 5s
nova.act("Click North")     # AI thinking: 5s
nova.act("Click 403")       # AI thinking: 5s
# Total: ~15s
```

**Power Automate (nhanh):**
```
[Click] treeitem[text='VIB Bank']     # <1s
[Wait] 1 second
[Click] treeitem[text='North']        # <1s
[Wait] 1 second
[Click] treeitem[text='403']          # <1s
# Total: ~3s
```

---

## 7. ERROR HANDLING

### Power Automate có built-in error handling:

```
Try:
  [Click button] Submit
Catch Exception:
  [Take screenshot] error.png
  [Log error] to file
  [Retry] 3 times
Finally:
  [Close browser]
```

→ Tương tự try/catch trong Python

---

## 8. KẾT HỢP PYTHON + POWER AUTOMATE

### Approach hybrid (recommended):

**Python (business logic):**
```python
# Đọc input.json
# Parse data
# Validate
# Generate output report
```

**Power Automate (UI automation):**
```
# Login CSP
# Navigate UI
# Fill forms
# Click buttons
# Get results
```

**Integration:**
```
Power Automate → Call Python script
Python → Return data to Power Automate
Power Automate → Continue flow
```

---

## 9. ƯU NHƯỢC ĐIỂM

### ✅ Ưu điểm Power Automate:
- **FREE** - không tốn API cost
- **Nhanh** - 5-10x nhanh hơn Nova Act
- **Deterministic** - kết quả ổn định
- **Easy to maintain** - visual flow dễ hiểu
- **Built-in error handling**
- **Desktop + Cloud** - có thể chạy headless trên VM

### ⚠️ Nhược điểm:
- **Selector maintenance** - UI thay đổi phải update
- **Windows only** - không chạy Linux/Mac
- **Learning curve** - phải học UI builder
- **Less flexible** than code

---

## 10. RECOMMENDATION

### Chọn Power Automate nếu:
✅ CSP UI **ít thay đổi**
✅ Cần **speed + stability**
✅ Muốn **FREE solution**
✅ Team không quen code Playwright
✅ Chạy trên **Windows environment**

### Giữ Nova Act nếu:
❌ CSP UI **thay đổi liên tục**
❌ Không có Windows máy
❌ Cần AI adaptive behavior

### Chuyển sang Playwright nếu:
🎯 Team quen **Python coding**
🎯 Muốn **cross-platform** (Linux/Mac/Windows)
🎯 Cần **CI/CD integration**
🎯 Muốn **fastest performance**

---

## 11. NEXT STEPS

1. **Demo**: Record 1 flow đơn giản (login CSP)
2. **POC**: Implement change branch flow
3. **Test**: So sánh speed vs Nova Act
4. **Decide**: Migrate toàn bộ hoặc giữ lại
5. **Production**: Deploy và monitor

---

**Kết luận:** Power Automate Desktop là **middle ground** giữa Nova Act (quá chậm) và Playwright (cần code nhiều). Phù hợp cho use case CSP automation.
