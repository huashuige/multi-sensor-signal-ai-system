import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def fix_user_email():
    """修复模拟数据的用户邮箱"""
    
    # 查找所有以 'sim_' 开头的任务
    simulated_tasks = MonitorTask.objects.filter(task_id__startswith='sim_')
    
    print(f"🔍 找到 {simulated_tasks.count()} 个模拟数据任务")
    
    # 获取当前登录用户的邮箱（这里需要你提供实际的邮箱）
    # 你可以从浏览器开发者工具中查看session中的user_email
    current_user_email = input("请输入你的用户邮箱: ").strip()
    
    if not current_user_email:
        print("❌ 未提供用户邮箱，退出")
        return
    
    for task in simulated_tasks:
        print(f"📊 任务ID: {task.task_id}")
        print(f"📊 任务名称: {task.task_name}")
        print(f"📊 当前用户邮箱: {task.user_email}")
        
        # 更新用户邮箱
        task.user_email = current_user_email
        task.user_name = "当前用户"  # 也可以更新用户名
        task.save()
        print(f"✅ 已更新用户邮箱为: {current_user_email}")
        
        print("-" * 50)
    
    print(f"\n🎯 修复完成！现在可以在深度学习模块中看到模拟数据了。")
    print(f"💡 请刷新深度学习页面并点击'刷新数据源'按钮")

if __name__ == "__main__":
    fix_user_email() 
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def fix_user_email():
    """修复模拟数据的用户邮箱"""
    
    # 查找所有以 'sim_' 开头的任务
    simulated_tasks = MonitorTask.objects.filter(task_id__startswith='sim_')
    
    print(f"🔍 找到 {simulated_tasks.count()} 个模拟数据任务")
    
    # 获取当前登录用户的邮箱（这里需要你提供实际的邮箱）
    # 你可以从浏览器开发者工具中查看session中的user_email
    current_user_email = input("请输入你的用户邮箱: ").strip()
    
    if not current_user_email:
        print("❌ 未提供用户邮箱，退出")
        return
    
    for task in simulated_tasks:
        print(f"📊 任务ID: {task.task_id}")
        print(f"📊 任务名称: {task.task_name}")
        print(f"📊 当前用户邮箱: {task.user_email}")
        
        # 更新用户邮箱
        task.user_email = current_user_email
        task.user_name = "当前用户"  # 也可以更新用户名
        task.save()
        print(f"✅ 已更新用户邮箱为: {current_user_email}")
        
        print("-" * 50)
    
    print(f"\n🎯 修复完成！现在可以在深度学习模块中看到模拟数据了。")
    print(f"💡 请刷新深度学习页面并点击'刷新数据源'按钮")

if __name__ == "__main__":
    fix_user_email() 
 
 