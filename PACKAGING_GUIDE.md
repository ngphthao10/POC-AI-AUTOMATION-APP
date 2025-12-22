# 📦 CSP Automation - Packaging & Distribution Guide

## 📚 Table of Contents

1. [Pre-Deployment Checklist](#-pre-deployment-checklist)
2. [Build Process](#-build-process)
3. [Distribution Package](#-distribution-package)
4. [End-User Setup](#-end-user-setup)
5. [Troubleshooting](#-troubleshooting)
6. [Advanced Topics](#-advanced-topics)

---

## ✅ Pre-Deployment Checklist

### 🔍 **CRITICAL: Complete BEFORE Building**

#### 1. Code & Configuration Review

- [ ] **All code tested and working**
  - Test on clean environment
  - Test all features (login, search, role change, branch change, save)
  - Verify error handling works

- [ ] **Remove debug code**
  - No `print("DEBUG: ...")` statements
  - No hardcoded test credentials
  - No development-only features enabled

- [ ] **Clean up files**
  - Remove `__pycache__` directories
  - Remove `.pyc` files
  - Remove test files and test data

#### 2. Configuration Files

- [ ] **`.env` file prepared**
  ```bash
  # Check .env has NO sensitive data
  # End users will add their own credentials

  # Good - Template only:
  AWS_PROFILE=your_aws_profile_name
  AWS_REGION=us-east-1
  RECORD_VIDEO=false

  # Bad - Real credentials:
  AWS_PROFILE=my-real-profile  # ❌ REMOVE THIS
  ```

- [ ] **`input.json` template ready**
  ```json
  {
    "admin_credentials": {
      "username": "your_admin_username",
      "password": "your_admin_password",
      "csp_admin_url": "https://your-csp-portal.com/users/list"
    },
    "users": [
      {
        "target_user": "user1@example.com",
        "new_role": "CSP_Inquiry",
        "branch_hierarchy": ["VIB Bank", "North", "001"]
      }
    ]
  }
  ```
  - Contains placeholders, NOT real data
  - Well-formatted and documented

- [ ] **Dependencies verified**
  ```bash
  # Check requirements.txt is up-to-date
  pip freeze > requirements_current.txt
  # Compare with requirements.txt
  ```

#### 3. Documentation

- [ ] **README files updated**
  - Installation instructions
  - Configuration guide
  - Usage examples
  - Troubleshooting section

- [ ] **Nova Act prompt best practices included**
  - Check `NOVA_ACT_PROMPT_BEST_PRACTICES.md` is present
  - Up-to-date with latest patterns

- [ ] **Quick Start guide ready**
  - Check `QUICK_START.md` exists
  - Clear step-by-step instructions

#### 4. Security Review

- [ ] **No hardcoded credentials**
  ```bash
  # Search for potential leaks
  grep -r "password" src/ --exclude-dir=venv
  grep -r "secret" src/ --exclude-dir=venv
  grep -r "api_key" src/ --exclude-dir=venv
  ```

- [ ] **No AWS credentials in code**
  - All AWS credentials come from environment
  - No hardcoded profile names

- [ ] **`.gitignore` properly configured**
  - `.env` is ignored
  - `logs/` is ignored
  - `screenshots/` is ignored
  - No sensitive data committed

#### 5. Testing

- [ ] **Fresh environment test**
  ```bash
  # Create fresh virtual environment
  python3 -m venv test_env
  source test_env/bin/activate
  pip install -r requirements.txt
  playwright install chromium
  python console_app.py
  # Test all features
  ```

- [ ] **Cross-platform compatibility** (if applicable)
  - Test on macOS
  - Test on Linux
  - Test on Windows (if supported)

---

## 🔨 Build Process

### Method 1: Using Makefile (Recommended)

```bash
# Show all available commands
make help

# Complete build pipeline (recommended)
make all

# Step-by-step
make install       # Install dependencies
make build         # Build executable
make verify        # Verify build
make package       # Create distribution zip
```

### Method 2: Using Build Script

```bash
# Make script executable (first time only)
chmod +x build_new.sh

# Run build
./build_new.sh
```

### Method 3: Manual Build

```bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Clean previous builds
rm -rf build dist

# 4. Build with PyInstaller
pyinstaller csp_automation.spec --clean --noconfirm

# 5. Copy assets
cp input.json dist/
cp .env dist/
mkdir -p dist/logs dist/screenshots
```

### Build Output

After successful build, you'll have:

```
dist/
├── csp_automation          # Main executable
├── launch.sh               # Launcher script
├── README.txt              # User instructions
├── input.json              # Configuration template
├── .env                    # Environment template
├── logs/                   # Log directory
└── screenshots/            # Screenshot directory
```

---

## 📦 Distribution Package

### Creating Distribution Package

```bash
# Using Makefile
make package

# Manual
cd dist
zip -r csp_automation_dist.zip . -x "*.DS_Store"
```

### Package Contents Checklist

Before distributing, verify package contains:

- [ ] **Executable**: `csp_automation`
- [ ] **Launcher**: `launch.sh` (executable)
- [ ] **Configuration**: `input.json` (template only)
- [ ] **Environment**: `.env` (template only)
- [ ] **Documentation**: `README.txt`
- [ ] **Directories**: `logs/`, `screenshots/`

### Package Size

Expected size: **~50-100MB**
- Executable: ~50MB
- Dependencies bundled
- No browser binaries (downloaded on first run)

### Security Before Distribution

```bash
# CRITICAL: Remove sensitive data
cd dist

# Check for credentials
grep -r "password" . 2>/dev/null
grep -r "secret" . 2>/dev/null

# Ensure templates only
cat input.json | grep "your_" || echo "⚠️ Check input.json!"
cat .env | grep "your_" || echo "⚠️ Check .env!"
```

---

## 👥 End-User Setup

### What End-Users Need

#### System Requirements

- **Operating System**: macOS 10.13+ or Linux
- **Internet**: Required (for Playwright browsers)
- **Disk Space**: ~500MB (for browser binaries)
- **Memory**: 2GB+ RAM recommended
- **Permissions**: Ability to execute binaries

#### No Installation Required

End users **DO NOT NEED**:
- ❌ Python installed
- ❌ pip or package managers
- ❌ Virtual environments
- ❌ Technical knowledge

### End-User Instructions

Provide these instructions to end users:

```markdown
# CSP Automation - User Guide

## 📥 Installation

1. **Extract the package**
   ```bash
   unzip csp_automation_dist.zip -d csp_automation
   cd csp_automation
   ```

2. **Make executable** (macOS/Linux)
   ```bash
   chmod +x launch.sh csp_automation
   ```

## ⚙️ Configuration

### Step 1: Edit input.json

Open `input.json` in a text editor:

```json
{
  "admin_credentials": {
    "username": "your_actual_username",
    "password": "your_actual_password",
    "csp_admin_url": "https://your-portal.com/users/list"
  },
  "users": [
    {
      "target_user": "user1@company.com",
      "new_role": "CSP_Inquiry",
      "branch_hierarchy": ["VIB Bank", "North", "001"]
    }
  ]
}
```

**Replace**:
- `your_actual_username` → Your CSP admin username
- `your_actual_password` → Your CSP admin password
- `https://your-portal.com/users/list` → Your actual CSP portal URL
- Add user entries as needed

### Step 2: Edit .env (Optional)

Only if you need AWS features:

```bash
AWS_PROFILE=your_aws_profile_name
AWS_REGION=us-east-1
RECORD_VIDEO=false
```

## 🚀 Running the Application

### Method 1: Using Launcher (Recommended)

```bash
./launch.sh
```

### Method 2: Direct Execution

```bash
./csp_automation
```

### First Run

The first time you run, it will:
1. Download Playwright browser binaries (~300MB)
2. This may take 2-5 minutes
3. Subsequent runs will be faster

## 📋 Usage

1. The application will show a menu
2. Select option 1: "CSP Admin - Change Role and Branch"
3. Review your configuration
4. Confirm to start automation
5. Browser will open automatically
6. Watch the automation process
7. Check results in logs/

## 📁 Output

- **Logs**: Check `logs/` folder for detailed execution logs
- **Screenshots**: Error screenshots saved in `screenshots/`
- **Results**: JSON results saved with timestamps

## 🔧 Troubleshooting

### "Permission denied"
```bash
chmod +x launch.sh csp_automation
```

### "Playwright not found"
```bash
# Install manually
playwright install chromium
```

### Application crashes
1. Check `logs/` folder for errors
2. Verify `input.json` is valid JSON
3. Verify credentials in configuration
4. Check internet connection

### Browser doesn't open
1. Ensure Playwright browsers installed
2. Check system has sufficient disk space
3. Try running with `./launch.sh` instead

## 📞 Support

- Check logs in `logs/` folder
- Screenshots in `screenshots/` folder
- Contact your administrator
```

---

## 🔧 Troubleshooting

### Build Issues

#### Issue: "nova_act not found"

**Solution:**
```bash
source venv/bin/activate
pip install nova-act
```

#### Issue: "PyInstaller failed"

**Solution:**
```bash
# Reinstall PyInstaller
pip uninstall pyinstaller
pip install pyinstaller --no-cache-dir

# Try build again
make build
```

#### Issue: "Playwright browsers missing"

**Solution:**
```bash
playwright install chromium

# Verify
python3 -c "from playwright.sync_api import sync_playwright; \
  with sync_playwright() as p: p.chromium.launch()"
```

#### Issue: "Hidden imports not found"

**Solution:**
Add to `csp_automation.spec`:
```python
hiddenimports=[
    # Add missing module here
    'your.missing.module',
]
```

### Runtime Issues

#### Issue: "Executable too large (>200MB)"

**Causes:**
- Unnecessary dependencies included
- Debug symbols not stripped

**Solution:**
```python
# In .spec file
exe = EXE(
    ...
    upx=True,           # Compress
    strip=True,         # Strip debug symbols
    excludes=[          # Exclude unnecessary packages
        'matplotlib',
        'numpy',
        'pandas',
    ]
)
```

#### Issue: "Application won't run on user's machine"

**Checklist:**
- [ ] User has correct OS (macOS/Linux)
- [ ] Executable has execute permissions
- [ ] Internet connection available
- [ ] Sufficient disk space (~500MB)
- [ ] No antivirus blocking

### Distribution Issues

#### Issue: "Package too large to share"

**Solution:**
```bash
# Use UPX compression
make build  # UPX enabled by default

# Or host on cloud storage
# - AWS S3
# - Google Drive
# - Dropbox
```

#### Issue: "Users can't configure application"

**Solution:**
- Provide clear `input.json` template
- Include example in README
- Create video tutorial
- Provide configuration validator script

---

## 🎓 Advanced Topics

### Multi-Platform Build

#### Building for Multiple Platforms

```bash
# macOS
./build_new.sh  # Builds for macOS

# Linux (on Linux machine)
./build_new.sh  # Builds for Linux

# Windows (future)
# Use build.bat on Windows machine
```

#### Cross-Compilation

Not recommended for Playwright-based apps. Build on target platform.

### Customization

#### Custom Application Name

Edit `csp_automation.spec`:
```python
APP_NAME = 'my_custom_name'
```

#### Custom Icon

Add icon to spec:
```python
exe = EXE(
    ...
    icon='path/to/icon.ico',  # Windows
    icon='path/to/icon.icns', # macOS
)
```

#### Version Information

Add to spec:
```python
import datetime

VERSION = '1.0.0'
BUILD_DATE = datetime.datetime.now().strftime('%Y-%m-%d')

# Add to EXE()
exe = EXE(
    ...
    version=f'{VERSION}+{BUILD_DATE}',
)
```

### CI/CD Integration

#### GitHub Actions Example

```yaml
name: Build Application

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Build
        run: |
          make all

      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: csp-automation
          path: csp_automation_dist.zip
```

### Code Signing (macOS)

```bash
# Sign the executable
codesign --force --sign "Developer ID Application: Your Name" \
  dist/csp_automation

# Verify signature
codesign --verify --verbose dist/csp_automation

# Check signature
codesign -dv dist/csp_automation
```

### Notarization (macOS)

Required for macOS 10.15+:

```bash
# Create .pkg installer
productbuild --component dist/csp_automation /Applications \
  csp_automation.pkg

# Submit for notarization
xcrun notarytool submit csp_automation.pkg \
  --apple-id your@email.com \
  --password your-app-specific-password \
  --team-id YOUR_TEAM_ID

# Staple notarization ticket
xcrun stapler staple csp_automation.pkg
```

---

## 📊 Summary Checklist

### Before Building

- [ ] Code tested and working
- [ ] Debug code removed
- [ ] Configuration files prepared (templates only)
- [ ] Dependencies verified
- [ ] Documentation updated
- [ ] Security review completed
- [ ] Fresh environment test passed

### Building

- [ ] Clean build completed
- [ ] No errors during PyInstaller
- [ ] Executable created in dist/
- [ ] Assets copied correctly
- [ ] Launcher script created

### Distribution

- [ ] Package created
- [ ] Package size reasonable (<100MB)
- [ ] All required files included
- [ ] No sensitive data in package
- [ ] README.txt included
- [ ] Package tested on clean machine

### Post-Distribution

- [ ] End-user instructions provided
- [ ] Support channels established
- [ ] Feedback mechanism in place
- [ ] Version tracking enabled

---

## 📞 Support & Resources

### Documentation Files

- `NOVA_ACT_PROMPT_BEST_PRACTICES.md` - Nova Act usage guide
- `QUICK_START.md` - Quick start guide
- `PHASE_1_2_INTEGRATION_GUIDE.md` - Integration guide
- `README.md` - Main project documentation

### Build Commands Quick Reference

```bash
# Show help
make help

# Complete pipeline
make all

# Quick build
make build

# Create package
make package

# Verify build
make verify

# Clean artifacts
make clean
```

---

**Version:** 2.0.0
**Last Updated:** 2025-12-22
**Maintainer:** CSP Automation Team
