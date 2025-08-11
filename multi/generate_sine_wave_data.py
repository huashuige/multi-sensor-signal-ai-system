import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta

def generate_sine_wave_data():
    """生成单通道正弦波模拟数据"""
    
    # 参数设置
    num_points = 20000
    sampling_rate = 100  # 采样率 100Hz
    duration = num_points / sampling_rate  # 200秒
    
    # 时间轴
    time = np.linspace(0, duration, num_points)
    
    # 生成正弦波
    frequency = 2  # 2Hz的正弦波
    amplitude = 5.0  # 振幅5
    offset = 10.0   # 偏移量10
    
    # 基础正弦波
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * time) + offset
    
    # 添加一些噪声使其更真实
    noise = np.random.normal(0, 0.1, num_points)
    signal = sine_wave + noise
    
    # 创建时间戳
    start_time = datetime.now()
    timestamps = [start_time + timedelta(seconds=i/sampling_rate) for i in range(num_points)]
    
    # 创建DataFrame
    df = pd.DataFrame({
        'Timestamp': timestamps,
        'CH0': signal  # 单通道数据
    })
    
    # 确保输出目录存在
    output_dir = 'multi/media/monitor_data'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'sine_wave_single_channel_{timestamp_str}.csv'
    filepath = os.path.join(output_dir, filename)
    
    # 保存数据
    df.to_csv(filepath, index=False)
    
    print(f"✅ 正弦波数据生成完成！")
    print(f"📁 文件路径: {filepath}")
    print(f"📊 数据点数量: {num_points}")
    print(f"📊 通道数: 1 (CH0)")
    print(f"📊 采样率: {sampling_rate}Hz")
    print(f"📊 信号频率: {frequency}Hz")
    print(f"📊 振幅: {amplitude}")
    print(f"📊 偏移量: {offset}")
    print(f"📊 数据范围: [{signal.min():.3f}, {signal.max():.3f}]")
    print(f"📊 均值: {signal.mean():.3f}")
    print(f"📊 标准差: {signal.std():.3f}")
    
    return filepath

if __name__ == "__main__":
    generate_sine_wave_data() 