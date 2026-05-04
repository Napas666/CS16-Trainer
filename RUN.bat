@echo off
cd /d "%~dp0"

echo Updating pip...
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org

echo Installing dependencies...
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

echo.
echo Starting CS 1.6 Trainer...
echo Run CS 1.6 first, then click ATTACH
echo.
python main.py
pause
