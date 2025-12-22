# 🔨 Build System - Quick Reference

## 🚀 Quick Start

### For Developers

```bash
# Install dependencies and build
make all

# Or step by step
make install    # Install dependencies
make build      # Build executable
make verify     # Verify build
make package    # Create distribution zip
```

### For End Users

```bash
# Extract package
unzip csp_automation_dist.zip -d csp_automation
cd csp_automation

# Configure
# Edit input.json with your credentials

# Run
./launch.sh
```

---

## 📁 Build Files Overview

### Build Configuration

| File | Purpose |
|------|---------|
| `csp_automation.spec` | PyInstaller configuration (NEW - updated for current structure) |
| `build_new.sh` | Build script with checks and verification |
| `Makefile` | Convenient build commands |
| `requirements.txt` | Python dependencies |

### Documentation

| File | Purpose |
|------|---------|
| `PACKAGING_GUIDE.md` | Complete packaging and distribution guide |
| `DEPLOYMENT_CHECKLIST.md` | Pre-deployment checklist |
| `BUILD_README.md` | This file - quick reference |
| `NOVA_ACT_PROMPT_BEST_PRACTICES.md` | Nova Act usage guide |

### Old Files (Can be removed)

| File | Status |
|------|--------|
| `ai_automation_app.spec` | ❌ OLD - Use `csp_automation.spec` instead |
| `build.sh` | ❌ OLD - Use `build_new.sh` instead |
| `build.bat` | ❌ OLD - For Windows (not updated) |
| `playwright_runtime_hook.py` | ❌ OLD - Removed (no longer needed) |

---

## 🎯 Common Tasks

### Build Executable

```bash
# Recommended: Using Makefile
make build

# Alternative: Using script
./build_new.sh

# Manual: Using PyInstaller directly
pyinstaller csp_automation.spec --clean --noconfirm
```

### Clean Build Artifacts

```bash
# Using Makefile
make clean

# Manual
rm -rf build dist __pycache__
find . -type d -name __pycache__ -exec rm -rf {} +
```

### Create Distribution Package

```bash
# Complete pipeline
make all

# Or just package existing build
make package
```

### Run in Development Mode

```bash
# Using Makefile
make run

# Direct
python console_app.py
```

### Verify Build

```bash
# Check build is valid
make verify

# Test built executable
cd dist
./csp_automation
```

---

## 📦 What Gets Built

### Build Process

```
Source Code
    ↓
[PyInstaller]
    ↓
dist/
├── csp_automation       ← Standalone executable (~50-100MB)
├── launch.sh            ← Launcher script
├── input.json           ← Configuration template
├── .env                 ← Environment template
├── README.txt           ← User instructions
├── logs/                ← Log directory
└── screenshots/         ← Screenshot directory
```

### Package Structure

```
csp_automation_dist.zip (~50-100MB)
└── [All files from dist/]
```

---

## ⚙️ Build Configuration

### PyInstaller Spec File: `csp_automation.spec`

Key configurations:

```python
# Application name
APP_NAME = 'csp_automation'

# Entry point
['console_app.py']

# Data files included
datas = [
    ('input.json', '.'),
    ('.env', '.'),
    ('src/features/csp/*.py', 'src/features/csp'),
    ('src/shared/*.py', 'src/shared'),
    # NovaAct artifacts
]

# Hidden imports (packages not auto-detected)
hiddenimports = [
    'playwright',
    'nova_act',
    'src.features.csp.csp_admin_main',
    # ... all application modules
]

# Console application
console=True
```

### Build Script: `build_new.sh`

Features:
- ✅ Preflight checks (Python, required files)
- ✅ Virtual environment setup
- ✅ Dependency installation
- ✅ Playwright browser installation
- ✅ Clean build
- ✅ Asset copying
- ✅ Launcher script creation
- ✅ Verification
- ✅ Helpful error messages

---

## 🔧 Troubleshooting

### Issue: Build fails with "module not found"

**Solution:** Add to `hiddenimports` in `csp_automation.spec`

```python
hiddenimports=[
    # Add missing module here
    'your.missing.module',
]
```

### Issue: Executable too large (>200MB)

**Solution:** Exclude unnecessary packages

```python
excludes=[
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
]
```

### Issue: "Permission denied" when running

**Solution:**
```bash
chmod +x dist/csp_automation dist/launch.sh
```

### Issue: Missing data files in build

**Solution:** Add to `datas` in spec file

```python
datas = [
    ('path/to/file', 'destination/in/build'),
]
```

---

## 🎓 Build System Architecture

### 3-Tier Build System

1. **Makefile** (Recommended)
   - High-level commands
   - Easy to remember
   - Consistent interface
   - Example: `make build`

2. **Build Script** (`build_new.sh`)
   - Detailed build process
   - Checks and verification
   - Error handling
   - Example: `./build_new.sh`

3. **PyInstaller** (Low-level)
   - Core build tool
   - Spec file configuration
   - Example: `pyinstaller csp_automation.spec`

### When to Use Each

| Use Case | Command |
|----------|---------|
| Regular build | `make build` |
| Complete pipeline | `make all` |
| Quick rebuild | `make build-fast` |
| Custom build | `./build_new.sh` |
| Debug build issues | `pyinstaller csp_automation.spec -y` |

---

## 📊 Makefile Commands Reference

### Development

```bash
make help           # Show all commands
make install        # Install dependencies
make dev            # Setup dev environment
make run            # Run in dev mode
```

### Build & Package

```bash
make clean          # Clean artifacts
make build          # Build executable
make build-fast     # Quick rebuild
make package        # Create distribution zip
make all            # Complete pipeline
```

### Verification

```bash
make verify         # Verify build
make verify-deps    # Verify dependencies
make show-config    # Show configuration
```

### Utilities

```bash
make logs           # View recent logs
make screenshots    # View recent screenshots
make dist-clean     # Clean distribution files
make dist-prepare   # Pre-distribution check
```

### Code Quality (if dev tools installed)

```bash
make lint           # Run linting
make format         # Format code
make test           # Run tests
```

---

## 🚀 Deployment Workflow

### Standard Workflow

```bash
# 1. Prepare
make clean

# 2. Check code
grep -r "DEBUG" src/
# Remove any debug code

# 3. Verify configuration
cat input.json  # Should be template
cat .env        # Should be template

# 4. Build and package
make all

# 5. Test package
cd dist
./launch.sh
# Test all features

# 6. Distribute
# Upload csp_automation_dist.zip
# Share with end users
```

### Quick Rebuild (During Development)

```bash
# Fast iteration during development
make build-fast

# Test changes
cd dist && ./csp_automation
```

---

## 📝 File Structure

### Before Build

```
project/
├── console_app.py                    # Entry point
├── csp_automation.spec               # Build config
├── build_new.sh                      # Build script
├── Makefile                          # Build commands
├── requirements.txt                  # Dependencies
├── input.json                        # Config template
├── .env                              # Env template
├── src/
│   ├── features/csp/                # CSP features
│   └── shared/                       # Shared utilities
└── venv/                             # Virtual environment
```

### After Build

```
project/
├── [all source files]
├── build/                            # Build artifacts (temp)
├── dist/                             # Distribution ready
│   ├── csp_automation               # ← EXECUTABLE
│   ├── launch.sh
│   ├── input.json
│   ├── .env
│   ├── README.txt
│   ├── logs/
│   └── screenshots/
└── csp_automation_dist.zip          # ← READY TO SHARE
```

---

## 🔗 Related Documentation

- **`PACKAGING_GUIDE.md`** - Detailed packaging guide
- **`DEPLOYMENT_CHECKLIST.md`** - Pre-deployment checklist
- **`QUICK_START.md`** - Quick start for users
- **`NOVA_ACT_PROMPT_BEST_PRACTICES.md`** - Nova Act usage

---

## ⚡ TL;DR - Fastest Path

```bash
# For first time setup
make all

# For subsequent builds
make build

# To create distribution
make package

# Done! Share: csp_automation_dist.zip
```

---

**Version:** 1.0.0
**Last Updated:** 2025-12-22
