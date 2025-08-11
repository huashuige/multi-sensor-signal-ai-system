import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def check_training_progress():
    """检查训练进度更新是否正常"""
    
    print("🔍 检查训练进度...")
    
    # 查找最新的训练集
    training_sets = TrainingSet.objects.filter(name__icontains='模拟数据').order_by('-created_at')
    
    if not training_sets.exists():
        print("❌ 没有找到模拟数据的训练集")
        return
    
    training_set = training_sets.first()
    print(f"📊 训练集: {training_set.name}")
    print(f"📊 训练集ID: {training_set.training_set_id}")
    print(f"📊 当前状态: {training_set.training_status}")
    print(f"📊 当前轮数: {training_set.current_epoch}")
    print(f"📊 总轮数: {training_set.total_epochs}")
    print(f"📊 训练状态: {training_set.status}")
    
    # 检查是否有训练历史
    if training_set.current_epoch > 0:
        print(f"✅ 训练进度正常，当前轮数: {training_set.current_epoch}")
    else:
        print(f"❌ 训练进度异常，当前轮数为0")
    
    # 检查学习参数
    learning_params = training_set.learning_params
    if isinstance(learning_params, dict):
        basic_params = learning_params.get('basic', {})
        total_epochs = basic_params.get('epochs', 100)
        print(f"📊 配置的总轮数: {total_epochs}")
        
        if training_set.total_epochs != total_epochs:
            print(f"⚠️ 总轮数不匹配: 数据库={training_set.total_epochs}, 配置={total_epochs}")
        else:
            print(f"✅ 总轮数匹配: {training_set.total_epochs}")

if __name__ == "__main__":
    check_training_progress() 
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def check_training_progress():
    """检查训练进度更新是否正常"""
    
    print("🔍 检查训练进度...")
    
    # 查找最新的训练集
    training_sets = TrainingSet.objects.filter(name__icontains='模拟数据').order_by('-created_at')
    
    if not training_sets.exists():
        print("❌ 没有找到模拟数据的训练集")
        return
    
    training_set = training_sets.first()
    print(f"📊 训练集: {training_set.name}")
    print(f"📊 训练集ID: {training_set.training_set_id}")
    print(f"📊 当前状态: {training_set.training_status}")
    print(f"📊 当前轮数: {training_set.current_epoch}")
    print(f"📊 总轮数: {training_set.total_epochs}")
    print(f"📊 训练状态: {training_set.status}")
    
    # 检查是否有训练历史
    if training_set.current_epoch > 0:
        print(f"✅ 训练进度正常，当前轮数: {training_set.current_epoch}")
    else:
        print(f"❌ 训练进度异常，当前轮数为0")
    
    # 检查学习参数
    learning_params = training_set.learning_params
    if isinstance(learning_params, dict):
        basic_params = learning_params.get('basic', {})
        total_epochs = basic_params.get('epochs', 100)
        print(f"📊 配置的总轮数: {total_epochs}")
        
        if training_set.total_epochs != total_epochs:
            print(f"⚠️ 总轮数不匹配: 数据库={training_set.total_epochs}, 配置={total_epochs}")
        else:
            print(f"✅ 总轮数匹配: {training_set.total_epochs}")

if __name__ == "__main__":
    check_training_progress() 
 
 