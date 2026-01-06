@echo off
setlocal

echo ============================================================
echo Building CSP Automation Console App for Windows
echo ============================================================
echo.

echo Step 1: Activate existing virtual environment
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please create venv first and add VIB certificate to:
    echo venv\Lib\site-packages\certifi\cacert.pem
    pause
    exit /b 1
)
echo Using existing virtual environment with VIB certificate...
call venv\Scripts\activate.bat

echo.
echo Step 2: Verify dependencies (skip reinstall to preserve cert)
echo Dependencies already installed in venv

echo.
echo Step 3: Install Playwright browsers
playwright install chromium

echo.
echo Step 4: Clean previous builds
if exist "build\" (
    echo Removing old build folder...
    rmdir /s /q build
)
if exist "dist\" (
    echo Removing old dist folder...
    rmdir /s /q dist
)
if exist "csp_automation.spec" (
    del csp_automation.spec
)

echo.
echo Step 5: Build executable with PyInstaller (including VIB cert)
pyinstaller --name=csp_automation ^
    --onefile ^
    --console ^
    --add-data "input.json;." ^
    --add-data ".env;." ^
    --add-data "template.json;." ^
    --add-data "venv\Lib\site-packages\certifi\cacert.pem;certifi" ^
    --hidden-import=nova_act ^
    --hidden-import=playwright ^
    --hidden-import=playwright.sync_api ^
    --hidden-import=certifi ^
    --collect-data certifi ^
    --clean ^
    --noconfirm ^
    console_app.py

echo.
echo Step 6: Copy required files to dist folder
copy input.json dist\ >nul 2>&1
copy template.json dist\ >nul 2>&1
copy .env dist\ >nul 2>&1
copy SETUP_WINDOWS.md dist\ >nul 2>&1

echo Creating output folders...
if not exist "dist\logs\" mkdir dist\logs
if not exist "dist\screenshots\" mkdir dist\screenshots

echo.
echo ============================================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ============================================================
pause
