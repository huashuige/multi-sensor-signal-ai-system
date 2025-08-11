# 多通道传感器数据LSTM预测系统

## 系统概述

这是一个基于PyTorch的多通道传感器数据时间序列预测系统，专门设计用于处理多通道传感器数据（如温度、湿度、加速度、电压等）的预测任务。

## 核心特性

### 🎯 **多通道支持**
- 支持任意数量的传感器通道
- 每个通道独立归一化处理
- 同时预测所有通道的未来值

### 📊 **数据处理**
- 自动缺失值处理（前向填充 + 后向填充）
- 异常值检测与处理（IQR方法）
- 多通道独立归一化
- 时间序列窗口创建

### 🧠 **深度学习模型**
- 基于LSTM的序列到序列模型
- 支持多层LSTM架构
- 可配置的隐藏层大小和dropout
- 早停机制防止过拟合

### 💾 **模型管理**
- `.pth`格式模型保存
- 完整的元数据保存
- 训练历史记录
- 模型加载和预测功能

## 文件结构

```
polls/
├── multi_channel_lstm.py          # 核心LSTM模型和训练器
├── sensor_data_loader.py          # 数据加载和预处理
├── deep_learning_views.py         # Django视图
├── test_multi_channel_training.py # 测试脚本
└── README_MULTI_CHANNEL_LSTM.md  # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install torch numpy pandas matplotlib
```

### 2. 运行测试

```bash
cd multi
python test_multi_channel_training.py
```

### 3. 在Django中使用

```python
from polls.sensor_data_loader import train_multi_channel_model, predict_with_model

# 训练模型
trainer, metadata = train_multi_channel_model(
    task_ids=['task1', 'task2'],
    channels=['temperature', 'humidity', 'acceleration'],
    model_config={
        'window_size': 24,
        'horizon': 12,
        'hidden_size': 64,
        'num_layers': 2,
        'dropout': 0.1,
        'batch_size': 32,
        'epochs': 100,
        'lr': 0.001,
        'patience': 10
    }
)

# 使用模型预测
prediction, metadata = predict_with_model(
    model_path='models/multi_channel_lstm_20240101_120000.pth',
    input_sequence=input_data,
    denormalize=True
)
```

## 数据格式

### 输入数据格式
```python
# 数据形状: (channels, timesteps)
data = np.array([
    [25.1, 25.2, 25.3, ...],  # 温度通道
    [60.2, 60.1, 60.3, ...],  # 湿度通道
    [0.12, 0.15, 0.13, ...],  # 加速度通道
    [220, 221, 220, ...]       # 电压通道
])
```

### 预测输出格式
```python
# 预测结果形状: (channels, horizon)
prediction = np.array([
    [26.1, 26.2, 26.3, ...],  # 温度预测
    [59.8, 59.9, 60.0, ...],  # 湿度预测
    [0.14, 0.15, 0.14, ...],  # 加速度预测
    [222, 223, 222, ...]       # 电压预测
])
```

## 模型配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `window_size` | 24 | 输入窗口大小（时间步数） |
| `horizon` | 12 | 预测步数 |
| `hidden_size` | 64 | LSTM隐藏层大小 |
| `num_layers` | 2 | LSTM层数 |
| `dropout` | 0.1 | Dropout比率 |
| `batch_size` | 32 | 批次大小 |
| `epochs` | 100 | 训练轮数 |
| `lr` | 0.001 | 学习率 |
| `patience` | 10 | 早停耐心值 |

## 支持的传感器通道

系统支持以下传感器通道：

- `temperature` - 温度
- `humidity` - 湿度
- `acceleration` - 加速度
- `voltage` - 电压
- `current` - 电流
- `power` - 功率
- `frequency` - 频率
- `pressure` - 压力
- `flow_rate` - 流量
- `level` - 液位

## Django集成

### URL路由
```python
# 深度学习仪表板
path('deep-learning-dashboard/', deep_learning_views.deep_learning_dashboard, name='deep_learning_dashboard'),

# API端点
path('api/start-model-training/', deep_learning_views.start_training, name='start_model_training'),
path('api/predict-data/', deep_learning_views.predict_data, name='predict_data'),
path('api/get-model-info/', deep_learning_views.get_model_info, name='get_model_info'),
path('api/get-available-channels/', deep_learning_views.get_available_channels, name='get_available_channels'),
path('api/get-recent-data/', deep_learning_views.get_recent_data, name='get_recent_data'),
path('api/delete-model/', deep_learning_views.delete_model, name='delete_model'),
```

### 前端调用示例

```javascript
// 开始训练
fetch('/api/start-model-training/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        task_ids: ['task1', 'task2'],
        channels: ['temperature', 'humidity', 'acceleration'],
        model_config: {
            window_size: 24,
            horizon: 12,
            hidden_size: 64,
            num_layers: 2,
            dropout: 0.1,
            batch_size: 32,
            epochs: 100,
            lr: 0.001,
            patience: 10
        }
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('训练已开始');
    } else {
        console.error('训练失败:', data.message);
    }
});

// 进行预测
fetch('/api/predict-data/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        model_path: 'models/multi_channel_lstm_20240101_120000.pth',
        input_data: input_sequence
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('预测结果:', data.data);
    } else {
        console.error('预测失败:', data.message);
    }
});
```

## 模型文件结构

### `.pth`文件内容
```python
{
    'model_state_dict': model.state_dict(),
    'model_config': {
        'num_channels': 4,
        'hidden_size': 64,
        'num_layers': 2,
        'horizon': 12
    },
    'training_history': {
        'train_losses': [...],
        'val_losses': [...],
        'best_val_loss': 0.001234
    },
    'metadata': {
        'model_name': 'MultiChannelLSTM',
        'training_date': '20240101_120000',
        'task_ids': ['task1', 'task2'],
        'channels': ['temperature', 'humidity', 'acceleration', 'voltage'],
        'channel_stats': {...}
    }
}
```

### 元数据文件 (`_metadata.json`)
```json
{
    "model_name": "MultiChannelLSTM",
    "training_date": "20240101_120000",
    "task_ids": ["task1", "task2"],
    "channels": ["temperature", "humidity", "acceleration", "voltage"],
    "data_info": {
        "num_channels": 4,
        "num_timesteps": 1000,
        "window_size": 24,
        "horizon": 12
    },
    "model_config": {
        "hidden_size": 64,
        "num_layers": 2,
        "dropout": 0.1
    },
    "channel_stats": {
        "0": {"min": 20.1, "max": 30.2, "mean": 25.1, "std": 2.1},
        "1": {"min": 40.0, "max": 80.0, "mean": 60.0, "std": 10.0},
        "2": {"min": 0.1, "max": 0.2, "mean": 0.15, "std": 0.02},
        "3": {"min": 220, "max": 240, "mean": 230, "std": 5.0}
    },
    "best_val_loss": 0.001234
}
```

## 性能优化建议

### 1. 数据预处理
- 确保数据质量，处理缺失值和异常值
- 选择合适的归一化方法
- 考虑数据的时间对齐

### 2. 模型配置
- 根据数据复杂度调整隐藏层大小
- 使用适当的dropout防止过拟合
- 调整学习率和早停参数

### 3. 训练策略
- 使用学习率调度器
- 监控验证损失
- 保存最佳模型

### 4. 预测优化
- 批量预测提高效率
- 使用GPU加速（如果可用）
- 缓存模型避免重复加载

## 故障排除

### 常见问题

1. **内存不足**
   - 减少batch_size
   - 减少hidden_size
   - 使用更小的window_size

2. **训练不收敛**
   - 检查学习率设置
   - 增加训练轮数
   - 检查数据质量

3. **预测结果异常**
   - 检查输入数据格式
   - 验证模型文件完整性
   - 确认通道数量匹配

4. **模型加载失败**
   - 检查文件路径
   - 验证PyTorch版本兼容性
   - 确认模型文件完整性

## 扩展功能

### 1. 添加新的传感器类型
在`sensor_data_loader.py`中的`channel_mapping`字典中添加新通道：

```python
self.channel_mapping = {
    'temperature': 'temperature',
    'humidity': 'humidity',
    'acceleration': 'acceleration',
    'voltage': 'voltage',
    'new_sensor': 'new_sensor'  # 添加新传感器
}
```

### 2. 自定义模型架构
继承`MultiChannelLSTM`类并重写`forward`方法：

```python
class CustomMultiChannelLSTM(MultiChannelLSTM):
    def __init__(self, num_channels, hidden_size, num_layers, horizon, dropout=0.1):
        super().__init__(num_channels, hidden_size, num_layers, horizon, dropout)
        # 添加自定义层
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=8)
    
    def forward(self, x):
        # 自定义前向传播逻辑
        # ...
        return output
```

### 3. 集成其他深度学习框架
系统设计为模块化，可以轻松集成其他框架如TensorFlow或Keras。

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个系统！

---

**注意**: 这是一个完整的PyTorch多通道传感器数据预测系统，支持`.pth`格式模型保存，可以用于后续的预测任务和其他数据集。 

## 系统概述

这是一个基于PyTorch的多通道传感器数据时间序列预测系统，专门设计用于处理多通道传感器数据（如温度、湿度、加速度、电压等）的预测任务。

## 核心特性

### 🎯 **多通道支持**
- 支持任意数量的传感器通道
- 每个通道独立归一化处理
- 同时预测所有通道的未来值

### 📊 **数据处理**
- 自动缺失值处理（前向填充 + 后向填充）
- 异常值检测与处理（IQR方法）
- 多通道独立归一化
- 时间序列窗口创建

### 🧠 **深度学习模型**
- 基于LSTM的序列到序列模型
- 支持多层LSTM架构
- 可配置的隐藏层大小和dropout
- 早停机制防止过拟合

### 💾 **模型管理**
- `.pth`格式模型保存
- 完整的元数据保存
- 训练历史记录
- 模型加载和预测功能

## 文件结构

```
polls/
├── multi_channel_lstm.py          # 核心LSTM模型和训练器
├── sensor_data_loader.py          # 数据加载和预处理
├── deep_learning_views.py         # Django视图
├── test_multi_channel_training.py # 测试脚本
└── README_MULTI_CHANNEL_LSTM.md  # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install torch numpy pandas matplotlib
```

### 2. 运行测试

```bash
cd multi
python test_multi_channel_training.py
```

### 3. 在Django中使用

```python
from polls.sensor_data_loader import train_multi_channel_model, predict_with_model

# 训练模型
trainer, metadata = train_multi_channel_model(
    task_ids=['task1', 'task2'],
    channels=['temperature', 'humidity', 'acceleration'],
    model_config={
        'window_size': 24,
        'horizon': 12,
        'hidden_size': 64,
        'num_layers': 2,
        'dropout': 0.1,
        'batch_size': 32,
        'epochs': 100,
        'lr': 0.001,
        'patience': 10
    }
)

# 使用模型预测
prediction, metadata = predict_with_model(
    model_path='models/multi_channel_lstm_20240101_120000.pth',
    input_sequence=input_data,
    denormalize=True
)
```

## 数据格式

### 输入数据格式
```python
# 数据形状: (channels, timesteps)
data = np.array([
    [25.1, 25.2, 25.3, ...],  # 温度通道
    [60.2, 60.1, 60.3, ...],  # 湿度通道
    [0.12, 0.15, 0.13, ...],  # 加速度通道
    [220, 221, 220, ...]       # 电压通道
])
```

### 预测输出格式
```python
# 预测结果形状: (channels, horizon)
prediction = np.array([
    [26.1, 26.2, 26.3, ...],  # 温度预测
    [59.8, 59.9, 60.0, ...],  # 湿度预测
    [0.14, 0.15, 0.14, ...],  # 加速度预测
    [222, 223, 222, ...]       # 电压预测
])
```

## 模型配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `window_size` | 24 | 输入窗口大小（时间步数） |
| `horizon` | 12 | 预测步数 |
| `hidden_size` | 64 | LSTM隐藏层大小 |
| `num_layers` | 2 | LSTM层数 |
| `dropout` | 0.1 | Dropout比率 |
| `batch_size` | 32 | 批次大小 |
| `epochs` | 100 | 训练轮数 |
| `lr` | 0.001 | 学习率 |
| `patience` | 10 | 早停耐心值 |

## 支持的传感器通道

系统支持以下传感器通道：

- `temperature` - 温度
- `humidity` - 湿度
- `acceleration` - 加速度
- `voltage` - 电压
- `current` - 电流
- `power` - 功率
- `frequency` - 频率
- `pressure` - 压力
- `flow_rate` - 流量
- `level` - 液位

## Django集成

### URL路由
```python
# 深度学习仪表板
path('deep-learning-dashboard/', deep_learning_views.deep_learning_dashboard, name='deep_learning_dashboard'),

# API端点
path('api/start-model-training/', deep_learning_views.start_training, name='start_model_training'),
path('api/predict-data/', deep_learning_views.predict_data, name='predict_data'),
path('api/get-model-info/', deep_learning_views.get_model_info, name='get_model_info'),
path('api/get-available-channels/', deep_learning_views.get_available_channels, name='get_available_channels'),
path('api/get-recent-data/', deep_learning_views.get_recent_data, name='get_recent_data'),
path('api/delete-model/', deep_learning_views.delete_model, name='delete_model'),
```

### 前端调用示例

```javascript
// 开始训练
fetch('/api/start-model-training/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        task_ids: ['task1', 'task2'],
        channels: ['temperature', 'humidity', 'acceleration'],
        model_config: {
            window_size: 24,
            horizon: 12,
            hidden_size: 64,
            num_layers: 2,
            dropout: 0.1,
            batch_size: 32,
            epochs: 100,
            lr: 0.001,
            patience: 10
        }
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('训练已开始');
    } else {
        console.error('训练失败:', data.message);
    }
});

// 进行预测
fetch('/api/predict-data/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        model_path: 'models/multi_channel_lstm_20240101_120000.pth',
        input_data: input_sequence
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('预测结果:', data.data);
    } else {
        console.error('预测失败:', data.message);
    }
});
```

## 模型文件结构

### `.pth`文件内容
```python
{
    'model_state_dict': model.state_dict(),
    'model_config': {
        'num_channels': 4,
        'hidden_size': 64,
        'num_layers': 2,
        'horizon': 12
    },
    'training_history': {
        'train_losses': [...],
        'val_losses': [...],
        'best_val_loss': 0.001234
    },
    'metadata': {
        'model_name': 'MultiChannelLSTM',
        'training_date': '20240101_120000',
        'task_ids': ['task1', 'task2'],
        'channels': ['temperature', 'humidity', 'acceleration', 'voltage'],
        'channel_stats': {...}
    }
}
```

### 元数据文件 (`_metadata.json`)
```json
{
    "model_name": "MultiChannelLSTM",
    "training_date": "20240101_120000",
    "task_ids": ["task1", "task2"],
    "channels": ["temperature", "humidity", "acceleration", "voltage"],
    "data_info": {
        "num_channels": 4,
        "num_timesteps": 1000,
        "window_size": 24,
        "horizon": 12
    },
    "model_config": {
        "hidden_size": 64,
        "num_layers": 2,
        "dropout": 0.1
    },
    "channel_stats": {
        "0": {"min": 20.1, "max": 30.2, "mean": 25.1, "std": 2.1},
        "1": {"min": 40.0, "max": 80.0, "mean": 60.0, "std": 10.0},
        "2": {"min": 0.1, "max": 0.2, "mean": 0.15, "std": 0.02},
        "3": {"min": 220, "max": 240, "mean": 230, "std": 5.0}
    },
    "best_val_loss": 0.001234
}
```

## 性能优化建议

### 1. 数据预处理
- 确保数据质量，处理缺失值和异常值
- 选择合适的归一化方法
- 考虑数据的时间对齐

### 2. 模型配置
- 根据数据复杂度调整隐藏层大小
- 使用适当的dropout防止过拟合
- 调整学习率和早停参数

### 3. 训练策略
- 使用学习率调度器
- 监控验证损失
- 保存最佳模型

### 4. 预测优化
- 批量预测提高效率
- 使用GPU加速（如果可用）
- 缓存模型避免重复加载

## 故障排除

### 常见问题

1. **内存不足**
   - 减少batch_size
   - 减少hidden_size
   - 使用更小的window_size

2. **训练不收敛**
   - 检查学习率设置
   - 增加训练轮数
   - 检查数据质量

3. **预测结果异常**
   - 检查输入数据格式
   - 验证模型文件完整性
   - 确认通道数量匹配

4. **模型加载失败**
   - 检查文件路径
   - 验证PyTorch版本兼容性
   - 确认模型文件完整性

## 扩展功能

### 1. 添加新的传感器类型
在`sensor_data_loader.py`中的`channel_mapping`字典中添加新通道：

```python
self.channel_mapping = {
    'temperature': 'temperature',
    'humidity': 'humidity',
    'acceleration': 'acceleration',
    'voltage': 'voltage',
    'new_sensor': 'new_sensor'  # 添加新传感器
}
```

### 2. 自定义模型架构
继承`MultiChannelLSTM`类并重写`forward`方法：

```python
class CustomMultiChannelLSTM(MultiChannelLSTM):
    def __init__(self, num_channels, hidden_size, num_layers, horizon, dropout=0.1):
        super().__init__(num_channels, hidden_size, num_layers, horizon, dropout)
        # 添加自定义层
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=8)
    
    def forward(self, x):
        # 自定义前向传播逻辑
        # ...
        return output
```

### 3. 集成其他深度学习框架
系统设计为模块化，可以轻松集成其他框架如TensorFlow或Keras。

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个系统！

---

**注意**: 这是一个完整的PyTorch多通道传感器数据预测系统，支持`.pth`格式模型保存，可以用于后续的预测任务和其他数据集。 
 
 