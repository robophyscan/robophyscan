"""
提供贴图工作流需要的函数。
"""

import os
import shutil
import subprocess
from pathlib import Path


def env_check():
    """
    检查环境变量中是否包含RealityScan.exe的路径。若未找到，则提示用户输入路径设置环境变量。
    """
    env_check_bool = (
        shutil.which("RealityScan.exe") is not None
    )  # 检查环境变量中是否包含RealityScan.exe的路径

    if not env_check_bool:  # 未找到路径时提示设置路径
        print(
            "在环境变量中未找到RealityScan.exe，请输入RealityScan.exe所在的文件夹路径："
        )
        path = Path(input("请输入RealityScan.exe所在的文件夹路径："))

        if not path.is_dir():  # 判断路径是否为文件夹
            raise ValueError(f"{path} 路径不是有效的文件夹")
        exe_path = path / "RealityScan.exe"

        if not exe_path.is_file():  # 判断路径下是否存在RealityScan.exe文件
            raise ValueError(f"{exe_path} 文件不存在")

        os.environ["PATH"] += os.pathsep + str(path)

    else:
        print("RealityScan.exe已在环境变量中存在")


def run_exe():
    """
    运行RealityScan.exe。
    """
    return ["RealityScan.exe"]


def headless():
    """
    添加无头模式参数。
    """
    return ["-headless"]


def add_folder(input_photo_dir):
    """
    添加输入照片文件夹路径参数。
    :param input_photo_dir: 输入照片文件夹路径
    """
    return ["-addFolder", input_photo_dir]


def start():
    """
    添加开始生成贴图。
    """
    # return ["-start"]
    command = []
    # command += ["-generateAIMasks"]
    command += ["-align"]
    command += ["-setReconstructionRegionAuto"]
    command += ["-calculateNormalModel"]
    command += ["-simplify"]
    command += ["-cleanModel"]
    command += ["-unwrap"]
    command += ["-calculateTexture"]
    return command


def export_model(export_path, export_model):
    """
    添加导出模型参数。
    :param export_path: 导出路径
    :param export_model: 导出的模型名称
    """
    return ["-selectModel", export_model, "-exportSelectedModel", export_path]


def save_project(project_dir_path):
    """
    将项目文件夹保存到指定路径。
    :param project_dir_path: 项目保存路径
    """
    return ["-save", project_dir_path]


def save():
    """
    添加保存项目参数。
    """
    return ["-save"]


def quit_app():
    """
    添加完成后退出参数。
    """
    return ["-quit"]


def load_project(project_path):
    """
    加载项目文件。
    :param project_path: 项目文件路径
    """
    return ["-load", project_path]


def import_model(model_path):
    """
    导入模型文件。
    :param model_path: 模型文件路径
    """
    return ["-importModel", model_path]


def reproject_texture(source_mesh, target_mesh):
    """
    将源网格的贴图重投影到目标网格上。
    :param source_mesh: 源网格文件路径
    :param target_mesh: 目标网格文件路径
    """
    return ["-reprojectTexture", source_mesh, target_mesh]


def unwrap(model_name):
    """
    展开模型的UV。
    :param model_name: 模型名称
    """
    return ["-selectModel", model_name, "-unwrap"]


def generate_workflow(
    input_photo_dir,
    project_dir,
    headless_bool=True,
    quit_bool=True,
):
    """
    调用RealityScan.exe生成贴图。
    :param input_photo_dir: 输入照片文件夹路径
    :param project_dir: 项目保存路径
    :param headless_bool: 是否无头模式
    :param Aimask_bool: 是否使用AI遮罩
    :param quit_bool: 是否在完成后退出
    """
    command = []
    command += run_exe()
    command += headless() if headless_bool else []
    command += add_folder(input_photo_dir)
    command += start()
    command += save_project(project_dir)
    command += quit_app() if quit_bool else []
    subprocess.run(command, check=True)


def export_compare_mesh_workflow(
    project_dir,
    export_compare_mesh_dir,
    compare_mesh="compare_mesh",
    model_name="Model 3",
    headless_bool=True,
    quit_bool=True,
):
    """
    导出贴图用于比较网格。
    :param project_dir: 项目保存路径
    :param export_compare_mesh_dir: 比较网格贴图输出路径
    :param compare_mesh: 比较网格贴图文件名
    :param model_name: 选择导出的模型名称
    :param headless_bool: 是否无头模式
    :param quit_bool: 是否在完成后退出
    """
    command = []
    load_path = project_dir + ".rsproj"
    compare_model_path = export_compare_mesh_dir + "\\" + compare_mesh + ".obj"
    command += run_exe()
    command += headless() if headless_bool else []
    command += load_project(load_path)
    command += export_model(compare_model_path, model_name)
    command += save()
    command += quit_app() if quit_bool else []
    subprocess.run(command, check=True)


def reproject_texture_workflow(
    project_dir,
    to_be_reprojected_mesh_dir,
    reprojected_mesh_dir,
    to_be_reprojected_mesh="to_be_reprojected_mesh",
    reprojected_mesh="reprojected_mesh",
    reprojection_model="Model 3",
    to_be_reprojected_model="Model 4",
    headless_bool=True,
    quit_bool=True,
):
    """
    导出贴图用于比较网格。
    :param project_dir: 项目保存路径
    :param to_be_reprojected_mesh_dir: 待重投影网格所在
    :param reprojected_mesh_dir: 重投影网格输出路径
    :param to_be_reprojected_mesh: 待重投影网格文件名
    :param reprojected_mesh: 重投影网格文件名
    :param reprojection_model: 用于重投影的模型名称
    :param to_be_reprojected_model: 待重投影的模型名称
    :param headless_bool: 是否无头模式
    :param quit_bool: 是否在完成后退出
    """
    command = []
    load_path = project_dir + ".rsproj"
    to_be_reprojected_model_path = (
        to_be_reprojected_mesh_dir + "\\" + to_be_reprojected_mesh + ".obj"
    )
    reprojected_mesh_path = reprojected_mesh_dir + "\\" + reprojected_mesh + ".obj"
    command += run_exe()
    command += headless() if headless_bool else []
    command += load_project(load_path)
    command += import_model(to_be_reprojected_model_path)
    command += unwrap(to_be_reprojected_model)
    command += reproject_texture(reprojection_model, to_be_reprojected_model)
    command += export_model(reprojected_mesh_path, to_be_reprojected_model)
    command += save()
    command += quit_app() if quit_bool else []
    subprocess.run(command, check=True)


if __name__ == "__main__":
    pass
