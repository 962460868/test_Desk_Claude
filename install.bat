@echo off
REM 3D资产库浏览器 - Windows安装脚本
chcp 65001 >nul
cls

echo ==================================
echo 3D资产库浏览器 - 安装程序
echo ==================================
echo.

REM 检查Python
echo 检查Python版本...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python
    echo 请先从 https://www.python.org 下载安装Python 3.7或更高版本
    pause
    exit /b 1
)
python --version
echo.

REM 检查pip
echo 检查pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到pip
    echo 请重新安装Python并确保勾选"Add Python to PATH"
    pause
    exit /b 1
)
echo ✅ pip已安装
echo.

REM 安装依赖
echo 正在安装Python依赖包...
echo 这可能需要几分钟时间...
echo.

pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ==================================
    echo ✅ 安装完成！
    echo ==================================
    echo.
    echo 运行方法：
    echo   python main.py
    echo.
    echo 或者双击 run.bat
    echo.
    pause
) else (
    echo.
    echo ❌ 安装失败
    echo 请检查错误信息并尝试手动安装：
    echo   pip install PyQt5 PyOpenGL pyassimp numpy
    echo.
    pause
    exit /b 1
)
