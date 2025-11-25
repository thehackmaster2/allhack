@echo off
echo.
echo ========================================
echo   NeoxSecBot - Cleanup Results Folder
echo ========================================
echo.
echo This will delete the deprecated 'results' folder
echo All data is now stored in Firebase only
echo.

if exist results (
    echo Found results folder
    echo.
    choice /C YN /M "Delete results folder"
    if errorlevel 2 goto :cancel
    if errorlevel 1 goto :delete
) else (
    echo Results folder not found (already clean)
    echo Bot is using Firebase-only storage
    goto :end
)

:delete
echo.
echo Deleting results folder...
rmdir /s /q results
if %errorlevel% == 0 (
    echo.
    echo [SUCCESS] Results folder deleted!
    echo [INFO] All data is now in Firebase only
) else (
    echo.
    echo [ERROR] Failed to delete folder
)
goto :end

:cancel
echo.
echo Cleanup cancelled
goto :end

:end
echo.
echo ========================================
echo   Current Storage Configuration
echo ========================================
echo   Chat History: Firebase
echo   Scan Results: Firebase
echo   User Data: Firebase
echo   Local Storage: None
echo ========================================
echo.
pause
