@echo off
echo Updating topics data from HTML files...
python extract_topic.py .
if %ERRORLEVEL% equ 0 (
    echo.
    echo Update successful! topics.json has been refreshed.
) else (
    echo.
    echo Update failed. Please check the error messages above.
)
pause
