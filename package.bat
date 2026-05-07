@echo off
REM ================================================================
REM  AutoClicker — build script
REM  Run this once on your Windows machine to produce AutoClicker.exe
REM ================================================================

echo [1/3] Installing PyInstaller...
pip install pyinstaller --quiet

echo [2/3] Building AutoClicker.exe (single file, no console window)...
python -m PyInstaller autoclicker_gui.py ^
    --onefile ^
    --noconsole ^
    --name FastAutoClicker ^
    --clean

echo [3/3] Done!
echo.
echo  Output: dist\AutoClicker.exe
echo.
pause