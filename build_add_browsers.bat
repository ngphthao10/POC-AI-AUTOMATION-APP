@echo off
echo ============================================================
echo Copy Playwright Browsers to dist folder
echo ============================================================
echo.

if not exist "dist\csp_automation.exe" (
    echo ERROR: Run build_simple.bat first!
    pause
    exit /b 1
)

set PLAYWRIGHT_SRC=%USERPROFILE%\AppData\Local\ms-playwright
set PLAYWRIGHT_DEST=dist\ms-playwright

echo Checking for Playwright browsers...
if not exist "%PLAYWRIGHT_SRC%\" (
    echo ERROR: Playwright browsers not found at:
    echo %PLAYWRIGHT_SRC%
    echo.
    echo Please run: playwright install chromium
    pause
    exit /b 1
)

echo Found browsers at: %PLAYWRIGHT_SRC%
echo.
echo Copying to dist folder (this takes 2-3 minutes for ~400MB)...
echo Please wait, do not cancel!
echo.

xcopy /E /I /Y /Q "%PLAYWRIGHT_SRC%" "%PLAYWRIGHT_DEST%"

if errorlevel 1 (
    echo ERROR: Copy failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo BROWSERS COPIED SUCCESSFULLY!
echo ============================================================
echo.
echo Now you can zip the entire dist\ folder and distribute
echo Size: ~450MB (includes browsers)
echo.
pause
