import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime
import warnings
import pandas as pd
import torch.nn.functional as F
warnings.filterwarnings('ignore')

class MultiChannelLSTM(nn.Module):
    """多通道传感器数据LSTM模型"""
    
    def __init__(self, num_channels, hidden_size, num_layers, horizon, dropout=0.1):
        super().__init__()
        self.num_channels = num_channels
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.horizon = horizon
        
        # LSTM层
        self.lstm = nn.LSTM(
            input_size=num_channels,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # 全连接层
        self.fc = nn.Linear(hidden_size, num_channels * horizon)
        
        # 初始化权重
        self._init_weights()
    
    def _init_weights(self):
        """初始化模型权重"""
        for name, param in self.named_parameters():
            if 'weight' in name:
                nn.init.xavier_uniform_(param)
            elif 'bias' in name:
                nn.init.zeros_(param)
    
    def forward(self, x):
        # x shape: (batch_size, window_size, num_channels)
        batch_size = x.size(0)
        
        # LSTM前向传播
        lstm_out, _ = self.lstm(x)
        # lstm_out shape: (batch_size, window_size, hidden_size)
        
        # 取最后一个时间步的输出
        last_output = lstm_out[:, -1, :]  # (batch_size, hidden_size)
        
        # 全连接层
        output = self.fc(last_output)  # (batch_size, num_channels * horizon)
        
        # 重塑为: (batch_size, num_channels, horizon)
        output = output.view(batch_size, self.num_channels, self.horizon)
        
        return output

class MultiChannelSensorPreprocessor:
    """多通道传感器数据预处理器"""
    
    def __init__(self, window_size, horizon, normalization='independent'):
        self.window_size = window_size
        self.horizon = horizon
        self.normalization = normalization
        self.channel_stats = {}
        
    def fit_transform(self, data):
        """多通道传感器数据预处理"""
        # 1. 数据验证
        self._validate_data(data)
        
        # 2. 缺失值处理
        data = self._handle_missing_values(data)
        
        # 3. 异常值检测与处理
        data = self._handle_outliers(data)
        
        # 4. 多通道独立归一化
        data, self.channel_stats = self._normalize_channels(data)
        
        # 5. 创建时间序列窗口
        X, y = self._create_sequences(data)
        
        # 6. 数据分割
        X_train, X_val, X_test, y_train, y_val, y_test = self._split_data(X, y)
        
        return {
            'X_train': X_train, 'y_train': y_train,
            'X_val': X_val, 'y_val': y_val,
            'X_test': X_test, 'y_test': y_test,
            'channel_stats': self.channel_stats,
            'num_channels': data.shape[0],
            'num_timesteps': data.shape[1]
        }
    
    def _validate_data(self, data):
        """验证多通道传感器数据"""
        if data.ndim != 2:
            raise ValueError("数据必须是2维数组 (channels, timesteps)")
        
        num_channels, num_timesteps = data.shape
        
        if num_timesteps < self.window_size + self.horizon:
            raise ValueError(f"数据长度({num_timesteps})不足以创建窗口({self.window_size + self.horizon})")
        
        print(f"数据验证通过: {num_channels}个通道, {num_timesteps}个时间点")
    
    def _handle_missing_values(self, data):
        """处理缺失值"""
        # 使用前向填充和后向填充
        data_filled = data.copy()
        
        for channel in range(data.shape[0]):
            channel_data = data[channel, :]
            # 前向填充
            channel_data = pd.Series(channel_data).fillna(method='ffill')
            # 后向填充（处理开头的缺失值）
            channel_data = pd.Series(channel_data).fillna(method='bfill')
            # 如果还有缺失值，用均值填充
            if channel_data.isna().any():
                mean_val = channel_data.dropna().mean()
                channel_data = channel_data.fillna(mean_val)
            
            data_filled[channel, :] = channel_data.values
        
        print("缺失值处理完成")
        return data_filled
    
    def _handle_outliers(self, data):
        """处理异常值"""
        data_cleaned = data.copy()
        
        for channel in range(data.shape[0]):
            channel_data = data[channel, :]
            
            # 使用IQR方法检测异常值
            Q1 = np.percentile(channel_data, 25)
            Q3 = np.percentile(channel_data, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # 将异常值替换为边界值
            channel_data = np.where(channel_data < lower_bound, lower_bound, channel_data)
            channel_data = np.where(channel_data > upper_bound, upper_bound, channel_data)
            
            data_cleaned[channel, :] = channel_data
        
        print("异常值处理完成")
        return data_cleaned
    
    def _normalize_channels(self, data):
        """多通道独立归一化"""
        num_channels, num_timesteps = data.shape
        normalized_data = np.zeros_like(data)
        channel_stats = {}
        
        # 检查数据质量
        invalid_channels = []
        for channel in range(num_channels):
            channel_data = data[channel, :]
            min_val = np.min(channel_data)
            max_val = np.max(channel_data)
            
            # 检查是否所有值都相同
            if max_val == min_val:
                print(f"警告: 通道{channel}所有值相同({min_val:.3f})，数据可能无效")
                invalid_channels.append(channel)
                # 所有值相同，设为0.5
                normalized_data[channel, :] = 0.5
                channel_stats[channel] = {
                    'min': min_val,
                    'max': max_val,
                    'mean': min_val,
                    'std': 0.0,
                    'normalization_method': 'constant_value',
                    'is_valid': False
                }
            else:
                # 正常的最小-最大归一化
                normalized_data[channel, :] = (channel_data - min_val) / (max_val - min_val)
                channel_stats[channel] = {
                    'min': min_val,
                    'max': max_val,
                    'mean': np.mean(channel_data),
                    'std': np.std(channel_data),
                    'original_range': max_val - min_val,
                    'normalization_method': 'min_max',
                    'is_valid': True
                }
            
            print(f"通道{channel}归一化: 范围[{min_val:.3f}, {max_val:.3f}] → [0, 1]")
        
        # 如果所有通道都无效，抛出异常
        if len(invalid_channels) == num_channels:
            raise ValueError(f"所有通道数据都无效（所有值相同），无法进行训练。请检查传感器连接或数据质量。")
        
        return normalized_data, channel_stats
    
    def _create_sequences(self, data):
        """创建时间序列窗口"""
        num_channels, num_timesteps = data.shape
        X, y = [], []
        
        for i in range(num_timesteps - self.window_size - self.horizon + 1):
            # 输入窗口: (channels, window_size)
            X.append(data[:, i:i+self.window_size])
            
            # 输出目标: (channels, horizon)
            y.append(data[:, i+self.window_size:i+self.window_size+self.horizon])
        
        X = np.array(X)  # shape: (samples, channels, window_size)
        y = np.array(y)  # shape: (samples, channels, horizon)
        
        print(f"创建序列: {X.shape[0]}个样本, {X.shape[1]}个通道, 窗口大小{X.shape[2]}, 预测步长{y.shape[2]}")
        
        return X, y
    
    def _split_data(self, X, y):
        """数据分割"""
        total_samples = X.shape[0]
        train_size = int(0.7 * total_samples)
        val_size = int(0.15 * total_samples)
        
        # 训练集
        X_train = X[:train_size]
        y_train = y[:train_size]
        
        # 验证集
        X_val = X[train_size:train_size+val_size]
        y_val = y[train_size:train_size+val_size]
        
        # 测试集
        X_test = X[train_size+val_size:]
        y_test = y[train_size+val_size:]
        
        print(f"数据分割: 训练集{train_size}, 验证集{val_size}, 测试集{total_samples-train_size-val_size}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test

class MultiChannelTrainer:
    """多通道LSTM模型训练器"""
    
    def __init__(self, model, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.train_losses = []
        self.val_losses = []
        self.best_val_loss = float('inf')
        self.best_model_state = None
        
    def train(self, train_loader, val_loader, epochs=100, lr=0.001, patience=10, progress_callback=None, training_set_id=None):
        """训练模型"""
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr, weight_decay=1e-5)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
        
        early_stopping_counter = 0
        zero_loss_counter = 0  # 计数器，用于检测连续零损失
        
        print(f"开始训练，设备: {self.device}")
        print(f"模型参数: {sum(p.numel() for p in self.model.parameters()):,}个参数")
        
        for epoch in range(epochs):
            # 检查训练状态（如果提供了training_set_id）
            if training_set_id:
                try:
                    from django.db import connection
                    from polls.models import TrainingSet
                    
                    # 重新建立数据库连接（因为可能在长时间训练中断开）
                    connection.close()
                    
                    training_set = TrainingSet.objects.get(training_set_id=training_set_id)
                    if training_set.training_status == 'stopped':
                        print(f"⏹️ 检测到停止信号，在第{epoch+1}轮停止训练")
                        return {
                            'train_loss': self.train_losses,
                            'val_loss': self.val_losses,
                            'best_val_loss': self.best_val_loss,
                            'epochs_trained': len(self.train_losses),
                            'status': 'stopped'
                        }
                    elif training_set.training_status == 'paused':
                        print(f"⏸️ 检测到暂停信号，在第{epoch+1}轮暂停训练")
                        # 等待恢复信号
                        while training_set.training_status == 'paused':
                            import time
                            time.sleep(1)
                            training_set.refresh_from_db()
                        print(f"▶️ 训练已恢复，继续第{epoch+1}轮")
                        
                except Exception as e:
                    print(f"⚠️ 检查训练状态时出错: {e}")
            
            # 训练阶段
            self.model.train()
            train_loss = 0.0
            batch_count = 0
            
            for batch_X, batch_y in train_loader:
                # 在每个批次前检查停止状态
                if training_set_id:
                    try:
                        training_set = TrainingSet.objects.get(training_set_id=training_set_id)
                        if training_set.training_status == 'stopped':
                            print(f"⏹️ 检测到停止信号，在批次中停止训练")
                            return {
                                'train_loss': self.train_losses,
                                'val_loss': self.val_losses,
                                'best_val_loss': self.best_val_loss,
                                'epochs_trained': len(self.train_losses),
                                'status': 'stopped'
                            }
                    except Exception as e:
                        print(f"⚠️ 检查训练状态时出错: {e}")
                
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                
                # 检查损失是否为NaN
                if torch.isnan(loss):
                    print(f"警告: 第{epoch+1}轮出现NaN损失，跳过此批次")
                    continue
                
                loss.backward()
                
                # 梯度裁剪防止梯度爆炸
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                optimizer.step()
                
                train_loss += loss.item()
                batch_count += 1
            
            if batch_count > 0:
                train_loss /= batch_count
            else:
                train_loss = 0.0
            
            # 检查训练损失是否为NaN或异常
            if np.isnan(train_loss):
                print(f"警告: 第{epoch+1}轮训练损失为NaN，停止训练")
                break
            
            # 检查是否连续出现零损失（可能表示数据问题）
            if train_loss < 1e-10:
                zero_loss_counter += 1
                if zero_loss_counter >= 5:  # 连续5轮零损失
                    print(f"警告: 连续{zero_loss_counter}轮训练损失接近零，可能数据无效，停止训练")
                    break
            else:
                zero_loss_counter = 0
                
            self.train_losses.append(train_loss)
            
            # 验证阶段
            self.model.eval()
            val_loss = 0.0
            val_batch_count = 0
            
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X = batch_X.to(self.device)
                    batch_y = batch_y.to(self.device)
                    
                    outputs = self.model(batch_X)
                    loss = criterion(outputs, batch_y)
                    val_loss += loss.item()
                    val_batch_count += 1
            
            if val_batch_count > 0:
                val_loss /= val_batch_count
            else:
                val_loss = 0.0
                
            self.val_losses.append(val_loss)
            
            # 学习率调度
            scheduler.step(val_loss)
            
            # 早停检查
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.best_model_state = self.model.state_dict().copy()
                early_stopping_counter = 0
            else:
                early_stopping_counter += 1
            
            # 实时进度更新（每轮都打印）
            print(f"Epoch [{epoch+1}/{epochs}] - "
                  f"Train Loss: {train_loss:.6f}, "
                  f"Val Loss: {val_loss:.6f}, "
                  f"LR: {optimizer.param_groups[0]['lr']:.6f}")
            
            # 调用进度回调函数
            if progress_callback:
                progress_data = {
                    'epoch': epoch + 1,
                    'total_epochs': epochs,
                    'train_loss': train_loss,
                    'val_loss': val_loss,
                    'learning_rate': optimizer.param_groups[0]['lr'],
                    'status': 'training'
                }
                should_continue = progress_callback(progress_data)
                if not should_continue:
                    print(f"⏸️ 训练被暂停/停止，在第{epoch+1}轮退出")
                    break
            
            # 早停
            if early_stopping_counter >= patience:
                print(f"早停触发，在第{epoch+1}轮停止训练")
                break
        
        # 恢复最佳模型
        if self.best_model_state is not None:
            self.model.load_state_dict(self.best_model_state)
            print(f"恢复最佳模型，验证损失: {self.best_val_loss:.6f}")
        
        # 返回训练历史
        return {
            'train_loss': self.train_losses,
            'val_loss': self.val_losses,
            'best_val_loss': self.best_val_loss,
            'epochs_trained': len(self.train_losses)
        }
    
    def save_model(self, filepath, metadata=None):
        """保存模型到.pth文件"""
        # 创建保存目录
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 准备保存数据
        save_data = {
            'model_state_dict': self.model.state_dict(),
            'model_config': {
                'num_channels': self.model.num_channels,
                'hidden_size': self.model.hidden_size,
                'num_layers': self.model.num_layers,
                'horizon': self.model.horizon
            },
            'training_history': {
                'train_losses': self.train_losses,
                'val_losses': self.val_losses,
                'best_val_loss': self.best_val_loss
            },
            'metadata': metadata or {}
        }
        
        # 保存模型
        torch.save(save_data, filepath)
        print(f"模型已保存到: {filepath}")
        
        # 保存元数据到JSON文件（需要处理numpy数组）
        metadata_file = filepath.replace('.pth', '_metadata.json')
        
        # 创建可序列化的metadata副本
        serializable_metadata = self._make_metadata_serializable(metadata or {})
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_metadata, f, indent=2, ensure_ascii=False)
        print(f"元数据已保存到: {metadata_file}")
    
    def _make_metadata_serializable(self, metadata):
        """将metadata中的numpy数组转换为可序列化的格式"""
        import numpy as np
        
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {key: convert_numpy(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            else:
                return obj
        
        return convert_numpy(metadata)
    
    def load_model(self, filepath):
        """从.pth文件加载模型"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"模型文件不存在: {filepath}")
        
        # 加载模型数据
        save_data = torch.load(filepath, map_location=self.device, weights_only=False)
        
        # 重建模型
        model_config = save_data['model_config']
        self.model = MultiChannelLSTM(**model_config).to(self.device)
        
        # 加载模型状态
        self.model.load_state_dict(save_data['model_state_dict'])
        
        # 恢复训练历史
        self.train_losses = save_data['training_history']['train_losses']
        self.val_losses = save_data['training_history']['val_losses']
        self.best_val_loss = save_data['training_history']['best_val_loss']
        
        print(f"模型已从 {filepath} 加载")
        print(f"模型配置: {model_config}")
        print(f"最佳验证损失: {self.best_val_loss:.6f}")
        
        return save_data.get('metadata', {})
    
    def plot_training_history(self, save_path=None):
        """绘制训练历史"""
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(self.train_losses, label='训练损失', color='blue')
        plt.plot(self.val_losses, label='验证损失', color='red')
        plt.title('训练历史')
        plt.xlabel('Epoch')
        plt.ylabel('损失')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(self.train_losses, label='训练损失', color='blue', alpha=0.7)
        plt.plot(self.val_losses, label='验证损失', color='red', alpha=0.7)
        plt.title('训练历史 (对数刻度)')
        plt.xlabel('Epoch')
        plt.ylabel('损失 (log)')
        plt.yscale('log')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"训练历史图已保存到: {save_path}")
        
        plt.show()

def create_data_loaders(X_train, y_train, X_val, y_val, batch_size=32):
    """创建PyTorch数据加载器"""
    # 转换数据形状: (samples, channels, window_size) -> (samples, window_size, channels)
    X_train = np.transpose(X_train, (0, 2, 1))  # (samples, window_size, channels)
    X_val = np.transpose(X_val, (0, 2, 1))      # (samples, window_size, channels)
    
    # 转换为PyTorch张量
    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.FloatTensor(y_train)
    X_val_tensor = torch.FloatTensor(X_val)
    y_val_tensor = torch.FloatTensor(y_val)
    
    print(f"✅ 数据形状转换完成:")
    print(f"  - X_train: {X_train_tensor.shape}")
    print(f"  - y_train: {y_train_tensor.shape}")
    print(f"  - X_val: {X_val_tensor.shape}")
    print(f"  - y_val: {y_val_tensor.shape}")
    
    # 创建数据集
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    val_dataset = TensorDataset(X_val_tensor, y_val_tensor)
    
    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader

def predict_future(model, last_sequence, horizon, device='cuda' if torch.cuda.is_available() else 'cpu'):
    """使用训练好的模型进行未来预测"""
    model.eval()
    
    # 确保输入格式正确
    if isinstance(last_sequence, np.ndarray):
        last_sequence = torch.FloatTensor(last_sequence)
    
    # 添加batch维度并转换形状
    if last_sequence.dim() == 2:  # (channels, window_size)
        last_sequence = last_sequence.unsqueeze(0)  # (1, channels, window_size)
        # 转换为 (1, window_size, channels)
        last_sequence = last_sequence.transpose(1, 2)
    
    last_sequence = last_sequence.to(device)
    
    with torch.no_grad():
        prediction = model(last_sequence)
        # prediction shape: (1, channels, horizon)
        prediction = prediction.squeeze(0).cpu().numpy()  # (channels, horizon)
    
    return prediction

# 使用示例
if __name__ == "__main__":
    # 模拟多通道传感器数据
    np.random.seed(42)
    num_channels = 4
    num_timesteps = 1000
    
    # 生成模拟数据
    data = np.random.randn(num_channels, num_timesteps)
    # 添加一些趋势和周期性
    for i in range(num_channels):
        trend = np.linspace(0, 2, num_timesteps)
        seasonal = 0.5 * np.sin(2 * np.pi * np.arange(num_timesteps) / 100)
        data[i, :] += trend + seasonal
    
    print("模拟数据生成完成")
    print(f"数据形状: {data.shape}")
    
    # 数据预处理
    preprocessor = MultiChannelSensorPreprocessor(window_size=24, horizon=12)
    processed_data = preprocessor.fit_transform(data)
    
    # 创建数据加载器
    train_loader, val_loader = create_data_loaders(
        processed_data['X_train'], processed_data['y_train'],
        processed_data['X_val'], processed_data['y_val'],
        batch_size=32
    )
    
    # 创建模型
    model = MultiChannelLSTM(
        num_channels=processed_data['num_channels'],
        hidden_size=64,
        num_layers=2,
        horizon=12
    )
    
    # 创建训练器
    trainer = MultiChannelTrainer(model)
    
    # 训练模型
    trainer.train(train_loader, val_loader, epochs=50, lr=0.001, patience=10)
    
    # 保存模型
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"models/multi_channel_lstm_{timestamp}.pth"
    
    metadata = {
        'model_name': 'MultiChannelLSTM',
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
        'channel_stats': processed_data['channel_stats']
    }
    
    trainer.save_model(model_path, metadata)
    
    # 绘制训练历史
    trainer.plot_training_history(f"models/training_history_{timestamp}.png")
    
    print("训练完成！") 