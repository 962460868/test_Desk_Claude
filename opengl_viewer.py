"""
OpenGL 3D视图组件
负责渲染和显示3D模型
"""
import numpy as np
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *
from model_loader import ModelData


class OpenGLViewer(QOpenGLWidget):
    """OpenGL 3D查看器组件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 模型数据
        self.model_data: ModelData = None

        # 视图参数
        self.rotation_x = 20.0
        self.rotation_y = 45.0
        self.zoom = 3.0

        # 鼠标交互
        self.last_mouse_pos = QPoint()
        self.mouse_pressed = False

        # 显示模式
        self.show_wireframe = True
        self.show_solid = True

        # 背景颜色
        self.bg_color = (0.2, 0.2, 0.25, 1.0)

    def initializeGL(self):
        """初始化OpenGL设置"""
        # 启用深度测试
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # 启用背面剔除
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # 设置光照
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # 设置光源
        light_pos = [5.0, 5.0, 5.0, 1.0]
        light_ambient = [0.3, 0.3, 0.3, 1.0]
        light_diffuse = [0.8, 0.8, 0.8, 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]

        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

        # 启用平滑着色
        glShadeModel(GL_SMOOTH)

        # 设置背景颜色
        glClearColor(*self.bg_color)

    def resizeGL(self, w, h):
        """窗口大小改变时调用"""
        if h == 0:
            h = 1

        glViewport(0, 0, w, h)

        # 设置投影矩阵
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect_ratio = w / h
        gluPerspective(45.0, aspect_ratio, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """渲染场景"""
        # 清除缓冲区
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 加载单位矩阵
        glLoadIdentity()

        # 设置相机位置
        gluLookAt(0, 0, self.zoom,  # 相机位置
                  0, 0, 0,           # 看向原点
                  0, 1, 0)           # 上方向

        # 应用旋转
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)

        # 绘制坐标轴
        self._draw_axis()

        # 绘制网格地板
        self._draw_grid()

        # 绘制模型
        if self.model_data:
            self._draw_model()

    def _draw_axis(self):
        """绘制坐标轴"""
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)

        glBegin(GL_LINES)

        # X轴 - 红色
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(1.0, 0.0, 0.0)

        # Y轴 - 绿色
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 1.0, 0.0)

        # Z轴 - 蓝色
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 1.0)

        glEnd()

        glEnable(GL_LIGHTING)

    def _draw_grid(self):
        """绘制网格地板"""
        glDisable(GL_LIGHTING)
        glColor3f(0.3, 0.3, 0.3)
        glLineWidth(1.0)

        grid_size = 10
        grid_step = 0.5

        glBegin(GL_LINES)
        for i in range(-grid_size, grid_size + 1):
            pos = i * grid_step
            # 平行于X轴的线
            glVertex3f(-grid_size * grid_step, -1.0, pos)
            glVertex3f(grid_size * grid_step, -1.0, pos)
            # 平行于Z轴的线
            glVertex3f(pos, -1.0, -grid_size * grid_step)
            glVertex3f(pos, -1.0, grid_size * grid_step)
        glEnd()

        glEnable(GL_LIGHTING)

    def _draw_model(self):
        """绘制3D模型"""
        if not self.model_data:
            return

        # 应用模型变换（居中和缩放）
        glPushMatrix()
        glScalef(self.model_data.scale, self.model_data.scale, self.model_data.scale)
        glTranslatef(-self.model_data.center[0], -self.model_data.center[1], -self.model_data.center[2])

        # 绘制实体模型
        if self.show_solid:
            glEnable(GL_LIGHTING)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glColor3f(0.7, 0.7, 0.7)  # 灰色材质

            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_NORMAL_ARRAY)

            glVertexPointer(3, GL_FLOAT, 0, self.model_data.vertices)
            glNormalPointer(GL_FLOAT, 0, self.model_data.normals)

            glDrawElements(GL_TRIANGLES, len(self.model_data.faces) * 3,
                          GL_UNSIGNED_INT, self.model_data.faces)

            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_NORMAL_ARRAY)

        # 绘制线框
        if self.show_wireframe:
            glDisable(GL_LIGHTING)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glColor3f(0.0, 0.0, 0.0)  # 黑色线框
            glLineWidth(1.0)

            # 如果同时显示实体，稍微偏移线框避免Z-fighting
            if self.show_solid:
                glEnable(GL_POLYGON_OFFSET_LINE)
                glPolygonOffset(-1.0, -1.0)

            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(3, GL_FLOAT, 0, self.model_data.vertices)
            glDrawElements(GL_TRIANGLES, len(self.model_data.faces) * 3,
                          GL_UNSIGNED_INT, self.model_data.faces)
            glDisableClientState(GL_VERTEX_ARRAY)

            if self.show_solid:
                glDisable(GL_POLYGON_OFFSET_LINE)

            glEnable(GL_LIGHTING)

        glPopMatrix()

    def load_model(self, model_data: ModelData):
        """
        加载模型数据

        Args:
            model_data: ModelData对象
        """
        self.model_data = model_data
        self.reset_view()
        self.update()

    def clear_model(self):
        """清除当前模型"""
        self.model_data = None
        self.update()

    def reset_view(self):
        """重置视图"""
        self.rotation_x = 20.0
        self.rotation_y = 45.0
        self.zoom = 3.0
        self.update()

    def set_display_mode(self, show_solid: bool, show_wireframe: bool):
        """
        设置显示模式

        Args:
            show_solid: 是否显示实体
            show_wireframe: 是否显示线框
        """
        self.show_solid = show_solid
        self.show_wireframe = show_wireframe
        self.update()

    # 鼠标事件处理
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        self.last_mouse_pos = event.pos()
        self.mouse_pressed = True

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.mouse_pressed = False

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if not self.mouse_pressed:
            return

        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()

        # 左键：旋转
        if event.buttons() & Qt.LeftButton:
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5
            self.update()

        # 右键：平移（暂不实现）

        self.last_mouse_pos = event.pos()

    def wheelEvent(self, event):
        """鼠标滚轮事件（缩放）"""
        delta = event.angleDelta().y()

        if delta > 0:
            self.zoom *= 0.9  # 放大
        else:
            self.zoom *= 1.1  # 缩小

        # 限制缩放范围
        self.zoom = max(0.5, min(self.zoom, 20.0))

        self.update()
