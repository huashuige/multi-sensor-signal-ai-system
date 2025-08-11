import os
import sys
import django
import threading
import time

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet
from polls.sensor_data_loader import train_multi_channel_model

def test_training_simple():
    """简单测试训练是否正常运行"""
    
    print("🧪 简单测试训练...")
    
    # 查找最新的训练集
    training_sets = TrainingSet.objects.filter(name__icontains='模拟数据').order_by('-created_at')
    
    if not training_sets.exists():
        print("❌ 没有找到模拟数据的训练集")
        return
    
    training_set = training_sets.first()
    print(f"📊 训练集: {training_set.name}")
    print(f"📊 训练集ID: {training_set.training_set_id}")
    
    # 获取训练参数
    learning_params = training_set.learning_params
    if not isinstance(learning_params, dict):
        print("❌ 学习参数格式错误")
        return
    
    basic_params = learning_params.get('basic', {})
    task_ids = training_set.selected_data_sources.get('dataSource', {}).get('task_id', [])
    channels = training_set.selected_data_sources.get('dataSource', {}).get('channels', [])
    
    print(f"📊 任务ID: {task_ids}")
    print(f"📊 通道: {channels}")
    print(f"📊 学习参数: {basic_params}")
    
    # 定义进度回调函数
    def progress_callback(progress_data):
        print(f"📊 进度回调: {progress_data}")
        return True
    
    # 创建模型配置
    model_config = {
        'window_size': basic_params.get('windowSize', 50),
        'horizon': basic_params.get('horizon', 10),
        'batch_size': basic_params.get('batchSize', 32),
        'epochs': basic_params.get('epochs', 100),
        'lr': basic_params.get('learningRate', 0.001),
        'hidden_size': basic_params.get('hiddenSize', 64),
        'num_layers': basic_params.get('lstmLayers', 1),
        'dropout': basic_params.get('dropoutRate', 0.2),
        'patience': basic_params.get('earlyStoppingPatience', 10)
    }
    
    print(f"📊 模型配置: {model_config}")
    
    try:
        # 启动训练
        print(f"🚀 开始训练...")
        
        def train_function():
            try:
                trainer, metadata = train_multi_channel_model(
                    task_ids=[task_ids],
                    channels=channels,
                    model_config=model_config,
                    save_dir="models",
                    progress_callback=progress_callback
                )
                print(f"✅ 训练完成！")
            except Exception as e:
                print(f"❌ 训练失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 启动训练线程
        training_thread = threading.Thread(target=train_function)
        training_thread.daemon = True
        training_thread.start()
        
        # 监控训练进度
        print(f"🔄 监控训练进度...")
        for i in range(60):  # 监控60秒
            time.sleep(1)
            print(f"⏳ 等待训练... ({i+1}/60秒)")
            
            # 检查训练是否完成
            if not training_thread.is_alive():
                print(f"🏁 训练线程已结束")
                break
        
        if training_thread.is_alive():
            print(f"⏰ 60秒后训练仍在进行...")
        
    except Exception as e:
        print(f"❌ 测试训练失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_training_simple() 
import sys
import django
import threading
import time

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet
from polls.sensor_data_loader import train_multi_channel_model

def test_training_simple():
    """简单测试训练是否正常运行"""
    
    print("🧪 简单测试训练...")
    
    # 查找最新的训练集
    training_sets = TrainingSet.objects.filter(name__icontains='模拟数据').order_by('-created_at')
    
    if not training_sets.exists():
        print("❌ 没有找到模拟数据的训练集")
        return
    
    training_set = training_sets.first()
    print(f"📊 训练集: {training_set.name}")
    print(f"📊 训练集ID: {training_set.training_set_id}")
    
    # 获取训练参数
    learning_params = training_set.learning_params
    if not isinstance(learning_params, dict):
        print("❌ 学习参数格式错误")
        return
    
    basic_params = learning_params.get('basic', {})
    task_ids = training_set.selected_data_sources.get('dataSource', {}).get('task_id', [])
    channels = training_set.selected_data_sources.get('dataSource', {}).get('channels', [])
    
    print(f"📊 任务ID: {task_ids}")
    print(f"📊 通道: {channels}")
    print(f"📊 学习参数: {basic_params}")
    
    # 定义进度回调函数
    def progress_callback(progress_data):
        print(f"📊 进度回调: {progress_data}")
        return True
    
    # 创建模型配置
    model_config = {
        'window_size': basic_params.get('windowSize', 50),
        'horizon': basic_params.get('horizon', 10),
        'batch_size': basic_params.get('batchSize', 32),
        'epochs': basic_params.get('epochs', 100),
        'lr': basic_params.get('learningRate', 0.001),
        'hidden_size': basic_params.get('hiddenSize', 64),
        'num_layers': basic_params.get('lstmLayers', 1),
        'dropout': basic_params.get('dropoutRate', 0.2),
        'patience': basic_params.get('earlyStoppingPatience', 10)
    }
    
    print(f"📊 模型配置: {model_config}")
    
    try:
        # 启动训练
        print(f"🚀 开始训练...")
        
        def train_function():
            try:
                trainer, metadata = train_multi_channel_model(
                    task_ids=[task_ids],
                    channels=channels,
                    model_config=model_config,
                    save_dir="models",
                    progress_callback=progress_callback
                )
                print(f"✅ 训练完成！")
            except Exception as e:
                print(f"❌ 训练失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 启动训练线程
        training_thread = threading.Thread(target=train_function)
        training_thread.daemon = True
        training_thread.start()
        
        # 监控训练进度
        print(f"🔄 监控训练进度...")
        for i in range(60):  # 监控60秒
            time.sleep(1)
            print(f"⏳ 等待训练... ({i+1}/60秒)")
            
            # 检查训练是否完成
            if not training_thread.is_alive():
                print(f"🏁 训练线程已结束")
                break
        
        if training_thread.is_alive():
            print(f"⏰ 60秒后训练仍在进行...")
        
    except Exception as e:
        print(f"❌ 测试训练失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_training_simple() 
 
 