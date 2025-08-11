import numpy as np
import pandas as pd
from django.db import connection
from .models import MonitorTask
from .multi_channel_lstm import MultiChannelSensorPreprocessor, MultiChannelLSTM, MultiChannelTrainer, create_data_loaders
import torch
import os
import json
from datetime import datetime

class SensorDataLoader:
    """传感器数据加载器"""
    
    def __init__(self):
        # 支持CSV文件中的通道列名（CH0, CH1, CH2, ...）
        self.channel_mapping = {}
        for i in range(16):  # 支持16个通道
            self.channel_mapping[f'CH{i}'] = f'CH{i}'
        
        # 也支持传统的传感器名称（向后兼容）
        traditional_channels = {
            'temperature': 'temperature',
            'humidity': 'humidity', 
            'acceleration': 'acceleration',
            'voltage': 'voltage',
            'current': 'current',
            'power': 'power',
            'frequency': 'frequency',
            'pressure': 'pressure',
            'flow_rate': 'flow_rate',
            'level': 'level'
        }
        self.channel_mapping.update(traditional_channels)
    
    def load_sensor_data(self, task_ids, channels, start_time=None, end_time=None):
        """
        从CSV文件加载多通道传感器数据
        
        Args:
            task_ids: 任务ID列表
            channels: 通道名称列表，如 ['temperature', 'humidity', 'acceleration']
            start_time: 开始时间 (datetime对象)
            end_time: 结束时间 (datetime对象)
        
        Returns:
            data: numpy数组，形状为 (channels, timesteps)
            channel_names: 通道名称列表
        """
        print(f"开始加载传感器数据...")
        print(f"任务ID: {task_ids}")
        print(f"通道: {channels}")
        
        # 验证通道
        valid_channels = []
        for channel in channels:
            if channel in self.channel_mapping:
                valid_channels.append(channel)
            else:
                print(f"警告: 未知通道 '{channel}'，已跳过")
        
        if not valid_channels:
            raise ValueError("没有有效的通道")
        
        # 从任务中获取CSV文件路径
        all_data = []
        channel_names = []
        
        for task_id in task_ids:
            try:
                task = MonitorTask.objects.get(task_id=task_id)
                csv_file_path = task.csv_file_path
                
                if not os.path.exists(csv_file_path):
                    print(f"警告: CSV文件不存在: {csv_file_path}")
                    continue
                
                # 读取CSV文件
                df = pd.read_csv(csv_file_path)
                print(f"从 {csv_file_path} 加载数据，形状: {df.shape}")
                
                # 提取指定通道的数据
                for channel in valid_channels:
                    if channel in df.columns:
                        channel_data = df[channel].values
                        all_data.append(channel_data)
                        channel_names.append(f"{task_id}_{channel}")
                    else:
                        print(f"警告: CSV文件中没有 '{channel}' 列")
                
            except MonitorTask.DoesNotExist:
                print(f"警告: 任务ID '{task_id}' 不存在")
            except Exception as e:
                print(f"警告: 加载任务 '{task_id}' 数据时出错: {e}")
        
        if not all_data:
            raise ValueError("没有找到有效的数据")
        
        # 转换为numpy数组
        data = np.array(all_data)
        
        print(f"数据加载完成: {data.shape[0]}个通道, {data.shape[1]}个时间点")
        print(f"通道名称: {channel_names}")
        
        return data, channel_names
    
    def load_data_by_task(self, task_id, channels=None):
        """
        根据任务ID加载数据
        
        Args:
            task_id: 任务ID
            channels: 通道列表，如果为None则加载所有可用通道
        
        Returns:
            data: numpy数组
            channel_names: 通道名称列表
        """
        # 检查任务是否存在
        try:
            task = MonitorTask.objects.get(task_id=task_id)
            print(f"任务信息: {task.task_name}")
        except MonitorTask.DoesNotExist:
            raise ValueError(f"任务ID '{task_id}' 不存在")
        
        # 如果没有指定通道，则获取所有可用通道
        if channels is None:
            channels = self._get_available_channels(task_id)
        
        return self.load_sensor_data([task_id], channels)
    
    def _get_available_channels(self, task_id):
        """获取任务中可用的通道"""
        try:
            task = MonitorTask.objects.get(task_id=task_id)
            csv_file_path = task.csv_file_path
            
            if not os.path.exists(csv_file_path):
                print(f"警告: CSV文件不存在: {csv_file_path}")
                return []
            
            # 读取CSV文件头部来获取可用列
            df = pd.read_csv(csv_file_path, nrows=1)  # 只读取第一行来获取列名
            
            available_channels = []
            # 查找所有CH开头的列（如CH0, CH1, CH2, ...）
            for column in df.columns:
                if column.startswith('CH') and column[2:].isdigit():
                    available_channels.append(column)
            
            # 如果没有找到CH格式的列，尝试查找传统的传感器名称
            if not available_channels:
                for channel in self.channel_mapping.keys():
                    if channel in df.columns:
                        available_channels.append(channel)
            
            print(f"可用通道: {available_channels}")
            return available_channels
            
        except MonitorTask.DoesNotExist:
            print(f"警告: 任务ID '{task_id}' 不存在")
            return []
        except Exception as e:
            print(f"警告: 获取可用通道时出错: {e}")
            return []

def train_multi_channel_model(task_ids, channels, model_config=None, save_dir="models", progress_callback=None, training_set_id=None):
    """
    训练多通道LSTM模型
    
    Args:
        task_ids: 任务ID列表
        channels: 通道名称列表
        model_config: 模型配置字典
        save_dir: 模型保存目录
        progress_callback: 训练进度回调函数
        training_set_id: 训练集ID，用于检查停止状态
    
    Returns:
        trainer: 训练好的训练器对象
        metadata: 模型元数据
    """
    print(f"🚀 开始多通道LSTM模型训练...")
    print(f"📊 任务ID: {task_ids}")
    print(f"📊 通道: {channels}")
    print(f"📊 模型配置: {model_config}")
    print(f"📁 保存目录: {save_dir}")
    if training_set_id:
        print(f"🆔 训练集ID: {training_set_id}")
    
    try:
        # 创建数据加载器
        print(f"📦 创建数据加载器...")
        loader = SensorDataLoader()
        
        # 加载数据
        print(f"📥 开始加载传感器数据...")
        data, channel_names = loader.load_sensor_data(task_ids, channels)
        print(f"✅ 数据加载完成，形状: {data.shape}")
        print(f"✅ 通道名称: {channel_names}")
        
        # 检查数据质量
        print(f"🔍 检查数据质量...")
        invalid_channels = []
        for i, channel in enumerate(channel_names):
            channel_data = data[i, :]
            min_val = channel_data.min()
            max_val = channel_data.max()
            mean_val = channel_data.mean()
            std_val = channel_data.std()
            
            print(f"  {channel}: 形状={channel_data.shape}, 范围=[{min_val:.3f}, {max_val:.3f}], 均值={mean_val:.3f}, 标准差={std_val:.3f}")
            
            # 检查数据是否有效
            if max_val == min_val:
                print(f"    ⚠️  警告: 通道数据无效（所有值相同）")
                invalid_channels.append(i)
        
        # 如果所有通道都无效，提前停止
        if len(invalid_channels) == len(channel_names):
            raise ValueError("所有通道数据都无效（所有值相同），无法进行训练。请检查传感器连接或使用有效的数据。")
        
        # 创建预处理器
        print(f"🔧 创建数据预处理器...")
        window_size = model_config.get('window_size', 24)
        horizon = model_config.get('horizon', 12)
        preprocessor = MultiChannelSensorPreprocessor(window_size=window_size, horizon=horizon)
        
        # 预处理数据
        print(f"🔄 开始数据预处理...")
        processed_data = preprocessor.fit_transform(data)
        print(f"✅ 数据预处理完成")
        print(f"📊 训练数据形状: {processed_data['X_train'].shape}")
        print(f"📊 验证数据形状: {processed_data['X_val'].shape}")
        print(f"📊 测试数据形状: {processed_data['X_test'].shape}")
        
        # 创建数据加载器
        print(f"📦 创建PyTorch数据加载器...")
        batch_size = model_config.get('batch_size', 32)
        
        print(f"📊 批次大小: {batch_size}")
        
        train_loader, val_loader = create_data_loaders(
            processed_data['X_train'], 
            processed_data['y_train'],
            processed_data['X_val'], 
            processed_data['y_val'],
            batch_size=batch_size
        )
        
        print(f"✅ 数据加载器创建完成")
        print(f"  - 训练集批次数: {len(train_loader)}")
        print(f"  - 验证集批次数: {len(val_loader)}")
        
        # 创建模型
        print(f"🏗️ 创建LSTM模型...")
        input_size = processed_data['num_channels']  # 通道数
        hidden_size = model_config.get('hidden_size', 64)
        num_layers = model_config.get('num_layers', 2)
        dropout = model_config.get('dropout', 0.1)
        horizon = model_config.get('horizon', 12)
        
        print(f"📊 输入维度: {input_size}")
        print(f"📊 隐藏层大小: {hidden_size}")
        print(f"📊 LSTM层数: {num_layers}")
        print(f"📊 Dropout率: {dropout}")
        print(f"📊 预测步长: {horizon}")
        
        # 创建LSTM模型
        model = MultiChannelLSTM(
            num_channels=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            horizon=horizon,
            dropout=dropout
        )
        
        # 创建训练器
        trainer = MultiChannelTrainer(model)
        
        # 开始训练
        print(f"🚀 开始训练...")
        history = trainer.train(
            train_loader, 
            val_loader, 
            epochs=model_config.get('epochs', 100),
            lr=model_config.get('lr', 0.001),
            patience=model_config.get('patience', 10),
            progress_callback=progress_callback,
            training_set_id=training_set_id
        )
        
        # 检查训练是否被停止
        if history.get('status') == 'stopped':
            print(f"⏹️ 训练已被停止")
            return trainer, {
                'model_path': None,
                'channels': channel_names,
                'data_info': {
                    'window_size': window_size,
                    'horizon': horizon,
                    'input_size': input_size,
                    'data_shape': data.shape
                },
                'model_config': model_config,
                'training_history': history,
                'channel_stats': processed_data['channel_stats'],
                'test_data': {
                    'X_test': processed_data['X_test'],
                    'y_test': processed_data['y_test']
                },
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'status': 'stopped'
            }
        
        print(f"✅ 训练完成！")
        print(f"⏰ 训练结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存模型
        print(f"💾 保存模型...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_filename = f"multi_channel_lstm_{timestamp}.pth"
        model_path = os.path.join(save_dir, model_filename)
        
        metadata = {
            'model_path': model_path,
            'channels': channel_names,
            'data_info': {
                'window_size': window_size,
                'horizon': horizon,
                'input_size': input_size,
                'data_shape': data.shape
            },
            'model_config': model_config,
            'training_history': history,
            'channel_stats': processed_data['channel_stats'],
            'test_data': {
                'X_test': processed_data['X_test'].tolist(),  # 转换为列表
                'y_test': processed_data['y_test'].tolist()   # 转换为列表
            },
            'timestamp': timestamp,
        }
        
        trainer.save_model(model_path, metadata)
        print(f"✅ 模型已保存到: {model_path}")
        
        # 打印训练结果
        print(f"📊 训练结果总结:")
        if history and 'train_loss' in history and len(history['train_loss']) > 0:
            print(f"  - 最终训练损失: {history['train_loss'][-1]:.6f}")
        if history and 'val_loss' in history and len(history['val_loss']) > 0:
            print(f"  - 最终验证损失: {history['val_loss'][-1]:.6f}")
        if history and 'best_val_loss' in history:
            print(f"  - 最佳验证损失: {history['best_val_loss']:.6f}")
        if history and 'epochs_trained' in history:
            print(f"  - 训练轮数: {history['epochs_trained']}")
        
        return trainer, metadata
        
    except Exception as e:
        print(f"❌ 训练过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        raise e

def load_trained_model(model_path):
    """
    加载训练好的模型
    
    Args:
        model_path: 模型文件路径
    
    Returns:
        trainer: 训练器对象
        metadata: 模型元数据
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    # 首先加载模型数据来获取配置
    save_data = torch.load(model_path, map_location='cpu', weights_only=False)
    model_config = save_data.get('model_config', {})
    
    # 从模型配置中获取通道数，必须存在
    if 'num_channels' not in model_config:
        raise ValueError(f"模型配置中缺少num_channels字段: {model_config}")
    
    num_channels = model_config['num_channels']
    hidden_size = model_config.get('hidden_size', 64)
    num_layers = model_config.get('num_layers', 2)
    horizon = model_config.get('horizon', 12)
    
    print(f"📊 从模型文件中读取的配置:")
    print(f"  - 通道数: {num_channels}")
    print(f"  - 隐藏层大小: {hidden_size}")
    print(f"  - LSTM层数: {num_layers}")
    print(f"  - 预测步长: {horizon}")
    
    # 使用正确的配置创建dummy模型
    dummy_model = MultiChannelLSTM(
        num_channels=num_channels,
        hidden_size=hidden_size,
        num_layers=num_layers,
        horizon=horizon
    )
    trainer = MultiChannelTrainer(dummy_model)
    
    # 加载模型
    metadata = trainer.load_model(model_path)
    
    # 确保metadata包含正确的model_config（使用模型文件中的配置）
    metadata['model_config'] = model_config
    
    return trainer, metadata

def predict_with_model(model_path, input_sequence, denormalize=True):
    """
    使用训练好的模型进行预测
    
    Args:
        model_path: 模型文件路径
        input_sequence: 输入序列，形状为 (channels, window_size)
        denormalize: 是否反归一化预测结果
    
    Returns:
        prediction: 预测结果
        metadata: 模型元数据
    """
    # 加载模型
    trainer, metadata = load_trained_model(model_path)
    model = trainer.model
    
    # 确保输入格式正确
    if isinstance(input_sequence, np.ndarray):
        input_sequence = torch.FloatTensor(input_sequence)
    
    # 添加batch维度
    if input_sequence.dim() == 2:  # (channels, window_size)
        input_sequence = input_sequence.unsqueeze(0)  # (1, channels, window_size)
    
    # 预测
    model.eval()
    with torch.no_grad():
        prediction = model(input_sequence)
        prediction = prediction.squeeze(0).cpu().numpy()  # (channels, horizon)
    
    # 反归一化
    if denormalize and 'channel_stats' in metadata:
        prediction = denormalize_prediction(prediction, metadata['channel_stats'])
    
    return prediction, metadata

def denormalize_prediction(prediction, channel_stats):
    """反归一化预测结果"""
    denormalized = prediction.copy()
    
    for channel in range(prediction.shape[0]):
        if str(channel) in channel_stats:
            stats = channel_stats[str(channel)]
            min_val = stats['min']
            max_val = stats['max']
            
            # 反归一化: normalized * (max - min) + min
            denormalized[channel, :] = prediction[channel, :] * (max_val - min_val) + min_val
    
    return denormalized

# 使用示例
if __name__ == "__main__":
    # 示例：训练模型
    task_ids = ['task1', 'task2']  # 替换为实际的任务ID
    channels = ['temperature', 'humidity', 'acceleration']  # 替换为实际的通道
    
    try:
        trainer, metadata = train_multi_channel_model(task_ids, channels)
        print("训练成功完成！")
        
        # 示例：使用模型进行预测
        # 假设我们有一个输入序列
        input_sequence = np.random.randn(3, 24)  # 3个通道，24个时间点
        
        prediction, _ = predict_with_model(
            "models/multi_channel_lstm_20240101_120000.pth",  # 替换为实际的模型路径
            input_sequence
        )
        
        print(f"预测结果形状: {prediction.shape}")
        
    except Exception as e:
        print(f"训练过程中出现错误: {e}") 
import pandas as pd
from django.db import connection
from .models import MonitorTask
from .multi_channel_lstm import MultiChannelSensorPreprocessor, MultiChannelLSTM, MultiChannelTrainer, create_data_loaders
import torch
import os
import json
from datetime import datetime

class SensorDataLoader:
    """传感器数据加载器"""
    
    def __init__(self):
        # 支持CSV文件中的通道列名（CH0, CH1, CH2, ...）
        self.channel_mapping = {}
        for i in range(16):  # 支持16个通道
            self.channel_mapping[f'CH{i}'] = f'CH{i}'
        
        # 也支持传统的传感器名称（向后兼容）
        traditional_channels = {
            'temperature': 'temperature',
            'humidity': 'humidity', 
            'acceleration': 'acceleration',
            'voltage': 'voltage',
            'current': 'current',
            'power': 'power',
            'frequency': 'frequency',
            'pressure': 'pressure',
            'flow_rate': 'flow_rate',
            'level': 'level'
        }
        self.channel_mapping.update(traditional_channels)
    
    def load_sensor_data(self, task_ids, channels, start_time=None, end_time=None):
        """
        从CSV文件加载多通道传感器数据
        
        Args:
            task_ids: 任务ID列表
            channels: 通道名称列表，如 ['temperature', 'humidity', 'acceleration']
            start_time: 开始时间 (datetime对象)
            end_time: 结束时间 (datetime对象)
        
        Returns:
            data: numpy数组，形状为 (channels, timesteps)
            channel_names: 通道名称列表
        """
        print(f"开始加载传感器数据...")
        print(f"任务ID: {task_ids}")
        print(f"通道: {channels}")
        
        # 验证通道
        valid_channels = []
        for channel in channels:
            if channel in self.channel_mapping:
                valid_channels.append(channel)
            else:
                print(f"警告: 未知通道 '{channel}'，已跳过")
        
        if not valid_channels:
            raise ValueError("没有有效的通道")
        
        # 从任务中获取CSV文件路径
        all_data = []
        channel_names = []
        
        for task_id in task_ids:
            try:
                task = MonitorTask.objects.get(task_id=task_id)
                csv_file_path = task.csv_file_path
                
                if not os.path.exists(csv_file_path):
                    print(f"警告: CSV文件不存在: {csv_file_path}")
                    continue
                
                # 读取CSV文件
                df = pd.read_csv(csv_file_path)
                print(f"从 {csv_file_path} 加载数据，形状: {df.shape}")
                
                # 提取指定通道的数据
                for channel in valid_channels:
                    if channel in df.columns:
                        channel_data = df[channel].values
                        all_data.append(channel_data)
                        channel_names.append(f"{task_id}_{channel}")
                    else:
                        print(f"警告: CSV文件中没有 '{channel}' 列")
                
            except MonitorTask.DoesNotExist:
                print(f"警告: 任务ID '{task_id}' 不存在")
            except Exception as e:
                print(f"警告: 加载任务 '{task_id}' 数据时出错: {e}")
        
        if not all_data:
            raise ValueError("没有找到有效的数据")
        
        # 转换为numpy数组
        data = np.array(all_data)
        
        print(f"数据加载完成: {data.shape[0]}个通道, {data.shape[1]}个时间点")
        print(f"通道名称: {channel_names}")
        
        return data, channel_names
    
    def load_data_by_task(self, task_id, channels=None):
        """
        根据任务ID加载数据
        
        Args:
            task_id: 任务ID
            channels: 通道列表，如果为None则加载所有可用通道
        
        Returns:
            data: numpy数组
            channel_names: 通道名称列表
        """
        # 检查任务是否存在
        try:
            task = MonitorTask.objects.get(task_id=task_id)
            print(f"任务信息: {task.task_name}")
        except MonitorTask.DoesNotExist:
            raise ValueError(f"任务ID '{task_id}' 不存在")
        
        # 如果没有指定通道，则获取所有可用通道
        if channels is None:
            channels = self._get_available_channels(task_id)
        
        return self.load_sensor_data([task_id], channels)
    
    def _get_available_channels(self, task_id):
        """获取任务中可用的通道"""
        try:
            task = MonitorTask.objects.get(task_id=task_id)
            csv_file_path = task.csv_file_path
            
            if not os.path.exists(csv_file_path):
                print(f"警告: CSV文件不存在: {csv_file_path}")
                return []
            
            # 读取CSV文件头部来获取可用列
            df = pd.read_csv(csv_file_path, nrows=1)  # 只读取第一行来获取列名
            
            available_channels = []
            # 查找所有CH开头的列（如CH0, CH1, CH2, ...）
            for column in df.columns:
                if column.startswith('CH') and column[2:].isdigit():
                    available_channels.append(column)
            
            # 如果没有找到CH格式的列，尝试查找传统的传感器名称
            if not available_channels:
                for channel in self.channel_mapping.keys():
                    if channel in df.columns:
                        available_channels.append(channel)
            
            print(f"可用通道: {available_channels}")
            return available_channels
            
        except MonitorTask.DoesNotExist:
            print(f"警告: 任务ID '{task_id}' 不存在")
            return []
        except Exception as e:
            print(f"警告: 获取可用通道时出错: {e}")
            return []

def train_multi_channel_model(task_ids, channels, model_config=None, save_dir="models", progress_callback=None, training_set_id=None):
    """
    训练多通道LSTM模型
    
    Args:
        task_ids: 任务ID列表
        channels: 通道名称列表
        model_config: 模型配置字典
        save_dir: 模型保存目录
        progress_callback: 训练进度回调函数
        training_set_id: 训练集ID，用于检查停止状态
    
    Returns:
        trainer: 训练好的训练器对象
        metadata: 模型元数据
    """
    print(f"🚀 开始多通道LSTM模型训练...")
    print(f"📊 任务ID: {task_ids}")
    print(f"📊 通道: {channels}")
    print(f"📊 模型配置: {model_config}")
    print(f"📁 保存目录: {save_dir}")
    if training_set_id:
        print(f"🆔 训练集ID: {training_set_id}")
    
    try:
        # 创建数据加载器
        print(f"📦 创建数据加载器...")
        loader = SensorDataLoader()
        
        # 加载数据
        print(f"📥 开始加载传感器数据...")
        data, channel_names = loader.load_sensor_data(task_ids, channels)
        print(f"✅ 数据加载完成，形状: {data.shape}")
        print(f"✅ 通道名称: {channel_names}")
        
        # 检查数据质量
        print(f"🔍 检查数据质量...")
        invalid_channels = []
        for i, channel in enumerate(channel_names):
            channel_data = data[i, :]
            min_val = channel_data.min()
            max_val = channel_data.max()
            mean_val = channel_data.mean()
            std_val = channel_data.std()
            
            print(f"  {channel}: 形状={channel_data.shape}, 范围=[{min_val:.3f}, {max_val:.3f}], 均值={mean_val:.3f}, 标准差={std_val:.3f}")
            
            # 检查数据是否有效
            if max_val == min_val:
                print(f"    ⚠️  警告: 通道数据无效（所有值相同）")
                invalid_channels.append(i)
        
        # 如果所有通道都无效，提前停止
        if len(invalid_channels) == len(channel_names):
            raise ValueError("所有通道数据都无效（所有值相同），无法进行训练。请检查传感器连接或使用有效的数据。")
        
        # 创建预处理器
        print(f"🔧 创建数据预处理器...")
        window_size = model_config.get('window_size', 24)
        horizon = model_config.get('horizon', 12)
        preprocessor = MultiChannelSensorPreprocessor(window_size=window_size, horizon=horizon)
        
        # 预处理数据
        print(f"🔄 开始数据预处理...")
        processed_data = preprocessor.fit_transform(data)
        print(f"✅ 数据预处理完成")
        print(f"📊 训练数据形状: {processed_data['X_train'].shape}")
        print(f"📊 验证数据形状: {processed_data['X_val'].shape}")
        print(f"📊 测试数据形状: {processed_data['X_test'].shape}")
        
        # 创建数据加载器
        print(f"📦 创建PyTorch数据加载器...")
        batch_size = model_config.get('batch_size', 32)
        
        print(f"📊 批次大小: {batch_size}")
        
        train_loader, val_loader = create_data_loaders(
            processed_data['X_train'], 
            processed_data['y_train'],
            processed_data['X_val'], 
            processed_data['y_val'],
            batch_size=batch_size
        )
        
        print(f"✅ 数据加载器创建完成")
        print(f"  - 训练集批次数: {len(train_loader)}")
        print(f"  - 验证集批次数: {len(val_loader)}")
        
        # 创建模型
        print(f"🏗️ 创建LSTM模型...")
        input_size = processed_data['num_channels']  # 通道数
        hidden_size = model_config.get('hidden_size', 64)
        num_layers = model_config.get('num_layers', 2)
        dropout = model_config.get('dropout', 0.1)
        horizon = model_config.get('horizon', 12)
        
        print(f"📊 输入维度: {input_size}")
        print(f"📊 隐藏层大小: {hidden_size}")
        print(f"📊 LSTM层数: {num_layers}")
        print(f"📊 Dropout率: {dropout}")
        print(f"📊 预测步长: {horizon}")
        
        # 创建LSTM模型
        model = MultiChannelLSTM(
            num_channels=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            horizon=horizon,
            dropout=dropout
        )
        
        # 创建训练器
        trainer = MultiChannelTrainer(model)
        
        # 开始训练
        print(f"🚀 开始训练...")
        history = trainer.train(
            train_loader, 
            val_loader, 
            epochs=model_config.get('epochs', 100),
            lr=model_config.get('lr', 0.001),
            patience=model_config.get('patience', 10),
            progress_callback=progress_callback,
            training_set_id=training_set_id
        )
        
        # 检查训练是否被停止
        if history.get('status') == 'stopped':
            print(f"⏹️ 训练已被停止")
            return trainer, {
                'model_path': None,
                'channels': channel_names,
                'data_info': {
                    'window_size': window_size,
                    'horizon': horizon,
                    'input_size': input_size,
                    'data_shape': data.shape
                },
                'model_config': model_config,
                'training_history': history,
                'channel_stats': processed_data['channel_stats'],
                'test_data': {
                    'X_test': processed_data['X_test'],
                    'y_test': processed_data['y_test']
                },
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'status': 'stopped'
            }
        
        print(f"✅ 训练完成！")
        print(f"⏰ 训练结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存模型
        print(f"💾 保存模型...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_filename = f"multi_channel_lstm_{timestamp}.pth"
        model_path = os.path.join(save_dir, model_filename)
        
        metadata = {
            'model_path': model_path,
            'channels': channel_names,
            'data_info': {
                'window_size': window_size,
                'horizon': horizon,
                'input_size': input_size,
                'data_shape': data.shape
            },
            'model_config': model_config,
            'training_history': history,
            'channel_stats': processed_data['channel_stats'],
            'test_data': {
                'X_test': processed_data['X_test'].tolist(),  # 转换为列表
                'y_test': processed_data['y_test'].tolist()   # 转换为列表
            },
            'timestamp': timestamp,
        }
        
        trainer.save_model(model_path, metadata)
        print(f"✅ 模型已保存到: {model_path}")
        
        # 打印训练结果
        print(f"📊 训练结果总结:")
        if history and 'train_loss' in history and len(history['train_loss']) > 0:
            print(f"  - 最终训练损失: {history['train_loss'][-1]:.6f}")
        if history and 'val_loss' in history and len(history['val_loss']) > 0:
            print(f"  - 最终验证损失: {history['val_loss'][-1]:.6f}")
        if history and 'best_val_loss' in history:
            print(f"  - 最佳验证损失: {history['best_val_loss']:.6f}")
        if history and 'epochs_trained' in history:
            print(f"  - 训练轮数: {history['epochs_trained']}")
        
        return trainer, metadata
        
    except Exception as e:
        print(f"❌ 训练过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        raise e

def load_trained_model(model_path):
    """
    加载训练好的模型
    
    Args:
        model_path: 模型文件路径
    
    Returns:
        trainer: 训练器对象
        metadata: 模型元数据
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    # 首先加载模型数据来获取配置
    save_data = torch.load(model_path, map_location='cpu', weights_only=False)
    model_config = save_data.get('model_config', {})
    
    # 从模型配置中获取通道数，必须存在
    if 'num_channels' not in model_config:
        raise ValueError(f"模型配置中缺少num_channels字段: {model_config}")
    
    num_channels = model_config['num_channels']
    hidden_size = model_config.get('hidden_size', 64)
    num_layers = model_config.get('num_layers', 2)
    horizon = model_config.get('horizon', 12)
    
    print(f"📊 从模型文件中读取的配置:")
    print(f"  - 通道数: {num_channels}")
    print(f"  - 隐藏层大小: {hidden_size}")
    print(f"  - LSTM层数: {num_layers}")
    print(f"  - 预测步长: {horizon}")
    
    # 使用正确的配置创建dummy模型
    dummy_model = MultiChannelLSTM(
        num_channels=num_channels,
        hidden_size=hidden_size,
        num_layers=num_layers,
        horizon=horizon
    )
    trainer = MultiChannelTrainer(dummy_model)
    
    # 加载模型
    metadata = trainer.load_model(model_path)
    
    # 确保metadata包含正确的model_config（使用模型文件中的配置）
    metadata['model_config'] = model_config
    
    return trainer, metadata

def predict_with_model(model_path, input_sequence, denormalize=True):
    """
    使用训练好的模型进行预测
    
    Args:
        model_path: 模型文件路径
        input_sequence: 输入序列，形状为 (channels, window_size)
        denormalize: 是否反归一化预测结果
    
    Returns:
        prediction: 预测结果
        metadata: 模型元数据
    """
    # 加载模型
    trainer, metadata = load_trained_model(model_path)
    model = trainer.model
    
    # 确保输入格式正确
    if isinstance(input_sequence, np.ndarray):
        input_sequence = torch.FloatTensor(input_sequence)
    
    # 添加batch维度
    if input_sequence.dim() == 2:  # (channels, window_size)
        input_sequence = input_sequence.unsqueeze(0)  # (1, channels, window_size)
    
    # 预测
    model.eval()
    with torch.no_grad():
        prediction = model(input_sequence)
        prediction = prediction.squeeze(0).cpu().numpy()  # (channels, horizon)
    
    # 反归一化
    if denormalize and 'channel_stats' in metadata:
        prediction = denormalize_prediction(prediction, metadata['channel_stats'])
    
    return prediction, metadata

def denormalize_prediction(prediction, channel_stats):
    """反归一化预测结果"""
    denormalized = prediction.copy()
    
    for channel in range(prediction.shape[0]):
        if str(channel) in channel_stats:
            stats = channel_stats[str(channel)]
            min_val = stats['min']
            max_val = stats['max']
            
            # 反归一化: normalized * (max - min) + min
            denormalized[channel, :] = prediction[channel, :] * (max_val - min_val) + min_val
    
    return denormalized

# 使用示例
if __name__ == "__main__":
    # 示例：训练模型
    task_ids = ['task1', 'task2']  # 替换为实际的任务ID
    channels = ['temperature', 'humidity', 'acceleration']  # 替换为实际的通道
    
    try:
        trainer, metadata = train_multi_channel_model(task_ids, channels)
        print("训练成功完成！")
        
        # 示例：使用模型进行预测
        # 假设我们有一个输入序列
        input_sequence = np.random.randn(3, 24)  # 3个通道，24个时间点
        
        prediction, _ = predict_with_model(
            "models/multi_channel_lstm_20240101_120000.pth",  # 替换为实际的模型路径
            input_sequence
        )
        
        print(f"预测结果形状: {prediction.shape}")
        
    except Exception as e:
        print(f"训练过程中出现错误: {e}") 
 
 