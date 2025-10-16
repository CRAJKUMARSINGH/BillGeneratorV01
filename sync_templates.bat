@echo off
REM Template Synchronization Script
REM This script synchronizes HTML templates across multiple directories

echo Template Synchronization Script
echo =============================

REM Copy templates from main directory to backup directories
echo Copying templates to templates_14102025...
copy /Y "templates\*.html" "templates_14102025\"

echo Copying templates to templates_14102025\templates_14102025...
copy /Y "templates\*.html" "templates_14102025\templates_14102025\"

echo Copying templates to templates_14102025\templates_14102025\tested templates...
copy /Y "templates\*.html" "templates_14102025\templates_14102025\tested templates\"

echo.
echo Template synchronization completed!
echo All templates are now synchronized across directories.
echo.

REM Verify the synchronization
echo Verifying synchronization...
echo Main templates directory:
dir /b "templates\*.html" | find /c /v ""
echo.
echo Backup templates directory:
dir /b "templates_14102025\*.html" | find /c /v ""
echo.
echo Nested templates directory:
dir /b "templates_14102025\templates_14102025\*.html" | find /c /v ""
echo.
echo Tested templates directory:
dir /b "templates_14102025\templates_14102025\tested templates\*.html" | find /c /v ""

echo.
echo Verification completed!
pause