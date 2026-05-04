@echo off
cd /d "%~dp0"

echo [1/3] Disabling system proxy temporarily...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f >/dev/null

echo [2/3] Installing dependencies...
pip install pymem customtkinter pygame pywin32 -i http://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --no-cache-dir

echo [2/3] Restoring system proxy...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f >/dev/null

echo.
echo [3/3] Starting trainer...
echo Run CS 1.6 first, then click ATTACH.
echo.
python trainer.py
pause
