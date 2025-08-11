import os
import sys
import django
import time

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def debug_training():
    """调试训练进度更新问题"""
    
    print("🔍 调试训练进度更新...")
    
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
    
    # 监控训练进度变化
    print(f"\n🔄 开始监控训练进度变化...")
    initial_epoch = training_set.current_epoch
    
    for i in range(30):  # 监控30秒
        time.sleep(1)
        
        # 重新获取训练集数据
        training_set.refresh_from_db()
        
        if training_set.current_epoch != initial_epoch:
            print(f"✅ 检测到进度更新: {initial_epoch} -> {training_set.current_epoch}")
            initial_epoch = training_set.current_epoch
        else:
            print(f"⏳ 等待进度更新... ({i+1}/30秒)")
            
        # 如果训练完成或失败，停止监控
        if training_set.training_status in ['completed', 'failed']:
            print(f"🏁 训练结束，最终状态: {training_set.training_status}")
            break
    
    print(f"\n📊 最终训练状态:")
    print(f"   - 当前轮数: {training_set.current_epoch}")
    print(f"   - 总轮数: {training_set.total_epochs}")
    print(f"   - 训练状态: {training_set.training_status}")
    print(f"   - 状态: {training_set.status}")

if __name__ == "__main__":
    debug_training() 
import sys
import django
import time

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def debug_training():
    """调试训练进度更新问题"""
    
    print("🔍 调试训练进度更新...")
    
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
    
    # 监控训练进度变化
    print(f"\n🔄 开始监控训练进度变化...")
    initial_epoch = training_set.current_epoch
    
    for i in range(30):  # 监控30秒
        time.sleep(1)
        
        # 重新获取训练集数据
        training_set.refresh_from_db()
        
        if training_set.current_epoch != initial_epoch:
            print(f"✅ 检测到进度更新: {initial_epoch} -> {training_set.current_epoch}")
            initial_epoch = training_set.current_epoch
        else:
            print(f"⏳ 等待进度更新... ({i+1}/30秒)")
            
        # 如果训练完成或失败，停止监控
        if training_set.training_status in ['completed', 'failed']:
            print(f"🏁 训练结束，最终状态: {training_set.training_status}")
            break
    
    print(f"\n📊 最终训练状态:")
    print(f"   - 当前轮数: {training_set.current_epoch}")
    print(f"   - 总轮数: {training_set.total_epochs}")
    print(f"   - 训练状态: {training_set.training_status}")
    print(f"   - 状态: {training_set.status}")

if __name__ == "__main__":
    debug_training() 
 
 