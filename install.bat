@echo off
set EXE_NAME=AiAdvisor
set OUT_DIR=install

echo Installing %EXE_NAME%...
pyinstaller --noconfirm --onefile --windowed ^
  --name %EXE_NAME%                          ^
  --icon "ico\brain.ico"                     ^
  --add-data "includes;includes/"            ^
  --add-data "controllers;controllers/"      ^
  --add-data "controls;controls/"            ^
  --add-data "icons;icons/"                  ^
  --add-data "Main.qml;."                    ^
  --exclude-module PyQt5                     ^
  --exclude-module sklearn                   ^
  --exclude-module torch                     ^
  --exclude-module keras                     ^
  --exclude-module tensorflow                ^
  --distpath %OUT_DIR%                       ^
  main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ======================================================
    echo BUILD FAILED
    echo ======================================================
    echo.
    echo PyInstaller encountered an error during the build process.
    echo Please check the error messages above for details.
    echo.
    echo Common issues:
    echo   - Missing dependencies or modules
    echo   - Insufficient disk space
    echo   - File permission issues
    echo   - Invalid file paths in --add-data arguments
    echo.
    echo ======================================================
    pause
    exit /b 1
)

if not exist "%OUT_DIR%\%EXE_NAME%.exe" (
    echo.
    echo ======================================================
    echo BUILD VERIFICATION FAILED
    echo ======================================================
    echo.
    echo PyInstaller completed but the executable was not found.
    echo Expected location: %OUT_DIR%\%EXE_NAME%.exe
    echo.
    echo Please check the PyInstaller output above for errors.
    echo.
    echo ======================================================
    pause
    exit /b 1
)

echo Copying configuration files...
xcopy /E /I /Y "config" "%OUT_DIR%\config"

if %ERRORLEVEL% neq 0 (
    echo.
    echo WARNING: Failed to copy configuration files.
    echo Please manually copy the 'config' folder to '%OUT_DIR%\config'
    echo.
)

echo Cleaning up temporary files...
if exist "build" rmdir /S /Q "build"
if exist "__pycache__" rmdir /S /Q "__pycache__"
if exist "%EXE_NAME%.spec" del "%EXE_NAME%.spec"

echo.
echo ======================================================
echo INSTALL COMPLETED!
echo ======================================================
echo.
echo The AiAdvisor application has been built and is ready for use.
echo.
echo VERIFICATION:
echo   Executable created: %OUT_DIR%\%EXE_NAME%.exe
echo   File size: 
for %%A in ("%OUT_DIR%\%EXE_NAME%.exe") do echo      %%~zA bytes
echo.
echo REQUIRED CONFIGURATION:
echo   Location: %OUT_DIR%\config\config.xml
echo.
echo   Please configure the following before running the application:
echo   1. Add your API keys for each AI model provider
echo   2. Configure or add your preferred AI models
echo   3. Adjust timeout settings if needed (optional)
echo.
echo OUTPUT DIRECTORY: %OUT_DIR%\
echo EXECUTABLE: %OUT_DIR%\%EXE_NAME%.exe
echo.
echo ======================================================
pause