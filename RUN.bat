@echo off
cd /d "%~dp0"

echo Installing dependencies (via mirror)...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo Starting CS 1.6 Trainer...
echo Run CS 1.6 first, then click ATTACH
echo.
python main.py
pause
