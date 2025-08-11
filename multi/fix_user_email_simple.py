import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def fix_user_email_simple():
    """修复模拟数据的用户邮箱为常见格式"""
    
    # 查找所有以 'sim_' 开头的任务
    simulated_tasks = MonitorTask.objects.filter(task_id__startswith='sim_')
    
    print(f"🔍 找到 {simulated_tasks.count()} 个模拟数据任务")
    
    # 使用常见的邮箱格式
    current_user_email = "admin@example.com"  # 你可以修改为你的实际邮箱
    
    for task in simulated_tasks:
        print(f"📊 任务ID: {task.task_id}")
        print(f"📊 任务名称: {task.task_name}")
        print(f"📊 当前用户邮箱: {task.user_email}")
        
        # 更新用户邮箱
        task.user_email = current_user_email
        task.user_name = "管理员"
        task.is_completed = True  # 确保标记为已完成
        task.save()
        print(f"✅ 已更新用户邮箱为: {current_user_email}")
        
        print("-" * 50)
    
    print(f"\n🎯 修复完成！")
    print(f"💡 如果还是看不到数据，请检查你的登录邮箱是否为: {current_user_email}")
    print(f"💡 或者你可以修改脚本中的邮箱地址为你的实际登录邮箱")

if __name__ == "__main__":
    fix_user_email_simple() 
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def fix_user_email_simple():
    """修复模拟数据的用户邮箱为常见格式"""
    
    # 查找所有以 'sim_' 开头的任务
    simulated_tasks = MonitorTask.objects.filter(task_id__startswith='sim_')
    
    print(f"🔍 找到 {simulated_tasks.count()} 个模拟数据任务")
    
    # 使用常见的邮箱格式
    current_user_email = "admin@example.com"  # 你可以修改为你的实际邮箱
    
    for task in simulated_tasks:
        print(f"📊 任务ID: {task.task_id}")
        print(f"📊 任务名称: {task.task_name}")
        print(f"📊 当前用户邮箱: {task.user_email}")
        
        # 更新用户邮箱
        task.user_email = current_user_email
        task.user_name = "管理员"
        task.is_completed = True  # 确保标记为已完成
        task.save()
        print(f"✅ 已更新用户邮箱为: {current_user_email}")
        
        print("-" * 50)
    
    print(f"\n🎯 修复完成！")
    print(f"💡 如果还是看不到数据，请检查你的登录邮箱是否为: {current_user_email}")
    print(f"💡 或者你可以修改脚本中的邮箱地址为你的实际登录邮箱")

if __name__ == "__main__":
    fix_user_email_simple() 
 
 