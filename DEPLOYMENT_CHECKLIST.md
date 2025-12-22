# 🚀 CSP Automation - Deployment Checklist

## ⚡ Quick Pre-Deployment Checklist

Use this checklist BEFORE building and distributing your application.

---

## 📋 Step-by-Step Checklist

### 1️⃣ Code Quality (30 mins)

- [ ] **All features tested manually**
  - Login works ✓
  - User search works ✓
  - Role change works ✓
  - Branch change works ✓
  - Save works ✓

- [ ] **Error handling tested**
  - Wrong credentials → Shows error message ✓
  - User not found → Shows error message ✓
  - Network error → Retries and logs error ✓

- [ ] **Remove debug code**
  ```bash
  # Search for debug statements
  grep -r "DEBUG" src/ console_app.py
  grep -r "print(" src/ console_app.py | grep -v "print(f" | grep -v "logger"
  ```
  - Remove all `print("DEBUG: ...")` ✓
  - Remove test/demo code ✓

### 2️⃣ Security Review (15 mins)

- [ ] **No hardcoded credentials**
  ```bash
  # Search for potential leaks
  grep -ri "password" src/ --exclude-dir=venv | grep -v "password_field"
  grep -ri "secret" src/ --exclude-dir=venv
  grep -ri "api_key" src/ --exclude-dir=venv
  ```

- [ ] **Configuration files are templates**
  - `input.json` contains "your_username", "your_password" ✓
  - `.env` contains "your_aws_profile" ✓
  - NO real credentials in files ✓

- [ ] **Git repository clean**
  ```bash
  # Check .gitignore
  cat .gitignore | grep -E "\.env|logs/|screenshots/"
  # Check no sensitive files committed
  git status
  ```

### 3️⃣ Configuration Files (10 mins)

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
        "target_user": "user@example.com",
        "new_role": "CSP_Inquiry",
        "branch_hierarchy": ["VIB Bank", "North", "001"]
      }
    ]
  }
  ```

- [ ] **`.env` template ready**
  ```env
  # AWS Configuration (optional)
  AWS_PROFILE=your_aws_profile_name
  AWS_REGION=us-east-1

  # Nova Act Configuration
  RECORD_VIDEO=false
  HEADLESS=false
  ```

### 4️⃣ Dependencies (10 mins)

- [ ] **Check requirements.txt**
  ```bash
  # Current dependencies
  pip freeze | grep -E "nova-act|playwright|boto3|pydantic|rich|fire"

  # Compare with requirements.txt
  cat requirements.txt
  ```

- [ ] **Verify installations**
  ```bash
  source venv/bin/activate
  python -c "import nova_act; print('✓ nova-act')"
  python -c "import playwright; print('✓ playwright')"
  python -c "import dotenv; print('✓ python-dotenv')"
  playwright install chromium
  ```

### 5️⃣ Documentation (15 mins)

- [ ] **README files updated**
  - `README.md` - Main documentation ✓
  - `QUICK_START.md` - Quick start guide ✓
  - `PACKAGING_GUIDE.md` - Packaging guide ✓
  - `NOVA_ACT_PROMPT_BEST_PRACTICES.md` - Prompt guide ✓

- [ ] **User documentation clear**
  - Installation steps clear ✓
  - Configuration steps clear ✓
  - Usage examples provided ✓
  - Troubleshooting section included ✓

### 6️⃣ Testing (20 mins)

- [ ] **Fresh environment test**
  ```bash
  # Create clean test environment
  rm -rf test_env
  python3 -m venv test_env
  source test_env/bin/activate
  pip install -r requirements.txt
  playwright install chromium

  # Test run
  python console_app.py
  # → Test all menu options
  # → Test actual automation with test data
  ```

- [ ] **Test with sample input**
  - Use `input.json` template ✓
  - Verify all fields work ✓
  - Test error cases ✓

### 7️⃣ Build (30 mins)

- [ ] **Clean build**
  ```bash
  # Clean previous builds
  make clean
  # or
  rm -rf build dist
  ```

- [ ] **Run build**
  ```bash
  # Using Makefile (recommended)
  make build

  # Or using script
  ./build_new.sh
  ```

- [ ] **Verify build output**
  ```bash
  # Check dist/ folder
  ls -la dist/

  # Should contain:
  # - csp_automation (executable)
  # - launch.sh
  # - input.json
  # - .env
  # - logs/
  # - screenshots/
  # - README.txt
  ```

### 8️⃣ Post-Build Verification (15 mins)

- [ ] **Test executable**
  ```bash
  cd dist
  ./launch.sh
  # → Should start application
  # → Test menu navigation
  ```

- [ ] **Check file sizes**
  ```bash
  du -h dist/csp_automation
  # Expected: 50-100MB

  du -sh dist/
  # Expected: 50-100MB (before first run)
  ```

- [ ] **Verify no sensitive data**
  ```bash
  cd dist
  grep -r "password" . | grep -v "your_password"
  # Should find nothing

  grep -r "secret" .
  # Should find nothing
  ```

### 9️⃣ Package Creation (10 mins)

- [ ] **Create distribution package**
  ```bash
  # Using Makefile
  make package

  # Or manually
  cd dist
  zip -r ../csp_automation_dist.zip . -x "*.DS_Store"
  ```

- [ ] **Verify package**
  ```bash
  # Check size
  ls -lh csp_automation_dist.zip
  # Expected: 50-100MB

  # Test extraction
  mkdir test_extract
  cd test_extract
  unzip ../csp_automation_dist.zip
  ls -la
  ```

### 🔟 Distribution (10 mins)

- [ ] **Final security check**
  ```bash
  # Extract and verify
  unzip csp_automation_dist.zip -d final_check
  cd final_check

  # Check for real credentials
  cat input.json | grep -E "your_|example.com"
  cat .env | grep "your_"

  # Should see only placeholders
  ```

- [ ] **Prepare distribution**
  - Upload to secure location ✓
  - Share download link ✓
  - Include user instructions ✓

---

## ✅ Pre-Distribution Final Checks

### Security Final Check

```bash
# 1. No hardcoded credentials
grep -ri "password.*=" src/ | grep -v "password_field" | grep -v "new_password"

# 2. Configuration files are templates
cat dist/input.json | grep "your_"
cat dist/.env | grep "your_"

# 3. No sensitive logs
ls -la logs/ 2>/dev/null
ls -la dist/logs/ 2>/dev/null
```

### Functionality Final Check

- [ ] Fresh install test (clean machine if possible)
- [ ] Configure with test credentials
- [ ] Run one complete automation
- [ ] Verify logs are created
- [ ] Verify screenshots work on errors

### Documentation Final Check

- [ ] README includes all steps
- [ ] Example `input.json` is clear
- [ ] Troubleshooting covers common issues
- [ ] Support contact information included

---

## 🚨 Common Mistakes to Avoid

### ❌ Don't Do This

1. **❌ Include real credentials in package**
   - Always use templates
   - Never commit real `.env` or `input.json`

2. **❌ Skip testing in fresh environment**
   - Always test in clean venv
   - Test on different machine if possible

3. **❌ Distribute debug builds**
   - Remove all debug prints
   - Remove test/demo code

4. **❌ Forget dependencies**
   - Verify `requirements.txt` is complete
   - Test `pip install -r requirements.txt`

5. **❌ Skip documentation**
   - Users need clear instructions
   - Include configuration examples

### ✅ Do This

1. **✅ Use version control**
   - Tag releases: `git tag v1.0.0`
   - Track what's in each version

2. **✅ Keep build logs**
   - Save build output
   - Track any warnings

3. **✅ Test on multiple machines**
   - Different OS versions
   - Fresh installs

4. **✅ Provide examples**
   - Sample `input.json`
   - Sample `.env`
   - Screenshots of UI

5. **✅ Plan support**
   - How will users report issues?
   - How will you distribute updates?

---

## 📊 Time Estimates

| Phase | Estimated Time |
|-------|----------------|
| Code Quality Check | 30 minutes |
| Security Review | 15 minutes |
| Configuration Prep | 10 minutes |
| Dependencies Check | 10 minutes |
| Documentation Review | 15 minutes |
| Testing | 20 minutes |
| Build Process | 30 minutes |
| Post-Build Verification | 15 minutes |
| Package Creation | 10 minutes |
| Final Distribution Prep | 10 minutes |
| **TOTAL** | **~2.5 hours** |

---

## 🎯 Quick Command Reference

```bash
# Complete deployment pipeline
make clean          # Clean artifacts
make install        # Install dependencies
make build          # Build executable
make verify         # Verify build
make package        # Create distribution zip

# Or all-in-one
make all

# Or use build script
./build_new.sh

# Verify package
unzip -t csp_automation_dist.zip

# Test extraction
mkdir test && cd test
unzip ../csp_automation_dist.zip
./launch.sh
```

---

## 📞 Support

If you encounter issues during deployment:

1. Check `PACKAGING_GUIDE.md` for detailed troubleshooting
2. Review build logs for errors
3. Test in fresh virtual environment
4. Verify all dependencies installed

---

**Last Updated:** 2025-12-22
**Version:** 1.0.0
