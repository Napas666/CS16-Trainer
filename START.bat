@echo off
cd /d "%~dp0"

REM Clear proxy vars that VPN sets and breaks pip SSL
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=
set ALL_PROXY=
set all_proxy=

echo [1/3] Configuring pip...
pip config set global.index-url http://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

echo [2/3] Installing dependencies...
pip install pymem customtkinter pygame pywin32 --no-cache-dir

echo.
echo [3/3] Starting trainer...
echo Run CS 1.6 first, then click ATTACH.
echo.
python trainer.py
pause
