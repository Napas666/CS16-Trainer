@echo off
cd /d "%~dp0"

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting CS 1.6 Trainer...
echo Run CS 1.6 first, then click ATTACH
echo.
python main.py
pause
