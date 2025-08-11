import os
import sys
import django
import time

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def test_training_control():
    """测试训练控制功能"""
    
    print("🧪 测试训练控制功能...")
    
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
    
    # 测试暂停功能
    print("\n⏸️ 测试暂停功能...")
    training_set.training_status = 'paused'
    training_set.save()
    print(f"✅ 训练已暂停，状态: {training_set.training_status}")
    
    # 测试恢复功能
    print("\n▶️ 测试恢复功能...")
    training_set.training_status = 'training'
    training_set.save()
    print(f"✅ 训练已恢复，状态: {training_set.training_status}")
    
    # 测试停止功能
    print("\n⏹️ 测试停止功能...")
    training_set.training_status = 'stopped'
    training_set.status = 'failed'
    training_set.save()
    print(f"✅ 训练已停止，状态: {training_set.training_status}")
    
    # 测试重新训练（重置进度）
    print("\n🔄 测试重新训练（重置进度）...")
    training_set.status = 'training'
    training_set.training_status = 'running'
    training_set.current_epoch = 0
    training_set.total_epochs = 0
    training_set.save()
    print(f"✅ 训练进度已重置，当前轮数: {training_set.current_epoch}")
    
    print("\n🎯 测试完成！")
    print("💡 现在可以测试实际的训练控制功能了")

if __name__ == "__main__":
    test_training_control() 
import sys
import django
import time

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def test_training_control():
    """测试训练控制功能"""
    
    print("🧪 测试训练控制功能...")
    
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
    
    # 测试暂停功能
    print("\n⏸️ 测试暂停功能...")
    training_set.training_status = 'paused'
    training_set.save()
    print(f"✅ 训练已暂停，状态: {training_set.training_status}")
    
    # 测试恢复功能
    print("\n▶️ 测试恢复功能...")
    training_set.training_status = 'training'
    training_set.save()
    print(f"✅ 训练已恢复，状态: {training_set.training_status}")
    
    # 测试停止功能
    print("\n⏹️ 测试停止功能...")
    training_set.training_status = 'stopped'
    training_set.status = 'failed'
    training_set.save()
    print(f"✅ 训练已停止，状态: {training_set.training_status}")
    
    # 测试重新训练（重置进度）
    print("\n🔄 测试重新训练（重置进度）...")
    training_set.status = 'training'
    training_set.training_status = 'running'
    training_set.current_epoch = 0
    training_set.total_epochs = 0
    training_set.save()
    print(f"✅ 训练进度已重置，当前轮数: {training_set.current_epoch}")
    
    print("\n🎯 测试完成！")
    print("💡 现在可以测试实际的训练控制功能了")

if __name__ == "__main__":
    test_training_control() 
 
 