"""
主窗口模块 - 现代化UI版本
包含双栏布局的文件浏览器、文件预览和3D视图
"""
import os
import json
import platform
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QTreeView, QListWidget, QListWidgetItem,
                             QToolBar, QPushButton, QLabel, QGroupBox, QCheckBox,
                             QMessageBox, QStatusBar, QLineEdit, QFileSystemModel,
                             QComboBox, QGridLayout, QScrollArea, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QDir, QSize, pyqtSignal, QThread, QFileInfo
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from opengl_viewer import OpenGLViewer
from model_loader import ModelLoader


class FilePreviewWidget(QWidget):
    """文件预览卡片组件"""
    file_double_clicked = pyqtSignal(str)

    def __init__(self, file_path, file_name, is_dir=False):
        super().__init__()
        self.file_path = file_path
        self.file_name = file_name
        self.is_dir = is_dir

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # 缩略图/图标
        self.thumbnail = QLabel()
        self.thumbnail.setFixedSize(120, 120)
        self.thumbnail.setAlignment(Qt.AlignCenter)
        self.thumbnail.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 4px;
            }
        """)

        # 加载预览
        self._load_thumbnail()

        layout.addWidget(self.thumbnail)

        # 文件名
        name_label = QLabel(file_name)
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setMaximumWidth(130)
        name_label.setStyleSheet("color: #ccc; font-size: 11px;")
        layout.addWidget(name_label)

        # 启用鼠标点击
        self.setMaximumWidth(140)
        self.setMaximumHeight(160)

    def _load_thumbnail(self):
        """加载缩略图"""
        if self.is_dir:
            # 文件夹图标
            self._draw_folder_icon()
        else:
            ext = os.path.splitext(self.file_path)[1].lower()

            # 图片文件显示缩略图
            if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tga', '.tif', '.tiff']:
                pixmap = QPixmap(self.file_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.thumbnail.setPixmap(scaled)
                else:
                    self._draw_file_icon("IMG")
            # 3D模型文件
            elif ext in ['.fbx', '.obj', '.dae', '.3ds', '.blend', '.stl', '.gltf', '.glb']:
                self._draw_file_icon("3D")
            # 其他文件
            else:
                self._draw_file_icon(ext[1:].upper() if ext else "FILE")

    def _draw_folder_icon(self):
        """绘制文件夹图标"""
        pixmap = QPixmap(120, 120)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制文件夹
        painter.setBrush(QColor("#FDB44B"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(20, 40, 80, 60, 8, 8)
        painter.drawRoundedRect(20, 30, 40, 15, 4, 4)

        painter.end()
        self.thumbnail.setPixmap(pixmap)

    def _draw_file_icon(self, label_text):
        """绘制文件图标"""
        pixmap = QPixmap(120, 120)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制文件背景
        painter.setBrush(QColor("#4A90E2"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(25, 15, 70, 90, 8, 8)

        # 绘制文本
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Arial", 14, QFont.Bold)
        painter.setFont(font)
        painter.drawText(25, 15, 70, 90, Qt.AlignCenter, label_text)

        painter.end()
        self.thumbnail.setPixmap(pixmap)

    def mouseDoubleClickEvent(self, event):
        """双击事件"""
        self.file_double_clicked.emit(self.file_path)


class FileGridView(QWidget):
    """文件网格视图"""
    file_double_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_path = QDir.homePath()

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 路径栏
        path_bar = QHBoxLayout()
        self.path_label = QLabel()
        self.path_label.setStyleSheet("padding: 5px; background-color: #2d2d2d; color: #ccc;")
        path_bar.addWidget(self.path_label)

        main_layout.addLayout(path_bar)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        # 网格容器
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        scroll.setWidget(self.grid_container)
        main_layout.addWidget(scroll)

    def set_path(self, path):
        """设置当前路径并刷新显示"""
        if not os.path.exists(path):
            return

        self.current_path = path
        self.path_label.setText(f"📁 {path}")
        self._refresh_grid()

    def _refresh_grid(self):
        """刷新网格显示"""
        # 清空现有内容
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            # 获取文件列表
            entries = []

            # 添加父目录
            parent_dir = os.path.dirname(self.current_path)
            if parent_dir and parent_dir != self.current_path:
                entries.append(('..', parent_dir, True))

            # 列出目录内容
            if os.path.isdir(self.current_path):
                items = os.listdir(self.current_path)

                # 分类：文件夹在前
                dirs = []
                files = []

                for item in items:
                    full_path = os.path.join(self.current_path, item)
                    if os.path.isdir(full_path):
                        dirs.append((item, full_path, True))
                    else:
                        files.append((item, full_path, False))

                # 排序
                dirs.sort(key=lambda x: x[0].lower())
                files.sort(key=lambda x: x[0].lower())

                entries.extend(dirs)
                entries.extend(files)

            # 添加到网格
            row, col = 0, 0
            max_cols = 5  # 每行最多5个

            for name, path, is_dir in entries:
                widget = FilePreviewWidget(path, name, is_dir)
                widget.file_double_clicked.connect(self._on_file_double_clicked)

                self.grid_layout.addWidget(widget, row, col)

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

        except PermissionError:
            QMessageBox.warning(self, "权限错误", f"无法访问目录: {self.current_path}")
        except Exception as e:
            print(f"刷新网格时出错: {e}")

    def _on_file_double_clicked(self, path):
        """文件双击事件"""
        if os.path.isdir(path):
            # 如果是目录，进入该目录
            self.set_path(path)
        else:
            # 如果是文件，触发信号
            self.file_double_clicked.emit(path)


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()

        self.current_model_path = None
        self.model_loader = ModelLoader()
        self.favorite_folders = self._load_favorites()

        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("3D资产库浏览器 - 现代版")
        self.setGeometry(100, 100, 1600, 1000)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 创建工具栏
        self._create_toolbar()

        # 创建主分割器（左右分栏）
        main_splitter = QSplitter(Qt.Horizontal)

        # 左侧面板（文件系统 + 收藏夹）
        left_panel = self._create_left_panel()
        main_splitter.addWidget(left_panel)

        # 右侧面板（文件预览 + 3D视图）
        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)

        # 设置分割比例
        main_splitter.setSizes([350, 1250])

        main_layout.addWidget(main_splitter)

        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")

        # 应用样式
        self._apply_styles()

    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        # 搜索栏
        toolbar.addWidget(QLabel("  🔍 搜索: "))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入文件名搜索...")
        self.search_input.setMaximumWidth(300)
        self.search_input.returnPressed.connect(self.search_files)
        toolbar.addWidget(self.search_input)

        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.search_files)
        toolbar.addWidget(search_btn)

        toolbar.addSeparator()

        # 重置视图按钮
        reset_btn = QPushButton("重置视图")
        reset_btn.clicked.connect(self.reset_view)
        toolbar.addWidget(reset_btn)

        toolbar.addSeparator()

        # 显示模式标签
        toolbar.addWidget(QLabel("  显示: "))

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

    def _create_left_panel(self):
        """创建左侧面板"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)

        # 创建垂直分割器
        splitter = QSplitter(Qt.Vertical)

        # 上半部分：文件系统浏览器
        fs_group = QGroupBox("文件系统")
        fs_layout = QVBoxLayout(fs_group)

        # 磁盘选择器
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(QLabel("磁盘:"))

        self.disk_combo = QComboBox()
        self._populate_drives()
        self.disk_combo.currentTextChanged.connect(self._on_disk_changed)
        disk_layout.addWidget(self.disk_combo)

        fs_layout.addLayout(disk_layout)

        # 文件树
        self.file_tree = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_tree.setModel(self.file_model)

        # 只显示文件名列
        for i in range(1, 4):
            self.file_tree.hideColumn(i)

        self.file_tree.doubleClicked.connect(self._on_tree_double_clicked)

        fs_layout.addWidget(self.file_tree)

        splitter.addWidget(fs_group)

        # 下半部分：收藏的资产文件夹
        fav_group = QGroupBox("收藏夹")
        fav_layout = QVBoxLayout(fav_group)

        self.favorite_list = QListWidget()
        self.favorite_list.itemDoubleClicked.connect(self._on_favorite_clicked)
        self._refresh_favorites()

        fav_layout.addWidget(self.favorite_list)

        # 添加/删除收藏按钮
        fav_btn_layout = QHBoxLayout()

        add_fav_btn = QPushButton("+ 添加当前")
        add_fav_btn.clicked.connect(self.add_to_favorites)
        fav_btn_layout.addWidget(add_fav_btn)

        remove_fav_btn = QPushButton("- 删除")
        remove_fav_btn.clicked.connect(self.remove_from_favorites)
        fav_btn_layout.addWidget(remove_fav_btn)

        fav_layout.addLayout(fav_btn_layout)

        splitter.addWidget(fav_group)

        # 设置分割比例
        splitter.setSizes([400, 200])

        layout.addWidget(splitter)

        return container

    def _create_right_panel(self):
        """创建右侧面板"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建垂直分割器
        splitter = QSplitter(Qt.Vertical)

        # 上半部分：文件网格预览
        preview_group = QGroupBox("文件预览")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        self.file_grid = FileGridView()
        self.file_grid.file_double_clicked.connect(self.load_model)
        preview_layout.addWidget(self.file_grid)

        splitter.addWidget(preview_group)

        # 下半部分：3D预览
        viewer_group = QGroupBox("3D预览")
        viewer_layout = QVBoxLayout(viewer_group)

        self.viewer = OpenGLViewer()
        viewer_layout.addWidget(self.viewer)

        # 模型信息
        info_layout = QHBoxLayout()
        self.info_label = QLabel("未加载模型")
        self.info_label.setStyleSheet("color: #ccc; padding: 5px;")
        info_layout.addWidget(self.info_label)
        viewer_layout.addLayout(info_layout)

        splitter.addWidget(viewer_group)

        # 设置分割比例
        splitter.setSizes([400, 600])

        layout.addWidget(splitter)

        return container

    def _populate_drives(self):
        """填充磁盘列表"""
        self.disk_combo.clear()

        system = platform.system()

        if system == "Windows":
            # Windows: 列出所有磁盘
            import string
            from ctypes import windll

            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(f"{letter}:/")
                bitmask >>= 1

            self.disk_combo.addItems(drives)
        else:
            # Linux/Mac: 常用目录
            self.disk_combo.addItem(QDir.homePath())
            self.disk_combo.addItem("/")
            if os.path.exists("/media"):
                self.disk_combo.addItem("/media")
            if os.path.exists("/mnt"):
                self.disk_combo.addItem("/mnt")

        # 设置默认为用户主目录
        home = QDir.homePath()
        index = self.disk_combo.findText(home)
        if index >= 0:
            self.disk_combo.setCurrentIndex(index)
        elif self.disk_combo.count() > 0:
            self.disk_combo.setCurrentIndex(0)

    def _on_disk_changed(self, drive):
        """磁盘切换事件"""
        if drive and os.path.exists(drive):
            self.file_tree.setRootIndex(self.file_model.index(drive))
            self.file_grid.set_path(drive)

    def _on_tree_double_clicked(self, index):
        """文件树双击事件"""
        path = self.file_model.filePath(index)
        if os.path.isdir(path):
            self.file_grid.set_path(path)
        else:
            self.load_model(path)

    def _load_favorites(self):
        """加载收藏夹"""
        config_path = os.path.join(QDir.homePath(), ".3d_asset_viewer_favorites.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_favorites(self):
        """保存收藏夹"""
        config_path = os.path.join(QDir.homePath(), ".3d_asset_viewer_favorites.json")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.favorite_folders, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存收藏夹失败: {e}")

    def _refresh_favorites(self):
        """刷新收藏夹显示"""
        self.favorite_list.clear()
        for folder in self.favorite_folders:
            if os.path.exists(folder):
                item = QListWidgetItem(f"📁 {folder}")
                item.setData(Qt.UserRole, folder)
                self.favorite_list.addItem(item)

    def _on_favorite_clicked(self, item):
        """收藏夹点击事件"""
        folder = item.data(Qt.UserRole)
        if folder and os.path.exists(folder):
            self.file_grid.set_path(folder)
            self.file_tree.setRootIndex(self.file_model.index(folder))

    def add_to_favorites(self):
        """添加到收藏夹"""
        current = self.file_grid.current_path
        if current and current not in self.favorite_folders:
            self.favorite_folders.append(current)
            self._save_favorites()
            self._refresh_favorites()
            self.statusBar.showMessage(f"已添加到收藏: {current}")

    def remove_from_favorites(self):
        """从收藏夹删除"""
        current_item = self.favorite_list.currentItem()
        if current_item:
            folder = current_item.data(Qt.UserRole)
            if folder in self.favorite_folders:
                self.favorite_folders.remove(folder)
                self._save_favorites()
                self._refresh_favorites()
                self.statusBar.showMessage(f"已从收藏移除: {folder}")

    def search_files(self):
        """搜索文件"""
        query = self.search_input.text().strip()
        if not query:
            return

        current_path = self.file_grid.current_path

        # 简单搜索实现
        matches = []
        try:
            for root, dirs, files in os.walk(current_path):
                # 只搜索当前目录，不递归
                for file in files:
                    if query.lower() in file.lower():
                        matches.append(os.path.join(root, file))
                break  # 只搜索一层

            if matches:
                msg = f"找到 {len(matches)} 个匹配项:\n" + "\n".join(matches[:10])
                if len(matches) > 10:
                    msg += f"\n... 还有 {len(matches) - 10} 个"
                QMessageBox.information(self, "搜索结果", msg)
            else:
                QMessageBox.information(self, "搜索结果", "未找到匹配的文件")

        except Exception as e:
            QMessageBox.warning(self, "搜索错误", f"搜索时出错: {e}")

    def load_model(self, file_path: str):
        """加载3D模型"""
        # 检查是否是支持的格式
        if not self.model_loader.is_supported_format(file_path):
            self.statusBar.showMessage(f"不支持的文件格式: {file_path}")
            return

        self.statusBar.showMessage(f"正在加载: {file_path}")

        # 加载模型
        model_data = self.model_loader.load_model(file_path)

        if model_data:
            self.current_model_path = file_path
            self.viewer.load_model(model_data)

            # 更新信息
            filename = os.path.basename(file_path)
            self.info_label.setText(
                f"📄 {filename} | 顶点: {model_data.vertex_count:,} | 面: {model_data.face_count:,}"
            )

            self.statusBar.showMessage(f"加载成功: {filename}")
        else:
            QMessageBox.warning(self, "加载失败", f"无法加载模型文件:\n{file_path}\n\n请检查控制台输出了解详细错误信息。")
            self.statusBar.showMessage("加载失败")

    def reset_view(self):
        """重置3D视图"""
        self.viewer.reset_view()
        self.statusBar.showMessage("视图已重置")

    def update_display_mode(self):
        """更新显示模式"""
        show_solid = self.solid_checkbox.isChecked()
        show_wireframe = self.wireframe_checkbox.isChecked()
        self.viewer.set_display_mode(show_solid, show_wireframe)

    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QGroupBox {
                color: #ccc;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTreeView, QListWidget {
                background-color: #252525;
                color: #ccc;
                border: 1px solid #444;
            }
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5A9FE8;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ccc;
                border: 1px solid #444;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ccc;
                border: 1px solid #444;
                padding: 3px;
            }
            QToolBar {
                background-color: #2d2d2d;
                border-bottom: 1px solid #444;
                spacing: 5px;
                padding: 5px;
            }
            QStatusBar {
                background-color: #2d2d2d;
                color: #ccc;
            }
        """)
