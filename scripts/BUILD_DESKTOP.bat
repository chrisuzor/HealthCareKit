@echo off
echo ========================================
echo HealthCareKit Desktop App Builder
echo ========================================
echo.

echo Step 1: Checking dependencies...
python ..\tests\test_desktop.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Dependency check failed!
    echo Please install missing dependencies and try again.
    pause
    exit /b 1
)

echo.
echo Step 2: Building desktop application...
python build_desktop_app.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo BUILD COMPLETE!
    echo ========================================
    echo.
    echo Your desktop app is ready at: dist\HealthCareKit.exe
    echo.
    echo Press any key to test the app...
    pause > nul
    start dist\HealthCareKit.exe
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Please check the error messages above.
    pause
)
