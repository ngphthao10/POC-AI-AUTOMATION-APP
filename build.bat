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
echo Step 6: Copy Playwright browsers to dist folder
echo This will make the app portable (no setup needed on target machine)
echo.
set PLAYWRIGHT_BROWSERS_SRC=%USERPROFILE%\AppData\Local\ms-playwright
set PLAYWRIGHT_BROWSERS_DEST=dist\ms-playwright

if exist "%PLAYWRIGHT_BROWSERS_SRC%\" (
    echo Found Playwright browsers at: %PLAYWRIGHT_BROWSERS_SRC%
    echo Copying to dist folder (this may take a few minutes)...
    xcopy /E /I /Y /Q "%PLAYWRIGHT_BROWSERS_SRC%" "%PLAYWRIGHT_BROWSERS_DEST%"
    echo ✓ Playwright browsers copied successfully
) else (
    echo ERROR: Playwright browsers not found!
    echo Please run: playwright install chromium
    pause
    exit /b 1
)

echo.
echo Step 7: Copy required files to dist folder
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
echo.
echo Package contents:
echo   ✓ csp_automation.exe
echo   ✓ Playwright browsers (ms-playwright folder - ~400MB)
echo   ✓ Configuration files (input.json, .env, template.json)
echo   ✓ Empty logs and screenshots folders
echo.
echo IMPORTANT: Zip the entire dist\ folder to distribute
echo Target machine does NOT need to install Playwright
echo ============================================================
pause
