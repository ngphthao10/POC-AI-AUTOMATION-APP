@echo off
echo ============================================================
echo Simple Build Script - Debug Version
echo ============================================================
echo.

REM Step 1: Activate venv
echo [1/4] Activating venv...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Cannot activate venv
    pause
    exit /b 1
)
echo OK

REM Step 2: Clean old build
echo.
echo [2/4] Cleaning old build...
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist
if exist "csp_automation.spec" del csp_automation.spec
echo OK

REM Step 3: Build with PyInstaller (without playwright browsers first)
echo.
echo [3/4] Building exe (this takes 2-5 minutes, please wait)...
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

if errorlevel 1 (
    echo ERROR: PyInstaller failed!
    pause
    exit /b 1
)
echo OK - exe created

REM Step 4: Copy files
echo.
echo [4/4] Copying files to dist...
copy input.json dist\ >nul 2>&1
copy template.json dist\ >nul 2>&1
copy .env dist\ >nul 2>&1
if not exist "dist\logs\" mkdir dist\logs
if not exist "dist\screenshots\" mkdir dist\screenshots
echo OK

echo.
echo ============================================================
echo BUILD COMPLETED!
echo ============================================================
echo.
echo EXE location: dist\csp_automation.exe
echo.
echo NOTE: Playwright browsers NOT included yet
echo To add browsers, run: build_add_browsers.bat
echo.
pause
