@echo off
cd /d "%~dp0"

echo Installing dependencies (offline, no internet needed)...
pip install --no-index --find-links=wheels pymem customtkinter pygame pywin32

echo.
echo Starting trainer...
echo Run CS 1.6 first, then click ATTACH.
echo.
python trainer.py
pause
