import os
import sys
import django
from datetime import datetime
import pandas as pd

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def register_simulated_data():
    """将模拟数据注册到数据库中"""
    
    # 查找最新的模拟数据文件
    data_dir = "multi/myproject/media/monitor_data"
    simulated_files = [f for f in os.listdir(data_dir) if f.startswith("simulated_data_")]
    
    if not simulated_files:
        print("❌ 没有找到模拟数据文件，请先运行 generate_simulated_data.py")
        return None
    
    # 获取最新的文件
    latest_file = max(simulated_files)
    file_path = os.path.join(data_dir, latest_file)
    
    print(f"📁 找到模拟数据文件: {latest_file}")
    
    # 读取文件信息
    df = pd.read_csv(file_path)
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    # 获取启用的通道
    enabled_channels = []
    for col in df.columns:
        if col.startswith('CH') and col[2:].isdigit():
            enabled_channels.append(int(col[2:]))
    
    # 创建MonitorTask记录
    task = MonitorTask.objects.create(
        task_id=f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        task_name="模拟数据 - 正弦波+PWM波",
        task_description="包含正弦波和PWM波的模拟传感器数据，用于深度学习训练测试",
        csv_file_path=file_path,
        sample_rate=10000,
        file_size_mb=file_size_mb,
        enabled_channels=enabled_channels,
        total_data_points=len(df)
    )
    
    print(f"✅ 模拟数据已注册到数据库")
    print(f"📊 任务ID: {task.task_id}")
    print(f"📊 任务名称: {task.task_name}")
    print(f"📊 文件路径: {task.csv_file_path}")
    print(f"📊 采样率: {task.sample_rate} Hz")
    print(f"📊 文件大小: {task.file_size_mb:.2f} MB")
    print(f"📊 启用通道: {task.enabled_channels}")
    print(f"📊 数据点数: {task.total_data_points}")
    
    return task

if __name__ == "__main__":
    task = register_simulated_data()
    if task:
        print(f"\n🎯 现在可以在训练界面中选择任务ID: {task.task_id}")
        print("💡 通道选择: CH0, CH1")
        print("💡 建议参数: 窗口大小=50, 预测步长=10") 
import sys
import django
from datetime import datetime
import pandas as pd

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def register_simulated_data():
    """将模拟数据注册到数据库中"""
    
    # 查找最新的模拟数据文件
    data_dir = "multi/myproject/media/monitor_data"
    simulated_files = [f for f in os.listdir(data_dir) if f.startswith("simulated_data_")]
    
    if not simulated_files:
        print("❌ 没有找到模拟数据文件，请先运行 generate_simulated_data.py")
        return None
    
    # 获取最新的文件
    latest_file = max(simulated_files)
    file_path = os.path.join(data_dir, latest_file)
    
    print(f"📁 找到模拟数据文件: {latest_file}")
    
    # 读取文件信息
    df = pd.read_csv(file_path)
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    # 获取启用的通道
    enabled_channels = []
    for col in df.columns:
        if col.startswith('CH') and col[2:].isdigit():
            enabled_channels.append(int(col[2:]))
    
    # 创建MonitorTask记录
    task = MonitorTask.objects.create(
        task_id=f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        task_name="模拟数据 - 正弦波+PWM波",
        task_description="包含正弦波和PWM波的模拟传感器数据，用于深度学习训练测试",
        csv_file_path=file_path,
        sample_rate=10000,
        file_size_mb=file_size_mb,
        enabled_channels=enabled_channels,
        total_data_points=len(df)
    )
    
    print(f"✅ 模拟数据已注册到数据库")
    print(f"📊 任务ID: {task.task_id}")
    print(f"📊 任务名称: {task.task_name}")
    print(f"📊 文件路径: {task.csv_file_path}")
    print(f"📊 采样率: {task.sample_rate} Hz")
    print(f"📊 文件大小: {task.file_size_mb:.2f} MB")
    print(f"📊 启用通道: {task.enabled_channels}")
    print(f"📊 数据点数: {task.total_data_points}")
    
    return task

if __name__ == "__main__":
    task = register_simulated_data()
    if task:
        print(f"\n🎯 现在可以在训练界面中选择任务ID: {task.task_id}")
        print("💡 通道选择: CH0, CH1")
        print("💡 建议参数: 窗口大小=50, 预测步长=10") 
 
 