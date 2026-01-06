# Setup AWS Credentials cho Nova Act Workflow

## Cách 1: Dùng AWS CLI (Khuyến nghị)

### Bước 1: Cài đặt AWS CLI
Download từ: https://aws.amazon.com/cli/

### Bước 2: Configure credentials
```bash
aws configure
```

Nhập thông tin:
```
AWS Access Key ID: [Your Access Key]
AWS Secret Access Key: [Your Secret Key]
Default region name: ap-southeast-1
Default output format: json
```

### Bước 3: Verify
```bash
aws sts get-caller-identity
```

---

## Cách 2: Dùng Environment Variables (Đơn giản hơn)

Thêm vào file `.env`:
```env
# Nova Act API Key Mode (comment out nếu dùng Workflow)
# NOVA_ACT_API_KEY=667f1144-738f-4c84-acce-f07ed3cb1661

# AWS Credentials for Workflow Mode
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_DEFAULT_REGION=ap-southeast-1

# Nova Act Workflow Settings
USE_WORKFLOW_MODE=true
WORKFLOW_NAME=csp_admin_workflow
```

---

## Cách 3: Dùng AWS Credentials File

Tạo file `C:\Users\[YourUser]\.aws\credentials`:
```ini
[default]
aws_access_key_id = AKIAXXXXXXXXXXXX
aws_secret_access_key = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Tạo file `C:\Users\[YourUser]\.aws\config`:
```ini
[default]
region = ap-southeast-1
output = json
```

---

## Lưu Ý Bảo Mật

⚠️ **QUAN TRỌNG:**
- Không commit AWS credentials vào Git
- File `.env` đã có trong `.gitignore`
- Không share Access Key/Secret Key cho ai
- Rotate credentials định kỳ
