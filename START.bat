@echo off
cd /d "%~dp0"

echo [1/2] Installing dependencies...
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
pip install -r requirements.txt -i http://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo [2/2] Starting trainer...
echo Run CS 1.6 first, then click ATTACH in the app.
echo.
python trainer.py
pause
