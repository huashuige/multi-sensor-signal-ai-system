import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def manual_update_progress():
    """手动更新训练进度，用于测试"""
    
    print("🔧 手动更新训练进度...")
    
    # 查找最新的训练集
    training_sets = TrainingSet.objects.filter(name__icontains='模拟数据').order_by('-created_at')
    
    if not training_sets.exists():
        print("❌ 没有找到模拟数据的训练集")
        return
    
    training_set = training_sets.first()
    print(f"📊 找到训练集: {training_set.name}")
    print(f"📊 训练集ID: {training_set.training_set_id}")
    print(f"📊 当前状态: {training_set.training_status}")
    print(f"📊 当前轮数: {training_set.current_epoch}")
    print(f"📊 总轮数: {training_set.total_epochs}")
    
    # 手动更新进度
    training_set.current_epoch = 5  # 设置为第5轮
    training_set.total_epochs = 100  # 设置总轮数为100
    training_set.training_status = 'training'
    training_set.save()
    
    print(f"✅ 已手动更新进度:")
    print(f"   - 当前轮数: {training_set.current_epoch}")
    print(f"   - 总轮数: {training_set.total_epochs}")
    print(f"   - 训练状态: {training_set.training_status}")
    
    print(f"\n💡 现在可以刷新训练监控页面查看效果")

if __name__ == "__main__":
    manual_update_progress() 
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def manual_update_progress():
    """手动更新训练进度，用于测试"""
    
    print("🔧 手动更新训练进度...")
    
    # 查找最新的训练集
    training_sets = TrainingSet.objects.filter(name__icontains='模拟数据').order_by('-created_at')
    
    if not training_sets.exists():
        print("❌ 没有找到模拟数据的训练集")
        return
    
    training_set = training_sets.first()
    print(f"📊 找到训练集: {training_set.name}")
    print(f"📊 训练集ID: {training_set.training_set_id}")
    print(f"📊 当前状态: {training_set.training_status}")
    print(f"📊 当前轮数: {training_set.current_epoch}")
    print(f"📊 总轮数: {training_set.total_epochs}")
    
    # 手动更新进度
    training_set.current_epoch = 5  # 设置为第5轮
    training_set.total_epochs = 100  # 设置总轮数为100
    training_set.training_status = 'training'
    training_set.save()
    
    print(f"✅ 已手动更新进度:")
    print(f"   - 当前轮数: {training_set.current_epoch}")
    print(f"   - 总轮数: {training_set.total_epochs}")
    print(f"   - 训练状态: {training_set.training_status}")
    
    print(f"\n💡 现在可以刷新训练监控页面查看效果")

if __name__ == "__main__":
    manual_update_progress() 
 
 