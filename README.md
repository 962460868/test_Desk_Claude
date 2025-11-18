# 3D资产库浏览器 - FBX Viewer

一个基于Python的3D模型预览软件，支持FBX、OBJ等多种3D格式，可以快速浏览模型的网格和布线。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)

## ✨ 功能特性

- 🎯 **FBX文件预览**：原生支持FBX格式
- 📁 **文件浏览器**：方便浏览和加载本地3D模型文件
- 🔄 **多种显示模式**：实体、线框、实体+线框
- 🖱️ **交互式3D视图**：鼠标旋转、缩放
- 📊 **模型信息显示**：顶点数、面数、尺寸等
- 🎨 **简洁界面**：类似专业3D软件的布局

## 🖼️ 支持的文件格式

- ✅ FBX (.fbx)
- ✅ OBJ (.obj)
- ✅ Collada (.dae)
- ✅ 3DS (.3ds)
- ✅ STL (.stl)
- ✅ Blender (.blend)

## 📋 系统要求

- Python 3.7 或更高版本
- OpenGL 2.0+ 支持的显卡
- Windows / Linux / macOS

## 🚀 安装步骤

### 1. 克隆或下载本项目

```bash
git clone <repository-url>
cd test_Desk_Claude
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

**注意**：如果你在安装`pyassimp`时遇到问题，可能需要先安装Assimp库：

**Ubuntu/Debian:**
```bash
sudo apt-get install libassimp-dev
```

**macOS (使用Homebrew):**
```bash
brew install assimp
```

**Windows:**
通常`pip install pyassimp`即可，如果有问题可以尝试：
```bash
pip install pyassimp --no-cache-dir
```

### 3. 运行程序

```bash
python main.py
```

## 📖 使用说明

### 基本操作

1. **加载模型**
   - 在左侧文件浏览器中找到你的FBX文件
   - 双击文件即可加载到3D视图中

2. **视图控制**
   - **旋转**：按住鼠标左键拖动
   - **缩放**：使用鼠标滚轮

3. **显示模式**
   - 顶部工具栏可以切换显示模式：
     - ☑️ **实体**：显示模型表面
     - ☑️ **线框**：显示模型布线
     - 可以同时勾选查看实体+线框效果

4. **重置视图**
   - 点击工具栏的"重置视图"按钮恢复默认视角

### 快捷目录切换

- 点击左侧的"主目录"或"桌面"按钮可以快速切换浏览目录

### 模型信息

右侧面板显示当前模型的详细信息：
- 文件名
- 顶点数
- 面数
- 模型尺寸

## 🎨 界面布局

```
┌─────────────────────────────────────────────────────────────┐
│  [重置视图] | 显示: ☑实体 ☑线框 | [使用说明]                  │
├──────────┬────────────────────────────────────┬─────────────┤
│          │                                    │             │
│  文件    │        3D预览窗口                   │  模型信息   │
│  浏览器  │                                    │             │
│          │      [3D模型显示区域]               │  文件详情   │
│  📁 FBX  │                                    │  ・顶点数   │
│  📁 OBJ  │                                    │  ・面数     │
│  📁 ...  │                                    │  ・尺寸     │
│          │                                    │             │
│  [主目录]│      鼠标左键: 旋转                 │  快捷操作   │
│  [桌面]  │      滚轮: 缩放                     │  [重新加载] │
│          │                                    │  [清除模型] │
└──────────┴────────────────────────────────────┴─────────────┘
```

## 🔧 项目结构

```
test_Desk_Claude/
├── main.py              # 主程序入口
├── main_window.py       # 主窗口和UI逻辑
├── opengl_viewer.py     # OpenGL 3D视图组件
├── model_loader.py      # 3D模型加载器
├── requirements.txt     # Python依赖列表
└── README.md           # 项目说明文档
```

## 🐛 常见问题

### Q: 安装pyassimp失败
A: 确保系统已安装Assimp库（见上方安装步骤），或尝试：
```bash
pip install pyassimp --no-cache-dir
```

### Q: 打开软件显示黑屏
A: 检查显卡是否支持OpenGL 2.0+，尝试更新显卡驱动

### Q: 某些FBX文件无法加载
A: FBX格式有多个版本，如果遇到问题可以尝试：
- 使用Blender等软件重新导出为较新版本的FBX
- 转换为OBJ格式后加载

### Q: 模型显示不完整或变形
A: 这是归一化缩放的结果，软件会自动将模型缩放到合适大小以便预览

## 💡 技术栈

- **GUI框架**: PyQt5
- **3D渲染**: PyOpenGL
- **模型加载**: PyAssimp
- **数值计算**: NumPy

## 📝 开发说明

本项目采用模块化设计，各模块职责清晰：

- `model_loader.py`: 负责使用Assimp库加载各种3D模型格式
- `opengl_viewer.py`: 使用OpenGL实现3D渲染和交互
- `main_window.py`: PyQt5界面布局和用户交互逻辑
- `main.py`: 应用程序入口

如需扩展功能，可以：
- 添加更多显示选项（如材质、纹理支持）
- 实现更多相机控制（如平移、聚焦）
- 添加模型对比功能
- 支持导出截图

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

如有问题或建议，欢迎联系。

---

**享受3D模型浏览的乐趣！** 🎉
