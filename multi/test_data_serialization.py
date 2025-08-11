import json
import numpy as np

# 模拟从WebSocket消费者传递的数据
test_data = {
    'task_name': '测试任务',
    'task_description': '测试描述',
    'start_time': '2025-07-17T18:44:43',
    'end_time': '2025-07-17T18:44:43',
    'monitor_config': {'sample_rate': 10000},
    'channel_configs': {},
    'enabled_channels': [0, 1, 2],
    'monitor_data': {
        'time_axis': [i * 0.0001 for i in range(6660)],
        'channel_data': {
            0: [-10.0674] * 6660,  # 悬空状态数据
            1: [-10.0674] * 6660,
            2: [-10.0674] * 6660
        }
    },
    'total_acquisitions': 10
}

print("=== 测试数据序列化 ===")
print(f"原始数据:")
print(f"  时间轴长度: {len(test_data['monitor_data']['time_axis'])}")
print(f"  通道数据键: {list(test_data['monitor_data']['channel_data'].keys())}")

for ch in test_data['enabled_channels']:
    ch_data = test_data['monitor_data']['channel_data'][ch]
    print(f"  CH{ch}: 长度={len(ch_data)}, 前5个值={ch_data[:5]}")

# 测试JSON序列化
try:
    json_str = json.dumps(test_data)
    print(f"\nJSON序列化成功，长度: {len(json_str)}")
    
    # 测试反序列化
    parsed_data = json.loads(json_str)
    print(f"JSON反序列化成功")
    
    # 检查反序列化后的数据
    time_axis = parsed_data['monitor_data']['time_axis']
    channel_data = parsed_data['monitor_data']['channel_data']
    
    print(f"\n反序列化后数据:")
    print(f"  时间轴长度: {len(time_axis)}")
    print(f"  时间轴前5个值: {time_axis[:5]}")
    
    for ch in parsed_data['enabled_channels']:
        if ch in channel_data:
            ch_data = channel_data[ch]
            print(f"  CH{ch}: 长度={len(ch_data)}, 前5个值={ch_data[:5]}")
        else:
            print(f"  CH{ch}: 数据不存在")
            
except Exception as e:
    print(f"JSON序列化失败: {e}")

# 测试numpy数组序列化
print(f"\n=== 测试numpy数组序列化 ===")
numpy_data = {
    'time_axis': np.array([i * 0.0001 for i in range(10)]),
    'channel_data': {
        0: np.array([-10.0674] * 10),
        1: np.array([-10.0674] * 10),
        2: np.array([-10.0674] * 10)
    }
}

print(f"numpy数据:")
print(f"  时间轴类型: {type(numpy_data['time_axis'])}")
print(f"  通道数据类型: {type(numpy_data['channel_data'][0])}")

# 转换为普通列表
converted_data = {
    'time_axis': list(numpy_data['time_axis']),
    'channel_data': {}
}

for ch in numpy_data['channel_data']:
    converted_data['channel_data'][ch] = [float(x) for x in numpy_data['channel_data'][ch]]

print(f"\n转换后数据:")
print(f"  时间轴类型: {type(converted_data['time_axis'])}")
print(f"  通道数据类型: {type(converted_data['channel_data'][0])}")

# 测试JSON序列化转换后的数据
try:
    json_str = json.dumps(converted_data)
    print(f"转换后数据JSON序列化成功")
except Exception as e:
    print(f"转换后数据JSON序列化失败: {e}") 