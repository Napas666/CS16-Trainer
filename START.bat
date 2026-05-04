@echo off
cd /d "%~dp0"

echo [1/3] Configuring pip...
pip config set global.index-url http://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

echo [2/3] Installing dependencies...
pip install pymem customtkinter pygame pywin32

echo.
echo [3/3] Starting trainer...
echo Run CS 1.6 first, then click ATTACH.
echo.
python trainer.py
pause
