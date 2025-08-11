import numpy as np
import pandas as pd
import os
import sys
import django
from datetime import datetime

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def generate_simulated_data():
    """生成模拟的传感器数据"""
    
    # 参数设置
    sample_rate = 10000  # 采样率 10kHz
    duration = 2.0  # 持续时间 2秒
    num_samples = int(sample_rate * duration)
    
    # 时间轴
    time = np.linspace(0, duration, num_samples)
    
    # 通道1: 正弦波 + 噪声
    frequency = 5.0  # 5Hz正弦波
    amplitude = 2.0
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * time)
    noise_level = 0.1
    noise = np.random.normal(0, noise_level, num_samples)
    ch0_data = sine_wave + noise
    
    # 通道2: PWM波 + 噪声
    pwm_frequency = 10.0  # 10Hz PWM
    duty_cycle = 0.3  # 30%占空比
    
    # 生成PWM波
    pwm_period = 1.0 / pwm_frequency
    samples_per_period = int(sample_rate / pwm_frequency)
    
    pwm_wave = np.zeros(num_samples)
    for i in range(0, num_samples, samples_per_period):
        # 计算当前周期内的样本数
        period_samples = min(samples_per_period, num_samples - i)
        high_samples = int(period_samples * duty_cycle)
        
        # 设置高电平和低电平
        pwm_wave[i:i+high_samples] = 3.0  # 高电平
        pwm_wave[i+high_samples:i+period_samples] = 0.0  # 低电平
    
    # 添加噪声
    pwm_noise = np.random.normal(0, 0.05, num_samples)
    ch1_data = pwm_wave + pwm_noise
    
    # 创建DataFrame
    df = pd.DataFrame({
        'Time(s)': time,
        'CH0': ch0_data,
        'CH1': ch1_data
    })
    
    return df

def create_and_register_simulated_data():
    """生成模拟数据并注册到数据库"""
    
    print("🚀 开始生成模拟数据...")
    
    # 生成数据
    df = generate_simulated_data()
    
    # 创建保存目录
    save_dir = "multi/myproject/media/monitor_data"
    os.makedirs(save_dir, exist_ok=True)
    
    # 生成文件名和任务ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"simulated_data_{timestamp}.csv"
    filepath = os.path.join(save_dir, filename)
    task_id = f"sim_{timestamp}"
    
    # 保存数据
    df.to_csv(filepath, index=False)
    
    print(f"✅ 模拟数据已保存到: {filepath}")
    print(f"📊 数据形状: {df.shape}")
    print(f"📈 通道0 (正弦波): 范围=[{df['CH0'].min():.3f}, {df['CH0'].max():.3f}], 均值={df['CH0'].mean():.3f}")
    print(f"📈 通道1 (PWM波): 范围=[{df['CH1'].min():.3f}, {df['CH1'].max():.3f}], 均值={df['CH1'].mean():.3f}")
    
    # 获取文件信息
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    
    # 获取启用的通道
    enabled_channels = []
    for col in df.columns:
        if col.startswith('CH') and col[2:].isdigit():
            enabled_channels.append(int(col[2:]))
    
    # 创建MonitorTask记录
    task = MonitorTask.objects.create(
        task_id=task_id,
        task_name="模拟数据 - 正弦波+PWM波",
        task_description="包含正弦波和PWM波的模拟传感器数据，用于深度学习训练测试",
        csv_file_path=filepath,
        sample_rate=10000,
        data_file_size=int(file_size_mb * 1024 * 1024),  # 转换为字节
        enabled_channels=enabled_channels,
        total_data_points=len(df),
        # 添加必需的字段
        start_time=datetime.now(),
        end_time=datetime.now(),
        interval_seconds=1,
        total_duration_minutes=1,
        points_per_acquisition=1000,
        channel_configs={},
        total_acquisitions=1,
        user_email="test@example.com",
        user_name="测试用户",
        is_completed=True  # 标记为已完成，这样才能在深度学习模块中显示
    )
    
    print(f"\n✅ 模拟数据已注册到数据库")
    print(f"📊 任务ID: {task.task_id}")
    print(f"📊 任务名称: {task.task_name}")
    print(f"📊 文件路径: {task.csv_file_path}")
    print(f"📊 采样率: {task.sample_rate} Hz")
    print(f"📊 文件大小: {task.file_size_mb:.2f} MB")
    print(f"📊 启用通道: {task.enabled_channels}")
    print(f"📊 数据点数: {task.total_data_points}")
    
    return task

if __name__ == "__main__":
    task = create_and_register_simulated_data()
    if task:
        print(f"\n🎯 现在可以在训练界面中选择任务ID: {task.task_id}")
        print("💡 通道选择: CH0, CH1")
        print("💡 建议参数: 窗口大小=50, 预测步长=10")
        print("💡 数据特征:")
        print("   - 通道0: 5Hz正弦波 + 噪声")
        print("   - 通道1: 10Hz PWM波 (30%占空比) + 噪声") 
import pandas as pd
import os
import sys
import django
from datetime import datetime

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def generate_simulated_data():
    """生成模拟的传感器数据"""
    
    # 参数设置
    sample_rate = 10000  # 采样率 10kHz
    duration = 2.0  # 持续时间 2秒
    num_samples = int(sample_rate * duration)
    
    # 时间轴
    time = np.linspace(0, duration, num_samples)
    
    # 通道1: 正弦波 + 噪声
    frequency = 5.0  # 5Hz正弦波
    amplitude = 2.0
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * time)
    noise_level = 0.1
    noise = np.random.normal(0, noise_level, num_samples)
    ch0_data = sine_wave + noise
    
    # 通道2: PWM波 + 噪声
    pwm_frequency = 10.0  # 10Hz PWM
    duty_cycle = 0.3  # 30%占空比
    
    # 生成PWM波
    pwm_period = 1.0 / pwm_frequency
    samples_per_period = int(sample_rate / pwm_frequency)
    
    pwm_wave = np.zeros(num_samples)
    for i in range(0, num_samples, samples_per_period):
        # 计算当前周期内的样本数
        period_samples = min(samples_per_period, num_samples - i)
        high_samples = int(period_samples * duty_cycle)
        
        # 设置高电平和低电平
        pwm_wave[i:i+high_samples] = 3.0  # 高电平
        pwm_wave[i+high_samples:i+period_samples] = 0.0  # 低电平
    
    # 添加噪声
    pwm_noise = np.random.normal(0, 0.05, num_samples)
    ch1_data = pwm_wave + pwm_noise
    
    # 创建DataFrame
    df = pd.DataFrame({
        'Time(s)': time,
        'CH0': ch0_data,
        'CH1': ch1_data
    })
    
    return df

def create_and_register_simulated_data():
    """生成模拟数据并注册到数据库"""
    
    print("🚀 开始生成模拟数据...")
    
    # 生成数据
    df = generate_simulated_data()
    
    # 创建保存目录
    save_dir = "multi/myproject/media/monitor_data"
    os.makedirs(save_dir, exist_ok=True)
    
    # 生成文件名和任务ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"simulated_data_{timestamp}.csv"
    filepath = os.path.join(save_dir, filename)
    task_id = f"sim_{timestamp}"
    
    # 保存数据
    df.to_csv(filepath, index=False)
    
    print(f"✅ 模拟数据已保存到: {filepath}")
    print(f"📊 数据形状: {df.shape}")
    print(f"📈 通道0 (正弦波): 范围=[{df['CH0'].min():.3f}, {df['CH0'].max():.3f}], 均值={df['CH0'].mean():.3f}")
    print(f"📈 通道1 (PWM波): 范围=[{df['CH1'].min():.3f}, {df['CH1'].max():.3f}], 均值={df['CH1'].mean():.3f}")
    
    # 获取文件信息
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    
    # 获取启用的通道
    enabled_channels = []
    for col in df.columns:
        if col.startswith('CH') and col[2:].isdigit():
            enabled_channels.append(int(col[2:]))
    
    # 创建MonitorTask记录
    task = MonitorTask.objects.create(
        task_id=task_id,
        task_name="模拟数据 - 正弦波+PWM波",
        task_description="包含正弦波和PWM波的模拟传感器数据，用于深度学习训练测试",
        csv_file_path=filepath,
        sample_rate=10000,
        data_file_size=int(file_size_mb * 1024 * 1024),  # 转换为字节
        enabled_channels=enabled_channels,
        total_data_points=len(df),
        # 添加必需的字段
        start_time=datetime.now(),
        end_time=datetime.now(),
        interval_seconds=1,
        total_duration_minutes=1,
        points_per_acquisition=1000,
        channel_configs={},
        total_acquisitions=1,
        user_email="test@example.com",
        user_name="测试用户",
        is_completed=True  # 标记为已完成，这样才能在深度学习模块中显示
    )
    
    print(f"\n✅ 模拟数据已注册到数据库")
    print(f"📊 任务ID: {task.task_id}")
    print(f"📊 任务名称: {task.task_name}")
    print(f"📊 文件路径: {task.csv_file_path}")
    print(f"📊 采样率: {task.sample_rate} Hz")
    print(f"📊 文件大小: {task.file_size_mb:.2f} MB")
    print(f"📊 启用通道: {task.enabled_channels}")
    print(f"📊 数据点数: {task.total_data_points}")
    
    return task

if __name__ == "__main__":
    task = create_and_register_simulated_data()
    if task:
        print(f"\n🎯 现在可以在训练界面中选择任务ID: {task.task_id}")
        print("💡 通道选择: CH0, CH1")
        print("💡 建议参数: 窗口大小=50, 预测步长=10")
        print("💡 数据特征:")
        print("   - 通道0: 5Hz正弦波 + 噪声")
        print("   - 通道1: 10Hz PWM波 (30%占空比) + 噪声") 
 
 