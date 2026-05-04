@echo off
cd /d "%~dp0"

echo [1/2] Installing dependencies...
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org -q
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

echo.
echo [2/2] Starting trainer...
echo Run CS 1.6 first, then click ATTACH in the app.
echo.
python trainer.py
pause
