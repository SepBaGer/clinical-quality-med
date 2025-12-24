@echo off
setlocal
echo ===================================================
echo   CLINICAL QUALITY DASHBOARD - GITHUB DEPLOYMENT
echo ===================================================

:: Ensure we are in the correct directory
cd /d "%~dp0"
echo Working Directory: %CD%

:: Check for Git in PATH first
set GIT_CMD=git
%GIT_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] 'git' not found in PATH. Searching common locations...
    
    if exist "C:\Program Files\Git\cmd\git.exe" (
        set GIT_CMD="C:\Program Files\Git\cmd\git.exe"
    ) else if exist "C:\Program Files\Git\bin\git.exe" (
        set GIT_CMD="C:\Program Files\Git\bin\git.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe" (
        set GIT_CMD="%LOCALAPPDATA%\Programs\Git\cmd\git.exe"
    ) else (
        color 4F
        echo.
        echo [ERROR] CRITICAL: Git executable not found automatically.
        echo Please make sure Git is installed and try running this script again.
        echo.
        pause
        exit /b 1
    )
)

echo Using Git: %GIT_CMD%
%GIT_CMD% --version

echo.
echo [1/5] Initializing/Updating Git Repo...
if not exist .git (
    %GIT_CMD% init
)
%GIT_CMD% branch -M main

echo.
echo [2/5] Staging files...
%GIT_CMD% add .

echo.
echo [3/5] Committing changes...
:: Allow commit to fail if nothing to commit
%GIT_CMD% commit -m "Manual deployment update" 

echo.
echo [4/5] Configuring Remote...
set REPO_URL=https://github.com/SepBaGer/clinical-quality-med.git
:: Remove origin if it exists to avoid conflicts on re-run
%GIT_CMD% remote remove origin >nul 2>&1
%GIT_CMD% remote add origin %REPO_URL%

echo.
echo [5/5] Pushing to GitHub...
echo Target: %REPO_URL%
%GIT_CMD% push -u origin main

if %errorlevel% neq 0 (
    color 4F
    echo.
    echo [ERROR] Push Failed! Check your internet or permissions.
    echo You may need to sign in to GitHub in the popup.
    pause
    exit /b 1
)

color 2F
echo.
echo [SUCCESS] Repository uploaded successfully!
echo You can now close this window.
pause
