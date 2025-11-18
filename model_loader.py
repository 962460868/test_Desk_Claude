"""
3D模型加载器模块
负责加载FBX等3D模型文件
"""
import pyassimp
import numpy as np
from typing import Optional, Dict, List, Tuple


class ModelData:
    """存储3D模型数据"""
    def __init__(self):
        self.vertices: np.ndarray = np.array([])
        self.faces: np.ndarray = np.array([])
        self.normals: np.ndarray = np.array([])
        self.bounds_min: np.ndarray = np.array([0, 0, 0])
        self.bounds_max: np.ndarray = np.array([0, 0, 0])
        self.center: np.ndarray = np.array([0, 0, 0])
        self.scale: float = 1.0
        self.vertex_count: int = 0
        self.face_count: int = 0


class ModelLoader:
    """3D模型加载器"""

    @staticmethod
    def load_model(file_path: str) -> Optional[ModelData]:
        """
        加载3D模型文件（支持FBX、OBJ等格式）

        Args:
            file_path: 模型文件路径

        Returns:
            ModelData对象，如果加载失败则返回None
        """
        try:
            # 使用pyassimp加载模型
            scene = pyassimp.load(file_path)

            if not scene.meshes:
                print(f"模型文件中没有网格数据: {file_path}")
                pyassimp.release(scene)
                return None

            # 收集所有网格的顶点和面
            all_vertices = []
            all_faces = []
            all_normals = []

            vertex_offset = 0

            for mesh in scene.meshes:
                # 获取顶点
                vertices = mesh.vertices
                all_vertices.append(vertices)

                # 获取面（三角形索引）
                faces = mesh.faces
                # 调整面的索引偏移
                for face in faces:
                    if len(face) >= 3:
                        # 只处理三角形（取前3个顶点）
                        adjusted_face = [idx + vertex_offset for idx in face[:3]]
                        all_faces.append(adjusted_face)

                # 获取法线
                if mesh.normals.any():
                    all_normals.append(mesh.normals)
                else:
                    # 如果没有法线，创建默认法线
                    default_normals = np.zeros_like(vertices)
                    default_normals[:, 2] = 1.0  # 默认指向Z轴
                    all_normals.append(default_normals)

                vertex_offset += len(vertices)

            # 合并所有数据
            model_data = ModelData()
            model_data.vertices = np.vstack(all_vertices)
            model_data.faces = np.array(all_faces, dtype=np.uint32)
            model_data.normals = np.vstack(all_normals)

            # 计算统计信息
            model_data.vertex_count = len(model_data.vertices)
            model_data.face_count = len(model_data.faces)

            # 计算边界框和中心点
            model_data.bounds_min = np.min(model_data.vertices, axis=0)
            model_data.bounds_max = np.max(model_data.vertices, axis=0)
            model_data.center = (model_data.bounds_min + model_data.bounds_max) / 2.0

            # 计算缩放比例（归一化到合适大小）
            bounds_size = model_data.bounds_max - model_data.bounds_min
            max_size = np.max(bounds_size)
            if max_size > 0:
                model_data.scale = 2.0 / max_size  # 归一化到2单位大小

            # 释放pyassimp资源
            pyassimp.release(scene)

            print(f"模型加载成功: {file_path}")
            print(f"  顶点数: {model_data.vertex_count}")
            print(f"  面数: {model_data.face_count}")

            return model_data

        except Exception as e:
            print(f"加载模型失败 {file_path}: {str(e)}")
            return None

    @staticmethod
    def get_model_info(file_path: str) -> Dict[str, any]:
        """
        获取模型文件信息（不完全加载模型）

        Args:
            file_path: 模型文件路径

        Returns:
            包含模型信息的字典
        """
        try:
            scene = pyassimp.load(file_path)

            total_vertices = 0
            total_faces = 0

            for mesh in scene.meshes:
                total_vertices += len(mesh.vertices)
                total_faces += len(mesh.faces)

            info = {
                'vertex_count': total_vertices,
                'face_count': total_faces,
                'mesh_count': len(scene.meshes),
                'has_materials': len(scene.materials) > 0,
                'has_textures': any(mat.properties.get(('file', 1)) for mat in scene.materials)
            }

            pyassimp.release(scene)
            return info

        except Exception as e:
            return {'error': str(e)}
