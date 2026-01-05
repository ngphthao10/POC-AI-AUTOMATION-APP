@echo off
setlocal

echo ============================================================
echo Building CSP Automation Console App for Windows
echo ============================================================
echo.

echo Step 1: Setup virtual environment
if exist "venv\" (
    echo Virtual environment found, activating...
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo.
echo Step 2: Install dependencies
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

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
echo Step 5: Build executable with PyInstaller
pyinstaller --name=csp_automation ^
    --onefile ^
    --console ^
    --add-data "input.json;." ^
    --add-data ".env;." ^
    --add-data "template.json;." ^
    --hidden-import=nova_act ^
    --hidden-import=playwright ^
    --hidden-import=playwright.sync_api ^
    --clean ^
    --noconfirm ^
    console_app.py

echo.
echo Step 6: Copy required files to dist folder
copy input.json dist\ >nul 2>&1
copy template.json dist\ >nul 2>&1
copy .env dist\ >nul 2>&1

echo Creating output folders...
if not exist "dist\logs\" mkdir dist\logs
if not exist "dist\screenshots\" mkdir dist\screenshots

echo.
echo Step 7: Create README for users
(
echo CSP AUTOMATION - CONSOLE APP
echo ==============================
echo.
echo HOW TO USE:
echo 1. Edit input.json with your configuration
echo 2. Double-click csp_automation.exe to run
echo 3. Follow the prompts in the console
echo.
echo FOLDER STRUCTURE:
echo - input.json: Configuration file
echo - template.json: Template for input configuration
echo - logs/: Automation logs
echo - screenshots/: Debug screenshots
echo.
echo REQUIREMENTS:
echo - Windows 10 or later
echo - Internet connection for browser automation
echo.
) > dist\README.txt

echo.
echo ============================================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ============================================================
echo.
echo Output: dist\csp_automation.exe
echo.
echo TO DISTRIBUTE:
echo 1. Copy the entire 'dist' folder to Windows machine
echo 2. Edit input.json in dist folder
echo 3. Run csp_automation.exe
echo.
echo ============================================================
pause
