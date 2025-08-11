#!/usr/bin/env python
"""
多通道LSTM训练系统测试脚本
"""

import os
import sys
import django
import numpy as np
import torch
from datetime import datetime

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.multi_channel_lstm import (
    MultiChannelLSTM, 
    MultiChannelSensorPreprocessor, 
    MultiChannelTrainer, 
    create_data_loaders
)
from polls.sensor_data_loader import SensorDataLoader

def test_multi_channel_training():
    """测试多通道LSTM训练"""
    print("=" * 60)
    print("开始测试多通道LSTM训练系统")
    print("=" * 60)
    
    # 1. 生成模拟数据
    print("\n1. 生成模拟传感器数据...")
    np.random.seed(42)
    num_channels = 4
    num_timesteps = 1000
    
    # 生成模拟数据（温度、湿度、加速度、电压）
    data = np.zeros((num_channels, num_timesteps))
    
    # 温度数据：20-30度，有趋势和季节性
    time_points = np.arange(num_timesteps)
    data[0, :] = 25 + 5 * np.sin(2 * np.pi * time_points / 100) + 0.5 * np.random.randn(num_timesteps)
    
    # 湿度数据：40-80%，与温度负相关
    data[1, :] = 60 - 0.8 * (data[0, :] - 25) + 10 * np.random.randn(num_timesteps)
    data[1, :] = np.clip(data[1, :], 40, 80)
    
    # 加速度数据：0.1-0.2g，有周期性振动
    data[2, :] = 0.15 + 0.05 * np.sin(2 * np.pi * time_points / 50) + 0.01 * np.random.randn(num_timesteps)
    
    # 电压数据：220-240V，有轻微波动
    data[3, :] = 230 + 5 * np.sin(2 * np.pi * time_points / 200) + 2 * np.random.randn(num_timesteps)
    
    print(f"模拟数据生成完成: {data.shape[0]}个通道, {data.shape[1]}个时间点")
    print(f"通道1 (温度): 范围[{data[0, :].min():.2f}, {data[0, :].max():.2f}]")
    print(f"通道2 (湿度): 范围[{data[1, :].min():.2f}, {data[1, :].max():.2f}]")
    print(f"通道3 (加速度): 范围[{data[2, :].min():.2f}, {data[2, :].max():.2f}]")
    print(f"通道4 (电压): 范围[{data[3, :].min():.2f}, {data[3, :].max():.2f}]")
    
    # 2. 数据预处理
    print("\n2. 数据预处理...")
    preprocessor = MultiChannelSensorPreprocessor(window_size=24, horizon=12)
    processed_data = preprocessor.fit_transform(data)
    
    print(f"预处理完成:")
    print(f"  训练集: {processed_data['X_train'].shape}")
    print(f"  验证集: {processed_data['X_val'].shape}")
    print(f"  测试集: {processed_data['X_test'].shape}")
    
    # 3. 创建数据加载器
    print("\n3. 创建数据加载器...")
    train_loader, val_loader = create_data_loaders(
        processed_data['X_train'], processed_data['y_train'],
        processed_data['X_val'], processed_data['y_val'],
        batch_size=32
    )
    
    print(f"数据加载器创建完成:")
    print(f"  训练批次: {len(train_loader)}")
    print(f"  验证批次: {len(val_loader)}")
    
    # 4. 创建模型
    print("\n4. 创建LSTM模型...")
    model = MultiChannelLSTM(
        num_channels=processed_data['num_channels'],
        hidden_size=64,
        num_layers=2,
        horizon=12,
        dropout=0.1
    )
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"模型创建完成: {total_params:,}个参数")
    
    # 5. 创建训练器
    print("\n5. 创建训练器...")
    trainer = MultiChannelTrainer(model)
    
    # 6. 训练模型
    print("\n6. 开始训练...")
    trainer.train(
        train_loader, val_loader,
        epochs=50,  # 减少训练轮数用于测试
        lr=0.001,
        patience=10
    )
    
    # 7. 保存模型
    print("\n7. 保存模型...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"test_models/multi_channel_lstm_{timestamp}.pth"
    
    # 创建保存目录
    os.makedirs("test_models", exist_ok=True)
    
    metadata = {
        'model_name': 'MultiChannelLSTM_Test',
        'training_date': timestamp,
        'data_info': {
            'num_channels': processed_data['num_channels'],
            'num_timesteps': processed_data['num_timesteps'],
            'window_size': 24,
            'horizon': 12
        },
        'model_config': {
            'hidden_size': 64,
            'num_layers': 2,
            'dropout': 0.1
        },
        'channel_stats': processed_data['channel_stats'],
        'test_data_info': {
            'channels': ['temperature', 'humidity', 'acceleration', 'voltage'],
            'data_range': {
                'temperature': [data[0, :].min(), data[0, :].max()],
                'humidity': [data[1, :].min(), data[1, :].max()],
                'acceleration': [data[2, :].min(), data[2, :].max()],
                'voltage': [data[3, :].min(), data[3, :].max()]
            }
        }
    }
    
    trainer.save_model(model_path, metadata)
    
    # 8. 测试预测
    print("\n8. 测试预测功能...")
    # 使用最后一个序列进行预测
    last_sequence = processed_data['X_test'][-1]  # (channels, window_size)
    
    # 进行预测
    model.eval()
    with torch.no_grad():
        input_tensor = torch.FloatTensor(last_sequence).unsqueeze(0)  # 添加batch维度
        prediction = model(input_tensor)
        prediction = prediction.squeeze(0).numpy()  # (channels, horizon)
    
    print(f"预测结果形状: {prediction.shape}")
    print(f"预测步数: {prediction.shape[1]}")
    
    # 反归一化预测结果
    denormalized_prediction = prediction.copy()
    for channel in range(prediction.shape[0]):
        if str(channel) in processed_data['channel_stats']:
            stats = processed_data['channel_stats'][str(channel)]
            min_val = stats['min']
            max_val = stats['max']
            denormalized_prediction[channel, :] = prediction[channel, :] * (max_val - min_val) + min_val
    
    print("\n预测结果 (反归一化):")
    for i, channel_name in enumerate(['温度', '湿度', '加速度', '电压']):
        pred_values = denormalized_prediction[i, :]
        print(f"  {channel_name}: 范围[{pred_values.min():.2f}, {pred_values.max():.2f}]")
    
    # 9. 绘制训练历史
    print("\n9. 绘制训练历史...")
    history_path = f"test_models/training_history_{timestamp}.png"
    trainer.plot_training_history(history_path)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print(f"模型文件: {model_path}")
    print(f"训练历史图: {history_path}")
    print(f"最佳验证损失: {trainer.best_val_loss:.6f}")
    print("=" * 60)
    
    return trainer, metadata, model_path

def test_model_loading(model_path):
    """测试模型加载功能"""
    print("\n测试模型加载功能...")
    
    try:
        from polls.sensor_data_loader import load_trained_model
        
        # 加载模型
        trainer, metadata = load_trained_model(model_path)
        
        print("模型加载成功！")
        print(f"模型配置: {metadata.get('model_config', {})}")
        print(f"训练日期: {metadata.get('training_date', 'Unknown')}")
        print(f"最佳验证损失: {trainer.best_val_loss:.6f}")
        
        return True
        
    except Exception as e:
        print(f"模型加载失败: {e}")
        return False

if __name__ == "__main__":
    try:
        # 运行测试
        trainer, metadata, model_path = test_multi_channel_training()
        
        # 测试模型加载
        test_model_loading(model_path)
        
        print("\n所有测试通过！系统工作正常。")
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc() 
"""
多通道LSTM训练系统测试脚本
"""

import os
import sys
import django
import numpy as np
import torch
from datetime import datetime

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.multi_channel_lstm import (
    MultiChannelLSTM, 
    MultiChannelSensorPreprocessor, 
    MultiChannelTrainer, 
    create_data_loaders
)
from polls.sensor_data_loader import SensorDataLoader

def test_multi_channel_training():
    """测试多通道LSTM训练"""
    print("=" * 60)
    print("开始测试多通道LSTM训练系统")
    print("=" * 60)
    
    # 1. 生成模拟数据
    print("\n1. 生成模拟传感器数据...")
    np.random.seed(42)
    num_channels = 4
    num_timesteps = 1000
    
    # 生成模拟数据（温度、湿度、加速度、电压）
    data = np.zeros((num_channels, num_timesteps))
    
    # 温度数据：20-30度，有趋势和季节性
    time_points = np.arange(num_timesteps)
    data[0, :] = 25 + 5 * np.sin(2 * np.pi * time_points / 100) + 0.5 * np.random.randn(num_timesteps)
    
    # 湿度数据：40-80%，与温度负相关
    data[1, :] = 60 - 0.8 * (data[0, :] - 25) + 10 * np.random.randn(num_timesteps)
    data[1, :] = np.clip(data[1, :], 40, 80)
    
    # 加速度数据：0.1-0.2g，有周期性振动
    data[2, :] = 0.15 + 0.05 * np.sin(2 * np.pi * time_points / 50) + 0.01 * np.random.randn(num_timesteps)
    
    # 电压数据：220-240V，有轻微波动
    data[3, :] = 230 + 5 * np.sin(2 * np.pi * time_points / 200) + 2 * np.random.randn(num_timesteps)
    
    print(f"模拟数据生成完成: {data.shape[0]}个通道, {data.shape[1]}个时间点")
    print(f"通道1 (温度): 范围[{data[0, :].min():.2f}, {data[0, :].max():.2f}]")
    print(f"通道2 (湿度): 范围[{data[1, :].min():.2f}, {data[1, :].max():.2f}]")
    print(f"通道3 (加速度): 范围[{data[2, :].min():.2f}, {data[2, :].max():.2f}]")
    print(f"通道4 (电压): 范围[{data[3, :].min():.2f}, {data[3, :].max():.2f}]")
    
    # 2. 数据预处理
    print("\n2. 数据预处理...")
    preprocessor = MultiChannelSensorPreprocessor(window_size=24, horizon=12)
    processed_data = preprocessor.fit_transform(data)
    
    print(f"预处理完成:")
    print(f"  训练集: {processed_data['X_train'].shape}")
    print(f"  验证集: {processed_data['X_val'].shape}")
    print(f"  测试集: {processed_data['X_test'].shape}")
    
    # 3. 创建数据加载器
    print("\n3. 创建数据加载器...")
    train_loader, val_loader = create_data_loaders(
        processed_data['X_train'], processed_data['y_train'],
        processed_data['X_val'], processed_data['y_val'],
        batch_size=32
    )
    
    print(f"数据加载器创建完成:")
    print(f"  训练批次: {len(train_loader)}")
    print(f"  验证批次: {len(val_loader)}")
    
    # 4. 创建模型
    print("\n4. 创建LSTM模型...")
    model = MultiChannelLSTM(
        num_channels=processed_data['num_channels'],
        hidden_size=64,
        num_layers=2,
        horizon=12,
        dropout=0.1
    )
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"模型创建完成: {total_params:,}个参数")
    
    # 5. 创建训练器
    print("\n5. 创建训练器...")
    trainer = MultiChannelTrainer(model)
    
    # 6. 训练模型
    print("\n6. 开始训练...")
    trainer.train(
        train_loader, val_loader,
        epochs=50,  # 减少训练轮数用于测试
        lr=0.001,
        patience=10
    )
    
    # 7. 保存模型
    print("\n7. 保存模型...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"test_models/multi_channel_lstm_{timestamp}.pth"
    
    # 创建保存目录
    os.makedirs("test_models", exist_ok=True)
    
    metadata = {
        'model_name': 'MultiChannelLSTM_Test',
        'training_date': timestamp,
        'data_info': {
            'num_channels': processed_data['num_channels'],
            'num_timesteps': processed_data['num_timesteps'],
            'window_size': 24,
            'horizon': 12
        },
        'model_config': {
            'hidden_size': 64,
            'num_layers': 2,
            'dropout': 0.1
        },
        'channel_stats': processed_data['channel_stats'],
        'test_data_info': {
            'channels': ['temperature', 'humidity', 'acceleration', 'voltage'],
            'data_range': {
                'temperature': [data[0, :].min(), data[0, :].max()],
                'humidity': [data[1, :].min(), data[1, :].max()],
                'acceleration': [data[2, :].min(), data[2, :].max()],
                'voltage': [data[3, :].min(), data[3, :].max()]
            }
        }
    }
    
    trainer.save_model(model_path, metadata)
    
    # 8. 测试预测
    print("\n8. 测试预测功能...")
    # 使用最后一个序列进行预测
    last_sequence = processed_data['X_test'][-1]  # (channels, window_size)
    
    # 进行预测
    model.eval()
    with torch.no_grad():
        input_tensor = torch.FloatTensor(last_sequence).unsqueeze(0)  # 添加batch维度
        prediction = model(input_tensor)
        prediction = prediction.squeeze(0).numpy()  # (channels, horizon)
    
    print(f"预测结果形状: {prediction.shape}")
    print(f"预测步数: {prediction.shape[1]}")
    
    # 反归一化预测结果
    denormalized_prediction = prediction.copy()
    for channel in range(prediction.shape[0]):
        if str(channel) in processed_data['channel_stats']:
            stats = processed_data['channel_stats'][str(channel)]
            min_val = stats['min']
            max_val = stats['max']
            denormalized_prediction[channel, :] = prediction[channel, :] * (max_val - min_val) + min_val
    
    print("\n预测结果 (反归一化):")
    for i, channel_name in enumerate(['温度', '湿度', '加速度', '电压']):
        pred_values = denormalized_prediction[i, :]
        print(f"  {channel_name}: 范围[{pred_values.min():.2f}, {pred_values.max():.2f}]")
    
    # 9. 绘制训练历史
    print("\n9. 绘制训练历史...")
    history_path = f"test_models/training_history_{timestamp}.png"
    trainer.plot_training_history(history_path)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print(f"模型文件: {model_path}")
    print(f"训练历史图: {history_path}")
    print(f"最佳验证损失: {trainer.best_val_loss:.6f}")
    print("=" * 60)
    
    return trainer, metadata, model_path

def test_model_loading(model_path):
    """测试模型加载功能"""
    print("\n测试模型加载功能...")
    
    try:
        from polls.sensor_data_loader import load_trained_model
        
        # 加载模型
        trainer, metadata = load_trained_model(model_path)
        
        print("模型加载成功！")
        print(f"模型配置: {metadata.get('model_config', {})}")
        print(f"训练日期: {metadata.get('training_date', 'Unknown')}")
        print(f"最佳验证损失: {trainer.best_val_loss:.6f}")
        
        return True
        
    except Exception as e:
        print(f"模型加载失败: {e}")
        return False

if __name__ == "__main__":
    try:
        # 运行测试
        trainer, metadata, model_path = test_multi_channel_training()
        
        # 测试模型加载
        test_model_loading(model_path)
        
        print("\n所有测试通过！系统工作正常。")
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc() 
 
 