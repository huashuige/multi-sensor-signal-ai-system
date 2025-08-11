import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet, MonitorTask

def check_training_logs():
    """检查训练日志和错误信息"""
    
    print("🔍 检查训练日志...")
    
    # 查找最新的训练集
    training_sets = TrainingSet.objects.filter(name__icontains='模拟数据').order_by('-created_at')
    
    if not training_sets.exists():
        print("❌ 没有找到模拟数据的训练集")
        return
    
    training_set = training_sets.first()
    print(f"📊 训练集: {training_set.name}")
    print(f"📊 训练集ID: {training_set.training_set_id}")
    print(f"📊 当前状态: {training_set.training_status}")
    print(f"📊 状态: {training_set.status}")
    
    # 检查数据源
    selected_data_sources = training_set.selected_data_sources
    print(f"📊 选中的数据源: {selected_data_sources}")
    
    if isinstance(selected_data_sources, dict):
        data_source = selected_data_sources.get('dataSource', {})
        task_id = data_source.get('task_id')
        channels = data_source.get('channels', [])
        
        print(f"📊 任务ID: {task_id}")
        print(f"📊 通道: {channels}")
        
        # 检查监控任务是否存在
        try:
            task = MonitorTask.objects.get(task_id=task_id)
            print(f"✅ 监控任务存在: {task.task_name}")
            print(f"📊 CSV文件路径: {task.csv_file_path}")
            print(f"📊 文件是否存在: {os.path.exists(task.csv_file_path)}")
            print(f"📊 启用通道: {task.enabled_channels}")
            print(f"📊 总数据点: {task.total_data_points}")
        except MonitorTask.DoesNotExist:
            print(f"❌ 监控任务不存在: {task_id}")
    
    # 检查学习参数
    learning_params = training_set.learning_params
    print(f"📊 学习参数: {learning_params}")
    
    if isinstance(learning_params, dict):
        basic_params = learning_params.get('basic', {})
        print(f"📊 基础参数:")
        for key, value in basic_params.items():
            print(f"   - {key}: {value}")
    
    # 检查是否有错误信息
    print(f"\n🔍 检查可能的错误...")
    
    # 检查数据文件大小
    if task_id:
        try:
            task = MonitorTask.objects.get(task_id=task_id)
            if os.path.exists(task.csv_file_path):
                file_size = os.path.getsize(task.csv_file_path)
                print(f"📊 数据文件大小: {file_size} 字节")
                
                if file_size < 1000:
                    print(f"⚠️ 警告: 数据文件太小，可能没有有效数据")
                
                # 尝试读取文件的前几行
                try:
                    import pandas as pd
                    df = pd.read_csv(task.csv_file_path, nrows=5)
                    print(f"📊 数据文件前5行:")
                    print(df.head())
                except Exception as e:
                    print(f"❌ 读取数据文件失败: {e}")
            else:
                print(f"❌ 数据文件不存在: {task.csv_file_path}")
        except MonitorTask.DoesNotExist:
            print(f"❌ 监控任务不存在")
    
    print(f"\n💡 建议:")
    print(f"1. 检查数据文件是否存在且有效")
    print(f"2. 检查训练参数是否正确")
    print(f"3. 检查是否有Python错误日志")
    print(f"4. 尝试重新启动训练")

if __name__ == "__main__":
    check_training_logs() 
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet, MonitorTask

def check_training_logs():
    """检查训练日志和错误信息"""
    
    print("🔍 检查训练日志...")
    
    # 查找最新的训练集
    training_sets = TrainingSet.objects.filter(name__icontains='模拟数据').order_by('-created_at')
    
    if not training_sets.exists():
        print("❌ 没有找到模拟数据的训练集")
        return
    
    training_set = training_sets.first()
    print(f"📊 训练集: {training_set.name}")
    print(f"📊 训练集ID: {training_set.training_set_id}")
    print(f"📊 当前状态: {training_set.training_status}")
    print(f"📊 状态: {training_set.status}")
    
    # 检查数据源
    selected_data_sources = training_set.selected_data_sources
    print(f"📊 选中的数据源: {selected_data_sources}")
    
    if isinstance(selected_data_sources, dict):
        data_source = selected_data_sources.get('dataSource', {})
        task_id = data_source.get('task_id')
        channels = data_source.get('channels', [])
        
        print(f"📊 任务ID: {task_id}")
        print(f"📊 通道: {channels}")
        
        # 检查监控任务是否存在
        try:
            task = MonitorTask.objects.get(task_id=task_id)
            print(f"✅ 监控任务存在: {task.task_name}")
            print(f"📊 CSV文件路径: {task.csv_file_path}")
            print(f"📊 文件是否存在: {os.path.exists(task.csv_file_path)}")
            print(f"📊 启用通道: {task.enabled_channels}")
            print(f"📊 总数据点: {task.total_data_points}")
        except MonitorTask.DoesNotExist:
            print(f"❌ 监控任务不存在: {task_id}")
    
    # 检查学习参数
    learning_params = training_set.learning_params
    print(f"📊 学习参数: {learning_params}")
    
    if isinstance(learning_params, dict):
        basic_params = learning_params.get('basic', {})
        print(f"📊 基础参数:")
        for key, value in basic_params.items():
            print(f"   - {key}: {value}")
    
    # 检查是否有错误信息
    print(f"\n🔍 检查可能的错误...")
    
    # 检查数据文件大小
    if task_id:
        try:
            task = MonitorTask.objects.get(task_id=task_id)
            if os.path.exists(task.csv_file_path):
                file_size = os.path.getsize(task.csv_file_path)
                print(f"📊 数据文件大小: {file_size} 字节")
                
                if file_size < 1000:
                    print(f"⚠️ 警告: 数据文件太小，可能没有有效数据")
                
                # 尝试读取文件的前几行
                try:
                    import pandas as pd
                    df = pd.read_csv(task.csv_file_path, nrows=5)
                    print(f"📊 数据文件前5行:")
                    print(df.head())
                except Exception as e:
                    print(f"❌ 读取数据文件失败: {e}")
            else:
                print(f"❌ 数据文件不存在: {task.csv_file_path}")
        except MonitorTask.DoesNotExist:
            print(f"❌ 监控任务不存在")
    
    print(f"\n💡 建议:")
    print(f"1. 检查数据文件是否存在且有效")
    print(f"2. 检查训练参数是否正确")
    print(f"3. 检查是否有Python错误日志")
    print(f"4. 尝试重新启动训练")

if __name__ == "__main__":
    check_training_logs() 
 
 