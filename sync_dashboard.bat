@echo off
echo ===================================================
echo   UHRP Tracking Dashboard - Data Sync Utility
echo ===================================================
echo.
echo Syncing updated Excel sheets (Form A, B, C) with dashboard...
echo.

python "%~dp0generate_analysis_data.py"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================================
    echo  SUCCESS: Dashboard data updated successfully!
    echo ===================================================
    echo.
    echo Opening dashboard in your default browser...
    start "" "%~dp0index.html"
) else (
    echo.
    echo ===================================================
    echo  ERROR: Failed to update data. 
    echo  Please ensure Python is installed and Excel files 
    echo  are closed (not locked by Microsoft Excel).
    echo ===================================================
)
echo.
pause
