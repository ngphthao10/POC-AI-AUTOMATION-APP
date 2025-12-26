@echo off
REM ############################################################################
REM CSP Automation Application - Build Script for Windows
REM Description: Builds standalone executable with PyInstaller and Playwright
REM Version: 2.0.0
REM Updated: 2025-12-22
REM ############################################################################

setlocal enabledelayedexpansion

REM Configuration
set APP_NAME=csp_automation
set SPEC_FILE=csp_automation.spec
set PYTHON_VERSION=3.10

REM ############################################################################
REM Helper Functions
REM ############################################################################

:print_header
echo.
echo ============================================================
echo   CSP Automation Application - Build Script
echo ============================================================
echo.
goto :eof

:print_step
echo [92m[*][0m %~1
goto :eof

:print_error
echo [91m[X][0m %~1
goto :eof

:print_warning
echo [93m[!][0m %~1
goto :eof

:print_success
echo [92m[+][0m %~1
goto :eof

REM ############################################################################
REM Preflight Checks
REM ############################################################################

:check_python
call :print_step "Checking Python installation..."

where python >nul 2>&1
if errorlevel 1 (
    call :print_error "Python is not installed. Please install Python 3.10+."
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
call :print_success "Python %PYTHON_VER% found"
goto :eof

:check_required_files
call :print_step "Checking required files..."

set MISSING=0

if not exist "console_app.py" (
    call :print_error "Missing: console_app.py"
    set MISSING=1
)

if not exist "requirements.txt" (
    call :print_error "Missing: requirements.txt"
    set MISSING=1
)

if not exist ".env" (
    call :print_error "Missing: .env"
    set MISSING=1
)

if not exist "input.json" (
    call :print_error "Missing: input.json"
    set MISSING=1
)

if %MISSING%==1 (
    call :print_error "Some required files are missing"
    exit /b 1
)

call :print_success "All required files present"
goto :eof

REM ############################################################################
REM Virtual Environment Setup
REM ############################################################################

:setup_venv
call :print_step "Setting up virtual environment..."

if exist "venv\" (
    call :print_warning "Virtual environment already exists, using it..."
    call venv\Scripts\activate.bat
) else (
    call :print_step "Creating new virtual environment..."
    python -m venv venv
    call venv\Scripts\activate.bat
    call :print_success "Virtual environment created"
)
goto :eof

:install_dependencies
call :print_step "Installing Python dependencies..."

python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

call :print_success "Dependencies installed"
goto :eof

:install_playwright
call :print_step "Installing Playwright browsers..."

playwright install chromium

if errorlevel 1 (
    call :print_error "Failed to install Playwright browsers"
    exit /b 1
)

call :print_success "Playwright browsers installed"
goto :eof

:verify_playwright
call :print_step "Verifying Playwright installation..."

python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().__enter__(); b = p.chromium.launch(headless=True); b.close()" 2>nul

if errorlevel 1 (
    call :print_error "Playwright verification failed"
    exit /b 1
)

call :print_success "Playwright verification passed"
goto :eof

REM ############################################################################
REM Build Process
REM ############################################################################

:clean_build
call :print_step "Cleaning previous builds..."

if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist
del /s /q *.pyc >nul 2>&1
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

call :print_success "Build artifacts cleaned"
goto :eof

:generate_spec
if not exist "%SPEC_FILE%" (
    call :print_step "Generating spec file..."

    pyi-makespec console_app.py --name="%APP_NAME%" --onefile --windowed --add-data="input.json;." --add-data=".env;." --hidden-import="nova_act" --hidden-import="playwright" --hidden-import="playwright.sync_api" --collect-all="playwright" --collect-all="nova_act"

    call :print_success "Spec file generated"
) else (
    call :print_step "Using existing spec file"
)
goto :eof

:run_pyinstaller
call :print_step "Running PyInstaller..."
echo.
echo This may take a few minutes...
echo.

pyinstaller "%SPEC_FILE%" --clean --noconfirm

if errorlevel 1 (
    call :print_error "PyInstaller build failed"
    exit /b 1
)

call :print_success "PyInstaller build completed"
goto :eof

:copy_assets
call :print_step "Copying assets to dist folder..."

if exist "input.json" (
    if not exist "dist\input.json" copy input.json dist\ >nul
)

if exist ".env" (
    if not exist "dist\.env" copy .env dist\ >nul
)

if not exist "dist\logs\" mkdir dist\logs
if not exist "dist\screenshots\" mkdir dist\screenshots

call :print_success "Assets copied"
goto :eof

:copy_playwright_browsers
call :print_step "Copying Playwright browsers to dist folder..."

set PLAYWRIGHT_CACHE=%LOCALAPPDATA%\ms-playwright

if exist "%PLAYWRIGHT_CACHE%" (
    call :print_step "Found Playwright browsers at: %PLAYWRIGHT_CACHE%"
    if not exist "dist\.playwright-browsers\" mkdir "dist\.playwright-browsers"
    xcopy /E /I /Y /Q "%PLAYWRIGHT_CACHE%\*" "dist\.playwright-browsers\" >nul
    call :print_success "Playwright browsers copied (~300MB)"
) else (
    call :print_warning "Playwright browsers not found in cache"
    call :print_warning "End users will need to install browsers separately"
)
goto :eof

:create_launcher
call :print_step "Creating launcher script..."

(
echo @echo off
echo REM CSP Automation Launcher Script
echo.
echo cd /d "%%~dp0"
echo.
echo echo Starting CSP Automation...
echo.
echo REM Set Playwright browsers path to bundled location
echo if exist ".playwright-browsers\" ^(
echo     set PLAYWRIGHT_BROWSERS_PATH=%%~dp0.playwright-browsers
echo     echo Using bundled Playwright browsers
echo ^) else ^(
echo     echo Warning: Bundled browsers not found, using system installation
echo ^)
echo.
echo REM Set TMPDIR to avoid permission issues
echo set TMPDIR=%%USERPROFILE%%\tmp
echo if not exist "%%TMPDIR%%" mkdir "%%TMPDIR%%"
echo.
echo REM Run the application
echo %APP_NAME%.exe %%*
echo.
echo if errorlevel 1 ^(
echo     echo.
echo     echo Application exited with error
echo     echo.
echo     echo Troubleshooting:
echo     echo   - Check input.json is properly configured
echo     echo   - Ensure .env file has correct credentials
echo     echo   - Check logs/ folder for detailed errors
echo     echo.
echo     pause
echo ^)
) > dist\launch.bat

call :print_success "Launcher script created"
goto :eof

:create_readme
call :print_step "Creating README for distribution..."

(
echo ============================================================
echo   CSP AUTOMATION APPLICATION - DISTRIBUTION PACKAGE
echo ============================================================
echo.
echo NOTE: This Windows build does NOT require code signing
echo       and will run without security warnings.
echo       ^(macOS builds require Apple Developer certificate^)
echo.
echo PACKAGE CONTENTS:
echo   - %APP_NAME%.exe       - Main executable
echo   - launch.bat            - Launcher script ^(recommended^)
echo   - input.json           - Configuration file ^(EDIT THIS^)
echo   - .env                 - Environment variables ^(credentials^)
echo   - logs/                - Log output directory
echo   - screenshots/         - Screenshot output directory
echo   - README.txt           - This file
echo.
echo QUICK START:
echo.
echo 1. Edit input.json with your configuration:
echo    - admin_credentials ^(username, password, csp_admin_url^)
echo    - users list ^(target_user, new_role, branch_hierarchy^)
echo.
echo 2. Edit .env with your credentials ^(if needed^)
echo.
echo 3. Run the application:
echo    Double-click: launch.bat
echo    or directly:  %APP_NAME%.exe
echo.
echo 4. Follow the on-screen menu
echo.
echo REQUIREMENTS:
echo   - Windows 10+ ^(RECOMMENDED PLATFORM - no code signing needed^)
echo   - Internet connection ^(for Playwright browsers on first run^)
echo   - Sufficient disk space ^(~500MB for browser binaries^)
echo.
echo TROUBLESHOOTING:
echo.
echo Issue: Application crashes
echo Fix:   Check logs/ folder for error details
echo        Ensure input.json is valid JSON
echo        Verify .env credentials are correct
echo.
echo Issue: Playwright browsers not found
echo Fix:   Run: playwright install chromium
echo.
echo SUPPORT:
echo   Check the logs/ folder for detailed error messages
echo   Screenshots are saved in screenshots/ folder on errors
echo.
echo NOTES:
echo   - First run may take longer ^(downloading browser binaries^)
echo   - Logs are saved with timestamps in logs/ folder
echo   - DO NOT delete browser cache directories
echo.
echo Version: 1.0.0
echo Built: %date% %time%
) > dist\README.txt

call :print_success "README created"
goto :eof

REM ############################################################################
REM Post-Build
REM ############################################################################

:verify_build
call :print_step "Verifying build..."

if not exist "dist\%APP_NAME%.exe" (
    call :print_error "Executable not found in dist/"
    exit /b 1
)

for %%A in ("dist\%APP_NAME%.exe") do set SIZE=%%~zA
set /a SIZE_MB=!SIZE! / 1048576

call :print_success "Build verified (Size: !SIZE_MB!MB)"
goto :eof

:print_summary
echo.
echo ============================================================
echo   BUILD COMPLETED SUCCESSFULLY
echo ============================================================
echo.
echo Build location: .\dist\
echo Executable:     .\dist\%APP_NAME%.exe
echo Launcher:       .\dist\launch.bat
echo.
echo Next steps:
echo   1. cd dist
echo   2. Edit input.json with your configuration
echo   3. Double-click launch.bat (or run %APP_NAME%.exe)
echo.
echo For distribution:
echo   - Zip the entire dist\ folder
echo   - Share with end users
echo   - Users only need to run launch.bat
echo.
goto :eof

REM ############################################################################
REM Main
REM ############################################################################

:main
call :print_header

REM Preflight checks
call :check_python
if errorlevel 1 exit /b 1

call :check_required_files
if errorlevel 1 exit /b 1

REM Setup
call :setup_venv
call :install_dependencies
call :install_playwright
if errorlevel 1 exit /b 1

call :verify_playwright
if errorlevel 1 exit /b 1

REM Build
call :clean_build
call :generate_spec
call :run_pyinstaller
if errorlevel 1 exit /b 1

REM Post-build
call :copy_assets
call :copy_playwright_browsers
call :create_launcher
call :create_readme
call :verify_build
if errorlevel 1 exit /b 1

REM Summary
call :print_summary

endlocal
pause
