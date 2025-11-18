"""
主窗口模块
包含文件浏览器、3D视图和控制面板
"""
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QTreeView, QFileSystemModel, QToolBar,
                             QPushButton, QLabel, QGroupBox, QCheckBox,
                             QMessageBox, QStatusBar)
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QIcon
from opengl_viewer import OpenGLViewer
from model_loader import ModelLoader


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()

        self.current_model_path = None
        self.model_loader = ModelLoader()

        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("3D资产库浏览器 - FBX Viewer")
        self.setGeometry(100, 100, 1400, 900)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)

        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：文件浏览器
        left_panel = self._create_file_browser()
        splitter.addWidget(left_panel)

        # 中间：3D视图
        middle_panel = self._create_viewer_panel()
        splitter.addWidget(middle_panel)

        # 右侧：信息面板
        right_panel = self._create_info_panel()
        splitter.addWidget(right_panel)

        # 设置分割器比例
        splitter.setSizes([300, 800, 300])

        main_layout.addWidget(splitter)

        # 创建工具栏
        self._create_toolbar()

        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")

    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # 重置视图按钮
        reset_btn = QPushButton("重置视图")
        reset_btn.clicked.connect(self.reset_view)
        toolbar.addWidget(reset_btn)

        toolbar.addSeparator()

        # 显示模式标签
        toolbar.addWidget(QLabel("  显示模式: "))

        # 实体显示复选框
        self.solid_checkbox = QCheckBox("实体")
        self.solid_checkbox.setChecked(True)
        self.solid_checkbox.stateChanged.connect(self.update_display_mode)
        toolbar.addWidget(self.solid_checkbox)

        # 线框显示复选框
        self.wireframe_checkbox = QCheckBox("线框")
        self.wireframe_checkbox.setChecked(True)
        self.wireframe_checkbox.stateChanged.connect(self.update_display_mode)
        toolbar.addWidget(self.wireframe_checkbox)

        toolbar.addSeparator()

        # 帮助信息
        help_btn = QPushButton("使用说明")
        help_btn.clicked.connect(self.show_help)
        toolbar.addWidget(help_btn)

    def _create_file_browser(self):
        """创建文件浏览器"""
        container = QWidget()
        layout = QVBoxLayout(container)

        # 标签
        label = QLabel("文件浏览器")
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(label)

        # 文件树视图
        self.file_tree = QTreeView()
        self.file_model = QFileSystemModel()

        # 设置根目录（用户主目录）
        home_dir = QDir.homePath()
        self.file_model.setRootPath(home_dir)

        # 设置文件过滤器（只显示3D模型文件）
        self.file_model.setNameFilters([
            "*.fbx", "*.FBX",
            "*.obj", "*.OBJ",
            "*.dae", "*.DAE",
            "*.3ds", "*.3DS",
            "*.blend", "*.BLEND",
            "*.stl", "*.STL"
        ])
        self.file_model.setNameFilterDisables(False)

        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(home_dir))

        # 只显示文件名列
        self.file_tree.setColumnWidth(0, 250)
        for i in range(1, 4):
            self.file_tree.hideColumn(i)

        # 双击加载模型
        self.file_tree.doubleClicked.connect(self.load_selected_model)

        layout.addWidget(self.file_tree)

        # 添加路径切换按钮
        path_layout = QHBoxLayout()

        home_btn = QPushButton("主目录")
        home_btn.clicked.connect(lambda: self.change_directory(QDir.homePath()))
        path_layout.addWidget(home_btn)

        desktop_btn = QPushButton("桌面")
        desktop_btn.clicked.connect(lambda: self.change_directory(
            os.path.join(QDir.homePath(), "Desktop")))
        path_layout.addWidget(desktop_btn)

        layout.addLayout(path_layout)

        return container

    def _create_viewer_panel(self):
        """创建3D视图面板"""
        container = QWidget()
        layout = QVBoxLayout(container)

        # 标签
        label = QLabel("3D预览窗口")
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(label)

        # OpenGL视图
        self.viewer = OpenGLViewer()
        layout.addWidget(self.viewer)

        # 操作提示
        hint_label = QLabel("鼠标左键拖动: 旋转 | 滚轮: 缩放")
        hint_label.setStyleSheet("color: #666; font-size: 11px;")
        hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint_label)

        return container

    def _create_info_panel(self):
        """创建信息面板"""
        container = QWidget()
        layout = QVBoxLayout(container)

        # 标签
        label = QLabel("模型信息")
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(label)

        # 信息组
        info_group = QGroupBox("文件详情")
        info_layout = QVBoxLayout()

        self.info_filename = QLabel("文件名: -")
        self.info_filename.setWordWrap(True)
        info_layout.addWidget(self.info_filename)

        self.info_vertices = QLabel("顶点数: -")
        info_layout.addWidget(self.info_vertices)

        self.info_faces = QLabel("面数: -")
        info_layout.addWidget(self.info_faces)

        self.info_bounds = QLabel("尺寸: -")
        self.info_bounds.setWordWrap(True)
        info_layout.addWidget(self.info_bounds)

        info_layout.addStretch()

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # 快捷操作组
        actions_group = QGroupBox("快捷操作")
        actions_layout = QVBoxLayout()

        reload_btn = QPushButton("重新加载模型")
        reload_btn.clicked.connect(self.reload_model)
        actions_layout.addWidget(reload_btn)

        clear_btn = QPushButton("清除模型")
        clear_btn.clicked.connect(self.clear_model)
        actions_layout.addWidget(clear_btn)

        actions_layout.addStretch()

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        layout.addStretch()

        return container

    def change_directory(self, path: str):
        """更改文件浏览器目录"""
        if os.path.exists(path):
            self.file_tree.setRootIndex(self.file_model.index(path))
            self.statusBar.showMessage(f"切换到: {path}")

    def load_selected_model(self, index):
        """加载选中的模型文件"""
        file_path = self.file_model.filePath(index)

        # 检查是否是文件
        if not os.path.isfile(file_path):
            return

        self.load_model(file_path)

    def load_model(self, file_path: str):
        """
        加载3D模型

        Args:
            file_path: 模型文件路径
        """
        self.statusBar.showMessage(f"正在加载: {file_path}")

        # 加载模型
        model_data = self.model_loader.load_model(file_path)

        if model_data:
            self.current_model_path = file_path
            self.viewer.load_model(model_data)

            # 更新信息面板
            filename = os.path.basename(file_path)
            self.info_filename.setText(f"文件名: {filename}")
            self.info_vertices.setText(f"顶点数: {model_data.vertex_count:,}")
            self.info_faces.setText(f"面数: {model_data.face_count:,}")

            bounds_size = model_data.bounds_max - model_data.bounds_min
            self.info_bounds.setText(
                f"尺寸: {bounds_size[0]:.2f} x {bounds_size[1]:.2f} x {bounds_size[2]:.2f}"
            )

            self.statusBar.showMessage(f"加载成功: {filename}")
        else:
            QMessageBox.warning(self, "加载失败", f"无法加载模型文件:\n{file_path}")
            self.statusBar.showMessage("加载失败")

    def reload_model(self):
        """重新加载当前模型"""
        if self.current_model_path:
            self.load_model(self.current_model_path)
        else:
            self.statusBar.showMessage("没有已加载的模型")

    def clear_model(self):
        """清除当前模型"""
        self.viewer.clear_model()
        self.current_model_path = None

        # 清空信息面板
        self.info_filename.setText("文件名: -")
        self.info_vertices.setText("顶点数: -")
        self.info_faces.setText("面数: -")
        self.info_bounds.setText("尺寸: -")

        self.statusBar.showMessage("模型已清除")

    def reset_view(self):
        """重置3D视图"""
        self.viewer.reset_view()
        self.statusBar.showMessage("视图已重置")

    def update_display_mode(self):
        """更新显示模式"""
        show_solid = self.solid_checkbox.isChecked()
        show_wireframe = self.wireframe_checkbox.isChecked()

        self.viewer.set_display_mode(show_solid, show_wireframe)

    def show_help(self):
        """显示帮助信息"""
        help_text = """
<h3>3D资产库浏览器 - 使用说明</h3>

<p><b>基本操作：</b></p>
<ul>
  <li>在左侧文件浏览器中<b>双击</b>FBX文件即可加载预览</li>
  <li>使用<b>鼠标左键拖动</b>旋转模型</li>
  <li>使用<b>鼠标滚轮</b>缩放视图</li>
  <li>点击<b>重置视图</b>按钮恢复默认视角</li>
</ul>

<p><b>显示模式：</b></p>
<ul>
  <li><b>实体</b>：显示模型表面</li>
  <li><b>线框</b>：显示模型布线</li>
  <li>可以同时勾选两者，查看实体+线框效果</li>
</ul>

<p><b>支持的文件格式：</b></p>
<ul>
  <li>FBX (.fbx)</li>
  <li>OBJ (.obj)</li>
  <li>Collada (.dae)</li>
  <li>3DS (.3ds)</li>
  <li>STL (.stl)</li>
  <li>Blender (.blend)</li>
</ul>

<p><b>提示：</b>右侧面板显示模型的详细信息（顶点数、面数等）</p>
        """

        QMessageBox.information(self, "使用说明", help_text)
