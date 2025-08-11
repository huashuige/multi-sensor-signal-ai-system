#!/usr/bin/env python3
"""
测试数据累积功能的脚本
"""
import os
import sys
import django
import numpy as np
from datetime import datetime

# 添加项目路径
sys.path.append('D:/multi/multi')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_data_accumulation():
    """测试数据累积功能"""
    
    # 模拟数据累积过程
    all_time_axis = []
    all_channel_data = {}
    enabled_channels = [0, 1, 2]
    
    print("开始测试数据累积功能...")
    
    # 模拟多次采集
    for acquisition in range(3):
        print(f"\n=== 第{acquisition + 1}次采集 ===")
        
        # 生成时间轴
        time_step = 1.0 / 10000  # 10kHz采样率
        start_idx = len(all_time_axis)
        points_per_channel = 1000
        end_idx = start_idx + points_per_channel
        time_axis = [i * time_step for i in range(start_idx, end_idx)]
        
        # 生成通道数据
        channel_data = {}
        for ch in enabled_channels:
            # 生成不同频率的正弦波
            frequency = 1 + ch * 0.5
            channel_data[ch] = np.sin(2 * np.pi * frequency * np.array(time_axis)) + np.random.normal(0, 0.1, len(time_axis))
        
        # 累积数据
        all_time_axis.extend(time_axis)
        
        # 确保所有启用的通道都有数据存储
        for ch in enabled_channels:
            if ch not in all_channel_data:
                all_channel_data[ch] = []
            
            # 如果当前数据包中有这个通道的数据，则添加
            if ch in channel_data and len(channel_data[ch]) > 0:
                all_channel_data[ch].extend(channel_data[ch])
                print(f"  累积CH{ch}数据: {len(channel_data[ch])}个点")
            else:
                # 如果没有数据，用NaN填充
                all_channel_data[ch].extend([float('nan')] * len(time_axis))
                print(f"  CH{ch}无数据，用NaN填充: {len(time_axis)}个点")
        
        print(f"  时间轴累积: {len(all_time_axis)}点")
        print(f"  通道数据: {list(all_channel_data.keys())}")
    
    # 验证最终结果
    print(f"\n=== 最终累积结果 ===")
    print(f"时间轴总长度: {len(all_time_axis)}")
    print(f"启用的通道: {enabled_channels}")
    
    for ch in enabled_channels:
        if ch in all_channel_data:
            data_length = len(all_channel_data[ch])
            print(f"CH{ch} 数据长度: {data_length}")
            if data_length > 0:
                print(f"  CH{ch} 前5个值: {all_channel_data[ch][:5]}")
                print(f"  CH{ch} 后5个值: {all_channel_data[ch][-5:]}")
        else:
            print(f"CH{ch} 没有数据")
    
    # 检查数据一致性
    expected_length = 3 * 1000  # 3次采集 * 1000点
    print(f"\n=== 数据一致性检查 ===")
    print(f"期望时间轴长度: {expected_length}")
    print(f"实际时间轴长度: {len(all_time_axis)}")
    print(f"时间轴长度一致: {len(all_time_axis) == expected_length}")
    
    for ch in enabled_channels:
        if ch in all_channel_data:
            ch_length = len(all_channel_data[ch])
            print(f"CH{ch} 数据长度一致: {ch_length == expected_length}")
    
    print("\n✅ 数据累积测试完成！")

if __name__ == "__main__":
    test_data_accumulation() 