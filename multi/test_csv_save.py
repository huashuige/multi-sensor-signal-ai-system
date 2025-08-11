#!/usr/bin/env python3
"""
测试CSV保存功能的脚本
"""
import os
import sys
import django
import pandas as pd
import numpy as np
from datetime import datetime

# 添加项目路径
sys.path.append('D:/multi/multi')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_csv_save():
    """测试CSV保存功能"""
    
    # 模拟监控数据
    time_axis = np.linspace(0, 10, 1000)  # 10秒，1000个点
    enabled_channels = [0, 1, 2, 3]  # 启用4个通道
    
    # 生成模拟的通道数据
    channel_data = {}
    for ch in enabled_channels:
        # 生成不同频率的正弦波
        frequency = 1 + ch * 0.5  # 不同通道不同频率
        channel_data[ch] = np.sin(2 * np.pi * frequency * time_axis) + np.random.normal(0, 0.1, len(time_axis))
    
    # 创建CSV文件
    csv_dir = os.path.join('media', 'monitor_data')
    os.makedirs(csv_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"test_monitor_data_{timestamp}.csv"
    csv_path = os.path.join(csv_dir, filename)
    
    # 创建数据框
    df_data = {'Time(s)': time_axis}
    
    # 确保所有启用的通道都有数据列
    for ch in enabled_channels:
        if ch in channel_data:
            df_data[f'CH{ch}'] = channel_data[ch]
        else:
            # 如果某个启用的通道没有数据，用NaN填充
            df_data[f'CH{ch}'] = [float('nan')] * len(time_axis)
    
    print(f"保存CSV文件: {csv_path}")
    print(f"时间轴长度: {len(time_axis)}")
    print(f"启用通道: {enabled_channels}")
    print(f"数据列: {list(df_data.keys())}")
    
    df = pd.DataFrame(df_data)
    
    # 验证数据完整性
    print(f"DataFrame形状: {df.shape}")
    print(f"DataFrame列: {df.columns.tolist()}")
    
    df.to_csv(csv_path, index=False)
    
    # 验证保存的文件
    saved_df = pd.read_csv(csv_path)
    print(f"保存的CSV文件形状: {saved_df.shape}")
    print(f"保存的CSV文件列: {saved_df.columns.tolist()}")
    
    # 检查数据内容
    print("\n数据预览:")
    print(saved_df.head())
    
    print(f"\n✅ 测试完成！CSV文件已保存到: {csv_path}")
    print(f"文件大小: {os.path.getsize(csv_path)} 字节")

if __name__ == "__main__":
    test_csv_save() 