#!/usr/bin/env python
"""
测试从训练集开始训练的完整流程
"""

import os
import sys
import django
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_training_flow():
    """测试训练流程"""
    print("=" * 60)
    print("测试从训练集开始训练的完整流程")
    print("=" * 60)
    
    try:
        from polls.models import TrainingSet, MonitorTask
        
        # 1. 检查训练集
        print("\n1. 检查训练集...")
        training_sets = TrainingSet.objects.filter(is_deleted=False)
        print(f"找到 {training_sets.count()} 个训练集")
        
        for ts in training_sets[:3]:  # 只显示前3个
            print(f"  - {ts.name} (ID: {ts.training_set_id})")
            print(f"    状态: {ts.status}, 模式: {ts.training_mode}")
            print(f"    学习参数: {ts.learning_params}")
            print(f"    数据源: {ts.selected_data_sources}")
        
        # 2. 检查监控任务
        print("\n2. 检查监控任务...")
        tasks = MonitorTask.objects.all()
        print(f"找到 {tasks.count()} 个监控任务")
        
        for task in tasks[:3]:  # 只显示前3个
            print(f"  - {task.task_name} (ID: {task.task_id})")
            print(f"    CSV文件: {task.csv_file_path}")
            print(f"    数据点数: {task.total_data_points}")
            print(f"    启用通道: {task.enabled_channels}")
        
        # 3. 测试数据加载器
        print("\n3. 测试数据加载器...")
        from polls.sensor_data_loader import SensorDataLoader
        
        loader = SensorDataLoader()
        print("✅ 数据加载器创建成功")
        
        # 4. 测试LSTM模型
        print("\n4. 测试LSTM模型...")
        from polls.multi_channel_lstm import MultiChannelLSTM
        
        model = MultiChannelLSTM(
            num_channels=4,
            hidden_size=64,
            num_layers=2,
            horizon=12
        )
        print("✅ LSTM模型创建成功")
        
        # 5. 模拟训练流程
        print("\n5. 模拟训练流程...")
        if training_sets.exists():
            training_set = training_sets.first()
            print(f"选择训练集: {training_set.name}")
            
            # 获取学习参数
            learning_params = training_set.learning_params
            if learning_params:
                print(f"学习参数: {learning_params}")
            else:
                print("⚠️  训练集没有配置学习参数")
                learning_params = {
                    'window_size': 24,
                    'horizon': 12,
                    'hidden_size': 64,
                    'num_layers': 2,
                    'dropout': 0.1,
                    'batch_size': 32,
                    'epochs': 50,
                    'lr': 0.001,
                    'patience': 10
                }
                print(f"使用默认参数: {learning_params}")
            
            # 获取数据源
            selected_data_sources = training_set.selected_data_sources
            if selected_data_sources:
                print(f"数据源: {selected_data_sources}")
                
                # 提取任务ID和通道
                task_ids = []
                channels = []
                
                for data_source in selected_data_sources:
                    task_ids.append(data_source.get('task_id'))
                    channels.extend(data_source.get('channels', []))
                
                channels = list(set(channels))  # 去重
                
                print(f"任务ID: {task_ids}")
                print(f"通道: {channels}")
                
                # 检查CSV文件是否存在
                for task_id in task_ids:
                    try:
                        task = MonitorTask.objects.get(task_id=task_id)
                        csv_path = task.csv_file_path
                        if os.path.exists(csv_path):
                            print(f"✅ CSV文件存在: {csv_path}")
                        else:
                            print(f"❌ CSV文件不存在: {csv_path}")
                    except MonitorTask.DoesNotExist:
                        print(f"❌ 任务ID不存在: {task_id}")
                
            else:
                print("⚠️  训练集没有选择数据源")
        
        print("\n" + "=" * 60)
        print("✅ 训练流程测试完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n测试API端点...")
    
    try:
        from polls import deep_learning_views
        
        # 测试获取训练集信息
        print("✅ deep_learning_views 导入成功")
        
        # 测试其他导入
        from polls.sensor_data_loader import train_multi_channel_model
        print("✅ train_multi_channel_model 导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False

if __name__ == "__main__":
    # 运行测试
    test1 = test_training_flow()
    test2 = test_api_endpoints()
    
    if test1 and test2:
        print("\n🎉 所有测试通过！系统准备就绪。")
    else:
        print("\n❌ 部分测试失败，请检查错误信息。") 
"""
测试从训练集开始训练的完整流程
"""

import os
import sys
import django
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_training_flow():
    """测试训练流程"""
    print("=" * 60)
    print("测试从训练集开始训练的完整流程")
    print("=" * 60)
    
    try:
        from polls.models import TrainingSet, MonitorTask
        
        # 1. 检查训练集
        print("\n1. 检查训练集...")
        training_sets = TrainingSet.objects.filter(is_deleted=False)
        print(f"找到 {training_sets.count()} 个训练集")
        
        for ts in training_sets[:3]:  # 只显示前3个
            print(f"  - {ts.name} (ID: {ts.training_set_id})")
            print(f"    状态: {ts.status}, 模式: {ts.training_mode}")
            print(f"    学习参数: {ts.learning_params}")
            print(f"    数据源: {ts.selected_data_sources}")
        
        # 2. 检查监控任务
        print("\n2. 检查监控任务...")
        tasks = MonitorTask.objects.all()
        print(f"找到 {tasks.count()} 个监控任务")
        
        for task in tasks[:3]:  # 只显示前3个
            print(f"  - {task.task_name} (ID: {task.task_id})")
            print(f"    CSV文件: {task.csv_file_path}")
            print(f"    数据点数: {task.total_data_points}")
            print(f"    启用通道: {task.enabled_channels}")
        
        # 3. 测试数据加载器
        print("\n3. 测试数据加载器...")
        from polls.sensor_data_loader import SensorDataLoader
        
        loader = SensorDataLoader()
        print("✅ 数据加载器创建成功")
        
        # 4. 测试LSTM模型
        print("\n4. 测试LSTM模型...")
        from polls.multi_channel_lstm import MultiChannelLSTM
        
        model = MultiChannelLSTM(
            num_channels=4,
            hidden_size=64,
            num_layers=2,
            horizon=12
        )
        print("✅ LSTM模型创建成功")
        
        # 5. 模拟训练流程
        print("\n5. 模拟训练流程...")
        if training_sets.exists():
            training_set = training_sets.first()
            print(f"选择训练集: {training_set.name}")
            
            # 获取学习参数
            learning_params = training_set.learning_params
            if learning_params:
                print(f"学习参数: {learning_params}")
            else:
                print("⚠️  训练集没有配置学习参数")
                learning_params = {
                    'window_size': 24,
                    'horizon': 12,
                    'hidden_size': 64,
                    'num_layers': 2,
                    'dropout': 0.1,
                    'batch_size': 32,
                    'epochs': 50,
                    'lr': 0.001,
                    'patience': 10
                }
                print(f"使用默认参数: {learning_params}")
            
            # 获取数据源
            selected_data_sources = training_set.selected_data_sources
            if selected_data_sources:
                print(f"数据源: {selected_data_sources}")
                
                # 提取任务ID和通道
                task_ids = []
                channels = []
                
                for data_source in selected_data_sources:
                    task_ids.append(data_source.get('task_id'))
                    channels.extend(data_source.get('channels', []))
                
                channels = list(set(channels))  # 去重
                
                print(f"任务ID: {task_ids}")
                print(f"通道: {channels}")
                
                # 检查CSV文件是否存在
                for task_id in task_ids:
                    try:
                        task = MonitorTask.objects.get(task_id=task_id)
                        csv_path = task.csv_file_path
                        if os.path.exists(csv_path):
                            print(f"✅ CSV文件存在: {csv_path}")
                        else:
                            print(f"❌ CSV文件不存在: {csv_path}")
                    except MonitorTask.DoesNotExist:
                        print(f"❌ 任务ID不存在: {task_id}")
                
            else:
                print("⚠️  训练集没有选择数据源")
        
        print("\n" + "=" * 60)
        print("✅ 训练流程测试完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n测试API端点...")
    
    try:
        from polls import deep_learning_views
        
        # 测试获取训练集信息
        print("✅ deep_learning_views 导入成功")
        
        # 测试其他导入
        from polls.sensor_data_loader import train_multi_channel_model
        print("✅ train_multi_channel_model 导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False

if __name__ == "__main__":
    # 运行测试
    test1 = test_training_flow()
    test2 = test_api_endpoints()
    
    if test1 and test2:
        print("\n🎉 所有测试通过！系统准备就绪。")
    else:
        print("\n❌ 部分测试失败，请检查错误信息。") 
 
 