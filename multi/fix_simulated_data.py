import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def fix_simulated_data():
    """修复现有的模拟数据，将其标记为已完成"""
    
    # 查找所有以 'sim_' 开头的任务
    simulated_tasks = MonitorTask.objects.filter(task_id__startswith='sim_')
    
    print(f"🔍 找到 {simulated_tasks.count()} 个模拟数据任务")
    
    for task in simulated_tasks:
        print(f"📊 任务ID: {task.task_id}")
        print(f"📊 任务名称: {task.task_name}")
        print(f"📊 当前状态: is_completed={task.is_completed}")
        
        # 检查文件是否存在
        if os.path.exists(task.csv_file_path):
            print(f"✅ 文件存在: {task.csv_file_path}")
            
            # 标记为已完成
            task.is_completed = True
            task.save()
            print(f"✅ 已标记为已完成")
        else:
            print(f"❌ 文件不存在: {task.csv_file_path}")
        
        print("-" * 50)
    
    print(f"\n🎯 修复完成！现在可以在深度学习模块中看到模拟数据了。")

if __name__ == "__main__":
    fix_simulated_data() 
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def fix_simulated_data():
    """修复现有的模拟数据，将其标记为已完成"""
    
    # 查找所有以 'sim_' 开头的任务
    simulated_tasks = MonitorTask.objects.filter(task_id__startswith='sim_')
    
    print(f"🔍 找到 {simulated_tasks.count()} 个模拟数据任务")
    
    for task in simulated_tasks:
        print(f"📊 任务ID: {task.task_id}")
        print(f"📊 任务名称: {task.task_name}")
        print(f"📊 当前状态: is_completed={task.is_completed}")
        
        # 检查文件是否存在
        if os.path.exists(task.csv_file_path):
            print(f"✅ 文件存在: {task.csv_file_path}")
            
            # 标记为已完成
            task.is_completed = True
            task.save()
            print(f"✅ 已标记为已完成")
        else:
            print(f"❌ 文件不存在: {task.csv_file_path}")
        
        print("-" * 50)
    
    print(f"\n🎯 修复完成！现在可以在深度学习模块中看到模拟数据了。")

if __name__ == "__main__":
    fix_simulated_data() 
 
 