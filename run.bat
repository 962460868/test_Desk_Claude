@echo off
REM 3D资产库浏览器 - 启动脚本
chcp 65001 >nul
python main.py
if %errorlevel% neq 0 (
    echo.
    echo 启动失败，请先运行 install.bat 安装依赖
    pause
)
