import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def temp_remove_user_filter():
    """临时移除用户邮箱过滤，显示所有数据"""
    
    print("🔍 查找所有模拟数据任务...")
    
    # 查找所有以 'sim_' 开头的任务
    simulated_tasks = MonitorTask.objects.filter(task_id__startswith='sim_')
    
    print(f"📊 找到 {simulated_tasks.count()} 个模拟数据任务")
    
    for task in simulated_tasks:
        print(f"📊 任务ID: {task.task_id}")
        print(f"📊 任务名称: {task.task_name}")
        print(f"📊 用户邮箱: {task.user_email}")
        print(f"📊 是否完成: {task.is_completed}")
        print(f"📊 文件路径: {task.csv_file_path}")
        print(f"📊 文件存在: {os.path.exists(task.csv_file_path)}")
        print("-" * 50)
    
    print(f"\n💡 如果文件存在但API不返回数据，可能是用户邮箱不匹配")
    print(f"💡 请检查你的登录邮箱，或者临时修改API代码移除用户过滤")

if __name__ == "__main__":
    temp_remove_user_filter() 
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def temp_remove_user_filter():
    """临时移除用户邮箱过滤，显示所有数据"""
    
    print("🔍 查找所有模拟数据任务...")
    
    # 查找所有以 'sim_' 开头的任务
    simulated_tasks = MonitorTask.objects.filter(task_id__startswith='sim_')
    
    print(f"📊 找到 {simulated_tasks.count()} 个模拟数据任务")
    
    for task in simulated_tasks:
        print(f"📊 任务ID: {task.task_id}")
        print(f"📊 任务名称: {task.task_name}")
        print(f"📊 用户邮箱: {task.user_email}")
        print(f"📊 是否完成: {task.is_completed}")
        print(f"📊 文件路径: {task.csv_file_path}")
        print(f"📊 文件存在: {os.path.exists(task.csv_file_path)}")
        print("-" * 50)
    
    print(f"\n💡 如果文件存在但API不返回数据，可能是用户邮箱不匹配")
    print(f"💡 请检查你的登录邮箱，或者临时修改API代码移除用户过滤")

if __name__ == "__main__":
    temp_remove_user_filter() 
 
 