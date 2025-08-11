import os
import sys
import django
import pandas as pd
from datetime import datetime

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def import_sine_data_to_db():
    """将正弦波数据信息导入到数据库"""
    
    # 数据文件路径
    data_file = 'multi/media/monitor_data/sine_wave_single_channel_20250731_152559.csv'
    
    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        return
    
    print(f"📁 正在读取数据文件: {data_file}")
    
    # 读取CSV文件
    df = pd.read_csv(data_file)
    print(f"✅ 数据读取成功，共 {len(df)} 行数据")
    
    # 解析时间范围
    timestamps = pd.to_datetime(df['Timestamp'])
    start_time = timestamps.min()
    end_time = timestamps.max()
    duration_minutes = (end_time - start_time).total_seconds() / 60
    
    # 计算采样率（基于时间间隔）
    time_diffs = timestamps.diff().dropna()
    avg_interval = time_diffs.mean().total_seconds()
    sample_rate = int(1 / avg_interval) if avg_interval > 0 else 100
    
    # 创建监控任务
    task_name = "正弦波单通道测试数据"
    task_description = "单通道正弦波模拟数据，用于深度学习训练测试。包含20000个数据点，采样率100Hz，信号频率2Hz。"
    
    # 检查是否已存在相同名称的任务
    existing_task = MonitorTask.objects.filter(task_name=task_name).first()
    if existing_task:
        print(f"⚠️  任务 '{task_name}' 已存在，使用现有任务")
        task = existing_task
    else:
        # 创建新的监控任务
        task = MonitorTask.objects.create(
            task_name=task_name,
            task_description=task_description,
            start_time=start_time,
            end_time=end_time,
            interval_seconds=1,  # 1秒间隔
            total_duration_minutes=int(duration_minutes),
            sample_rate=sample_rate,
            points_per_acquisition=1,
            enabled_channels=['CH0'],  # 只启用CH0通道
            channel_configs={
                'CH0': {
                    'enabled': True,
                    'range': '±10V',
                    'sample_rate': sample_rate
                }
            },
            csv_file_path=data_file,
            data_file_size=os.path.getsize(data_file),
            total_acquisitions=len(df),
            total_data_points=len(df),
            user_email='test@example.com',
            user_name='测试用户',
            is_completed=True,
            is_deleted=False
        )
        print(f"✅ 创建监控任务: {task.task_id}")
    
    print(f"✅ 数据导入完成！")
    print(f"📊 任务ID: {task.task_id}")
    print(f"📊 任务名称: {task.task_name}")
    print(f"📊 总数据条数: {len(df)}")
    print(f"📊 数据时间范围: {start_time} 到 {end_time}")
    print(f"📊 总时长: {duration_minutes:.2f} 分钟")
    print(f"📊 采样率: {sample_rate}Hz")
    print(f"📊 数据范围: [{df['CH0'].min():.3f}, {df['CH0'].max():.3f}]")
    print(f"📊 数据均值: {df['CH0'].mean():.3f}")
    print(f"📊 数据标准差: {df['CH0'].std():.3f}")
    print(f"📊 启用通道: {task.enabled_channels}")
    
    return task.task_id

if __name__ == "__main__":
    import_sine_data_to_db() 