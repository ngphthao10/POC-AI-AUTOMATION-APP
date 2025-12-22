# Hướng Dẫn Sử Dụng Login với Nova Act và Browser Tool

## Tổng Quan

Dự án này demo cách sử dụng **Amazon Bedrock AgentCore Browser Tool** kết hợp với **Nova Act** để thực hiện tự động đăng nhập bằng natural language instructions.

Dựa trên hướng dẫn từ: `01_getting_started-agentcore-browser-tool-with-nova-act.ipynb`

## Kiến Trúc

```
┌─────────────────────────────────────────┐
│   Natural Language Instruction          │
│   "Log in with username X and pwd Y"    │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│           Nova Act SDK                   │
│   (Chuyển instruction thành actions)     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    Bedrock AgentCore Browser Tool        │
│    (Cung cấp CDP endpoint)               │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│       Playwright Actuations              │
│    (Thực hiện automation trên browser)   │
└─────────────────────────────────────────┘
```

## Cài Đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình AWS Credentials

Đảm bảo AWS credentials của bạn có đủ quyền cho Bedrock AgentCore Browser Tool.

Xem: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-onboarding.html#browser-credentials-config

```bash
aws configure
```

### 3. Set Nova Act API Key

```bash
export NOVA_ACT_API_KEY="your-nova-act-api-key"
```

Hoặc thêm vào file `.env`:
```
NOVA_ACT_API_KEY=your-nova-act-api-key
```

## Cách Sử Dụng

### Script 1: login_browser_automation.py (Simple Script)

Script đơn giản theo pattern của notebook, nhận natural language prompt trực tiếp:

```bash
python login_browser_automation.py \
  --prompt "Log in to the website with username 'mb\nghia.ht.dev' and password 'VIB@vib#21'" \
  --starting-page "https://10.50.142.37:7051/branchgui-web-client/portal/users/list" \
  --region "us-west-2"
```

**Parameters:**
- `--prompt`: Natural language instruction cho Nova Act
- `--starting-page`: URL trang login
- `--nova-act-key`: (Optional) Nova Act API key, hoặc dùng env variable
- `--region`: (Optional) AWS region, default: us-west-2

### Script 2: login_with_browser_tool.py (Class-based)

Script có cấu trúc class, hỗ trợ 2 methods:

#### Method 1: Multi-step (Recommended)
Chia thành nhiều bước rõ ràng: điền username → điền password → click login → verify

```bash
python src/features/login/login_with_browser_tool.py --method multi
```

#### Method 2: Single-prompt
Một prompt duy nhất cho toàn bộ flow login:

```bash
python src/features/login/login_with_browser_tool.py --method single
```

**Parameters:**
- `--username`: Username (hoặc đọc từ input.json)
- `--password`: Password (hoặc đọc từ input.json)
- `--method`: `multi` hoặc `single`
- `--region`: AWS region
- `--config`: Path to config.json

## Cấu Trúc File

```
poc-ai-automation-app/
├── login_browser_automation.py           # Simple script theo pattern notebook
├── src/features/login/
│   ├── login_with_browser_tool.py       # Class-based implementation
│   ├── login_handler.py                 # Old version (Playwright only)
│   ├── login_handler_nova_act.py        # Nova Act version (không dùng browser_session)
│   └── config.json                      # Login configuration
├── requirements.txt                      # Dependencies
└── .env                                 # Environment variables
```

## So Sánh Các Approaches

### 1. login_handler.py (Old - Playwright Only)
- ❌ Sử dụng Playwright selectors trực tiếp
- ❌ Cần maintain selectors khi UI thay đổi
- ✅ Không cần Nova Act API key
- ✅ Nhanh và deterministic

### 2. login_handler_nova_act.py (Nova Act - No Browser Tool)
- ✅ Sử dụng natural language
- ❌ Không dùng Bedrock AgentCore Browser Tool
- ❌ Tạo NovaAct instance trực tiếp (local browser)

### 3. login_browser_automation.py (Recommended)
- ✅ Sử dụng Bedrock AgentCore Browser Tool
- ✅ Natural language instructions
- ✅ Theo pattern của notebook
- ✅ Managed browser session qua AWS
- ✅ Scalable và secure

## Ví Dụ Prompts

### Single Prompt Example:
```python
prompt = """
Log in to the CSP portal with these credentials:
- Username: mb\nghia.ht.dev
- Password: VIB@vib#21

Steps:
1. Fill the username field
2. Fill the password field
3. Click the login button
4. Verify successful login
"""
```

### Multi-step Example:
```python
# Step 1
"Fill in the username field with 'mb\nghia.ht.dev'"

# Step 2
"Fill in the password field with 'VIB@vib#21'"

# Step 3
"Click the login button to submit"

# Step 4
"Verify the login was successful"
```

## Troubleshooting

### Lỗi: "NovaAct error"
- Kiểm tra Nova Act API key đã được set chưa
- Verify network connection

### Lỗi: AWS credentials
- Chạy `aws configure` để setup credentials
- Verify IAM permissions cho Bedrock AgentCore

### SSL Certificate Error
- Thêm vào .env:
  ```
  NODE_TLS_REJECT_UNAUTHORIZED=0
  PYTHONHTTPSVERIFY=0
  ```

## Best Practices

1. **Sử dụng Multi-step method** cho stability và debugging
2. **Clear và specific prompts** để Nova Act hiểu đúng
3. **Verify login success** sau khi login
4. **Handle errors gracefully** với try-catch
5. **Log actions** để debug khi cần

## References

- Notebook: `01_getting_started-agentcore-browser-tool-with-nova-act.ipynb`
- AWS Bedrock AgentCore Docs: https://docs.aws.amazon.com/bedrock-agentcore/
- Nova Act Docs: [Nova Act Documentation]

## License

Internal use only
