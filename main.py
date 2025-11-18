#!/usr/bin/env python3
"""
3D资产库浏览器
主程序入口
"""
import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow


def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)

    # 设置应用程序信息
    app.setApplicationName("3D资产库浏览器")
    app.setOrganizationName("FBX Viewer")

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 启动应用程序事件循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
