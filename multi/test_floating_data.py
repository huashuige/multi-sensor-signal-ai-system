#!/usr/bin/env python3
"""
测试悬空状态数据采集的脚本
"""
import os
import sys
import django
import numpy as np
import pandas as pd
from datetime import datetime

# 添加项目路径
sys.path.append('D:/multi/multi')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_floating_data():
    """测试悬空状态数据采集"""
    
    print("开始测试悬空状态数据采集...")
    
    # 模拟悬空状态的数据（固定值约10.xxxV）
    time_axis = np.linspace(0, 10, 1000)  # 10秒，1000个点
    enabled_channels = [0, 1, 2, 3]
    
    # 生成悬空状态的数据（固定值 + 微小噪声）
    channel_data = {}
    for ch in enabled_channels:
        # 悬空状态通常是接近电源电压的固定值
        base_voltage = 10.0 + ch * 0.1  # 不同通道略有不同
        noise = np.random.normal(0, 0.001, len(time_axis))  # 微小噪声
        channel_data[ch] = base_voltage + noise
    
    # 创建CSV文件
    csv_dir = os.path.join('media', 'monitor_data')
    os.makedirs(csv_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"floating_test_{timestamp}.csv"
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
    
    print(f"保存悬空测试CSV文件: {csv_path}")
    print(f"时间轴长度: {len(time_axis)}")
    print(f"启用通道: {enabled_channels}")
    print(f"数据列: {list(df_data.keys())}")
    
    df = pd.DataFrame(df_data)
    
    # 验证数据完整性
    print(f"DataFrame形状: {df.shape}")
    print(f"DataFrame列: {df.columns.tolist()}")
    
    # 检查每个通道的数据
    for ch in enabled_channels:
        col_name = f'CH{ch}'
        if col_name in df.columns:
            data = df[col_name].dropna()
            if len(data) > 0:
                print(f"{col_name}: {len(data)}个有效数据点, 范围: {data.min():.4f}~{data.max():.4f}")
                print(f"  {col_name} 前5个值: {data.head().tolist()}")
            else:
                print(f"{col_name}: 无有效数据")
        else:
            print(f"{col_name}: 列不存在")
    
    df.to_csv(csv_path, index=False)
    
    # 验证保存的文件
    saved_df = pd.read_csv(csv_path)
    print(f"\n保存的CSV文件形状: {saved_df.shape}")
    print(f"保存的CSV文件列: {saved_df.columns.tolist()}")
    
    # 检查数据内容
    print("\n数据预览:")
    print(saved_df.head())
    
    print(f"\n✅ 悬空状态测试完成！CSV文件已保存到: {csv_path}")
    print(f"文件大小: {os.path.getsize(csv_path)} 字节")
    
    # 验证悬空状态特征
    print("\n=== 悬空状态特征验证 ===")
    for ch in enabled_channels:
        col_name = f'CH{ch}'
        if col_name in saved_df.columns:
            data = saved_df[col_name].dropna()
            if len(data) > 0:
                mean_val = data.mean()
                std_val = data.std()
                print(f"{col_name}: 平均值={mean_val:.4f}V, 标准差={std_val:.6f}V")
                print(f"  特征: 固定值约{mean_val:.1f}V, 微小波动")
            else:
                print(f"{col_name}: 无有效数据")

if __name__ == "__main__":
    test_floating_data() 