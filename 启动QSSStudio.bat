@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动 QSS Studio...
python qss_designer.py
if errorlevel 1 (
    echo.
    echo 程序异常退出，请将上方错误信息反馈。
    pause
)
