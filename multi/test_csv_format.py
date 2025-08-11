#!/usr/bin/env python
"""
测试CSV格式处理
"""

import os
import sys
import django
import pandas as pd
import numpy as np

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_csv_format():
    """测试CSV格式处理"""
    print("=" * 60)
    print("测试CSV格式处理")
    print("=" * 60)
    
    try:
        from polls.models import MonitorTask
        from polls.sensor_data_loader import SensorDataLoader
        
        # 1. 检查监控任务
        print("\n1. 检查监控任务...")
        tasks = MonitorTask.objects.all()
        print(f"找到 {tasks.count()} 个监控任务")
        
        for task in tasks[:3]:  # 只显示前3个
            print(f"  - {task.task_name} (ID: {task.task_id})")
            print(f"    CSV文件: {task.csv_file_path}")
            print(f"    启用通道: {task.enabled_channels}")
            
            # 检查CSV文件是否存在
            if os.path.exists(task.csv_file_path):
                print(f"    ✅ CSV文件存在")
                
                # 读取CSV文件头部
                try:
                    df = pd.read_csv(task.csv_file_path, nrows=5)
                    print(f"    CSV列名: {list(df.columns)}")
                    print(f"    CSV形状: {df.shape}")
                    
                    # 检查数据格式
                    if len(df.columns) > 1:
                        print(f"    数据示例:")
                        for i, col in enumerate(df.columns[:5]):  # 显示前5列
                            if i < len(df):
                                print(f"      {col}: {df[col].iloc[0]}")
                    
                except Exception as e:
                    print(f"    ❌ 读取CSV文件失败: {e}")
            else:
                print(f"    ❌ CSV文件不存在")
        
        # 2. 测试数据加载器
        print("\n2. 测试数据加载器...")
        loader = SensorDataLoader()
        
        # 测试通道映射
        print("通道映射:")
        for i in range(5):  # 显示前5个通道
            channel_name = f'CH{i}'
            if channel_name in loader.channel_mapping:
                print(f"  {channel_name}: {loader.channel_mapping[channel_name]}")
        
        # 3. 测试获取可用通道
        print("\n3. 测试获取可用通道...")
        if tasks.exists():
            task = tasks.first()
            available_channels = loader._get_available_channels(task.task_id)
            print(f"任务 '{task.task_name}' 的可用通道: {available_channels}")
        
        # 4. 测试数据加载
        print("\n4. 测试数据加载...")
        if tasks.exists():
            task = tasks.first()
            try:
                # 获取可用通道
                available_channels = loader._get_available_channels(task.task_id)
                if available_channels:
                    # 只使用前2个通道进行测试
                    test_channels = available_channels[:2]
                    print(f"测试通道: {test_channels}")
                    
                    # 加载数据
                    data, channel_names = loader.load_sensor_data(
                        task_ids=[task.task_id],
                        channels=test_channels
                    )
                    
                    print(f"数据加载成功:")
                    print(f"  数据形状: {data.shape}")
                    print(f"  通道名称: {channel_names}")
                    print(f"  数据范围:")
                    for i, channel in enumerate(channel_names):
                        if i < data.shape[0]:
                            channel_data = data[i, :]
                            print(f"    {channel}: [{channel_data.min():.3f}, {channel_data.max():.3f}]")
                
            except Exception as e:
                print(f"❌ 数据加载测试失败: {e}")
        
        print("\n" + "=" * 60)
        print("✅ CSV格式处理测试完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_csv():
    """创建示例CSV文件用于测试"""
    print("\n创建示例CSV文件...")
    
    # 创建示例数据
    time_points = np.linspace(0, 10, 1000)  # 10秒，1000个点
    data = {
        '时间': time_points,
        'CH0': 2 + 0.5 * np.sin(2 * np.pi * time_points) + 0.1 * np.random.randn(1000),
        'CH1': 1.5 + 0.3 * np.cos(2 * np.pi * time_points * 2) + 0.1 * np.random.randn(1000),
        'CH2': 3 + 0.2 * np.sin(2 * np.pi * time_points * 0.5) + 0.1 * np.random.randn(1000),
        'CH3': 1 + 0.4 * np.cos(2 * np.pi * time_points * 1.5) + 0.1 * np.random.randn(1000)
    }
    
    df = pd.DataFrame(data)
    
    # 保存到media目录
    media_dir = os.path.join(os.path.dirname(__file__), 'myproject', 'media', 'monitor_data')
    os.makedirs(media_dir, exist_ok=True)
    
    sample_file = os.path.join(media_dir, 'sample_test_data.csv')
    df.to_csv(sample_file, index=False)
    
    print(f"示例CSV文件已创建: {sample_file}")
    print(f"文件内容预览:")
    print(df.head())
    
    return sample_file

if __name__ == "__main__":
    # 运行测试
    test_csv_format()
    
    # 可选：创建示例CSV文件
    # create_sample_csv() 
"""
测试CSV格式处理
"""

import os
import sys
import django
import pandas as pd
import numpy as np

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_csv_format():
    """测试CSV格式处理"""
    print("=" * 60)
    print("测试CSV格式处理")
    print("=" * 60)
    
    try:
        from polls.models import MonitorTask
        from polls.sensor_data_loader import SensorDataLoader
        
        # 1. 检查监控任务
        print("\n1. 检查监控任务...")
        tasks = MonitorTask.objects.all()
        print(f"找到 {tasks.count()} 个监控任务")
        
        for task in tasks[:3]:  # 只显示前3个
            print(f"  - {task.task_name} (ID: {task.task_id})")
            print(f"    CSV文件: {task.csv_file_path}")
            print(f"    启用通道: {task.enabled_channels}")
            
            # 检查CSV文件是否存在
            if os.path.exists(task.csv_file_path):
                print(f"    ✅ CSV文件存在")
                
                # 读取CSV文件头部
                try:
                    df = pd.read_csv(task.csv_file_path, nrows=5)
                    print(f"    CSV列名: {list(df.columns)}")
                    print(f"    CSV形状: {df.shape}")
                    
                    # 检查数据格式
                    if len(df.columns) > 1:
                        print(f"    数据示例:")
                        for i, col in enumerate(df.columns[:5]):  # 显示前5列
                            if i < len(df):
                                print(f"      {col}: {df[col].iloc[0]}")
                    
                except Exception as e:
                    print(f"    ❌ 读取CSV文件失败: {e}")
            else:
                print(f"    ❌ CSV文件不存在")
        
        # 2. 测试数据加载器
        print("\n2. 测试数据加载器...")
        loader = SensorDataLoader()
        
        # 测试通道映射
        print("通道映射:")
        for i in range(5):  # 显示前5个通道
            channel_name = f'CH{i}'
            if channel_name in loader.channel_mapping:
                print(f"  {channel_name}: {loader.channel_mapping[channel_name]}")
        
        # 3. 测试获取可用通道
        print("\n3. 测试获取可用通道...")
        if tasks.exists():
            task = tasks.first()
            available_channels = loader._get_available_channels(task.task_id)
            print(f"任务 '{task.task_name}' 的可用通道: {available_channels}")
        
        # 4. 测试数据加载
        print("\n4. 测试数据加载...")
        if tasks.exists():
            task = tasks.first()
            try:
                # 获取可用通道
                available_channels = loader._get_available_channels(task.task_id)
                if available_channels:
                    # 只使用前2个通道进行测试
                    test_channels = available_channels[:2]
                    print(f"测试通道: {test_channels}")
                    
                    # 加载数据
                    data, channel_names = loader.load_sensor_data(
                        task_ids=[task.task_id],
                        channels=test_channels
                    )
                    
                    print(f"数据加载成功:")
                    print(f"  数据形状: {data.shape}")
                    print(f"  通道名称: {channel_names}")
                    print(f"  数据范围:")
                    for i, channel in enumerate(channel_names):
                        if i < data.shape[0]:
                            channel_data = data[i, :]
                            print(f"    {channel}: [{channel_data.min():.3f}, {channel_data.max():.3f}]")
                
            except Exception as e:
                print(f"❌ 数据加载测试失败: {e}")
        
        print("\n" + "=" * 60)
        print("✅ CSV格式处理测试完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_csv():
    """创建示例CSV文件用于测试"""
    print("\n创建示例CSV文件...")
    
    # 创建示例数据
    time_points = np.linspace(0, 10, 1000)  # 10秒，1000个点
    data = {
        '时间': time_points,
        'CH0': 2 + 0.5 * np.sin(2 * np.pi * time_points) + 0.1 * np.random.randn(1000),
        'CH1': 1.5 + 0.3 * np.cos(2 * np.pi * time_points * 2) + 0.1 * np.random.randn(1000),
        'CH2': 3 + 0.2 * np.sin(2 * np.pi * time_points * 0.5) + 0.1 * np.random.randn(1000),
        'CH3': 1 + 0.4 * np.cos(2 * np.pi * time_points * 1.5) + 0.1 * np.random.randn(1000)
    }
    
    df = pd.DataFrame(data)
    
    # 保存到media目录
    media_dir = os.path.join(os.path.dirname(__file__), 'myproject', 'media', 'monitor_data')
    os.makedirs(media_dir, exist_ok=True)
    
    sample_file = os.path.join(media_dir, 'sample_test_data.csv')
    df.to_csv(sample_file, index=False)
    
    print(f"示例CSV文件已创建: {sample_file}")
    print(f"文件内容预览:")
    print(df.head())
    
    return sample_file

if __name__ == "__main__":
    # 运行测试
    test_csv_format()
    
    # 可选：创建示例CSV文件
    # create_sample_csv() 
 
 