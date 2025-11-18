#!/bin/bash
# 3D资产库浏览器 - 安装脚本

echo "=================================="
echo "3D资产库浏览器 - 安装程序"
echo "=================================="
echo ""

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1)
if [ $? -ne 0 ]; then
    echo "❌ 错误: 未找到Python3"
    echo "请先安装Python 3.7或更高版本"
    exit 1
fi
echo "✅ $python_version"
echo ""

# 检查pip
echo "检查pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到pip3"
    echo "请先安装pip3"
    exit 1
fi
echo "✅ pip3 已安装"
echo ""

# 安装依赖
echo "正在安装Python依赖包..."
echo "这可能需要几分钟时间..."
echo ""

pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ 安装完成！"
    echo "=================================="
    echo ""
    echo "运行方法："
    echo "  python3 main.py"
    echo ""
    echo "或者："
    echo "  chmod +x main.py"
    echo "  ./main.py"
    echo ""
else
    echo ""
    echo "❌ 安装失败"
    echo "请检查错误信息并尝试手动安装："
    echo "  pip3 install PyQt5 PyOpenGL pyassimp numpy"
    echo ""
    exit 1
fi
