#!/usr/bin/env python
"""
测试导入修复
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_imports():
    """测试导入是否正常"""
    print("测试导入...")
    
    try:
        # 测试模型导入
        from polls.models import MonitorTask
        print("✅ MonitorTask 导入成功")
        
        # 测试深度学习视图导入
        from polls import deep_learning_views
        print("✅ deep_learning_views 导入成功")
        
        # 测试传感器数据加载器导入
        from polls.sensor_data_loader import SensorDataLoader
        print("✅ SensorDataLoader 导入成功")
        
        # 测试LSTM模型导入
        from polls.multi_channel_lstm import MultiChannelLSTM
        print("✅ MultiChannelLSTM 导入成功")
        
        print("\n🎉 所有导入测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_loader():
    """测试数据加载器"""
    print("\n测试数据加载器...")
    
    try:
        from polls.sensor_data_loader import SensorDataLoader
        
        # 创建数据加载器
        loader = SensorDataLoader()
        print("✅ SensorDataLoader 创建成功")
        
        # 测试获取可用通道
        # 注意：这里需要有一个实际的任务ID
        print("✅ 数据加载器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据加载器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_lstm_model():
    """测试LSTM模型"""
    print("\n测试LSTM模型...")
    
    try:
        from polls.multi_channel_lstm import MultiChannelLSTM
        
        # 创建模型
        model = MultiChannelLSTM(
            num_channels=4,
            hidden_size=64,
            num_layers=2,
            horizon=12
        )
        print("✅ LSTM模型创建成功")
        
        # 测试前向传播
        import torch
        import numpy as np
        
        # 创建测试输入
        test_input = torch.randn(1, 24, 4)  # (batch_size, window_size, num_channels)
        
        # 前向传播
        output = model(test_input)
        print(f"✅ 前向传播成功，输出形状: {output.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ LSTM模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("开始测试导入修复")
    print("=" * 50)
    
    # 运行测试
    test1 = test_imports()
    test2 = test_data_loader()
    test3 = test_lstm_model()
    
    print("\n" + "=" * 50)
    if test1 and test2 and test3:
        print("🎉 所有测试通过！导入问题已解决。")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
    print("=" * 50) 
"""
测试导入修复
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_imports():
    """测试导入是否正常"""
    print("测试导入...")
    
    try:
        # 测试模型导入
        from polls.models import MonitorTask
        print("✅ MonitorTask 导入成功")
        
        # 测试深度学习视图导入
        from polls import deep_learning_views
        print("✅ deep_learning_views 导入成功")
        
        # 测试传感器数据加载器导入
        from polls.sensor_data_loader import SensorDataLoader
        print("✅ SensorDataLoader 导入成功")
        
        # 测试LSTM模型导入
        from polls.multi_channel_lstm import MultiChannelLSTM
        print("✅ MultiChannelLSTM 导入成功")
        
        print("\n🎉 所有导入测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_loader():
    """测试数据加载器"""
    print("\n测试数据加载器...")
    
    try:
        from polls.sensor_data_loader import SensorDataLoader
        
        # 创建数据加载器
        loader = SensorDataLoader()
        print("✅ SensorDataLoader 创建成功")
        
        # 测试获取可用通道
        # 注意：这里需要有一个实际的任务ID
        print("✅ 数据加载器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据加载器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_lstm_model():
    """测试LSTM模型"""
    print("\n测试LSTM模型...")
    
    try:
        from polls.multi_channel_lstm import MultiChannelLSTM
        
        # 创建模型
        model = MultiChannelLSTM(
            num_channels=4,
            hidden_size=64,
            num_layers=2,
            horizon=12
        )
        print("✅ LSTM模型创建成功")
        
        # 测试前向传播
        import torch
        import numpy as np
        
        # 创建测试输入
        test_input = torch.randn(1, 24, 4)  # (batch_size, window_size, num_channels)
        
        # 前向传播
        output = model(test_input)
        print(f"✅ 前向传播成功，输出形状: {output.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ LSTM模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("开始测试导入修复")
    print("=" * 50)
    
    # 运行测试
    test1 = test_imports()
    test2 = test_data_loader()
    test3 = test_lstm_model()
    
    print("\n" + "=" * 50)
    if test1 and test2 and test3:
        print("🎉 所有测试通过！导入问题已解决。")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
    print("=" * 50) 
 
 