"""
3D模型加载器模块（改进版）
负责加载FBX等3D模型文件
"""
import os
import sys
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

    def __init__(self):
        """初始化加载器并检查pyassimp"""
        self.assimp_available = False
        self.pyassimp = None
        self.error_message = ""

        try:
            import pyassimp
            self.pyassimp = pyassimp
            self.assimp_available = True
            print("✅ PyAssimp 加载成功")
        except ImportError as e:
            self.error_message = f"PyAssimp 未安装: {str(e)}"
            print(f"❌ {self.error_message}")
        except Exception as e:
            self.error_message = f"PyAssimp 加载失败: {str(e)}"
            print(f"❌ {self.error_message}")

    def load_model(self, file_path: str) -> Optional[ModelData]:
        """
        加载3D模型文件（支持FBX、OBJ等格式）

        Args:
            file_path: 模型文件路径

        Returns:
            ModelData对象，如果加载失败则返回None
        """
        if not self.assimp_available:
            print(f"❌ 无法加载模型: PyAssimp不可用")
            print(f"错误信息: {self.error_message}")
            return None

        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return None

        try:
            print(f"\n开始加载模型: {file_path}")
            print(f"文件大小: {os.path.getsize(file_path)} bytes")

            # 使用pyassimp加载模型，添加更多的后处理选项
            scene = self.pyassimp.load(
                file_path,
                processing=self.pyassimp.postprocess.aiProcess_Triangulate |
                          self.pyassimp.postprocess.aiProcess_GenSmoothNormals |
                          self.pyassimp.postprocess.aiProcess_JoinIdenticalVertices
            )

            if not scene:
                print(f"❌ 加载失败: scene为空")
                return None

            if not scene.meshes or len(scene.meshes) == 0:
                print(f"❌ 模型文件中没有网格数据: {file_path}")
                self.pyassimp.release(scene)
                return None

            print(f"✅ 场景加载成功，包含 {len(scene.meshes)} 个网格")

            # 收集所有网格的顶点和面
            all_vertices = []
            all_faces = []
            all_normals = []

            vertex_offset = 0

            for i, mesh in enumerate(scene.meshes):
                print(f"  处理网格 {i+1}/{len(scene.meshes)}...")

                # 获取顶点
                vertices = np.array(mesh.vertices, dtype=np.float32)
                if len(vertices) == 0:
                    print(f"    ⚠️ 网格 {i+1} 没有顶点，跳过")
                    continue

                all_vertices.append(vertices)
                print(f"    顶点数: {len(vertices)}")

                # 获取面（三角形索引）
                faces = mesh.faces
                mesh_faces = []
                for face in faces:
                    if len(face) >= 3:
                        # 只处理三角形（取前3个顶点）
                        adjusted_face = [idx + vertex_offset for idx in face[:3]]
                        mesh_faces.append(adjusted_face)

                if len(mesh_faces) > 0:
                    all_faces.extend(mesh_faces)
                    print(f"    面数: {len(mesh_faces)}")

                # 获取法线
                if hasattr(mesh, 'normals') and mesh.normals is not None and len(mesh.normals) > 0:
                    normals = np.array(mesh.normals, dtype=np.float32)
                    all_normals.append(normals)
                    print(f"    法线数: {len(normals)}")
                else:
                    # 如果没有法线，创建默认法线
                    default_normals = np.zeros((len(vertices), 3), dtype=np.float32)
                    default_normals[:, 1] = 1.0  # 默认指向Y轴
                    all_normals.append(default_normals)
                    print(f"    使用默认法线")

                vertex_offset += len(vertices)

            # 检查是否有有效数据
            if len(all_vertices) == 0:
                print(f"❌ 没有提取到任何顶点数据")
                self.pyassimp.release(scene)
                return None

            if len(all_faces) == 0:
                print(f"❌ 没有提取到任何面数据")
                self.pyassimp.release(scene)
                return None

            # 合并所有数据
            model_data = ModelData()
            model_data.vertices = np.vstack(all_vertices).astype(np.float32)
            model_data.faces = np.array(all_faces, dtype=np.uint32)
            model_data.normals = np.vstack(all_normals).astype(np.float32)

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
            else:
                model_data.scale = 1.0

            # 释放pyassimp资源
            self.pyassimp.release(scene)

            print(f"\n✅ 模型加载成功!")
            print(f"  总顶点数: {model_data.vertex_count:,}")
            print(f"  总面数: {model_data.face_count:,}")

            return model_data

        except Exception as e:
            print(f"\n❌ 加载模型时发生异常: {file_path}")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def get_model_info(self, file_path: str) -> Dict[str, any]:
        """
        获取模型文件信息（不完全加载模型）

        Args:
            file_path: 模型文件路径

        Returns:
            包含模型信息的字典
        """
        if not self.assimp_available:
            return {'error': self.error_message}

        try:
            scene = self.pyassimp.load(file_path)

            total_vertices = 0
            total_faces = 0

            for mesh in scene.meshes:
                total_vertices += len(mesh.vertices)
                total_faces += len(mesh.faces)

            info = {
                'vertex_count': total_vertices,
                'face_count': total_faces,
                'mesh_count': len(scene.meshes),
                'has_materials': len(scene.materials) > 0 if hasattr(scene, 'materials') else False,
            }

            self.pyassimp.release(scene)
            return info

        except Exception as e:
            return {'error': str(e)}

    def is_supported_format(self, file_path: str) -> bool:
        """
        检查文件格式是否支持

        Args:
            file_path: 文件路径

        Returns:
            是否支持该格式
        """
        supported_extensions = [
            '.fbx', '.obj', '.dae', '.3ds', '.blend', '.stl',
            '.ply', '.gltf', '.glb', '.x', '.ase', '.ifc'
        ]

        ext = os.path.splitext(file_path)[1].lower()
        return ext in supported_extensions
