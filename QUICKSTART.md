# 快速开始指南

## 5分钟快速上手

### Windows用户

1. **安装依赖**
   ```
   双击运行 install.bat
   ```

2. **启动程序**
   ```
   双击运行 run.bat
   或
   双击运行 main.py
   ```

3. **加载模型**
   - 在左侧文件浏览器找到你的FBX文件
   - 双击文件即可预览

### Linux/Mac用户

1. **安装依赖**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   或手动安装:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **启动程序**
   ```bash
   python3 main.py
   ```

3. **加载模型**
   - 在左侧文件浏览器找到你的FBX文件
   - 双击文件即可预览

## 基本控制

| 操作 | 说明 |
|------|------|
| 鼠标左键拖动 | 旋转模型 |
| 鼠标滚轮 | 缩放视图 |
| 重置视图按钮 | 恢复默认视角 |

## 显示模式

- ☑️ **实体**: 显示模型表面（灰色材质）
- ☑️ **线框**: 显示模型布线（黑色线条）
- 两者可以同时勾选，查看实体+线框组合效果

## 常见问题

**Q: 安装时出错怎么办？**

A: 尝试逐个安装依赖：
```bash
pip3 install PyQt5
pip3 install PyOpenGL
pip3 install numpy
pip3 install pyassimp
```

**Q: 可以测试程序是否正确安装吗？**

A: 运行测试脚本：
```bash
python3 test_imports.py
```

**Q: 支持哪些3D文件格式？**

A: 支持FBX、OBJ、DAE、3DS、STL、BLEND等格式

## 示例文件

如果你没有测试用的3D模型，可以：

1. 从这些网站下载免费模型：
   - [Sketchfab](https://sketchfab.com/) (支持下载FBX)
   - [Free3D](https://free3d.com/)
   - [TurboSquid](https://www.turbosquid.com/Search/3D-Models/free)

2. 使用Blender创建简单模型并导出为FBX

## 下一步

查看完整的 [README.md](README.md) 了解更多功能和详细信息。

---

**祝你使用愉快！** 🎉
