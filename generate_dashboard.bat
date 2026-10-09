@echo off
echo ===================================================
echo   UHRP Tracking Dashboard - Generate Dashboard
echo ===================================================
echo.
echo Compiling data and generating latest dashboard...
echo.

python "%~dp0generate_analysis_data.py"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================================
    echo  SUCCESS: Dashboard generated successfully!
    echo ===================================================
    echo.
    echo Opening UHRP Tracking Dashboard in your browser...
    start "" "%~dp0index.html"
) else (
    echo.
    echo ===================================================
    echo  ERROR: Failed to generate dashboard.
    echo  Please ensure Excel files are closed and Python is available.
    echo ===================================================
)
echo.
pause
