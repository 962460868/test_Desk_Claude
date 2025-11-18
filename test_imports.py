#!/usr/bin/env python3
"""
测试脚本 - 检查所有依赖是否正确安装
"""
import sys

print("=" * 50)
print("3D资产库浏览器 - 依赖检查")
print("=" * 50)
print()

# 检查Python版本
print(f"Python版本: {sys.version}")
print()

# 检查各个依赖
dependencies = [
    ("PyQt5", "PyQt5.QtWidgets"),
    ("PyQt5.QtCore", "PyQt5.QtCore"),
    ("PyQt5.QtGui", "PyQt5.QtGui"),
    ("PyOpenGL", "OpenGL.GL"),
    ("PyOpenGL.GLU", "OpenGL.GLU"),
    ("pyassimp", "pyassimp"),
    ("numpy", "numpy"),
]

all_ok = True

for name, module in dependencies:
    try:
        __import__(module)
        print(f"✅ {name:20s} - 已安装")
    except ImportError as e:
        print(f"❌ {name:20s} - 未安装")
        all_ok = False

print()

if all_ok:
    print("=" * 50)
    print("✅ 所有依赖已正确安装！")
    print("=" * 50)
    print()
    print("可以运行程序:")
    print("  python3 main.py")
    print()
else:
    print("=" * 50)
    print("❌ 部分依赖未安装")
    print("=" * 50)
    print()
    print("请运行安装命令:")
    print("  pip3 install -r requirements.txt")
    print()
    print("或手动安装:")
    print("  pip3 install PyQt5 PyOpenGL pyassimp numpy")
    print()

# 如果所有依赖都安装了，测试模块导入
if all_ok:
    print("测试项目模块导入...")
    try:
        import model_loader
        print("✅ model_loader - OK")
    except Exception as e:
        print(f"❌ model_loader - {e}")
        all_ok = False

    try:
        import opengl_viewer
        print("✅ opengl_viewer - OK")
    except Exception as e:
        print(f"❌ opengl_viewer - {e}")
        all_ok = False

    try:
        import main_window
        print("✅ main_window - OK")
    except Exception as e:
        print(f"❌ main_window - {e}")
        all_ok = False

    print()
    if all_ok:
        print("✅ 所有模块导入成功！程序可以正常运行。")
    else:
        print("❌ 模块导入失败，请检查错误信息。")

sys.exit(0 if all_ok else 1)
