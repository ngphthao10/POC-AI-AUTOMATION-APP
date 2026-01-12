# Nova Act Best Practices

Tài liệu này tổng hợp các best practices khi sử dụng Amazon Nova Act, dựa trên kinh nghiệm thực tế và khuyến nghị từ AWS.

## Mục lục
- [Nguyên tắc cơ bản](#nguyên-tắc-cơ-bản)
- [Cách viết prompt hiệu quả](#cách-viết-prompt-hiệu-quả)
- [Kết hợp Nova Act với Playwright](#kết-hợp-nova-act-với-playwright)
- [Verification và Error Handling](#verification-và-error-handling)
- [Performance và Optimization](#performance-và-optimization)
- [Anti-patterns cần tránh](#anti-patterns-cần-tránh)

---

## Nguyên tắc cơ bản

### 1. Giới hạn số bước
Nova Act hoạt động tốt nhất khi task có thể hoàn thành trong **dưới 30 bước**. Nếu task phức tạp hơn, cần chia nhỏ thành nhiều act() calls.

### 2. Chia nhỏ task phức tạp
Thay vì một act() call lớn, chia thành nhiều bước nhỏ có thể kiểm soát và verify được.

**VÍ DỤ THỰC TẾ:**
```python
# ❌ KHÔNG NÊN: Một act() cho toàn bộ flow
self.nova.act("Search for user, open edit form, change role to Admin, and save")

# ✅ NÊN: Chia thành các bước rõ ràng
# Step 1: Search and open edit
self.nova.act("Click the Login field")
self.page.keyboard.type(target_user)
self.nova.act("Click the Search button")
self.nova.act("In the results table, click the first row's Actions dropdown and select Edit")

# Step 2: Change role
self.nova.act("Click the 'Roles' tab in the Edit user modal")
self.nova.act("In the FIRST Role row (top-most), click the dropdown arrow to open the role selector")
# ... các bước tiếp theo
```

---

## Cách viết prompt hiệu quả

### 1. Trực tiếp và súc tích (Direct and Succinct)

Viết prompt rõ ràng, chỉ định chính xác action cần thực hiện.

**❌ KHÔNG NÊN:**
```python
nova.act("Let's see what options we have here")
nova.act("Maybe try to save the changes")
```

**✅ NÊN:**
```python
nova.act("Click the green 'Save' button")
nova.act("Click the Cancel button or X button to close the modal")
```

### 2. Cung cấp hướng dẫn đầy đủ (Complete Instructions)

Chỉ định rõ ràng **vị trí, màu sắc, thứ tự** của UI elements.

**VÍ DỤ THỰC TẾ:**
```python
# Chỉ định vị trí cụ thể
self.nova.act("In the FIRST Role row (top-most), click the dropdown arrow to open the role selector")

# Chỉ định column trong hierarchical selector
self.nova.act("In the LEFTMOST column, click on 'Bank A'")
self.nova.act("In the MIDDLE column, click on 'Region North'")
self.nova.act("In the rightmost column, type 'Branch 001' in the search box, check the 'Branch 001' checkbox")

# Chỉ định màu sắc button
self.nova.act("Click the purple 'Select' button to confirm the selection")
self.nova.act("Click the green 'Save' button")
```

### 3. Sử dụng điều kiện và fallback

Xử lý các UI elements có thể không xuất hiện.

**VÍ DỤ THỰC TẾ:**
```python
# Expand filters nếu có
self.nova.act("Click 'More filters' if visible")
```

### 4. Explicit về thứ tự và vị trí

Khi có nhiều elements giống nhau, chỉ định rõ cái nào.

```python
# ❌ KHÔNG RÕ RÀNG
self.nova.act("Click the role dropdown")

# ✅ RÕ RÀNG
self.nova.act("In the FIRST Role row (top-most), click the dropdown arrow")
```

---

## Kết hợp Nova Act với Playwright

### 1. KHI NÀO DÙNG NOVA ACT vs PLAYWRIGHT

**Dùng Nova Act cho:**
- Navigation: click buttons, tabs, dropdowns
- UI interactions: select from dropdowns, click checkboxes
- Complex UI flows: multi-step selections

**Dùng Playwright cho:**
- **Sensitive data**: username, password, personal info
- **Typing text khi cần độ chính xác cao**
- **Keyboard shortcuts**: Control+A, Enter, Backspace
- **Verification**: wait_for_selector, count()

### 2. Ví dụ thực tế: Login (KHÔNG dùng Nova Act cho credentials)

```python
def login(self, username: str, password: str) -> bool:
    """
    ❌ KHÔNG BAO GIỜ: self.nova.act(f"Login with username {username} and password {password}")

    Lý do: Username và password sẽ bị log vào AI logs → security risk
    """

    # ✅ SỬ DỤNG PLAYWRIGHT cho sensitive data
    # Fill username
    username_selectors = ["input[name='username']", "input[type='text']"]
    for selector in username_selectors:
        locator = self.page.locator(selector).first
        if locator.count() > 0:
            locator.fill(username)
            break

    # Fill password
    password_selectors = ["input[name='password']", "input[type='password']"]
    for selector in password_selectors:
        locator = self.page.locator(selector).first
        if locator.count() > 0:
            locator.fill(password)
            break

    # Submit
    button = self.page.locator("button[type='submit']").first
    if button.count() > 0:
        button.click()
```

### 3. Ví dụ: Typing với Playwright (stability)

```python
# Nova Act mở dropdown
self.nova.act("In the FIRST Role row (top-most), click the dropdown arrow to open the role selector")
time.sleep(1.5)

# Nova Act click vào search field
self.nova.act("Click the select search field in the open dropdown")
time.sleep(1.5)

# Playwright typing (reliable, no AI logs)
self.page.keyboard.press("Control+A")
self.page.keyboard.press("Backspace")
time.sleep(0.3)
self.page.keyboard.type(new_role, delay=100)  # Type with delay for stability
time.sleep(2)

# Nova Act select từ filtered list
self.nova.act(f"In the dropdown list, click on the FIRST visible role option (should be '{new_role}' after filtering)")
```

---

## Verification và Error Handling

### 1. Sử dụng act_get() với Schema để verify

**VÍ DỤ THỰC TẾ:**
```python
from nova_act import BOOL_SCHEMA, ActInvalidModelGenerationError

# Check current state trước khi update
result = self.nova.act_get(
    f"Look at the FIRST Role field (top-most row). Does it already show '{new_role}'?",
    schema=BOOL_SCHEMA
)
if result.parsed_response:
    logger.info(f"Role already set to: {new_role}. Skipping update.")
    return True

# Verify sau khi update
result = self.nova.act_get(
    f"Look at the FIRST Role field (top-most row). Does it now show '{new_role}' as the selected value?",
    schema=BOOL_SCHEMA
)
if result.parsed_response:
    print(f"✓ Role '{new_role}' selected successfully")
else:
    raise Exception(f"Role field should show '{new_role}'")
```

### 2. Handle ActInvalidModelGenerationError

```python
try:
    result = self.nova.act_get(
        f"Look at the Scope field in the FIRST row. Does it now show the path with '{branch}'?",
        schema=BOOL_SCHEMA
    )
    if result.parsed_response:
        logger.debug("✓ Verification PASSED")
    else:
        raise Exception("Scope field should show selected branch path")
except ActInvalidModelGenerationError as e:
    logger.error(f"Verification INVALID: {str(e)}")
    raise Exception(f"Failed to verify Scope field: {str(e)}")
```

### 3. Verify với Playwright selectors

```python
def _verify_login(self) -> bool:
    try:
        self.page.wait_for_selector("text='Administration'", timeout=5000)
        logger.debug("Login verified - Administration menu found")
        return True
    except Exception as e:
        logger.error(f"Login verification failed: {e}")
        return False
```

---

## Performance và Optimization

### 1. Check state trước khi action

Tránh unnecessary actions bằng cách check trước.

```python
# Check if role is already correct
result = self.nova.act_get(
    f"Look at the FIRST Role field (top-most row). Does it already show '{new_role}'?",
    schema=BOOL_SCHEMA
)
if result.parsed_response:
    logger.info(f"Role already set to: {new_role}. Skipping update.")
    return True

# Only proceed if needed
# ... perform update
```

### 2. Time.sleep() hợp lý

Thêm delays giữa các bước để UI có thời gian render.

```python
self.nova.act("Click the Bank user field")
time.sleep(1)  # Wait for selector to open

self.nova.act("In the LEFTMOST column, click on 'Bank A'")
time.sleep(1)  # Wait for middle column to load

self.nova.act("In the MIDDLE column, click on 'Region North'")
time.sleep(1)  # Wait for rightmost column to load
```

**Guidelines:**
- Quick actions: 0.3-0.5s
- Normal actions: 1-1.5s
- Page/modal loads: 2-3s
- After typing: 0.3s
- After search/filter: 2s

### 3. Tách logic thành private methods

Khi workflow phức tạp, tách thành các methods nhỏ.

```python
def change_branch_hierarchical(self, branch_hierarchy: List[str]) -> bool:
    bank, region, branch = branch_hierarchy[0], branch_hierarchy[1], branch_hierarchy[2]

    # Step 1: Change Bank User
    self._change_bank_user(bank, region, branch)

    # Step 2: Change Scope
    self._change_scope(bank, region, branch)

    return True

def _change_bank_user(self, bank: str, region: str, branch: str):
    # Detailed implementation
    pass

def _change_scope(self, bank: str, region: str, branch: str):
    # Detailed implementation with verification
    pass
```

---

## Anti-patterns cần tránh

### 1. ❌ Prompt mơ hồ, không rõ ràng
```python
nova.act("Let's see what we can do here")
nova.act("Try to find the user")
```

### 2. ❌ Gộp quá nhiều actions trong một act()
```python
nova.act("Search for user, open edit, change role to Admin, change branch to HCM, and save")
```

### 3. ❌ Không verify kết quả
```python
self.nova.act("Select Admin role")
# Không check xem role đã được select chưa
```

### 4. ❌ Expose sensitive data trong Nova Act
```python
# DANGER!
self.nova.act(f"Type username '{username}' and password '{password}'")
```

### 5. ❌ Không chỉ định vị trí elements
```python
# Unclear khi có nhiều dropdowns
self.nova.act("Click the dropdown")

# Should be:
self.nova.act("In the FIRST Role row (top-most), click the dropdown arrow")
```

### 6. ❌ Không có time delays
```python
self.nova.act("Click Save")
self.nova.act("Click Next")  # Có thể chạy trước khi save hoàn tất
```

### 7. ❌ Không handle errors
```python
try:
    self.nova.act("Click the Save button")
    # Không có error handling
except:
    pass  # Swallow error
```

---

## Tổng kết Quick Reference

### DO ✅
- Viết prompt trực tiếp, rõ ràng, cụ thể
- Chia task lớn thành các bước nhỏ
- Verify kết quả sau actions quan trọng
- Dùng Playwright cho sensitive data và typing
- Chỉ định rõ vị trí UI elements (FIRST, LEFTMOST, etc.)
- Thêm time.sleep() giữa các bước
- Check state trước khi action (optimization)
- Handle exceptions và log errors

### DON'T ❌
- Viết prompt mơ hồ, không cụ thể
- Gộp nhiều actions trong một act()
- Expose sensitive data trong Nova Act prompts
- Skip verification steps
- Không chỉ định vị trí elements khi có nhiều cái giống nhau
- Quên thêm delays giữa các bước
- Swallow exceptions không xử lý

---

## Code Template

```python
from nova_act import NovaAct, ActInvalidModelGenerationError, BOOL_SCHEMA
import time
from shared.logger import setup_logger

logger = setup_logger(__name__)

class YourHandler:
    def __init__(self, nova: NovaAct):
        self.nova = nova
        self.page = nova.page

    def your_action(self, param: str) -> bool:
        try:
            logger.info(f"Starting action with: {param}")

            # Step 1: Navigate
            self.nova.act("Click the specific tab/button")
            time.sleep(1)

            # Step 2: Check current state (optimization)
            result = self.nova.act_get(
                f"Does field already show '{param}'?",
                schema=BOOL_SCHEMA
            )
            if result.parsed_response:
                logger.info("Already correct. Skipping.")
                return True

            # Step 3: Perform action (Nova Act for UI)
            self.nova.act("Click the FIRST dropdown in the top row")
            time.sleep(1)

            # Step 4: Type data (Playwright for stability/security)
            self.page.keyboard.type(param, delay=100)
            time.sleep(1)

            # Step 5: Confirm
            self.nova.act("Click the green 'Confirm' button")
            time.sleep(1.5)

            # Step 6: Verify result
            result = self.nova.act_get(
                f"Does field now show '{param}'?",
                schema=BOOL_SCHEMA
            )
            if not result.parsed_response:
                raise Exception(f"Verification failed: field should show '{param}'")

            logger.info("Action completed successfully")
            return True

        except ActInvalidModelGenerationError as e:
            logger.error(f"Invalid model generation: {e}")
            raise
        except Exception as e:
            logger.error(f"Action failed: {e}")
            raise
```

---

**Version:** 1.0
**Last Updated:** January 2026
**Tested on:** CSP Automation Project
