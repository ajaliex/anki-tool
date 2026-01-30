@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo       GitHub Upload Tool for Theory Memorization App
echo ========================================================
echo.

:: Check for Git
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git is not installed. Please install specific Git for Windows first.
    pause
    exit /b
)

:: Initialize or re-initialize
if not exist ".git" (
    echo [INFO] Initializing Git repository...
    git init
    git branch -M main
)

:: Configure dummy user if not set (fixing the commit error)
git config user.email "anki-tool@example.com"
git config user.name "Anki Tool User"

:: Add files
echo [INFO] Adding files...
git add .

:: Commit (allow empty if nothing changed)
echo [INFO] Committing changes...
git commit -m "Update topic data" >nul 2>nul

echo.
echo ========================================================
echo Please enter your GitHub Repository URL.
echo (Right-click to paste)
echo Example: https://github.com/YourName/anki-tool.git
echo ========================================================
set /p REPO_URL="Repository URL: "

:: Update remote
git remote remove origin >nul 2>nul
git remote add origin !REPO_URL!

:: Push
echo.
echo [INFO] Pushing to GitHub...
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo [SUCCESS] Upload completed successfully!
    echo ========================================================
) else (
    echo.
    echo [ERROR] Push failed. 
    echo Please check your internet connection or URL.
)

pause
